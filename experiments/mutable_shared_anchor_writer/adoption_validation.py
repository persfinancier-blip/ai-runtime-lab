from __future__ import annotations

from experiments.shared_anchor_intent_ledger.protocol import ALLOWED_INTENT_TYPES

from .state_machine_udfs import expected_request_id


class AdoptionValidationError(RuntimeError):
    pass


def _is_canonical_sha256(value) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(ch in "0123456789abcdef" for ch in value)
    )


def validate_existing_mutable_state_locked(q) -> bool:
    """Reject pre-LAB-091 rows that could not be created by the supported state machine.

    This runs under the same BEGIN IMMEDIATE transaction that installs the
    persistent LAB-091 guards. The lower LAB-082 durable verifier owns receipt
    signatures/provider-generation binding. This validator closes state-machine
    invariants that persistent triggers cannot enforce retroactively.
    """
    if not q.in_transaction:
        raise AdoptionValidationError(
            "LAB-091 adoption validation requires an active transaction"
        )

    meta = q.execute(
        "SELECT reserved_position FROM shared_anchor_meta WHERE singleton=1"
    ).fetchone()
    if meta is None or type(meta[0]) is not int or meta[0] < 0:
        raise AdoptionValidationError("LAB-091 shared-anchor meta singleton is invalid")
    reserved_position = meta[0]

    rows = q.execute(
        "SELECT intent_id,component_id,intent_type,payload_digest,"
        "provider_id,provider_generation,"
        "predecessor_position,position,request_id,status,receipt_binding "
        "FROM shared_anchor_intents ORDER BY position"
    ).fetchall()

    if len(rows) != reserved_position:
        raise AdoptionValidationError(
            "LAB-091 reserved tail does not equal contiguous intent history"
        )

    prepared_count = 0
    expected_position = 1
    for (
        intent_id,
        component_id,
        intent_type,
        payload_digest,
        provider_id,
        provider_generation,
        predecessor_position,
        position,
        request_id,
        status,
        receipt_binding,
    ) in rows:
        if not all(
            isinstance(value, str) and value
            for value in (intent_id, component_id, provider_id)
        ):
            raise AdoptionValidationError(
                "LAB-091 existing intent identity/provider is invalid"
            )
        if intent_type not in ALLOWED_INTENT_TYPES:
            raise AdoptionValidationError(
                "LAB-091 existing intent type is unsupported"
            )
        if not _is_canonical_sha256(payload_digest):
            raise AdoptionValidationError(
                "LAB-091 existing intent payload digest is non-canonical"
            )
        if type(provider_generation) is not int or provider_generation < 1:
            raise AdoptionValidationError(
                "LAB-091 existing intent provider generation is invalid"
            )
        if position != expected_position or predecessor_position != position - 1:
            raise AdoptionValidationError(
                "LAB-091 existing intent history is not contiguous"
            )
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
        if status == "PREPARED":
            prepared_count += 1
            if receipt_binding is not None or position != reserved_position:
                raise AdoptionValidationError(
                    "LAB-091 PREPARED intent must be the unresolved tail"
                )
        elif status == "CONFIRMED":
            if receipt_binding is None:
                raise AdoptionValidationError(
                    "LAB-091 CONFIRMED intent is missing receipt binding"
                )
        else:
            raise AdoptionValidationError("LAB-091 existing intent status is invalid")
        expected_position += 1

    if prepared_count > 1:
        raise AdoptionValidationError(
            "LAB-091 existing state has multiple unresolved intents"
        )

    orphan = q.execute(
        "SELECT r.request_id FROM asymmetric_provider_receipts r "
        "WHERE NOT EXISTS("
        "SELECT 1 FROM shared_anchor_intents i WHERE i.request_id=r.request_id"
        ") LIMIT 1"
    ).fetchone()
    if orphan is not None:
        raise AdoptionValidationError(
            "LAB-091 existing provider receipt is not owned by a shared-anchor intent"
        )

    watermarks = q.execute(
        "SELECT component_id,position FROM component_anchor_watermarks"
    ).fetchall()
    for component_id, position in watermarks:
        if not isinstance(component_id, str) or not component_id:
            raise AdoptionValidationError("LAB-091 existing watermark component is invalid")
        if type(position) is not int or position < 0 or position > reserved_position:
            raise AdoptionValidationError("LAB-091 existing watermark position is invalid")
        if position == 0:
            continue
        confirmed = q.execute(
            "SELECT COUNT(*) FROM shared_anchor_intents "
            "WHERE position>=1 AND position<=? "
            "AND status='CONFIRMED' AND receipt_binding IS NOT NULL",
            (position,),
        ).fetchone()[0]
        bad_predecessor = q.execute(
            "SELECT 1 FROM shared_anchor_intents "
            "WHERE position>=1 AND position<=? "
            "AND predecessor_position != position-1 LIMIT 1",
            (position,),
        ).fetchone()
        if confirmed != position or bad_predecessor is not None:
            raise AdoptionValidationError(
                "LAB-091 existing watermark is not backed by complete confirmed history"
            )

    return True
