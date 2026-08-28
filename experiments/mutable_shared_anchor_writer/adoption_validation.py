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

    Do not rely on legacy table constraints being intact during first adoption:
    CREATE TABLE IF NOT EXISTS does not prove the preexisting schema still has
    the LAB-080 primary/unique constraints. Recheck identity cardinality here so
    a weakened legacy schema cannot import ambiguous canonical identities.
    """
    if not q.in_transaction:
        raise AdoptionValidationError(
            "LAB-091 adoption validation requires an active transaction"
        )

    meta_rows = q.execute(
        "SELECT singleton,reserved_position FROM shared_anchor_meta"
    ).fetchall()
    if (
        len(meta_rows) != 1
        or meta_rows[0][0] != 1
        or type(meta_rows[0][1]) is not int
        or meta_rows[0][1] < 0
    ):
        raise AdoptionValidationError("LAB-091 shared-anchor meta singleton is invalid")
    reserved_position = meta_rows[0][1]

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
    seen_intent_ids = set()
    seen_request_ids = set()
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
        if intent_id in seen_intent_ids:
            raise AdoptionValidationError(
                "LAB-091 existing intent identity is duplicated"
            )
        seen_intent_ids.add(intent_id)
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
        if request_id in seen_request_ids:
            raise AdoptionValidationError(
                "LAB-091 existing request identity is duplicated"
            )
        seen_request_ids.add(request_id)
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

    duplicate_receipt = q.execute(
        "SELECT request_id FROM asymmetric_provider_receipts "
        "GROUP BY request_id HAVING COUNT(*)!=1 LIMIT 1"
    ).fetchone()
    if duplicate_receipt is not None:
        raise AdoptionValidationError(
            "LAB-091 existing provider receipt identity is duplicated"
        )

    watermarks = q.execute(
        "SELECT component_id,position FROM component_anchor_watermarks"
    ).fetchall()
    seen_components = set()
    for component_id, position in watermarks:
        if not isinstance(component_id, str) or not component_id:
            raise AdoptionValidationError("LAB-091 existing watermark component is invalid")
        if component_id in seen_components:
            raise AdoptionValidationError(
                "LAB-091 existing watermark component is duplicated"
            )
        seen_components.add(component_id)
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
