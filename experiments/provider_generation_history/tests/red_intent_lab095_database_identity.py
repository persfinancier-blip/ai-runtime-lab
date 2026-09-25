"""RED-intent contract for LAB-095 database/history identity.

Expected pre-fix behavior:
- production database_identity module is absent;
- DurableProviderHistory / SharedAnchorLedger retain mutable public path state.

Expected post-fix behavior:
- logical identity is created only by an externally CONFIRMED identity intent;
- identity digest is path-independent and commits the exact confirmed row/receipt;
- parent-chain links are deterministic and domain-separated;
- constructed supported history/ledger objects cannot be rebound to another path.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from experiments.provider_generation_history.protocol import (
    DurableProviderHistory,
    GenerationDescriptor,
)
from experiments.provider_generation_history.tests import lab095_database_identity_reference as ref
from experiments.provider_generation_history.database_identity import (
    confirmed_identity_digest,
    genesis_parent_chain_link,
    transition_parent_chain_link,
)


class LAB095DatabaseIdentityRedIntent(unittest.TestCase):
    def test_confirmed_identity_matches_frozen_canonical_reference(self):
        args = {
            "payload_digest": "11" * 32,
            "provider_id": "provider-alpha",
            "provider_generation": 8,
            "position": 42,
            "request_id": "shared-anchor:42:" + "22" * 32,
            "receipt_binding": "33" * 32,
        }
        self.assertEqual(confirmed_identity_digest(**args), ref.confirmed_identity_digest(**args))

    def test_identity_is_not_path_derived(self):
        args = {
            "payload_digest": "44" * 32,
            "provider_id": "provider-alpha",
            "provider_generation": 2,
            "position": 7,
            "request_id": "shared-anchor:7:" + "55" * 32,
            "receipt_binding": "66" * 32,
        }
        expected = ref.confirmed_identity_digest(**args)
        with tempfile.TemporaryDirectory() as td:
            a = str(Path(td) / "a.sqlite")
            b = str(Path(td) / "renamed.sqlite")
            # Paths are intentionally not inputs to identity derivation.
            self.assertNotEqual(a, b)
            self.assertEqual(confirmed_identity_digest(**args), expected)

    def test_parent_chain_links_match_reference(self):
        dbid = "77" * 32
        bootstrap = "88" * 32
        parent = genesis_parent_chain_link(
            logical_database_identity_digest=dbid,
            bootstrap_generation_id=bootstrap,
        )
        self.assertEqual(
            parent,
            ref.genesis_parent_chain_link(
                logical_database_identity_digest=dbid,
                bootstrap_generation_id=bootstrap,
            ),
        )
        args = {
            "logical_database_identity_digest": dbid,
            "parent_chain_link_digest": parent,
            "provider_id": "provider-alpha",
            "old_generation_id": "99" * 32,
            "new_generation_id": "aa" * 32,
            "old_mac": "bb" * 32,
            "new_mac": "cc" * 32,
        }
        self.assertEqual(
            transition_parent_chain_link(**args),
            ref.transition_parent_chain_link(**args),
        )

    def test_history_path_cannot_be_rebound_after_construction(self):
        with tempfile.TemporaryDirectory() as td:
            a = Path(td) / "a.sqlite"
            b = Path(td) / "b.sqlite"
            bootstrap = GenerationDescriptor("provider-alpha", 1, ("01" * 32))
            history = DurableProviderHistory(a, bootstrap)
            DurableProviderHistory(b, bootstrap)
            with self.assertRaises((AttributeError, TypeError)):
                history.path = str(b)
            self.assertEqual(history.current().generation_id, bootstrap.generation_id)


if __name__ == "__main__":
    unittest.main()
