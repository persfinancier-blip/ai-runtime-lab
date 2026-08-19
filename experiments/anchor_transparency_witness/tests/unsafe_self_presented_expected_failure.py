import unittest
from experiments.anchor_transparency_witness.protocol import ReferenceLog, UnsafeSelfPresentedClient
class UnsafeBaseline(unittest.TestCase):
    def test_two_forks_should_not_both_be_accepted_but_are(self):
        key=b'log-key'; a=ReferenceLog('log-A',key,[b'common',b'good']).checkpoint(); b=ReferenceLog('log-A',key,[b'common',b'evil']).checkpoint(); c=UnsafeSelfPresentedClient(key); accepted=int(c.accept(a))+int(c.accept(b)); self.assertEqual(accepted,1,'unsafe client accepted both signed fork checkpoints')
if __name__=='__main__': unittest.main()
