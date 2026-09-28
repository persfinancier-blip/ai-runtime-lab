from __future__ import annotations


class AdoptionForeignKeyError(RuntimeError):
    pass


_PROTECTED_TABLES = (
    "shared_anchor_meta",
    "shared_anchor_intents",
    "component_anchor_watermarks",
    "asymmetric_provider_receipts",
)


def validate_no_foreign_key_constraints(q) -> bool:
    """Reject legacy foreign keys that can narrow the supported write contract.

    The canonical LAB-080/LAB-082 mutable tables do not declare foreign keys.
    A preexisting REFERENCES clause is therefore not harmless schema metadata:
    when foreign-key enforcement is enabled on the connection it can reject an
    otherwise valid LAB-091 state-machine write because an unrelated legacy
    parent row is absent. Adoption cannot prove arbitrary parent-table lifetime
    or mutation semantics, so accept no inherited foreign keys on protected
    mutable tables.
    """
    if not q.in_transaction:
        raise AdoptionForeignKeyError(
            "LAB-091 foreign-key validation requires an active transaction"
        )

    for table in _PROTECTED_TABLES:
        rows = q.execute(f"PRAGMA foreign_key_list({table})").fetchall()
        if rows:
            raise AdoptionForeignKeyError(
                f"LAB-091 legacy schema has restrictive FOREIGN KEY constraint(s) for {table}"
            )

    return True
