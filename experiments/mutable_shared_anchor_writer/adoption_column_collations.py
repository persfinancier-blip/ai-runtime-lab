from __future__ import annotations

import sqlite3


class AdoptionColumnCollationError(RuntimeError):
    pass


_CANONICAL_TEXT_COLUMNS = {
    "shared_anchor_intents": (
        "intent_id",
        "component_id",
        "intent_type",
        "payload_digest",
        "provider_id",
        "request_id",
        "status",
        "receipt_binding",
    ),
    "component_anchor_watermarks": ("component_id",),
    "asymmetric_provider_receipts": (
        "request_id",
        "provider_id",
        "kind",
        "challenge",
        "signature",
        "stable_binding",
    ),
}


def validate_resolvable_column_collations(q) -> bool:
    """Require every canonical TEXT column's declared collation to resolve.

    SQLite stores the collation name in CREATE TABLE but does not require that
    collation to be registered when a database is reopened. A later comparison
    that inherits the column collation can then fail while evaluating an
    otherwise-authorized trigger or query. Prepare a zero-row self-comparison
    for every canonical TEXT field: this resolves the declared collation without
    mutating data or relying on rows being present.
    """
    if not q.in_transaction:
        raise AdoptionColumnCollationError(
            "LAB-091 column-collation validation requires an active transaction"
        )

    for table, columns in _CANONICAL_TEXT_COLUMNS.items():
        for column in columns:
            try:
                q.execute(
                    f'SELECT "{column}"="{column}" FROM "{table}" LIMIT 0'
                ).fetchall()
            except sqlite3.OperationalError as exc:
                if "collation sequence" not in str(exc).lower():
                    raise
                raise AdoptionColumnCollationError(
                    f"LAB-091 legacy schema has unavailable collation for "
                    f"{table}.{column}: {exc}"
                ) from exc
    return True
