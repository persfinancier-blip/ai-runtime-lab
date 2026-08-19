# RFC 9162 compact consistency proof reference

This standard-library prototype implements RFC 9162 §2.1.1 and §2.1.4 Merkle Tree Hash, compact consistency-proof generation, and fail-closed verification.

The verifier consumes only `(old_size, old_root, new_size, new_root, proof_nodes)`. It does **not** require old or new leaf material, which is the integration property needed by LAB-040 witnesses.

Boundary semantics:
- `0 < old_size < new_size`: RFC compact proof is required;
- `old_size == new_size`: accepted only with an empty proof and identical roots;
- `old_size == 0`: deliberately rejected as a meaningless consistency proof, matching `transparency-dev/merkle` reference behavior;
- each SHA-256 proof node must be exactly 32 bytes;
- missing, extra, tampered, or wrong-order nodes fail closed.

Run:

```bash
python -m unittest discover -s experiments/rfc9162_consistency/tests -p 'test_*.py' -v
```

The deliberately unsafe old-root-ignoring verifier is outside passing discovery:

```bash
python -m unittest experiments.rfc9162_consistency.tests.unsafe_new_root_only_expected_failure -v
```
