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
    """Reject legacy columns that can make canonical supported DML fail.

    LAB-091 can safely ignore ordinary additive metadata when callers may omit
    it. An ordinary extra column declared NOT NULL without a DEFAULT requires
    every INSERT to provide a value. A generated extra column is also unsafe to
    adopt: even though callers do not supply it, its legacy expression is
    evaluated on canonical writes and can raise or otherwise reject values that
    are valid under the LAB-091 contract.

    SQLite ``PRAGMA table_xinfo`` marks generated columns with hidden=2 (VIRTUAL)
    or hidden=3 (STORED). Those generated extras are rejected fail-closed after
    a reproduced supported-write failure; ordinary nullable/defaulted extras
    remain accepted.
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
        generated = []
        for row in rows:
            name = row[1]
            not_null = bool(row[3])
            default = row[4]
            hidden = row[6] if len(row) > 6 else 0
            if name in canonical:
                continue
            if hidden in (2, 3):
                generated.append(name)
            elif hidden == 0 and not_null and default is None:
                restrictive.append(name)

        if generated:
            raise AdoptionExtraColumnError(
                f"LAB-091 legacy schema has generated extra column(s) for {table}: "
                + ", ".join(generated)
            )
        if restrictive:
            raise AdoptionExtraColumnError(
                f"LAB-091 legacy schema has required extra column(s) for {table}: "
                + ", ".join(restrictive)
            )

    return True
