from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from experiments.anchor_attestation.protocol import (
    AttestationVerifier,
    AttestedCatchup,
    ProviderIdentity,
)
from experiments.provider_generation_history.activation import FencedActivationProvider
from experiments.provider_generation_history.activation_schema_migration import (
    migrate_activation_schema_v1,
)
from experiments.provider_generation_history.protocol import GenerationDescriptor


def descriptor(generation: int, key: bytes) -> GenerationDescriptor:
    return GenerationDescriptor("anchor-A", generation, key.hex())


def attested(provider, generation: int, key: bytes) -> AttestedCatchup:
    verifier = AttestationVerifier(
        {("anchor-A", generation): key},
        ProviderIdentity("anchor-A", generation),
    )
    return AttestedCatchup(provider, verifier)


class ProviderHistoryCapabilitySurfaceTests(unittest.TestCase):
    def test_public_history_view_cannot_recover_coordinator_mutation_surface(self):
        """Delegating the supported ledger must not delegate history mutation helpers."""
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "ledger.sqlite"
            k1 = b"provider-key-1"
            k2 = b"provider-key-2"
            g1 = descriptor(1, k1)
            g2 = descriptor(2, k2)

            provider = FencedActivationProvider("anchor-A", 1, k1, value=0)
            ledger = migrate_activation_schema_v1(
                path,
                attested(provider, 1, k1),
                g1,
            )
            self.assertEqual(provider.value, 1)

            history = ledger.provider_history
            self.assertEqual(history.current().generation, 1)
            self.assertEqual(history.make_transition(g1, g2).new_generation_id, g2.generation_id)

            # The public object is an inspection view, not the live strategy.
            for forbidden in (
                "rotate",
                "_rotate_locked",
                "_current_locked",
                "_verify_durable_locked",
                "_load_receipt_locked",
                "store_receipt",
                "_con",
                "path",
                "bootstrap",
            ):
                with self.assertRaises(AttributeError, msg=forbidden):
                    getattr(history, forbidden)

            with self.assertRaises(AttributeError):
                history.extra_capability = object()

            # The retained trust root is construction-bound even if internal state
            # is reached by Python introspection; verification must keep using g1.
            internal = ledger._history()
            self.assertEqual(internal.bootstrap.generation_id, g1.generation_id)
            with self.assertRaises(AttributeError):
                internal.bootstrap = g2
            with self.assertRaises(AttributeError):
                internal._bootstrap_generation = g2
            self.assertEqual(internal.bootstrap.generation_id, g1.generation_id)
            self.assertTrue(internal.verify_durable())

            # A caller may still possess the ledger connection, but the delegated
            # public history surface supplies no locked mutation primitive to pair it with.
            q = ledger._con()
            try:
                q.execute("BEGIN IMMEDIATE")
                with self.assertRaises(AttributeError):
                    history._rotate_locked(q, g2, history.make_transition(g1, g2))
                q.rollback()
            finally:
                q.close()

            self.assertEqual(ledger.provider_history.current().generation, 1)
            self.assertEqual(
                ledger._descriptor_from_attested(ledger.attested).generation,
                1,
            )


if __name__ == "__main__":
    unittest.main()
