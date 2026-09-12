"""LAB-099 isolated RED-intent contract tests.

This file is intentionally NOT named ``test_*.py`` so normal repository discovery does
not accidentally treat an unexecuted contract as a passing regression. Run it
explicitly once the LAB-099 precursor-cutover surface exists and exact repository
materialization is available.

The tests are deliberately written against a narrow future seam rather than changing
production behavior on the LAB-092 branch. They freeze the first six source-proved
cutover cases from the durable LAB-099 contract.
"""

from __future__ import annotations

import importlib
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
from experiments.provider_generation_history.activation_schema_provenance import (
    ProvenancedHistoricalSharedAnchorLedger,
)
from experiments.provider_generation_history.protocol import GenerationDescriptor
from experiments.provider_generation_history.supported import SupportedHistoricalSharedAnchorLedger


LAB099_MODULE = "experiments.provider_generation_history.activation_reservation_provenance"


def descriptor(generation: int, key: bytes) -> GenerationDescriptor:
    return GenerationDescriptor("anchor-A", generation, key.hex())


def attested(provider, generation: int, key: bytes) -> AttestedCatchup:
    verifier = AttestationVerifier(
        {("anchor-A", generation): key}, ProviderIdentity("anchor-A", generation)
    )
    return AttestedCatchup(provider, verifier)


class Lab099PrecursorCutoverRedIntentTests(unittest.TestCase):
    """First executable contract slice; expected RED until LAB-099 exists."""

    def _future_surface(self):
        try:
            module = importlib.import_module(LAB099_MODULE)
        except ModuleNotFoundError as exc:
            self.fail(
                "RED intent: LAB-099 precursor-cutover production module does not exist yet: "
                f"{exc}"
            )

        required = (
            "PrecursorCutoverMigrationRequired",
            "PrecursorCutoverVerificationError",
            "PrecursorGovernedHistoricalSharedAnchorLedger",
            "classify_precursor_cutover_v1",
        )
        missing = [name for name in required if not hasattr(module, name)]
        if missing:
            self.fail(
                "RED intent: LAB-099 precursor-cutover surface is incomplete: "
                + ", ".join(missing)
            )
        return module

    def _legacy_lab092_complete(self):
        td = tempfile.TemporaryDirectory()
        path = Path(td.name) / "shared.db"
        key = b"provider-key-1"
        provider = FencedActivationProvider("anchor-A", 1, key, value=0)
        g1 = descriptor(1, key)

        # Build the inherited database, erase only LAB-090 activation DDL to model
        # a legitimate pre-LAB-090 source, then complete the real LAB-092 migration.
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
        return td, path, key, provider, g1

    def test_lab092_v1_completion_alone_is_not_precursor_authority(self):
        surface = self._future_surface()
        td, path, key, provider, g1 = self._legacy_lab092_complete()
        with td:
            state = surface.classify_precursor_cutover_v1(path)
            self.assertEqual(state, "ABSENT")
            with self.assertRaises(surface.PrecursorCutoverMigrationRequired):
                surface.PrecursorGovernedHistoricalSharedAnchorLedger(
                    path, attested(provider, 1, key), g1
                )

    def test_orphan_precursor_ddl_without_prepared_fails_closed(self):
        surface = self._future_surface()
        td, path, key, provider, g1 = self._legacy_lab092_complete()
        with td:
            surface.install_precursor_relation_for_test_only(path)
            self.assertEqual(
                surface.classify_precursor_cutover_v1(path),
                "ORPHAN_UNAUTHENTICATED_SCHEMA",
            )
            with self.assertRaises(surface.PrecursorCutoverVerificationError):
                surface.PrecursorGovernedHistoricalSharedAnchorLedger(
                    path, attested(provider, 1, key), g1
                )

    def test_atomic_ddl_prepared_crash_resumes_only_exact_prepared(self):
        surface = self._future_surface()
        td, path, key, provider, g1 = self._legacy_lab092_complete()
        with td:
            prepared = surface.install_atomic_prepared_cutover_for_test_only(
                path, attested(provider, 1, key), g1
            )
            self.assertEqual(
                surface.classify_precursor_cutover_v1(path), "PREPARED_INCOMPLETE"
            )
            recovered = surface.resume_precursor_cutover_v1(
                path,
                attested(provider, 1, key),
                g1,
                expected_prepared_digest=prepared.prepared_event_digest,
            )
            self.assertEqual(
                recovered.prepared_event_digest, prepared.prepared_event_digest
            )
            self.assertEqual(surface.classify_precursor_cutover_v1(path), "CONFIRMED")

    def test_stale_or_forked_parent_epoch_replay_is_rejected(self):
        surface = self._future_surface()
        td, path, key, provider, g1 = self._legacy_lab092_complete()
        with td:
            prepared = surface.build_prepared_cutover_for_test_only(
                path, attested(provider, 1, key), g1
            )
            surface.advance_provenance_parent_for_test_only(path)
            with self.assertRaises(surface.PrecursorCutoverVerificationError):
                surface.commit_prepared_cutover_for_test_only(path, prepared)

    def test_confirmed_binds_exact_prepared_digest(self):
        surface = self._future_surface()
        td, path, key, provider, g1 = self._legacy_lab092_complete()
        with td:
            prepared = surface.install_atomic_prepared_cutover_for_test_only(
                path, attested(provider, 1, key), g1
            )
            sibling = surface.build_sibling_prepared_for_test_only(path, prepared)
            surface.install_confirmed_for_test_only(
                path,
                prepared_event_digest=sibling.prepared_event_digest,
            )
            with self.assertRaises(surface.PrecursorCutoverVerificationError):
                surface.PrecursorGovernedHistoricalSharedAnchorLedger(
                    path, attested(provider, 1, key), g1
                )

    def test_confirmed_forbids_downgrade_after_precursor_relation_deletion(self):
        surface = self._future_surface()
        td, path, key, provider, g1 = self._legacy_lab092_complete()
        with td:
            surface.migrate_precursor_cutover_v1(
                path, attested(provider, 1, key), g1
            )
            self.assertEqual(surface.classify_precursor_cutover_v1(path), "CONFIRMED")
            surface.delete_precursor_relation_for_test_only(path)
            with self.assertRaises(surface.PrecursorCutoverVerificationError):
                surface.PrecursorGovernedHistoricalSharedAnchorLedger(
                    path, attested(provider, 1, key), g1
                )


if __name__ == "__main__":
    unittest.main()
