from __future__ import annotations

from .operation_permit import PermitConnection


HISTORY_TRIGGER_NAMES = (
    "lab091_v4_intent_requires_deterministic_request_id",
    "lab091_v4_watermark_insert_requires_confirmed_prefix",
    "lab091_v4_watermark_update_requires_confirmed_prefix",
    "lab091_v4_confirmation_requires_matching_receipt",
)


def install_history_binding_guards(q: PermitConnection) -> None:
    """Bind new intents and watermark advances to deterministic/confirmed history."""
    if type(q) is not PermitConnection:
        raise TypeError("exact LAB-091 permit connection required")
    if not q.in_transaction:
        raise RuntimeError("history guard installation requires an active transaction")

    for name in HISTORY_TRIGGER_NAMES:
        q.execute(f"DROP TRIGGER IF EXISTS {name}")

    q.execute(
        """CREATE TRIGGER lab091_v4_intent_requires_deterministic_request_id
           BEFORE INSERT ON shared_anchor_intents
           WHEN NEW.request_id != lab091_expected_request_id(
             NEW.position,
             NEW.intent_id,
             NEW.component_id,
             NEW.intent_type,
             NEW.payload_digest
           )
           BEGIN
             SELECT RAISE(ABORT,'LAB-091 deterministic request_id mismatch');
           END"""
    )
    q.execute(
        """CREATE TRIGGER lab091_v4_watermark_insert_requires_confirmed_prefix
           BEFORE INSERT ON component_anchor_watermarks
           WHEN NEW.position>0 AND (
             (SELECT COUNT(*) FROM shared_anchor_intents i
              WHERE i.position>=1 AND i.position<=NEW.position
                AND i.status='CONFIRMED' AND i.receipt_binding IS NOT NULL) != NEW.position
             OR EXISTS(
               SELECT 1 FROM shared_anchor_intents i
               WHERE i.position>=1 AND i.position<=NEW.position
                 AND i.predecessor_position != i.position-1
             )
           )
           BEGIN
             SELECT RAISE(ABORT,'LAB-091 watermark insert lacks complete confirmed history');
           END"""
    )
    q.execute(
        """CREATE TRIGGER lab091_v4_watermark_update_requires_confirmed_prefix
           BEFORE UPDATE ON component_anchor_watermarks
           WHEN NEW.component_id != OLD.component_id
             OR NEW.position<OLD.position
             OR (
               NEW.position>OLD.position AND (
                 (SELECT COUNT(*) FROM shared_anchor_intents i
                  WHERE i.position>OLD.position AND i.position<=NEW.position
                    AND i.status='CONFIRMED' AND i.receipt_binding IS NOT NULL)
                   != NEW.position-OLD.position
                 OR EXISTS(
                   SELECT 1 FROM shared_anchor_intents i
                   WHERE i.position>OLD.position AND i.position<=NEW.position
                     AND i.predecessor_position != i.position-1
                 )
               )
             )
           BEGIN
             SELECT RAISE(ABORT,'LAB-091 watermark update lacks complete confirmed history');
           END"""
    )
    q.execute(
        """CREATE TRIGGER lab091_v4_confirmation_requires_matching_receipt
           BEFORE UPDATE ON shared_anchor_intents
           WHEN NEW.status COLLATE BINARY = 'CONFIRMED' COLLATE BINARY AND (
             NEW.receipt_binding IS NULL
             OR NOT EXISTS(
               SELECT 1 FROM asymmetric_provider_receipts r
               WHERE r.request_id COLLATE BINARY = NEW.request_id COLLATE BINARY
                 AND r.provider_id COLLATE BINARY = NEW.provider_id COLLATE BINARY
                 AND r.generation=NEW.provider_generation
                 AND r.position=NEW.position
                 AND r.kind COLLATE BINARY = 'RECONCILE' COLLATE BINARY
                 AND r.stable_binding COLLATE BINARY = NEW.receipt_binding COLLATE BINARY
             )
           )
           BEGIN
             SELECT RAISE(ABORT,'LAB-091 confirmation lacks matching provider receipt');
           END"""
    )
