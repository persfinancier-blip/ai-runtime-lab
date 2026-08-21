import fcntl,json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from experiments.memfd_credential_transport.protocol import *
SECRET=b'memfd-secret-value'
class Tests(unittest.TestCase):
 def setUp(self): self.v=MemfdVault(b'audit'); self.p=self.v.rotate('api','seller-read',SECRET)
 def test_path_consuming_child_reads_exact_secret(self):
  t=self.v.open_transport(self.p)
  try:self.assertEqual(child_read_via_path(t),SECRET)
  finally:t.close()
 def test_descriptor_not_readable_without_explicit_inheritance(self):
  t=self.v.open_transport(self.p)
  try:self.assertFalse(child_can_read_without_inheritance(t))
  finally:t.close()
 def test_procfd_reference_and_evidence_contain_no_raw_secret(self):
  t=self.v.open_transport(self.p)
  try:self.assertNotIn(SECRET.decode(),t.path);self.assertNotIn(SECRET.decode(),json.dumps(evidence(self.p)))
  finally:t.close()
 def test_close_removes_self_procfd_reference(self):
  t=self.v.open_transport(self.p); path=t.path; self.assertTrue(Path(path).exists());t.close();self.assertFalse(Path(path).exists())
 def test_seals_prevent_write_grow_and_shrink(self):
  t=self.v.open_transport(self.p)
  try:
   self.assertTrue(verify_seals(t))
   with self.assertRaises(OSError):os.write(t.fd,b'x')
   with self.assertRaises(OSError):os.ftruncate(t.fd,len(SECRET)+1)
   with self.assertRaises(OSError):os.ftruncate(t.fd,1)
  finally:t.close()
 def test_stale_generation_rejected(self):
  old=self.p;self.v.rotate('api','seller-read',b'new')
  with self.assertRaises(StaleCredential):self.v.open_transport(old)
 def test_retry_reuses_nonsecret_permit_identity(self):
  a=evidence(self.p);b=evidence(self.v.permit());self.assertEqual(a,b);self.assertNotIn(SECRET,repr(a).encode())
 def test_compatibility_probe_routes_memfd(self):
  r=route_for_path_only_tool(self.v,self.p);self.assertEqual(r['route'],'MEMFD_PROCFD');r['transport'].close()
 def test_unavailable_memfd_routes_named_fallback(self):
  original=getattr(os,'memfd_create')
  try:
   delattr(os,'memfd_create');r=route_for_path_only_tool(self.v,self.p);self.assertEqual(r['route'],'LAB-068_NAMED_FALLBACK')
  finally:setattr(os,'memfd_create',original)
 def test_unsafe_named_path_leaves_directory_entry(self):
  with tempfile.TemporaryDirectory() as td:
   p=UnsafeNamedPath().create(td,SECRET);self.assertTrue(Path(p).exists());self.assertEqual(Path(p).read_bytes(),SECRET)
if __name__=='__main__':unittest.main()
