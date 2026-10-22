"""Experiment 2b — analysis.

Per model:
  derivation recall / precision  (minimal passage sets, exact set match)
  tau_extracted  = tau computed from the model's derivations with the true passage->paper map
  tau_direct     = the model's own min_papers_to_fail
  accuracy and mean absolute error of both against the true tau

Usage: python -m exp2.analyze_llm results/exp2.jsonl
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from evaudit.core import Poly, minimal_sets, tau, witnesses

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("results")
    ap.add_argument("--data", default=str(ROOT / "data" / "exp2" / "theories.jsonl"))
    a = ap.parse_args()
    truth = {json.loads(l)["id"]: json.loads(l) for l in open(a.data, encoding="utf-8")}
    by_model = defaultdict(list)
    for l in open(a.results, encoding="utf-8"):
        r = json.loads(l)
        by_model[r["model"]].append(r)

    for m, rs in sorted(by_model.items()):
        rec, prec, ex_ok, dir_ok, ex_err, dir_err, fails = [], [], [], [], [], [], 0
        pairs = []  # (true tau, tau from extraction, tau stated directly, votes) where both exist
        for r in rs:
            t = truth[r["id"]]
            p = r["parsed"]
            if not p:
                fails += 1
                continue
            valid = {q["pid"] for q in t["passages"]}
            true_d = minimal_sets(frozenset(d) for d in t["derivations"])
            pred_d = minimal_sets(frozenset(d) for d in p["derivations"] if d and set(d) <= valid)
            hit = len(true_d & pred_d)
            rec.append(hit / len(true_d))
            prec.append(hit / len(pred_d) if pred_d else 0.0)
            sigma = {q["pid"]: q["source"] for q in t["passages"]}
            t_true = t["truth"]["tau"]
            t_ex = tau(witnesses(Poly.from_derivations([sorted(d) for d in pred_d]), sigma)) if pred_d else 0
            ex_ok.append(t_ex == t_true)
            ex_err.append(abs(t_ex - t_true))
            try:
                t_dir = int(p["min_papers_to_fail"])
                dir_ok.append(t_dir == t_true)
                dir_err.append(abs(t_dir - t_true))
                pairs.append((t_true, t_ex, t_dir, t["truth"]["votes"]))
            except (TypeError, ValueError):
                pass
        print(f"\n{m}  (n={len(rs)}, parse failures={fails})")
        print(f"  derivation recall {np.mean(rec):.2f}, precision {np.mean(prec):.2f}")
        print(f"  tau from extraction: accuracy {np.mean(ex_ok):.2f}, MAE {np.mean(ex_err):.2f}")
        if dir_ok:
            print(f"  tau stated directly: accuracy {np.mean(dir_ok):.2f}, MAE {np.mean(dir_err):.2f}")
        if len(pairs) >= 6:
            from scipy.stats import binomtest, spearmanr

            T, E, D, V = map(np.array, zip(*pairs))
            a, b = E == T, D == T
            n10, n01 = int((a & ~b).sum()), int((~a & b).sum())
            p = binomtest(n10, n10 + n01).pvalue if n10 + n01 else float("nan")
            print(f"  paired (n={len(T)}): only extraction right {n10}, only direct right {n01}, exact McNemar p={p:.1g}")
            print(f"  always-answer-1 baseline accuracy {np.mean(T == 1):.2f}")
            print(f"  direct answer over/under true tau: {np.mean(D > T):.2f} / {np.mean(D < T):.2f}; "
                  f"extraction over/under: {np.mean(E > T):.2f} / {np.mean(E < T):.2f}")
            print(f"  Spearman: direct~votes {spearmanr(D, V)[0]:.2f}, direct~tau {spearmanr(D, T)[0]:.2f}, "
                  f"extraction~tau {spearmanr(E, T)[0]:.2f}")


if __name__ == "__main__":
    main()
