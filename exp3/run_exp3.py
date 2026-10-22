"""Experiment 3 — runner. Tasks per item and model:
  direct        : the model names the conditions, every minimal failure set, and any single point of failure
  direct_ex     : as direct, with definitions and a worked example from an unrelated domain
  extract       : the model only lists, for each route, the studies and conditions it uses (we compute the rest)
  extract_model : the model lists the routes and then computes the failure sets itself; we also compute them
                  from its own routes, which separates extraction errors from computation errors

  python -m exp3.run_exp3 --models A B C --env-file .env --out results/exp3.jsonl [--dry-run|--mock]
"""
import argparse
import json
import random
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from exp1.run_exp1 import call, load_key

COMMON = (
    "Treat each cited study as a source that could turn out to be wrong, and each assumption stated in the "
    "reasoning as a condition that could turn out to be false. Two stated assumptions are the same condition only "
    "if they assert the same thing about the same objects, whatever the wording; give each distinct condition one id "
    "(C1, C2, ...). Refer to studies by their letter (A, B, C).\n\n"
)
# Definitions and a worked example from an unrelated domain, with a structure not used in the items
# (one route has two conditions), so the example does not hand over an answer template.
DEFS = (
    "Definitions. A route needs ALL of its studies and conditions; the claim survives while at least one route has "
    "nothing failed. A failure set is a set of studies and/or conditions that, if all failed, leaves NO route intact; "
    "it is minimal if no smaller subset does so. A failure set must therefore hit every route. Listing what each "
    "route needs is not the same thing.\n"
    "Worked example (different topic). Claim: bridge X carries 40 t. Route 1 uses Study P and assumes K1 (the steel "
    "grade is S355). Route 2 uses Study Q and assumes K1 and K2 (the load test was static). "
    "Routes: {{P, K1}} and {{Q, K1, K2}}. Minimal failure sets: {{K1}}, {{P, Q}}, {{P, K2}}. "
    "Single point of failure: K1. Wrong answer: {{P, K1}}, {{Q, K1, K2}} (these are the routes, not failure sets).\n\n"
)

PROMPTS = {
    "direct": COMMON + (
        "Then list every minimal failure set: a set of studies and/or condition ids such that, if all of them failed, "
        "no route to the claim would remain, and no smaller subset would do. Finally say whether one single study or "
        "condition, failing alone, would leave the claim with no remaining route.\n"
        'Reply with JSON only, no comments: {{"conditions": [{{"id": "C1", "text": "...", "routes": [1, 2]}}], '
        '"failure_sets": [["A", "C1"]], "single_point_of_failure": "C1 or a study letter or none"}}\n\n{report}'),
    "direct_ex": COMMON + DEFS + (
        "Now do the same for the report below. List every minimal failure set, and say whether one single study or "
        "condition, failing alone, would leave the claim with no remaining route.\n"
        'Reply with JSON only, no comments: {{"conditions": [{{"id": "C1", "text": "...", "routes": [1, 2]}}], '
        '"failure_sets": [["A", "C1"]], "single_point_of_failure": "C1 or a study letter or none"}}\n\n{report}'),
    "extract_model": COMMON + (
        "First list, for each route, the studies and conditions it uses. Then, using only those routes, list every "
        "minimal failure set: a set of studies and/or condition ids such that, if all of them failed, no route to the "
        "claim would remain, and no smaller subset would do. Finally say whether one single study or condition, "
        "failing alone, would leave the claim with no remaining route.\n"
        'Reply with JSON only, no comments: {{"conditions": [{{"id": "C1", "text": "..."}}], '
        '"routes": [{{"route": 1, "studies": ["A"], "conditions": ["C1"]}}], '
        '"failure_sets": [["A", "C1"]], "single_point_of_failure": "C1 or a study letter or none"}}\n\n{report}'),
    "extract": COMMON + (
        "Only extract the structure. Do not assess robustness.\n"
        'Reply with JSON only, no comments: {{"conditions": [{{"id": "C1", "text": "..."}}], '
        '"routes": [{{"route": 1, "studies": ["A"], "conditions": ["C1"]}}]}}\n\n{report}'),
}


def parse(text):
    m = re.search(r"\{.*\}", text or "", re.S)
    if not m:
        return None
    raw = m.group(0)
    for cand in (raw, re.sub(r'(?m)\s*//[^\n"]*$', "", raw)):
        try:
            return json.loads(cand)
        except json.JSONDecodeError:
            continue
    # Some answers revise themselves ("Wait, let me reconsider") and give a second JSON object: keep the last one.
    dec, objs, i = json.JSONDecoder(), [], 0
    while True:
        j = text.find("{", i)
        if j < 0:
            break
        try:
            obj, end = dec.raw_decode(text, j)
            objs.append(obj)
            i = end
        except json.JSONDecodeError:
            i = j + 1
    objs = [o for o in objs if isinstance(o, dict) and ("routes" in o or "failure_sets" in o)]
    return objs[-1] if objs else None


def mock(item, task, rng):
    """Pipeline test only. Extraction is correct except that paraphrased shared conditions are split 30% of the
    time; direct answers always report no single point of failure (a counting-style judge)."""
    routes = item["routes"]
    ids = {}
    for r in routes:
        key = r["condition"]
        if item["variant"] == "shared_para" and rng.random() < .3:
            key = f'{key}-{r["route"]}'
        ids.setdefault(key, f"C{len(ids) + 1}")
    conds = [{"id": v, "text": k, "routes": [r["route"] for r in routes if ids.get(r["condition"]) == v or
                                             ids.get(f'{r["condition"]}-{r["route"]}') == v]} for k, v in ids.items()]
    if task in ("extract", "extract_model"):
        rr = [{"route": r["route"], "studies": r["studies"],
               "conditions": [ids.get(f'{r["condition"]}-{r["route"]}', ids.get(r["condition"]))]} for r in routes]
        d = {"conditions": conds, "routes": rr}
        if task == "extract_model":
            d.update(failure_sets=[[s for r in routes for s in r["studies"][:1]]], single_point_of_failure="none")
        return json.dumps(d)
    return json.dumps({"conditions": conds, "failure_sets": [[s for r in routes for s in r["studies"][:1]]],
                       "single_point_of_failure": "none"})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/exp3/items.jsonl")
    ap.add_argument("--models", nargs="+", default=["MOCK"])
    ap.add_argument("--tasks", nargs="+", default=["direct", "direct_ex", "extract", "extract_model"])
    ap.add_argument("--n", type=int, default=0, help="use only the first n items (0 = all)")
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--env-file")
    ap.add_argument("--out", default="results/exp3.jsonl")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--mock", action="store_true")
    a = ap.parse_args()
    items = [json.loads(l) for l in open(a.data, encoding="utf-8")]
    if a.n:
        items = items[: a.n]
    jobs = [(it, m, t) for it in items for m in a.models for t in a.tasks]
    if a.dry_run:
        print(PROMPTS["direct_ex"].format(report=items[0]["report"]))
        chars = sum(len(PROMPTS[t].format(report=it["report"])) for it, m, t in jobs)
        print(f"\n{len(jobs)} calls; ~{chars / 4 / 1e6:.2f}M input tokens (chars/4), output ~{len(jobs) * 250 / 1e6:.2f}M")
        return
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if out.exists():
        for l in open(out, encoding="utf-8"):
            d = json.loads(l)
            if d.get("parsed") is not None:
                done.add((d["id"], d["model"], d["task"]))
    todo = [j for j in jobs if (j[0]["id"], j[1], j[2]) not in done]
    key = None if a.mock else load_key(a.env_file)
    rng = random.Random(0)

    def work(job):
        it, m, t = job
        if a.mock:
            text, usage = mock(it, t, rng), {}
        else:
            text, usage = call(m, PROMPTS[t].format(report=it["report"]), key, a.temperature, max_tokens=1500)
        return {"id": it["id"], "model": m, "task": t, "raw": text, "parsed": parse(text), "usage": usage}

    with ThreadPoolExecutor(a.workers) as ex, open(out, "a", encoding="utf-8") as f:
        for row in ex.map(work, todo):
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            f.flush()
    print(f"done -> {out} ({len(todo)} new calls)")


if __name__ == "__main__":
    main()
