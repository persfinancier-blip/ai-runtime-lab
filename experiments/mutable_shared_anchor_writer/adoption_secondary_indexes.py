from __future__ import annotations


class AdoptionSecondaryIndexError(RuntimeError):
    pass


_PROTECTED_TABLES = (
    "shared_anchor_meta",
    "shared_anchor_intents",
    "component_anchor_watermarks",
    "asymmetric_provider_receipts",
)


def validate_secondary_index_collations(q) -> bool:
    """Reject inherited non-UNIQUE indexes that require non-BINARY collations.

    Secondary indexes participate in every matching INSERT/UPDATE even though
    they do not establish identity. A legacy index that names a custom collation
    can therefore make an otherwise-valid supported write fail after restart
    when that legacy-only collation is not registered on the LAB-091 connection.

    Canonical identity/UNIQUE indexes are validated separately by the schema
    domain gate. Ordinary BINARY secondary indexes remain compatible.
    """
    if not q.in_transaction:
        raise AdoptionSecondaryIndexError(
            "LAB-091 secondary-index validation requires an active transaction"
        )

    for table in _PROTECTED_TABLES:
        for index_row in q.execute(f"PRAGMA index_list({table})").fetchall():
            # UNIQUE/PK indexes are already covered by adoption_schema_domains.
            if index_row[2]:
                continue
            index_name = index_row[1].replace("'", "''")
            terms = [
                row
                for row in q.execute(f"PRAGMA index_xinfo('{index_name}')").fetchall()
                if row[5] == 1
            ]
            nonbinary = [
                row[2] if row[2] is not None else "<expression>"
                for row in terms
                if (row[4] or "BINARY").upper() != "BINARY"
            ]
            if nonbinary:
                raise AdoptionSecondaryIndexError(
                    f"LAB-091 legacy secondary index requires non-BINARY collation "
                    f"on {table}: {index_row[1]} ({', '.join(nonbinary)})"
                )

    return True
