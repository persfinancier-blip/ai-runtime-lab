import unittest
from experiments.child_sandbox.protocol import UnsafeBroadPolicy, SandboxSpec
class Unsafe(unittest.TestCase):
 def test_broad_authority_should_deny_host_write_but_does_not(self):
  s=SandboxSpec("t","/work",1,1)
  allowed=UnsafeBroadPolicy().check(s,None,"write","/home/user/.ssh/authorized_keys")
  self.assertFalse(allowed,"unsafe broad authority allowed host write")
if __name__=="__main__": unittest.main()
