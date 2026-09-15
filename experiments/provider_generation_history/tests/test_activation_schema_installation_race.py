import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path

from experiments.anchor_attestation.protocol import (
    AttestationVerifier,
    AttestedCatchup,
    ProviderIdentity,
)
from experiments.provider_generation_history.activation import FencedActivationProvider
from experiments.provider_generation_history.protocol import (
    GenerationDescriptor,
    HistoricalVerificationError,
    PendingRotationBlocked,
)
from experiments.provider_generation_history.supported import SupportedHistoricalSharedAnchorLedger
from experiments.shared_anchor_intent_ledger.protocol import Intent


def descriptor(generation, key):
    return GenerationDescriptor("anchor-A", generation, key.hex())


def attested(provider, generation, key):
    verifier = AttestationVerifier(
        {("anchor-A", generation): key}, ProviderIdentity("anchor-A", generation)
    )
    return AttestedCatchup(provider, verifier)


class PausingConnection:
    def __init__(self, inner, table_created, release_install):
        self._inner = inner
        self._table_created = table_created
        self._release_install = release_install

    def _maybe_pause(self, sql):
        if "provider_generation_activations" in sql and "CREATE TABLE" in sql:
            self._table_created.set()
            if not self._release_install.wait(timeout=5):
                raise RuntimeError("activation schema installation pause timed out")

    def execute(self, sql, parameters=()):
        result = self._inner.execute(sql, parameters)
        self._maybe_pause(sql)
        return result

    def executescript(self, sql_script):
        result = self._inner.executescript(sql_script)
        self._maybe_pause(sql_script)
        return result

    def __getattr__(self, name):
        return getattr(self._inner, name)


class PausingActivationSchemaLedger(SupportedHistoricalSharedAnchorLedger):
    def __init__(self, *args, table_created, release_install, **kwargs):
        self._table_created = table_created
        self._release_install = release_install
        super().__init__(*args, **kwargs)

    def _con(self):
        return PausingConnection(
            super()._con(), self._table_created, self._release_install
        )


class ActivationSchemaInstallationRaceTests(unittest.TestCase):
    def test_missing_trigger_reinstall_does_not_admit_writer_with_unresolved_activation(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            key = b"provider-key-1"
            g1 = descriptor(1, key)
            provider = FencedActivationProvider("anchor-A", 1, key, value=0)
            live = SupportedHistoricalSharedAnchorLedger(
                path, attested(provider, 1, key), g1
            )

            q = sqlite3.connect(path)
            try:
                q.execute("DROP TRIGGER block_intent_during_provider_activation")
                q.execute(
                    "INSERT INTO provider_generation_activations VALUES(?,?,?,?,?,?,'SQL_COMMITTED')",
                    (
                        "provider-activation:" + g1.generation_id + ":0",
                        g1.generation_id,
                        g1.provider_id,
                        g1.generation,
                        0,
                        1,
                    ),
                )
                q.commit()
            finally:
                q.close()

            table_created = threading.Event()
            release_install = threading.Event()
            restart_error = []
            writer_error = []

            def restart():
                try:
                    PausingActivationSchemaLedger(
                        path,
                        attested(provider, 1, key),
                        g1,
                        table_created=table_created,
                        release_install=release_install,
                    )
                except Exception as exc:
                    restart_error.append(exc)

            def writer():
                try:
                    live.reserve(
                        Intent(
                            "writer-during-trigger-reinstall",
                            "component-A",
                            "migration",
                            {"x": 1},
                        )
                    )
                except Exception as exc:
                    writer_error.append(exc)

            restart_thread = threading.Thread(target=restart)
            restart_thread.start()
            self.assertTrue(table_created.wait(timeout=5))

            writer_thread = threading.Thread(target=writer)
            writer_thread.start()
            writer_thread.join(timeout=0.2)

            # Correct installation holds the SQLite writer lock across table+trigger
            # installation, so this writer must not complete in the exposed gap.
            admitted_before_trigger_install = not writer_thread.is_alive()

            release_install.set()
            restart_thread.join(timeout=5)
            writer_thread.join(timeout=5)

            self.assertFalse(
                admitted_before_trigger_install,
                "writer completed between activation table verification and trigger install",
            )
            self.assertTrue(restart_error)
            self.assertIsInstance(restart_error[0], HistoricalVerificationError)
            self.assertEqual(len(writer_error), 1)
            self.assertIsInstance(writer_error[0], PendingRotationBlocked)
            self.assertEqual(provider.value, 0)


if __name__ == "__main__":
    unittest.main()
