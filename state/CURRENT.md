# Current Lab State

Last updated: 2026-08-19

## Active objective

Advance from bounded witness/split-view detection to interoperable compact append-only consistency proofs. LAB-040 is complete: independent views can now be compared through durable witness checkpoints, replay/freeze handling, distinct-witness quorum and explicit split-view detection, while consensus/prevention remains deliberately out of scope.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-040.
- Completed Issue #76 / LAB-040.
- Merged PR #77 / LAB-040 as `e184ce26f9372707a6e4a6015307fda21c0f9dbb`.
- Active next: Issue #78 / LAB-041 — READY.
- Active branch: none yet.
- Active PR: none.

## Last completed step

LAB-040 built and audited `experiments/anchor_transparency_witness/`. It implements versioned signed checkpoints, RFC-style Merkle commitments, a deterministic self-contained append-only reference proof, durable witness watermark/restart state, local freshness policy, witness countersignatures, distinct-identity threshold checking and a checkpoint observer that detects conflicting same-size roots after independently obtained views meet.

The unsafe self-presented-checkpoint baseline accepted two validly signed forks. The corrected suite distinguishes cryptographic replay from local freeze/freshness and explicitly states that witnessing detects equivocation after observation/gossip rather than preventing isolated forks.

## Evidence produced

- `experiments/anchor_transparency_witness/protocol.py`
- `experiments/anchor_transparency_witness/tests/test_protocol.py`
- `experiments/anchor_transparency_witness/tests/unsafe_self_presented_expected_failure.py`
- `experiments/anchor_transparency_witness/README.md`
- `research/2026-08-19-witnessed-transparency-checkpoints.md`
- Corrected exact local suite: 14/14 deterministic tests passed.
- Unsafe baseline: expected failure, two forks accepted (`2 != 1`).
- `python -m compileall -q experiments` passed.
- Remote protocol/test/unsafe blob SHA values matched locally executed `git hash-object` values after the final audit fix.
- Audit fixes: RFC-style tree decomposition; cross-witness observer; restart-self-contained reference proof; duplicate witness de-duplication without quorum inflation/DoS; local freshness semantics; strict checkpoint type/structure validation.
- Primary donors: RFC 9162 Certificate Transparency v2, transparency-dev Witness, Trillian transparent logging.
- PR #77 remote patch audited and squash-merged as `e184ce26f9372707a6e4a6015307fda21c0f9dbb`.

## Known blockers / constraints

- Local shell DNS to GitHub remains unavailable/unreliable; GitHub connector plus local execution is the supported path.
- HMAC remains reference-only deterministic cryptography; production log/witness private keys must not reside in verifier state.
- LAB-040 consistency evidence is deliberately explicit/non-succinct and is not RFC 9162 wire-compatible; this is the concrete gap assigned to LAB-041.
- A freshness timeout is a local policy observation, not cryptographic proof that a log operator is malicious.
- Witnessing cannot prevent an isolated split view before independent evidence is distributed/compared and does not implement Byzantine consensus.
- Witness-store rollback resistance remains a separate LAB-034/035 external-anchor concern.

## Exact next action

Start Issue #78 / LAB-041. Research the exact RFC 9162 Merkle consistency proof generation/verification algorithm and a primary/reference implementation or authoritative vector set. Build `experiments/rfc9162_consistency/` with compact proofs, malformed/tampered proof rejection, power-of-two and odd-size edge cases, and differential/reference validation. Integrate the compact verifier with LAB-040 witness checkpoints without requiring prior leaf material.

## Backlog

- #78 / LAB-041 — RFC 9162 compact consistency-proof interoperability and differential conformance — READY.
- Independent witness/gossip transport reliability and Byzantine consensus remain intentionally outside LAB-040; create follow-up only if later product requirements justify them.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
