import sqlite3
import tempfile
import unittest
from pathlib import Path

from experiments.asymmetric_break_glass_history.suffix import AsymmetricBreakGlassError,SupportedAsymmetricBreakGlassLedger
from experiments.asymmetric_provider_history.protocol import GenerationSigner
from experiments.provider_threshold_rotation.enablement import ThresholdEnablement
from experiments.provider_threshold_rotation.protocol import ThresholdNotMet
from experiments.provider_recovery_authority_lifecycle.custody_break_glass import custody_enablement_payload
from experiments.provider_recovery_authority_lifecycle.tests.test_public_custody_supported import attested,authority,public_recovery,public_signatures,recovery,signatures

class AsymmetricSuffixIntegrationTests(unittest.TestCase):
    def make_ledger(self,path):
        signer=GenerationSigner.from_seed("anchor-A",1,b"A"*32);_,a1=attested(1,b"hmac-1");root,root_raw=authority();rec,rec_raw=recovery();public,public_signers=public_recovery()
        base=ThresholdEnablement(signer.public.generation_id,1,root.authority_id,1,1,())
        enable=ThresholdEnablement(base.start_provider_generation_id,1,root.authority_id,1,1,signatures(root_raw,base.payload,2))
        enable_payload=custody_enablement_payload(root,rec,public)
        ledger=SupportedAsymmetricBreakGlassLedger(path,a1,signer.public,signer,root,enable,rec.recovery,public,custody_enablement_signatures=public_signatures(public_signers,enable_payload,3))
        return ledger,signer,root,rec,rec_raw,public,public_signers,enable
    def migrate(self,ledger,public_signers):
        payload=ledger.migration_guard.payload();return ledger.migration_guard.establish(public_signatures(public_signers,payload,3))
    def test_post_cutoff_recovery_uses_only_asymmetric_proof_and_restarts(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"db";ledger,signer,root1,rec1,_,public1,public_signers,enable=self.make_ledger(path);self.migrate(ledger,public_signers);root2,_=authority(2,2,"asymmetric");payload=ledger.asymmetric_recovery_payload(root2);out=ledger.recover_rotation_authority_asymmetric(root2,public_signatures(public_signers,payload,3));self.assertEqual(out["new_rotation_authority_id"],root2.authority_id)
            q=sqlite3.connect(path);self.assertEqual(q.execute("SELECT COUNT(*) FROM provider_rotation_recovery_transitions").fetchone()[0],0);self.assertEqual(q.execute("SELECT COUNT(*) FROM provider_asymmetric_break_glass_proofs").fetchone()[0],1);q.close()
            restarted=SupportedAsymmetricBreakGlassLedger(path,ledger.attested,signer.public,signer,root1,enable,rec1.recovery,public1);self.assertTrue(restarted.verify_durable());self.assertEqual(restarted.rotation_authority.current().authority_id,root2.authority_id)
    def test_hmac_compatibility_entry_points_are_blocked_after_migration(self):
        with tempfile.TemporaryDirectory() as td:
            ledger,_,_,_,_,_,public_signers,_=self.make_ledger(Path(td)/"db");self.migrate(ledger,public_signers)
            with self.assertRaises(AsymmetricBreakGlassError):ledger.recover_rotation_authority(None,())
            with self.assertRaises(AsymmetricBreakGlassError):ledger.recover_rotation_authority_with_custody(None,(),())
    def test_asymmetric_recovery_requires_current_public_threshold(self):
        with tempfile.TemporaryDirectory() as td:
            ledger,_,_,_,_,_,public_signers,_=self.make_ledger(Path(td)/"db");self.migrate(ledger,public_signers);root2,_=authority(2,2,"threshold");payload=ledger.asymmetric_recovery_payload(root2)
            with self.assertRaises(ThresholdNotMet):ledger.recover_rotation_authority_asymmetric(root2,public_signatures(public_signers,payload,1))
    def test_old_public_signers_cannot_authorize_after_recovery_rotation(self):
        with tempfile.TemporaryDirectory() as td:
            ledger,_,_,_,rec1_raw,_,old_public_signers,_=self.make_ledger(Path(td)/"db");self.migrate(ledger,old_public_signers)
            _,root_raw=authority();rec2,rec2_raw=recovery(2,2,"recovery-new");public2,public2_signers=public_recovery(2,2,"public-new")
            symmetric_payload,public_payload=ledger.recovery_custody_rotation_payloads(rec2,public2)
            ledger.rotate_recovery_authority_with_custody(rec2,public2,signatures(rec1_raw,symmetric_payload,3),signatures(rec2_raw,symmetric_payload,3),signatures(root_raw,symmetric_payload,2),public_signatures(old_public_signers,public_payload,3),public_signatures(public2_signers,public_payload,3))
            root2,_=authority(2,2,"after-recovery-rotation");payload=ledger.asymmetric_recovery_payload(root2)
            with self.assertRaises(ThresholdNotMet):ledger.recover_rotation_authority_asymmetric(root2,public_signatures(old_public_signers,payload,3))
            ledger.recover_rotation_authority_asymmetric(root2,public_signatures(public2_signers,payload,3));self.assertTrue(ledger.verify_durable())
    def test_asymmetric_proof_tamper_fails_restart(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"db";ledger,signer,root1,rec1,_,public1,public_signers,enable=self.make_ledger(path);self.migrate(ledger,public_signers);root2,_=authority(2,2,"tamper");payload=ledger.asymmetric_recovery_payload(root2);ledger.recover_rotation_authority_asymmetric(root2,public_signatures(public_signers,payload,3));q=sqlite3.connect(path);q.execute("UPDATE provider_asymmetric_break_glass_proofs SET public_signatures_json='[]'");q.commit();q.close()
            with self.assertRaises(Exception):SupportedAsymmetricBreakGlassLedger(path,ledger.attested,signer.public,signer,root1,enable,rec1.recovery,public1)
    def test_exactly_one_root_proof_type_is_required(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"db";ledger,_,_,_,_,_,public_signers,_=self.make_ledger(path);self.migrate(ledger,public_signers);root2,_=authority(2,2,"count");payload=ledger.asymmetric_recovery_payload(root2);ledger.recover_rotation_authority_asymmetric(root2,public_signatures(public_signers,payload,3));q=sqlite3.connect(path);q.execute("INSERT INTO provider_rotation_authority_transitions VALUES(?,?,?,?,?)",(root2.authority_id,ledger.rotation_authority.bootstrap.authority_id,"0"*64,"[]","[]"));q.commit();q.close()
            with self.assertRaises(Exception):ledger.verify_durable()

if __name__=="__main__":unittest.main()
