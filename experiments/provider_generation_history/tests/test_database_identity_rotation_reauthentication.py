from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from experiments.anchor_attestation.protocol import (
    AttestationVerifier,
    AttestedCatchup,
    ProviderIdentity,
    SignedAnchorProvider,
)
from experiments.provider_generation_history.database_identity_migration import (
    migrate_database_identity,
)
from experiments.provider_generation_history.protocol import (
    GenerationDescriptor,
    HistoricalVerificationError,
)
from experiments.provider_generation_history.supported import (
    SupportedHistoricalSharedAnchorLedger,
)


def _descriptor(generation: int, key: bytes) -> GenerationDescriptor:
    return GenerationDescriptor("anchor-A", generation, key.hex())


def _attested(provider, generation: int, key: bytes) -> AttestedCatchup:
    verifier = AttestationVerifier(
        {("anchor-A", generation): key},
        ProviderIdentity("anchor-A", generation),
    )
    return AttestedCatchup(provider, verifier)


class DatabaseIdentityRotationReauthenticationTests(unittest.TestCase):
    def test_complete_identity_reauthenticates_through_historical_receipt_after_rotation(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            k1 = b"provider-key-1"
            k2 = b"provider-key-2"
            g1 = _descriptor(1, k1)
            g2 = _descriptor(2, k2)

            p1 = SignedAnchorProvider("anchor-A", 1, k1, value=0)
            ledger = SupportedHistoricalSharedAnchorLedger(
                path, _attested(p1, 1, k1), g1
            )
            digest = migrate_database_identity(ledger, ledger.provider_history)

            q = sqlite3.connect(path)
            request_id = q.execute(
                """SELECT intent_request_id
                   FROM provider_history_database_identity
                   WHERE singleton=1"""
            ).fetchone()[0]
            receipt = q.execute(
                """SELECT provider_id,generation,position,request_id
                   FROM historical_provider_receipts
                   WHERE request_id=?""",
                (request_id,),
            ).fetchone()
            q.close()
            self.assertEqual(receipt, ("anchor-A", 1, 1, request_id))

            p2 = SignedAnchorProvider("anchor-A", 2, k2, value=1)
            ledger.rotate_provider(
                g2,
                ledger.provider_history.make_transition(g1, g2),
                _attested(p2, 2, k2),
            )
            p1.available = False

            self.assertEqual(
                migrate_database_identity(ledger, ledger.provider_history),
                digest,
            )

            q = sqlite3.connect(path)
            q.execute(
                "DELETE FROM historical_provider_receipts WHERE request_id=?",
                (request_id,),
            )
            q.commit()
            q.close()

            with self.assertRaises(HistoricalVerificationError):
                migrate_database_identity(ledger, ledger.provider_history)


if __name__ == "__main__":
    unittest.main()
