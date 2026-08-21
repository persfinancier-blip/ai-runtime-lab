# Current Lab State

Last updated: 2026-08-21

## Active objective

LAB-072 — serialize concurrent broker requests and credential rotation around one durable local transaction boundary while preserving LAB-071 per-message sender authority, stable idempotency identity, UNKNOWN reconciliation, and no raw-secret persistence.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-071.
- LAB-071 Issue #133 closed DONE; PR #134 squash-merged as `f1ae711bc4b934529187756b401c80b618601afa`.
- Active Issue #135 / LAB-072 — IN_PROGRESS.
- Active branch: `lab/072-transactional-broker-journal`.
- Draft PR #136 `[LAB-072] Transactional broker request journal`.
- Published first-slice head: `a6ac75116ba6b91f2e7d6cf3b26a0ad0f5a146ef`.

## Last completed step

LAB-071 was exact-source reconstructed from GitHub connector bytes, blob-verified, and regression-tested before merge. Final published LAB-071 evidence: corrected protocol/restart 18/18, LAB-069 14/14, LAB-070 8/8, LAB-031 8/8; unsafe socket-possession seed failed as expected. A final audit also hardened durable JSON parsing and required supplied credential generation to match durable state generation.

LAB-072 then started. Its first executable SQLite reference slice atomically serializes request reservation and credential rotation, persists canonical request digest + stable effect key + `INTENT/UNKNOWN/CONFIRMED`, and uses a separate idempotent side-effect sink for reconciliation. An unsafe check-then-act baseline duplicated one logical request.

A semantic audit found and fixed a rotation race: rotation must not commit while current-generation `INTENT`/`UNKNOWN` requests remain unresolved unless old secret generations are explicitly retained. The reference rule now blocks rotation until those requests are reconciled/confirmed.

The published LAB-072 protocol blob `6066d90b3032eeefc0f2dbbd272c09a9a716b5b2` and corrected-test blob `656284062a96b7915e3283b181c58bd7a8e9281d` matched the exact locally executed bytes.

## Evidence produced

- LAB-071 merge: `f1ae711bc4b934529187756b401c80b618601afa`.
- LAB-071 final protocol blob: `44c46e30f537cffea26cdf76c2f0be8493711026`.
- LAB-071 final restart-test blob: `4897f884b2c669418ac0fc4d4bef621af2243681`.
- LAB-072 first-slice protocol: `experiments/transactional_broker_journal/protocol.py`.
- LAB-072 failure matrix: `experiments/transactional_broker_journal/tests/test_protocol.py`.
- LAB-072 unsafe seed: `experiments/transactional_broker_journal/tests/unsafe_concurrent_expected_failure.py`.
- LAB-072 research note: `research/2026-08-21-transactional-broker-journal.md`.
- LAB-072 corrected exact-source suite: 13/13 passed.
- LAB-072 20 repeated rotation-vs-reservation races: only safe serial outcomes observed.
- LAB-072 unsafe seed: failed as expected because two identical requests produced two side effects instead of one.
- LAB-072 compileall: passed.

## Known blockers / constraints

- No owner-level blocker.
- PR #136 is intentionally draft; LAB-072 is not merge-ready.
- Current LAB-072 slice isolates SQL/effect semantics and still accepts an abstract `Request`; it does not yet sit behind LAB-071's actual kernel `SCM_CREDENTIALS` + live pidfd/starttime authority boundary.
- Current concurrency evidence uses separate SQLite connections/worker objects in threads; add real process-level multi-worker contention before completion.
- The idempotent sink is an adapter contract. A real external system that cannot expose stable idempotency/reconciliation cannot inherit the same UNKNOWN semantics; do not claim universal exactly-once behavior.
- SQLite single-writer behavior is a local correctness reference, not a PostgreSQL production performance/locking result.

## Exact next action

Resume Issue #135 / draft PR #136. Integrate `TransactionalJournal.reserve/process` behind LAB-071's real `ReceivedRequest` sender validation so kernel-observed SCM_CREDENTIALS and fresh pidfd/starttime authorization occur before any new durable reservation/effect, while exact already-committed retries remain digest-bound and reconcilable. Add a real process-level multi-worker race against one journal/sink, including same-request and substitution cases. Then reconstruct exact published PR bytes, run LAB-072 plus exact LAB-071/LAB-015/LAB-031 regressions and compileall, perform a separate remote patch audit, fix findings, and only then consider marking PR #136 ready/merging.

## Backlog

- #135 / LAB-072 — concurrent broker request serialization + transactional effect journal — IN_PROGRESS; draft PR #136.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
