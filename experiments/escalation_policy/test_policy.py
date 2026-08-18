import unittest
from policy import Context, Decision, decide, naive_decide


def base(**kw):
    data = dict(
        reversible=True,
        externally_consequential=False,
        requires_human_authorization=False,
        authorization_available=True,
        legal_identity_payment_secret_gate=False,
        uncertainty=0.10,
        evidence_quality=0.95,
        evidence_conflict=False,
        safe_primary_route=True,
        safe_fallback_route=False,
        cheap_reversible_probe=False,
        genuine_product_fork=False,
        side_effect_outcome_unknown=False,
    )
    data.update(kw)
    return Context(**data)


class PolicyTests(unittest.TestCase):
    def test_reversible_technical_choice_proceeds(self):
        self.assertEqual(decide(base()).decision, Decision.PROCEED)

    def test_preferred_tool_failure_uses_safe_fallback(self):
        self.assertEqual(decide(base(safe_primary_route=False, safe_fallback_route=True)).decision, Decision.FALLBACK)

    def test_no_safe_route_blocks(self):
        self.assertEqual(decide(base(safe_primary_route=False, safe_fallback_route=False)).decision, Decision.BLOCK)

    def test_irreversible_external_effect_escalates(self):
        ctx = base(reversible=False, externally_consequential=True)
        self.assertEqual(decide(ctx).decision, Decision.ESCALATE)
        self.assertEqual(naive_decide(ctx).decision, Decision.PROCEED)

    def test_missing_payment_or_secret_authority_blocks(self):
        ctx = base(legal_identity_payment_secret_gate=True, authorization_available=False)
        self.assertEqual(decide(ctx).decision, Decision.BLOCK)

    def test_payment_or_secret_gate_with_access_still_escalates(self):
        ctx = base(legal_identity_payment_secret_gate=True, authorization_available=True)
        self.assertEqual(decide(ctx).decision, Decision.ESCALATE)

    def test_high_uncertainty_cheap_probe_before_escalation(self):
        ctx = base(uncertainty=0.90, cheap_reversible_probe=True)
        self.assertEqual(decide(ctx).decision, Decision.PROBE)
        self.assertEqual(naive_decide(ctx).decision, Decision.ESCALATE)

    def test_conflicting_high_quality_evidence_without_probe_escalates(self):
        ctx = base(evidence_conflict=True, cheap_reversible_probe=False)
        self.assertEqual(decide(ctx).decision, Decision.ESCALATE)

    def test_conflicting_evidence_with_probe_probes(self):
        ctx = base(evidence_conflict=True, cheap_reversible_probe=True)
        self.assertEqual(decide(ctx).decision, Decision.PROBE)

    def test_product_direction_fork_escalates(self):
        self.assertEqual(decide(base(genuine_product_fork=True)).decision, Decision.ESCALATE)

    def test_unknown_effect_outcome_reconciles_via_probe(self):
        ctx = base(side_effect_outcome_unknown=True, cheap_reversible_probe=True)
        self.assertEqual(decide(ctx).decision, Decision.PROBE)

    def test_unknown_effect_without_reconciliation_blocks(self):
        ctx = base(side_effect_outcome_unknown=True, cheap_reversible_probe=False)
        self.assertEqual(decide(ctx).decision, Decision.BLOCK)

    def test_human_authorization_required_escalates(self):
        self.assertEqual(decide(base(requires_human_authorization=True)).decision, Decision.ESCALATE)


if __name__ == '__main__':
    unittest.main()
