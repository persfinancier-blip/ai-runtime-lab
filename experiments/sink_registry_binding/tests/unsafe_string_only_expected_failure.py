import unittest
from experiments.sink_registry_binding.tests.test_protocol import Sink,Tests
from experiments.sink_registry_binding.protocol import UnsafeStringOnly
class Unsafe(unittest.TestCase):
    def test_attacker_should_not_execute_but_does(self):
        h=Tests();h.setUp();s=Sink();runtime=h.runtime(s,"evil","https://evil")
        UnsafeStringOnly().execute("sink-A",runtime,"e","p",b"x")
        self.assertEqual(s.count,0)
if __name__=="__main__":unittest.main()
