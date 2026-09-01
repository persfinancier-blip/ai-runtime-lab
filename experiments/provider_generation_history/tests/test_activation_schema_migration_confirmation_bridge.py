import sqlite3
import tempfile
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
    _completion_intent,
)
from experiments.provider_generation_history.protocol import GenerationDescriptor
from experiments.provider_generation_history.supported import SupportedHistoricalSharedAnchorLedger
from experiments.shared_anchor_intent_ledger.protocol import PendingIntent


def descriptor(generation, key):
    return GenerationDescriptor("anchor-A", generation, key.hex())


def attested(provider, generation, key):
    verifier = AttestationVerifier(
        {("anchor-A", generation): key}, ProviderIdentity("anchor-A", generation)
    )
    return AttestedCatchup(provider, verifier)


class ActivationSchemaMigrationConfirmationBridgeTests(unittest.TestCase):
    def test_pre_confirmation_bridge_does_not_run_activation_recovery_constructor_side_effect(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            key = b"provider-key-1"
            g1 = descriptor(1, key)
            provider = FencedActivationProvider("anchor-A", 1, key, value=0)
            SupportedHistoricalSharedAnchorLedger(path, attested(provider, 1, key), g1)

            q = sqlite3.connect(path)
            try:
                q.execute("DROP TRIGGER block_intent_during_provider_activation")
                q.execute("DROP TABLE provider_generation_activations")
                q.commit()
            finally:
                q.close()

            original_recover = SupportedHistoricalSharedAnchorLedger._recover_pending_activation

            def forbid_recovery_before_confirmation(ledger):
                q = sqlite3.connect(path)
                try:
                    row = q.execute(
                        "SELECT status FROM shared_anchor_intents WHERE intent_id=?",
                        (_completion_intent().intent_id,),
                    ).fetchone()
                finally:
                    q.close()
                if row != ("CONFIRMED",):
                    raise AssertionError(
                        "activation recovery ran before schema provenance confirmation"
                    )
                return original_recover(ledger)

            with patch.object(
                SupportedHistoricalSharedAnchorLedger,
                "_recover_pending_activation",
                forbid_recovery_before_confirmation,
            ):
                migrated = ProvenancedHistoricalSharedAnchorLedger.migrate_activation_schema_v1(
                    path, attested(provider, 1, key), g1
                )

            self.assertTrue(migrated.verify_activation_schema_provenance())

    def test_restart_reauthenticates_confirmed_provenance_before_activation_recovery(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            key = b"provider-key-1"
            g1 = descriptor(1, key)
            provider = FencedActivationProvider("anchor-A", 1, key, value=0)
            SupportedHistoricalSharedAnchorLedger(path, attested(provider, 1, key), g1)

            q = sqlite3.connect(path)
            try:
                q.execute("DROP TRIGGER block_intent_during_provider_activation")
                q.execute("DROP TABLE provider_generation_activations")
                q.commit()
            finally:
                q.close()

            ProvenancedHistoricalSharedAnchorLedger.migrate_activation_schema_v1(
                path, attested(provider, 1, key), g1
            )

            # Same authenticated identity/key and tail, but no external result for the
            # migration request. A local CONFIRMED row alone must not authorize any
            # LAB-090 activation recovery side effect during restart.
            fresh_provider = FencedActivationProvider("anchor-A", 1, key, value=1)

            def forbidden_recovery(_ledger):
                raise AssertionError(
                    "activation recovery ran before confirmed provenance was reauthenticated"
                )

            with patch.object(
                SupportedHistoricalSharedAnchorLedger,
                "_recover_pending_activation",
                forbidden_recovery,
            ):
                with self.assertRaises(PendingIntent):
                    ProvenancedHistoricalSharedAnchorLedger(
                        path, attested(fresh_provider, 1, key), g1
                    )


if __name__ == "__main__":
    unittest.main()
