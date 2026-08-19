import unittest
from experiments.replay_watermark.protocol import *
class Unsafe(unittest.TestCase):
 def test_split_commit_inconsistent(self):
  s=UnsafeSplitStore(); s.publish_record_only(sign_record(b'k','t',1,1,1,'d')); self.assertEqual(s.watermark,1,'record committed but watermark did not')
