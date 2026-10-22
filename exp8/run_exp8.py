"""Experiment 8 — where frontier models stop being reliable auditors.

Experiment 6 showed that frontier models derive the failure sets of small controlled reports by themselves. Experiment 5
showed that, auditing real reports, the same models seldom name a single point of failure that their own reading of the
report contains. Experiment 8 locates the gap.

  8A scale : synthetic reports from materials and energy science whose structure is written out explicitly (the
             study behind each reference, the lines of reasoning, the assumptions of each line). Four sizes, S to XL.
             The model answers four audit questions; answers are scored exactly against the program. Reading is taken
             out of the task, so the errors are errors of reasoning over a stated structure.
  8B self  : each model receives its own extraction of each case-study report (Experiment 5), written out in the same
             explicit form, and answers the same four questions. Can the model draw the consequences of its own
             reading once that reading is written down?
  8C hint  : the Experiment 5 strong audit with one added instruction to look for assumptions that every line of
             reasoning shares. Does the gap of Experiment 5 close by prompting?

Questions (8A, 8B):
  (a) every assumption holding, how many studies can be wrong with the conclusion still supported  [tau_S - 1]
  (b) which assumptions alone, if false, leave no supporting line                                 [single-condition bottlenecks]
  (c) a smallest set of assumptions whose confirmation makes the conclusion survive any one wrong study,
      whatever the unchecked assumptions are                                                      [minimum 2-plan]
  (d) one named assumption false, the others holding: how many studies can be wrong               [tau_S after rejection - 1]

  python -m exp8.run_exp8 gen                                   # data/exp8/items.jsonl, no API calls
  python -m exp8.run_exp8 scale --env-file .env --models M1 M2 --max-usd 3.5
  python -m exp8.run_exp8 self  --env-file .env --models M1 M2 --max-usd 1.0
  python -m exp8.run_exp8 hint  --env-file .env --models M1 M2 --max-usd 1.0
  python -m exp8.run_exp8 grade --env-file .env --max-usd 0.3   # grader for 8C, as in Experiment 5
  python -m exp8.run_exp8 analyze
Add --mock to any step for an offline test (writes *_mock files; no API calls).
"""
import argparse
import json
import random
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from evaudit.core import minimal_sets, restrict, verification_bounds, verification_plan  # noqa: E402
from evaudit.llm import Budget, BudgetExceeded, call, last_object  # noqa: E402

DATA, RES = ROOT / "data" / "exp8", ROOT / "results"
INF = float("inf")
SIZES = {  # studies, extra references that relay an earlier study, lines of reasoning, assumptions
    "S": (3, 1, 3, 4), "M": (5, 2, 6, 7), "L": (8, 3, 10, 10), "XL": (12, 4, 15, 14)}

DOMAINS = [
    ("electrolyte Voltrex-7", "has an ionic conductivity above 10 mS/cm at 25 °C"),
    ("LFP cell LX-280", "retains at least 80% of its capacity after 6,000 full cycles"),
    ("perovskite module PV-3", "converts sunlight at above 22% efficiency"),
    ("concrete mix CM-50", "reaches 50 MPa compressive strength at 28 days"),
    ("catalyst NiFe-2", "drives 10 mA/cm2 of oxygen evolution below 300 mV overpotential"),
    ("insulation panel AeroBoard", "has a thermal conductivity below 0.020 W/(m K)"),
]
ASSUMPTIONS = [
    "the tested samples have the commercial composition of the {p}",
    "the measurements were made at the temperature stated in the claim",
    "the test geometry and cell format match the {p} as sold",
    "the reported values are averages over samples, not best-sample results",
    "the measurement method agrees with the reference method within its stated uncertainty",
    "the samples were not aged or pre-conditioned beyond the claim's conditions",
    "the end-of-test criterion matches the one used in the claim",
    "the instrument calibration was traceable to a standard",
    "the production batch tested is representative of current production",
    "the operating conditions (rate, load or humidity) match those of the claim",
    "the values were not extrapolated beyond the measured range",
    "the units and normalisation (per area, per mass or per volume) match the claim",
    "the reported uncertainty covers batch-to-batch variation",
    "the test laboratory had no stake in the result",
    "the environmental conditions during testing were controlled",
    "the data processing did not exclude outlying samples without stated reasons",
]
AUTHORS = ["Tanaka", "Mbeki", "Larsen", "Okafor", "Silva", "Novak", "Haddad", "Kowalski", "Ibrahim", "Moreau",
           "Chen", "Petrov", "Duarte", "Nakamura", "Osei", "Fischer"]

QUESTIONS = (
    "Below is the evidence behind one conclusion of a technical report, with its structure written out. Each line of "
    "reasoning supports the conclusion on its own, provided that every reference it uses is correct and every "
    "assumption it lists holds. References that report the same underlying study stand or fall together: if a study "
    "is wrong, every reference to it is wrong.\n\n"
    "Answer four questions.\n"
    "(a) Suppose every assumption holds. What is the largest number k such that the conclusion stays supported "
    "whichever k studies turn out wrong? Count underlying studies, not references.\n"
    "(b) Which assumptions would, if that one assumption alone were false (every other assumption holding and every "
    "study correct), leave the conclusion with no supporting line? Give their ids, or [] if there are none.\n"
    "(c) All assumptions start unchecked, and an unchecked assumption may be false. Give a smallest set of "
    "assumptions such that, once all of them are confirmed, the conclusion stays supported even if any one study is "
    "wrong, whatever the truth of the assumptions left unchecked. Answer null if no set of assumptions achieves "
    "this.\n"
    "(d) Suppose assumption {x} is false and every other assumption holds. What is the largest number of studies "
    "that can be wrong with the conclusion still supported? Answer -1 if no supporting line remains.\n\n"
    'Reply with JSON only: {{"a": 0, "b": ["A1"], "c": ["A1", "A2"], "d": 0}}\n\n{structure}')

HINT = (
    "Before answering, look for assumptions that every line of reasoning in the report depends on, whichever study it "
    "cites (for example, that the population, product, dose or test conditions of the studies match the "
    "conclusion). If such an assumption is false, no cited study supports the conclusion, however many there are.\n")


# ---------------------------------------------------------------- structure, truth and rendering

def truth(W, R, x):
    """Answers to (a)-(d) for witnesses W over sources 'S:' and assumptions 'R:'."""
    def tol(t):
        return None if t == INF else int(t) - 1
    a = tol(verification_bounds(W, R, confirmed=R)[0])
    b = sorted(c[2:] for c in R if not restrict(W, false={c}))
    plan = verification_plan(W, R, 2) if len(R) <= 14 else "skipped"   # exact enumeration is slow beyond this
    d = tol(verification_bounds(W, R, confirmed=R - {x}, rejected={x})[0])
    if plan == "skipped":
        return {"a": a, "b": b, "c_size": "skipped", "c_example": None, "d": d}
    return {"a": a, "b": b, "c_size": None if plan is None else len(plan[0]),
            "c_example": None if plan is None else [c[2:] for c in plan[0]], "d": d}


def pick_x(W, R):
    """For (d): an assumption used by several lines but not by all, else any assumption."""
    use = {c: sum(c in w for w in W) for c in R}
    partial = [c for c in sorted(R) if 1 < use[c] < len(W)]
    return (partial or sorted(R, key=lambda c: -use[c]))[0]


def render(claim, refs, routes, assumptions):
    """refs: [(n, citation, study label, relay_of)], routes: [(refs, assumption ids)], assumptions: {id: text}."""
    out = [f"Conclusion: {claim}", "", "References (with the underlying study of each):"]
    for n, cit, s, relay in refs:
        out.append(f"[{n}] {cit}. Underlying study: {s}" + (f" (reports the same measurements as [{relay}])"
                                                             if relay else ""))
    out += ["", "Lines of reasoning:"]
    for i, (rs, cs) in enumerate(routes, 1):
        out.append(f"Line {i}: uses references {', '.join(f'[{r}]' for r in rs)}; assumes {', '.join(cs)}.")
    out += ["", "Assumptions:"]
    out += [f"{k}: {v}" for k, v in sorted(assumptions.items(), key=lambda kv: (int(kv[0][1:].split(".")[0]), kv[0]))]
    return "\n".join(out)


def witnesses(refs, routes):
    study = {n: s for n, _, s, _ in refs}
    return minimal_sets(frozenset({"S:" + study[r] for r in rs} | {"R:" + c for c in cs}) for rs, cs in routes)


def gen_item(size, i, rng):
    n_st, n_relay, n_routes, n_cond = SIZES[size]
    product, claim_tail = DOMAINS[i % len(DOMAINS)]
    claim = f"The {product} {claim_tail}."
    authors = rng.sample(AUTHORS, n_st)
    refs, n = [], 0
    for k in range(n_st):
        n += 1
        refs.append((n, f"{authors[k]} et al. ({2016 + rng.randrange(9)}), measurement study", f"S{k + 1}", None))
    for _ in range(n_relay):
        src = rng.choice(refs[:n_st])
        n += 1
        refs.append((n, f"{rng.choice(['Review', 'Trade article', 'Conference summary'])} citing {src[1].split(',')[0]}",
                     src[2], src[0]))
    texts = rng.sample(ASSUMPTIONS, n_cond)
    assumptions = {f"A{j + 1}": t.format(p=product) for j, t in enumerate(texts)}
    ids = list(assumptions)
    global_c = ids[0] if i % 2 == 0 else None          # half the items: one assumption shared by every line
    routes = []
    for r in range(n_routes):
        rs = sorted(rng.sample([x[0] for x in refs], 1 if rng.random() < 0.6 else 2))
        cs = set(rng.sample(ids[1:], rng.choice([1, 1, 2, 2, 3])))
        if global_c:
            cs.add(global_c)
        routes.append((rs, sorted(cs, key=lambda c: int(c[1:]))))
    used = sorted({c for _, cs in routes for c in cs})
    perm = rng.sample(range(1, len(used) + 1), len(used))     # relabel so that no id hints at its role
    ren = {c: f"A{j}" for c, j in zip(used, perm)}
    routes = [(rs, sorted((ren[c] for c in cs), key=lambda c: int(c[1:]))) for rs, cs in routes]
    assumptions = {ren[k]: v for k, v in assumptions.items() if k in ren}
    W = witnesses(refs, routes)
    R = {x for w in W for x in w if x.startswith("R:")}
    x = pick_x(W, R)
    return {"id": f"{size}-{i}", "size": size, "x": x[2:], "n_refs": len(refs), "n_studies": n_st,
            "n_lines": n_routes, "n_assumptions": len(R),
            "structure": render(claim, refs, routes, assumptions), "truth": truth(W, R, x),
            "W": [sorted(w) for w in W]}


def from_extraction(p, scope=None):
    """An Experiment 5 extraction in the explicit form of 8A, or None if malformed. With `scope` (Experiment 9
    labels), every each_study condition is stated once per study on each route that uses it."""
    from exp4.run_exp4 import norm
    try:
        studies, refs = {}, []
        for x in sorted(p.get("references", []), key=lambda x: int(x["ref"])):
            s = norm(x.get("underlying_study", "unknown"))
            key = f"ref{int(x['ref'])}" if s in ("", "unknown", "unclear", "not stated") else s
            studies.setdefault(key, f"S{len(studies) + 1}")
            refs.append((int(x["ref"]), x.get("underlying_study") or "not identified", studies[key], None))
        conds = {str(c["id"]): c.get("text", "") for c in p.get("conditions", []) + p.get("unstated", [])}
        ren = {c: f"A{i + 1}" for i, c in enumerate(conds)}
        label = {n: s for n, _, s, _ in refs}
        known = set(label)
        routes, text = [], {}
        for x in p["routes"]:
            rs = sorted(int(r) for r in x.get("refs", []))
            if not rs:
                continue
            if any(r not in known for r in rs):
                return None
            cs = []
            for c in map(str, x.get("conditions", [])):
                if c not in ren:
                    continue
                if scope and scope.get(c) == "each_study":
                    for st in sorted({label[r] for r in rs}):
                        cs.append(f"{ren[c]}.{st}")
                        text[f"{ren[c]}.{st}"] = f"{conds[c]} (for study {st})"
                else:
                    cs.append(ren[c])
                    text[ren[c]] = conds[c]
            routes.append((rs, sorted(set(cs))))
        if not routes:
            return None
        assumptions = text
    except (KeyError, TypeError, ValueError):
        return None
    W = witnesses(refs, routes)
    R = {x for w in W for x in w if x.startswith("R:")}
    if not R:
        return None
    x = pick_x(W, R)
    return {"x": x[2:], "structure": render(p.get("conclusion", "(as stated in the report)"), refs, routes, assumptions),
            "truth": truth(W, R, x), "n_lines": len(routes), "n_assumptions": len(R),
            "n_studies": len({s for _, _, s, _ in refs}), "W": [sorted(w) for w in W]}


# ---------------------------------------------------------------- scoring

def ids(v):
    if not isinstance(v, list):
        return None
    return sorted({str(x).strip().upper() for x in v})


def as_int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def score(ans, item):
    """Per question: right or wrong; (c) is right if the set is valid and as small as possible."""
    t = item["truth"]
    if not isinstance(ans, dict):
        return None
    W = [frozenset(w) for w in item["W"]]
    R = {x for w in W for x in w if x.startswith("R:")}
    a, d = as_int(ans.get("a")), as_int(ans.get("d"))
    b = ids(ans.get("b"))
    c = ans.get("c")
    if t["c_size"] == "skipped":
        c_ok = c_valid = None
    elif t["c_size"] is None:
        c_ok = c is None
        c_valid = c is None
    else:
        cs = ids(c)
        c_valid = cs is not None and set("R:" + x for x in cs) <= R and \
            verification_bounds(W, R, confirmed={"R:" + x for x in cs})[0] >= 2
        c_ok = c_valid and len(cs) == t["c_size"]
    ta = t["a"]
    return {"a": a == ta, "a_over": a is not None and ta is not None and a > ta,
            "b": b == sorted(t["b"]), "b_missed": len(set(t["b"]) - set(b or [])),
            "c": None if c_ok is None else bool(c_ok), "c_valid": None if c_valid is None else bool(c_valid),
            "d": d == t["d"],
            "all": a == ta and b == sorted(t["b"]) and (c_ok is None or bool(c_ok)) and d == t["d"]}


# ---------------------------------------------------------------- running

def load(p):
    p = Path(p)
    return [json.loads(l) for l in open(p, encoding="utf-8")] if p.exists() else []


def out(name, mock):
    return RES / f"exp8_{name}{'_mock' if mock else ''}.jsonl"


def mock_answer(item, rng):
    t = item["truth"]
    good = rng.random() < 0.6
    return json.dumps({"a": t["a"] if good else (t["a"] or 0) + 1, "b": t["b"] if good else [],
                       "c": t["c_example"], "d": t["d"]})


def run_jobs(jobs, work, path, workers):
    n = stopped = 0
    with ThreadPoolExecutor(workers) as ex, open(path, "a", encoding="utf-8") as f:
        for fu in [ex.submit(work, j) for j in jobs]:
            try:
                row = fu.result()
            except BudgetExceeded as e:
                stopped += 1
                if stopped == 1:
                    print("STOPPED:", e)
                continue
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            f.flush()
            n += 1
            print(f"{n:3d} {row['id']:12s} {row['model']:36s} {'ok' if row['parsed'] is not None else 'PARSE FAIL'}"
                  f"{' (truncated)' if (row.get('usage') or {}).get('finish_reason') == 'length' else ''}")
    print(f"{n} rows -> {path}; {stopped} calls skipped by the cap")


def ask(a, key, budget, rng, items, path):
    done = {(r["id"], r["model"]) for r in load(path) if r.get("parsed") is not None
            and (r.get("usage") or {}).get("finish_reason") != "length"}
    jobs = [(it, m) for m in a.models for it in items if (it["id"], m) not in done]

    def work(job):
        it, m = job
        prompt = QUESTIONS.format(x=it["x"], structure=it["structure"])
        if a.mock:
            text, usage = mock_answer(it, rng), {}
        else:
            text, usage = call(m, prompt, key, budget, None, a.max_tokens, reasoning=a.reasoning)
        return {"id": it["id"], "model": m, "raw": text, "parsed": last_object(text, "a"), "usage": usage}
    run_jobs(jobs, work, path, a.workers)


def step_gen(a):
    rng = random.Random(8)
    DATA.mkdir(parents=True, exist_ok=True)
    items = [gen_item(s, i, rng) for s in a.sizes for i in range(a.per_size)]
    with open(DATA / "items.jsonl", "w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    for s in a.sizes:
        its = [it for it in items if it["size"] == s]
        print(f"{s:3s} {len(its)} items; lines {its[0]['n_lines']}; studies {its[0]['n_studies']}; refs "
              f"{its[0]['n_refs']}; bottleneck items {sum(bool(it['truth']['b']) for it in its)}; "
              f"no-plan items {sum(it['truth']['c_size'] is None for it in its)}; "
              f"plan sizes {[it['truth']['c_size'] for it in its]}")
    print("->", DATA / "items.jsonl")


def step_scale(a, key, budget, rng):
    items = load(DATA / "items.jsonl")
    if not items:
        sys.exit("run the gen step first")
    if a.sizes:
        items = [it for it in items if it["size"] in a.sizes]
    ask(a, key, budget, rng, items, out("scale", a.mock))


def step_self(a, key, budget, rng):
    """Each model sees only its own extractions."""
    from exp5.run_exp5 import paths
    rows = {}
    for r in load(paths(False)["extract"]):
        rows[(r["id"], r["model"])] = r
    path = out("self_split" if a.split else "self", a.mock)
    scopes = {}
    if a.split:
        for r in load(RES / "exp9_scope.jsonl"):
            if r.get("file") == "exp5_extract.jsonl" and r.get("parsed"):
                scopes[(r["id"], r["model"])] = {str(x.get("id")): x.get("scope") for x in r["parsed"].get("scopes", [])}
    done = {(r["id"], r["model"]) for r in load(path) if r.get("parsed") is not None}
    jobs = []
    for (rid, m), r in sorted(rows.items()):
        if m in a.models and r.get("parsed") and (rid, m) not in done:
            if a.split and (rid, m) not in scopes:
                continue
            it = from_extraction(r["parsed"], scopes.get((rid, m)) if a.split else None)
            if it:
                jobs.append(({**it, "id": rid}, m))
    print(f"{len(jobs)} own-extraction items")

    def work(job):
        it, m = job
        prompt = QUESTIONS.format(x=it["x"], structure=it["structure"])
        if a.mock:
            text, usage = mock_answer(it, rng), {}
        else:
            text, usage = call(m, prompt, key, budget, None, a.max_tokens, reasoning=a.reasoning)
        return {"id": it["id"], "model": m, "raw": text, "parsed": last_object(text, "a"), "usage": usage,
                "item": it}
    run_jobs(jobs, work, path, a.workers)


def step_hint(a, key, budget, rng):
    from exp5.run_exp5 import PLAIN, STRONG, STRONG_FMT, mock_text, reports
    prompt = STRONG + HINT + STRONG_FMT
    path = out("hint", a.mock)
    done = {(r["id"], r["model"]) for r in load(path) if r.get("parsed")}
    jobs = [(r, m) for m in a.models for r in reports() if (r["id"], m) not in done]

    def work(job):
        r, m = job
        if a.mock:
            text, usage = mock_text("strong", rng), {}
        else:
            text, usage = call(m, prompt.format(report=r["report"]), key, budget, None, a.max_tokens,
                               reasoning=a.reasoning)
        return {"id": r["id"], "model": m, "prompt": "hint", "raw": text, "parsed": last_object(text, "checks"),
                "usage": usage}
    run_jobs(jobs, work, path, a.workers)


def step_grade(a, key, budget, rng):
    from exp5.run_exp5 import GRADE, GRADER, cards, mock_text
    C = cards(False)
    path = out("hint_grade", a.mock)
    done = {(r["id"], r["model"]) for r in load(path) if r.get("parsed")}
    audits = {(r["id"], r["model"]): r for r in load(out("hint", a.mock))}
    jobs = [(k, r) for k, r in audits.items() if r.get("parsed") and k in C and C[k]["bottlenecks"] and k not in done]

    def work(job):
        (rid, m), r = job
        card = C[(rid, m)]
        conds = "\n".join(f"{b['id']}: {b['text']}" for b in card["bottlenecks"])
        checks = "\n".join(f"{c.get('n')}: {c.get('check', '')} (where: {c.get('where', '')})"
                           for c in r["parsed"].get("checks", []))
        if a.mock:
            text, usage = mock_text("grade", rng, card=card), {}
        else:
            text, usage = call(GRADER, GRADE.format(conds=conds, checks=checks), key, budget, 0.0, 2000)
        return {"id": rid, "model": m, "prompt": "hint", "raw": text, "parsed": last_object(text, "matches"),
                "usage": usage}
    run_jobs(jobs, work, path, a.workers)


# ---------------------------------------------------------------- analysis

def summarise(rows, items_by_id, group):
    S = defaultdict(lambda: defaultdict(int))
    for r in rows:
        it = items_by_id(r)
        if it is None:
            continue
        g = S[group(r, it)]
        g["n"] += 1
        sc = score(r.get("parsed"), it)
        if sc is None:
            g["parse_fail"] += 1
            continue
        for k, v in sc.items():
            if v is None:
                continue
            g[k] += int(v)
        g["c_scored"] += sc["c"] is not None
        g["bottlenecks"] += len(it["truth"]["b"])
    return S


def fmt_group(name, g):
    n = g["n"]
    return (f"{name:48s} n={n:2d}  (a) tolerance {g['a']}/{n} [over {g['a_over']}]  (b) single points {g['b']}/{n} "
            f"[missed {g['b_missed']}/{g['bottlenecks']}]  (c) minimum plan {g['c']}/{g['c_scored']} [valid {g['c_valid']}]  "
            f"(d) after one rejection {g['d']}/{n}  all four {g['all']}/{n}"
            + (f"  parse failures {g['parse_fail']}" if g["parse_fail"] else ""))


def step_analyze(a):
    summary, lines = {}, []
    items = {it["id"]: it for it in load(DATA / "items.jsonl")}
    rows = {(r["id"], r["model"]): r for r in load(out("scale", a.mock))}
    if rows:
        lines.append("8A scale (explicit structure, synthetic materials/energy reports)")
        S = summarise(rows.values(), lambda r: items.get(r["id"]), lambda r, it: (r["model"], it["size"]))
        order = list(SIZES)
        for (m, s), g in sorted(S.items(), key=lambda kv: (kv[0][0], order.index(kv[0][1]))):
            lines.append(fmt_group(f"  {m} {s}", g))
            summary[f"scale | {m} | {s}"] = dict(g)
    for tag, title in [("self", "8B self (the model's own extraction of each case-study report, written out)"),
                       ("self_split", "8B self, conditions stated per study (Experiment 9 scopes)")]:
        rows = {(r["id"], r["model"]): r for r in load(out(tag, a.mock))}
        if rows:
            lines.append(title)
            S = summarise(rows.values(), lambda r: r["item"], lambda r, it: r["model"])
            for m, g in sorted(S.items()):
                lines.append(fmt_group(f"  {m}", g))
                summary[f"{tag} | {m}"] = dict(g)
    hint = {(r["id"], r["model"]): r for r in load(out("hint", a.mock))}
    if hint:
        from exp5.run_exp5 import as_int_list, cards
        C = cards(False)
        grades = {(r["id"], r["model"]): r for r in load(out("hint_grade", a.mock))}
        H = defaultdict(lambda: defaultdict(int))
        for (rid, m), r in hint.items():
            h = H[m]
            card = C.get((rid, m))
            if card is None or not r.get("parsed"):
                h["missing"] += 1
                continue
            pr = r["parsed"]
            B = card["bottlenecks"]
            match = {str(x.get("id")): as_int_list(x.get("checks"))
                     for x in ((grades.get((rid, m)) or {}).get("parsed") or {}).get("matches", []) or []}
            alone = set(as_int_list(pr.get("alone_removes_support")))
            h["reports"] += 1
            h["bottlenecks"] += len(B)
            h["flagged"] += sum(1 for b in B if set(match.get(b["id"], [])) & alone)
            if B:
                h["reports_with_bottleneck"] += 1
                h["said_none"] += int(not alone)
            t = card["tau_S"]
            tr = None if t == INF else int(t) - 1
            st = as_int(pr.get("studies_that_can_be_wrong"))
            h["tol_exact"] += int(st is not None and st == tr)
            h["tol_over"] += int(st is not None and tr is not None and st > tr)
        lines.append("8C hint (Experiment 5 strong audit + an instruction to look for shared assumptions)")
        for m, h in sorted(H.items()):
            lines.append(f"  {m:46s} flagged {h['flagged']}/{h['bottlenecks']}; said 'none' on "
                         f"{h['said_none']}/{h['reports_with_bottleneck']} reports that have a single point; "
                         f"tolerance exact {h['tol_exact']}/{h['reports']} (over {h['tol_over']})"
                         + (f"; missing {h['missing']}" if h["missing"] else ""))
            summary[f"hint | {m}"] = dict(h)
    path = RES / f"exp8_summary{'_mock' if a.mock else ''}.json"
    json.dump(summary, open(path, "w"), indent=1)
    print("\n".join(lines))
    print("->", path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["gen", "scale", "self", "hint", "grade", "analyze"])
    ap.add_argument("--env-file")
    ap.add_argument("--models", nargs="+", default=[])
    ap.add_argument("--sizes", nargs="+", default=list(SIZES))
    ap.add_argument("--per-size", type=int, default=6)
    ap.add_argument("--reasoning", default="medium")
    ap.add_argument("--max-tokens", type=int, default=24000)
    ap.add_argument("--max-usd", type=float, default=1.0)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--split", action="store_true", help="self: state each_study conditions per study")
    a = ap.parse_args()
    if a.step == "gen":
        return step_gen(a)
    if a.step == "analyze":
        return step_analyze(a)
    if a.step != "grade" and not a.models:
        sys.exit("name the models with --models")
    from exp1.run_exp1 import load_key
    key = None if a.mock else load_key(a.env_file)
    budget, rng = Budget(a.max_usd), random.Random(0)
    {"scale": step_scale, "self": step_self, "hint": step_hint, "grade": step_grade}[a.step](a, key, budget, rng)
    print(f"spent ${budget.spent:.3f} (cap ${a.max_usd:.2f})")


if __name__ == "__main__":
    main()
