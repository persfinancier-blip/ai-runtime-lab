import json,unittest
from experiments.launch_record_integrity.protocol import unsafe_accept_unsigned
class UnsafeSeed(unittest.TestCase):
    def test_forged(self):
        self.assertFalse(unsafe_accept_unsigned(json.dumps({'task_id':'task-A','pid':999999}),'task-A'),'unsigned structural trust accepted forged durable record')
