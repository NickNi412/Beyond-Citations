"""Experiment 1 — analysis.

Key quantities per (model, prompt), at the largest k:
  inflation[c]   = mean support(c, kmax) - mean support(single, 1)
  discount ratio = (support(independent) - support(same_source_verbatim)) / inflation[independent]
                   1 -> copies earn nothing extra (provenance-aware); 0 -> copies count like
                   independent studies (counting-semiring behaviour)
  paired test    = Wilcoxon signed-rank over claims, independent vs same-source (claim means)
  count accuracy = for the 'aware' prompt, how often reported independent_studies == tau

Usage: python -m exp1.analyze_exp1 results/pilot.jsonl --fig results/pilot.png
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict

import numpy as np

ALL_CONDS = ["independent", "same_source_distinct", "same_source_verbatim", "same_source_paraphrase"]
COND_ORDER = ALL_CONDS  # narrowed to the conditions present in the data at load time
COND_LABEL = {"independent": "k independent studies", "same_source_distinct": "one study, k findings",
              "same_source_verbatim": "one finding, relayed k times (verbatim)",
              "same_source_paraphrase": "one finding, relayed k times (paraphrased)"}
COLORS = {"independent": "#2a78d6", "same_source_distinct": "#eb6834", "same_source_verbatim": "#1baf7a",
          "same_source_paraphrase": "#eda100"}


def load(path):
    rows = []
    for l in open(path, encoding="utf-8"):
        d = json.loads(l)
        p = d.get("parsed") or {}
        try:
            d["support"] = float(p["support"])
        except (KeyError, TypeError, ValueError):
            d["support"] = None
        d["count"] = p.get("independent_studies")
        rows.append(d)
    return rows


def boot_ci(x, n=2000, seed=0):
    x = np.asarray(x, float)
    if len(x) < 2:
        return (np.nan, np.nan)
    rng = np.random.default_rng(seed)
    m = rng.choice(x, (n, len(x))).mean(1)
    return tuple(np.percentile(m, [2.5, 97.5]))


def claim_means(rows):
    """mean support per (model, prompt, condition, k, claim) over samples"""
    acc = defaultdict(list)
    for r in rows:
        if r["support"] is not None:
            acc[(r["model"], r["prompt"], r["condition"], r["k"], r["claim_index"])].append(r["support"])
    return {k: float(np.mean(v)) for k, v in acc.items()}


def summarize(rows):
    from scipy.stats import wilcoxon

    global COND_ORDER
    present = {r["condition"] for r in rows}
    COND_ORDER = [c for c in ALL_CONDS if c in present]

    cm = claim_means(rows)
    groups = sorted({(m, p) for m, p, *_ in cm})
    ks = sorted({k for (_, _, _, k, _) in cm})
    kmax = ks[-1]
    out = {"n_rows": len(rows), "parse_failures": sum(r["support"] is None for r in rows), "by_group": {}}
    for m, p in groups:
        g = {"curves": {}, "contrasts": {}}
        base = [v for (mm, pp, c, k, _), v in cm.items() if (mm, pp, c, k) == (m, p, "single", 1)]
        for c in COND_ORDER:
            curve = [{"k": 1, "mean": float(np.mean(base)), "ci": boot_ci(base)}]
            for k in ks[1:]:
                v = [val for (mm, pp, cc, kk, _), val in cm.items() if (mm, pp, cc, kk) == (m, p, c, k)]
                if v:
                    curve.append({"k": k, "mean": float(np.mean(v)), "ci": boot_ci(v)})
            g["curves"][c] = curve
        top = {c: g["curves"][c][-1]["mean"] for c in COND_ORDER}
        b = float(np.mean(base))
        infl = {c: top[c] - b for c in COND_ORDER}
        g["contrasts"]["inflation_at_kmax"] = infl
        for c in ["same_source_distinct", "same_source_verbatim"]:
            ratio = (top["independent"] - top[c]) / infl["independent"] if abs(infl["independent"]) > 1e-9 else None
            g["contrasts"][f"discount_ratio_{c}"] = ratio
            a = {ci: v for (mm, pp, cc, kk, ci), v in cm.items() if (mm, pp, cc, kk) == (m, p, "independent", kmax)}
            s = {ci: v for (mm, pp, cc, kk, ci), v in cm.items() if (mm, pp, cc, kk) == (m, p, c, kmax)}
            common = sorted(set(a) & set(s))
            diffs = [a[i] - s[i] for i in common]
            pval = float(wilcoxon(diffs).pvalue) if len(common) >= 6 and any(diffs) else None
            g["contrasts"][f"paired_{c}"] = {"n_claims": len(common), "mean_diff": float(np.mean(diffs)) if diffs else None,
                                             "wilcoxon_p": pval}
        if p == "aware":
            cnt = [(r["count"], r["tau"], r["condition"]) for r in rows
                   if r["model"] == m and r["prompt"] == p and isinstance(r["count"], (int, float))]
            g["count_accuracy"] = {
                c: float(np.mean([x == t for x, t, cc in cnt if cc == c])) if any(cc == c for *_, cc in cnt) else None
                for c in ["single"] + COND_ORDER}
        # Two invariances that source-level support satisfies by construction:
        #  D (duplication invariance): relaying one finding k times should score like seeing it once
        #  S (source sensitivity): identical content under k sources should score above the same content
        #    under one source, since tau = k vs 1
        def paired(c1, k1, c2, k2):
            a = {ci: v for (mm, pp, cc, kk, ci), v in cm.items() if (mm, pp, cc, kk) == (m, p, c1, k1)}
            b2 = {ci: v for (mm, pp, cc, kk, ci), v in cm.items() if (mm, pp, cc, kk) == (m, p, c2, k2)}
            common = sorted(set(a) & set(b2))
            d = [a[i] - b2[i] for i in common]
            pv = float(wilcoxon(d).pvalue) if len(d) >= 6 and any(d) else None
            return {"n_claims": len(d), "mean_diff": float(np.mean(d)) if d else None, "wilcoxon_p": pv}
        ax = {}
        for c in ["same_source_verbatim", "same_source_paraphrase"]:
            if c in COND_ORDER:
                ax[f"D_violation_{c}"] = paired(c, kmax, "single", 1)
        if "same_source_distinct" in COND_ORDER:
            sg = paired("independent", kmax, "same_source_distinct", kmax)
            sg["share_of_independent_gain"] = (sg["mean_diff"] / infl["independent"]
                                               if sg["mean_diff"] is not None and abs(infl["independent"]) > 1e-9 else None)
            ax["S_gap"] = sg
        g["axioms"] = ax
        out["by_group"][f"{m} | {p}"] = g
    return out, groups, ks


def plot(summary, groups, ks, path):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    n = len(groups)
    cols = min(n, 3)
    rws = int(np.ceil(n / cols))
    fig, axes = plt.subplots(rws, cols, figsize=(4.2 * cols, 3.4 * rws), squeeze=False, sharey=True)
    for ax in axes.flat[n:]:
        ax.set_visible(False)
    for ax, (m, p) in zip(axes.flat, groups):
        g = summary["by_group"][f"{m} | {p}"]
        labelled = []
        for c in COND_ORDER:
            cur = g["curves"][c]
            x = [d["k"] for d in cur]
            y = [d["mean"] for d in cur]
            lo = [d["ci"][0] for d in cur]
            hi = [d["ci"][1] for d in cur]
            ax.fill_between(x, lo, hi, color=COLORS[c], alpha=.12, linewidth=0)
            ax.plot(x, y, color=COLORS[c], lw=2, marker="o", ms=5, label=COND_LABEL[c])
            if all(abs(y[-1] - v) > 2.5 for v in labelled):  # skip end labels that would collide
                ax.annotate(f"{y[-1]:.0f}", (x[-1], y[-1]), xytext=(5, 0), textcoords="offset points",
                            va="center", fontsize=8, color="#52514e")
                labelled.append(y[-1])
        ax.set_title(f"{m}\nprompt: {p}", fontsize=9, color="#0b0b0b")
        ax.set_xticks(ks)
        ax.set_xlabel("evidence items shown (k)", fontsize=8, color="#52514e")
        ax.grid(axis="y", color="#e6e5e0", lw=.6)
        for s in ["top", "right"]:
            ax.spines[s].set_visible(False)
        ax.tick_params(labelsize=8, colors="#52514e")
    axes[0][0].set_ylabel("judge support score (0-100)", fontsize=8, color="#52514e")
    h, l = axes[0][0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=3, frameon=False, fontsize=8)
    fig.suptitle("Source-level tau: independent = k, both same-source conditions = 1", fontsize=9, color="#52514e")
    fig.tight_layout(rect=(0, .07, 1, .95))
    fig.savefig(path, dpi=180)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("results")
    ap.add_argument("--fig")
    ap.add_argument("--json")
    a = ap.parse_args()
    rows = load(a.results)
    summary, groups, ks = summarize(rows)
    txt = json.dumps(summary["by_group"], indent=1, default=lambda o: None)
    print(f"rows {summary['n_rows']}, parse failures {summary['parse_failures']}")
    for name, g in summary["by_group"].items():
        c = g["contrasts"]
        print(f"\n{name}")
        print("  inflation at kmax:", {k: round(v, 1) for k, v in c["inflation_at_kmax"].items()})
        for cc in ["same_source_distinct", "same_source_verbatim"]:
            r = c[f"discount_ratio_{cc}"]
            pr = c[f"paired_{cc}"]
            print(f"  discount ratio {cc}: {None if r is None else round(r, 2)}  "
                  f"(indep - same = {pr['mean_diff'] if pr['mean_diff'] is None else round(pr['mean_diff'], 1)}, "
                  f"n={pr['n_claims']}, p={pr['wilcoxon_p']})")
        for name, v in g.get("axioms", {}).items():
            extra = f", share of independent gain {v['share_of_independent_gain']:.2f}" if v.get("share_of_independent_gain") is not None else ""
            print(f"  {name}: mean diff {v['mean_diff']:.1f} (n={v['n_claims']}, p={v['wilcoxon_p']}){extra}")
        if "count_accuracy" in g:
            print("  independent-study count == tau:", g["count_accuracy"])
    if a.json:
        open(a.json, "w").write(txt)
    if a.fig:
        plot(summary, groups, ks, a.fig)
        print("figure ->", a.fig)


if __name__ == "__main__":
    main()
