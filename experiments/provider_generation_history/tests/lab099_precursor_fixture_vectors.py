"""Test-only executable LAB-099 PREPARED/CONFIRMED fixture vectors.

This module turns the already-frozen LAB-099 PREPARED canonical bytes and cutover
storage identity into one mechanical SQLite mutation plan. CONFIRMED mutation is
strictly limited to the independently frozen exact ledger/provenance bridge; it does
not synthesize receipt/head/epoch authority for arbitrary PREPARED digests.

It deliberately does not import production LAB-099 code and does not perform any
external provider call.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any

from experiments.provider_generation_history.tests import (
    lab099_confirmed_ledger_reference as confirmed_bridge,
)
from experiments.provider_generation_history.tests import (
    lab099_cutover_storage_reference as storage,
)
from experiments.provider_generation_history.tests import (
    lab099_precursor_reference_vectors as authority,
)
from experiments.provider_generation_history.tests import (
    lab099_precursor_relation_reference as relation,
)


class FixtureVectorError(RuntimeError):
    pass


def _canon(obj: object) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _request_id(
    position: int,
    intent_id: str,
    component_id: str,
    intent_type: str,
    payload_digest: str,
) -> str:
    binding = hashlib.sha256(
        _canon(
            {
                "position": position,
                "intent_id": intent_id,
                "component_id": component_id,
                "intent_type": intent_type,
                "payload_digest": payload_digest,
            }
        )
    ).hexdigest()
    return f"shared-anchor:{position}:{binding}"


def _expected_provider(attested: Any) -> tuple[str, int]:
    verifier = getattr(attested, "verifier", None)
    expected = getattr(verifier, "expected", None)
    provider_id = getattr(expected, "provider_id", None)
    generation = getattr(expected, "generation", None)
    if type(provider_id) is not str or not provider_id:
        raise FixtureVectorError("attested verifier expected provider_id is unavailable")
    if type(generation) is not int or generation < 1:
        raise FixtureVectorError("attested verifier expected generation is unavailable")
    return provider_id, generation


def _read_reservation_snapshot(
    path: Path | str,
    attested: Any,
    bootstrap: Any,
) -> tuple[str, int, int]:
    validate = getattr(bootstrap, "validate", None)
    if not callable(validate):
        raise FixtureVectorError("bootstrap must expose validate()")
    validate()
    expected_provider_id, expected_generation = _expected_provider(attested)

    q = sqlite3.connect(str(path), timeout=5, isolation_level=None)
    q.execute("PRAGMA busy_timeout=5000")
    try:
        pending = q.execute(
            "SELECT COUNT(*) FROM shared_anchor_intents WHERE status='PREPARED'"
        ).fetchone()
        if pending is None or pending[0] != 0:
            raise FixtureVectorError(
                "fixture requires no pre-existing PREPARED shared-anchor intent"
            )
        row = q.execute(
            "SELECT reserved_position FROM shared_anchor_meta WHERE singleton=1"
        ).fetchone()
        if row is None or type(row[0]) is not int or row[0] < 0:
            raise FixtureVectorError("shared-anchor reserved_position is unavailable")
        predecessor = row[0]
        head = q.execute(
            "SELECT g.provider_id,h.generation FROM provider_generation_head h "
            "JOIN provider_generations g ON g.generation_id=h.generation_id "
            "WHERE h.singleton=1"
        ).fetchone()
        if head != (expected_provider_id, expected_generation):
            raise FixtureVectorError(
                "runtime provider does not match durable provider-generation head"
            )
        return expected_provider_id, expected_generation, predecessor
    finally:
        q.close()


def atomic_prepared_plan(path: Path | str, attested: Any, bootstrap: Any):
    """Return exact DDL+materialization+anchor-PREPARED+meta-CAS mutations."""

    if authority.validate_reference_vectors() is not True:
        raise FixtureVectorError("authority reference self-check failed")
    if relation.validate_precursor_relation_reference() is not True:
        raise FixtureVectorError("precursor relation reference self-check failed")
    if storage.validate_reference() is not True:
        raise FixtureVectorError("cutover storage reference self-check failed")
    if (
        authority.PREPARED_REFERENCE_VALUES[7]
        != relation.FROZEN_RELATION_DEFINITION_DIGEST
    ):
        raise FixtureVectorError("PREPARED relation digest differs from frozen DDL")

    provider_id, generation, predecessor = _read_reservation_snapshot(
        path, attested, bootstrap
    )
    position = predecessor + 1
    prepared_digest = authority.PREPARED_DIGEST
    confirmation_nonce = authority.CONFIRMATION_NONCE
    intent_id = storage.anchor_intent_id(prepared_digest)
    payload_digest = storage.anchor_payload_digest(
        prepared_digest, confirmation_nonce
    ).hex()
    request_id = _request_id(
        position,
        intent_id,
        storage.ANCHOR_COMPONENT_ID,
        storage.ANCHOR_INTENT_TYPE,
        payload_digest,
    )
    values = authority.PREPARED_REFERENCE_VALUES

    plan = (
        (relation.PRECURSOR_RELATION_DDL_V1, (), None),
        (storage.CUTOVER_RELATION_SQL, (), None),
        (
            "INSERT INTO provider_activation_reservation_cutovers "
            "VALUES(?,?,?,?,?,?,?,?,?)",
            (
                values[1],
                values[5],
                values[6],
                values[3],
                values[4],
                authority.PREPARED_CANONICAL_BYTES,
                prepared_digest,
                confirmation_nonce,
                intent_id,
            ),
            1,
        ),
        (
            "INSERT INTO shared_anchor_intents("
            "intent_id,component_id,intent_type,payload_digest,provider_id,"
            "provider_generation,predecessor_position,position,request_id,status,"
            "receipt_binding) "
            "SELECT ?,?,?,?,g.provider_id,g.generation,?,?,?,'PREPARED',NULL "
            "FROM provider_generation_head h "
            "JOIN provider_generations g ON g.generation_id=h.generation_id "
            "WHERE h.singleton=1 AND g.provider_id=? AND g.generation=?",
            (
                intent_id,
                storage.ANCHOR_COMPONENT_ID,
                storage.ANCHOR_INTENT_TYPE,
                payload_digest,
                predecessor,
                position,
                request_id,
                provider_id,
                generation,
            ),
            1,
        ),
        (
            "UPDATE shared_anchor_meta SET reserved_position=? "
            "WHERE singleton=1 AND reserved_position=?",
            (position, predecessor),
            1,
        ),
    )
    return plan, prepared_digest


def confirmed_event_plan(path: Path | str, prepared_event_digest: bytes):
    """Return the sole frozen PREPARED->CONFIRMED SQLite mutation.

    The reference bridge is deliberately exact, not a receipt/head generator. The
    supplied digest must be the frozen PREPARED digest and the existing durable row
    must match every authority-relevant field of the independently frozen CONFIRMED
    reference except status/receipt. A stale or substituted row therefore yields
    rowcount 0 and the fixture adapter rolls the transaction back.
    """

    del path  # the plan is pure; SQLite enforces the exact pre-state atomically.
    if type(prepared_event_digest) is not bytes or len(prepared_event_digest) != 32:
        raise FixtureVectorError("prepared_event_digest must be exact 32-byte bytes")
    if prepared_event_digest != authority.PREPARED_DIGEST:
        raise FixtureVectorError(
            "no frozen CONFIRMED bridge exists for the supplied PREPARED digest"
        )
    if confirmed_bridge.validate_reference_bridge() is not True:
        raise FixtureVectorError("CONFIRMED ledger/provenance bridge self-check failed")

    entry = confirmed_bridge.reference_confirmed_entry()
    intent_id = storage.anchor_intent_id(prepared_event_digest)
    if entry["intent_id"] != intent_id:
        raise FixtureVectorError("CONFIRMED bridge intent identity drift")

    sql = (
        "UPDATE shared_anchor_intents SET status='CONFIRMED',receipt_binding=? "
        "WHERE intent_id=? AND component_id=? AND intent_type=? AND payload_digest=? "
        "AND provider_id=? AND provider_generation=? AND predecessor_position=? "
        "AND position=? AND request_id=? AND status='PREPARED' "
        "AND receipt_binding IS NULL "
        "AND EXISTS (SELECT 1 FROM provider_activation_reservation_cutovers c "
        "WHERE c.prepared_digest=? AND c.anchor_intent_id=shared_anchor_intents.intent_id)"
    )
    params = (
        entry["receipt_binding"],
        entry["intent_id"],
        entry["component_id"],
        entry["intent_type"],
        entry["payload_digest"],
        entry["provider_id"],
        entry["provider_generation"],
        entry["predecessor_position"],
        entry["position"],
        entry["request_id"],
        prepared_event_digest,
    )
    return ((sql, params, 1),)


def validate_fixture_vectors() -> bool:
    if (
        hashlib.sha256(authority.PREPARED_CANONICAL_BYTES).digest()
        != authority.PREPARED_DIGEST
    ):
        raise AssertionError("PREPARED canonical digest drift")
    if storage.anchor_payload_digest(
        authority.PREPARED_DIGEST, authority.CONFIRMATION_NONCE
    ) != storage.REFERENCE_ANCHOR_PAYLOAD_DIGEST:
        raise AssertionError("cutover anchor payload digest drift")
    if authority.PREPARED_REFERENCE_VALUES[5] != storage.ANCHOR_COMPONENT_ID:
        raise AssertionError(
            "PREPARED target schema set no longer matches cutover component"
        )
    if (
        authority.PREPARED_REFERENCE_VALUES[7]
        != relation.FROZEN_RELATION_DEFINITION_DIGEST
    ):
        raise AssertionError("PREPARED relation digest drift")
    if confirmed_bridge.validate_reference_bridge() is not True:
        raise AssertionError("CONFIRMED bridge drift")
    return True


if __name__ == "__main__":
    assert validate_fixture_vectors()
