from __future__ import annotations

from experiments.mutable_shared_anchor_writer.operation_permit import PermitConnection


def install_operation_scoped_guards(q: PermitConnection) -> None:
    """Install one-shot LAB-091 DML guards inside an existing transaction."""
    if type(q) is not PermitConnection:
        raise TypeError("exact LAB-091 permit connection required")
    if not q.in_transaction:
        raise RuntimeError("guard installation requires an active transaction")

    statements = (
        """CREATE TRIGGER lab091_meta_no_insert
           BEFORE INSERT ON shared_anchor_meta
           BEGIN SELECT RAISE(ABORT,'LAB-091 meta singleton already initialized'); END""",
        """CREATE TRIGGER lab091_meta_permit_update
           BEFORE UPDATE ON shared_anchor_meta
           WHEN lab091_consume_permit(
             'meta-update',
             CAST(OLD.singleton AS TEXT),
             CAST(OLD.reserved_position AS TEXT),
             CAST(NEW.reserved_position AS TEXT)
           )!=1
           BEGIN SELECT RAISE(ABORT,'LAB-091 exact meta permit required'); END""",
        """CREATE TRIGGER lab091_meta_no_delete
           BEFORE DELETE ON shared_anchor_meta
           BEGIN SELECT RAISE(ABORT,'LAB-091 meta cannot be deleted'); END""",
        """CREATE TRIGGER lab091_watermark_permit_insert
           BEFORE INSERT ON component_anchor_watermarks
           WHEN lab091_consume_permit(
             'watermark-insert',
             NEW.component_id,
             '',
             CAST(NEW.position AS TEXT)
           )!=1
           BEGIN SELECT RAISE(ABORT,'LAB-091 exact watermark insert permit required'); END""",
        """CREATE TRIGGER lab091_watermark_permit_update
           BEFORE UPDATE ON component_anchor_watermarks
           WHEN NEW.component_id IS NOT OLD.component_id
             OR NEW.position<OLD.position
             OR lab091_consume_permit(
               'watermark-update',
               OLD.component_id,
               CAST(OLD.position AS TEXT),
               CAST(NEW.position AS TEXT)
             )!=1
           BEGIN SELECT RAISE(ABORT,'LAB-091 exact watermark update permit required'); END""",
        """CREATE TRIGGER lab091_watermark_no_delete
           BEFORE DELETE ON component_anchor_watermarks
           BEGIN SELECT RAISE(ABORT,'LAB-091 watermark cannot be deleted'); END""",
    )
    for statement in statements:
        q.execute(statement)
