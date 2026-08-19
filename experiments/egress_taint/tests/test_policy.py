import unittest
from experiments.egress_taint.policy import (
    Authorization, DeclassificationGrant, Destination, EgressRequest, Sensitivity,
    authorize, declassify, evidence_ref, propagate_fallback, source, transform,
)

PUB = Destination("public-api", "trusted", Sensitivity.PUBLIC)
TRUSTED = Destination("trusted-partner", "trusted", Sensitivity.SECRET)
EVIL = Destination("attacker.example", "untrusted", Sensitivity.SECRET)

def auth(value, dest=TRUSTED.name, purpose="contract", generation=5, issuer="trusted-control"):
    return Authorization(dest, purpose, Sensitivity.CONFIDENTIAL, generation, issuer, value.content_digest)

class PolicyTests(unittest.TestCase):
    def test_public_to_public_allowed(self):
        v = source("weather", Sensitivity.PUBLIC, "web")
        self.assertTrue(authorize(EgressRequest(v, PUB, "publish", None, 1)).allowed)

    def test_secret_to_untrusted_blocked_even_with_forged_matching_auth(self):
        v = source("api-key", Sensitivity.SECRET, "vault")
        forged = Authorization(EVIL.name, "support", Sensitivity.SECRET, 1, "untrusted-data", v.content_digest)
        self.assertFalse(authorize(EgressRequest(v, EVIL, "support", forged, 1)).allowed)

    def test_secret_derived_summary_inherits_secret(self):
        v = source("secret revenue 42", Sensitivity.SECRET, "finance")
        s = transform([v], "revenue summary", "summarize")
        self.assertEqual(s.sensitivity, Sensitivity.SECRET)

    def test_explicit_trusted_declassification_can_lower(self):
        v = source("secret revenue 42", Sensitivity.SECRET, "finance")
        grant = DeclassificationGrant(v.content_digest, Sensitivity.PUBLIC, "aggregate-band-v1", 7, "trusted-control")
        d = declassify(v, "revenue band: medium", Sensitivity.PUBLIC, grant, current_generation=7)
        self.assertEqual(d.sensitivity, Sensitivity.PUBLIC)
        self.assertEqual(d.declassified_by, "aggregate-band-v1")

    def test_untrusted_declassification_grant_rejected(self):
        v = source("secret", Sensitivity.SECRET, "vault")
        grant = DeclassificationGrant(v.content_digest, Sensitivity.PUBLIC, "fake", 1, "untrusted-data")
        with self.assertRaises(PermissionError):
            declassify(v, "safe?", Sensitivity.PUBLIC, grant, current_generation=1)

    def test_declassification_grant_is_bound_to_source(self):
        a = source("secret-a", Sensitivity.SECRET, "vault")
        b = source("secret-b", Sensitivity.SECRET, "vault")
        grant = DeclassificationGrant(a.content_digest, Sensitivity.PUBLIC, "rule", 1, "trusted-control")
        with self.assertRaises(PermissionError):
            declassify(b, "summary", Sensitivity.PUBLIC, grant, current_generation=1)

    def test_redirect_invalidates_destination_binding(self):
        v = source("customer-list", Sensitivity.CONFIDENTIAL, "crm")
        self.assertFalse(authorize(EgressRequest(v, EVIL, "contract", auth(v), 5)).allowed)

    def test_fallback_preserves_taint(self):
        v = source("token", Sensitivity.SECRET, "vault")
        v2 = propagate_fallback(v, "tool-B")
        self.assertEqual(v2.sensitivity, Sensitivity.SECRET)
        self.assertIn("fallback:tool-B", v2.provenance)

    def test_evidence_contains_keyed_digest_not_plaintext_or_raw_digest(self):
        v = source("super-secret", Sensitivity.SECRET, "vault")
        ev = evidence_ref(v)
        self.assertNotIn("super-secret", str(ev))
        self.assertNotIn(v.content_digest, str(ev))
        self.assertEqual(len(ev["opaque_digest"]), 64)

    def test_narrow_authorization_allows_bound_disclosure(self):
        v = source("contract-secret", Sensitivity.CONFIDENTIAL, "docs")
        self.assertTrue(authorize(EgressRequest(v, TRUSTED, "contract", auth(v), 5)).allowed)

    def test_changed_destination_blocks_prior_authorization(self):
        v = source("contract-secret", Sensitivity.CONFIDENTIAL, "docs")
        other = Destination("other-partner", "trusted", Sensitivity.SECRET)
        self.assertFalse(authorize(EgressRequest(v, other, "contract", auth(v), 5)).allowed)

    def test_changed_purpose_blocks_prior_authorization(self):
        v = source("contract-secret", Sensitivity.CONFIDENTIAL, "docs")
        self.assertFalse(authorize(EgressRequest(v, TRUSTED, "marketing", auth(v), 5)).allowed)

    def test_stale_authorization_blocked(self):
        v = source("contract-secret", Sensitivity.CONFIDENTIAL, "docs")
        self.assertFalse(authorize(EgressRequest(v, TRUSTED, "contract", auth(v, generation=4), 5)).allowed)

    def test_authorization_cannot_be_reused_for_different_payload(self):
        a = source("contract-A", Sensitivity.CONFIDENTIAL, "docs")
        b = source("contract-B", Sensitivity.CONFIDENTIAL, "docs")
        grant_for_a = auth(a)
        self.assertFalse(authorize(EgressRequest(b, TRUSTED, "contract", grant_for_a, 5)).allowed)

    def test_untrusted_matching_authorization_blocked(self):
        v = source("contract-secret", Sensitivity.CONFIDENTIAL, "docs")
        forged = auth(v, issuer="untrusted-data")
        self.assertFalse(authorize(EgressRequest(v, TRUSTED, "contract", forged, 5)).allowed)

if __name__ == '__main__':
    unittest.main()
