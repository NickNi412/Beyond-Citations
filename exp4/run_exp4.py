"""Experiment 4 — case study on real AI-generated reports.

Step 1 (reports): a search-enabled model writes a short cited report for each question.
Step 2 (extract): each judge reads the report and returns its routes as sets of references and conditions,
                  the study each reference ultimately reports, and premises every route needs but the report
                  does not state. Nothing is scored by the model.
Step 3 (cards):   the program computes, per report and judge, source resilience, the interval with every
                  condition unresolved, the full set of minimal failure certificates and the audit questions.

  python -m exp4.run_exp4 reports --model perplexity/sonar-pro --env-file .env
  python -m exp4.run_exp4 extract --models A B C --env-file .env
  python -m exp4.run_exp4 cards
Add --mock to test without API calls. Outputs go to data/exp4/ and results/exp4_*.
"""
import argparse
import json
import random
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from evaudit.core import audit_card, minimal_sets, verification_plan  # noqa: E402
from exp1.run_exp1 import load_key  # noqa: E402

URL = "https://openrouter.ai/api/v1/chat/completions"
DATA = ROOT / "data" / "exp4"
RES = ROOT / "results"
PREFIX = "exp4"


def use_mock_paths():
    """Offline test runs write to separate files, so they can never mix with real results."""
    global DATA, PREFIX
    DATA = ROOT / "data" / "exp4_mock"
    PREFIX = "exp4_mock"

REPORT_PROMPT = (
    "Write a short evidence report (400-700 words) answering the question below for an informed reader. "
    "Search the literature. State one main conclusion in the first sentence. Support it with the evidence you "
    "found, citing sources inline as [1], [2], ... End with a numbered reference list giving, for each "
    "reference, its title, its authors or organisation, its year and its URL.\n\nQuestion: {question}"
)

EXTRACT_PROMPT = (
    "You are auditing the argument of the report below. Do not judge whether the conclusion is true; only "
    "record how the report supports it.\n"
    "1. State the report's main conclusion in one sentence.\n"
    "2. For each numbered reference, give the original study or dataset it ultimately reports (for example "
    "'Martineau 2017 meta-analysis' or 'UK BEIS 2021 field trial'). If two references report the same study, "
    "give them the same name. If you cannot tell, write 'unknown'.\n"
    "3. List the conditions the argument relies on: assumptions that a step needs and that a person could "
    "check, such as that a tested population, product or setting matches the one in the conclusion, or that a "
    "cited result transfers to a different dose, scale or period. Two conditions are the same only if they "
    "assert the same thing about the same objects, whatever the wording; give each distinct condition one id "
    "(C1, C2, ...).\n"
    "4. List the routes: each route is a minimal set of references that, together with its conditions, the "
    "report uses to support the conclusion on its own. A reference may appear in several routes.\n"
    "5. List premises that every route needs but the report never states (empty list if none). Give each an id "
    "U1, U2, ... and add it to the conditions of every route that needs it.\n"
    'Reply with JSON only, no comments: {{"conclusion": "...", '
    '"references": [{{"ref": 1, "underlying_study": "..."}}], '
    '"conditions": [{{"id": "C1", "text": "..."}}], '
    '"unstated": [{{"id": "U1", "text": "..."}}], '
    '"routes": [{{"route": 1, "refs": [1, 3], "conditions": ["C1", "U1"], "summary": "..."}}]}}\n\n'
    "Report:\n{report}"
)


def post(model, prompt, key, max_tokens, temperature=0.0, tries=5):
    import requests
    body = {"model": model, "temperature": temperature, "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}]}
    err = "no response"
    for i in range(tries):
        try:
            r = requests.post(URL, headers={"Authorization": f"Bearer {key}"}, json=body, timeout=300)
            if r.status_code == 200:
                return r.json()
            if r.status_code in (429, 500, 502, 503, 504):
                time.sleep(2 ** i)
                continue
            return {"error": f"HTTP {r.status_code}: {r.text[:300]}"}
        except Exception as e:  # noqa: BLE001
            err = repr(e)
            time.sleep(2 ** i)
    return {"error": err}


def parse_json(text):
    dec, objs, i = json.JSONDecoder(), [], 0
    text = text or ""
    while True:
        j = text.find("{", i)
        if j < 0:
            break
        try:
            o, end = dec.raw_decode(text, j)
            objs.append(o)
            i = end
        except json.JSONDecodeError:
            i = j + 1
    objs = [o for o in objs if isinstance(o, dict) and "routes" in o]
    return objs[-1] if objs else None


def load_jsonl(p):
    p = Path(p)
    return [json.loads(l) for l in open(p, encoding="utf-8")] if p.exists() else []


# ---------------------------------------------------------------- step 1
MOCK_REPORT = (
    "Supplementation modestly reduces infections in deficient adults [1][2][3]. A meta-analysis of trials found a "
    "12% reduction [1]; a news summary of the same meta-analysis reports the same figure [2]. A separate cohort "
    "found lower infection rates at higher serum levels [3], assuming serum levels reflect supplementation.\n\n"
    "References\n1. Meta-analysis, Martineau et al., 2017, https://example.org/a\n"
    "2. News article on Martineau 2017, Health News, 2017, https://example.org/b\n"
    "3. Cohort study, Ginde et al., 2009, https://example.org/c\n"
)


def step_reports(a):
    topics = json.load(open(ROOT / "exp4" / "topics.json", encoding="utf-8"))
    if a.n:
        topics = topics[: a.n]
    DATA.mkdir(parents=True, exist_ok=True)
    out = DATA / "reports.jsonl"
    done = {r["id"] for r in load_jsonl(out) if r.get("report") and r["report"] != MOCK_REPORT}
    key = None if a.mock else load_key(a.env_file)
    with open(out, "a", encoding="utf-8") as f:
        for t in topics:
            if t["id"] in done:
                continue
            if a.mock:
                j = {"choices": [{"message": {"content": MOCK_REPORT}}], "usage": {}}
            else:
                j = post(a.model, REPORT_PROMPT.format(question=t["question"]), key, max_tokens=2500, temperature=0.3)
            if "error" in j:
                print(t["id"], j["error"])
                continue
            msg = j["choices"][0]["message"]
            row = {"id": t["id"], "question": t["question"], "model": a.model, "report": msg.get("content", ""),
                   "citations": j.get("citations") or msg.get("annotations"), "usage": j.get("usage", {})}
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            f.flush()
            print(t["id"], len(row["report"]), "chars")


# ---------------------------------------------------------------- step 2
def mock_extract(report, rng):
    return json.dumps({
        "conclusion": "Supplementation modestly reduces infections in deficient adults.",
        "references": [{"ref": 1, "underlying_study": "Martineau 2017 meta-analysis"},
                       {"ref": 2, "underlying_study": "Martineau 2017 meta-analysis"},
                       {"ref": 3, "underlying_study": "Ginde 2009 cohort"}],
        "conditions": [{"id": "C1", "text": "serum levels reflect supplementation"}],
        "unstated": [{"id": "U1", "text": "trial populations resemble the adults in the conclusion"}],
        "routes": [{"route": 1, "refs": [1], "conditions": ["U1"]}, {"route": 2, "refs": [2], "conditions": ["U1"]},
                   {"route": 3, "refs": [3], "conditions": ["C1", "U1"]}]})


def step_extract(a):
    reports = [r for r in load_jsonl(DATA / "reports.jsonl") if r.get("report")]
    if not a.mock and any(r["report"] == MOCK_REPORT for r in reports):
        sys.exit("data/exp4/reports.jsonl contains the offline test report; remove that line first.")
    out = RES / f"{PREFIX}_extract.jsonl"
    RES.mkdir(exist_ok=True)
    done = {(r["id"], r["model"]) for r in load_jsonl(out) if r.get("parsed")}
    jobs = [(r, m) for r in reports for m in a.models if (r["id"], m) not in done]
    key = None if a.mock else load_key(a.env_file)
    rng = random.Random(0)

    def work(job):
        r, m = job
        if a.mock:
            text, usage = mock_extract(r["report"], rng), {}
        else:
            j = post(m, EXTRACT_PROMPT.format(report=r["report"]), key, max_tokens=3000)
            text = j["choices"][0]["message"]["content"] if "choices" in j else j.get("error")
            usage = j.get("usage", {})
        return {"id": r["id"], "model": m, "raw": text, "parsed": parse_json(text), "usage": usage}

    with ThreadPoolExecutor(a.workers) as ex, open(out, "a", encoding="utf-8") as f:
        for row in ex.map(work, jobs):
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            f.flush()
            print(row["id"], row["model"], "ok" if row["parsed"] else "PARSE FAIL")


# ---------------------------------------------------------------- step 3
def norm(s):
    s = re.sub(r"[^a-z0-9 ]", " ", str(s).lower())
    return " ".join(s.split())


def build(p):
    """Witnesses over sources and conditions from one extraction. Returns None if malformed."""
    try:
        study = {int(x["ref"]): norm(x.get("underlying_study", "unknown")) for x in p.get("references", [])}
        conds = {str(c["id"]): c.get("text", "") for c in p.get("conditions", []) + p.get("unstated", [])}
        W, unknown = [], set()
        for r in p["routes"]:
            srcs = set()
            for ref in r.get("refs", []):
                ref = int(ref)
                s = study.get(ref, "unknown")
                if s in ("", "unknown", "unclear", "not stated"):
                    unknown.add(ref)
                    s = f"ref{ref}"           # not established: kept as its own source and flagged
                srcs.add("S:" + s)
            cs = {"R:" + str(c) for c in r.get("conditions", [])}
            if srcs:
                W.append(frozenset(srcs | cs))
    except (KeyError, TypeError, ValueError):
        return None
    if not W:
        return None
    W = minimal_sets(W)
    R = {x for w in W for x in w if x.startswith("R:")}
    return {"W": W, "R": R, "conds": conds, "unknown_refs": sorted(unknown),
            "n_refs": len(study), "n_routes": len(p["routes"]),
            "n_sources": len({x for w in W for x in w if x.startswith("S:")})}


def fmt(x):
    return "inf" if x == float("inf") else str(int(x))


def step_cards(a):
    reports = {r["id"]: r for r in load_jsonl(DATA / "reports.jsonl")}
    rows = {}
    for r in load_jsonl(RES / f"{PREFIX}_extract.jsonl"):
        rows[(r["id"], r["model"])] = r            # last row per key wins
    cards, md = [], ["# Experiment 4: audit cards for real AI-generated reports", "",
                     "Computed by the program from each judge's extraction. Nothing here has been checked by a person yet.", ""]
    for rid in reports:
        md += [f"## {rid}: {reports[rid]['question']}", ""]
        for (i, m), r in sorted(rows.items()):
            if i != rid:
                continue
            p = r.get("parsed")
            g = build(p) if p else None
            if g is None:
                md += [f"### {m}", "", "extraction could not be used", ""]
                cards.append({"id": rid, "model": m, "ok": False})
                continue
            c = audit_card(g["W"], g["R"])
            plan = verification_plan(g["W"], g["R"], 2)
            L, H = c["interval"]
            rec = {"id": rid, "model": m, "ok": True, "conclusion": p.get("conclusion"),
                   "n_refs": g["n_refs"], "n_routes": g["n_routes"], "n_sources": g["n_sources"],
                   "tau_S": c["source_only_tau"], "interval": [L, H],
                   "certificates": c["failure_certificates"], "condition_bottlenecks": c["condition_bottlenecks"],
                   "unknown_refs": g["unknown_refs"], "n_unstated": len(p.get("unstated", []) or []),
                   "plan_k2": None if plan is None else [x[2:] for x in plan[0]],
                   "questions": [{"condition": q["condition"], "text": g["conds"].get(q["condition"][2:], ""),
                                  "routes": q["routes_using_it"], "if_confirmed": q["if_confirmed"],
                                  "if_rejected": q["if_rejected"]} for q in c["questions"]]}
            cards.append(rec)
            md += [f"### {m}", "",
                   f"- Conclusion: {rec['conclusion']}",
                   f"- References cited: {rec['n_refs']}; routes: {rec['n_routes']}; distinct sources in routes: {rec['n_sources']}",
                   f"- Source resilience if all conditions hold: {fmt(rec['tau_S'])}",
                   f"- Interval with every condition unresolved: [{fmt(L)}, {fmt(H)}]",
                   f"- Minimal failure certificates ({len(rec['certificates'])}): " + "; ".join(
                       "{" + ", ".join(x[2:] for x in k) + "}" for k in rec["certificates"][:12])
                   + (" ..." if len(rec["certificates"]) > 12 else ""),
                   f"- Single-condition bottlenecks: " + (", ".join(
                       f"{k[0][2:]} ({g['conds'].get(k[0][2:], '')})" for k in rec["condition_bottlenecks"]) or "none"),
                   f"- References whose study could not be identified (kept separate): {rec['unknown_refs'] or 'none'}",
                   f"- Unstated premises proposed: {rec['n_unstated']}",
                   "- Checklist to survive any one incorrect source (minimum 2-plan): " + (
                       "unreachable" if rec["plan_k2"] is None else ", ".join(
                           f"{x} ({g['conds'].get(x, '')})" for x in rec["plan_k2"])), ""]
            for q in rec["questions"][:8]:
                md.append(f"  - check {q['condition'][2:]} ({q['text']}): used by {q['routes']} route(s); "
                          f"if confirmed [{fmt(q['if_confirmed'][0])}, {fmt(q['if_confirmed'][1])}], "
                          f"if rejected [{fmt(q['if_rejected'][0])}, {fmt(q['if_rejected'][1])}]")
            md.append("")
    # cross-judge agreement
    md += ["## Agreement across judges", "", "| report | refs | tau_S per judge | bottleneck found per judge |", "|---|---|---|---|"]
    summ = []
    for rid in reports:
        cs = [c for c in cards if c["id"] == rid and c["ok"]]
        taus = [fmt(c["tau_S"]) for c in cs]
        bott = ["yes" if c["condition_bottlenecks"] else "no" for c in cs]
        refs = max([c["n_refs"] for c in cs], default=0)
        md.append(f"| {rid} | {refs} | {', '.join(taus)} | {', '.join(bott)} |")
        summ.append({"id": rid, "refs": refs, "tau": taus, "bottleneck": bott,
                     "tau_agree": len(set(taus)) == 1 and len(taus) > 1})
    RES.mkdir(exist_ok=True)
    (RES / f"{PREFIX}_cards.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    json.dump({"cards": cards, "summary": summ}, open(RES / f"{PREFIX}_cards.json", "w"), indent=1, default=str)
    print("\n".join(md[-(len(reports) + 3):]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["reports", "extract", "cards"])
    ap.add_argument("--model", default="perplexity/sonar-pro")
    ap.add_argument("--models", nargs="+", default=["MOCK"])
    ap.add_argument("--env-file")
    ap.add_argument("--n", type=int, default=0)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--mock", action="store_true", help="offline test; writes data/exp4_mock/ and results/exp4_mock_*")
    a = ap.parse_args()
    if a.mock:
        use_mock_paths()
    {"reports": step_reports, "extract": step_extract, "cards": step_cards}[a.step](a)


if __name__ == "__main__":
    main()
