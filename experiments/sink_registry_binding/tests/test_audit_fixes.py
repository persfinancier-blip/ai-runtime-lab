import tempfile
import unittest

from experiments.sink_registry_binding import protocol as base
from experiments.sink_registry_binding.audit_fixes import (
    CorrectedRegistryBoundJournal,
    CorrectedRegistryBrokerWorker,
)
from experiments.sink_registry_binding.protocol import (
    HistoricalExecutionBlocked,
    RegistryAuthError,
    RegistryBindingError,
)
from experiments.sink_registry_binding.tests.test_protocol import Tests, Sink, Req, Bound, Journal


class LegacyAuditRegistryBoundJournal(CorrectedRegistryBoundJournal):
    """Test-only adapter preserving the historical dict capability fixture.

    The supported surface is stricter; this subclass exists only so inherited
    prototype tests can continue exercising registry-specific audit behavior.
    """

    def _capability_fields(self, capability, *, now):
        return base.RegistryBoundJournal._capability_fields(
            self, capability, now=now
        )


class AuditFixTests(Tests):
    def setup(self, td):
        j = Journal(f"{td}/j.db")
        r = LegacyAuditRegistryBoundJournal(Bound(j), self.auth)
        return j, r

    def test_supported_surface_rejects_unauthenticated_new_capability(self):
        with tempfile.TemporaryDirectory() as td:
            j = Journal(f"{td}/strict.db")
            r = CorrectedRegistryBoundJournal(Bound(j), self.auth)
            with self.assertRaises(RegistryBindingError):
                r.reserve(
                    Req("strict", "p"),
                    {"sink_id": "sink-A", "reconcile_by_key": True},
                    self.entry(),
                    now=0,
                )
            q = j._con()
            try:
                self.assertEqual(
                    q.execute("SELECT COUNT(*) FROM broker_requests").fetchone()[0],
                    0,
                )
            finally:
                q.close()

    def test_supported_worker_rejects_unaudited_registry_journal(self):
        with tempfile.TemporaryDirectory() as td:
            j = Journal(f"{td}/prototype.db")
            prototype = base.RegistryBoundJournal(Bound(j), self.auth)
            with self.assertRaises(RegistryBindingError):
                CorrectedRegistryBrokerWorker(
                    prototype, self.runtime(Sink()), b"x"
                )

    def test_preexisting_content_address_row_is_verified_before_activation(self):
        with tempfile.TemporaryDirectory() as td:
            j, r = self.setup(td)
            entry = self.entry()
            q = j._con()
            try:
                q.execute(
                    "INSERT INTO sink_registry_entries VALUES(?,?,?,?,?,?,?,?,?,?)",
                    (
                        entry.entry_digest,
                        entry.sink_id,
                        entry.generation,
                        entry.adapter_digest,
                        entry.endpoint_origin,
                        entry.operation_profile,
                        entry.predecessor_entry_digest,
                        entry.issuer_id,
                        entry.issuer_generation,
                        "0" * 64,
                    ),
                )
                q.commit()
            finally:
                q.close()
            with self.assertRaises(RegistryAuthError):
                r.observe(entry)
            q = j._con()
            try:
                self.assertEqual(
                    q.execute("SELECT COUNT(*) FROM sink_registry_heads").fetchone()[0],
                    0,
                )
            finally:
                q.close()

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

    def _make_unknown_then_rotate(self, td):
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
        return r, sink, w2, e2

    def test_unknown_requires_current_reconcile_capability(self):
        with tempfile.TemporaryDirectory() as td:
            _, sink, w2, e2 = self._make_unknown_then_rotate(td)
            with self.assertRaises(HistoricalExecutionBlocked):
                w2.process(
                    Req("unknown", "p"),
                    {"sink_id": "sink-A", "reconcile_by_key": False},
                    e2,
                    now=1,
                )
            self.assertEqual(sink.count, 1)

    def test_unknown_missing_reconcile_capability_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            _, sink, w2, e2 = self._make_unknown_then_rotate(td)
            with self.assertRaises(HistoricalExecutionBlocked):
                w2.process(
                    Req("unknown", "p"),
                    {"sink_id": "sink-A"},
                    e2,
                    now=1,
                )
            self.assertEqual(sink.count, 1)


if __name__ == "__main__":
    unittest.main()
