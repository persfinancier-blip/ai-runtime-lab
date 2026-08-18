import json
import tempfile
import unittest
from pathlib import Path

from experiments.durable_run_state.protocol import (
    DurableEngine,
    EffectLedger,
    FenceError,
    JsonStateStore,
    StaleStateError,
    UnknownOutcome,
    UnsupportedSchemaError,
)


class DurableRunStateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.state_path = root / "state.json"
        self.ledger_path = root / "effects.json"

    def tearDown(self):
        self.tmp.cleanup()

    def engine(self):
        return DurableEngine(JsonStateStore(self.state_path), EffectLedger(self.ledger_path))

    def test_clean_checkpoint_process_loss_resume(self):
        e1 = self.engine()
        s1 = e1.start_or_resume("work-1")
        e1.prepare_effect(s1, value="alpha")

        e2 = self.engine()
        s2 = e2.start_or_resume("work-1")
        s2 = e2.execute_effect(s2)
        s2 = e2.complete(s2)
        self.assertEqual(s2.phase, "DONE")
        self.assertEqual(e2.ledger.apply_count, 1)

    def test_duplicate_delivery_does_not_repeat_effect(self):
        e1 = self.engine()
        s = e1.start_or_resume("work-2")
        s = e1.prepare_effect(s, value="beta")
        s = e1.execute_effect(s)
        e1.complete(s)

        e2 = self.engine()
        duplicate = e2.start_or_resume("work-2")
        self.assertEqual(duplicate.phase, "DONE")
        self.assertEqual(e2.ledger.apply_count, 1)

    def test_stale_schema_is_rejected(self):
        e = self.engine()
        e.start_or_resume("work-3")
        raw = json.loads(self.state_path.read_text())
        raw["schema_version"] = 999
        self.state_path.write_text(json.dumps(raw), encoding="utf-8")
        with self.assertRaises(UnsupportedSchemaError):
            self.engine().start_or_resume("work-3")

    def test_failure_before_side_effect_can_retry_safely(self):
        e1 = self.engine()
        s1 = e1.start_or_resume("work-4")
        e1.prepare_effect(s1, value="gamma")
        e2 = self.engine()
        s2 = e2.start_or_resume("work-4")
        self.assertEqual(s2.phase, "EFFECT_INTENT_RECORDED")
        s2 = e2.execute_effect(s2)
        e2.complete(s2)
        self.assertEqual(e2.ledger.apply_count, 1)

    def test_timeout_unknown_outcome_is_reconciled_without_duplicate(self):
        e1 = self.engine()
        s1 = e1.start_or_resume("work-5")
        s1 = e1.prepare_effect(s1, value="delta")
        with self.assertRaises(UnknownOutcome):
            e1.execute_effect(s1, timeout_after_commit=True)
        self.assertEqual(e1.ledger.apply_count, 1)

        e2 = self.engine()
        s2 = e2.start_or_resume("work-5")
        self.assertEqual(s2.phase, "EFFECT_CONFIRMED")
        self.assertIsNotNone(s2.effect_receipt)
        e2.complete(s2)
        self.assertEqual(e2.ledger.apply_count, 1)

    def test_retry_after_success_is_idempotent(self):
        e1 = self.engine()
        s1 = e1.start_or_resume("work-6")
        s1 = e1.prepare_effect(s1, value="epsilon")
        s1 = e1.execute_effect(s1)
        receipt = s1.effect_receipt
        self.assertEqual(e1.ledger.apply_count, 1)

        raw = json.loads(self.state_path.read_text())
        raw["phase"] = "EFFECT_INTENT_RECORDED"
        raw["effect_receipt"] = None
        self.state_path.write_text(json.dumps(raw), encoding="utf-8")

        e2 = self.engine()
        s2 = e2.start_or_resume("work-6")
        self.assertEqual(s2.effect_receipt, receipt)
        self.assertEqual(e2.ledger.apply_count, 1)

    def test_stale_worker_is_fenced_from_external_effect(self):
        e1 = self.engine()
        stale = e1.start_or_resume("work-7")
        stale = e1.prepare_effect(stale, value="zeta")

        e2 = self.engine()
        fresh = e2.start_or_resume("work-7")
        self.assertGreater(fresh.fence, stale.fence)

        with self.assertRaises(FenceError):
            e1.ledger.apply(
                work_id=stale.work_id,
                effect_key=stale.effect_key,
                fence=stale.fence,
                value="zeta",
            )

    def test_stale_generation_cannot_overwrite_newer_state(self):
        store = JsonStateStore(self.state_path)
        ledger = EffectLedger(self.ledger_path)
        e = DurableEngine(store, ledger)
        old = e.start_or_resume("work-8")
        old_generation = old.generation
        old_fence = old.fence

        current = store.load()
        current.payload["new"] = True
        store.save(current, expected_generation=current.generation, expected_fence=current.fence)

        old.payload["stale"] = True
        with self.assertRaises(StaleStateError):
            store.save(old, expected_generation=old_generation, expected_fence=old_fence)


if __name__ == "__main__":
    unittest.main()
