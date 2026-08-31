import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

from experiments.anchor_attestation.protocol import (
    AttestationVerifier,
    AttestedCatchup,
    ProviderIdentity,
)
from experiments.provider_generation_history.activation import FencedActivationProvider
from experiments.provider_generation_history.activation_schema_provenance import (
    ProvenancedHistoricalSharedAnchorLedger,
)
from experiments.provider_generation_history.protocol import GenerationDescriptor
from experiments.provider_generation_history.supported import SupportedHistoricalSharedAnchorLedger
from experiments.shared_anchor_intent_ledger.protocol import Intent


def descriptor(generation, key):
    return GenerationDescriptor("anchor-A", generation, key.hex())


def attested(provider, generation, key):
    verifier = AttestationVerifier(
        {("anchor-A", generation): key}, ProviderIdentity("anchor-A", generation)
    )
    return AttestedCatchup(provider, verifier)


class PauseAfterActivationDDL(SupportedHistoricalSharedAnchorLedger):
    ddl_installed = None
    allow_marker = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ddl_installed.set()
        if not self.allow_marker.wait(timeout=5):
            raise RuntimeError("activation migration marker pause timed out")


class ActivationSchemaMigrationConcurrencyTests(unittest.TestCase):
    def test_writer_cannot_enter_between_activation_ddl_and_provenance_marker(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            key = b"provider-key-1"
            g1 = descriptor(1, key)
            provider = FencedActivationProvider("anchor-A", 1, key, value=0)
            live = SupportedHistoricalSharedAnchorLedger(
                path, attested(provider, 1, key), g1
            )

            # Recreate the legitimate pre-LAB-090 migration state while retaining
            # the already-initialized shared-anchor ledger.
            q = sqlite3.connect(path)
            try:
                q.execute("DROP TRIGGER block_intent_during_provider_activation")
                q.execute("DROP TABLE provider_generation_activations")
                q.commit()
            finally:
                q.close()

            ddl_installed = threading.Event()
            allow_marker = threading.Event()
            writer_finished = threading.Event()
            migration_errors = []
            writer_errors = []

            PauseAfterActivationDDL.ddl_installed = ddl_installed
            PauseAfterActivationDDL.allow_marker = allow_marker

            def migrate():
                try:
                    with patch(
                        "experiments.provider_generation_history.activation_schema_provenance."
                        "SupportedHistoricalSharedAnchorLedger",
                        PauseAfterActivationDDL,
                    ):
                        ProvenancedHistoricalSharedAnchorLedger.migrate_activation_schema_v1(
                            path, attested(provider, 1, key), g1
                        )
                except Exception as exc:
                    migration_errors.append(exc)

            def writer():
                try:
                    live.reserve(
                        Intent(
                            "writer-during-activation-schema-migration",
                            "component-A",
                            "migration",
                            {"x": 1},
                        )
                    )
                except Exception as exc:
                    writer_errors.append(exc)
                finally:
                    writer_finished.set()

            migration_thread = threading.Thread(target=migrate)
            migration_thread.start()
            self.assertTrue(ddl_installed.wait(timeout=5))

            writer_thread = threading.Thread(target=writer)
            writer_thread.start()
            writer_thread.join(timeout=0.2)
            admitted_before_provenance = writer_finished.is_set()

            # Always release the migration thread before asserting so a RED result
            # cannot strand the test process.
            allow_marker.set()
            migration_thread.join(timeout=5)
            writer_thread.join(timeout=5)

            self.assertFalse(
                admitted_before_provenance,
                "shared-anchor writer entered after activation DDL commit but before provenance marker reservation",
            )
            self.assertFalse(migration_errors)
            self.assertTrue(writer_finished.is_set())
            self.assertLessEqual(len(writer_errors), 1)


if __name__ == "__main__":
    unittest.main()
