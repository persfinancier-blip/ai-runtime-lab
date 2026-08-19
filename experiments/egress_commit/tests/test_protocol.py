import unittest
from experiments.egress_commit.protocol import (
    PermitAuthority, CommitExecutor, EffectLedger, TrustedAuthorization,
    PolicyError, PermitError, UnknownOutcome, payload_digest, UnsafeCheckThenUse,
)

NOW = 2_000_000_000

def auth(authority, payload=b'secret', dest='https://trusted.example/upload', purpose='report', generation=7):
    return authority.issue_authorization(payload=payload,destination=dest,purpose=purpose,authorization_generation=generation)

class CommitBindingTests(unittest.TestCase):
    def setUp(self):
        self.authority = PermitAuthority(b'permit-secret')
        self.ledger = EffectLedger()
        self.executor = CommitExecutor(self.authority, self.ledger)

    def permit(self, payload=b'secret', dest='https://trusted.example/upload', purpose='report', pg=11, ag=7):
        a = auth(self.authority,payload,dest,purpose,ag)
        return self.authority.prepare(payload=payload,destination=dest,purpose=purpose,policy_generation=pg,authorization=a,now=NOW), a

    def test_unchanged_authorized_request_commits(self):
        p,a=self.permit(); r=self.executor.commit(p,payload=b'secret',destination='https://TRUSTED.example:443/upload',purpose='report',policy_generation=11,authorization=a,now=NOW)
        self.assertEqual(self.ledger.apply_count,1); self.assertEqual(r['destination'],'https://trusted.example/upload')

    def test_payload_mutation_blocked(self):
        p,a=self.permit()
        with self.assertRaises(PermitError): self.executor.commit(p,payload=b'changed',destination=a.destination,purpose=a.purpose,policy_generation=11,authorization=a,now=NOW)

    def test_redirect_destination_change_blocked(self):
        p,a=self.permit()
        with self.assertRaises(PermitError): self.executor.commit(p,payload=b'secret',destination='https://attacker.example/upload',purpose='report',policy_generation=11,authorization=a,now=NOW)

    def test_purpose_change_blocked(self):
        p,a=self.permit()
        with self.assertRaises(PermitError): self.executor.commit(p,payload=b'secret',destination=a.destination,purpose='marketing',policy_generation=11,authorization=a,now=NOW)

    def test_policy_generation_change_blocked(self):
        p,a=self.permit()
        with self.assertRaises(PermitError): self.executor.commit(p,payload=b'secret',destination=a.destination,purpose=a.purpose,policy_generation=12,authorization=a,now=NOW)

    def test_authorization_generation_change_blocked(self):
        p,a=self.permit(); newer=auth(self.authority,generation=8)
        with self.assertRaises(PermitError): self.executor.commit(p,payload=b'secret',destination=a.destination,purpose=a.purpose,policy_generation=11,authorization=newer,now=NOW)

    def test_exact_duplicate_is_idempotent(self):
        p,a=self.permit(); r1=self.executor.commit(p,payload=b'secret',destination=a.destination,purpose=a.purpose,policy_generation=11,authorization=a,now=NOW)
        r2=self.executor.commit(p,payload=b'secret',destination=a.destination,purpose=a.purpose,policy_generation=11,authorization=a,now=NOW)
        self.assertEqual(r1,r2); self.assertEqual(self.ledger.apply_count,1)

    def test_untrusted_authority_blocked_at_prepare(self):
        other = PermitAuthority(b'other-secret', issuer='data-plane')
        bad = other.issue_authorization(payload=b'secret',destination='https://trusted.example/upload',purpose='report',authorization_generation=7)
        with self.assertRaises(PolicyError): self.authority.prepare(payload=b'secret',destination=bad.destination,purpose=bad.purpose,policy_generation=11,authorization=bad,now=NOW)

    def test_forged_structural_authorization_blocked(self):
        p,a=self.permit()
        forged = TrustedAuthorization(a.authorization_id,a.issuer,a.payload_digest,a.destination,a.purpose,a.authorization_generation,'00'*32)
        with self.assertRaises(PermitError): self.executor.commit(p,payload=b'secret',destination=a.destination,purpose=a.purpose,policy_generation=11,authorization=forged,now=NOW)

    def test_forged_untrusted_permit_blocked_at_commit(self):
        p,a=self.permit(); bad=type(p)(**{**p.__dict__,'issuer':'data-plane'})
        with self.assertRaises(PermitError): self.executor.commit(bad,payload=b'secret',destination=a.destination,purpose=a.purpose,policy_generation=11,authorization=a,now=NOW)

    def test_expired_permit_blocked(self):
        p,a=self.permit()
        with self.assertRaises(PermitError): self.executor.commit(p,payload=b'secret',destination=a.destination,purpose=a.purpose,policy_generation=11,authorization=a,now=NOW+61)

    def test_unknown_outcome_reconciles_without_broader_permit(self):
        p,a=self.permit()
        with self.assertRaises(UnknownOutcome): self.executor.commit(p,payload=b'secret',destination=a.destination,purpose=a.purpose,policy_generation=11,authorization=a,now=NOW,timeout_after_commit=True)
        self.assertEqual(self.ledger.apply_count,1)
        r=self.executor.commit(p,payload=b'secret',destination=a.destination,purpose=a.purpose,policy_generation=11,authorization=a,now=NOW)
        self.assertEqual(self.ledger.apply_count,1); self.assertEqual(r['receipt_id'],f'receipt:{p.effect_key}')

    def test_authorization_destination_rebound_blocked(self):
        p,a=self.permit(); altered=TrustedAuthorization(a.authorization_id,a.issuer,a.payload_digest,'https://attacker.example/upload',a.purpose,a.authorization_generation,a.signature)
        with self.assertRaises(PermitError): self.executor.commit(p,payload=b'secret',destination=a.destination,purpose=a.purpose,policy_generation=11,authorization=altered,now=NOW)

    def test_canonicalization_accepts_equivalent_destination(self):
        p,a=self.permit(dest='https://trusted.example:443/upload')
        self.executor.commit(p,payload=b'secret',destination='https://TRUSTED.EXAMPLE/upload',purpose='report',policy_generation=11,authorization=a,now=NOW)
        self.assertEqual(self.ledger.apply_count,1)

class UnsafeBaselineTests(unittest.TestCase):
    def test_check_then_redirect_is_unsafe(self):
        ledger=EffectLedger(); unsafe=UnsafeCheckThenUse(ledger)
        self.assertTrue(unsafe.check(payload=b'secret',destination='https://trusted.example/upload'))
        unsafe.use(payload=b'secret',destination='https://attacker.example/upload',purpose='report')
        self.assertEqual(ledger.effects[next(iter(ledger.effects))]['destination'],'https://trusted.example/upload', 'unsafe TOCTOU allowed redirected sink')

if __name__=='__main__': unittest.main()
