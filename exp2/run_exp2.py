"""Experiment 2b — can an LLM recover the derivation structure, and does tau computed
from its extraction beat its own direct estimate of robustness?

For each theory the model returns
  derivations          : list of passage-id sets, each sufficient to establish the conclusion
  min_papers_to_fail   : its direct estimate of how many distinct papers must be wrong
We then compute tau from the extracted derivations using the TRUE passage->paper map.

Same modes as exp1: --dry-run, --mock, or real calls with OPENROUTER_API_KEY.
Usage:
  python -m exp2.run_exp2 --n 60 --dry-run
  python -m exp2.run_exp2 --n 60 --models <model ids> --env-file ~/osi/.env --out results/exp2.jsonl
"""
from __future__ import annotations

import argparse
import json
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from exp1.run_exp1 import call, load_key

ROOT = Path(__file__).resolve().parents[1]

PROMPT = (
    "Below are passages from a literature digest about a material sample. Each passage is attributed to a paper.\n\n"
    "{passages}\n\n"
    "Question: {question}\n\n"
    "1. List every distinct way the passages establish that the answer is yes. For each way, give the minimal set of "
    "passage ids it relies on (facts and rules). Passages that restate the same claim count as alternatives.\n"
    "2. Treat each paper as a source. What is the minimum number of distinct papers that would have to be wrong "
    "for the conclusion to no longer be established by any of these ways?\n"
    'Reply with JSON only: {{"derivations": [["P1", "P4"], ...], "min_papers_to_fail": <integer>}}'
)


def render(row):
    ps = "\n".join(f"[{p['pid']}] {p['text']}" for p in row["passages"])
    return PROMPT.format(passages=ps, question=row["question"])


def parse(text):
    import re

    m = re.search(r"\{.*\}", text or "", re.S)
    if not m:
        return None
    raw = m.group(0)
    try:
        try:
            d = json.loads(raw)
        except json.JSONDecodeError:  # some models add // comments inside the JSON
            d = json.loads(re.sub(r'(?m)\s*//[^\n"]*$', "", raw))
        ders = [sorted(map(str, x)) for x in d.get("derivations", []) if isinstance(x, list)]
        return {"derivations": ders, "min_papers_to_fail": d.get("min_papers_to_fail")}
    except (json.JSONDecodeError, TypeError):
        return None


def mock(row, rng):
    """Synthetic extractor: returns the true derivations minus one at random, and a direct
    estimate equal to the number of derivations (a counting heuristic). Pipeline test only."""
    ders = list(row["derivations"])
    if len(ders) > 1 and rng.random() < .3:
        ders.pop(rng.randrange(len(ders)))
    return json.dumps({"derivations": ders, "min_papers_to_fail": len(row["derivations"])})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(ROOT / "data" / "exp2" / "theories.jsonl"))
    ap.add_argument("--n", type=int, default=60)
    ap.add_argument("--models", nargs="+", default=["MOCK"])
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--env-file")
    ap.add_argument("--out", default="results/exp2.jsonl")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--mock", action="store_true")
    a = ap.parse_args()

    rows = [json.loads(l) for l in open(a.data, encoding="utf-8")][: a.n]
    jobs = [(r, m) for r in rows for m in a.models]
    if a.dry_run:
        print(render(rows[0]))
        chars = sum(len(render(r)) for r, _ in jobs)
        print(f"\n{len(jobs)} calls; ~{chars / 4 / 1e6:.2f}M input tokens")
        return
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if out.exists():
        done = {(json.loads(l)["id"], json.loads(l)["model"]) for l in open(out, encoding="utf-8")}
    jobs = [(r, m) for r, m in jobs if (r["id"], "MOCK" if a.mock else m) not in done]
    key = None if a.mock else load_key(a.env_file)
    rng = random.Random(0)

    def work(job):
        r, m = job
        if a.mock:
            text, usage = mock(r, rng), {}
        else:
            text, usage = call(m, render(r), key, a.temperature, max_tokens=1000)
        return {"id": r["id"], "model": "MOCK" if a.mock else m, "raw": text, "parsed": parse(text), "usage": usage}

    with open(out, "a", encoding="utf-8") as f, ThreadPoolExecutor(a.workers) as ex:
        for fu in as_completed([ex.submit(work, j) for j in jobs]):
            f.write(json.dumps(fu.result(), ensure_ascii=False) + "\n")
    print("done ->", out)


if __name__ == "__main__":
    main()
