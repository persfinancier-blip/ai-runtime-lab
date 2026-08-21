import os,tempfile,unittest
from pathlib import Path
from experiments.credential_file_scavenging.protocol import CredentialLeaseStore,UnsafeGlobCleanup
from experiments.supervisor_restart.protocol import Generations,launch
class Unsafe(unittest.TestCase):
 def test_live_file_should_survive_but_glob_deletes_it(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);d=root/"c";d.mkdir();s=CredentialLeaseStore(root/"db",audit_key=b"k")
   l=s.create_named_fallback(task_id="t",credential_id="api",scope="s",secret=b"secret",directory=d)
   p,r,fd=launch("t",Generations(1,l.credential_generation,1),seconds=30);os.close(fd)
   try:s.handoff(l.lease_id,r);UnsafeGlobCleanup().cleanup(d);self.assertTrue((d/l.name).exists())
   finally:p.kill();p.wait()
if __name__=="__main__":unittest.main()
