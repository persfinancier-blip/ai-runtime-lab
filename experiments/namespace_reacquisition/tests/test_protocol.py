import os, shutil, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from experiments.namespace_reacquisition.protocol import *

class Tests(unittest.TestCase):
    def setUp(self): self.key=b"authority-key"
    def test_unchanged_object_reacquires_when_handle_available(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"archive"; p.mkdir()
            r=capture(p,self.key)
            out=reacquire(r,self.key)
            self.assertIn(out["status"],{"REACQUIRED","UNSUPPORTED_STRONG_REACQUISITION"})
            if r.handle is not None: self.assertEqual(out["status"],"REACQUIRED")
    def test_boot_change_fails_closed_without_reopen_capability(self):
        import experiments.namespace_reacquisition.protocol as mod
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"archive"; p.mkdir(); r=capture(p,self.key)
            with patch.object(mod,"boot_id",return_value="different-boot"):
                self.assertEqual(reacquire(r,self.key)["status"],"UNSUPPORTED_STRONG_REACQUISITION")
    def test_byte_identical_replacement_detected(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"archive"; p.mkdir(); (p/"x").write_bytes(b"same")
            r=capture(p,self.key); old=Path(td)/"old"; p.rename(old); p.mkdir(); (p/"x").write_bytes(b"same")
            out=reacquire(r,self.key)
            if r.handle is not None: self.assertEqual(out["status"],"PATH_REPLACED")
            else: self.assertEqual(out["status"],"UNSUPPORTED_STRONG_REACQUISITION")
    def test_symlink_replacement_detected(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"archive"; p.mkdir(); r=capture(p,self.key)
            real=Path(td)/"real"; real.mkdir(); p.rmdir(); p.symlink_to(real, target_is_directory=True)
            self.assertEqual(reacquire(r,self.key)["status"],"PATH_REPLACED")
    def test_missing_path_is_not_silently_rebound(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"archive"; p.mkdir(); r=capture(p,self.key); p.rmdir()
            out=reacquire(r,self.key)
            self.assertIn(out["status"],{"PATH_MISSING","UNSUPPORTED_STRONG_REACQUISITION"})
    def test_detached_object_found_when_strong_handle_reopen_succeeds(self):
        import experiments.namespace_reacquisition.protocol as mod
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"archive"; p.mkdir(); st=p.stat()
            fake=HandleEvidence(1,1,"01")
            unsigned={"schema_version":1,"archive_path":os.path.abspath(p),"namespace_generation":1,
                      "boot_id":boot_id(),"st_dev":st.st_dev,"st_ino":st.st_ino,"handle":asdict(fake)}
            r=ContinuityRecord(1,os.path.abspath(p),1,unsigned["boot_id"],st.st_dev,st.st_ino,fake,mac(self.key,unsigned))
            detached=Path(td)/"detached"; p.rename(detached)
            def reopen(_handle): return os.open(detached,os.O_RDONLY|os.O_DIRECTORY|os.O_CLOEXEC)
            with patch.object(mod,"_open_saved_handle",side_effect=reopen):
                self.assertEqual(detached_classification(r,self.key)["status"],"DETACHED_OBJECT_FOUND")
    def test_tampered_record_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"archive"; p.mkdir(); r=capture(p,self.key)
            bad=ContinuityRecord(r.schema_version,r.archive_path,r.namespace_generation+1,r.boot_id,r.st_dev,r.st_ino,r.handle,r.mac)
            with self.assertRaises(AuthenticationError): reacquire(bad,self.key)
    def test_authenticated_migration_advances_generation(self):
        with tempfile.TemporaryDirectory() as td:
            a=Path(td)/"a"; b=Path(td)/"b"; a.mkdir(); b.mkdir()
            r=capture(a,self.key); permit=issue_migration(r,b,2,self.key); n=migrate(r,permit,self.key)
            self.assertEqual(n.archive_path,os.path.abspath(b)); self.assertEqual(n.namespace_generation,2)
            self.assertEqual(reacquire(n,self.key)["status"],"REACQUIRED" if n.handle else "UNSUPPORTED_STRONG_REACQUISITION")
    def test_stale_migration_fenced(self):
        with tempfile.TemporaryDirectory() as td:
            a=Path(td)/"a"; b=Path(td)/"b"; a.mkdir(); b.mkdir(); r=capture(a,self.key)
            with self.assertRaises(MigrationError): issue_migration(r,b,3,self.key)
    def test_wrong_predecessor_permit_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            a=Path(td)/"a"; b=Path(td)/"b"; c=Path(td)/"c"; [x.mkdir() for x in (a,b,c)]
            r1=capture(a,self.key); r2=capture(c,self.key)
            permit=issue_migration(r1,b,2,self.key)
            with self.assertRaises(MigrationError): migrate(r2,permit,self.key)
    def test_unsafe_path_bytes_accepts_replacement(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"a"; p.mkdir(); (p/"x").write_bytes(b"same")
            expected={"x":b"same"}; old=Path(td)/"old"; p.rename(old); p.mkdir(); (p/"x").write_bytes(b"same")
            self.assertTrue(UnsafePathBytesTrust().trust(p,expected))

if __name__=="__main__": unittest.main()
