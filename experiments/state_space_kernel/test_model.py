import unittest
from experiments.state_space_kernel.model import explore,replay,randomized
class Tests(unittest.TestCase):
 def test_correct(self): self.assertTrue(explore(8)["ok"])
 def test_split(self):
  r=explore(8,"split_unsafe");self.assertFalse(r["ok"]);self.assertIn("done_without_current_evidence",r["violations"]);self.assertEqual(replay(r["trace"],"split_unsafe")[0],r["violations"])
 def test_reopen(self):
  r=explore(8,"reopen_unsafe");self.assertFalse(r["ok"]);self.assertIn("terminal_reopened",r["violations"])
 def test_stale(self):
  r=explore(8,"stale_unsafe");self.assertFalse(r["ok"]);self.assertIn("duplicate_effect",r["violations"])
 def test_random(self):self.assertTrue(randomized()["ok"])
if __name__=="__main__":unittest.main()
