"""Non-discoverable LAB-099 persisted CONFIRMED cross-binding contract.

This file freezes fixture-level negative cases for the exact CONFIRMED bridge. It is
not a production RED/GREEN claim and is intentionally not named ``test_*.py``. Run
explicitly only from an exact repository materialization.
"""
from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from experiments.provider_generation_history.tests import lab099_confirmed_fixture_row_verifier as verifier
from experiments.provider_generation_history.tests import lab099_confirmed_ledger_reference as bridge
from experiments.provider_generation_history.tests import lab099_cutover_storage_reference as storage
from experiments.provider_generation_history.tests import lab099_precursor_reference_vectors as authority


_SHARED_ANCHOR_DDL = """
CREATE TABLE shared_anchor_intents(
  intent_id TEXT PRIMARY KEY,
  component_id TEXT NOT NULL,
  intent_type TEXT NOT NULL,
  payload_digest TEXT NOT NULL,
  provider_id TEXT NOT NULL,
  provider_generation INTEGER NOT NULL,
  predecessor_position INTEGER NOT NULL,
  position INTEGER NOT NULL UNIQUE,
  request_id TEXT NOT NULL UNIQUE,
  status TEXT NOT NULL CHECK(status IN ('PREPARED','CONFIRMED')),
  receipt_binding TEXT
)
"""


class _Provider:
    def reconcile_increment(self, *, challenge, request_id):
        del challenge
        entry = bridge.reference_confirmed_entry()
        if request_id != entry["request_id"]:
            return None
        return SimpleNamespace(
            provider_id=entry["provider_id"],
            generation=entry["provider_generation"],
            position=entry["position"],
            request_id=entry["request_id"],
        )


class _Verifier:
    def __init__(self):
        self.expected = SimpleNamespace(
            provider_id=bridge.REFERENCE_PROVIDER_ID,
            generation=bridge.REFERENCE_PROVIDER_GENERATION,
        )

    def verify(self, obs, *, expected_challenge, allowed_kinds):
        del expected_challenge
        if allowed_kinds != {"RECONCILE"}:
            raise AssertionError("unexpected attestation kind set")
        return obs


class _Attested:
    def __init__(self):
        self.provider = _Provider()
        self.verifier = _Verifier()

    def challenge(self):
        return b"lab099-confirmed-reference-challenge"


def _install_exact_confirmed(path: Path) -> None:
    values = authority.PREPARED_REFERENCE_VALUES
    entry = bridge.reference_confirmed_entry()
    q = sqlite3.connect(path)
    try:
        q.execute(storage.CUTOVER_RELATION_SQL)
        q.execute(_SHARED_ANCHOR_DDL)
        q.execute(
            "INSERT INTO provider_activation_reservation_cutovers VALUES(?,?,?,?,?,?,?,?,?)",
            (
                values[1], values[5], values[6], values[3], values[4],
                authority.PREPARED_CANONICAL_BYTES, authority.PREPARED_DIGEST,
                authority.CONFIRMATION_NONCE, entry["intent_id"],
            ),
        )
        q.execute(
            "INSERT INTO shared_anchor_intents VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            (
                entry["intent_id"], entry["component_id"], entry["intent_type"],
                entry["payload_digest"], entry["provider_id"],
                entry["provider_generation"], entry["predecessor_position"],
                entry["position"], entry["request_id"], entry["status"],
                entry["receipt_binding"],
            ),
        )
        q.commit()
    finally:
        q.close()


def _verify(path: Path, *, head: bytes = bridge.REFERENCE_CONFIRMED_HEAD_DIGEST) -> bool:
    return verifier.verify_installed_confirmed_cutover(
        path,
        _Attested(),
        prepared_event_digest=authority.PREPARED_DIGEST,
        expected_confirmed_position=bridge.REFERENCE_POSITION,
        expected_confirmed_head_digest=head,
    )


class Lab099PersistedConfirmedCrossBindingContract(unittest.TestCase):
    def _db(self):
        td = tempfile.TemporaryDirectory()
        path = Path(td.name) / "confirmed.db"
        _install_exact_confirmed(path)
        return td, path

    def test_exact_confirmed_reference_is_accepted(self):
        td, path = self._db()
        with td:
            self.assertTrue(_verify(path))

    def test_changed_receipt_binding_fails_closed(self):
        td, path = self._db()
        with td:
            verifier.tamper_confirmed_fixture_for_test_only(
                path, prepared_event_digest=authority.PREPARED_DIGEST,
                field="receipt_binding",
            )
            with self.assertRaises(verifier.ConfirmedFixtureRowVerificationError):
                _verify(path)

    def test_changed_confirmed_position_fails_closed(self):
        td, path = self._db()
        with td:
            verifier.tamper_confirmed_fixture_for_test_only(
                path, prepared_event_digest=authority.PREPARED_DIGEST,
                field="position",
            )
            with self.assertRaises(verifier.ConfirmedFixtureRowVerificationError):
                _verify(path)

    def test_changed_external_confirmed_head_fails_closed(self):
        td, path = self._db()
        with td:
            wrong = bytes(32)
            self.assertNotEqual(wrong, bridge.REFERENCE_CONFIRMED_HEAD_DIGEST)
            with self.assertRaises(verifier.ConfirmedFixtureRowVerificationError):
                _verify(path, head=wrong)

    def test_changed_prepared_digest_ancestry_fails_closed(self):
        td, path = self._db()
        with td:
            verifier.tamper_confirmed_fixture_for_test_only(
                path, prepared_event_digest=authority.PREPARED_DIGEST,
                field="prepared_digest",
            )
            with self.assertRaises(verifier.ConfirmedFixtureRowVerificationError):
                _verify(path)


if __name__ == "__main__":
    unittest.main()
