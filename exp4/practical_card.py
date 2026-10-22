"""Plain-language audit card, rendered from one extraction.

  python -m exp4.practical_card            -> results/exp4_cards_practical.md
Uses only the stored extractions; no model calls.
"""
import json
from pathlib import Path

from evaudit.core import blocker, minimal_sets, verification_bounds, verification_plan
from exp4.run_exp4 import build, load_jsonl, DATA, RES

INF = float("inf")


def n(x):
    return "unbounded" if x == INF else str(int(x))


def tol(t):
    """What a resilience value t means, in words."""
    if t == INF:
        return "holds whichever studies are wrong"
    t = int(t)
    if t <= 0:
        return "has no support left"
    if t == 1:
        return "holds only if every study it uses is correct"
    return f"holds even if any {t - 1} stud{'y is' if t == 2 else 'ies are'} wrong"


def render(p, g, k=2):
    W, R = g["W"], g["R"]
    refs = {int(x["ref"]): x.get("underlying_study", "unknown") for x in p.get("references", [])}
    # short labels for sources, in order of first reference
    src_refs = {}
    for ref in sorted(refs):
        s = "S:" + __import__("exp4.run_exp4", fromlist=["norm"]).norm(refs[ref])
        src_refs.setdefault(s, []).append(ref)
    label = {s: f"S{i + 1}" for i, s in enumerate(src_refs)}
    cond_refs = {}
    for r in p["routes"]:
        for c in r.get("conditions", []):
            cond_refs.setdefault(str(c), set()).update(int(x) for x in r.get("refs", []))
    text = lambda c: g["conds"].get(c, "")
    tauS = verification_bounds(W, R, confirmed=R)[0]
    L, H = verification_bounds(W, R)
    single = sorted(c[2:] for c in R if frozenset({c}) in blocker(W))
    plan = verification_plan(W, R, k)
    out = ["**Conclusion.** " + p.get("conclusion", ""),
           f"**Target.** The conclusion should hold even if any {k - 1} stud{'y is' if k == 2 else 'ies are'} wrong (k = {k}).", ""]
    status = "CERTIFIED" if L >= k else ("NOT CERTIFIED; the target cannot be reached" if H < k else "NOT CERTIFIED yet")
    now = ("no guarantee yet, since every route still rests on an unchecked assumption" if L == 0 else
           "the conclusion " + tol(L))
    out += [f"**Status: {status}.**",
            f"- If every assumption below holds, the conclusion {tol(tauS)}.",
            f"- Now: {now}.",
            f"- Best reachable by checking: the conclusion {tol(H)}.", ""]
    if plan is None:
        if single:
            out.append("Single points of failure: " + "; ".join(f"{c}: {text(c)}" for c in single))
        out += ["**Checklist.** None: even if every assumption is confirmed, the target is out of reach. "
                "More independent evidence is needed, or the conclusion must be narrowed.", ""]
    else:
        Q = sorted(plan[0], key=lambda c: (c[2:] not in single, c))
        out.append(f"**Checklist to reach the target** ({len(Q)} checks; all must be confirmed; "
                   "single points of failure first)")
        for i, c in enumerate(Q, 1):
            Hn = verification_bounds(W, R, rejected={c})[1]
            flag = " [single point of failure]" if c[2:] in single else ""
            after = "no support remains; stop" if Hn == 0 else f"at best the conclusion {tol(Hn)}"
            out.append(f"{i}. {c[2:]}{flag}: {text(c[2:])}  *Look in:* refs "
                       f"{', '.join(map(str, sorted(cond_refs.get(c[2:], []))))}.  *If false:* {after}.")
        Lq = verification_bounds(W, R, confirmed=set(Q))[0]
        out += [f"*If all {len(Q)} are confirmed:* the conclusion {tol(Lq)}.", ""]
    out.append("**Studies behind the references**")
    out += [f"- {label[s]}: {refs[r[0]]} (ref{'s' if len(r) > 1 else ''} {', '.join(map(str, r))})"
            for s, r in src_refs.items()]
    certs = sorted(blocker(W), key=lambda c: (len(c), sorted(c)))
    def show(c):
        cs = sorted(x[2:] for x in c if x.startswith("R:"))
        ss = sorted(label.get(x, x[2:]) for x in c if x.startswith("S:"))
        parts = [f"{', '.join(cs)} false"] if cs else []
        if ss:
            parts.append(f"{', '.join(ss)} wrong")
        return " and ".join(parts)
    out += ["", f"**Smallest ways the conclusion can lose all support** ({len(certs)} in total): "
            + "; ".join(show(c) for c in certs[:6]) + (" ..." if len(certs) > 6 else ""), ""]
    u = [x for x in p.get("unstated", []) or []]
    out += ["**Not covered by this card**",
            "- Whether each cited passage says what the report claims (citation checks are assumed done).",
            f"- Assumptions the report never states, added during reading: {', '.join(x['id'] for x in u) or 'none'}; "
            "a person must accept them.",
            f"- References whose study could not be identified: {', '.join(map(str, g['unknown_refs'])) or 'none'}."]
    return "\n".join(out)


def main():
    reports = {r["id"]: r for r in load_jsonl(DATA / "reports.jsonl")}
    rows = {}
    for r in load_jsonl(RES / "exp4_extract.jsonl"):
        rows[(r["id"], r["model"])] = r
    md = ["# Audit cards (plain-language form)", "",
          "Rendered by the program from each judge's extraction. Nothing here has been checked by a person yet.", ""]
    for rid in reports:
        md += [f"## {rid}: {reports[rid]['question']}", ""]
        for (i, m), r in sorted(rows.items()):
            if i == rid and r.get("parsed") and build(r["parsed"]):
                md += [f"### {m}", "", render(r["parsed"], build(r["parsed"])), ""]
    (RES / "exp4_cards_practical.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("->", RES / "exp4_cards_practical.md")


if __name__ == "__main__":
    main()
