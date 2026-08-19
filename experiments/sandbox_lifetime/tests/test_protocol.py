import os, subprocess, time, unittest
from experiments.sandbox_lifetime.protocol import *

G=Generations(3,7,11)

def sleeper():
    return subprocess.Popen(["/bin/sleep","30"], start_new_session=True,
        stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

class Tests(unittest.TestCase):
    def test_live_then_stale_after_exit(self):
        p=sleeper(); h=bind("t",p,G)
        self.assertTrue(validate_fresh(h,G))
        p.terminate(); p.wait(timeout=2)
        self.assertFalse(validate_fresh(h,G)); os.close(h.pidfd)
    def test_generation_drift_fences(self):
        p=sleeper(); h=bind("t",p,G)
        self.assertFalse(validate_fresh(h,Generations(4,7,11)))
        p.kill();p.wait();os.close(h.pidfd)
    def test_forged_starttime_rejected(self):
        p=sleeper(); h=bind("t",p,G)
        forged=LaunchReceipt("t",p.pid,h.receipt.starttime+1,G)
        self.assertFalse(reconstructible_identity_matches(forged))
        p.kill();p.wait();os.close(h.pidfd)
    def test_old_numeric_pid_receipt_not_authority(self):
        p=sleeper(); h=bind("t",p,G); old=h.receipt
        p.kill();p.wait()
        self.assertFalse(reconstructible_identity_matches(old))
        self.assertFalse(validate_fresh(h,G));os.close(h.pidfd)
    def test_group_termination_no_pipe_hang(self):
        code="import subprocess,time; subprocess.Popen(['/bin/sleep','30'],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(30)"
        p=subprocess.Popen(["python","-c",code],start_new_session=True,
          stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        h=bind("tree",p,G); time.sleep(.1)
        ev=terminate_process_group(h)
        p.wait(timeout=2)
        self.assertTrue(ev["terminated"]); self.assertEqual(ev["kind"],"termination")
        os.close(h.pidfd)
    def test_required_cgroup_fails_closed(self):
        with self.assertRaises(RuntimeError): require_cgroup_tree_containment()
    def test_evidence_kinds_separate(self):
        p=sleeper();h=bind("t",p,G)
        self.assertEqual(h.receipt.evidence_kind,EvidenceKind.LAUNCH)
        self.assertNotEqual(completion_evidence(True)["kind"],h.receipt.evidence_kind.value)
        p.kill();p.wait();os.close(h.pidfd)
    def test_foreign_receipt_cannot_validate_handle(self):
        a=sleeper();b=sleeper();ha=bind("a",a,G);hb=bind("b",b,G)
        mixed=SupervisionHandle(hb.receipt,ha.pidfd)
        self.assertFalse(validate_fresh(mixed,G))
        for p,h in [(a,ha),(b,hb)]: p.kill();p.wait();os.close(h.pidfd)
