import threading
import unittest
from experiments.transactional_broker_journal.protocol import *

class Unsafe(unittest.TestCase):
    def test_same_request_should_apply_once_but_race_applies_twice(self):
        unsafe=UnsafeCheckThenApply(); req=Request('r','task','read',1,'payload'); barrier=threading.Barrier(2)
        ts=[threading.Thread(target=unsafe.process_with_barrier,args=(req,barrier)) for _ in range(2)]
        [t.start() for t in ts]; [t.join(5) for t in ts]
        self.assertEqual(unsafe.apply_count,1)

if __name__=='__main__':
    unittest.main()
