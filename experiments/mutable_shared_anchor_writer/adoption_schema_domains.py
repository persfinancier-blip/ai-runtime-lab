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

# LAB-091 may adopt an older table layout when its effective write semantics are
# still the same as the canonical schema. Additional UNIQUE constraints are not
# harmless metadata: they can reject a write that the supported state machine is
# entitled to make. In particular, a legacy NOCASE primary key plus a separate
# BINARY UNIQUE index makes identity discovery look canonical while still making
# `Alpha` and `alpha` mutually exclusive on INSERT. Keep only canonical unique
# keys, with byte-exact BINARY comparison for indexed text terms.
_ALLOWED_UNIQUE_KEYS = {
    "shared_anchor_meta": {("singleton",)},
    "shared_anchor_intents": {
        ("intent_id",),
        ("position",),
        ("request_id",),
    },
    "component_anchor_watermarks": {("component_id",)},
    "asymmetric_provider_receipts": {("request_id",)},
}

# Missing canonical CHECK constraints are intentionally tolerated here because
# LAB-091's persisted guards re-impose the protected state-machine predicates.
# Extra legacy CHECK constraints are different: they can reject a write that the
# supported state machine is entitled to make. Keep only the canonical CHECK
# expressions, while permitting a legacy table to omit any of them.
_ALLOWED_CHECK_EXPRESSIONS = {
    "shared_anchor_meta": {
        "SINGLETON=1",
        "RESERVED_POSITION>=0",
    },
    "shared_anchor_intents": {
        "STATUSIN('PREPARED','CONFIRMED')",
    },
    "component_anchor_watermarks": {
        "POSITION>=0",
    },
    "asymmetric_provider_receipts": set(),
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


def _normalize_sql_outside_literals(sql: str) -> str:
    """Normalize SQL syntax while preserving quoted literal/identifier bytes."""
    out = []
    quote = None
    index = 0
    while index < len(sql):
        char = sql[index]
        if quote is None:
            if char in ("'", '"', "`"):
                quote = char
                out.append(char)
            elif char == "[":
                quote = "]"
                out.append(char)
            elif not char.isspace():
                out.append(char.upper())
        else:
            out.append(char)
            if char == quote:
                if (
                    quote in ("'", '"', "`")
                    and index + 1 < len(sql)
                    and sql[index + 1] == quote
                ):
                    out.append(sql[index + 1])
                    index += 1
                else:
                    quote = None
        index += 1
    return "".join(out)


def _extract_check_expressions(create_sql: str) -> list[str]:
    """Return normalized CHECK bodies from one SQLite CREATE TABLE statement."""
    sql = _normalize_sql_outside_literals(create_sql)
    expressions = []
    offset = 0
    marker = "CHECK("
    while True:
        start = sql.find(marker, offset)
        if start < 0:
            return expressions

        body_start = start + len(marker)
        depth = 1
        quote = None
        index = body_start
        while index < len(sql):
            char = sql[index]
            if quote is None:
                if char in ("'", '"', "`"):
                    quote = char
                elif char == "[":
                    quote = "]"
                elif char == "(":
                    depth += 1
                elif char == ")":
                    depth -= 1
                    if depth == 0:
                        expressions.append(sql[body_start:index])
                        offset = index + 1
                        break
            elif char == quote:
                if (
                    quote in ("'", '"', "`")
                    and index + 1 < len(sql)
                    and sql[index + 1] == quote
                ):
                    index += 1
                else:
                    quote = None
            index += 1
        else:
            raise AdoptionSchemaDomainError(
                "LAB-091 legacy schema has malformed CHECK constraint"
            )


def _validate_check_write_contract(q) -> None:
    for table, allowed_checks in _ALLOWED_CHECK_EXPRESSIONS.items():
        row = q.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
            (table,),
        ).fetchone()
        if row is None or row[0] is None:
            raise AdoptionSchemaDomainError(
                f"LAB-091 legacy schema is missing required table: {table}"
            )
        observed_checks = _extract_check_expressions(row[0])
        restrictive = [check for check in observed_checks if check not in allowed_checks]
        if restrictive:
            raise AdoptionSchemaDomainError(
                f"LAB-091 legacy schema has restrictive CHECK constraint(s) for {table}: "
                + ", ".join(restrictive)
            )


def _validate_unique_write_contract(q) -> None:
    for table, allowed_keys in _ALLOWED_UNIQUE_KEYS.items():
        for index_row in q.execute(f"PRAGMA index_list({table})").fetchall():
            if not index_row[2]:
                continue
            index_name = index_row[1].replace("'", "''")
            if index_row[4]:
                raise AdoptionSchemaDomainError(
                    f"LAB-091 legacy schema has restrictive partial UNIQUE index "
                    f"on {table}: {index_row[1]}"
                )
            terms = [
                row
                for row in q.execute(f"PRAGMA index_xinfo('{index_name}')").fetchall()
                if row[5] == 1
            ]
            if not terms or any(row[2] is None for row in terms):
                raise AdoptionSchemaDomainError(
                    f"LAB-091 legacy schema has restrictive expression UNIQUE index "
                    f"on {table}: {index_row[1]}"
                )
            columns = tuple(row[2] for row in terms)
            if columns not in allowed_keys:
                rendered = ",".join(columns)
                raise AdoptionSchemaDomainError(
                    f"LAB-091 legacy schema has extra UNIQUE constraint for {table}: "
                    f"({rendered})"
                )
            nonbinary = [
                row[2]
                for row in terms
                if (row[4] or "BINARY").upper() != "BINARY"
            ]
            if nonbinary:
                raise AdoptionSchemaDomainError(
                    f"LAB-091 legacy schema has non-BINARY UNIQUE identity for {table}: "
                    + ", ".join(nonbinary)
                )


def validate_required_not_null_contract(q) -> bool:
    """Require canonical field/write-domain guarantees CREATE TABLE IF NOT EXISTS cannot repair."""
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

    _validate_unique_write_contract(q)
    _validate_check_write_contract(q)
    return True
