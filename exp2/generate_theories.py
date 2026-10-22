"""Experiment 2 — source-attributed rule theories with exact provenance.

Each instance is a short "literature digest" about one material sample:
  * fact passages   "[P3] Okafor et al. (2019) report that sample S-12 is porous."
  * rule passages   "[P7] Haddad et al. (2017) establish that porous, doped samples are conductive."
Every passage is an evidence atom; its source is the paper it is attributed to.
Corroboration and duplication are injected deliberately:
  * a base fact may be reported by a second, *different* paper (true corroboration)
  * a fact or rule may be restated by the *same* paper in another passage (duplicate)
  * a review may restate a primary paper's claim and cite it (relay: same source)
  * a rule may be independently established by a second paper

Ground truth is exact: we enumerate every derivation of the target property
(acyclic Horn rules), project to sources, and compute the minimal witnesses,
tau, nu and the counting baselines with evaudit.core.

Usage: python -m exp2.generate_theories --n 500 --seed 7
"""
from __future__ import annotations

import argparse
import itertools
import json
import random
from collections import defaultdict
from pathlib import Path

from evaudit.core import Poly, audit, minimal_sets

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "exp2"

PROPS = ["crystalline", "porous", "doped", "annealed", "hydrophobic", "magnetic", "layered", "amorphous",
         "nanostructured", "oxidised", "strained", "defect-rich", "thermally stable", "conductive",
         "photoactive", "catalytically active", "ductile", "transparent", "piezoelectric", "superhydrophobic",
         "corrosion-resistant", "ion-conducting", "luminescent", "ferroelectric", "semiconducting"]
SURNAMES = ["Okafor", "Lindqvist", "Haddad", "Moreau", "Tanaka", "Kowalski", "Mensah", "Ribeiro", "Novak",
            "Petrov", "Sato", "Varga", "Delgado", "Iyer", "Fischer", "Brennan", "Castillo", "Ferreira",
            "Hoffmann", "Jansen", "Kaur", "Larsen", "Murphy", "Nguyen", "Ortiz", "Quinn", "Rossi", "Weber"]
FACT_T = ["{S} report that sample {X} is {p}.", "According to {S}, sample {X} is {p}.",
          "{S} found sample {X} to be {p}."]
RULE_T = ["{S} establish that {body} samples are {h}.", "{S} show that any sample that is {body} is {h}.",
          "Following {S}, {a_body} sample is {h}."]
RELAY_T = ["A review citing {S} states that {content}", "{R}, summarising {S}, note that {content}"]


def join_body(ps):
    return ps[0] if len(ps) == 1 else ", ".join(ps[:-1]) + " and " + ps[-1]


def gen_instance(rng: random.Random, idx: int):
    props = rng.sample(PROPS, 12)
    target, derived_pool, base_pool = props[0], props[1:5], props[5:]
    n_src = rng.randint(4, 7)
    papers = [f"{s} et al. ({rng.randint(2010, 2024)})" for s in rng.sample(SURNAMES, n_src)]
    X = f"S-{rng.randint(1, 99)}"

    # rules: target <- 2-3 alternative bodies; derived <- 1-2 bodies; bodies drawn from lower layers
    layer = {target: 2}
    for d in derived_pool:
        layer[d] = 1
    for b in base_pool:
        layer[b] = 0
    rules = []  # (head, tuple(body))
    used_derived = rng.sample(derived_pool, rng.randint(1, 3))
    for _ in range(rng.randint(2, 3)):
        cand = used_derived + base_pool
        rules.append((target, tuple(sorted(rng.sample(cand, rng.randint(1, 2))))))
    for d in used_derived:
        for _ in range(rng.randint(1, 2)):
            rules.append((d, tuple(sorted(rng.sample(base_pool, rng.randint(1, 2))))))
    rules = list(dict.fromkeys(rules))

    # which base facts hold: everything mentioned in bodies, minus a few (so some rules don't fire)
    mentioned = sorted({b for _, body in rules for b in body if layer[b] == 0})
    holds = set(rng.sample(mentioned, max(1, len(mentioned) - rng.randint(0, 2))))
    holds |= set(rng.sample(base_pool, 2))  # distractor facts

    passages = []  # dict(pid, text, source, kind, content_key)

    def add(text, source, kind, key):
        passages.append({"text": text, "source": source, "kind": kind, "key": key})

    for f in sorted(holds):
        s1 = rng.choice(papers)
        add(rng.choice(FACT_T).format(S=s1, X=X, p=f), s1, "fact", ("fact", f))
        r = rng.random()
        if r < 0.30:  # independent corroboration by a different paper
            s2 = rng.choice([p for p in papers if p != s1])
            add(rng.choice(FACT_T).format(S=s2, X=X, p=f), s2, "fact", ("fact", f))
        elif r < 0.55:  # relay: a review restates s1 (same source)
            content = f"sample {X} is {f}."
            add(rng.choice(RELAY_T).format(S=s1, R="Review authors", content=content), s1, "relay", ("fact", f))
    for h, body in rules:
        s1 = rng.choice(papers)
        jb = join_body(list(body))
        a_body = ("an " if jb[0] in "aeiou" else "a ") + jb
        add(rng.choice(RULE_T).format(S=s1, body=jb, a_body=a_body, h=h), s1, "rule", ("rule", h, body))
        r = rng.random()
        if r < 0.35:  # rule independently established by a different paper
            s2 = rng.choice([q for q in papers if q != s1])
            add(rng.choice(RULE_T).format(S=s2, body=jb, a_body=a_body, h=h), s2, "rule", ("rule", h, body))
        elif r < 0.55:
            content = f"{join_body(list(body))} samples are {h}."
            add(rng.choice(RELAY_T).format(S=s1, R="Review authors", content=content), s1, "relay", ("rule", h, body))
    rng.shuffle(passages)
    for i, p in enumerate(passages):
        p["pid"] = f"P{i + 1}"

    # exact proofs: proofs(prop) = union over atoms stating it, and over rules for it of
    # rule-atom x product of body proofs
    by_key = defaultdict(list)
    for p in passages:
        by_key[p["key"]].append(p["pid"])

    memo = {}

    def proofs(prop):
        if prop in memo:
            return memo[prop]
        out = set()
        for pid in by_key.get(("fact", prop), []):
            out.add(frozenset([pid]))
        for h, body in rules:
            if h != prop:
                continue
            body_proofs = [proofs(b) for b in body]
            if any(not bp for bp in body_proofs):
                continue
            for rule_pid in by_key[("rule", h, body)]:
                for combo in itertools.product(*body_proofs):
                    out.add(frozenset([rule_pid]).union(*combo))
        memo[prop] = minimal_sets(out) if len(out) > 200 else out
        return memo[prop]

    P = proofs(target)
    if not P:
        return None
    sigma = {p["pid"]: p["source"] for p in passages}
    poly = Poly.from_derivations([sorted(d) for d in P])
    a = audit(poly, sigma)
    fact_level = audit(poly)
    return {
        "id": f"theory-{idx:04d}", "sample": X, "target": target,
        "question": f"Is sample {X} {target}?",
        "passages": [{k: p[k] for k in ("pid", "text", "source", "kind")} for p in passages],
        "derivations": sorted(sorted(d) for d in P),
        "truth": {
            "votes": a["votes"], "distinct_passages": a["distinct_atoms"],
            "pagr_multiplicity": a["pagr_multiplicity"],
            "fact_level_tau": fact_level["tau"], "fact_level_nu": fact_level["nu"],
            "source_witnesses": a["minimal_witnesses"], "tau": a["tau"], "nu": a["nu"],
            "critical_sources": a["critical_sources"], "min_transversal": a["min_transversal"],
            "n_sources_used": a["n_sources"],
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=500)
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    rows, idx = [], 0
    while len(rows) < a.n:
        inst = gen_instance(rng, idx)
        idx += 1
        if inst:
            rows.append(inst)
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "theories.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"{len(rows)} derivable theories ({idx} generated) -> {OUT / 'theories.jsonl'}")


if __name__ == "__main__":
    main()
