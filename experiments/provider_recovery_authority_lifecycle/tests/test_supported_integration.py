import sqlite3
import tempfile
import unittest
from pathlib import Path

from experiments.anchor_attestation.protocol import AttestationVerifier,AttestedCatchup,ProviderIdentity,SignedAnchorProvider
from experiments.asymmetric_provider_history.protocol import GenerationSigner
from experiments.provider_threshold_rotation.enablement import ThresholdEnablement
from experiments.provider_threshold_rotation.protocol import RotationAuthority,Signature,ThresholdNotMet,key_id,mac
from experiments.provider_rotation_recovery.protocol import RecoveryAuthority,RecoveryAuthorityMismatch
from experiments.provider_recovery_authority_lifecycle.protocol import VersionedRecoveryAuthority
from experiments.provider_recovery_authority_lifecycle.supported import SupportedRecoveryAuthorityLifecycleLedger


def authority(version=1,generation=1,prefix="rot"):
    raw=[f"{prefix}-{version}-{generation}-{i}".encode() for i in range(3)]
    return RotationAuthority("provider-rotation",version,generation,2,{key_id(k):k.hex() for k in raw}),raw


def recovery(version=1,generation=1,prefix="recovery"):
    raw=[f"{prefix}-{version}-{generation}-{i}".encode() for i in range(4)]
    return VersionedRecoveryAuthority(
        version,
        RecoveryAuthority("provider-rotation-recovery",generation,3,{key_id(k):k.hex() for k in raw}),
    ),raw


def signatures(raw,payload,count):
    return tuple(Signature(key_id(k),mac(k,payload)) for k in raw[:count])


def attested(generation,key,position=0):
    p=SignedAnchorProvider("anchor-A",generation,key,value=position)
    v=AttestationVerifier({("anchor-A",generation):key},ProviderIdentity("anchor-A",generation))
    return p,AttestedCatchup(p,v)


class SupportedLifecycleIntegrationTests(unittest.TestCase):
    def make_ledger(self,path):
        signer=GenerationSigner.from_seed("anchor-A",1,b"A"*32)
        provider,a1=attested(1,b"hmac-1")
        root,root_raw=authority(); rec,rec_raw=recovery()
        base=ThresholdEnablement(signer.public.generation_id,1,root.authority_id,1,1,())
        enable=ThresholdEnablement(base.start_provider_generation_id,1,root.authority_id,1,1,signatures(root_raw,base.payload,2))
        ledger=SupportedRecoveryAuthorityLifecycleLedger(path,a1,signer.public,signer,root,enable,rec.recovery)
        return provider,ledger,signer,root,root_raw,rec,rec_raw,enable

    def test_old_breakglass_remains_verifiable_after_recovery_rotation_and_restart(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"db";_,ledger,signer,root1,_,rec1,rec1_raw,enable=self.make_ledger(path)
            root2,_=authority(2,2,"recovered")
            rintent=ledger.recovery.make_intent(root1,root2,rec1.recovery)
            ledger.recover_rotation_authority(root2,signatures(rec1_raw,rintent.payload,3))

            rec2,rec2_raw=recovery(2,2,"recovery-new")
            payload=ledger.recovery_rotation_payload(rec2)
            root2_raw=[f"recovered-2-2-{i}".encode() for i in range(3)]
            ledger.rotate_recovery_authority(
                rec2,signatures(rec1_raw,payload,3),signatures(rec2_raw,payload,3),signatures(root2_raw,payload,2)
            )
            self.assertEqual(ledger.recovery.current_recovery_locked(ledger._con()).authority_id,rec2.recovery.authority_id)
            restarted=SupportedRecoveryAuthorityLifecycleLedger(path,ledger.attested,signer.public,signer,root1,enable,rec1.recovery)
            self.assertTrue(restarted.verify_durable())

    def test_old_recovery_generation_cannot_authorize_breakglass_after_cutoff(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"db";_,ledger,_,root1,root1_raw,rec1,rec1_raw,_=self.make_ledger(path)
            rec2,rec2_raw=recovery(2,2,"recovery-new")
            payload=ledger.recovery_rotation_payload(rec2)
            ledger.rotate_recovery_authority(rec2,signatures(rec1_raw,payload,3),signatures(rec2_raw,payload,3),signatures(root1_raw,payload,2))
            root2,_=authority(2,2,"post-cutoff")
            stale_intent=ledger.recovery.make_intent(root1,root2,rec1.recovery)
            with self.assertRaises(ThresholdNotMet):
                ledger.recover_rotation_authority(root2,signatures(rec1_raw,stale_intent.payload,3))

    def test_tampered_post_cutoff_old_recovery_edge_fails_durable_verification(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"db";_,ledger,_,root1,root1_raw,rec1,rec1_raw,_=self.make_ledger(path)
            rec2,rec2_raw=recovery(2,2,"recovery-new")
            payload=ledger.recovery_rotation_payload(rec2)
            ledger.rotate_recovery_authority(rec2,signatures(rec1_raw,payload,3),signatures(rec2_raw,payload,3),signatures(root1_raw,payload,2))
            root2,_=authority(2,2,"forged-old-recovery")
            intent=ledger.recovery.make_intent(root1,root2,rec1.recovery)
            sigs=signatures(rec1_raw,intent.payload,3)
            q=sqlite3.connect(path)
            ledger.rotation_authority._insert_authority_locked(q,root2)
            q.execute(
                "INSERT INTO provider_rotation_recovery_transitions VALUES(?,?,?,?,?,?,?,?)",
                (root2.authority_id,root1.authority_id,root1.version,root1.generation,rec1.recovery.authority_id,rec1.recovery.generation,intent.intent_digest,ledger.recovery._encode_signatures(sigs)),
            )
            q.execute("UPDATE provider_rotation_authority_head SET authority_id=?,version=?,generation=? WHERE singleton=1",(root2.authority_id,2,2))
            q.commit();q.close()
            with self.assertRaises(RecoveryAuthorityMismatch): ledger.verify_durable()

    def test_recovery_rotation_requires_current_normal_root_quorum(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"db";_,ledger,_,root1,_,rec1,rec1_raw,_=self.make_ledger(path)
            rec2,rec2_raw=recovery(2,2,"recovery-new");payload=ledger.recovery_rotation_payload(rec2)
            unrelated,unrelated_raw=authority(1,1,"unrelated")
            with self.assertRaises(ThresholdNotMet):
                ledger.rotate_recovery_authority(rec2,signatures(rec1_raw,payload,3),signatures(rec2_raw,payload,3),signatures(unrelated_raw,payload,2))
            self.assertEqual(ledger.recovery_lifecycle.current().authority_id,rec1.authority_id)

    def test_recovery_and_lifecycle_heads_must_match(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"db";_,ledger,_,root1,root1_raw,rec1,rec1_raw,_=self.make_ledger(path)
            rec2,rec2_raw=recovery(2,2,"recovery-new");payload=ledger.recovery_rotation_payload(rec2)
            ledger.rotate_recovery_authority(rec2,signatures(rec1_raw,payload,3),signatures(rec2_raw,payload,3),signatures(root1_raw,payload,2))
            q=sqlite3.connect(path);q.execute("UPDATE provider_rotation_recovery_head SET authority_id=?,generation=?",(rec1.recovery.authority_id,rec1.recovery.generation));q.commit();q.close()
            with self.assertRaises(RecoveryAuthorityMismatch): ledger.verify_durable()


if __name__=="__main__": unittest.main()
