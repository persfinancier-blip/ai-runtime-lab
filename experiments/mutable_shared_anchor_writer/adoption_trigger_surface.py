from __future__ import annotations


class AdoptionTriggerSurfaceError(RuntimeError):
    pass


_EXPECTED_TRIGGERS_BY_TABLE = {
    "shared_anchor_meta": {
        "lab091_v2_meta_no_insert",
        "lab091_v2_meta_exact_update",
        "lab091_v2_meta_no_delete",
        "lab091_v3_meta_requires_matching_prepared_intent",
    },
    "shared_anchor_intents": {
        "lab091_v2_intent_exact_insert",
        "lab091_v2_intent_exact_confirm",
        "lab091_v2_intent_no_delete",
        "lab091_v3_intent_requires_current_tail_and_provider",
        "lab091_v4_intent_requires_deterministic_request_id",
        "lab091_v4_confirmation_requires_matching_receipt",
    },
    "component_anchor_watermarks": {
        "lab091_v2_watermark_exact_insert",
        "lab091_v2_watermark_exact_update",
        "lab091_v2_watermark_no_delete",
        "lab091_v4_watermark_insert_requires_confirmed_prefix",
        "lab091_v4_watermark_update_requires_confirmed_prefix",
    },
    "asymmetric_provider_receipts": {
        "lab091_v2_receipt_exact_insert",
        "lab091_v2_receipt_no_update",
        "lab091_v2_receipt_no_delete",
        "lab091_v3_receipt_requires_matching_prepared_intent",
    },
}


def validate_protected_trigger_surface(q) -> bool:
    """Reject persisted trigger code outside the exact LAB-091 protected surface.

    A trigger attached to a protected table executes inside the same SQLite
    statement as an otherwise authorized LAB-091 write.  An unknown durable
    trigger could therefore act as a confused deputy and mutate a different
    table without possessing a LAB-091 one-shot permit.  The final constructor
    installs/replaces every supported LAB-091 trigger immediately before this
    check, so the durable trigger surface must match the exact known set.
    """
    if not q.in_transaction:
        raise AdoptionTriggerSurfaceError(
            "LAB-091 trigger-surface validation requires an active transaction"
        )

    protected_tables = tuple(_EXPECTED_TRIGGERS_BY_TABLE)
    placeholders = ",".join("?" for _ in protected_tables)
    rows = q.execute(
        "SELECT name,tbl_name FROM sqlite_master "
        f"WHERE type='trigger' AND tbl_name IN ({placeholders})",
        protected_tables,
    ).fetchall()

    observed = {table: set() for table in protected_tables}
    for name, table in rows:
        observed[table].add(name)

    for table, expected in _EXPECTED_TRIGGERS_BY_TABLE.items():
        actual = observed[table]
        missing = expected - actual
        unexpected = actual - expected
        if missing or unexpected:
            details = []
            if missing:
                details.append("missing=" + ",".join(sorted(missing)))
            if unexpected:
                details.append("unexpected=" + ",".join(sorted(unexpected)))
            raise AdoptionTriggerSurfaceError(
                f"LAB-091 protected trigger surface mismatch for {table}: "
                + "; ".join(details)
            )

    return True
