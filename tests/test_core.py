import random
import unittest

import networkx as nx

from evaudit.core import (BOOLEAN, COUNTING, TROPICAL, VITERBI, INF, Poly, audit, critical_sources, evaluate,
                          lineage_tau_nu, lineage_witnesses, minimal_sets, next_to_verify, nu, nu_bruteforce,
                          pagr_multiplicity, posbool, rank, tau, tau_bruteforce, verify, vote_count, witnesses)


def rand_family(rng, n_src=7, n_sets=6, max_size=3):
    src = [f"s{i}" for i in range(n_src)]
    return {frozenset(rng.sample(src, rng.randint(1, max_size))) for _ in range(n_sets)}


def rand_poly(rng, atoms, n_der=5, max_len=4):
    return Poly.from_derivations([rng.choices(atoms, k=rng.randint(1, max_len)) for _ in range(n_der)])


class Examples(unittest.TestCase):
    def test_triangle(self):
        # three models, each uses two of three papers p, q, r
        p = Poly.from_derivations([["p", "q"], ["q", "r"], ["p", "r"]])
        a = audit(p)
        self.assertEqual((a["votes"], a["tau"], a["nu"]), (3, 2, 1))

    def test_shared_paper(self):
        # three models each add their own step M_i on top of the same paper p
        p = Poly.from_derivations([["p", "M1"], ["p", "M2"], ["p", "M3"]])
        a = audit(p)
        self.assertEqual((a["votes"], a["tau"], a["nu"]), (3, 1, 1))
        self.assertEqual(a["critical_sources"], ["p"])

    def test_paraphrase_inflates_counts_not_tau(self):
        # one paper, cited through three paraphrased excerpts e1..e3, each used alone
        p = Poly.from_derivations([["e1"], ["e2"], ["e3"]])
        sigma = {"e1": "paperA", "e2": "paperA", "e3": "paperA"}
        a_fact, a_src = audit(p), audit(p, sigma)
        self.assertEqual(a_fact["tau"], 3)              # fact level: looks robust
        self.assertEqual(a_fact["pagr_multiplicity"], 2)  # PAGR: no single point of failure
        self.assertEqual(a_src["tau"], 1)                # source level: one paper
        self.assertEqual(a_src["nu"], 1)

    def test_independent_sources(self):
        p = Poly.from_derivations([["e1"], ["e2"], ["e3"]])
        sigma = {"e1": "A", "e2": "B", "e3": "C"}
        self.assertEqual((audit(p, sigma)["tau"], audit(p, sigma)["nu"]), (3, 3))

    def test_conventions(self):
        self.assertEqual(tau(set()), 0)
        self.assertEqual(nu(set()), 0)
        self.assertEqual(tau({frozenset()}), INF)

    def test_semiring_eval(self):
        p = Poly.from_derivations([["x", "y"], ["x", "z"]])
        self.assertTrue(evaluate(p, BOOLEAN, {"x": True, "y": False, "z": True}))
        self.assertFalse(evaluate(p, BOOLEAN, {"x": False, "y": True, "z": True}))
        self.assertEqual(evaluate(p, COUNTING, {"x": 1, "y": 1, "z": 1}), 2)
        self.assertAlmostEqual(evaluate(p, VITERBI, {"x": .9, "y": .5, "z": .8}), .72)
        self.assertEqual(evaluate(p, TROPICAL, {"x": 1, "y": 5, "z": 2}), 3)


class Proposition1(unittest.TestCase):
    """Duplication invariance holds exactly for idempotent evaluations."""

    def test_duplicate_derivation(self):
        rng = random.Random(0)
        atoms = list("abcdef")
        for _ in range(200):
            p = rand_poly(rng, atoms)
            m = rng.choice(list(p.terms))
            dup = p + Poly({m: 1})
            for K, gen in [(BOOLEAN, lambda: rng.random() < .6), (VITERBI, rng.random),
                           (TROPICAL, lambda: rng.randint(0, 9))]:
                v = {a: gen() for a in atoms}
                self.assertEqual(evaluate(p, K, v), evaluate(dup, K, v))
            self.assertEqual(posbool(p), posbool(dup))
            self.assertEqual(vote_count(dup), vote_count(p) + 1)

    def test_same_source_rename(self):
        # replace an atom in one derivation by a fresh same-source atom
        rng = random.Random(1)
        for _ in range(200):
            atoms = [f"x{i}" for i in range(6)]
            sigma = {a: f"S{i % 3}" for i, a in enumerate(atoms)}
            ders = [rng.choices(atoms, k=rng.randint(1, 3)) for _ in range(4)]
            d = ders[0]
            old = d[0]
            new = old + "_para"
            sigma[new] = sigma[old]
            ders2 = [[new if (j == 0 and a == old) else a for a in d] for j, d in enumerate(ders)]
            W1 = witnesses(Poly.from_derivations(ders), sigma)
            W2 = witnesses(Poly.from_derivations(ders2), sigma)
            self.assertEqual(W1, W2)

    def test_absorption(self):
        p = Poly.from_derivations([["a"], ["a", "b"]])
        self.assertEqual(posbool(p), {frozenset({"a"})})


class Proposition2(unittest.TestCase):
    def test_bounds_and_exactness(self):
        rng = random.Random(2)
        for _ in range(300):
            W = minimal_sets(rand_family(rng))
            t, n, r = tau(W), nu(W), rank(W)
            self.assertEqual(t, tau_bruteforce(W))
            self.assertEqual(n, nu_bruteforce(W))
            self.assertLessEqual(n, t)
            self.assertLessEqual(t, r * n)


class Proposition3(unittest.TestCase):
    def test_menger_on_random_dags(self):
        rng = random.Random(3)
        checked = 0
        for _ in range(150):
            G = nx.gnp_random_graph(8, 0.35, seed=rng.randint(0, 10**6), directed=True)
            G = nx.DiGraph([(u, v) for u, v in G.edges() if u < v])  # make it a DAG
            G.add_nodes_from(range(8))
            G = nx.relabel_nodes(G, {0: "o", 7: "c"})
            if G.has_edge("o", "c"):
                G.remove_edge("o", "c")
            W = lineage_witnesses(G, "o", "c")
            if not W:
                continue
            k = lineage_tau_nu(G, "o", "c")
            self.assertEqual(tau(W), k)
            self.assertEqual(nu(W), k)
            checked += 1
        self.assertGreater(checked, 50)


class Proposition4(unittest.TestCase):
    def test_verification_monotone(self):
        rng = random.Random(4)
        for _ in range(200):
            W = minimal_sets(rand_family(rng))
            s = rng.choice(sorted({a for w in W for a in w}))
            W2 = verify(W, s)
            self.assertGreaterEqual(tau(W2), tau(W))
            self.assertGreaterEqual(nu(W2), nu(W))

    def test_next_to_verify_picks_bottleneck(self):
        W = witnesses(Poly.from_derivations([["p", "M1"], ["p", "M2"], ["p", "M3"]]))
        best = next_to_verify(W)[0]
        self.assertEqual(best[0], "p")
        self.assertEqual(critical_sources(W), {"p"})


if __name__ == "__main__":
    unittest.main()
