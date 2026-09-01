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
from experiments.provider_generation_history.protocol import (
    GenerationDescriptor,
    PendingRotationBlocked,
)
from experiments.provider_generation_history.supported import SupportedHistoricalSharedAnchorLedger


def descriptor(generation, key):
    return GenerationDescriptor("anchor-A", generation, key.hex())


def attested(provider, generation, key):
    verifier = AttestationVerifier(
        {("anchor-A", generation): key}, ProviderIdentity("anchor-A", generation)
    )
    return AttestedCatchup(provider, verifier)


class LeaveActivationUnresolvedLedger(SupportedHistoricalSharedAnchorLedger):
    """Test-only surface that reaches marker reservation without recovery side effects."""

    def _recover_pending_activation(self):
        return None

    def _verify_activation_records(self):
        return True


class ActivationSchemaMigrationUnresolvedActivationTests(unittest.TestCase):
    def test_unresolved_activation_blocks_marker_and_never_confirms_provenance(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            key = b"provider-key-1"
            g1 = descriptor(1, key)
            provider = FencedActivationProvider("anchor-A", 1, key, value=0)
            SupportedHistoricalSharedAnchorLedger(
                path, attested(provider, 1, key), g1
            )

            activation_id = f"provider-activation:{g1.generation_id}:0"
            q = sqlite3.connect(path)
            try:
                q.execute(
                    "INSERT INTO provider_generation_activations VALUES(?,?,?,?,?,?,'SQL_COMMITTED')",
                    (
                        activation_id,
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

            with patch(
                "experiments.provider_generation_history.activation_schema_provenance."
                "SupportedHistoricalSharedAnchorLedger",
                LeaveActivationUnresolvedLedger,
            ):
                with self.assertRaises(PendingRotationBlocked):
                    ProvenancedHistoricalSharedAnchorLedger.migrate_activation_schema_v1(
                        path, attested(provider, 1, key), g1
                    )

            q = sqlite3.connect(path)
            try:
                marker = q.execute(
                    "SELECT status FROM shared_anchor_intents WHERE intent_id=?",
                    (_completion_intent().intent_id,),
                ).fetchone()
                activation = q.execute(
                    "SELECT status FROM provider_generation_activations WHERE activation_id=?",
                    (activation_id,),
                ).fetchone()
            finally:
                q.close()

            self.assertIsNone(marker)
            self.assertEqual(activation, ("SQL_COMMITTED",))


if __name__ == "__main__":
    unittest.main()
