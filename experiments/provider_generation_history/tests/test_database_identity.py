from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from experiments.provider_generation_history import database_identity as dbid
from experiments.provider_generation_history.tests import lab095_database_identity_reference as ref


class LAB095DatabaseIdentityProductionTests(unittest.TestCase):
    def _create_anchor_table(self, q):
        q.execute(
            """CREATE TABLE shared_anchor_intents(
              intent_id TEXT PRIMARY KEY,
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
            )"""
        )

    def _install(self, path, *, intent_status="PREPARED", finalize=False):
        q = sqlite3.connect(path, isolation_level=None)
        self._create_anchor_table(q)
        dbid.install_custody_schema(q)
        nonce = "01" * 32
        bootstrap = "02" * 32
        payload_digest = dbid.identity_payload_digest(
            nonce_hex=nonce, bootstrap_generation_id=bootstrap
        )
        request_id = "shared-anchor:1:" + ("03" * 32)
        receipt = "04" * 32 if intent_status == "CONFIRMED" else None
        q.execute(
            "INSERT INTO shared_anchor_intents VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            (
                dbid.IDENTITY_INTENT_ID,
                dbid.IDENTITY_COMPONENT,
                "migration",
                payload_digest,
                "provider-alpha",
                1,
                0,
                1,
                request_id,
                intent_status,
                receipt,
            ),
        )
        custody = [
            1,
            "PREPARED",
            nonce,
            bootstrap,
            payload_digest,
            request_id,
            None,
            None,
            None,
            None,
            None,
        ]
        if finalize:
            custody = [
                1,
                "CONFIRMED",
                nonce,
                bootstrap,
                payload_digest,
                request_id,
                "provider-alpha",
                1,
                1,
                receipt,
                dbid.confirmed_identity_digest(
                    payload_digest=payload_digest,
                    provider_id="provider-alpha",
                    provider_generation=1,
                    position=1,
                    request_id=request_id,
                    receipt_binding=receipt,
                ),
            ]
        q.execute(
            "INSERT INTO provider_history_database_identity VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            custody,
        )
        q.close()

    def test_derivations_match_frozen_reference(self):
        args = dict(
            payload_digest="11" * 32,
            provider_id="provider-alpha",
            provider_generation=8,
            position=42,
            request_id="shared-anchor:42:" + ("22" * 32),
            receipt_binding="33" * 32,
        )
        self.assertEqual(
            dbid.confirmed_identity_digest(**args),
            ref.confirmed_identity_digest(**args),
        )
        db_identity = "77" * 32
        bootstrap = "88" * 32
        parent = dbid.genesis_parent_chain_link(
            logical_database_identity_digest=db_identity,
            bootstrap_generation_id=bootstrap,
        )
        self.assertEqual(
            parent,
            ref.genesis_parent_chain_link(
                logical_database_identity_digest=db_identity,
                bootstrap_generation_id=bootstrap,
            ),
        )

    def test_classifier_state_progression_and_tamper(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            absent = root / "absent.sqlite"
            self.assertEqual(
                dbid.classify_identity_custody(absent),
                dbid.IdentityCustodyState.ABSENT,
            )

            prepared = root / "prepared.sqlite"
            self._install(prepared)
            self.assertEqual(
                dbid.classify_identity_custody(prepared),
                dbid.IdentityCustodyState.PREPARED,
            )

            confirmed = root / "confirmed.sqlite"
            self._install(confirmed, intent_status="CONFIRMED")
            self.assertEqual(
                dbid.classify_identity_custody(confirmed),
                dbid.IdentityCustodyState.CONFIRMED_NEEDS_FINALIZE,
            )

            complete = root / "complete.sqlite"
            self._install(complete, intent_status="CONFIRMED", finalize=True)
            self.assertEqual(
                dbid.classify_identity_custody(complete),
                dbid.IdentityCustodyState.COMPLETE,
            )
            q = sqlite3.connect(complete)
            q.execute(
                "UPDATE provider_history_database_identity "
                "SET logical_database_identity_digest=?",
                ("ff" * 32,),
            )
            q.commit()
            q.close()
            self.assertEqual(
                dbid.classify_identity_custody(complete),
                dbid.IdentityCustodyState.CORRUPT,
            )

    def test_orphan_custody_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "orphan.sqlite"
            q = sqlite3.connect(path, isolation_level=None)
            dbid.install_custody_schema(q)
            q.execute(
                "INSERT INTO provider_history_database_identity VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (
                    1,
                    "PREPARED",
                    "01" * 32,
                    "02" * 32,
                    dbid.identity_payload_digest(
                        nonce_hex="01" * 32,
                        bootstrap_generation_id="02" * 32,
                    ),
                    "shared-anchor:1:" + ("03" * 32),
                    None,
                    None,
                    None,
                    None,
                    None,
                ),
            )
            q.close()
            self.assertEqual(
                dbid.classify_identity_custody(path),
                dbid.IdentityCustodyState.CORRUPT,
            )


if __name__ == "__main__":
    unittest.main()
