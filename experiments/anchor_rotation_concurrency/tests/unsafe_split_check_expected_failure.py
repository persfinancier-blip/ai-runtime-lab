import unittest
from experiments.anchor_rotation_concurrency.tests.test_protocol import ConcurrencyTests
from experiments.anchor_rotation_concurrency.protocol import UnsafeCheckThenWriteStore
class UnsafeBaseline(unittest.TestCase):
 def test_split_check_then_write_accepts_two_successors(self):
  fx=ConcurrencyTests(); fx.setUp()
  try:
   pa,pb=fx.rotation(fx.a,'A'),fx.rotation(fx.b,'B'); s=UnsafeCheckThenWriteStore(fx.old); ca,cb=s.check(pa),s.check(pb); self.assertTrue(ca and cb); s.write_without_recheck(pa); s.write_without_recheck(pb)
   self.assertEqual(len(s.accepted),1,'unsafe store accepted two independently valid successors')
  finally:fx.tearDown()
if __name__=='__main__':unittest.main()
