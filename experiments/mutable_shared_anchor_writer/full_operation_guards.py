from __future__ import annotations

from .operation_permit import PermitConnection


def install_full_operation_guards(q: PermitConnection) -> None:
    """Install exact one-shot DML guards inside an existing write transaction."""
    if type(q) is not PermitConnection:
        raise TypeError("exact LAB-091 permit connection required")
    if not q.in_transaction:
        raise RuntimeError("guard installation requires an active transaction")

    names = (
        "lab091_meta_no_insert",
        "lab091_meta_exact_update",
        "lab091_meta_no_delete",
        "lab091_intent_exact_insert",
        "lab091_intent_exact_confirm",
        "lab091_intent_no_delete",
        "lab091_watermark_exact_insert",
        "lab091_watermark_exact_update",
        "lab091_watermark_no_delete",
        "lab091_receipt_exact_insert",
        "lab091_receipt_no_update",
        "lab091_receipt_no_delete",
    )
    for name in names:
        q.execute(f"DROP TRIGGER IF EXISTS {name}")

    statements = (
        """CREATE TRIGGER lab091_meta_no_insert
           BEFORE INSERT ON shared_anchor_meta
           BEGIN SELECT RAISE(ABORT,'LAB-091 meta singleton already initialized'); END""",
        """CREATE TRIGGER lab091_meta_exact_update
           BEFORE UPDATE ON shared_anchor_meta
           WHEN NEW.singleton IS NOT OLD.singleton
             OR NEW.reserved_position!=OLD.reserved_position+1
             OR lab091_consume_permit(
               'meta-update',CAST(OLD.singleton AS TEXT),
               CAST(OLD.reserved_position AS TEXT),CAST(NEW.reserved_position AS TEXT)
             )!=1
           BEGIN SELECT RAISE(ABORT,'LAB-091 exact meta permit required'); END""",
        """CREATE TRIGGER lab091_meta_no_delete
           BEFORE DELETE ON shared_anchor_meta
           BEGIN SELECT RAISE(ABORT,'LAB-091 meta cannot be deleted'); END""",
        """CREATE TRIGGER lab091_intent_exact_insert
           BEFORE INSERT ON shared_anchor_intents
           WHEN NEW.status!='PREPARED'
             OR NEW.receipt_binding IS NOT NULL
             OR NEW.position!=NEW.predecessor_position+1
             OR EXISTS(
               SELECT 1 FROM shared_anchor_intents
               WHERE intent_id=NEW.intent_id OR request_id=NEW.request_id OR position=NEW.position
             )
             OR lab091_consume_permit(
               'intent-insert',NEW.intent_id,'',
               lab091_intent_row_token(
                 NEW.intent_id,NEW.component_id,NEW.intent_type,NEW.payload_digest,
                 NEW.provider_id,NEW.provider_generation,NEW.predecessor_position,
                 NEW.position,NEW.request_id,NEW.status,NEW.receipt_binding
               )
             )!=1
           BEGIN SELECT RAISE(ABORT,'LAB-091 exact intent creation permit required'); END""",
        """CREATE TRIGGER lab091_intent_exact_confirm
           BEFORE UPDATE ON shared_anchor_intents
           WHEN OLD.status!='PREPARED'
             OR NEW.status!='CONFIRMED'
             OR NEW.intent_id IS NOT OLD.intent_id
             OR NEW.component_id IS NOT OLD.component_id
             OR NEW.intent_type IS NOT OLD.intent_type
             OR NEW.payload_digest IS NOT OLD.payload_digest
             OR NEW.provider_id IS NOT OLD.provider_id
             OR NEW.provider_generation IS NOT OLD.provider_generation
             OR NEW.predecessor_position IS NOT OLD.predecessor_position
             OR NEW.position IS NOT OLD.position
             OR NEW.request_id IS NOT OLD.request_id
             OR OLD.receipt_binding IS NOT NULL
             OR NEW.receipt_binding IS NULL
             OR lab091_consume_permit(
               'intent-confirm',OLD.intent_id,
               lab091_intent_row_token(
                 OLD.intent_id,OLD.component_id,OLD.intent_type,OLD.payload_digest,
                 OLD.provider_id,OLD.provider_generation,OLD.predecessor_position,
                 OLD.position,OLD.request_id,OLD.status,OLD.receipt_binding
               ),
               lab091_intent_row_token(
                 NEW.intent_id,NEW.component_id,NEW.intent_type,NEW.payload_digest,
                 NEW.provider_id,NEW.provider_generation,NEW.predecessor_position,
                 NEW.position,NEW.request_id,NEW.status,NEW.receipt_binding
               )
             )!=1
           BEGIN SELECT RAISE(ABORT,'LAB-091 exact intent confirmation permit required'); END""",
        """CREATE TRIGGER lab091_intent_no_delete
           BEFORE DELETE ON shared_anchor_intents
           BEGIN SELECT RAISE(ABORT,'LAB-091 intent history cannot be deleted'); END""",
        """CREATE TRIGGER lab091_watermark_exact_insert
           BEFORE INSERT ON component_anchor_watermarks
           WHEN EXISTS(
               SELECT 1 FROM component_anchor_watermarks WHERE component_id=NEW.component_id
             )
             OR lab091_consume_permit(
               'watermark-insert',NEW.component_id,'',CAST(NEW.position AS TEXT)
             )!=1
           BEGIN SELECT RAISE(ABORT,'LAB-091 exact watermark insert permit required'); END""",
        """CREATE TRIGGER lab091_watermark_exact_update
           BEFORE UPDATE ON component_anchor_watermarks
           WHEN NEW.component_id IS NOT OLD.component_id
             OR NEW.position<OLD.position
             OR lab091_consume_permit(
               'watermark-update',OLD.component_id,
               CAST(OLD.position AS TEXT),CAST(NEW.position AS TEXT)
             )!=1
           BEGIN SELECT RAISE(ABORT,'LAB-091 exact watermark update permit required'); END""",
        """CREATE TRIGGER lab091_watermark_no_delete
           BEFORE DELETE ON component_anchor_watermarks
           BEGIN SELECT RAISE(ABORT,'LAB-091 watermark cannot be deleted'); END""",
        """CREATE TRIGGER lab091_receipt_exact_insert
           BEFORE INSERT ON asymmetric_provider_receipts
           WHEN EXISTS(
               SELECT 1 FROM asymmetric_provider_receipts WHERE request_id=NEW.request_id
             )
             OR lab091_consume_permit(
               'receipt-insert',NEW.request_id,'',
               lab091_receipt_row_token(
                 NEW.request_id,NEW.provider_id,NEW.generation,NEW.position,
                 NEW.kind,NEW.challenge,NEW.signature,NEW.stable_binding
               )
             )!=1
           BEGIN SELECT RAISE(ABORT,'LAB-091 exact receipt creation permit required'); END""",
        """CREATE TRIGGER lab091_receipt_no_update
           BEFORE UPDATE ON asymmetric_provider_receipts
           BEGIN SELECT RAISE(ABORT,'LAB-091 provider receipt is immutable'); END""",
        """CREATE TRIGGER lab091_receipt_no_delete
           BEFORE DELETE ON asymmetric_provider_receipts
           BEGIN SELECT RAISE(ABORT,'LAB-091 provider receipt cannot be deleted'); END""",
    )
    for statement in statements:
        q.execute(statement)
