# RFC 9162 compact consistency proofs — interoperability experiment

Date: 2026-08-20  
Issue: #78 / LAB-041  
Branch: `lab/041-rfc9162-consistency`

## Question

Can LAB-040 witnesses replace explicit prior/appended leaf material with the compact consistency proof semantics used by real Certificate Transparency-style logs, while failing closed on malformed or non-canonical evidence?

## Primary algorithm

RFC 9162 §2.1.1 defines the Merkle Tree Hash:

- empty tree: `SHA-256("")`;
- leaf: `SHA-256(0x00 || data)`;
- internal node: `SHA-256(0x01 || left || right)`;
- non-power-of-two trees split at the largest power of two smaller than the tree size.

RFC 9162 §2.1.4 defines the unique minimal consistency proof recursively as `PROOF(m, D_n) = SUBPROOF(m, D_n, true)` for `0 < m < n`, and specifies a verifier that reconstructs both the old and new roots from the compact node path. The proof is bounded by `ceil(log2(n)) + 1` nodes.

Primary source: https://www.rfc-editor.org/rfc/rfc9162.html#section-2.1.4

RFC 9162 §4.11 carries these nodes as `consistency_path` together with `log_id`, `tree_size_1`, and `tree_size_2` in `ConsistencyProofDataV2`.

Primary source: https://www.rfc-editor.org/rfc/rfc9162.html#section-4.11

## Independent/reference implementation

`transparency-dev/merkle` is a production-grade reference library used in the transparency ecosystem. At commit `4abf9fec7365d41d742236b36a22e122f84dcb83`, `proof/verify.go` exposes `VerifyConsistency` / `RootFromConsistencyProof` and uses strict boundary behavior:

- `size2 < size1` is rejected;
- `size1 == 0` is rejected as a meaningless consistency proof;
- equal sizes require an empty proof;
- non-equal sizes require a non-empty proof;
- proof length is checked rather than allowing unused nodes.

Reference source: https://github.com/transparency-dev/merkle/blob/4abf9fec7365d41d742236b36a22e122f84dcb83/proof/verify.go

The same repository currently fuzzes consistency proofs against a reference implementation and contains accumulated Merkle subtree vector tests, which is useful evidence that malformed/edge behavior is treated as an interoperability surface rather than just a happy-path algorithm.

Reference repository: https://github.com/transparency-dev/merkle

## Reference comparison executed

The deterministic test suite reproduces the literal RFC 9162 §2.1.5 seven-leaf example. Using the RFC node labels:

- `PROOF(3, D[7]) == [c, d, g, l]`;
- `PROOF(4, D[7]) == [l]`;
- `PROOF(6, D[7]) == [i, j, k]`.

The implementation generated exactly these node sequences from raw leaves. This is an authoritative example-vector comparison independent of the lab's own expected roots.

In addition, every `(old_size, new_size)` pair for tree sizes `2..64` was generated and verified: **2,016 compact proofs**. This is exhaustive over the bounded size range, not a random sample.

## Boundary decisions

### Empty tree

RFC compact consistency proof generation is defined for `0 < m < n`; `transparency-dev/merkle` explicitly rejects `size1 == 0` as meaningless. LAB-041 therefore rejects an empty-old-tree consistency proof rather than inventing a synthetic proof. A caller may separately treat the empty tree as a trust bootstrap rule, but that is outside the compact proof verifier.

### Equal size

Although RFC §2.1.4.2 describes `0 < first < second`, the witness integration needs deterministic equal-size handling. LAB-041 accepts equal sizes only when:

- proof is empty; and
- roots are byte-identical.

A different root at the same size is a split-view condition at the LAB-040 layer.

### Malformed proof material

LAB-041 rejects:

- hash nodes not exactly 32 bytes for SHA-256;
- missing nodes;
- extra nodes;
- tampered nodes;
- old size greater than new size;
- booleans/coercible values masquerading as integer tree sizes;
- proof paths exceeding the RFC logarithmic node bound.

## Unsafe seeded design

A deliberately unsafe verifier reconstructs only the new root and ignores whether the same path reconstructs the claimed old root. For a non-power-of-two old tree, the compact proof contains its own seed, so a valid proof can be paired with an unrelated claimed old checkpoint.

Observed expected failure:

```text
AssertionError: True is not false : unsafe verifier ignored reconstructed old root
FAILED (failures=1)
```

This demonstrates why consistency verification must bind **both** advertised heads, not merely show that proof nodes can produce the current root.

## Corrected exact local evidence

Commands executed from the generated source tree:

```bash
PYTHONPATH=. python -m unittest discover -s experiments/rfc9162_consistency/tests -p 'test_*.py' -v
python -m compileall -q experiments
```

Observed result: **13/13 deterministic tests passed**, including the 2,016-pair exhaustive bounded sweep. `compileall` passed.

The deliberately unsafe test was run separately and failed as expected.

## LAB-040 integration

LAB-040's current `ConsistencyProof` stores `prior_leaves_hex` plus `appended_leaves_hex`, so verification scales with leaf history and is deliberately not wire-compatible.

LAB-041's `verify_checkpoint_growth(old, new, proof)` requires only:

- old checkpoint `size` and root;
- new checkpoint `size` and root;
- compact proof nodes.

Therefore a productionized LAB-040 witness can replace leaf-material proof verification with compact node-path verification after binding the proof's `log_id/tree_size_1/tree_size_2` envelope to the exact signed checkpoints.

## Wire-format / cryptographic differences that remain

The prototype implements the **Merkle consistency semantics**, not the complete CT v2 wire ecosystem:

- it uses raw Python `bytes` proof nodes rather than TLS-encoded `TransItem<consistency_proof_v2>`;
- it does not implement CT v2 `LogID` serialization;
- checkpoint/log signatures remain outside this module and are already modeled in LAB-040;
- SHA-256 is fixed for the experiment; production code should bind the hasher to the log profile;
- there is no network CT client/server.

These are deliberate non-goals under Issue #78's stop condition.

## Decision

Adopt RFC 9162 compact consistency proof semantics as the witness consistency primitive. Keep checkpoint signature/witness quorum and split-view observation in LAB-040, but replace explicit leaf-history consistency evidence with a compact path bound to both old and new checkpoint heads.
