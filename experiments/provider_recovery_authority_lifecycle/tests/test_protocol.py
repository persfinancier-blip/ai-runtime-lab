import sqlite3
import tempfile
import unittest
from pathlib import Path

from experiments.provider_threshold_rotation.protocol import (
    RotationAuthority,Signature,ThresholdNotMet,key_id,mac,
)
from experiments.provider_rotation_recovery.protocol import RecoveryAuthority
from experiments.provider_recovery_authority_lifecycle.protocol import (
    DurableRecoveryAuthorityLifecycle,LifecycleRollback,LifecycleSubstitution,
    UnsafeRecoveryOnlySwap,VersionedRecoveryAuthority,
)


def recovery(version=1,generation=1,prefix="rec",revoked=()):
    raw=[f"{prefix}-{version}-{generation}-{i}".encode() for i in range(4)]
    return VersionedRecoveryAuthority(
        version,
        RecoveryAuthority(
            "provider-rotation-recovery",generation,3,
            {key_id(k):k.hex() for k in raw},tuple(revoked)
        ),
    ),raw


def root(version=1,generation=1,prefix="root"):
    raw=[f"{prefix}-{version}-{generation}-{i}".encode() for i in range(3)]
    return RotationAuthority(
        "provider-rotation",version,generation,2,{key_id(k):k.hex() for k in raw}
    ),raw


def sigs(raw,payload,count):
    return tuple(Signature(key_id(k),mac(k,payload)) for k in raw[:count])


class Tests(unittest.TestCase):
    def test_three_party_rotation_and_restart(self):
        with tempfile.TemporaryDirectory() as td:
            old,old_raw=recovery(); new,new_raw=recovery(2,2,"new"); r,rraw=root()
            store=DurableRecoveryAuthorityLifecycle(Path(td)/"db",old)
            p=store.make_intent(r,old,new).payload
            out=store.rotate(r,new,sigs(old_raw,p,3),sigs(new_raw,p,3),sigs(rraw,p,2))
            self.assertEqual(len(out["old_recovery_signers"]),3)
            self.assertEqual(store.current().authority_id,new.authority_id)
            restarted=DurableRecoveryAuthorityLifecycle(Path(td)/"db",old)
            self.assertTrue(restarted.verify_durable())

    def test_old_recovery_quorum_alone_cannot_self_swap(self):
        with tempfile.TemporaryDirectory() as td:
            old,old_raw=recovery(); new,new_raw=recovery(2,2,"new"); r,rraw=root()
            store=DurableRecoveryAuthorityLifecycle(Path(td)/"db",old); p=store.make_intent(r,old,new).payload
            with self.assertRaises(ThresholdNotMet):
                store.rotate(r,new,sigs(old_raw,p,3),(),sigs(rraw,p,2))

    def test_current_root_quorum_required(self):
        with tempfile.TemporaryDirectory() as td:
            old,old_raw=recovery(); new,new_raw=recovery(2,2,"new"); r,rraw=root()
            store=DurableRecoveryAuthorityLifecycle(Path(td)/"db",old); p=store.make_intent(r,old,new).payload
            with self.assertRaises(ThresholdNotMet):
                store.rotate(r,new,sigs(old_raw,p,3),sigs(new_raw,p,3),())

    def test_new_recovery_quorum_required(self):
        with tempfile.TemporaryDirectory() as td:
            old,old_raw=recovery(); new,new_raw=recovery(2,2,"new"); r,rraw=root()
            store=DurableRecoveryAuthorityLifecycle(Path(td)/"db",old); p=store.make_intent(r,old,new).payload
            with self.assertRaises(ThresholdNotMet):
                store.rotate(r,new,sigs(old_raw,p,3),sigs(new_raw,p,2),sigs(rraw,p,2))

    def test_generation_and_version_must_advance_exactly_one(self):
        with tempfile.TemporaryDirectory() as td:
            old,old_raw=recovery(); r,rraw=root(); store=DurableRecoveryAuthorityLifecycle(Path(td)/"db",old)
            for new in (recovery(3,2,"vskip")[0],recovery(2,3,"gskip")[0]):
                p=store.make_intent(r,old,new).payload
                with self.assertRaises(LifecycleRollback):
                    store.rotate(r,new,sigs(old_raw,p,3),(),sigs(rraw,p,2))

    def test_old_generation_remains_historical_after_rotation(self):
        with tempfile.TemporaryDirectory() as td:
            old,old_raw=recovery(); new,new_raw=recovery(2,2,"new"); r,rraw=root()
            store=DurableRecoveryAuthorityLifecycle(Path(td)/"db",old); p=store.make_intent(r,old,new).payload
            store.rotate(r,new,sigs(old_raw,p,3),sigs(new_raw,p,3),sigs(rraw,p,2))
            historical=store.historical(old.authority_id)
            self.assertEqual(historical.authority_id,old.authority_id)
            self.assertNotEqual(store.current().authority_id,old.authority_id)

    def test_stale_old_generation_cannot_authorize_next_rotation(self):
        with tempfile.TemporaryDirectory() as td:
            old,old_raw=recovery(); two,two_raw=recovery(2,2,"two"); three,three_raw=recovery(3,3,"three"); r,rraw=root()
            store=DurableRecoveryAuthorityLifecycle(Path(td)/"db",old); p1=store.make_intent(r,old,two).payload
            store.rotate(r,two,sigs(old_raw,p1,3),sigs(two_raw,p1,3),sigs(rraw,p1,2))
            p2=store.make_intent(r,two,three).payload
            with self.assertRaises(ThresholdNotMet):
                store.rotate(r,three,sigs(old_raw,p2,3),sigs(three_raw,p2,3),sigs(rraw,p2,2))

    def test_corrupted_transition_proof_fails_restart(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"db"; old,old_raw=recovery(); new,new_raw=recovery(2,2,"new"); r,rraw=root()
            store=DurableRecoveryAuthorityLifecycle(path,old); p=store.make_intent(r,old,new).payload
            store.rotate(r,new,sigs(old_raw,p,3),sigs(new_raw,p,3),sigs(rraw,p,2))
            q=sqlite3.connect(path);q.execute(
                "UPDATE provider_recovery_lifecycle_transitions SET root_signatures_json='[]'"
            );q.commit();q.close()
            with self.assertRaises(ThresholdNotMet):
                DurableRecoveryAuthorityLifecycle(path,old)

    def test_root_material_substitution_fails_restart(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"db"; old,old_raw=recovery(); new,new_raw=recovery(2,2,"new"); r,rraw=root()
            store=DurableRecoveryAuthorityLifecycle(path,old); p=store.make_intent(r,old,new).payload
            store.rotate(r,new,sigs(old_raw,p,3),sigs(new_raw,p,3),sigs(rraw,p,2))
            q=sqlite3.connect(path);q.execute(
                "UPDATE provider_recovery_lifecycle_roots SET authority_json='{}'"
            );q.commit();q.close()
            with self.assertRaises(Exception):
                DurableRecoveryAuthorityLifecycle(path,old)

    def test_head_rollback_fails_restart(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"db"; old,old_raw=recovery(); new,new_raw=recovery(2,2,"new"); r,rraw=root()
            store=DurableRecoveryAuthorityLifecycle(path,old); p=store.make_intent(r,old,new).payload
            store.rotate(r,new,sigs(old_raw,p,3),sigs(new_raw,p,3),sigs(rraw,p,2))
            q=sqlite3.connect(path);q.execute(
                "UPDATE provider_recovery_lifecycle_head SET authority_id=?,version=1,generation=1",
                (old.authority_id,),
            );q.commit();q.close()
            with self.assertRaises(LifecycleRollback):
                DurableRecoveryAuthorityLifecycle(path,old)

    def test_caller_key_map_mutation_does_not_change_pinned_bootstrap(self):
        with tempfile.TemporaryDirectory() as td:
            old, _ = recovery()
            store = DurableRecoveryAuthorityLifecycle(Path(td) / "db", old)
            pinned = store.bootstrap.authority_id
            old.recovery.keys.clear()
            self.assertEqual(store.bootstrap.authority_id, pinned)
            self.assertTrue(store.verify_durable())

    def test_unsafe_recovery_only_swap_baseline(self):
        self.assertTrue(UnsafeRecoveryOnlySwap.allows(True))


if __name__=="__main__": unittest.main()
