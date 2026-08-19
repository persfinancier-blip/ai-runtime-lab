import unittest
from dataclasses import replace
from experiments.anchor_attestation.protocol import *

class Tests(unittest.TestCase):
    def setUp(self):
        self.p=SignedAnchorProvider()
        self.v=AttestationVerifier({("anchor-A",1):b"k1"},ProviderIdentity("anchor-A",1))
        self.c=AttestedCatchup(self.p,self.v)
    def test_valid_current(self):
        self.p.value=3; o=self.c.authenticated_read(challenge="n1",request_id="r1"); self.assertEqual(o.position,3)
    def test_forged_position(self):
        o=self.p.read(challenge="n",request_id="r"); bad=replace(o,position=99)
        with self.assertRaises(ForgedObservation): self.v.verify(bad,expected_challenge="n",allowed_kinds={"READ"})
    def test_replayed_old_observation(self):
        o=self.p.read(challenge="n",request_id="r"); self.v.verify(o,expected_challenge="n",allowed_kinds={"READ"})
        self.p.value=1
        with self.assertRaises(ReplayObservation): self.v.verify(o,expected_challenge="n",allowed_kinds={"READ"})
    def test_wrong_provider(self):
        q=SignedAnchorProvider("B",1,b"kb"); o=q.read(challenge="n",request_id="r")
        v=AttestationVerifier({("B",1):b"kb"},ProviderIdentity("A",1))
        with self.assertRaises(WrongProvider): v.verify(o,expected_challenge="n",allowed_kinds={"READ"})
    def test_stale_generation(self):
        o=self.p.read(challenge="n",request_id="r")
        v=AttestationVerifier({("anchor-A",1):b"k1"},ProviderIdentity("anchor-A",2))
        with self.assertRaises(StaleGeneration): v.verify(o,expected_challenge="n",allowed_kinds={"READ"})
    def test_challenge_mismatch(self):
        o=self.p.read(challenge="n",request_id="r")
        with self.assertRaises(ChallengeMismatch): self.v.verify(o,expected_challenge="other",allowed_kinds={"READ"})
    def test_unknown_reconcile_no_duplicate(self):
        self.p.value=0
        ref=self.c.catch_up_one(db_sequence=1,request_id="inc-1",timeout_after_commit=True)
        self.assertTrue(ref); self.assertEqual(self.p.value,1); self.assertEqual(self.p.increment_calls,1)
    def test_rotation_rejects_old_receipt(self):
        old=self.p.read(challenge="n",request_id="r")
        v2=AttestationVerifier({("anchor-A",2):b"k2"},ProviderIdentity("anchor-A",2))
        with self.assertRaises(StaleGeneration): v2.verify(old,expected_challenge="n",allowed_kinds={"READ"})
    def test_unavailable_is_not_rollback(self):
        self.p.available=False
        with self.assertRaises(ProviderUnavailable): self.c.authenticated_read()
    def test_evidence_ref_not_secret(self):
        o=self.p.read(challenge="n",request_id="r"); self.v.verify(o,expected_challenge="n",allowed_kinds={"READ"})
        ref=receipt_ref(o); self.assertNotIn("k1",ref); self.assertEqual(len(ref),64)
    def test_same_request_idempotent_increment_receipt(self):
        o1=self.p.increment(expected=0,challenge="a",request_id="x")
        o2=self.p.increment(expected=999,challenge="b",request_id="x")
        self.assertEqual(o1.position,o2.position); self.assertEqual(self.p.value,1)
    def test_wrong_kind_rejected(self):
        o=self.p.read(challenge="n",request_id="r")
        with self.assertRaises(AttestationError): self.v.verify(o,expected_challenge="n",allowed_kinds={"INCREMENT"})

if __name__=="__main__": unittest.main()
