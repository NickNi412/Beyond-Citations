"""Experiment 6 — does a reasoning model compute failure certificates by itself?

Runs a thinking model on the 72 items of Experiment 3 with the strongest direct prompt (definitions and a worked
example) and, budget permitting, the extract-then-compute prompt. Prompts and parsing are those of Experiment 3,
so the answers are scored by exp3/analyze_exp3.py exactly as the other judges were.

  python -m exp6.run_exp6 --dry-run
  python -m exp6.run_exp6 --env-file .env                  # direct_ex with the default model, cap $1.40
  python -m exp3.analyze_exp3 results/exp6.jsonl --json results/exp6_summary.json
  python -m exp6.run_exp6 --mock --out results/exp6_mock.jsonl   # offline test

Default model: qwen/qwen3-235b-a22b-thinking-2507, the thinking variant of the Qwen judge of Experiment 3, so the
comparison isolates thinking. Tasks run in the order given; the cap stops the run cleanly between calls, and a rerun
resumes where it stopped.
"""
import argparse
import json
import random
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from evaudit.llm import Budget, BudgetExceeded, call  # noqa: E402
from exp1.run_exp1 import load_key  # noqa: E402
from exp3.run_exp3 import PROMPTS, mock, parse  # noqa: E402

MODEL = "qwen/qwen3-235b-a22b-thinking-2507"
PRICE = (0.45, 3.50)  # $/M input, output tokens, used only when the provider reports no cost


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(ROOT / "data" / "exp3" / "items.jsonl"))
    ap.add_argument("--models", nargs="+", default=[MODEL])
    ap.add_argument("--tasks", nargs="+", default=["direct_ex"],
                    choices=list(PROMPTS))
    ap.add_argument("--temperature", default="0.6", help="0.6 suits Qwen thinking; 'none' leaves the provider default")
    ap.add_argument("--reasoning", default=None, help="reasoning effort for models that take one (low/medium/high)")
    ap.add_argument("--max-tokens", type=int, default=24000, help="reasoning tokens count against this limit")
    ap.add_argument("--max-usd", type=float, default=1.40)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--env-file")
    ap.add_argument("--out", default=str(ROOT / "results" / "exp6.jsonl"))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--mock", action="store_true")
    a = ap.parse_args()
    a.temperature = None if str(a.temperature).lower() == "none" else float(a.temperature)

    items = [json.loads(l) for l in open(a.data, encoding="utf-8")]
    if len(items) != 72:
        sys.exit(f"expected the 72 corrected items of Experiment 3, found {len(items)}")
    out = Path(a.out)
    if not a.mock and out.name.startswith("exp6") and "mock" in out.name:
        sys.exit("refusing to write real answers to a mock file name")
    done = set()
    if out.exists():
        for l in open(out, encoding="utf-8"):
            d = json.loads(l)
            if d.get("parsed") is not None and d.get("usage", {}).get("finish_reason") != "length":
                done.add((d["id"], d["model"], d["task"]))
    jobs = [(it, m, t) for t in a.tasks for m in a.models for it in items if (it["id"], m, t) not in done]
    if a.dry_run:
        chars = sum(len(PROMPTS[t].format(report=it["report"])) for it, m, t in jobs)
        est_out = len(jobs) * 4000
        print(PROMPTS[a.tasks[0]].format(report=items[0]["report"]))
        print(f"\n{len(jobs)} calls to do; ~{chars / 4 / 1e6:.3f}M input tokens; output assumed ~4k tokens per call")
        print(f"estimated cost ${(chars / 4 * PRICE[0] + est_out * PRICE[1]) / 1e6:.2f}; cap ${a.max_usd:.2f}")
        return
    key = None if a.mock else load_key(a.env_file)
    budget, rng = Budget(a.max_usd), random.Random(0)

    def work(job):
        it, m, t = job
        if a.mock:
            text, usage = mock(it, t, rng), {"finish_reason": "stop", "cost": 0.0}
        else:
            text, usage = call(m, PROMPTS[t].format(report=it["report"]), key, budget, a.temperature,
                               a.max_tokens, fallback_price=PRICE if m == MODEL else None, reasoning=a.reasoning)
        return {"id": it["id"], "model": m, "task": t, "raw": text, "parsed": parse(text), "usage": usage,
                "temperature": a.temperature, "reasoning": a.reasoning}

    out.parent.mkdir(parents=True, exist_ok=True)
    n = stopped = 0
    with ThreadPoolExecutor(a.workers) as ex, open(out, "a", encoding="utf-8") as f:
        futs = [ex.submit(work, j) for j in jobs]
        for fu in futs:
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
            trunc = row["usage"].get("finish_reason") == "length"
            print(f"{n:3d} {row['task']:13s} {row['id']:28s} {'ok' if row['parsed'] else 'PARSE FAIL'}"
                  f"{' (truncated)' if trunc else ''}  spent ${budget.spent:.3f}")
    print(f"done -> {out}: {n} answers written, {stopped} calls skipped by the cap, spent ${budget.spent:.3f}")


if __name__ == "__main__":
    main()
