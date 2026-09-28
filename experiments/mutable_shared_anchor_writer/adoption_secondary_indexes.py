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
    """Reject inherited non-UNIQUE indexes with unsafe maintenance semantics.

    Secondary indexes participate in every matching INSERT/UPDATE even though
    they do not establish identity. A legacy index can therefore make an
    otherwise-valid supported write fail after restart when LAB-091 does not
    register a legacy-only collation or deterministic UDF used by that index.

    Canonical identity/UNIQUE indexes are validated separately by the schema
    domain gate. Ordinary BINARY, column-only, non-partial secondary indexes
    remain compatible. Expression and partial indexes are rejected fail-closed
    because their maintenance may depend on legacy-only SQL functions or other
    expression semantics not owned by the supported LAB-091 connection.
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
            if any(row[2] is None for row in terms):
                raise AdoptionSecondaryIndexError(
                    f"LAB-091 legacy secondary index uses an expression on "
                    f"{table}: {index_row[1]}"
                )
            # PRAGMA index_list columns are seq, name, unique, origin, partial.
            if len(index_row) > 4 and index_row[4]:
                raise AdoptionSecondaryIndexError(
                    f"LAB-091 legacy secondary index is partial on "
                    f"{table}: {index_row[1]}"
                )
            nonbinary = [
                row[2]
                for row in terms
                if (row[4] or "BINARY").upper() != "BINARY"
            ]
            if nonbinary:
                raise AdoptionSecondaryIndexError(
                    f"LAB-091 legacy secondary index requires non-BINARY collation "
                    f"on {table}: {index_row[1]} ({', '.join(nonbinary)})"
                )

    return True
