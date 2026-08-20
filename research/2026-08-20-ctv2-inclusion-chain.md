# LAB-044 — CT v2 authenticated inclusion proof and exact leaf binding

Date: 2026-08-20  
Issue: #84  
Branch: `lab/044-ctv2-inclusion-chain`

## Question

How can a client prove that one exact CT v2 log-entry `TransItem` is included under a cryptographically authenticated `signed_tree_head_v2`, without trusting a caller-supplied leaf hash or an unbound inclusion proof?

## Primary source

RFC 9162 is the authoritative source.

Transferable mechanisms:

- §2.1.3 defines compact Merkle inclusion proofs and fail-closed verification using `leaf_index`, `tree_size`, path nodes, and the advertised root.
- §4.5 assigns `inclusion_proof_v2` type `0x0106` inside `TransItem`.
- §4.7 defines CT v2 leaves as `HASH(0x00 || exact TransItem bytes)` where the leaf `TransItem` is `x509_entry_v2` or `precert_entry_v2`.
- §4.12 binds an inclusion proof to `LogID`, `tree_size`, `leaf_index`, and `inclusion_path`.
- §5.4 explicitly notes that the inclusion proof need not be signed because it is verified against the selected signed STH.

Source: https://www.rfc-editor.org/rfc/rfc9162.html

## Implemented chain

`verify_authenticated_inclusion()` performs:

1. authenticate the STH through LAB-043 and its immutable `LogProfile`;
2. strict-decode `TransItem<inclusion_proof_v2>`;
3. require exact proof `LogID == profile.log_id`;
4. require exact proof `tree_size == authenticated STH tree_size`;
5. compute SHA-256 leaf identity from the exact presented leaf `TransItem` bytes;
6. reject leaf types other than `x509_entry_v2` / `precert_entry_v2`;
7. run the RFC 9162 inclusion algorithm against the authenticated STH root.

The strict wire boundary rejects wrong type, malformed DER LogID value, zero tree size, out-of-range leaf index, wrong node length, vector overrun, truncation, and trailing bytes.

## Unsafe seed

The unsafe verifier accepts a caller-supplied leaf hash. A valid proof for `real-artifact` can therefore be accepted while the caller presents `attacker-artifact`, because the verifier never recomputes the hash from the presented exact leaf bytes.

Observed expected failure:

`AssertionError: True is not false : unsafe verifier accepted proof while caller presented different leaf bytes`

## Corrected validation

Observed locally:

- corrected deterministic suite: 16/16 passed;
- exhaustive small-tree check: every leaf index for tree sizes 1..32 passed;
- unsafe hash-only seed: expected failure;
- `python -m compileall -q experiments/ctv2_inclusion_chain`: passed.

The local environment emitted an unrelated spreadsheet-runtime warmup warning during Python startup; unittest and compileall exit codes were still observed directly and were 0 for corrected validation.

## Security boundary

A Merkle proof authenticates membership of a **hash**, not the human-level artifact a caller claims that hash represents. The verifier must derive the leaf hash itself from the exact serialized leaf bytes crossing the verification boundary.

Likewise, the unsigned inclusion proof gains authority only through exact binding to a cryptographically authenticated STH for the same log and tree size.

## Non-goals / remaining gap

This experiment does not verify that an SCT corresponds to the exact leaf that later appears in the tree, nor does it evaluate Maximum Merge Delay. That promise-to-inclusion relationship is a separate next-layer problem.
