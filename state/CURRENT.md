# Current Lab State

Last updated: 2026-08-19

## Active objective

Advance from concurrency-safe trust-root activation to externally observable split-view detection. LAB-039 is complete: one shared authoritative store now activates exactly one threshold-authorized successor per exact predecessor, but global anti-equivocation still requires independently comparable transparency/witness evidence.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-039.
- Completed Issue #75 / LAB-039.
- LAB-039 final files are integrated directly in `main` through the allowed Contents API fallback because PR creation was blocked before execution by an external safety-status gate.
- Active next: Issue #76 / LAB-040 — READY.
- Active branch: none yet.
- Active PR: none.

## Last completed step

LAB-039 built and audited `experiments/anchor_rotation_concurrency/`. The final reference protocol restores LAB-038 threshold-signature verification, binds activation to the exact predecessor digest/version/authority epoch, serializes activation in one SQLite write transaction, enforces one local successor per predecessor, and reconciles timeout-after-commit by stable transition identity.

Remote branch audit found and corrected two material defects before integration: an earlier draft treated structural `signer_ids` as if they were threshold proof, and an initial reconciliation path trusted `proposal_id` without rechecking transition digests. Superseded draft research/test artifacts were removed before integration.

## Evidence produced

- `experiments/anchor_rotation_concurrency/protocol.py`
- `experiments/anchor_rotation_concurrency/tests/test_protocol.py`
- `experiments/anchor_rotation_concurrency/tests/unsafe_split_check_expected_failure.py`
- `experiments/anchor_rotation_concurrency/README.md`
- `research/2026-08-19-concurrent-threshold-rotation.md`
- Corrected local deterministic suite: 11/11 passed.
- Unsafe split check-then-write baseline: expected failure, two successors accepted (`2 != 1`).
- `python -m compileall -q experiments` passed.
- Real two-thread SQLite race: exactly one activation committed.
- Rotation-vs-recovery race: exactly one authority transition committed.
- Crash-before-commit rollback, timeout-after-commit reconciliation, restart reconstruction, stale loser retry, proposal substitution rejection and split-view observation are covered.
- Primary donors: TUF root continuity, PostgreSQL Serializable/row-locking semantics, RFC 9162 Certificate Transparency and transparency.dev consistency concepts.
- Final LAB-039 content was compare-audited as exactly five added, conflict-free paths before Contents API integration; latest LAB-039 content commit in `main`: `f7f869818e5b25305cfa6500803c822560fa8b8a`.

## Known blockers / constraints

- Local shell DNS to GitHub remains unavailable/unreliable; GitHub connector plus local execution is the supported path.
- PR creation for LAB-039 was blocked before execution by an external safety-status gate; safe Contents API integration succeeded, so this is not an active blocker.
- SQLite is a deterministic transaction reference, not a PostgreSQL performance/distributed-concurrency claim.
- HMAC remains reference-only deterministic cryptography; production trust-root private signing material must not reside in verifier state.
- LAB-039 proves one successor only inside a shared authoritative store. Two independent/forked stores can still show divergent histories; `TransparencyObserver` only detects a conflict once both views are observed.
- LAB-034/035 monotonic-anchor guarantees remain separate from global transparency consistency.

## Exact next action

Start Issue #76 / LAB-040. Research RFC 9162 checkpoint/consistency semantics plus at least one production transparency/witness mechanism. Build `experiments/anchor_transparency_witness/` with versioned checkpoints, append-only consistency verification, durable witness watermark, stale/freeze/replay handling, duplicate-witness protection, restart recovery, and an unsafe self-presented-checkpoint baseline. Explicitly separate split-view detection after witness/gossip from consensus/prevention.

## Backlog

- #76 / LAB-040 — witnessed transparency checkpoints and split-view anti-equivocation conformance — READY.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
