"""Experiment 9 — do single-condition bottlenecks survive when conditions are stated per study?

A condition such as "the cited studies used valid kidney measurements" is a claim about each study. Treated as one
proposition, it fails as soon as one study fails it, and so can create a single point of failure that the evidence
does not have. This script labels every extracted condition as
  each_study : it attributes a property to the cited studies, trials or sources, so it can hold for one and fail for
               another (population, method, measurement, dose, duration, quality ...);
  single     : one proposition about the conclusion, a definition, a product or a transfer step, true or false as a
               whole whichever study is cited.
It then splits every each_study condition into one condition per study on each route that uses it, recomputes the
cards, and reports what changes.

  python -m exp9.split_conditions classify --env-file .env --files results/exp4_extract.jsonl results/exp5_extract.jsonl
  python -m exp9.split_conditions analyze  --files results/exp4_extract.jsonl results/exp5_extract.jsonl
Add --mock for an offline test (labels at random, writes *_mock files).
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
from evaudit.core import minimal_sets, restrict, verification_bounds, verification_plan  # noqa: E402
from evaudit.llm import Budget, BudgetExceeded, call, last_object  # noqa: E402
from exp4.run_exp4 import norm  # noqa: E402

RES = ROOT / "results"
CLASSIFIER = "openai/gpt-6.1-sol"
FRONTIER = ["anthropic/claude-opus-5.5", "google/gemini-3.1-pro-preview", "openai/gpt-6.1-sol"]
INF = float("inf")

PROMPT = (
    "Below are the conditions that an argument relies on, each with the references of the routes that use it. For "
    "each condition, decide its scope.\n"
    "each_study: the condition attributes a property to the cited studies, trials, reviews, sources or their "
    "participants, methods, measurements, doses, durations or quality, so that it could hold for one cited study and "
    "fail for another.\n"
    "single: the condition is one proposition that is true or false as a whole whichever study is cited, for "
    "example about the conclusion's wording or scope, a definition, a product's identity, or whether a result "
    "transfers from one setting to another.\n"
    "If a condition mixes both, choose each_study.\n"
    'Reply with JSON only: {{"scopes": [{{"id": "C1", "scope": "each_study"}}]}}\n\n'
    "Conclusion: {conclusion}\n\nConditions:\n{conds}")


def load(p):
    p = Path(p)
    return [json.loads(l) for l in open(p, encoding="utf-8")] if p.exists() else []


def rows_of(files):
    out = {}
    for f in files:
        for r in load(ROOT / f if not Path(f).is_absolute() else f):
            if r.get("parsed"):
                out[(Path(f).name, r["id"], r["model"])] = r
    return out


def conditions(p):
    conds = {str(c["id"]): c.get("text", "") for c in p.get("conditions", []) + p.get("unstated", [])}
    used = defaultdict(set)
    for r in p.get("routes", []):
        for c in r.get("conditions", []):
            used[str(c)].update(int(x) for x in r.get("refs", []))
    return {c: (t, sorted(used.get(c, []))) for c, t in conds.items() if c in used}


def structure(p, scope=None):
    """Witnesses over 'S:' study atoms and 'R:' condition atoms; each_study conditions split per study if scope."""
    study = {}
    for x in p.get("references", []):
        s = norm(x.get("underlying_study", "unknown"))
        study[int(x["ref"])] = f"ref{int(x['ref'])}" if s in ("", "unknown", "unclear", "not stated") else s
    W = []
    for r in p["routes"]:
        srcs = {study.get(int(x), f"ref{int(x)}") for x in r.get("refs", [])}
        if not srcs:
            continue
        cs = set()
        for c in map(str, r.get("conditions", [])):
            if scope and scope.get(c) == "each_study":
                cs.update(f"R:{c}@{s}" for s in srcs)
            else:
                cs.add(f"R:{c}")
        W.append(frozenset({"S:" + s for s in srcs} | cs))
    W = minimal_sets(W)
    R = {x for w in W for x in w if x.startswith("R:")}
    return W, R


def card(W, R):
    t = verification_bounds(W, R, confirmed=R)[0]
    bott = sorted(c for c in R if not restrict(W, false={c}))
    plan = verification_plan(W, R, 2) if len(R) <= 14 else "skipped"   # enumeration grows fast with |R|
    return {"tol": None if t == INF else int(t) - 1, "bottlenecks": bott,
            "plan": plan if plan in (None, "skipped") else len(plan[0])}


def step_classify(a):
    from exp1.run_exp1 import load_key
    rows = rows_of(a.files)
    out = RES / f"exp9_scope{'_mock' if a.mock else ''}.jsonl"
    done = {(r["file"], r["id"], r["model"]) for r in load(out) if r.get("parsed")}
    jobs = [(k, r) for k, r in rows.items() if k not in done]
    key = None if a.mock else load_key(a.env_file)
    budget, rng = Budget(a.max_usd), random.Random(0)

    def work(job):
        (f, rid, m), r = job
        cs = conditions(r["parsed"])
        text = "\n".join(f"{c}: {t} (routes using refs {refs})" for c, (t, refs) in cs.items())
        if a.mock:
            raw = json.dumps({"scopes": [{"id": c, "scope": rng.choice(["each_study", "single"])} for c in cs]})
            usage = {}
        else:
            raw, usage = call(CLASSIFIER, PROMPT.format(conclusion=r["parsed"].get("conclusion", ""), conds=text),
                              key, budget, None, 8000, reasoning="low")
        return {"file": f, "id": rid, "model": m, "raw": raw, "parsed": last_object(raw, "scopes"), "usage": usage}

    n = stopped = 0
    with ThreadPoolExecutor(a.workers) as ex, open(out, "a", encoding="utf-8") as fh:
        for fu in [ex.submit(work, j) for j in jobs]:
            try:
                row = fu.result()
            except BudgetExceeded as e:
                stopped += 1
                if stopped == 1:
                    print("STOPPED:", e)
                continue
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            n += 1
            print(f"{n:3d} {row['file']:22s} {row['id']:10s} {row['model']:38s} "
                  f"{'ok' if row['parsed'] else 'PARSE FAIL'}")
    print(f"{n} rows -> {out}; {stopped} skipped by the cap; spent ${budget.spent:.3f}")


def step_analyze(a):
    rows = rows_of(a.files)
    scopes = {}
    for r in load(RES / f"exp9_scope{'_mock' if a.mock else ''}.jsonl"):
        if r.get("parsed"):
            scopes[(r["file"], r["id"], r["model"])] = {str(x.get("id")): x.get("scope")
                                                       for x in r["parsed"].get("scopes", [])}
    # free audits of Experiment 5 (strong prompt) and their grades, to recount what the audits name
    from exp5.run_exp5 import as_int_list
    audits = {(r["id"], r["model"]): r for r in load(RES / "exp5_audit.jsonl") if r.get("prompt") == "strong"}
    grades = {(r["id"], r["model"]): r for r in load(RES / "exp5_grade.jsonl") if r.get("prompt") == "strong"}
    S = defaultdict(lambda: defaultdict(int))
    review = ["# Experiment 9: condition scopes, for spot checks", ""]
    for (f, rid, m), r in sorted(rows.items()):
        sc = scopes.get((f, rid, m))
        if sc is None:
            continue
        p = r["parsed"]
        W0, R0 = structure(p)
        W1, R1 = structure(p, sc)
        c0, c1 = card(W0, R0), card(W1, R1)
        g = S[(f, m)]
        cs = conditions(p)
        g["cards"] += 1
        g["conditions"] += len(cs)
        g["each_study"] += sum(sc.get(c) == "each_study" for c in cs)
        g["bott_before"] += len(c0["bottlenecks"])
        g["bott_after"] += len(c1["bottlenecks"])
        g["cards_with_bott_before"] += bool(c0["bottlenecks"])
        g["cards_with_bott_after"] += bool(c1["bottlenecks"])
        g["plan_changed"] += c0["plan"] != c1["plan"] and "skipped" not in (c0["plan"], c1["plan"])
        if m in FRONTIER and (rid, m) in audits and audits[(rid, m)].get("parsed"):
            pr = audits[(rid, m)]["parsed"]
            alone = set(as_int_list(pr.get("alone_removes_support")))
            match = {str(x.get("id")): as_int_list(x.get("checks"))
                     for x in ((grades.get((rid, m)) or {}).get("parsed") or {}).get("matches", []) or []}
            after = sorted({b[2:].split("@")[0] for b in c1["bottlenecks"]})
            if after:
                g["audits_with_bott_after"] += 1
                g["said_none_after"] += int(not alone)
                g["named_after"] += sum(1 for b in after if set(match.get(b, [])) & alone)
                g["bott_ids_after"] += len(after)
            st = pr.get("studies_that_can_be_wrong")
            try:
                st = int(st)
            except (TypeError, ValueError):
                st = None
            g["tol_over"] += int(st is not None and c1["tol"] is not None and st > c1["tol"])
            g["tol_exact"] += int(st is not None and st == c1["tol"])
        review += [f"## {f} / {rid} / {m}", f"bottlenecks before {c0['bottlenecks']} -> after {c1['bottlenecks']}; "
                   f"plan {c0['plan']} -> {c1['plan']}"]
        review += [f"- {c} [{sc.get(c)}]: {t}" for c, (t, _) in cs.items()]
        review.append("")
    lines, summary = [], {}
    for (f, m), g in sorted(S.items()):
        d = dict(g)
        summary[f"{f} | {m}"] = d
        s = (f"{f:22s} {m:38s} cards {g['cards']}; each_study {g['each_study']}/{g['conditions']}; bottlenecks "
             f"{g['bott_before']} -> {g['bott_after']}; cards with a bottleneck {g['cards_with_bott_before']} -> "
             f"{g['cards_with_bott_after']}; plan size changed on {g['plan_changed']}")
        if g.get("audits_with_bott_after") is not None and m in FRONTIER:
            s += (f" | free audit, against split cards: said none on {g['said_none_after']}/"
                  f"{g['audits_with_bott_after']}; named {g['named_after']}/{g['bott_ids_after']}; "
                  f"tolerance over {g['tol_over']}, exact {g['tol_exact']}")
        lines.append(s)
    suf = "_mock" if a.mock else ""
    json.dump(summary, open(RES / f"exp9_summary{suf}.json", "w"), indent=1)
    (RES / f"exp9_review{suf}.md").write_text("\n".join(review) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"-> {RES / f'exp9_summary{suf}.json'}, {RES / f'exp9_review{suf}.md'}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["classify", "analyze"])
    ap.add_argument("--files", nargs="+", default=["results/exp4_extract.jsonl", "results/exp5_extract.jsonl"])
    ap.add_argument("--env-file")
    ap.add_argument("--max-usd", type=float, default=1.0)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--mock", action="store_true")
    a = ap.parse_args()
    {"classify": step_classify, "analyze": step_analyze}[a.step](a)


if __name__ == "__main__":
    main()
