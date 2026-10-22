"""Experiment 1 — duplication stress test: build the instances.

For each claim we present k evidence items under three conditions that share
the same surface wrappers (so only provenance differs):

  independent            k different supporting statements, k different studies
  same_source_distinct   k different supporting statements, all attributed to ONE study
  same_source_verbatim   one supporting statement relayed k times, all citing ONE study

Votes / item count = k in every condition; source-level tau = nu = k for
`independent` and 1 for both same-source conditions. k = 1 is shared.

Attributions (study names) are synthetic and randomised per instance; the
evidence statements are real (HealthVer: COVID-19 paper abstracts; Climate-FEVER:
Wikipedia sentences). Same seed -> same instances.

Usage:  python -m exp1.build_exp1 --pilot 20 --full 200
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import re
from collections import defaultdict
from pathlib import Path

from evaudit.core import Poly, audit

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "exp1"

SURNAMES = ["Okafor", "Lindqvist", "Haddad", "Moreau", "Tanaka", "Kowalski", "Mensah", "Ribeiro", "Novak",
            "Petrov", "Achterberg", "Sato", "Varga", "Delgado", "Iyer", "Fischer", "Nakamura", "Oyelaran",
            "Brennan", "Castillo", "Ferreira", "Hoffmann", "Jansen", "Kaur", "Larsen", "Murphy", "Nguyen",
            "Ortiz", "Quinn", "Rossi", "Schmidt", "Takahashi", "Underwood", "Weber", "Yilmaz", "Zhou"]
WRAPPERS = [
    "{S} reported: “{e}”",
    "A review summarising {S} states: “{e}”",
    "A news article citing {S} writes: “{e}”",
    "A preprint discussing {S} notes: “{e}”",
    "A conference talk referencing {S} said: “{e}”",
]
CONDITIONS = ["independent", "same_source_distinct", "same_source_verbatim"]


def norm(s: str) -> set:
    return set(re.findall(r"[a-z0-9]+", s.lower()))


def jaccard(a: str, b: str) -> float:
    A, B = norm(a), norm(b)
    return len(A & B) / max(1, len(A | B))


def dedup(evs, thr=0.6):
    out = []
    for e in evs:
        if all(jaccard(e, f) < thr for f in out):
            out.append(e)
    return out


def load_healthver():
    g = defaultdict(list)
    for split in ["train", "dev", "test"]:
        with open(RAW / f"healthver_{split}.csv", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r["label"] == "Supports":
                    e = r["evidence"].strip()
                    if 8 <= len(e.split()) <= 80 and e not in g[r["claim"].strip()]:
                        g[r["claim"].strip()].append(e)
    return {c: dedup(v) for c, v in g.items()}


def load_climate_fever():
    g = {}
    with open(RAW / "climate-fever.jsonl", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            by_article = {}
            for e in r["evidences"]:
                if e["evidence_label"] == "SUPPORTS" and e["article"] not in by_article:
                    by_article[e["article"]] = e["evidence"].strip()
            g[r["claim"].strip()] = dedup(list(by_article.values()))
    return g


YEARS = {"healthver": (2020, 2022), "climatefever": (2005, 2019)}
NEGATED = re.compile(r"\b(debunk\w*|not|no|false|myth|hoax|doesn't|does not|cannot|can't|won't|isn't|aren't|"
                     r"don't|never|fake)\b", re.I)


def study_names(rng, n, years):
    names = rng.sample(SURNAMES, n)
    return [f"the study by {s} et al. ({rng.randint(*years)})" for s in names]


def make_items(rng, condition, k, evs, names):
    wrappers = rng.sample(WRAPPERS, k) if k <= len(WRAPPERS) else [rng.choice(WRAPPERS) for _ in range(k)]
    items = []
    for j in range(k):
        if condition == "independent":
            e, src = evs[j], names[j]
        elif condition == "same_source_distinct":
            e, src = evs[j], names[0]
        else:  # same_source_verbatim
            e, src = evs[0], names[0]
        text = wrappers[j].format(S=src, e=e)
        items.append({"text": text[0].upper() + text[1:], "statement": e, "cited_source": src})
    rng.shuffle(items)  # position of the original/first study carries no signal
    return items


def provenance(items):
    # each item is one derivation using one atom; atom -> its cited source
    atoms = [f"item{j + 1}" for j in range(len(items))]
    sigma = {a: it["cited_source"] for a, it in zip(atoms, items)}
    a = audit(Poly.from_derivations([[x] for x in atoms]), sigma)
    return {"atoms": atoms, "sigma": sigma, "votes": a["votes"], "tau": a["tau"], "nu": a["nu"]}


def build(dataset, claims, ks, rng):
    rows = []
    for ci, (claim, evs) in enumerate(claims):
        kmax = max(ks)
        evs = rng.sample(evs, kmax)
        names = study_names(rng, kmax, YEARS[dataset])
        for k in ks:
            conds = ["independent"] if k == 1 else CONDITIONS
            for cond in conds:
                items = make_items(rng, cond, k, evs, names)
                rows.append({
                    "id": f"{dataset}-c{ci:04d}-k{k}-{cond}",
                    "dataset": dataset, "claim_index": ci, "claim": claim,
                    "k": k, "condition": cond if k > 1 else "single",
                    "items": items, "provenance": provenance(items),
                })
    return rows


def select(g, kmax, n, rng):
    # drop negated claims ("Debunked: no, ...") whose 'Supports' labels are ambiguous
    eligible = sorted(c for c, v in g.items() if len(v) >= kmax and not NEGATED.search(c))
    rng.shuffle(eligible)
    return [(c, g[c]) for c in eligible[:n]], len(eligible)


def write(rows, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", type=int, default=20)
    ap.add_argument("--full", type=int, default=200)
    ap.add_argument("--seed", type=int, default=13)
    a = ap.parse_args()

    summary = {}
    hv = load_healthver()
    rng = random.Random(a.seed)
    sel, n_elig = select(hv, 5, a.pilot + a.full, rng)
    pilot, full = sel[:a.pilot], sel[a.pilot:]
    write(build("healthver", pilot, [1, 3, 5], random.Random(a.seed + 1)), OUT / "healthver_pilot.jsonl")
    write(build("healthver", full, [1, 3, 5], random.Random(a.seed + 2)), OUT / "healthver_full.jsonl")
    summary["healthver"] = {"eligible_claims_k5": n_elig, "pilot_claims": len(pilot), "full_claims": len(full)}

    cf = load_climate_fever()
    rng = random.Random(a.seed + 3)
    sel, n_elig = select(cf, 3, 10**9, rng)
    write(build("climatefever", sel, [1, 2, 3], random.Random(a.seed + 4)), OUT / "climatefever_all.jsonl")
    summary["climatefever"] = {"eligible_claims_k3": n_elig, "claims": len(sel)}

    (OUT / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
