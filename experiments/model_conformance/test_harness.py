import tempfile
import unittest
from pathlib import Path

from experiments.model_conformance.harness import CORPUS, compare, load_trace, save_trace


class ConformanceTests(unittest.TestCase):
    def test_correct_kernel_conforms_on_corpus(self):
        for trace in CORPUS:
            with self.subTest(trace=trace):
                self.assertTrue(compare(trace)["ok"], compare(trace))

    def test_reopen_done_reports_first_divergence(self):
        trace = ["claim", "intent", "effect_ok", "append_evidence", "complete", "duplicate"]
        result = compare(trace, "reopen_done")
        self.assertFalse(result["ok"])
        self.assertEqual(result["step"], 6)
        self.assertIn("phase", result["fields"])

    def test_stale_fence_mutation_reports_divergence(self):
        result = compare(["claim", "intent", "stale_mutate"], "stale_fence")
        self.assertFalse(result["ok"])
        self.assertEqual(result["step"], 3)
        self.assertIn("confirmed", result["fields"])

    def test_invalid_evidence_completion_reports_divergence(self):
        trace = ["claim", "intent", "effect_ok", "append_evidence", "invalidate", "complete"]
        result = compare(trace, "invalid_completion")
        self.assertFalse(result["ok"])
        self.assertEqual(result["step"], 6)
        self.assertIn("phase", result["fields"])

    def test_unknown_retry_reports_duplicate_effect(self):
        trace = ["claim", "intent", "effect_unknown", "effect_unknown"]
        result = compare(trace, "unknown_retry")
        self.assertFalse(result["ok"])
        self.assertEqual(result["step"], 4)
        self.assertIn("effect_count", result["fields"])

    def test_terminal_invalidation_semantics_reports_divergence(self):
        trace = ["claim", "intent", "effect_ok", "append_evidence", "complete", "invalidate"]
        result = compare(trace, "terminal_invalidation")
        self.assertFalse(result["ok"])
        self.assertEqual(result["step"], 6)
        self.assertIn("phase", result["fields"])

    def test_trace_roundtrip_is_versioned(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "trace.json"
            trace = CORPUS[1]
            save_trace(path, trace)
            self.assertEqual(load_trace(path), trace)


if __name__ == "__main__":
    unittest.main()
