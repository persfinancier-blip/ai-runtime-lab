# Current Lab State

Last updated: 2026-08-20

## Active objective

Advance from strict CT v2 consistency-proof wire interoperability to authenticated CT v2 signed tree heads. LAB-042 is complete: the compact LAB-041 proof is now carried in a strict RFC 9162 `TransItem<consistency_proof_v2>` envelope and bound to the exact log ID and old/new checkpoint sizes before Merkle verification.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-042.
- Completed Issue #80 / LAB-042.
- Merged PR #81 / LAB-042 as `1554c94469b368132170bc34ce6dfa337d3f6cbc`.
- Active next: Issue #82 / LAB-043 — READY.
- Active branch: none yet.
- Active PR: none.

## Last completed step

LAB-042 built and audited `experiments/ctv2_consistency_wire/`. It implements strict TLS-presentation-language encoding/decoding for RFC 9162 `consistency_proof_v2`: two-byte TransItem type, DER-OID-value `LogID<2..127>`, two network-order uint64 tree sizes, a uint16-length consistency vector, and HASH_SIZE-bound NodeHash elements. Truncation, trailing bytes, wrong type, malformed vector boundaries, noncanonical/unterminated OID subidentifiers, wrong hash lengths and uint64/type errors fail closed.

The binding adapter checks exact LogID and both tree sizes against old/new witnessed checkpoints before delegating to LAB-041 compact consistency verification. Audit added canonical OID validation and an end-to-end 3→7 compact-proof adapter test rather than relying only on a spy verifier.

## Evidence produced

- `experiments/ctv2_consistency_wire/protocol.py`
- `experiments/ctv2_consistency_wire/tests/test_protocol.py`
- `experiments/ctv2_consistency_wire/tests/unsafe_prefix_expected_failure.py`
- `experiments/ctv2_consistency_wire/README.md`
- `research/2026-08-20-ctv2-consistency-wire.md`
- Corrected local suite after audit: 14/14 deterministic tests passed.
- Independent literal fixture constructed with `struct.pack` matched encoder output.
- End-to-end adapter test generated a LAB-041 3→7 compact proof, serialized it, decoded/bound it and verified both roots.
- Unsafe prefix parser: expected failure because attacker-controlled trailing bytes were accepted.
- `python -m compileall -q experiments/ctv2_consistency_wire` passed.
- Local shell `git clone` still failed DNS resolution; wire exact source was locally executed before publication, while the end-to-end integration run used an interface-compatible local LAB-041 copy. LAB-041 itself was independently exact-source validated in its own completed task.
- Primary provenance: RFC 9162 §§1.2, 4.4, 4.5, 4.9, 4.11 plus RFC 8446 §3 encoding conventions.
- PR #81 remote patch audited and squash-merged as `1554c94469b368132170bc34ce6dfa337d3f6cbc`.

## Known blockers / constraints

- Local shell DNS to GitHub remains unavailable/unreliable; GitHub connector plus local execution is the supported path.
- LAB-042 trusts the old/new checkpoint roots supplied to its adapter; it does not authenticate RFC 9162 signed tree heads.
- SHA-256/HASH_SIZE=32 is the exercised profile; general log profile/key distribution remains external.
- Full CT HTTP/base64 client/server behavior, log discovery and PKI trust distribution remain outside scope.
- Witness quorum/split-view observation remain in LAB-040 rather than being duplicated.

## Exact next action

Start Issue #82 / LAB-043. Research RFC 9162 §§4.1, 4.9, 4.10 and the signature-algorithm/profile binding. Build `experiments/ctv2_sth_chain/` with strict `signed_tree_head_v2` parsing, exact signature-input verification, LogID/key/profile binding and malformed-input rejection. Then replace LAB-042's pretrusted checkpoint roots with two authenticated STH artifacts and demonstrate the full chain `signed old STH + signed new STH + consistency_proof_v2 -> LAB-041 append-only verification`. Retain an unsafe seed that trusts parsed STH fields without verifying their signature.

## Backlog

- #82 / LAB-043 — CT v2 signed-tree-head wire/signature binding and proof-chain conformance — READY.
- Independent witness/gossip transport reliability and Byzantine consensus remain intentionally out of scope unless later product requirements justify them.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
