import sqlite3
import tempfile
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
)
from experiments.provider_generation_history.supported import SupportedHistoricalSharedAnchorLedger


def descriptor(generation, key):
    return GenerationDescriptor("anchor-A", generation, key.hex())


def attested(provider, generation, key):
    verifier = AttestationVerifier(
        {("anchor-A", generation): key}, ProviderIdentity("anchor-A", generation)
    )
    return AttestedCatchup(provider, verifier)


class ActivationSchemaTamperRestartTests(unittest.TestCase):
    def test_restart_rejects_activation_table_replaced_by_empty_view(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            key = b"provider-key-1"
            g1 = descriptor(1, key)
            provider = FencedActivationProvider("anchor-A", 1, key, value=0)
            SupportedHistoricalSharedAnchorLedger(
                path, attested(provider, 1, key), g1
            )

            q = sqlite3.connect(path)
            try:
                q.executescript(
                    """
                    DROP TRIGGER block_intent_during_provider_activation;
                    DROP TABLE provider_generation_activations;
                    CREATE VIEW provider_generation_activations AS
                    SELECT
                      CAST(NULL AS TEXT) AS activation_id,
                      CAST(NULL AS TEXT) AS new_generation_id,
                      CAST(NULL AS TEXT) AS provider_id,
                      CAST(NULL AS INTEGER) AS generation,
                      CAST(NULL AS INTEGER) AS expected_position,
                      CAST(NULL AS INTEGER) AS fence,
                      CAST(NULL AS TEXT) AS status
                    WHERE 0;
                    CREATE TRIGGER block_intent_during_provider_activation
                    BEFORE INSERT ON shared_anchor_intents
                    WHEN EXISTS(
                      SELECT 1 FROM provider_generation_activations WHERE status='SQL_COMMITTED'
                    )
                    BEGIN
                      SELECT RAISE(ABORT, 'provider activation unresolved');
                    END;
                    """
                )
                q.commit()
            finally:
                q.close()

            with self.assertRaises(HistoricalVerificationError):
                SupportedHistoricalSharedAnchorLedger(
                    path, attested(provider, 1, key), g1
                )


if __name__ == "__main__":
    unittest.main()
