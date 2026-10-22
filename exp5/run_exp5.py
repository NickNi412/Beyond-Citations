"""Experiment 5 — does a plain LLM audit find what the audit card finds?

On the six real reports of the case study, each model audits the report directly, without our structure, under two
prompts:
  plain  : list, in priority order, what a reader should check before relying on the conclusion, and where to look;
  strong : the same, and answer three questions the card answers: which single check, if false, removes all support;
           how many cited studies can be wrong with the conclusion still supported; which checks are enough for the
           conclusion to survive any one wrong study.
A separate grader model (not one of the audited models) then maps each single-condition bottleneck of the same
model's audit card (computed from that model's extraction in the case study) to the checks of its direct audit.

Pre-registered measures, per model and prompt (computed in `analyze`):
  1. coverage   : share of the card's single-condition bottlenecks that the direct audit asks the reader to check;
  2. flagged    : (strong) share of those bottlenecks that the direct audit says would alone remove all support;
  3. enough-set : (strong) whether the checks it calls enough contain every card bottleneck. Every set of checks that
                  makes the conclusion survive one wrong study must contain all single-condition bottlenecks, so a set
                  that misses one is insufficient on the model's own reading of the report;
  4. tolerance  : (strong) stated number of studies that can be wrong, against tau_S - 1 from the same model's card;
  5. length     : number of checks listed.

Steps (each resumes where it stopped; add --mock for an offline test that writes *_mock files):
  python -m exp5.run_exp5 extract --env-file .env     # extraction by the thinking model, for its own card
  python -m exp5.run_exp5 audit   --env-file .env     # direct audits, 4 models x 2 prompts x 6 reports
  python -m exp5.run_exp5 grade   --env-file .env     # grader maps card bottlenecks to direct-audit checks
  python -m exp5.run_exp5 analyze                     # summary and a side-by-side file for human spot checks
"""
import argparse
import json
import random
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from evaudit.core import blocker, verification_bounds, verification_plan  # noqa: E402
from evaudit.llm import Budget, BudgetExceeded, call, last_object  # noqa: E402
from exp1.run_exp1 import load_key  # noqa: E402
from exp4.run_exp4 import EXTRACT_PROMPT, build, parse_json  # noqa: E402

JUDGES = ["anthropic/claude-haiku-4.5", "openai/gpt-4.1", "qwen/qwen3-235b-a22b-2507"]
THINKING = "qwen/qwen3-235b-a22b-thinking-2507"
GRADER = "google/gemini-2.5-flash"
PRICES = {THINKING: (0.45, 3.50)}
WORKERS = 2
DATA, RES = ROOT / "data" / "exp4", ROOT / "results"

PLAIN = (
    "You are auditing the AI-generated report below for a reader who must decide whether to rely on its main "
    "conclusion. List, in order of priority, the things the reader should check before relying on the conclusion. "
    "For each check, say exactly what to verify and where to look (which numbered reference, or which part of the "
    "report).\n")
PLAIN_FMT = ('Reply with JSON only: {{"conclusion": "...", "checks": [{{"n": 1, "check": "...", "where": "..."}}]}}'
             "\n\nReport:\n{report}")
STRONG = PLAIN + (
    "Then answer three questions about your checks.\n"
    "(a) Which checks, if that check alone turned out false, would leave the conclusion with no support at all?\n"
    "(b) If everything your checks verify holds, how many of the cited studies could turn out to be wrong with the "
    "conclusion still supported?\n"
    "(c) Which checks are enough, if all of them are confirmed, for the conclusion to stay supported even if any one "
    "cited study is wrong?\n")
STRONG_FMT = ('Reply with JSON only: {{"conclusion": "...", "checks": [{{"n": 1, "check": "...", "where": "..."}}], '
              '"alone_removes_support": [1], "studies_that_can_be_wrong": 0, "enough_for_one_wrong_study": [1]}}'
              "\n\nReport:\n{report}")
PROMPTS = {"plain": PLAIN + PLAIN_FMT, "strong": STRONG + STRONG_FMT}

GRADE = (
    "You are grading an audit of a report. Below are (1) a list of CONDITIONS, each an assumption the report's "
    "argument depends on, and (2) the numbered CHECKS that an auditor proposed.\n"
    "For each condition, list the numbers of the checks that ask the reader to verify that same assumption, or a "
    "narrower or broader version of it about the same objects (for example, the same population, dose, product or "
    "outcome). A check that only asks generally whether the evidence is good does not count. Use an empty list if no "
    "check matches.\n"
    'Reply with JSON only: {{"matches": [{{"id": "C1", "checks": [2]}}]}}\n\n'
    "CONDITIONS:\n{conds}\n\nCHECKS:\n{checks}")


def load(p):
    p = Path(p)
    return [json.loads(l) for l in open(p, encoding="utf-8")] if p.exists() else []


def last_rows(rows, key):
    d = {}
    for r in rows:
        d[key(r)] = r          # the last row per key wins (resumed runs)
    return d


def paths(mock):
    s = "_mock" if mock else ""
    d = {k: RES / f"exp5_{k}{s}.jsonl" for k in ("extract", "audit", "grade")}
    d.update(summary=RES / f"exp5_summary{s}.json", review=RES / f"exp5_review{s}.md")
    return d


def reports():
    rs = [r for r in load(DATA / "reports.jsonl") if r.get("report")]
    if len(rs) != 6:
        sys.exit(f"expected the six case-study reports in data/exp4/reports.jsonl, found {len(rs)}")
    return rs


def cards(mock):
    """Per (report, model): the card computed from that model's extraction (case study, or exp5 for THINKING)."""
    rows = last_rows(load(RES / "exp4_extract.jsonl") + load(paths(mock)["extract"]), lambda r: (r["id"], r["model"]))
    out = {}
    for (rid, m), r in rows.items():
        g = build(r["parsed"]) if r.get("parsed") else None
        if not g:
            continue
        W, R = g["W"], g["R"]
        single = sorted(c for c in R if frozenset({c}) in blocker(W))
        plan = verification_plan(W, R, 2)
        out[(rid, m)] = {"tau_S": verification_bounds(W, R, confirmed=R)[0],
                         "bottlenecks": [{"id": c[2:], "text": g["conds"].get(c[2:], "")} for c in single],
                         "plan_size": None if plan is None else len(plan[0])}
    return out


def run(jobs, work, out, label):
    n = stopped = 0
    with ThreadPoolExecutor(WORKERS) as ex, open(out, "a", encoding="utf-8") as f:
        for fu in [ex.submit(work, j) for j in jobs]:
            try:
                row = fu.result()
            except BudgetExceeded as e:
                stopped += 1
                if stopped == 1:
                    print("STOPPED:", e)
                continue
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            f.flush()
            n += 1
            print(f"{label} {n:3d} {row['id']:10s} {row['model']:40s} {row.get('prompt', '')} "
                  f"{'ok' if row['parsed'] else 'PARSE FAIL'}")
    print(f"{label}: {n} rows -> {out}; {stopped} calls skipped by the cap")


def mock_text(kind, rng, r=None, card=None):
    if kind == "extract":
        return json.dumps({"conclusion": "x", "references": [{"ref": 1, "underlying_study": "s1"},
                                                            {"ref": 2, "underlying_study": "s2"}],
                           "conditions": [{"id": "C1", "text": "population matches"}],
                           "unstated": [], "routes": [{"route": 1, "refs": [1], "conditions": ["C1"]},
                                                      {"route": 2, "refs": [2], "conditions": ["C1"]}]})
    if kind in ("plain", "strong"):
        d = {"conclusion": "x", "checks": [{"n": i, "check": f"check {i}", "where": "ref 1"} for i in (1, 2, 3)]}
        if kind == "strong":
            d.update(alone_removes_support=[1], studies_that_can_be_wrong=rng.choice([0, 1, 2]),
                     enough_for_one_wrong_study=[1, 2])
        return json.dumps(d)
    return json.dumps({"matches": [{"id": b["id"], "checks": [1] if rng.random() < .6 else []}
                                   for b in card["bottlenecks"]]})


def settings(m, a):
    """(temperature, max_tokens, reasoning) per model: the case-study judges as before, Qwen thinking at 0.6,
    models named with --models at the provider's default temperature and the given reasoning effort."""
    if m in JUDGES:
        return 0.0, 3000, None
    if m == THINKING:
        return 0.6, 24000, None
    return None, 24000, a.reasoning


def step_extract(a, P, key, budget, rng):
    models = a.models or [THINKING]
    done = {(r["id"], r["model"]) for r in load(P["extract"]) if r.get("parsed")}
    jobs = [(r, m) for m in models for r in reports() if (r["id"], m) not in done]

    def work(job):
        r, m = job
        if a.mock:
            text, usage = mock_text("extract", rng), {}
        else:
            temp, mt, reas = settings(m, a)
            text, usage = call(m, EXTRACT_PROMPT.format(report=r["report"]), key, budget, temp, mt,
                               fallback_price=PRICES.get(m), reasoning=reas)
        return {"id": r["id"], "model": m, "raw": text, "parsed": parse_json(text), "usage": usage}
    run(jobs, work, P["extract"], "extract")


def step_audit(a, P, key, budget, rng):
    done = {(r["id"], r["model"], r["prompt"]) for r in load(P["audit"]) if r.get("parsed")}
    models = a.models or JUDGES + [THINKING]
    jobs = [(r, m, p) for p in ("plain", "strong") for m in models for r in reports()
            if (r["id"], m, p) not in done]

    def work(job):
        r, m, p = job
        if a.mock:
            text, usage = mock_text(p, rng), {}
        else:
            temp, mt, reas = settings(m, a)
            text, usage = call(m, PROMPTS[p].format(report=r["report"]), key, budget, temp, mt,
                               fallback_price=PRICES.get(m), reasoning=reas)
        return {"id": r["id"], "model": m, "prompt": p, "raw": text, "parsed": last_object(text, "checks"),
                "usage": usage}
    run(jobs, work, P["audit"], "audit")


def step_grade(a, P, key, budget, rng):
    C = cards(a.mock)
    audits = last_rows(load(P["audit"]), lambda r: (r["id"], r["model"], r["prompt"]))
    done = {(r["id"], r["model"], r["prompt"]) for r in load(P["grade"]) if r.get("parsed")}
    jobs = [(k, r) for k, r in audits.items() if r.get("parsed") and (k[0], k[1]) in C
            and C[(k[0], k[1])]["bottlenecks"] and k not in done]

    def work(job):
        (rid, m, p), r = job
        card = C[(rid, m)]
        conds = "\n".join(f"{b['id']}: {b['text']}" for b in card["bottlenecks"])
        checks = "\n".join(f"{c.get('n')}: {c.get('check', '')} (where: {c.get('where', '')})"
                           for c in r["parsed"].get("checks", []))
        if a.mock:
            text, usage = mock_text("grade", rng, card=card), {}
        else:
            text, usage = call(GRADER, GRADE.format(conds=conds, checks=checks), key, budget, 0.0, 2000)
        return {"id": rid, "model": m, "prompt": p, "raw": text, "parsed": last_object(text, "matches"),
                "usage": usage}
    run(jobs, work, P["grade"], "grade")


def as_int_list(x):
    out = []
    for v in x if isinstance(x, list) else []:
        try:
            out.append(int(v))
        except (TypeError, ValueError):
            pass
    return out


def step_analyze(a, P):
    C = cards(a.mock)
    audits = last_rows(load(P["audit"]), lambda r: (r["id"], r["model"], r["prompt"]))
    grades = last_rows(load(P["grade"]), lambda r: (r["id"], r["model"], r["prompt"]))
    S, review = defaultdict(lambda: defaultdict(list)), ["# Experiment 5: direct audits next to the audit cards", "",
                                                        "For human spot checks of the grader. Bottlenecks come from "
                                                        "the card computed from the same model's extraction.", ""]
    for (rid, m, p), r in sorted(audits.items()):
        s = S[(m, p)]
        s["reports"].append(rid)
        if not r.get("parsed"):
            s["parse_fail"].append(rid)
            continue
        checks = r["parsed"].get("checks", []) or []
        s["n_checks"].append(len(checks))
        card = C.get((rid, m))
        if card is None:
            continue
        g = grades.get((rid, m, p), {}).get("parsed") or {}
        match = {str(x.get("id")): as_int_list(x.get("checks")) for x in g.get("matches", []) or []}
        B = card["bottlenecks"]
        if B and not g:
            s["grade_missing"].append(rid)
        covered = [b["id"] for b in B if match.get(b["id"])]
        s["bottlenecks"].append(len(B))
        s["covered"].append(len(covered))
        if p == "strong":
            pr = r["parsed"]
            alone = set(as_int_list(pr.get("alone_removes_support")))
            enough = set(as_int_list(pr.get("enough_for_one_wrong_study")))
            s["flagged"].append(sum(1 for b in B if set(match.get(b["id"], [])) & alone))
            if B:
                s["enough_given"].append(bool(enough))
                s["enough_contains_all"].append(bool(enough) and all(set(match.get(b["id"], [])) & enough for b in B))
                s["enough_size"].append(len(enough))
                s["card_plan_size"].append(card["plan_size"])
            try:
                stated = int(pr.get("studies_that_can_be_wrong"))
            except (TypeError, ValueError):
                stated = None
            t = card["tau_S"]
            truth = None if t == float("inf") else int(t) - 1
            s["tolerance"].append((stated, truth))
        review += [f"## {rid} / {m} / {p}", "", "Card bottlenecks: " + ("; ".join(
            f"{b['id']} ({b['text']}) -> checks {match.get(b['id'], [])}" for b in B) or "none"), ""]
        review += [f"{c.get('n')}. {c.get('check', '')} [where: {c.get('where', '')}]" for c in checks]
        if p == "strong":
            pr = r["parsed"]
            review += ["", f"alone_removes_support={pr.get('alone_removes_support')}; "
                           f"studies_that_can_be_wrong={pr.get('studies_that_can_be_wrong')} "
                           f"(card: tau_S-1={None if card['tau_S'] == float('inf') else int(card['tau_S']) - 1}); "
                           f"enough_for_one_wrong_study={pr.get('enough_for_one_wrong_study')} "
                           f"(card plan size {card['plan_size']})"]
        review.append("")
    summary, lines = {}, []
    for (m, p), s in sorted(S.items()):
        tol = s.get("tolerance", [])
        d = {"reports": len(s["reports"]), "parse_fail": len(s["parse_fail"]),
             "grade_missing": len(s.get("grade_missing", [])),
             "mean_checks": round(sum(s["n_checks"]) / len(s["n_checks"]), 1) if s["n_checks"] else None,
             "bottlenecks": sum(s["bottlenecks"]), "covered": sum(s["covered"])}
        if p == "strong":
            d.update(flagged=sum(s["flagged"]),
                     enough_given=f"{sum(s['enough_given'])}/{len(s['enough_given'])}",
                     enough_contains_all_bottlenecks=f"{sum(s['enough_contains_all'])}/{len(s['enough_contains_all'])}",
                     tolerance_exact=f"{sum(1 for x, y in tol if x is not None and x == y)}/{len(tol)}",
                     tolerance_over=sum(1 for x, y in tol if x is not None and y is not None and x > y),
                     tolerance_under=sum(1 for x, y in tol if x is not None and y is not None and x < y),
                     tolerance_pairs=tol)
        summary[f"{m} | {p}"] = d
        lines.append(f"{m:40s} {p:6s} checks {d['mean_checks']}; bottlenecks covered {d['covered']}/{d['bottlenecks']}"
                     + (f"; flagged as single point {d['flagged']}/{d['bottlenecks']}; enough-set contains all "
                        f"bottlenecks {d['enough_contains_all_bottlenecks']}; tolerance exact {d['tolerance_exact']} "
                        f"(over {d['tolerance_over']}, under {d['tolerance_under']})" if p == "strong" else "")
                     + (f"; parse failures {d['parse_fail']}" if d["parse_fail"] else "")
                     + (f"; ungraded {d['grade_missing']}" if d["grade_missing"] else ""))
    json.dump(summary, open(P["summary"], "w"), indent=1, default=str)
    Path(P["review"]).write_text("\n".join(review) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"-> {P['summary']}, {P['review']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["extract", "audit", "grade", "analyze"])
    ap.add_argument("--env-file")
    ap.add_argument("--max-usd", type=float, default=0.60, help="cap for this step")
    ap.add_argument("--models", nargs="+", help="extract/audit: models to run (default: the original set)")
    ap.add_argument("--reasoning", default="medium", help="reasoning effort for models named with --models")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--mock", action="store_true")
    a = ap.parse_args()
    global WORKERS
    WORKERS = a.workers
    P = paths(a.mock)
    if a.step == "analyze":
        return step_analyze(a, P)
    key = None if a.mock else load_key(a.env_file)
    budget, rng = Budget(a.max_usd), random.Random(0)
    {"extract": step_extract, "audit": step_audit, "grade": step_grade}[a.step](a, P, key, budget, rng)
    print(f"spent ${budget.spent:.3f} (cap ${a.max_usd:.2f})")


if __name__ == "__main__":
    main()
