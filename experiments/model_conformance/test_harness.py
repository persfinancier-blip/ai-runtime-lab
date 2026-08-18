import tempfile
import unittest
from pathlib import Path
from experiments.model_conformance.harness import CORPUS,bounded_traces,compare,load_trace,save_trace

class ConformanceTests(unittest.TestCase):
 def test_correct_kernel_conforms_on_corpus(self):
  for trace in CORPUS:
   with self.subTest(trace=trace):
    result=compare(trace);self.assertTrue(result["ok"],result)
 def test_correct_kernel_conforms_on_all_depth3_traces(self):
  for trace in bounded_traces(3):
   result=compare(trace)
   self.assertTrue(result["ok"],result)
 def test_reopen_done_reports_first_divergence(self):
  r=compare(["claim","intent","effect_ok","append_evidence","complete","duplicate"],"reopen_done");self.assertFalse(r["ok"]);self.assertEqual(r["step"],6);self.assertIn("phase",r["fields"])
 def test_stale_fence_mutation_reports_divergence(self):
  r=compare(["claim","intent","stale_mutate"],"stale_fence");self.assertFalse(r["ok"]);self.assertEqual(r["step"],3);self.assertIn("confirmed",r["fields"])
 def test_invalid_evidence_completion_reports_divergence(self):
  r=compare(["claim","intent","effect_ok","append_evidence","invalidate","complete"],"invalid_completion");self.assertFalse(r["ok"]);self.assertEqual(r["step"],6);self.assertIn("phase",r["fields"])
 def test_unknown_retry_reports_duplicate_effect(self):
  r=compare(["claim","intent","effect_unknown","effect_unknown"],"unknown_retry");self.assertFalse(r["ok"]);self.assertEqual(r["step"],4);self.assertIn("effect_count",r["fields"])
 def test_terminal_invalidation_semantics_reports_divergence(self):
  r=compare(["claim","intent","effect_ok","append_evidence","complete","invalidate"],"terminal_invalidation");self.assertFalse(r["ok"]);self.assertEqual(r["step"],6);self.assertIn("phase",r["fields"])
 def test_trace_roundtrip_is_versioned(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/"trace.json";trace=CORPUS[1];save_trace(path,trace);self.assertEqual(load_trace(path),trace)
if __name__=="__main__":unittest.main()
