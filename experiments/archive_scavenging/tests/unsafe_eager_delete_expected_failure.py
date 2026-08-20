import tempfile,unittest
from experiments.archive_scavenging.protocol import UnsafeEagerDelete
from experiments.archive_scavenging.tests.test_protocol import Layer
class Unsafe(unittest.TestCase):
 def test_reachable_should_survive(self):
  with tempfile.TemporaryDirectory() as td:
   l=Layer(td);a=l.export(commit=True);UnsafeEagerDelete().delete(l,a);self.assertTrue(all(p.exists() for p in l._archive_paths(a)))
if __name__=="__main__":unittest.main()
