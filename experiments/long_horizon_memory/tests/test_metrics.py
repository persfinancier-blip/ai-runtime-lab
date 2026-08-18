import unittest

from experiments.long_horizon_memory.benchmark import STRATEGIES, evaluate
from experiments.long_horizon_memory.metrics import surface_relevance


class MemoryMetricSeparationTests(unittest.TestCase):
    def test_similarity_can_be_surface_relevant_while_stale(self):
        relevance = surface_relevance("similarity")
        correctness = evaluate(STRATEGIES["similarity"])
        self.assertGreater(relevance, 0.85)
        self.assertEqual(correctness["mean_current_causal_recall"], 1.0)
        self.assertGreater(correctness["mean_stale_intrusion"], 0.20)

    def test_temporal_graph_removes_stale_intrusion(self):
        result = evaluate(STRATEGIES["typed_temporal_graph"])
        self.assertEqual(result["mean_current_causal_recall"], 1.0)
        self.assertEqual(result["mean_stale_intrusion"], 0.0)


if __name__ == "__main__":
    unittest.main()
