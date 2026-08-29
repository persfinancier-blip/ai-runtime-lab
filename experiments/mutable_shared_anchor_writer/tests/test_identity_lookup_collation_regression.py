from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path

import pytest

from experiments.asymmetric_provider_history.protocol import SignedReceipt
from experiments.mutable_shared_anchor_writer.binary_identity_provider_history import (
    BinaryIdentityIntegratedAsymmetricProviderHistory,
)
from experiments.mutable_shared_anchor_writer.history_bound_operation_scoped import (
    SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger,
)
from experiments.shared_anchor_intent_ledger.protocol import IntentSubstitution


class _ReceiptProbe(BinaryIdentityIntegratedAsymmetricProviderHistory):
    def _verify_receipt_locked(self, q, receipt):
        return receipt


def _ledger_without_constructor(path):
    ledger = object.__new__(SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger)
    ledger.path = str(path)
    return ledger


def test_final_entry_and_watermark_reads_do_not_inherit_legacy_nocase():
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "identity.db"
        q = sqlite3.connect(path)
        try:
            q.executescript(
                """
                CREATE TABLE shared_anchor_intents(
                  intent_id TEXT COLLATE NOCASE NOT NULL,
                  component_id TEXT NOT NULL,
                  intent_type TEXT NOT NULL,
                  payload_digest TEXT NOT NULL,
                  provider_id TEXT NOT NULL,
                  provider_generation INTEGER NOT NULL,
                  predecessor_position INTEGER NOT NULL,
                  position INTEGER NOT NULL,
                  request_id TEXT NOT NULL,
                  status TEXT NOT NULL,
                  receipt_binding TEXT
                );
                CREATE UNIQUE INDEX intent_id_binary
                  ON shared_anchor_intents(intent_id COLLATE BINARY);
                CREATE TABLE component_anchor_watermarks(
                  component_id TEXT COLLATE NOCASE NOT NULL,
                  position INTEGER NOT NULL
                );
                CREATE UNIQUE INDEX component_id_binary
                  ON component_anchor_watermarks(component_id COLLATE BINARY);
                """
            )
            payload_digest = "0" * 64
            request_id = SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger._request_id(
                1, "Alpha", "Component", "migration", payload_digest
            )
            q.execute(
                "INSERT INTO shared_anchor_intents VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (
                    "Alpha",
                    "Component",
                    "migration",
                    payload_digest,
                    "provider",
                    1,
                    0,
                    1,
                    request_id,
                    "PREPARED",
                    None,
                ),
            )
            q.execute("INSERT INTO component_anchor_watermarks VALUES('Comp',1)")
            q.commit()
        finally:
            q.close()

        ledger = _ledger_without_constructor(path)
        assert ledger.entry("Alpha").intent_id == "Alpha"
        with pytest.raises(IntentSubstitution, match="missing ledger entry"):
            ledger.entry("alpha")
        assert ledger.watermark("Comp") == 1
        assert ledger.watermark("comp") == 0


def test_binary_receipt_helper_does_not_alias_case_distinct_request_id():
    q = sqlite3.connect(":memory:")
    try:
        q.executescript(
            """
            CREATE TABLE asymmetric_provider_receipts(
              request_id TEXT COLLATE NOCASE NOT NULL,
              provider_id TEXT NOT NULL,
              generation INTEGER NOT NULL,
              position INTEGER NOT NULL,
              kind TEXT NOT NULL,
              challenge TEXT NOT NULL,
              signature TEXT NOT NULL,
              stable_binding TEXT NOT NULL
            );
            CREATE UNIQUE INDEX receipt_request_id_binary
              ON asymmetric_provider_receipts(request_id COLLATE BINARY);
            INSERT INTO asymmetric_provider_receipts VALUES(
              'ReqA','provider',1,1,'RECONCILE','challenge','signature','binding'
            );
            """
        )
        history = object.__new__(_ReceiptProbe)
        assert history._maybe_load_receipt_locked(q, "reqa") is None
        receipt = history._maybe_load_receipt_locked(q, "ReqA")
        assert isinstance(receipt, SignedReceipt)
        assert receipt.request_id == "ReqA"
    finally:
        q.close()
