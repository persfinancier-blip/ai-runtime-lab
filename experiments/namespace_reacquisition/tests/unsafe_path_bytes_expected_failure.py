import tempfile, unittest
from pathlib import Path
from experiments.namespace_reacquisition.protocol import UnsafePathBytesTrust
class Unsafe(unittest.TestCase):
    def test_replacement_should_not_be_trusted_but_is(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"a"; p.mkdir(); (p/"x").write_bytes(b"same")
            old=Path(td)/"old"; p.rename(old); p.mkdir(); (p/"x").write_bytes(b"same")
            self.assertFalse(UnsafePathBytesTrust().trust(p,{"x":b"same"}))
if __name__=="__main__": unittest.main()
