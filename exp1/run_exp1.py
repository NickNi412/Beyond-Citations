"""Experiment 1 — query LLM judges (OpenRouter, OpenAI-compatible API).

Modes
  --dry-run   print one rendered prompt per prompt variant + call count and token estimate; no network
  --mock      run a synthetic 'naive counter' judge (no network) to exercise the pipeline
  (default)   real calls; needs OPENROUTER_API_KEY in the environment or in --env-file

Results are appended to --out (JSONL) and the run resumes where it stopped.

Example
  python -m exp1.run_exp1 --data data/exp1/healthver_pilot.jsonl --dry-run
  python -m exp1.run_exp1 --data data/exp1/healthver_pilot.jsonl \
      --models anthropic/claude-sonnet-4.5 openai/gpt-5-mini qwen/qwen3-235b-a22b \
      --env-file ~/osi/.env --out results/pilot.jsonl
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

PROMPTS = {
    "plain": (
        "You are assessing the evidence for a scientific claim.\n\n"
        "Claim: {claim}\n\n"
        "Evidence collected:\n{items}\n\n"
        "Taking all the evidence together, how strongly is the claim supported? "
        "Answer on a scale from 0 (no support) to 100 (conclusively established).\n"
        'Reply with JSON only: {{"support": <integer 0-100>}}'
    ),
    "aware": (
        "You are assessing the evidence for a scientific claim.\n\n"
        "Claim: {claim}\n\n"
        "Evidence collected:\n{items}\n\n"
        "Several items may report the same underlying study; count each underlying study only once. "
        "Taking all the evidence together, how strongly is the claim supported? "
        "Answer on a scale from 0 (no support) to 100 (conclusively established), and say how many "
        "independent underlying studies the evidence contains.\n"
        'Reply with JSON only: {{"support": <integer 0-100>, "independent_studies": <integer>}}'
    ),
}
URL = "https://openrouter.ai/api/v1/chat/completions"


def render(row, prompt):
    items = "\n".join(f"[{j + 1}] {it['text']}" for j, it in enumerate(row["items"]))
    return PROMPTS[prompt].format(claim=row["claim"], items=items)


def parse(text):
    m = re.search(r"\{.*?\}", text or "", re.S)
    if not m:
        return None
    try:
        d = json.loads(m.group(0))
        return {k: d[k] for k in ("support", "independent_studies") if k in d}
    except json.JSONDecodeError:
        return None


def load_key(env_file):
    if os.environ.get("OPENROUTER_API_KEY"):
        return os.environ["OPENROUTER_API_KEY"]
    if env_file:
        for line in Path(env_file).expanduser().read_text().splitlines():
            if line.strip().startswith("OPENROUTER_API_KEY"):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("No OPENROUTER_API_KEY found (environment or --env-file).")


def call(model, prompt_text, key, temperature, max_retries=5, max_tokens=200):
    import requests

    err = "no response"
    body = {"model": model, "temperature": temperature, "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt_text}]}
    for attempt in range(max_retries):
        try:
            r = requests.post(URL, headers={"Authorization": f"Bearer {key}"}, json=body, timeout=120)
            if r.status_code == 200:
                j = r.json()
                return j["choices"][0]["message"]["content"], j.get("usage", {})
            if r.status_code in (429, 500, 502, 503, 504):
                time.sleep(2 ** attempt)
                continue
            return f"HTTP {r.status_code}: {r.text[:300]}", {}
        except Exception as e:  # network hiccup
            time.sleep(2 ** attempt)
            err = repr(e)
    return f"ERROR: {err}", {}


def mock_judge(row, prompt, rng):
    """Synthetic 'naive counter': support grows with item count, ignores provenance.
    Only for testing the pipeline; never report these numbers."""
    k = row["k"]
    out = {"support": int(min(100, 55 + 7 * k + rng.gauss(0, 4)))}
    if prompt == "aware":
        out["independent_studies"] = k
    return json.dumps(out), {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--models", nargs="+", default=["MOCK"])
    ap.add_argument("--prompts", nargs="+", default=["plain", "aware"])
    ap.add_argument("--samples", type=int, default=2)
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--env-file")
    ap.add_argument("--out", default="results/exp1.jsonl")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--mock", action="store_true")
    a = ap.parse_args()

    rows = [json.loads(l) for l in open(a.data, encoding="utf-8")]
    jobs = [(r, m, p, s) for r in rows for m in a.models for p in a.prompts for s in range(a.samples)]

    if a.dry_run:
        for p in a.prompts:
            print(f"===== prompt '{p}' for {rows[-1]['id']} =====\n{render(rows[-1], p)}\n")
        chars = sum(len(render(r, p)) for r, m, p, s in jobs)
        print(f"{len(jobs)} calls; ~{chars / 4 / 1e6:.2f}M input tokens (chars/4), output ~{len(jobs) * 20 / 1e6:.2f}M")
        return

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if out.exists():
        for l in open(out, encoding="utf-8"):
            d = json.loads(l)
            done.add((d["id"], d["model"], d["prompt"], d["sample"]))
    jobs = [j for j in jobs if (j[0]["id"], j[1], j[2], j[3]) not in done]
    print(f"{len(jobs)} calls to make ({len(done)} already done)")
    key = None if a.mock else load_key(a.env_file)
    rng = random.Random(0)

    def work(job):
        r, m, p, s = job
        text, usage = mock_judge(r, p, rng) if a.mock else call(m, render(r, p), key, a.temperature)
        return {"id": r["id"], "dataset": r["dataset"], "claim_index": r["claim_index"], "k": r["k"],
                "condition": r["condition"], "tau": r["provenance"]["tau"], "model": "MOCK" if a.mock else m,
                "prompt": p, "sample": s, "raw": text, "parsed": parse(text), "usage": usage}

    with open(out, "a", encoding="utf-8") as f, ThreadPoolExecutor(a.workers) as ex:
        futs = [ex.submit(work, j) for j in jobs]
        for i, fu in enumerate(as_completed(futs), 1):
            f.write(json.dumps(fu.result(), ensure_ascii=False) + "\n")
            f.flush()
            if i % 50 == 0:
                print(f"  {i}/{len(jobs)}")
    print("done ->", out)


if __name__ == "__main__":
    main()
