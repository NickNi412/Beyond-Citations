"""Take a small, decisive slice of an Exp1 file: the first N claims, only k = 1 and the largest k.

  python -m exp1.subset --data data/exp1/healthver_full.jsonl --n 60 --out data/exp1/healthver_night.jsonl
"""
import argparse
import json

ap = argparse.ArgumentParser()
ap.add_argument("--data", required=True)
ap.add_argument("--n", type=int, default=60)
ap.add_argument("--out", required=True)
a = ap.parse_args()
rows = [json.loads(l) for l in open(a.data, encoding="utf-8")]
kmax = max(r["k"] for r in rows)
keep = sorted({r["claim_index"] for r in rows})[: a.n]
out = [r for r in rows if r["claim_index"] in set(keep) and r["k"] in (1, kmax)]
with open(a.out, "w", encoding="utf-8") as f:
    for r in out:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print(f"{len(out)} rows, {len(keep)} claims, k in (1, {kmax}) -> {a.out}")
