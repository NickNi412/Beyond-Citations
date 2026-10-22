"""Experiment 1 — paraphrased relays.

Step 1 (needs API): for every statement that appears in a `same_source_verbatim` row at the
largest k, ask one model for k-1 meaning-preserving paraphrases. Cached in
data/exp1/paraphrases_<dataset>.json, so reruns only fill what is missing.

Step 2 (no API): add `same_source_paraphrase` rows next to the verbatim rows: same cited study,
same wrappers, same order, but each relay after the first carries a different paraphrase.
Source-level tau is still 1, so a provenance-aware judge should score it like k = 1.

Usage:
  python -m exp1.make_paraphrases --data data/exp1/healthver_full.jsonl --model <id> --env-file .env
  python -m exp1.make_paraphrases --data data/exp1/healthver_full.jsonl --build-only
Writes data/exp1/<name>_pp.jsonl (original rows + paraphrase rows).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from exp1.run_exp1 import call, load_key

PROMPT = (
    "Rewrite the sentence below in {n} different ways. Keep its meaning, every number and every "
    "qualification exactly; change the wording and sentence structure; add nothing new.\n\n"
    "Sentence: {s}\n\n"
    'Reply with JSON only: {{"paraphrases": ["...", "..."]}}'
)


def key(s):
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:16]


def parse(text, n):
    m = re.search(r"\{.*\}", text or "", re.S)
    if not m:
        return None
    try:
        ps = [p.strip() for p in json.loads(m.group(0)).get("paraphrases", []) if isinstance(p, str) and p.strip()]
    except json.JSONDecodeError:
        return None
    return ps[:n] if len(ps) >= n else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--model")
    ap.add_argument("--env-file")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--build-only", action="store_true")
    a = ap.parse_args()

    path = Path(a.data)
    rows = [json.loads(l) for l in open(path, encoding="utf-8")]
    dataset = rows[0]["dataset"]
    kmax = max(r["k"] for r in rows)
    n = kmax - 1
    cache_path = path.parent / f"paraphrases_{dataset}.json"
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}

    verb = [r for r in rows if r["condition"] == "same_source_verbatim" and r["k"] == kmax]
    todo = sorted({r["items"][0]["statement"] for r in verb if key(r["items"][0]["statement"]) not in cache})
    if todo and not a.build_only:
        if not a.model:
            raise SystemExit("--model is required to generate paraphrases")
        k_api = load_key(a.env_file)

        def work(s):
            for _ in range(3):
                text, _ = call(a.model, PROMPT.format(n=n, s=s), k_api, 0.9, max_tokens=1500)
                ps = parse(text, n)
                if ps:
                    return s, ps
            return s, None

        with ThreadPoolExecutor(a.workers) as ex:
            for s, ps in ex.map(work, todo):
                if ps:
                    cache[key(s)] = {"statement": s, "paraphrases": ps}
        cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=1))
        print(f"paraphrased {sum(1 for s in todo if key(s) in cache)}/{len(todo)} statements -> {cache_path}")

    out, missing = list(rows), 0
    for r in rows:
        if r["condition"] != "same_source_verbatim":
            continue
        s = r["items"][0]["statement"]
        entry = cache.get(key(s))
        if not entry:
            missing += 1
            continue
        new = json.loads(json.dumps(r))
        new["id"] = r["id"].replace("same_source_verbatim", "same_source_paraphrase")
        new["condition"] = "same_source_paraphrase"
        for j, it in enumerate(new["items"]):
            if j == 0:
                continue  # first relay keeps the original wording
            p = entry["paraphrases"][(j - 1) % len(entry["paraphrases"])]
            it["text"] = it["text"].replace(it["statement"], p)
            it["statement"] = p
        out.append(new)
    dst = path.with_name(path.stem + "_pp.jsonl")
    with open(dst, "w", encoding="utf-8") as f:
        for r in out:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"{len(out) - len(rows)} paraphrase rows added ({missing} verbatim rows lacked paraphrases) -> {dst}")


if __name__ == "__main__":
    main()
