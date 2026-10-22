"""Source-level provenance for auditing the support of a conclusion.

Objects
-------
* A *derivation* is a multiset of evidence atoms (strings).
* A provenance polynomial in N[X] is a map  monomial -> coefficient, where a
  monomial is a sorted tuple of (atom, exponent) pairs.
* A source map sigma: atom -> source.  Projecting by sigma merges atoms that
  come from the same source (e.g. paraphrases of one paper).
* The witness family of a conclusion is the set of variable supports of the
  projected monomials; its minimal elements are the minimal witnesses.
* tau  = minimum transversal (fewest sources whose failure kills every witness)
* nu   = maximum number of pairwise source-disjoint witnesses
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import combinations
from typing import Callable, Dict, FrozenSet, Hashable, Iterable, List, Mapping, Optional, Sequence, Set, Tuple

import numpy as np

Atom = Hashable
Monomial = Tuple[Tuple[Atom, int], ...]
Family = Set[FrozenSet[Atom]]
INF = float("inf")


# ---------------------------------------------------------------- polynomials
def monomial(atoms: Iterable[Atom]) -> Monomial:
    c = Counter(atoms)
    return tuple(sorted(c.items(), key=lambda kv: repr(kv[0])))


class Poly:
    """Element of N[X]: sum over derivations of the product of their atoms."""

    def __init__(self, terms: Optional[Mapping[Monomial, int]] = None):
        self.terms: Dict[Monomial, int] = {m: c for m, c in (terms or {}).items() if c}

    @classmethod
    def from_derivations(cls, derivations: Iterable[Iterable[Atom]]) -> "Poly":
        t: Counter = Counter()
        for d in derivations:
            t[monomial(d)] += 1
        return cls(t)

    def __add__(self, other: "Poly") -> "Poly":
        t = Counter(self.terms)
        t.update(other.terms)
        return Poly(t)

    def __mul__(self, other: "Poly") -> "Poly":
        t: Counter = Counter()
        for m1, c1 in self.terms.items():
            for m2, c2 in other.terms.items():
                e = Counter(dict(m1))
                e.update(dict(m2))
                t[tuple(sorted(e.items(), key=lambda kv: repr(kv[0])))] += c1 * c2
        return Poly(t)

    def __eq__(self, other) -> bool:
        return isinstance(other, Poly) and self.terms == other.terms

    def __repr__(self) -> str:
        if not self.terms:
            return "0"
        parts = []
        for m, c in sorted(self.terms.items(), key=repr):
            mono = "·".join(f"{a}" + (f"^{e}" if e > 1 else "") for a, e in m) or "1"
            parts.append((f"{c}" if c > 1 else "") + mono)
        return " + ".join(parts)

    def variables(self) -> Set[Atom]:
        return {a for m in self.terms for a, _ in m}

    def supports(self) -> Family:
        """Variable supports of the monomials (the family A(c))."""
        return {frozenset(a for a, _ in m) for m in self.terms}

    def project(self, sigma: Mapping[Atom, Atom]) -> "Poly":
        """Homomorphism N[X] -> N[S] induced by x -> sigma(x)."""
        t: Counter = Counter()
        for m, c in self.terms.items():
            e: Counter = Counter()
            for a, k in m:
                e[sigma.get(a, a)] += k
            t[tuple(sorted(e.items(), key=lambda kv: repr(kv[0])))] += c
        return Poly(t)


# ------------------------------------------------------------------ semirings
@dataclass(frozen=True)
class Semiring:
    name: str
    zero: object
    one: object
    plus: Callable
    times: Callable
    idempotent: bool


BOOLEAN = Semiring("boolean", False, True, lambda a, b: a or b, lambda a, b: a and b, True)
COUNTING = Semiring("counting", 0, 1, lambda a, b: a + b, lambda a, b: a * b, False)
VITERBI = Semiring("viterbi", 0.0, 1.0, max, lambda a, b: a * b, True)
TROPICAL = Semiring("tropical", INF, 0.0, min, lambda a, b: a + b, True)
PROBABILITY = Semiring("probability", 0.0, 1.0, lambda a, b: a + b, lambda a, b: a * b, False)


def evaluate(p: Poly, K: Semiring, v: Mapping[Atom, object]) -> object:
    """Unique semiring homomorphism Eval_v: N[X] -> K extending v."""
    total = K.zero
    for m, c in p.terms.items():
        prod = K.one
        for a, e in m:
            for _ in range(e):
                prod = K.times(prod, v[a])
        for _ in range(c):
            total = K.plus(total, prod)
    return total


# --------------------------------------------------------- witness families
def minimal_sets(family: Iterable[FrozenSet[Atom]]) -> Family:
    fam = sorted(set(map(frozenset, family)), key=len)
    out: List[FrozenSet[Atom]] = []
    for s in fam:
        if not any(t <= s for t in out):
            out.append(s)
    return set(out)


def posbool(p: Poly) -> Family:
    """Image of p in PosBool: the antichain of minimal supports (monotone DNF)."""
    return minimal_sets(p.supports())


def witnesses(p: Poly, sigma: Optional[Mapping[Atom, Atom]] = None) -> Family:
    return posbool(p.project(sigma) if sigma else p)


def holds(W: Family, alive: Set[Atom]) -> bool:
    return any(w <= alive for w in W)


def survives_failure(W: Family, failed: Set[Atom]) -> bool:
    return any(not (w & failed) for w in W)


def rank(W: Family) -> int:
    return max((len(w) for w in W), default=0)


def _ground(W: Family) -> List[Atom]:
    return sorted({a for w in W for a in w}, key=repr)


def _milp(c, A, lb, ub, maximize=False):
    from scipy.optimize import Bounds, LinearConstraint, milp

    n = len(c)
    res = milp(
        c=-np.asarray(c, float) if maximize else np.asarray(c, float),
        constraints=LinearConstraint(np.asarray(A, float), lb, ub),
        integrality=np.ones(n),
        bounds=Bounds(np.zeros(n), np.ones(n)),
    )
    if not res.success:
        raise RuntimeError(res.message)
    return res


def tau(W: Family) -> float:
    """Minimum transversal of the minimal-witness hypergraph."""
    W = sorted(minimal_sets(W), key=lambda w: sorted(map(repr, w)))
    if not W:
        return 0
    if frozenset() in W:
        return INF
    ground = _ground(set(W))
    idx = {a: i for i, a in enumerate(ground)}
    A = np.zeros((len(W), len(ground)))
    for r, w in enumerate(W):
        for a in w:
            A[r, idx[a]] = 1
    res = _milp(np.ones(len(ground)), A, np.ones(len(W)), np.full(len(W), np.inf))
    return int(round(res.fun))


def min_transversal(W: Family) -> Set[Atom]:
    """One minimum transversal; ties are broken deterministically (sorted input)."""
    W = sorted(minimal_sets(W), key=lambda w: sorted(map(repr, w)))
    if not W or frozenset() in W:
        return set()
    ground = _ground(set(W))
    idx = {a: i for i, a in enumerate(ground)}
    A = np.zeros((len(W), len(ground)))
    for r, w in enumerate(W):
        for a in w:
            A[r, idx[a]] = 1
    res = _milp(np.ones(len(ground)), A, np.ones(len(W)), np.full(len(W), np.inf))
    return {ground[i] for i, x in enumerate(res.x) if x > 0.5}


def nu(W: Family) -> float:
    """Maximum number of pairwise disjoint minimal witnesses."""
    W = sorted(minimal_sets(W), key=lambda w: sorted(map(repr, w)))
    if not W:
        return 0
    if frozenset() in W:
        return INF
    ground = _ground(set(W))
    idx = {a: i for i, a in enumerate(ground)}
    A = np.zeros((len(ground), len(W)))
    for j, w in enumerate(W):
        for a in w:
            A[idx[a], j] = 1
    res = _milp(np.ones(len(W)), A, np.zeros(len(ground)), np.ones(len(ground)), maximize=True)
    return int(round(-res.fun))


def tau_bruteforce(W: Family) -> float:
    W = minimal_sets(W)
    if not W:
        return 0
    if frozenset() in W:
        return INF
    ground = _ground(W)
    for k in range(1, len(ground) + 1):
        for F in combinations(ground, k):
            if all(set(F) & w for w in W):
                return k
    return INF


def nu_bruteforce(W: Family) -> float:
    W = list(minimal_sets(W))
    if not W:
        return 0
    if frozenset() in W:
        return INF
    best = 0
    for k in range(1, len(W) + 1):
        for C in combinations(W, k):
            if all(not (a & b) for a, b in combinations(C, 2)):
                best = k
                break
    return best


def verify(W: Family, s: Atom) -> Family:
    """Mark source s as verified (cannot fail): remove it from every witness."""
    return minimal_sets(w - {s} for w in W)


def next_to_verify(W: Family) -> List[Tuple[Atom, float, float]]:
    """Rank sources by the gain in (tau, nu) obtained by verifying them."""
    t0, n0 = tau(W), nu(W)
    rows = []
    for s in _ground(W):
        W2 = verify(W, s)
        rows.append((s, tau(W2) - t0, nu(W2) - n0))
    rows.sort(key=lambda r: (-r[1], -r[2], repr(r[0])))
    return rows


def critical_sources(W: Family) -> Set[Atom]:
    """Sources in every minimal witness: single points of failure."""
    W = minimal_sets(W)
    if not W:
        return set()
    return set.intersection(*(set(w) for w in W))


# ----------------------------------------------------------------- baselines
def vote_count(p: Poly) -> int:
    """Number of derivations: evaluation in the counting semiring with v = 1."""
    return evaluate(p, COUNTING, {a: 1 for a in p.variables()})


def distinct_atom_count(p: Poly) -> int:
    """Number of distinct cited evidence atoms (a 'citation count')."""
    return len(p.variables())


def pagr_multiplicity(p: Poly) -> int:
    """PAGR (arXiv:2609.06127, §13.2) evidential multiplicity at fact level:
    the number of monomials that survive deletion of any single base fact
    (min over facts). Zero means a single point of failure."""
    mons = list(p.terms)
    if not mons:
        return 0
    facts = p.variables()
    return min(sum(1 for m in mons if all(a != f for a, _ in m)) for f in facts) if facts else len(mons)


def audit(p: Poly, sigma: Optional[Mapping[Atom, Atom]] = None) -> Dict[str, object]:
    W = witnesses(p, sigma)
    return {
        "votes": vote_count(p),
        "distinct_atoms": distinct_atom_count(p),
        "pagr_multiplicity": pagr_multiplicity(p),
        "n_sources": len(_ground(W)),
        "minimal_witnesses": sorted((sorted(map(str, w)) for w in W)),
        "tau": tau(W),
        "nu": nu(W),
        "rank": rank(W),
        "critical_sources": sorted(map(str, critical_sources(W))),
        "min_transversal": sorted(map(str, min_transversal(W))),
    }


# ------------------------------------------------------ lineage-graph case
def lineage_tau_nu(G, origin, target) -> int:
    """Proposition 3: on a directed lineage graph whose witnesses are the
    internal vertex sets of origin->target paths, tau = nu = local vertex
    connectivity (Menger), computed by max-flow."""
    import networkx as nx
    from networkx.algorithms.connectivity import local_node_connectivity

    if G.has_edge(origin, target):
        raise ValueError("origin and target must be non-adjacent")
    if not nx.has_path(G, origin, target):
        return 0
    return local_node_connectivity(G, origin, target)


def lineage_witnesses(G, origin, target, cutoff: Optional[int] = None) -> Family:
    import networkx as nx

    return minimal_sets(
        frozenset(path[1:-1]) for path in nx.all_simple_paths(G, origin, target, cutoff=cutoff)
    )


# ------------------------------------------------- conditions and auditing
# Witness families may mix two kinds of variables: sources (after the pushforward sigma) and
# auditable conditions r (citation bridges or inference guards). Conditions keep their identity
# under sigma (sigma.get(r, r) = r), so `witnesses(P, sigma)` already returns W_f over S + R.

def blocker(W: Family) -> Family:
    """All inclusion-minimal transversals of W (Berge's incremental algorithm).
    Exact; exponential in the worst case, fine at audit scale."""
    W = minimal_sets(W)
    if not W:
        return {frozenset()}          # nothing to destroy: the empty set already 'kills' support
    if frozenset() in W:
        return set()                  # an empty witness cannot be hit
    B: Family = {frozenset()}
    for w in sorted(W, key=lambda s: (len(s), sorted(map(repr, s)))):
        nxt = set()
        for b in B:
            if b & w:
                nxt.add(b)
            else:
                nxt.update(b | {x} for x in w)
        B = minimal_sets(nxt)
    return B


def restrict(W: Family, true: Iterable[Atom] = (), false: Iterable[Atom] = ()) -> Family:
    """Cofactor of the monotone function with minimal witnesses W: variables in `true` fixed to 1
    (removed from witnesses), variables in `false` fixed to 0 (witnesses using them dropped)."""
    t, f = set(true), set(false)
    return minimal_sets(w - t for w in W if not (w & f))


def source_tau(W: Family, conditions: Iterable[Atom] = ()) -> float:
    """tau_S: fewest *sources* whose withdrawal removes all support, every condition already fixed.
    Witnesses must contain sources only. Conventions: no witness -> 0; empty witness -> inf."""
    W = minimal_sets(W)
    cond = set(conditions)
    assert not any(w & cond for w in W), "fix every condition before computing tau_S"
    return tau(W)


def verification_bounds(W: Family, conditions: Iterable[Atom], confirmed: Iterable[Atom] = (),
                        rejected: Iterable[Atom] = ()) -> Tuple[float, float]:
    """[L, H]: source resilience if every unresolved condition fails (L) or holds (H).
    For any condition assignment compatible with the audit outcomes, L <= tau_S <= H."""
    R, T, D = set(conditions), set(confirmed), set(rejected)
    U = R - T - D
    lo = source_tau(restrict(W, true=T, false=D | U), R)
    hi = source_tau(restrict(W, true=T | U, false=D), R)
    return lo, hi


def audit_card(W: Family, conditions: Iterable[Atom], confirmed: Iterable[Atom] = (),
               rejected: Iterable[Atom] = ()) -> Dict[str, object]:
    """Everything an auditor needs for one conclusion under the current audit state."""
    R, T, D = set(conditions), set(confirmed), set(rejected)
    U = sorted(R - T - D, key=repr)
    L, H = verification_bounds(W, R, T, D)
    current = restrict(W, true=T, false=D)                 # unresolved conditions still free
    certs = sorted(blocker(current), key=lambda c: (len(c), sorted(map(repr, c))))
    questions = []
    for r in U:
        yes = verification_bounds(W, R, T | {r}, D)
        no = verification_bounds(W, R, T, D | {r})
        routes = sum(1 for w in current if r in w)
        if yes != no or routes:
            questions.append({"condition": r, "routes_using_it": routes,
                              "if_confirmed": yes, "if_rejected": no, "if_unresolved": (L, H)})
    src_only = source_tau(restrict(W, true=R), R)          # every condition assumed to hold
    return {
        "source_only_tau": src_only,
        "tolerates_any": None if src_only in (0, INF) else src_only - 1,
        "interval": (L, H),
        "failure_certificates": [sorted(map(str, c)) for c in certs],
        "condition_bottlenecks": [sorted(map(str, c)) for c in certs if c and set(c) <= R and len(c) == 1],
        "questions": questions,
    }


def verification_plan(W: Family, conditions: Iterable[Atom], k: int, confirmed: Iterable[Atom] = (),
                      rejected: Iterable[Atom] = (), cost: Optional[Mapping[Atom, float]] = None):
    """Minimum-cost k-plan: a set P of unresolved conditions such that, if every condition in P is confirmed,
    L >= k. Returns (P, cost) or None when no plan exists (H < k). Exact, by enumeration in order of cost;
    fine at audit scale (tens of conditions)."""
    import itertools
    R, T, D = set(conditions), set(confirmed), set(rejected)
    U = sorted(R - T - D, key=repr)
    c = {u: (cost or {}).get(u, 1.0) for u in U}
    if verification_bounds(W, R, T, D)[1] < k:
        return None
    best = None
    for n in range(len(U) + 1):
        for P in itertools.combinations(U, n):
            w = sum(c[u] for u in P)
            if best is not None and w >= best[1]:
                continue
            if verification_bounds(W, R, T | set(P), D)[0] >= k:
                best = (sorted(P, key=repr), w)
        if best is not None and cost is None:
            break                                  # unit costs: the first size that works is optimal
    return best
