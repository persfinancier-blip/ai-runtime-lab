# CT v2 signed-tree-head authentication chain

Reference LAB-043 implementation for RFC 9162 `signed_tree_head_v2`.

Security boundary:

1. decode the complete `TransItem<signed_tree_head_v2>` with no trailing data;
2. decode `TreeHeadDataV2` with exact HASH_SIZE and canonical extension ordering;
3. bind the artifact `LogID` to immutable log profile data;
4. verify the profile-declared signature over **exactly the encoded `tree_head` field**;
5. only then convert the authenticated STHs to LAB-042 checkpoints;
6. bind the consistency-proof envelope to the same LogID and exact size pair;
7. run LAB-041 compact Merkle consistency verification.

The executable reference profile uses RFC 9162's `ed25519 (0x0807)` with `cryptography`. Algorithm/key/profile distribution is intentionally external to STH verification.

Run:

```bash
python -m unittest discover -s experiments/ctv2_sth_chain/tests -p 'test_*.py' -v
python -m unittest experiments.ctv2_sth_chain.tests.unsafe_parsed_expected_failure -v
python -m compileall -q experiments/ctv2_sth_chain
```

The unsafe seed is expected to fail because it trusts parsed fields after deliberately corrupting the signature.
