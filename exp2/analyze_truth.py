"""Experiment 2a — how far do counting-style support measures diverge from source-level tau?
Uses only the exact ground truth (no model calls).

Usage: python -m exp2.analyze_truth --fig results/exp2_truth.png
"""
from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(ROOT / "data" / "exp2" / "theories.jsonl"))
    ap.add_argument("--fig")
    ap.add_argument("--json")
    a = ap.parse_args()
    from scipy.stats import spearmanr

    T = [json.loads(l)["truth"] for l in open(a.data, encoding="utf-8")]
    n = len(T)
    tau = np.array([t["tau"] for t in T])
    nu = np.array([t["nu"] for t in T])
    votes = np.array([t["votes"] for t in T])
    passages = np.array([t["distinct_passages"] for t in T])
    pagr = np.array([t["pagr_multiplicity"] for t in T])
    ftau = np.array([t["fact_level_tau"] for t in T])

    def frac(mask):
        return float(np.mean(mask))

    disc = tot = 0
    for i, j in itertools.combinations(range(n), 2):
        if votes[i] != votes[j] and tau[i] != tau[j]:
            tot += 1
            disc += (votes[i] - votes[j]) * (tau[i] - tau[j]) < 0
    stats = {
        "n_theories": n,
        "tau_distribution": dict(sorted(Counter(tau.tolist()).items())),
        "share_votes_ge3_but_tau1": frac((votes >= 3) & (tau == 1)),
        "share_of_tau1_with_votes_ge3": frac(votes[tau == 1] >= 3),
        "share_pagr_no_single_point_but_tau1": frac((pagr >= 1) & (tau == 1)),
        "share_passage_level_tau_overstates": frac(ftau > tau),
        "share_tau_gt_nu": frac(tau > nu),
        "spearman_votes_tau": float(spearmanr(votes, tau).statistic),
        "spearman_passages_tau": float(spearmanr(passages, tau).statistic),
        "discordant_pairs_votes_vs_tau": disc / tot if tot else None,
        "median_votes_by_tau": {int(k): float(np.median(votes[tau == k])) for k in sorted(set(tau))},
    }
    print(json.dumps(stats, indent=1))
    if a.json:
        Path(a.json).write_text(json.dumps(stats, indent=1))
    if a.fig:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        ks = sorted(set(tau))
        fig, ax = plt.subplots(figsize=(5.2, 3.4))
        rng = np.random.default_rng(0)
        for x, k in enumerate(ks):
            v = votes[tau == k]
            ax.scatter(x + rng.uniform(-.18, .18, len(v)), v, s=9, color="#2a78d6", alpha=.35, linewidths=0)
            ax.plot([x - .25, x + .25], [np.median(v)] * 2, color="#0b0b0b", lw=2)
            ax.annotate(f"n={len(v)}, median {np.median(v):.0f}", (x, v.max()), xytext=(0, 6),
                        textcoords="offset points", ha="center", fontsize=8, color="#52514e")
        ax.set_xticks(range(len(ks)), [f"tau = {k}" for k in ks])
        ax.set_yscale("log")
        ax.set_ylim(.8, votes.max() * 4)
        ax.set_ylabel("derivations counted (votes, log scale)", fontsize=8, color="#52514e")
        ax.set_title("Vote counts overlap heavily across source-level robustness", fontsize=9)
        ax.grid(axis="y", color="#e6e5e0", lw=.6)
        for s in ["top", "right"]:
            ax.spines[s].set_visible(False)
        ax.tick_params(labelsize=8, colors="#52514e")
        fig.tight_layout()
        fig.savefig(a.fig, dpi=180)
        print("figure ->", a.fig)


if __name__ == "__main__":
    main()
