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


def _unique_key_sets(q, table: str) -> set[tuple[str, ...]]:
    keys: set[tuple[str, ...]] = set()
    table_info = q.execute(f"PRAGMA table_info({table})").fetchall()
    pk_rows = [row for row in sorted(table_info, key=lambda row: row[5]) if row[5] > 0]
    pk_columns = tuple(row[1] for row in pk_rows)
    # INTEGER PRIMARY KEY is the rowid identity itself and has no backing index.
    # Text/composite PKs are accepted only through their backing UNIQUE index below,
    # where we can also prove canonical BINARY comparison semantics.
    if (
        len(pk_rows) == 1
        and pk_rows[0][2].strip().upper() == "INTEGER"
    ):
        keys.add(pk_columns)
    for index_row in q.execute(f"PRAGMA index_list({table})").fetchall():
        # A partial UNIQUE index protects only rows selected by its WHERE clause.
        # It therefore cannot establish a table-wide identity invariant even if
        # its indexed column list is identical to the canonical UNIQUE key.
        if not index_row[2] or index_row[4]:
            continue
        index_name = index_row[1].replace("'", "''")
        index_terms = [
            row
            for row in q.execute(f"PRAGMA index_xinfo('{index_name}')").fetchall()
            if row[5] == 1
        ]
        # Expression terms are reported with name=NULL. Silently dropping them
        # can collapse UNIQUE(id, expression) into a false UNIQUE(id) guarantee.
        if any(row[2] is None for row in index_terms):
            continue
        # Canonical LAB-080/LAB-082 identities use SQLite BINARY comparison.
        # A legacy NOCASE/RTRIM/custom collation can reject otherwise valid,
        # byte-distinct identifiers and is therefore not schema-compatible.
        if any((row[4] or "BINARY").upper() != "BINARY" for row in index_terms):
            continue
        columns = tuple(row[2] for row in index_terms)
        if columns:
            keys.add(columns)
    return keys


def _require_identity_constraints(q) -> None:
    required = {
        "shared_anchor_meta": {("singleton",)},
        "shared_anchor_intents": {
            ("intent_id",),
            ("position",),
            ("request_id",),
        },
        "component_anchor_watermarks": {("component_id",)},
        "asymmetric_provider_receipts": {("request_id",)},
    }
    for table, expected_keys in required.items():
        observed = _unique_key_sets(q, table)
        missing = expected_keys - observed
        if missing:
            rendered = ", ".join("(" + ",".join(key) + ")" for key in sorted(missing))
            raise AdoptionValidationError(
                f"LAB-091 legacy schema is missing canonical identity constraint(s) "
                f"for {table}: {rendered}"
            )


def validate_existing_mutable_state_locked(q) -> bool:
    """Reject pre-LAB-091 rows that could not be created by the supported state machine.

    This runs under the same BEGIN IMMEDIATE transaction that installs the
    persistent LAB-091 guards. The lower LAB-082 durable verifier owns receipt
    signatures/provider-generation binding. This validator closes state-machine
    invariants that persistent triggers cannot enforce retroactively.

    CREATE TABLE IF NOT EXISTS does not repair a weakened preexisting schema.
    Require the canonical PK/UNIQUE identity constraints as well as rechecking
    current row cardinality, so future guarded writes cannot reintroduce
    ambiguous identities after a clean first-adoption snapshot.
    """
    if not q.in_transaction:
        raise AdoptionValidationError(
            "LAB-091 adoption validation requires an active transaction"
        )

    _require_identity_constraints(q)

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
