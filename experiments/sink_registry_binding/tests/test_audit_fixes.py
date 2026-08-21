import tempfile
import unittest

from experiments.sink_registry_binding.audit_fixes import (
    CorrectedRegistryBoundJournal,
    CorrectedRegistryBrokerWorker,
)
from experiments.sink_registry_binding.protocol import HistoricalExecutionBlocked
from experiments.sink_registry_binding.tests.test_protocol import Tests, Sink, Req, Bound, Journal


class AuditFixTests(Tests):
    def setup(self, td):
        j = Journal(f"{td}/j.db")
        r = CorrectedRegistryBoundJournal(Bound(j), self.auth)
        return j, r

    def test_confirmed_receipt_ignores_stale_inputs(self):
        with tempfile.TemporaryDirectory() as td:
            _, r = self.setup(td)
            e1 = self.entry()
            sink = Sink()
            w = CorrectedRegistryBrokerWorker(r, self.runtime(sink), b"x")
            self.assertEqual(
                w.process(Req("terminal", "p"), {"sink_id": "sink-A"}, e1, now=0)[0],
                "COMMITTED",
            )
            e2 = self.entry(2, pred=e1.entry_digest, endpoint="https://b.example")
            r.observe(e2)
            attacker = CorrectedRegistryBrokerWorker(
                r, self.runtime(Sink(), "evil", "https://evil"), b"x"
            )
            self.assertEqual(
                attacker.process(
                    Req("terminal", "p"), {"sink_id": "wrong"}, e1, now=99
                )[0],
                "ALREADY_COMMITTED",
            )

    def test_unknown_requires_current_reconcile_capability(self):
        with tempfile.TemporaryDirectory() as td:
            _, r = self.setup(td)
            e1 = self.entry()
            sink = Sink()
            w1 = CorrectedRegistryBrokerWorker(r, self.runtime(sink), b"x")
            with self.assertRaises(Exception):
                w1.process(
                    Req("unknown", "p"),
                    {"sink_id": "sink-A"},
                    e1,
                    now=0,
                    timeout_after_commit=True,
                )
            e2 = self.entry(2, pred=e1.entry_digest, endpoint="https://b.example")
            r.observe(e2)
            w2 = CorrectedRegistryBrokerWorker(
                r, self.runtime(sink, endpoint="https://b.example"), b"x"
            )
            with self.assertRaises(HistoricalExecutionBlocked):
                w2.process(
                    Req("unknown", "p"),
                    {"sink_id": "sink-A", "reconcile_by_key": False},
                    e2,
                    now=1,
                )
            self.assertEqual(sink.count, 1)


if __name__ == "__main__":
    unittest.main()
