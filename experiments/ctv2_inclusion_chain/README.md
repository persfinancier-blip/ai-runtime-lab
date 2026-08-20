# CT v2 Authenticated Inclusion Chain

LAB-044 reference implementation for RFC 9162 inclusion proofs.

The corrected boundary is:

`exact leaf TransItem bytes -> HASH(0x00 || TransItem) -> strict inclusion_proof_v2 -> authenticated LAB-043 STH root -> RFC 9162 inclusion verification`

The inclusion proof itself is not trusted or signed. Its authority comes from exact binding to the same LogID and tree size as a cryptographically authenticated signed tree head.

Run:

```bash
python -m unittest discover -s experiments/ctv2_inclusion_chain/tests -p 'test_*.py' -v
python -m compileall -q experiments/ctv2_inclusion_chain
```

The deliberately unsafe seed is outside normal discovery:

```bash
python -m unittest experiments.ctv2_inclusion_chain.tests.unsafe_hash_only_expected_failure -v
```

It is expected to fail because a hash-only verifier accepts a valid proof while the caller presents different leaf/artifact bytes.

Non-goals: certificate-policy validation, SCT issuance policy, HTTP/base64 transport, log scraping, and witness consensus.
