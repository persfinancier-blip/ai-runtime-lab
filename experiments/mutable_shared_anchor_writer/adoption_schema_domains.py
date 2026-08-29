from __future__ import annotations


class AdoptionSchemaDomainError(RuntimeError):
    pass


_REQUIRED_NOT_NULL = {
    "shared_anchor_meta": ("reserved_position",),
    "shared_anchor_intents": (
        "component_id",
        "intent_type",
        "payload_digest",
        "provider_id",
        "provider_generation",
        "predecessor_position",
        "position",
        "request_id",
        "status",
    ),
    "component_anchor_watermarks": ("position",),
}


def validate_required_not_null_contract(q) -> bool:
    """Require canonical NOT NULL guarantees that CREATE TABLE IF NOT EXISTS cannot repair."""
    if not q.in_transaction:
        raise AdoptionSchemaDomainError(
            "LAB-091 schema-domain validation requires an active transaction"
        )

    for table, required_columns in _REQUIRED_NOT_NULL.items():
        rows = q.execute(f"PRAGMA table_info({table})").fetchall()
        observed = {row[1]: bool(row[3]) for row in rows}
        missing_columns = [name for name in required_columns if name not in observed]
        if missing_columns:
            raise AdoptionSchemaDomainError(
                f"LAB-091 legacy schema is missing required column(s) for {table}: "
                + ", ".join(missing_columns)
            )
        weakened = [name for name in required_columns if not observed[name]]
        if weakened:
            raise AdoptionSchemaDomainError(
                f"LAB-091 legacy schema is missing canonical NOT NULL constraint(s) "
                f"for {table}: " + ", ".join(weakened)
            )
    return True
