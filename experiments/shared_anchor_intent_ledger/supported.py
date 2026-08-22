from __future__ import annotations

from experiments.shared_anchor_intent_ledger.protocol import (
    IntentSubstitution,
    ProviderMismatch,
    SharedAnchorLedger,
)


class SupportedSharedAnchorLedger(SharedAnchorLedger):
    """Audited LAB-080 surface with restart-time durable-state verification."""

    def __init__(self, path, attested):
        super().__init__(path, attested)
        self.verify_durable()

    def verify_durable(self):
        q = self._con()
        try:
            q.execute("BEGIN")
            meta = q.execute(
                "SELECT reserved_position FROM shared_anchor_meta WHERE singleton=1"
            ).fetchall()
            if len(meta) != 1 or type(meta[0][0]) is not int or meta[0][0] < 0:
                raise IntentSubstitution("invalid reserved_position metadata")
            reserved = meta[0][0]

            rows = q.execute(
                "SELECT intent_id,component_id,intent_type,payload_digest,provider_id,provider_generation,"
                "predecessor_position,position,request_id,status,receipt_binding "
                "FROM shared_anchor_intents ORDER BY position"
            ).fetchall()
            if len(rows) != reserved:
                raise IntentSubstitution("reserved_position does not match ledger tail")

            provider_id, generation = self._provider()
            prepared = 0
            for expected, row in enumerate(rows, 1):
                entry = self._row_entry(row)
                if entry.position != expected or entry.predecessor_position != expected - 1:
                    raise IntentSubstitution("durable ledger is not contiguous")
                if (entry.provider_id, entry.provider_generation) != (provider_id, generation):
                    # LAB-080 deliberately has no historical provider-verification surface.
                    raise ProviderMismatch("historical provider generation cannot be reauthenticated")
                if entry.status == "PREPARED":
                    prepared += 1
                    if entry.position != reserved:
                        raise IntentSubstitution("PREPARED intent is not the ledger tail")
            if prepared > 1:
                raise IntentSubstitution("multiple unresolved durable intents")

            for component_id, position in q.execute(
                "SELECT component_id,position FROM component_anchor_watermarks"
            ).fetchall():
                if not isinstance(component_id, str) or not component_id:
                    raise IntentSubstitution("invalid durable component watermark identity")
                if type(position) is not int or position < 0 or position > reserved:
                    raise IntentSubstitution("invalid durable component watermark")
                if position:
                    row = q.execute(
                        "SELECT status FROM shared_anchor_intents WHERE position=?", (position,)
                    ).fetchone()
                    if row is None or row[0] != "CONFIRMED":
                        raise IntentSubstitution("watermark does not end on confirmed history")
            q.commit()
            return True
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()
