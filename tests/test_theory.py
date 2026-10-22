"""Randomised checks of every statement in paper/theory.tex (impossibility, characterisation,
robust soundness, fact- vs source-level, failure probability, composition).

Robust soundness is checked against *semantics* (forward chaining of a Horn program), not against
the provenance machinery, so it tests that tau really is the minimum number of failed sources that
can make a conclusion unsupported.
"""
import itertools
import random
import unittest

from evaudit.core import (BOOLEAN, COUNTING, PROBABILITY, TROPICAL, VITERBI, Poly, evaluate, minimal_sets,
                          nu, pagr_multiplicity, tau, witnesses)


def closure(facts, rules):
    """Least model of a propositional Horn program: rules are (frozenset body, head)."""
    m = set(facts)
    changed = True
    while changed:
        changed = False
        for body, head in rules:
            if head not in m and body <= m:
                m.add(head)
                changed = True
    return m


def random_program(rng, n_atoms=7, n_sources=4, n_derived=5, n_rules=9):
    atoms = [f"x{i}" for i in range(n_atoms)]
    sigma = {a: f"s{rng.randrange(n_sources)}" for a in atoms}
    derived = [f"d{i}" for i in range(n_derived)]
    rules = []
    for _ in range(n_rules):
        head = rng.choice(derived)
        pool = atoms + [d for d in derived if d < head]  # acyclic, but derived atoms may chain
        rules.append((frozenset(rng.sample(pool, rng.randint(1, 3))), head))
    return atoms, sigma, rules, derived


def semantic_witnesses(atoms, rules, goal):
    """Minimal sets of evidence atoms whose closure contains goal (by enumeration)."""
    sup = [frozenset(E) for r in range(len(atoms) + 1) for E in itertools.combinations(atoms, r)
           if goal in closure(E, rules)]
    return minimal_sets(sup)


def project(W, sigma):
    return minimal_sets(frozenset(sigma[a] for a in w) for w in W)


class Theorem1RobustSoundness(unittest.TestCase):
    def test_tau_is_min_number_of_failed_sources(self):
        rng = random.Random(1)
        checked = 0
        for _ in range(250):
            atoms, sigma, rules, derived = random_program(rng)
            goal = rng.choice(derived)
            W = semantic_witnesses(atoms, rules, goal)
            if not W:
                continue
            Ws = project(W, sigma)
            sources = sorted(set(sigma.values()))
            t = tau(Ws)
            semantic_min = None
            for r in range(len(sources) + 1):
                for F in itertools.combinations(sources, r):
                    correct = [a for a in atoms if sigma[a] not in F]
                    supported = goal in closure(correct, rules)
                    is_transversal = all(set(F) & w for w in Ws)
                    # (i) soundness: F not a transversal  =>  goal follows from correct sources
                    # (ii) tightness: F a transversal     =>  least model of correct sources omits goal
                    self.assertEqual(supported, not is_transversal)
                    if not supported and semantic_min is None:
                        semantic_min = r
            self.assertEqual(t, semantic_min)
            checked += 1
        self.assertGreater(checked, 100)


class Theorem2Characterisation(unittest.TestCase):
    def test_D_moves_preserve_source_witnesses(self):
        rng = random.Random(2)
        for _ in range(300):
            atoms = [f"x{i}" for i in range(6)]
            sigma = {a: f"s{rng.randrange(3)}" for a in atoms}
            ders = [rng.sample(atoms, rng.randint(1, 3)) for _ in range(rng.randint(1, 4))]
            P = Poly.from_derivations(ders)
            W = witnesses(P, sigma)
            # D1 duplicate a derivation / raise an exponent
            d = rng.choice(ders)
            self.assertEqual(witnesses(Poly.from_derivations(ders + [d, d + [d[0]]]), sigma), W)
            # D2 add a redundant derivation (superset of an existing one)
            self.assertEqual(witnesses(Poly.from_derivations(ders + [d + rng.sample(atoms, 2)]), sigma), W)
            # D3 replace one occurrence of an atom by another atom from the same source
            x = rng.choice(d)
            same = [a for a in atoms if sigma[a] == sigma[x]]
            d2 = [rng.choice(same) if a == x else a for a in d]
            self.assertEqual(witnesses(Poly.from_derivations(ders + [d2]), sigma), W)

    def test_canonical_form(self):
        """Equal source witness families  =>  equal canonical forms under D1-D3 (the converse direction)."""
        rng = random.Random(3)
        for _ in range(300):
            atoms = [f"x{i}" for i in range(6)]
            sigma = {a: f"s{rng.randrange(3)}" for a in atoms}
            rep = {}
            for a in atoms:
                rep.setdefault(sigma[a], a)

            def canon(P):
                return minimal_sets(frozenset(rep[sigma[a]] for a in s) for s in P.supports())

            P = Poly.from_derivations([rng.sample(atoms, rng.randint(1, 3)) for _ in range(rng.randint(1, 4))])
            Q = Poly.from_derivations([rng.sample(atoms, rng.randint(1, 3)) for _ in range(rng.randint(1, 4))])
            self.assertEqual(witnesses(P, sigma) == witnesses(Q, sigma), canon(P) == canon(Q))


class Theorem3Impossibility(unittest.TestCase):
    def test_no_symmetric_semiring_score_separates_independent_from_relayed(self):
        for K, c in [(BOOLEAN, True), (COUNTING, 1), (VITERBI, .7), (TROPICAL, 2.0), (PROBABILITY, .3)]:
            for k in range(2, 6):
                indep = Poly.from_derivations([[f"x{i}"] for i in range(k)])        # sigma(x_i) = s_i
                relay = Poly.from_derivations([[f"y{i}"] for i in range(k)])        # sigma(y_i) = s
                s_ind = {f"x{i}": f"s{i}" for i in range(k)}
                s_rel = {f"y{i}": "s" for i in range(k)}
                for P, Q in [(indep, relay), (indep.project(s_ind), relay.project(s_rel))]:
                    vP = evaluate(P, K, {a: c for a in P.variables()})
                    vQ = evaluate(Q, K, {a: c for a in Q.variables()})
                    self.assertEqual(vP, vQ)
                # tau separates them
                self.assertEqual(tau(witnesses(indep, s_ind)), k)
                self.assertEqual(tau(witnesses(relay, s_rel)), 1)


class Proposition6Algebra(unittest.TestCase):
    def test_and_or(self):
        rng = random.Random(4)
        for _ in range(400):
            S = [f"s{i}" for i in range(7)]

            def fam(pool):
                return minimal_sets(frozenset(rng.sample(pool, rng.randint(1, 3))) for _ in range(rng.randint(1, 4)))

            A, B = fam(S), fam(S)
            conj = minimal_sets(a | b for a in A for b in B)
            disj = minimal_sets(A | B)
            self.assertEqual(tau(conj), min(tau(A), tau(B)))
            self.assertLessEqual(max(tau(A), tau(B)), tau(disj))
            self.assertLessEqual(tau(disj), tau(A) + tau(B))
            A2, B2 = fam(S[:3]), fam(S[3:])                                   # source-disjoint
            self.assertEqual(tau(minimal_sets(A2 | B2)), tau(A2) + tau(B2))
            self.assertLessEqual(nu(A), tau(A))


class Proposition7FactVsSource(unittest.TestCase):
    def test_fact_level_overestimates_and_pagr(self):
        rng = random.Random(5)
        strict = 0
        for _ in range(400):
            atoms = [f"x{i}" for i in range(7)]
            sigma = {a: f"s{rng.randrange(3)}" for a in atoms}
            P = Poly.from_derivations([rng.sample(atoms, rng.randint(1, 3)) for _ in range(rng.randint(1, 5))])
            t_fact, t_src = tau(witnesses(P)), tau(witnesses(P, sigma))
            self.assertLessEqual(t_src, t_fact)
            strict += t_src < t_fact
            self.assertEqual(pagr_multiplicity(P) == 0, t_fact == 1)
        self.assertGreater(strict, 0)
        # one paper paraphrased into m facts: fact-level tau = m, source-level tau = 1
        for m in range(1, 6):
            P = Poly.from_derivations([[f"x{i}"] for i in range(m)])
            self.assertEqual(tau(witnesses(P)), m)
            self.assertEqual(tau(witnesses(P, {f"x{i}": "paper" for i in range(m)})), 1)


class Proposition8Reliability(unittest.TestCase):
    def test_failure_probability_leading_term(self):
        rng = random.Random(6)
        for _ in range(60):
            S = [f"s{i}" for i in range(6)]
            W = minimal_sets(frozenset(rng.sample(S, rng.randint(1, 3))) for _ in range(rng.randint(1, 5)))
            ground = sorted({s for w in W for s in w})
            n = len(ground)
            trans = [F for r in range(n + 1) for F in itertools.combinations(ground, r) if all(set(F) & w for w in W)]
            t = tau(W)
            N_t = sum(len(F) == t for F in trans)
            for p in [1e-3, 1e-4]:
                exact = sum(p ** len(F) * (1 - p) ** (n - len(F)) for F in trans)
                self.assertAlmostEqual(exact / (N_t * p ** t), 1.0, delta=50 * p * 2 ** n)



class Proposition11Procedure(unittest.TestCase):
    def test_coarsening_lowers_tau_and_verification_raises_it(self):
        from evaudit.core import verify
        rng = random.Random(7)
        for _ in range(300):
            atoms = [f"x{i}" for i in range(7)]
            sigma = {a: f"s{rng.randrange(5)}" for a in atoms}
            merge = {f"s{i}": f"g{rng.randrange(3)}" for i in range(5)}      # coarser source map
            coarse = {a: merge[s] for a, s in sigma.items()}
            P = Poly.from_derivations([rng.sample(atoms, rng.randint(1, 3)) for _ in range(rng.randint(1, 5))])
            W = witnesses(P, sigma)
            self.assertLessEqual(tau(witnesses(P, coarse)), tau(W))
            s = rng.choice(sorted({x for w in W for x in w}))
            self.assertGreaterEqual(tau(verify(W, s)), tau(W))



class ConditionsAndPartialVerification(unittest.TestCase):
    """Joint failure certificates over sources + conditions, and the partial-verification interval."""

    def _random(self, rng):
        from evaudit.core import Poly, witnesses
        atoms = [f"x{i}" for i in range(5)]
        sigma = {a: f"s{rng.randrange(3)}" for a in atoms}
        conds = [f"r{i}" for i in range(3)]
        ders = [rng.sample(atoms, rng.randint(1, 2)) + rng.sample(conds, rng.randint(0, 2))
                for _ in range(rng.randint(1, 4))]
        return witnesses(Poly.from_derivations(ders), sigma), set(conds), sorted(set(sigma.values()))

    def test_blocker_is_exactly_the_minimal_transversals(self):
        from evaudit.core import blocker
        rng = random.Random(11)
        for _ in range(300):
            W, R, S = self._random(rng)
            ground = sorted({x for w in W for x in w})
            brute = minimal_sets(frozenset(C) for k in range(len(ground) + 1)
                                 for C in itertools.combinations(ground, k) if all(set(C) & w for w in W))
            self.assertEqual(blocker(W), brute)

    def test_bounds_hold_for_every_compatible_assignment_and_nest(self):
        from evaudit.core import restrict, source_tau, verification_bounds
        rng = random.Random(12)
        for _ in range(300):
            W, R, S = self._random(rng)
            Rl = sorted(R)
            T = set(rng.sample(Rl, rng.randint(0, 1)))
            D = set(rng.sample([r for r in Rl if r not in T], rng.randint(0, 1)))
            U = sorted(R - T - D)
            L, H = verification_bounds(W, R, T, D)
            self.assertLessEqual(L, H)
            for bits in itertools.product([0, 1], repeat=len(U)):
                on = T | {u for u, b in zip(U, bits) if b}
                off = D | {u for u, b in zip(U, bits) if not b}
                t = source_tau(restrict(W, true=on, false=off), R)
                self.assertLessEqual(L, t)
                self.assertLessEqual(t, H)
            if U:  # a correct conclusive answer about one unresolved condition nests the interval
                u = U[0]
                for L2, H2 in [verification_bounds(W, R, T | {u}, D), verification_bounds(W, R, T, D | {u})]:
                    self.assertLessEqual(L, L2)
                    self.assertLessEqual(H2, H)

    def test_running_example(self):
        from evaudit.core import audit_card
        sig = {"x_a": "a", "x_b": "b", "x_c": "c"}
        W = witnesses(Poly.from_derivations([["r", "x_a"], ["r", "x_b", "x_c"]]), sig)
        card = audit_card(W, {"r"})
        self.assertEqual(card["failure_certificates"], [["r"], ["a", "b"], ["a", "c"]])
        self.assertEqual(card["interval"], (0, 2))
        self.assertEqual(card["questions"][0]["if_confirmed"], (2, 2))
        self.assertEqual(card["questions"][0]["if_rejected"], (0, 0))
        self.assertEqual(card["tolerates_any"], 1)
        W2 = witnesses(Poly.from_derivations([["r1", "x_a"], ["r2", "x_b", "x_c"]]), sig)
        card2 = audit_card(W2, {"r1", "r2"})
        self.assertEqual(card2["condition_bottlenecks"], [])
        q = {x["condition"]: x for x in card2["questions"]}
        self.assertEqual(q["r1"]["if_confirmed"], (1, 2))
        self.assertEqual(q["r1"]["if_rejected"], (0, 1))


if __name__ == "__main__":
    unittest.main()


class AuditCardCorollary(unittest.TestCase):
    """Corollary (what an audit card certifies): with a grouping no finer than the failure domains and correct
    confirmations, fewer than L failing domains leave a witness whose sources are intact and whose conditions hold."""

    def test_random(self):
        import itertools
        import random
        from evaudit.core import verification_bounds
        rng = random.Random(7)
        for _ in range(300):
            domains = [f"d{i}" for i in range(rng.randint(2, 5))]
            conds = [f"r{i}" for i in range(rng.randint(1, 3))]
            # represented sources: a coarsening of the domains
            k = rng.randint(1, len(domains))
            grp = {d: f"s{rng.randrange(k)}" for d in domains}
            W_dom = []
            for _ in range(rng.randint(1, 4)):
                w = set(rng.sample(domains, rng.randint(1, len(domains))))
                w |= set(rng.sample(conds, rng.randint(0, len(conds))))
                W_dom.append(frozenset(w))
            W_rep = [frozenset(grp.get(x, x) for x in w) for w in W_dom]
            truth = {c: rng.random() < .5 for c in conds}
            confirmed = [c for c in conds if truth[c] and rng.random() < .6]
            rejected = [c for c in conds if not truth[c] and rng.random() < .6]
            L, H = verification_bounds(W_rep, conds, confirmed, rejected)
            for n in range(len(domains) + 1):
                if n >= L:
                    break
                for F in itertools.combinations(domains, n):
                    ok = any(not (w & set(F)) and all(truth[c] for c in w if c in conds) for w in W_dom)
                    self.assertTrue(ok, (W_dom, grp, F, L))


class VerificationPlans(unittest.TestCase):
    def test_example_and_bruteforce(self):
        import itertools
        import random
        from evaudit.core import verification_plan, verification_bounds
        W = [frozenset({'A', 'c', 'e'}), frozenset({'B', 'e'})]
        self.assertEqual(verification_plan(W, {'c', 'e'}, 1), (['e'], 1.0))
        self.assertEqual(verification_plan(W, {'c', 'e'}, 2), (['c', 'e'], 2.0))
        self.assertIsNone(verification_plan(W, {'c', 'e'}, 1, rejected={'e'}))
        rng = random.Random(3)
        for _ in range(200):
            S = ['s%d' % i for i in range(rng.randint(1, 4))]
            R = ['r%d' % i for i in range(rng.randint(1, 4))]
            W = [frozenset(rng.sample(S, rng.randint(1, len(S))) + rng.sample(R, rng.randint(0, len(R))))
                 for _ in range(rng.randint(1, 4))]
            k = rng.randint(1, 3)
            p = verification_plan(W, set(R), k)
            H = verification_bounds(W, set(R))[1]
            self.assertEqual(p is None, H < k)          # a plan exists iff H >= k
            if p is not None:                           # minimal size, checked by brute force
                sizes = [n for n in range(len(R) + 1) for P in itertools.combinations(R, n)
                         if verification_bounds(W, set(R), set(P))[0] >= k]
                self.assertEqual(len(p[0]), min(sizes))
