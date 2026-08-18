import tempfile
import unittest

from experiments.capability_planner.planner import CapabilityObservation, Route
from experiments.correctness_kernel.kernel import Kernel
from experiments.durable_run_state.protocol import FenceError, UnknownOutcome
from experiments.escalation_policy.policy import Context
from experiments.memory_safety.memory_safety import Memory
from experiments.verification_harness.protocol import Evidence


class CorrectnessKernelTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.kernel = Kernel(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def context(self, **overrides):
        values = dict(
            reversible=True,
            externally_consequential=False,
            requires_human_authorization=False,
            authorization_available=True,
            legal_identity_payment_secret_gate=False,
            uncertainty=0.1,
            evidence_quality=0.9,
            evidence_conflict=False,
            safe_primary_route=True,
            safe_fallback_route=True,
            cheap_reversible_probe=True,
            genuine_product_fork=False,
            side_effect_outcome_unknown=False,
        )
        values.update(overrides)
        return Context(**values)

    def routes(self, primary_available=True):
        routes = [
            Route("primary", "write", "c1", {"safe": True, "preferred": True}, 10),
            Route("fallback", "write", "c2", {"safe": True}, 1),
        ]
        observations = [
            CapabilityObservation(
                1,
                "c1",
                "primary",
                "write",
                0,
                100,
                primary_available,
                {"safe": True, "preferred": True},
                "cap1",
            ),
            CapabilityObservation(
                1,
                "c2",
                "fallback",
                "write",
                0,
                100,
                True,
                {"safe": True},
                "cap2",
            ),
        ]
        return routes, observations

    def test_unknown_reconcile_receipt_before_completion(self):
        state = self.kernel.start("w", "a1")
        with self.assertRaises(UnknownOutcome):
            self.kernel.perform(state, True)
        state, receipt_id = self.kernel.reconcile_receipt(state)
        self.assertIsNotNone(receipt_id)
        self.assertEqual(self.kernel.effects.apply_count, 1)
        test_id, test_evidence = self.kernel.add_test_evidence("a1")
        side_effect = Evidence(receipt_id, "side_effect", "a1", True, "pass", ())
        self.assertTrue(
            self.kernel.completion(
                "a1", ("done",), (receipt_id, test_id), (side_effect, test_evidence)
            ).done
        )

    def test_invalidation_revokes_completion(self):
        evidence_id, evidence = self.kernel.add_test_evidence("a1")
        self.assertTrue(
            self.kernel.completion("a1", ("done",), (evidence_id,), (evidence,)).done
        )
        self.kernel.ledger.invalidate(evidence_id, "regression")
        self.assertFalse(
            self.kernel.completion("a1", ("done",), (evidence_id,), (evidence,)).done
        )

    def test_quarantined_memory_not_authoritative(self):
        memory = Memory.make("route", "use unsafe route", 0.99, trust="verified")
        self.kernel.memory.add(memory)
        self.kernel.memory.quarantine(memory.id, "false")
        self.assertEqual(self.kernel.authoritative_memory("route"), [])

    def test_fallback_preserves_binding_identity(self):
        state = self.kernel.start("w", "a1")
        before = self.kernel.binding(state)
        routes, observations = self.routes(False)
        plan = self.kernel.plan_route(routes, observations)
        after = self.kernel.binding(self.kernel.store.load())
        self.assertEqual(plan.selected, "fallback")
        self.assertEqual(before, after)

    def test_payment_gate_dominates_route(self):
        routes, observations = self.routes()
        plan = self.kernel.plan_route(routes, observations)
        action = self.kernel.safe_next_action(
            self.context(legal_identity_payment_secret_gate=True), "manager", plan.selected
        )
        self.assertEqual(action, "ESCALATE")

    def test_topology_cannot_bypass_block(self):
        action = self.kernel.safe_next_action(
            self.context(side_effect_outcome_unknown=True, cheap_reversible_probe=False),
            "handoff",
            "primary",
        )
        self.assertEqual(action, "BLOCK")

    def test_stale_fence_after_reroute_rejected(self):
        first = self.kernel.start("w", "a1")
        old_fence = first.fence
        current = self.kernel.engine.start_or_resume("w")
        self.assertGreater(current.fence, old_fence)
        with self.assertRaises(FenceError):
            self.kernel.effects.apply(
                work_id="w",
                effect_key=current.effect_key,
                fence=old_fence,
                value="x",
            )

    def test_restart_preserves_memory_quarantine(self):
        memory = Memory.make("route", "unsafe", 0.99, trust="verified")
        self.kernel.memory.add(memory)
        self.kernel.memory.quarantine(memory.id, "false")
        restarted = Kernel(self.tmp.name)
        self.assertEqual(restarted.authoritative_memory("route"), [])
        self.assertEqual(restarted.memory.items[memory.id].status, "QUARANTINED")

    def test_restart_deterministic_next_action(self):
        routes, observations = self.routes(False)
        first_plan = self.kernel.plan_route(routes, observations)
        first_action = self.kernel.safe_next_action(
            self.context(safe_primary_route=False), "single", first_plan.selected
        )
        restarted = Kernel(self.tmp.name)
        second_plan = restarted.plan_route(routes, observations)
        second_action = restarted.safe_next_action(
            self.context(safe_primary_route=False), "single", second_plan.selected
        )
        self.assertEqual(first_action, second_action)

    def test_narrative_memory_never_completes(self):
        self.kernel.memory.add(
            Memory.make("status", "done successfully", 1.0, trust="verified")
        )
        self.assertTrue(self.kernel.naive_done_from_narrative("status"))
        self.assertFalse(self.kernel.completion("a1", ("done",), (), ()).done)

    def test_fabricated_claim_semantics_rejected(self):
        evidence_id, _ = self.kernel.add_test_evidence("a1", ("done",))
        forged = Evidence(evidence_id, "test", "a1", True, "pass", ("done", "extra"))
        self.assertFalse(
            self.kernel.completion(
                "a1", ("done", "extra"), (evidence_id,), (forged,)
            ).done
        )

    def test_duplicate_replay_effect_idempotent(self):
        state = self.kernel.start("w", "a1")
        self.kernel.perform(state)
        replay = self.kernel.engine.start_or_resume("w")
        self.kernel.effects.apply(
            work_id="w",
            effect_key=replay.effect_key,
            fence=replay.fence,
            value="a1",
        )
        self.assertEqual(self.kernel.effects.apply_count, 1)


if __name__ == "__main__":
    unittest.main()
