from __future__ import annotations

from experiments.asymmetric_provider_history.integration import IntegratedAsymmetricProviderHistory
from experiments.asymmetric_provider_history.protocol import HistoricalVerificationError, SignedReceipt


class BinaryIdentityIntegratedAsymmetricProviderHistory(IntegratedAsymmetricProviderHistory):
    """LAB-091 receipt helpers with byte-exact request identity semantics.

    Legacy SQLite schemas may declare request_id with a non-BINARY default
    collation while retaining a separate canonical BINARY UNIQUE index.  Every
    supported lookup/store predicate therefore states BINARY explicitly rather
    than inheriting the legacy column collation.
    """

    def _load_receipt_locked(self, q, request_id):
        row = q.execute(
            "SELECT provider_id,generation,position,request_id,kind,challenge,signature,stable_binding "
            "FROM asymmetric_provider_receipts "
            "WHERE request_id COLLATE BINARY = ? COLLATE BINARY",
            (request_id,),
        ).fetchone()
        if row is None:
            raise HistoricalVerificationError("missing asymmetric historical receipt")
        receipt = self._verify_receipt_locked(q, SignedReceipt(*row[:7]))
        if row[7] != receipt.stable_binding:
            raise HistoricalVerificationError("asymmetric historical receipt binding mismatch")
        return receipt

    def _maybe_load_receipt_locked(self, q, request_id):
        row = q.execute(
            "SELECT provider_id,generation,position,request_id,kind,challenge,signature,stable_binding "
            "FROM asymmetric_provider_receipts "
            "WHERE request_id COLLATE BINARY = ? COLLATE BINARY",
            (request_id,),
        ).fetchone()
        if row is None:
            return None
        receipt = self._verify_receipt_locked(q, SignedReceipt(*row[:7]))
        if row[7] != receipt.stable_binding:
            raise HistoricalVerificationError("asymmetric historical receipt binding mismatch")
        return receipt

    def _store_receipt_locked(self, q, receipt: SignedReceipt):
        self._verify_receipt_locked(q, receipt)
        expected = (
            receipt.provider_id,
            receipt.generation,
            receipt.position,
            receipt.kind,
            receipt.challenge,
            receipt.signature,
            receipt.stable_binding,
        )
        existing = q.execute(
            "SELECT provider_id,generation,position,kind,challenge,signature,stable_binding "
            "FROM asymmetric_provider_receipts "
            "WHERE request_id COLLATE BINARY = ? COLLATE BINARY",
            (receipt.request_id,),
        ).fetchone()
        if existing is not None and existing != expected:
            raise HistoricalVerificationError("asymmetric receipt substitution")
        if existing is None:
            q.execute(
                "INSERT INTO asymmetric_provider_receipts VALUES(?,?,?,?,?,?,?,?)",
                (
                    receipt.request_id,
                    receipt.provider_id,
                    receipt.generation,
                    receipt.position,
                    receipt.kind,
                    receipt.challenge,
                    receipt.signature,
                    receipt.stable_binding,
                ),
            )
        return receipt.stable_binding
