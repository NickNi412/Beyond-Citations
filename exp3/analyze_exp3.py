"""Experiment 3 — analysis.

A condition is identified by the set of routes it guards, so model and ground-truth condition ids are compared
through that signature. Per model and task we report:
  bottleneck  accuracy of deciding whether a single condition removes every route (true only for shared items)
  certs       exact recovery of the full family of minimal failure certificates
  sharing     (program-scored) the model's grouping of route conditions equals the truth
Unparsable answers count as wrong; every count is reported over all items attempted. Methods are compared on the
same items with an exact McNemar test, a cluster bootstrap over the 18 scenario families, and a family-level sign
test, since the four variants of one scenario are not independent.

  python -m exp3.analyze_exp3 results/exp3.jsonl
"""
import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

import numpy as np

from evaudit.core import blocker, minimal_sets

ROOT = Path(__file__).resolve().parents[1]
VARIANTS = ["shared_same", "shared_para", "separate_diss", "separate_sim"]


def letter(x):
    m = re.search(r"\b([A-F])\b", str(x).replace("Study", " "))
    return m.group(1) if m else None


def canon_family(fam, sig):
    """Rewrite each set: studies stay letters, conditions become 'C' + sorted route signature."""
    out = set()
    for s in fam:
        t = set()
        for x in s:
            if x in sig:
                t.add("C" + ",".join(map(str, sorted(sig[x]))))
            else:
                l = letter(x)
                if l is None:
                    return None
                t.add(l)
        out.add(frozenset(t))
    return out


def truth(item):
    sig = defaultdict(set)
    W = []
    for r in item["routes"]:
        sig[r["condition"]].add(r["route"])
        W.append(frozenset(r["studies"]) | {r["condition"]})
    W = minimal_sets(W)
    B = canon_family(blocker(W), sig)
    n = len(item["routes"])
    return {"certs": B, "bottleneck": any(len(c) == 1 and next(iter(c)).startswith("C") for c in B),
            "partition": {frozenset(v) for v in sig.values()}, "n_routes": n}


def from_extract(p):
    sig = defaultdict(set)
    W = []
    for r in p.get("routes", []):
        try:
            k = int(r["route"])
        except (KeyError, TypeError, ValueError):
            return None
        conds = [str(c) for c in r.get("conditions", [])]
        studies = [letter(s) for s in r.get("studies", [])]
        if None in studies or not studies:
            return None
        for c in conds:
            sig[c].add(k)
        W.append(frozenset(studies) | set(conds))
    if not W:
        return None
    W = minimal_sets(W)
    B = canon_family(blocker(W), sig)
    if B is None:
        return None
    return {"certs": B, "bottleneck": any(len(c) == 1 and next(iter(c)).startswith("C") for c in B),
            "partition": {frozenset(v) for v in sig.values()}}


def from_direct(p, n_routes):
    sig = {}
    for c in p.get("conditions", []):
        try:
            sig[str(c["id"])] = {int(x) for x in c.get("routes", [])}
        except (KeyError, TypeError, ValueError):
            return None
    certs = canon_family([set(map(str, s)) for s in p.get("failure_sets", []) if isinstance(s, list)], sig)
    spf = str(p.get("single_point_of_failure", "none")).strip()
    bott = spf in sig and len(sig[spf]) == n_routes
    return {"certs": minimal_sets(certs) if certs is not None else None, "bottleneck": bott}


METHODS = [  # (name, task, how scored)
    ("direct", "direct", "model"),
    ("direct_ex", "direct_ex", "model"),
    ("extract", "extract", "program"),
    ("ext_model:model", "extract_model", "model"),
    ("ext_model:program", "extract_model", "program"),
]
PAIRS = [("direct", "extract"), ("direct_ex", "extract"), ("ext_model:model", "ext_model:program")]


def score(r, t):
    """Return {bottleneck, certs[, sharing][, added_common]} or None if unparsable."""
    p = r.get("parsed")
    if not p:
        return None
    out = {}
    if r["how"] == "program":
        got = from_extract(p)
        if got is None:
            return None
        out["sharing"] = got["partition"] == t["partition"]
        # an extra condition guarding every route, absent from the truth (an unstated common premise)
        n = t["n_routes"]
        out["added_common"] = (not t["bottleneck"]) and any(len(v) == n for v in got["partition"])
    else:
        q = dict(p)
        if r["task"] == "extract_model":  # conditions carry no route lists here; derive them from the routes
            sig = defaultdict(set)
            for rr in p.get("routes", []):
                for c in rr.get("conditions", []):
                    try:
                        sig[str(c)].add(int(rr["route"]))
                    except (KeyError, TypeError, ValueError):
                        return None
            q["conditions"] = [{"id": k, "routes": sorted(v)} for k, v in sig.items()]
        got = from_direct(q, t["n_routes"])
        if got is None or got["certs"] is None:
            return None
    out["bottleneck"] = got["bottleneck"] == t["bottleneck"]
    out["certs"] = got["certs"] == t["certs"]
    return out


def family(item_id):
    return item_id.rsplit("-", 1)[0]  # domain-structure: the four variants of one scenario


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("results")
    ap.add_argument("--data", default=str(ROOT / "data" / "exp3" / "items.jsonl"))
    ap.add_argument("--json")
    ap.add_argument("--boot", type=int, default=5000)
    a = ap.parse_args()
    items = {json.loads(l)["id"]: json.loads(l) for l in open(a.data, encoding="utf-8")}
    T = {k: truth(v) for k, v in items.items()}
    rows = {}
    for l in open(a.results, encoding="utf-8"):
        r = json.loads(l)
        rows[(r["model"], r["task"], r["id"])] = r  # last row per key wins (retries)
    models = sorted({k[0] for k in rows})
    from scipy.stats import binomtest
    rng = np.random.default_rng(0)
    out = {}
    for m in models:
        S = {}  # method -> id -> score dict or None
        for name, task, how in METHODS:
            d = {}
            for i in items:
                r = rows.get((m, task, i))
                if r is None:
                    continue
                d[i] = score({**r, "how": how}, T[i])
            if d:
                S[name] = d
        o = {}
        print(f"\n{m}")
        for name, d in S.items():
            ok = {i: s for i, s in d.items() if s is not None}
            o[name] = {"n_items": len(d), "n_valid": len(ok), "parse_fail": len(d) - len(ok)}
            # unparsable answers count as wrong; denominators are all items attempted
            for k in ["bottleneck", "certs", "sharing", "added_common"]:
                if ok and k in next(iter(ok.values())):
                    o[name][k] = sum(s[k] for s in ok.values())
            o[name]["by_variant"] = {v: {"n": sum(items[i]["variant"] == v for i in d),
                                         "certs": sum(bool(s and s["certs"]) for i, s in d.items() if items[i]["variant"] == v),
                                         "bottleneck": sum(bool(s and s["bottleneck"]) for i, s in d.items() if items[i]["variant"] == v)}
                                     for v in VARIANTS}
            x = o[name]
            line = f"  {name:18s} valid {x['n_valid']}/{x['n_items']}  bottleneck {x.get('bottleneck', 0)}/{x['n_items']}  certs {x.get('certs', 0)}/{x['n_items']}"
            if "sharing" in x:
                line += f"  sharing {x['sharing']}/{x['n_items']}  added-common-premise {x['added_common']}"
            print(line)
            print("      " + "  ".join(f"{v} {b['certs']}/{b['n']}" for v, b in x["by_variant"].items()))
        for A, B in PAIRS:
            if A not in S or B not in S:
                continue
            ids = sorted(set(S[A]) & set(S[B]))
            for k in ["bottleneck", "certs"]:
                a_ = {i: bool(S[A][i] and S[A][i][k]) for i in ids}
                b_ = {i: bool(S[B][i] and S[B][i][k]) for i in ids}
                nb = sum(b_[i] and not a_[i] for i in ids)
                na = sum(a_[i] and not b_[i] for i in ids)
                pv = binomtest(nb, nb + na).pvalue if nb + na else float("nan")
                # cluster bootstrap over the 18 scenario families (four variants each)
                fams = sorted({family(i) for i in ids})
                byf = {f: [i for i in ids if family(i) == f] for f in fams}
                diffs = []
                for _ in range(a.boot):
                    pick = rng.choice(len(fams), len(fams))
                    sel = [i for j in pick for i in byf[fams[j]]]
                    diffs.append(np.mean([b_[i] for i in sel]) - np.mean([a_[i] for i in sel]))
                lo, hi = np.percentile(diffs, [2.5, 97.5])
                d = np.mean([b_[i] for i in ids]) - np.mean([a_[i] for i in ids])
                # family-level sign test: families where B beats A on total correct vs the reverse
                fb = sum(sum(b_[i] for i in byf[f]) > sum(a_[i] for i in byf[f]) for f in fams)
                fa = sum(sum(b_[i] for i in byf[f]) < sum(a_[i] for i in byf[f]) for f in fams)
                fp = binomtest(fb, fb + fa).pvalue if fb + fa else float("nan")
                print(f"  {B} vs {A} [{k}]: n={len(ids)}  {B}-only {nb}, {A}-only {na}, McNemar p={pv:.2g}; "
                      f"diff {d:+.2f} (family bootstrap 95% CI {lo:+.2f}..{hi:+.2f}); families {fb} vs {fa}, sign p={fp:.2g}")
                o[f"{B}_vs_{A}_{k}"] = {"n": len(ids), "b_only": nb, "a_only": na, "p": pv, "diff": d,
                                        "ci": [lo, hi], "families_b": fb, "families_a": fa, "family_sign_p": fp}
        out[m] = o
    if a.json:
        json.dump(out, open(a.json, "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
