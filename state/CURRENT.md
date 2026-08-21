# Current Lab State

Last updated: 2026-08-21

## Active objective

LAB-074 — finish exact-source validation and integration of LAB-073 authenticated sink capability/retry authority into LAB-072's transactional broker journal.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-073.
- Active: Issue #139 / LAB-074 — IN_PROGRESS.
- Active branch: `lab/074-broker-sink-capability`.
- Active PR: #140 `[LAB-074] Bind transactional broker to authenticated sink capability` — DRAFT, mergeable.
- Current audited PR HEAD: `5584e214d8548c20d171778777da0de346860c5a`.

## Last completed step

LAB-074 now extends the existing LAB-072 `broker_requests` rows in place with exact LAB-073 capability identity and adds a durable monotonic `sink_capability_heads` watermark per sink. New external work requires current authenticated sink capability; CONFIRMED durable receipts remain readable after later rotation without any external action; UNKNOWN after rotation is reconciliation-only and cannot execute a second effect under the new capability.

A separate audit found and fixed six material cross-layer defects before merge:

1. current capability was checked before returning an already CONFIRMED durable receipt;
2. capability `sink_id` was not bound to the configured external sink adapter;
3. old but still correctly signed capability generations could be replayed because there was no durable latest-generation watermark;
4. capability head could change between observation and request INSERT;
5. durable verification checked request/head tables independently instead of their relationship;
6. rotated UNKNOWN could still probe a sink whose current capability no longer authorized reconciliation.

The final implementation rechecks the capability head in the same SQL write transaction that inserts INTENT, persists restart-stable capability heads, binds worker execution to configured sink identity, and validates request-plan ↔ capability-head relations during durable verification.

## Evidence produced

- Draft PR #140; current HEAD `5584e214d8548c20d171778777da0de346860c5a`.
- Exact main LAB-072 protocol/test Git blobs reconstructed and matched GitHub: `6817459fca8ac37c11cce71865937b8f65567d83`, `656284062a96b7915e3283b181c58bd7a8e9281d`.
- Exact main LAB-073 protocol/test Git blobs reconstructed and matched GitHub: `fc05d27d5512ece585d7d6313e079ae6a234f737`, `55e42d5027fbbe1c7b66b11f08162765eba90a25`.
- Local post-audit combined suite on the tested implementation: 49/49 passed; compileall passed.
- Exact unsafe PR seed Git blob `4c5aef361082cfe8c6feaea97df5bc3cf31a3ee3` failed as intended because a journal with no capability binding executed 1 external effect when 0 was expected.
- Published PR integration-test file now matches the locally executed Git blob `d6f003b07484775e62e8da93b3574f8eb484ea7e`.
- Remote PR audit established configured sink identity binding, durable capability-head monotonicity, insert-race fencing, and reconciliation-only behavior after rotation.

## Known blockers / constraints

- No product/owner blocker.
- PR #140 remains draft because exact-source evidence has not yet been established for the final published `capability.py` byte identity. The published file contains the audited semantics, but its current Git blob differs from the locally executed post-audit copy due to editorial/formatting differences during connector publication. Do not claim the local 49/49 as exact execution of that final published blob.
- Direct shell checkout of GitHub remains unavailable in this runtime. Connector-based exact reconstruction is therefore required.
- Provider retry-retention duration remains authenticated provider/contract material; unknown retention is fail-closed.
- Mapping a configured `sink_id` to production adapter/code/endpoint identity is a trusted boundary not cryptographically solved by LAB-074.
- Time freshness beyond LAB-073's trusted `now` assumption and whole-store rollback/tamper remain delegated to earlier clock/anchor layers.
- Universal exactly-once external effects remain a non-goal.

## Exact next action

Resume PR #140 first. Reconstruct the exact current PR-head `experiments/transactional_broker_journal/capability.py` bytes through the GitHub connector without normalization and record its Git blob identity. Execute those exact bytes together with the already exact PR integration test, exact LAB-072 regression suite, exact LAB-073 regression suite, unsafe split-authority seed, and compileall. If all pass, perform one fresh full patch audit across all four PR files and update the research note/PR evidence with the observed exact hashes/results. Only then mark PR #140 ready, squash-merge with expected HEAD, close Issue #139 DONE, and select the highest-value next correctness gap.

## Backlog

- #139 / LAB-074 — transactional broker + authenticated sink-capability integration — IN_PROGRESS / exact published-source gate only.
- Candidate next gap after LAB-074: authenticated sink-adapter/endpoint registry binding so `sink_id -> concrete adapter/endpoint` is itself versioned, restart-persistent and substitution-resistant.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
