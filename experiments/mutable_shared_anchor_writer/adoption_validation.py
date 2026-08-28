from __future__ import annotations

from .state_machine_udfs import expected_request_id


class AdoptionValidationError(RuntimeError):
    pass


def validate_existing_mutable_state_locked(q) -> bool:
    """Reject pre-LAB-091 rows that could not be created by the supported state machine.

    This runs under the same BEGIN IMMEDIATE transaction that installs the
    persistent LAB-091 guards.  The lower LAB-082 durable verifier already owns
    history continuity, signatures, provider generation binding and confirmed
    receipt binding.  This adoption check closes only the invariants introduced
    by LAB-091 that triggers cannot retroactively enforce on existing rows.
    """
    if not q.in_transaction:
        raise AdoptionValidationError("LAB-091 adoption validation requires an active transaction")

    rows = q.execute(
        "SELECT intent_id,component_id,intent_type,payload_digest,position,request_id "
        "FROM shared_anchor_intents ORDER BY position"
    ).fetchall()
    for intent_id, component_id, intent_type, payload_digest, position, request_id in rows:
        expected = expected_request_id(
            position,
            intent_id,
            component_id,
            intent_type,
            payload_digest,
        )
        if request_id != expected:
            raise AdoptionValidationError(
                "LAB-091 existing intent has non-deterministic request_id"
            )

    orphan = q.execute(
        "SELECT r.request_id FROM asymmetric_provider_receipts r "
        "WHERE NOT EXISTS(SELECT 1 FROM shared_anchor_intents i WHERE i.request_id=r.request_id) "
        "LIMIT 1"
    ).fetchone()
    if orphan is not None:
        raise AdoptionValidationError(
            "LAB-091 existing provider receipt is not owned by a shared-anchor intent"
        )
    return True
