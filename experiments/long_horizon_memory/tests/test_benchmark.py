import unittest

from experiments.long_horizon_memory.benchmark import (
    STRATEGIES,
    corpus,
    evaluate,
    run_all,
)


class LongHorizonMemoryBenchmarkTests(unittest.TestCase):
    def test_all_four_strategies_run_on_same_corpus(self):
        self.assertEqual(
            set(STRATEGIES),
            {"recency", "similarity", "typed_temporal_graph", "bounded_hybrid"},
        )
        for strategy in STRATEGIES.values():
            self.assertEqual(len(evaluate(strategy)["rows"]), len(corpus()))

    def test_recency_loses_long_horizon_current_fact(self):
        result = evaluate(STRATEGIES["recency"])
        row = next(r for r in result["rows"] if r["case"] == "long_horizon_noise")
        self.assertEqual(row["current_causal_recall"], 0.0)

    def test_similarity_retrieves_stale_superseded_memory(self):
        result = evaluate(STRATEGIES["similarity"])
        stale_cases = [r for r in result["rows"] if r["stale_intrusion"] > 0]
        self.assertGreaterEqual(len(stale_cases), 4)
        self.assertGreater(result["mean_stale_intrusion"], 0.20)

    def test_typed_graph_preserves_current_causal_facts_without_stale_intrusion(self):
        result = evaluate(STRATEGIES["typed_temporal_graph"])
        self.assertEqual(result["mean_current_causal_recall"], 1.0)
        self.assertEqual(result["mean_stale_intrusion"], 0.0)

    def test_hybrid_preserves_current_causal_facts_without_stale_intrusion(self):
        result = evaluate(STRATEGIES["bounded_hybrid"])
        self.assertEqual(result["mean_current_causal_recall"], 1.0)
        self.assertEqual(result["mean_stale_intrusion"], 0.0)

    def test_causal_case_requires_reason_and_decision(self):
        for name in ("typed_temporal_graph", "bounded_hybrid"):
            row = next(
                r
                for r in evaluate(STRATEGIES[name])["rows"]
                if r["case"] == "causal_chain"
            )
            self.assertEqual(row["current_causal_recall"], 1.0)

    def test_expected_aggregate_snapshot(self):
        results = run_all()
        self.assertAlmostEqual(results["recency"]["mean_current_causal_recall"], 5 / 6)
        self.assertAlmostEqual(results["recency"]["mean_stale_intrusion"], 1 / 6)
        self.assertAlmostEqual(results["similarity"]["mean_current_causal_recall"], 1.0)
        self.assertAlmostEqual(results["similarity"]["mean_stale_intrusion"], 2 / 9)


if __name__ == "__main__":
    unittest.main()
