from __future__ import annotations

from .operation_permit import PermitConnection


CROSS_TABLE_TRIGGER_NAMES = (
    "lab091_v3_meta_requires_matching_prepared_intent",
    "lab091_v3_intent_requires_current_tail_and_provider",
    "lab091_v3_receipt_requires_matching_prepared_intent",
)


def install_cross_table_guards(q: PermitConnection) -> None:
    """Bind one-shot row permits to the authoritative LAB-080/LAB-082 state machine."""
    if type(q) is not PermitConnection:
        raise TypeError("exact LAB-091 permit connection required")
    if not q.in_transaction:
        raise RuntimeError("cross-table guard installation requires an active transaction")

    for name in CROSS_TABLE_TRIGGER_NAMES:
        q.execute(f"DROP TRIGGER IF EXISTS {name}")

    q.execute(
        """CREATE TRIGGER lab091_v3_meta_requires_matching_prepared_intent
           BEFORE UPDATE ON shared_anchor_meta
           WHEN NEW.reserved_position != OLD.reserved_position + 1
           OR NOT EXISTS(
             SELECT 1 FROM shared_anchor_intents i
             WHERE i.position=NEW.reserved_position
               AND i.predecessor_position=OLD.reserved_position
               AND i.status='PREPARED'
               AND i.receipt_binding IS NULL
           )
           BEGIN
             SELECT RAISE(ABORT,'LAB-091 meta advance lacks exact next PREPARED intent');
           END"""
    )
    q.execute(
        """CREATE TRIGGER lab091_v3_intent_requires_current_tail_and_provider
           BEFORE INSERT ON shared_anchor_intents
           WHEN NEW.position != NEW.predecessor_position + 1
           OR EXISTS(
             SELECT 1 FROM shared_anchor_intents i
             WHERE i.status='PREPARED'
           )
           OR NOT EXISTS(
             SELECT 1 FROM shared_anchor_meta m
             WHERE m.singleton=1 AND m.reserved_position=NEW.predecessor_position
           )
           OR NOT EXISTS(
             SELECT 1
             FROM asymmetric_provider_head h
             JOIN asymmetric_provider_generations g
               ON g.generation_id=h.generation_id
             WHERE h.singleton=1
               AND h.generation=g.generation
               AND g.provider_id=NEW.provider_id
               AND g.generation=NEW.provider_generation
           )
           BEGIN
             SELECT RAISE(ABORT,'LAB-091 intent is not exact next tail/current provider or another intent is unresolved');
           END"""
    )
    q.execute(
        """CREATE TRIGGER lab091_v3_receipt_requires_matching_prepared_intent
           BEFORE INSERT ON asymmetric_provider_receipts
           WHEN NEW.kind!='RECONCILE'
           OR NOT EXISTS(
             SELECT 1 FROM shared_anchor_intents i
             WHERE i.request_id=NEW.request_id
               AND i.provider_id=NEW.provider_id
               AND i.provider_generation=NEW.generation
               AND i.position=NEW.position
               AND i.status='PREPARED'
               AND i.receipt_binding IS NULL
           )
           BEGIN
             SELECT RAISE(ABORT,'LAB-091 receipt lacks matching PREPARED intent');
           END"""
    )
