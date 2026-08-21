import tempfile,unittest
from pathlib import Path
from experiments.namespace_retirement.protocol import UnsafePathRetirement
class Unsafe(unittest.TestCase):
    def test_current_namespace_should_survive_but_does_not(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"current"; p.mkdir(); UnsafePathRetirement().retire(p)
            self.assertTrue(p.exists())
if __name__=="__main__": unittest.main()
