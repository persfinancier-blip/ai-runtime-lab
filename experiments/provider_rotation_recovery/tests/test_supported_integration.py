import sqlite3
import tempfile
import unittest
from pathlib import Path

from experiments.anchor_attestation.protocol import AttestationVerifier, AttestedCatchup, ProviderIdentity, SignedAnchorProvider
from experiments.asymmetric_provider_history.integration import PendingRotationBlocked
from experiments.asymmetric_provider_history.protocol import GenerationSigner
from experiments.provider_threshold_rotation.enablement import ThresholdEnablement
from experiments.provider_threshold_rotation.protocol import ProviderRotationIntent, RotationAuthority, Signature, ThresholdNotMet, key_id, mac
from experiments.provider_rotation_recovery.protocol import RecoveryAuthority, RecoveryError
from experiments.provider_rotation_recovery.supported import SupportedRecoveryThresholdProviderLedger
from experiments.shared_anchor_intent_ledger.protocol import Intent


def authority(version=1, generation=1, prefix="rot"):
    raw=[f"{prefix}-{version}-{generation}-{i}".encode() for i in range(3)]
    return RotationAuthority("provider-rotation",version,generation,2,{key_id(k):k.hex() for k in raw}),raw

def recovery_authority():
    raw=[f"recovery-1-{i}".encode() for i in range(4)]
    return RecoveryAuthority("provider-rotation-recovery",1,3,{key_id(k):k.hex() for k in raw}),raw

def signatures(raw,payload,count):
    return tuple(Signature(key_id(k),mac(k,payload)) for k in raw[:count])

def attested(generation,key,position=0):
    p=SignedAnchorProvider("anchor-A",generation,key,value=position)
    v=AttestationVerifier({("anchor-A",generation):key},ProviderIdentity("anchor-A",generation))
    return p,AttestedCatchup(p,v)


class SupportedRecoveryIntegrationTests(unittest.TestCase):
    def make_ledger(self,path):
        signer=GenerationSigner.from_seed("anchor-A",1,b"A"*32)
        provider,a1=attested(1,b"hmac-1")
        auth,auth_raw=authority(); recovery,recovery_raw=recovery_authority()
        base=ThresholdEnablement(signer.public.generation_id,1,auth.authority_id,1,1,())
        enable=ThresholdEnablement(base.start_provider_generation_id,1,auth.authority_id,1,1,signatures(auth_raw,base.payload,2))
        ledger=SupportedRecoveryThresholdProviderLedger(path,a1,signer.public,signer,auth,enable,recovery)
        return provider,ledger,signer,auth,auth_raw,recovery,recovery_raw,enable

    def test_recovery_edge_and_restart_verify_mixed_history(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"db"; _,ledger,s1,auth,_,recovery,recovery_raw,enable=self.make_ledger(path)
            new,new_raw=authority(2,2,"recovered")
            intent=ledger.recovery.make_intent(auth,new,recovery)
            ledger.recover_rotation_authority(new,signatures(recovery_raw,intent.payload,3))
            self.assertEqual(ledger.rotation_authority.current().authority_id,new.authority_id)
            restarted=SupportedRecoveryThresholdProviderLedger(path,ledger.attested,s1.public,s1,auth,enable,recovery)
            self.assertTrue(restarted.verify_durable())

    def test_pre_recovery_quorum_cannot_authorize_new_provider_rotation(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"db"; _,ledger,s1,old,old_raw,recovery,recovery_raw,_=self.make_ledger(path)
            new_auth,new_raw=authority(2,2,"recovered")
            rintent=ledger.recovery.make_intent(old,new_auth,recovery)
            ledger.recover_rotation_authority(new_auth,signatures(recovery_raw,rintent.payload,3))
            s2=GenerationSigner.from_seed("anchor-A",2,b"B"*32)
            proof=ledger.provider_history.make_transition(s1,s2)
            _,a2=attested(2,b"hmac-2")
            stale=ProviderRotationIntent("anchor-A",s1.public.generation_id,s2.public.generation_id,old.authority_id,old.version,old.generation)
            with self.assertRaises(ThresholdNotMet):
                ledger.rotate_provider(s2,proof,a2,signatures(old_raw,stale.payload,2))

    def test_prepared_work_blocks_normal_rotation_and_recovery(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"db"; _,ledger,_,old,old_raw,recovery,recovery_raw,_=self.make_ledger(path)
            ledger.reserve(Intent("pending","component-A","migration",{"v":1}))
            normal,normal_raw=authority(2,2,"normal")
            payload=ledger.rotation_authority.authority_rotation_payload(old,normal)
            with self.assertRaises(PendingRotationBlocked):
                ledger.rotate_rotation_authority(normal,signatures(old_raw,payload,2),signatures(normal_raw,payload,2))
            recovered,_=authority(2,2,"recovered")
            rintent=ledger.recovery.make_intent(old,recovered,recovery)
            with self.assertRaises(PendingRotationBlocked):
                ledger.recover_rotation_authority(recovered,signatures(recovery_raw,rintent.payload,3))
            self.assertEqual(ledger.rotation_authority.current().authority_id,old.authority_id)

    def test_duplicate_normal_and_recovery_proof_for_same_edge_fails(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"db"; _,ledger,_,old,old_raw,recovery,recovery_raw,_=self.make_ledger(path)
            new,new_raw=authority(2,2,"recovered")
            rintent=ledger.recovery.make_intent(old,new,recovery)
            ledger.recover_rotation_authority(new,signatures(recovery_raw,rintent.payload,3))
            payload=ledger.rotation_authority.authority_rotation_payload(old,new)
            q=sqlite3.connect(path)
            q.execute("INSERT INTO provider_rotation_authority_transitions VALUES(?,?,?,?,?)",(new.authority_id,old.authority_id,__import__('experiments.provider_threshold_rotation.protocol',fromlist=['sha']).sha(payload),ledger.rotation_authority._encode_signatures(signatures(old_raw,payload,2)),ledger.rotation_authority._encode_signatures(signatures(new_raw,payload,2))))
            q.commit(); q.close()
            with self.assertRaises(RecoveryError): ledger.verify_durable()

if __name__=="__main__": unittest.main()
