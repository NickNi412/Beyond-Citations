"""Experiment 7 — connecting the audit to the literature through Valency's MCP Bond.

For the six case-study reports:
  resolve  : each numbered reference is matched to an indexed paper (PMC id lookup, else a title search filtered by
             year). Two references that resolve to the same paper are one source; unmatched references are listed.
  evidence : for every single-condition bottleneck on the three judges' cards, a semantic search returns papers
             that bear on that condition, marking which of them the report already cites.
  render   : writes results/exp7_bond_cards.md, the plain-language card of one judge per report with the Bond links.

  python -m exp7.link resolve  --env-file .env        # about 35 Bond calls
  python -m exp7.link evidence --env-file .env        # about 50 Bond calls
  python -m exp7.link render  [--judge anthropic/claude-haiku-4.5]
Add --mock to any step for an offline test (writes *_mock files). Bond is free; nothing here calls a paid model.
"""
import argparse
import difflib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from evaudit.core import blocker  # noqa: E402
from exp4.run_exp4 import build  # noqa: E402

DATA, RES = ROOT / "data" / "exp4", ROOT / "results"
JUDGES = ["anthropic/claude-haiku-4.5", "openai/gpt-4.1", "qwen/qwen3-235b-a22b-2507"]


def load(p):
    p = Path(p)
    return [json.loads(l) for l in open(p, encoding="utf-8")] if p.exists() else []


def out(name, mock):
    return RES / (f"exp7_{name}_mock.json" if mock else f"exp7_{name}.json")


def norm(s):
    s = re.sub(r"[^a-z0-9 ]", " ", (s or "").lower().replace("₄", "4").replace("₂", "2"))
    return " ".join(s.split())


def parse_refs(report):
    """Numbered references at the end of a report: number, title, year, url."""
    refs = []
    for line in report.split("\n"):
        m = re.match(r"^\s*\[?(\d+)[\.\]]\s+(.*)$", line)
        if not m:
            continue
        n, rest = int(m.group(1)), m.group(2)
        t = (re.search(r"“(.+?)”", rest) or re.search(r"\*\*(.+?)\*\*", rest) or re.search(r"\*(.+?)\*", rest))
        title = (t.group(1) if t else rest.split(",")[0]).strip().rstrip(",.")
        tail = rest[t.end():] if t else rest
        y = re.search(r"\b(19|20)\d{2}\b", tail)
        u = re.search(r"https?://\S+", rest)
        url = u.group(0).rstrip(").,") if u else None
        pmc = re.search(r"(PMC\d+)", url or "")
        refs.append({"ref": n, "title": title, "year": int(y.group(0)) if y else None, "url": url,
                     "pmc": pmc.group(1) if pmc else None})
    return refs


class MockBond:
    """Offline stand-in: finds a paper for every second reference and returns two candidate papers per query."""
    def call(self, name, **a):
        if name == "get_paper_by_id":
            return {"found": True, "paper": {"id": a["paper_id"], "title": "mock title", "source": "pubmed",
                                             "url": "https://example.org", "abstract": "mock abstract"}}
        if name == "search_by_title":
            q = a["query"]
            return {"papers": [{"id": "M" + str(abs(hash(q)) % 1000), "title": q if len(q) % 2 else q + " (other)",
                                "source": "pubmed", "url": "https://example.org", "abstract": "mock abstract",
                                "dates": {"first_available": "2020-01-01"}}]}
        return {"confidence": "good_match", "papers": [
            {"id": "S1", "title": "mock study on " + a["query"][:40], "source": "pubmed", "url": "https://example.org"},
            {"id": "S2", "title": "another mock study", "source": "medrxiv", "url": "https://example.org"}]}


def bond(a):
    if a.mock:
        return MockBond()
    from exp7.bond import Bond, load_token
    return Bond(load_token(a.env_file))


def slim(p, abstract_chars=600):
    if not p:
        return None
    ab = p.get("abstract") or ""
    return {"id": p.get("id"), "title": p.get("title"), "source": p.get("source"), "doi": p.get("doi"),
            "url": p.get("url"), "date": (p.get("dates") or {}).get("first_available") or p.get("datestamp"),
            "abstract": ab[:abstract_chars] + ("..." if len(ab) > abstract_chars else "")}


def similarity(a, b):
    return difflib.SequenceMatcher(None, norm(a), norm(b)).ratio()


# Words in a title that narrow who was studied or what kind of study it is. A title can be almost identical to the
# one a report gives and still differ in exactly these words, which a similarity score does not catch.
QUALIFIERS = ["older adults", "elderly", "aged", "children", "adolescents", "infants", "pregnan", "women", "men",
              "obese", "overweight", "athletes", "patients with", "healthy", "narrative review", "case report",
              "pilot", "mice", "rats", "animal", "in vitro", "protocol"]


def qualifiers(text):
    t = f" {norm(text)} "
    return {q for q in QUALIFIERS if (f" {q}" in t if q in ("pregnan", "aged") else f" {q} " in t)}


def scope_notes(ref_title, paper_title, question):
    """(words in the indexed title missing from the report's citation, words missing from the question)."""
    found = qualifiers(paper_title)
    return sorted(found - qualifiers(ref_title)), sorted(found - qualifiers(ref_title) - qualifiers(question))


def step_resolve(a):
    B, res = bond(a), {}
    for r in load(DATA / "reports.jsonl"):
        rows = []
        for ref in parse_refs(r["report"]):
            hit, how = None, None
            if ref["pmc"]:
                try:
                    d = B.call("get_paper_by_id", paper_id=ref["pmc"], source="pubmed", max_authors=5)
                    if d.get("found"):
                        hit, how = d["paper"], "pmc id"
                except RuntimeError as e:
                    print("  get_paper_by_id failed:", e)
            if hit is None:
                kw = {"query": ref["title"][:900], "limit": 5, "max_authors": 5}
                if ref["year"]:
                    kw.update(start_date=str(ref["year"] - 1), end_date=str(ref["year"] + 1))
                try:
                    papers = B.call("search_by_title", **kw).get("papers", [])
                except RuntimeError as e:
                    print("  search_by_title failed:", e)
                    papers = []
                best = max(papers, key=lambda p: similarity(p.get("title"), ref["title"]), default=None)
                if best is not None and similarity(best.get("title"), ref["title"]) >= 0.85:
                    hit, how = best, "title search"
            sim = similarity(hit.get("title"), ref["title"]) if hit else None
            rows.append({**ref, "matched": bool(hit), "how": how, "title_similarity": sim, "paper": slim(hit)})
            print(f"{r['id']:9s} ref {ref['ref']}: {'MATCH ' + how if hit else 'not found'}"
                  f"{'' if sim is None else f' (title similarity {sim:.2f})'}")
        ids = [x["paper"]["id"] for x in rows if x["matched"]]
        dup = sorted({i for i in ids if ids.count(i) > 1})
        res[r["id"]] = {"question": r["question"], "refs": rows,
                        "same_paper": [[x["ref"] for x in rows if x["matched"] and x["paper"]["id"] == i] for i in dup]}
    json.dump(res, open(out("resolve", a.mock), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    n = sum(len(v["refs"]) for v in res.values())
    m = sum(x["matched"] for v in res.values() for x in v["refs"])
    print(f"resolved {m}/{n} references -> {out('resolve', a.mock)}")


def bottlenecks():
    """Single-condition bottlenecks of each judge's card, per report: {rid: [{judge, id, text}]}."""
    rows = {}
    for r in load(RES / "exp4_extract.jsonl"):
        rows[(r["id"], r["model"])] = r
    outd = {}
    for (rid, m), r in sorted(rows.items()):
        g = build(r["parsed"]) if r.get("parsed") else None
        if not g:
            continue
        for c in sorted(c for c in g["R"] if frozenset({c}) in blocker(g["W"])):
            outd.setdefault(rid, []).append({"judge": m, "id": c[2:], "text": g["conds"].get(c[2:], "")})
    return outd


def step_evidence(a):
    B = bond(a)
    resolved = json.load(open(out("resolve", a.mock), encoding="utf-8")) if out("resolve", a.mock).exists() else {}
    reports = {r["id"]: r for r in load(DATA / "reports.jsonl")}
    res = {}
    for rid, bs in bottlenecks().items():
        cited = {x["paper"]["id"] for x in resolved.get(rid, {}).get("refs", []) if x.get("matched")}
        res[rid] = []
        for b in bs:
            q = f"{reports[rid]['question']} Condition to check: {b['text']}"
            try:
                d = B.call("semantic_search_papers", query=q[:4900], limit=5, max_authors=5)
            except RuntimeError as e:
                print("  semantic_search_papers failed:", e)
                d = {}
            papers = [dict(slim(p, 300), cited_by_report=p.get("id") in cited) for p in d.get("papers", [])]
            res[rid].append({**b, "confidence": d.get("confidence"), "papers": papers})
            print(f"{rid:9s} {b['judge'].split('/')[-1]:22s} {b['id']:4s} {d.get('confidence')}: {len(papers)} papers, "
                  f"{sum(p['cited_by_report'] for p in papers)} already cited")
    json.dump(res, open(out("evidence", a.mock), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("->", out("evidence", a.mock))


def step_render(a):
    from exp4.practical_card import render
    resolved = json.load(open(out("resolve", a.mock), encoding="utf-8"))
    evidence = json.load(open(out("evidence", a.mock), encoding="utf-8")) if out("evidence", a.mock).exists() else {}
    rows = {}
    for r in load(RES / "exp4_extract.jsonl"):
        rows[(r["id"], r["model"])] = r
    md = ["# Audit cards linked to the literature through Valency MCP Bond", "",
          f"One card per report ({a.judge}). Reference matching and the literature for each single point of failure "
          "come from Bond; nothing here has been checked by a person yet.", ""]
    for rid, v in resolved.items():
        r = rows.get((rid, a.judge))
        md += [f"## {rid}: {v['question']}", ""]
        if r and r.get("parsed") and build(r["parsed"]):
            md += [render(r["parsed"], build(r["parsed"])), ""]
        md += ["**References matched to indexed papers (Bond)**"]
        for x in v["refs"]:
            p = x["paper"]
            md.append(f"- ref {x['ref']}: " + (f"[{p['title']}]({p['url']}) ({p['source']}, via {x['how']})" if p
                                               else f"not found in the index: {x['title']}"))
            hidden = scope_notes(x["title"], p["title"], v["question"])[0] if p else []
            if hidden:
                md.append(f"    - check scope: the indexed paper's title says \"{', '.join(hidden)}\", which the report's "
                          f"citation (\"{x['title']}\") leaves out. Confirm that the paper supports the claim for the "
                          f"population and study type in the question: \"{v['question']}\"")
            if p and x.get("title_similarity") is not None and x["title_similarity"] < 0.9:
                md.append(f"    - check: the report gives this reference as \"{x['title']}\"; the indexed paper's title "
                          f"differs (similarity {x['title_similarity']:.2f}). Confirm that the cited paper supports the "
                          "claim at the report's scope.")
        if v["same_paper"]:
            md.append("- Same paper cited more than once: " + "; ".join("refs " + ", ".join(map(str, g))
                                                                        for g in v["same_paper"]))
        md.append("")
        mine = [e for e in evidence.get(rid, []) if e["judge"] == a.judge]
        if mine:
            md.append("**Literature bearing on each single point of failure (Bond)**")
            for e in mine:
                md.append(f"- {e['id']}: {e['text']} (match: {e['confidence']})")
                md += [f"    - [{p['title']}]({p['url']}) ({p['source']}{', cited by the report' if p['cited_by_report'] else ''})"
                       for p in e["papers"][:3]]
            md.append("")
    path = RES / ("exp7_bond_cards_mock.md" if a.mock else "exp7_bond_cards.md")
    path.write_text("\n".join(md) + "\n", encoding="utf-8")
    print("->", path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["resolve", "evidence", "render"])
    ap.add_argument("--env-file")
    ap.add_argument("--judge", default=JUDGES[0])
    ap.add_argument("--mock", action="store_true")
    a = ap.parse_args()
    {"resolve": step_resolve, "evidence": step_evidence, "render": step_render}[a.step](a)


if __name__ == "__main__":
    main()
