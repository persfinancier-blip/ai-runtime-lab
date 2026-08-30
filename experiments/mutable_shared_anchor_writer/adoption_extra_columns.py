from __future__ import annotations


class AdoptionExtraColumnError(RuntimeError):
    pass


_CANONICAL_COLUMNS = {
    "shared_anchor_meta": {"singleton", "reserved_position"},
    "shared_anchor_intents": {
        "intent_id",
        "component_id",
        "intent_type",
        "payload_digest",
        "provider_id",
        "provider_generation",
        "predecessor_position",
        "position",
        "request_id",
        "status",
        "receipt_binding",
    },
    "component_anchor_watermarks": {"component_id", "position"},
    "asymmetric_provider_receipts": {
        "request_id",
        "provider_id",
        "generation",
        "position",
        "kind",
        "challenge",
        "signature",
        "stable_binding",
    },
}


def validate_no_required_extra_columns(q) -> bool:
    """Reject legacy columns that make a canonical supported INSERT impossible.

    LAB-091 can safely ignore some additive legacy metadata, but an ordinary
    extra column declared NOT NULL without a DEFAULT requires every INSERT to
    provide a value. The supported writer intentionally emits only the
    canonical column set, so accepting such a table would make adoption succeed
    while later supported DML fails.

    Generated/hidden columns are not caller-supplied values and are outside this
    narrow reproduced defect; they are therefore not rejected here without a
    separate reachable counterexample.
    """
    if not q.in_transaction:
        raise AdoptionExtraColumnError(
            "LAB-091 extra-column validation requires an active transaction"
        )

    for table, canonical in _CANONICAL_COLUMNS.items():
        rows = q.execute(f"PRAGMA table_xinfo({table})").fetchall()
        if not rows:
            raise AdoptionExtraColumnError(
                f"LAB-091 legacy schema is missing required table: {table}"
            )

        restrictive = []
        for row in rows:
            name = row[1]
            not_null = bool(row[3])
            default = row[4]
            hidden = row[6] if len(row) > 6 else 0
            if (
                name not in canonical
                and hidden == 0
                and not_null
                and default is None
            ):
                restrictive.append(name)

        if restrictive:
            raise AdoptionExtraColumnError(
                f"LAB-091 legacy schema has required extra column(s) for {table}: "
                + ", ".join(restrictive)
            )

    return True
