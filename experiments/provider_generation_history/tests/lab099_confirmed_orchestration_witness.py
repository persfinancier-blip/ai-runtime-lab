"""Test-only end-to-end orchestration for the frozen LAB-099 CONFIRMED witness.

This helper composes already-frozen, separately-audited fixture mechanisms only:
legitimate shared-anchor prefix 1..41 -> frozen PREPARED at 42 -> existing provider
increment/RECONCILE -> frozen CONFIRMED mutation -> persisted CONFIRMED verification.

It MUST NOT derive or replace LAB-099 authority. Any divergence from the independently
frozen request, receipt, position, or confirmed-head identity fails closed.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path

from experiments.provider_generation_history.protocol import HistoricalReceipt
from experiments.provider_generation_history.tests import (
    lab099_confirmed_fixture_row_verifier as confirmed_rows,
)
from experiments.provider_generation_history.tests import (
    lab099_confirmed_ledger_reference as confirmed,
)
from experiments.provider_generation_history.tests import (
    lab099_cutover_storage_reference as storage,
)
from experiments.provider_generation_history.tests import (
    lab099_precursor_fixture_adapter as adapter,
)
from experiments.provider_generation_history.tests import (
    lab099_shared_anchor_prefix_witness as prefix,
)

INCREMENT_CHALLENGE = "lab099-orchestration-increment"
RECONCILE_CHALLENGE = "lab099-orchestration-reconcile"


class ConfirmedOrchestrationError(RuntimeError):
    pass


def _canon(obj: object) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _stable_receipt(provider_id: str, generation: int, position: int, request_id: str) -> str:
    return hashlib.sha256(
        _canon(
            {
                "provider_id": provider_id,
                "generation": generation,
                "position": position,
                "request_id": request_id,
            }
        )
    ).hexdigest()


def _read_prepared_identity(path: Path | str, intent_id: str) -> tuple[int, int, str, str]:
    q = sqlite3.connect(str(path), timeout=5, isolation_level=None)
    q.execute("PRAGMA busy_timeout=5000")
    try:
        row = q.execute(
            "SELECT predecessor_position,position,request_id,status "
            "FROM shared_anchor_intents WHERE intent_id=?",
            (intent_id,),
        ).fetchone()
    finally:
        q.close()
    if row is None or len(row) != 4:
        raise ConfirmedOrchestrationError("frozen PREPARED row is unavailable")
    predecessor, position, request_id, status = row
    if (
        predecessor != confirmed.REFERENCE_PREDECESSOR_POSITION
        or position != confirmed.REFERENCE_POSITION
        or request_id != confirmed.REFERENCE_REQUEST_ID
        or status != "PREPARED"
    ):
        raise ConfirmedOrchestrationError("frozen PREPARED authority identity drift")
    return predecessor, position, request_id, status


def execute_frozen_confirmed_orchestration(path: Path | str) -> dict[str, object]:
    """Execute the exact frozen witness without creating any replacement authority."""

    witness = prefix.build_legitimate_prefix(path)
    if witness.ledger.verify_durable() is not True:
        raise ConfirmedOrchestrationError("legitimate prefix failed durable verification")

    prepared = adapter.install_atomic_prepared_cutover(
        path,
        witness.attested,
        witness.bootstrap,
    )
    intent_id = storage.anchor_intent_id(prepared.prepared_event_digest)
    predecessor, position, request_id, _ = _read_prepared_identity(path, intent_id)

    frozen_entry = confirmed.reference_confirmed_entry()
    if intent_id != frozen_entry["intent_id"]:
        raise ConfirmedOrchestrationError("frozen anchor intent id drift")

    provider = witness.attested.provider
    verifier = witness.attested.verifier
    increment = provider.increment(
        expected=predecessor,
        challenge=INCREMENT_CHALLENGE,
        request_id=request_id,
    )
    verified_increment = verifier.verify(
        increment,
        expected_challenge=INCREMENT_CHALLENGE,
        allowed_kinds={"INCREMENT"},
    )
    if (
        verified_increment.position != position
        or verified_increment.request_id != request_id
    ):
        raise ConfirmedOrchestrationError("provider increment does not match frozen request")

    reconciled = provider.reconcile_increment(
        challenge=RECONCILE_CHALLENGE,
        request_id=request_id,
    )
    if reconciled is None:
        raise ConfirmedOrchestrationError("provider did not retain frozen request result")
    verified = verifier.verify(
        reconciled,
        expected_challenge=RECONCILE_CHALLENGE,
        allowed_kinds={"RECONCILE"},
    )
    receipt = HistoricalReceipt(
        verified.provider_id,
        verified.generation,
        verified.position,
        verified.request_id,
        verified.kind,
        verified.challenge,
        verified.mac,
    )
    stable_receipt = _stable_receipt(
        verified.provider_id,
        verified.generation,
        verified.position,
        verified.request_id,
    )
    if receipt.stable_binding != stable_receipt:
        raise ConfirmedOrchestrationError("provider receipt binding implementation drift")
    if stable_receipt != confirmed.REFERENCE_RECEIPT_BINDING:
        raise ConfirmedOrchestrationError("provider result does not reproduce frozen receipt")
    stored_binding = witness.ledger.provider_history.store_receipt(receipt)
    if stored_binding != confirmed.REFERENCE_RECEIPT_BINDING:
        raise ConfirmedOrchestrationError("durable provider-history receipt binding drift")

    adapter.install_confirmed_event(
        path,
        prepared_event_digest=prepared.prepared_event_digest,
    )
    if confirmed_rows.verify_installed_confirmed_cutover(
        path,
        witness.attested,
        prepared_event_digest=prepared.prepared_event_digest,
        expected_confirmed_position=confirmed.REFERENCE_POSITION,
        expected_confirmed_head_digest=confirmed.REFERENCE_CONFIRMED_HEAD_DIGEST,
    ) is not True:
        raise ConfirmedOrchestrationError("persisted CONFIRMED verification failed")

    head = storage.confirmed_head_digest(frozen_entry)
    if head != confirmed.REFERENCE_CONFIRMED_HEAD_DIGEST:
        raise ConfirmedOrchestrationError("frozen confirmed head drift")
    if witness.ledger.verify_durable() is not True:
        raise ConfirmedOrchestrationError("final historical ledger verification failed")

    return {
        "intent_id": intent_id,
        "request_id": request_id,
        "receipt_binding": stable_receipt,
        "confirmed_position": position,
        "confirmed_head_digest": head.hex(),
    }


def validate_orchestration_contract_shape() -> bool:
    if prefix.PREFIX_LAST_POSITION != confirmed.REFERENCE_PREDECESSOR_POSITION:
        raise AssertionError("prefix/frozen predecessor drift")
    if confirmed.REFERENCE_POSITION != confirmed.REFERENCE_PREDECESSOR_POSITION + 1:
        raise AssertionError("frozen CONFIRMED position is not contiguous")
    if len(confirmed.REFERENCE_RECEIPT_BINDING) != 64:
        raise AssertionError("frozen receipt identity is malformed")
    if len(confirmed.REFERENCE_CONFIRMED_HEAD_DIGEST) != 32:
        raise AssertionError("frozen confirmed head identity is malformed")
    return True


if __name__ == "__main__":
    assert validate_orchestration_contract_shape()
