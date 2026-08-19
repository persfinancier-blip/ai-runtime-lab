import unittest
from experiments.child_sandbox.protocol import *
class T(unittest.TestCase):
 def setUp(self):
  self.s=SandboxSpec("t","/work",3,7,read_roots=("/work",),write_roots=("/work/out",),exec_allow=("/usr/bin/python",),fd_allow=(3,),allow_network=True)
  self.p=Policy(); self.permit=self.p.issue(self.s)
 def ok(self,op,t): self.assertTrue(self.p.check(self.s,self.permit,op,t))
 def deny(self,op,t):
  with self.assertRaises(Denied): self.p.check(self.s,self.permit,op,t)
 def test_workspace_read(self): self.ok("read","/work/a")
 def test_home_denied(self): self.deny("read","/home/user/.config/x")
 def test_write_outside_denied(self): self.deny("write","/tmp/leak")
 def test_exec_scoped(self): self.ok("exec","/usr/bin/python"); self.deny("exec","/bin/sh")
 def test_fd_allowlist(self): self.ok("fd","3"); self.deny("fd","4")
 def test_network_distinct(self): self.ok("network","x"); self.deny("local_socket","/run/docker.sock")
 def test_generation_stale(self):
  s2=SandboxSpec(**{**self.s.__dict__,"generation":4})
  with self.assertRaises(Denied): self.p.check(s2,self.permit,"read","/work/a")
 def test_credential_generation_bound(self):
  s2=SandboxSpec(**{**self.s.__dict__,"credential_generation":8})
  with self.assertRaises(Denied): self.p.check(s2,self.permit,"read","/work/a")
 def test_unsafe_baseline_violates(self): self.assertTrue(UnsafeBroadPolicy().check(self.s,self.permit,"write","/home/user/.ssh/authorized_keys"))
