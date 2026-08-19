# Current Lab State

Last updated: 2026-08-20

## Active objective

Advance from compact Merkle consistency semantics to strict CT v2 proof-envelope interoperability. LAB-041 is complete: RFC 9162 compact consistency proof generation/verification now replaces explicit leaf-history semantics at the witness boundary, with authoritative RFC example comparison and fail-closed malformed-proof handling.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-041.
- Completed Issue #78 / LAB-041.
- Merged PR #79 / LAB-041 as `16d3857b36e8109fd13b70b63b4f3633af3226da`.
- Active next: Issue #80 / LAB-042 — READY.
- Active branch: none yet.
- Active PR: none.

## Last completed step

LAB-041 built and audited `experiments/rfc9162_consistency/`. It implements RFC 9162 §2.1.1 Merkle Tree Hash, recursive compact consistency-proof generation and the §2.1.4 verifier that reconstructs and binds both old and new roots. Equal-size handling requires identical roots and an empty proof; empty-old-tree consistency proof is explicitly rejected, matching the current `transparency-dev/merkle` reference behavior.

The unsafe seed verified only the current/new root and therefore accepted a valid proof paired with an unrelated claimed old checkpoint. The corrected verifier rejects this by requiring reconstruction of both advertised heads.

## Evidence produced

- `experiments/rfc9162_consistency/protocol.py`
- `experiments/rfc9162_consistency/tests/test_protocol.py`
- `experiments/rfc9162_consistency/tests/unsafe_new_root_only_expected_failure.py`
- `experiments/rfc9162_consistency/README.md`
- `research/2026-08-20-rfc9162-compact-consistency.md`
- Corrected exact-source suite: 13/13 deterministic tests passed.
- Exhaustive bounded sweep: all 2,016 `(old_size,new_size)` pairs through tree size 64 passed.
- Literal RFC 9162 §2.1.5 reference examples reproduced exactly: 3→7 `[c,d,g,l]`, 4→7 `[l]`, 6→7 `[i,j,k]`.
- Unsafe baseline: expected failure because an unrelated old checkpoint was accepted by the new-root-only verifier.
- `python -m compileall -q experiments` passed.
- Published protocol blob SHA `536e430ff2e8c5e3c0b2e5c1f3e072d6d98cba08` and corrected test blob SHA `a11c25655e86557da12cafe26676d9e85d2c5cf9` matched locally executed source.
- Audit fix: Python boolean/coercible tree sizes are rejected consistently at verifier, generator and checkpoint boundaries.
- Primary donors: RFC 9162 and `transparency-dev/merkle` reference verifier at commit `4abf9fec7365d41d742236b36a22e122f84dcb83`.
- PR #79 remote patch audited and squash-merged as `16d3857b36e8109fd13b70b63b4f3633af3226da`.

## Known blockers / constraints

- Local shell DNS to GitHub remains unavailable/unreliable; GitHub connector plus local execution is the supported path.
- LAB-041 implements compact Merkle semantics but not full CT v2 `TransItem` / `ConsistencyProofDataV2` wire encoding.
- SHA-256 is fixed in the reference prototype; production hasher/profile binding remains external.
- CT log/checkpoint signatures, witness quorum and split-view observation remain in LAB-040 rather than being duplicated here.
- Empty-tree bootstrap is a caller trust-policy concern, not an RFC compact consistency proof.
- Full CT client/server/network behavior remains outside scope.

## Exact next action

Start Issue #80 / LAB-042. Research exact RFC 9162 TLS-style encoding for `TransItem<consistency_proof_v2>` and `ConsistencyProofDataV2`. Build `experiments/ctv2_consistency_wire/` with strict encode/decode, malformed/trailing/length-bound rejection, exact `log_id/tree_size_1/tree_size_2` binding to LAB-040 checkpoints, and an adapter that invokes LAB-041 compact proof verification without leaf material. Cross-check at least one encoded fixture against a primary/reference implementation or authoritative structure/vector and retain an unsafe parser/binding expected-failure seed.

## Backlog

- #80 / LAB-042 — CT v2 consistency-proof wire binding and strict decoder conformance — READY.
- Independent witness/gossip transport reliability and Byzantine consensus remain intentionally out of scope unless later product requirements justify them.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
