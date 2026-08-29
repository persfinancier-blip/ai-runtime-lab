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
    "asymmetric_provider_receipts": (
        "provider_id",
        "generation",
        "position",
        "kind",
        "challenge",
        "signature",
        "stable_binding",
    ),
}

_REQUIRED_AFFINITY = {
    "shared_anchor_meta": {
        "singleton": "INTEGER",
        "reserved_position": "INTEGER",
    },
    "shared_anchor_intents": {
        "intent_id": "TEXT",
        "component_id": "TEXT",
        "intent_type": "TEXT",
        "payload_digest": "TEXT",
        "provider_id": "TEXT",
        "provider_generation": "INTEGER",
        "predecessor_position": "INTEGER",
        "position": "INTEGER",
        "request_id": "TEXT",
        "status": "TEXT",
        "receipt_binding": "TEXT",
    },
    "component_anchor_watermarks": {
        "component_id": "TEXT",
        "position": "INTEGER",
    },
    "asymmetric_provider_receipts": {
        "request_id": "TEXT",
        "provider_id": "TEXT",
        "generation": "INTEGER",
        "position": "INTEGER",
        "kind": "TEXT",
        "challenge": "TEXT",
        "signature": "TEXT",
        "stable_binding": "TEXT",
    },
}


def _sqlite_affinity(declared_type: str) -> str:
    """Return SQLite column affinity using SQLite's documented type-name rules."""
    value = (declared_type or "").upper()
    if "INT" in value:
        return "INTEGER"
    if any(token in value for token in ("CHAR", "CLOB", "TEXT")):
        return "TEXT"
    if "BLOB" in value or not value:
        return "BLOB"
    if any(token in value for token in ("REAL", "FLOA", "DOUB")):
        return "REAL"
    return "NUMERIC"


def validate_required_not_null_contract(q) -> bool:
    """Require canonical field-domain guarantees CREATE TABLE IF NOT EXISTS cannot repair."""
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

    for table, expected_affinities in _REQUIRED_AFFINITY.items():
        rows = q.execute(f"PRAGMA table_info({table})").fetchall()
        observed = {row[1]: _sqlite_affinity(row[2]) for row in rows}
        missing_columns = [name for name in expected_affinities if name not in observed]
        if missing_columns:
            raise AdoptionSchemaDomainError(
                f"LAB-091 legacy schema is missing required column(s) for {table}: "
                + ", ".join(missing_columns)
            )
        weakened = [
            name
            for name, expected in expected_affinities.items()
            if observed[name] != expected
        ]
        if weakened:
            detail = ", ".join(
                f"{name}={observed[name]} (expected {expected_affinities[name]})"
                for name in weakened
            )
            raise AdoptionSchemaDomainError(
                f"LAB-091 legacy schema has incompatible SQLite affinity for {table}: "
                + detail
            )
    return True
