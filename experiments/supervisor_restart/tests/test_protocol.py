import os, subprocess, unittest
from experiments.supervisor_restart.protocol import *

G=Generations(1,2,3)

class RestartTests(unittest.TestCase):
    def cleanup(self,proc):
        if proc.poll() is None:
            try: os.killpg(os.getpgid(proc.pid),9)
            except ProcessLookupError: pass
        try: proc.wait(timeout=1)
        except Exception: pass

    def test_restart_reacquires_fresh_pidfd(self):
        p,r,oldfd=launch('t1',G)
        try:
            os.close(oldfd)
            rr=DurableLaunchRecord.from_json(r.to_json())
            state,a,_=reconcile(rr,G)
            self.assertEqual(state,ReconcileState.SAME_INSTANCE)
            self.assertTrue(can_continue(state,a))
            self.assertEqual(pidfd_target_pid(a.pidfd),r.pid)
            os.close(a.pidfd)
        finally: self.cleanup(p)

    def test_generation_drift_fails_closed(self):
        p,r,fd=launch('t2',G)
        try:
            os.close(fd)
            state,a,_=reconcile(r,Generations(2,2,3))
            self.assertEqual(state,ReconcileState.GENERATION_DRIFT); self.assertIsNone(a)
        finally: self.cleanup(p)

    def test_identity_mismatch_is_rejected(self):
        p,r,fd=launch('t3',G)
        try:
            os.close(fd)
            bad=DurableLaunchRecord(r.task_id,r.pid,r.starttime+1,r.generations,r.process_group)
            state,a,_=reconcile(bad,G)
            self.assertEqual(state,ReconcileState.IDENTITY_MISMATCH); self.assertIsNone(a)
        finally: self.cleanup(p)

    def test_exited_is_distinguished(self):
        p,r,fd=launch('t4',G,.05)
        os.close(fd); p.wait(timeout=1)
        state,a,_=reconcile(r,G)
        self.assertEqual(state,ReconcileState.EXITED); self.assertIsNone(a)

    def test_consequential_continuation_needs_fresh_authority(self):
        p,r,fd=launch('t5',G)
        try:
            os.close(fd)
            self.assertFalse(can_continue(ReconcileState.SAME_INSTANCE,None))
            state,a,_=reconcile(r,G)
            self.assertTrue(can_continue(state,a)); os.close(a.pidfd)
        finally: self.cleanup(p)

    def test_orphan_termination_after_restart(self):
        p,r,fd=launch('t6',G)
        try:
            os.close(fd)
            state,a,_=reconcile(r,G)
            self.assertEqual(state,ReconcileState.SAME_INSTANCE)
            out=terminate_orphan(a)
            self.assertTrue(out['terminated'],out)
            os.close(a.pidfd)
        finally: self.cleanup(p)

    def test_process_group_drift_blocks_group_signal(self):
        p,r,fd=launch('t7',G)
        try:
            os.close(fd)
            bad=DurableLaunchRecord(r.task_id,r.pid,r.starttime,r.generations,r.process_group+999999)
            state,a,_=reconcile(bad,G)
            self.assertEqual(state,ReconcileState.SAME_INSTANCE)
            out=terminate_orphan(a)
            self.assertFalse(out['terminated']); self.assertEqual(out['reason'],'process_group_drift')
            os.close(a.pidfd)
        finally: self.cleanup(p)

    def test_foreign_task_record_is_rejected(self):
        p,r,fd=launch('t9',G)
        try:
            os.close(fd)
            state,a,_=reconcile(r,G,expected_task_id='different-task')
            self.assertEqual(state,ReconcileState.IDENTITY_MISMATCH); self.assertIsNone(a)
        finally: self.cleanup(p)

    def test_serialized_record_contains_no_pidfd(self):
        p,r,fd=launch('t8',G)
        try:
            text=r.to_json(); self.assertNotIn('pidfd',text.lower())
        finally:
            os.close(fd); self.cleanup(p)
