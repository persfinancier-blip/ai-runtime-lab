# Current Lab State

Last updated: 2026-08-27

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Current observed PR #165 HEAD: `95fa5da3c457e3431cd596ec969d5939b0a1d925`; mergeable=false; full current-head LAB-080→086 real-ledger execution gate remains outstanding.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; current observed HEAD `56e0a64af7055ca89d8bd6bd662afdf5cc8ca95c`, mergeable=false, draft.

## Last completed step

Resumed LAB-086 first. Re-read AGENTS.md, CURRENT and SELF_RESUME, rechecked PR #165, and probed direct GitHub transport in this runtime. DNS remains unavailable; explicit `curl --resolve` probes against multiple GitHub IPs also failed to connect. The GitHub connector remains healthy. No LAB-086 PASS or merge claim was fabricated; the exact full LAB-080→086 closure still requires connector reconstruction.

Used the recorded fallback to close the outstanding LAB-091 v4 evidence gap. Reconstructed the exact published branch bytes through the GitHub connector, verified every file with local `git hash-object`, and executed the published regression:

- `operation_permit.py` `637784a5cb61a024a1df3e0e983887b6d0a838be` — exact match;
- `state_machine_udfs.py` `8c1d6d0cd075285aed3a90ac337b60b60c1d608b` — exact match;
- `history_binding_guards.py` `bd1f8fe16d3cdeaaa0f96bca1406e1edb02cfe0f` — exact match;
- `test_history_binding_guards.py` `a8af116bc220113cd63106e8ffa6336dda88d5f9` — exact match.

Executed `experiments.mutable_shared_anchor_writer.tests.test_history_binding_guards`: **9/9 PASS**. Compileall over the reconstructed `mutable_shared_anchor_writer` package passed. The recurring artifact-tool spreadsheet warmup timeout was unrelated Python startup noise; unittest and compileall both returned rc=0.

This promotes the previous focused-only v4 evidence to **exact-published-source 9/9 PASS + compileall**.

## Evidence retained

- LAB-086 lower-stack exact evidence: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, asymmetric custody 8/8, public/final 11/11; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 reference layer exact 11/11 PASS + compileall; unsafe raw-DML seed failed as intended.
- LAB-091 one-shot primitive exact 6/6 PASS + compileall.
- LAB-091 full mutable-row guards + legacy persistence exact 12/12 PASS.
- LAB-091 v3 cross-table state-machine published-source regression exact 6/6 PASS + compileall.
- LAB-091 v4 deterministic request-id/history-binding published-source regression now exact **9/9 PASS + compileall**.

## Known blockers / constraints

- LAB-086 remains first priority. Merge gate is exact current-head execution on one LAB-080→086 closure: own/lower cardinality + migration + suffix + final-supported/security suites, unsafe seed, compileall and final audit. Do not reconcile/integrate before that gate is clean.
- Direct shell GitHub transport remains unavailable, including explicit-IP `--resolve` probes. Connector reconstruction works but the full LAB-080→086 closure remains file-by-file/expensive.
- LAB-091 final candidate is `SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger`; v4 focused evidence is now exact, but the candidate still needs execution against real LAB-080/LAB-082 across restart, actual concurrent workers, crash rollback, timeout/UNKNOWN reconciliation and LAB-087 restricted-worker composition.
- LAB-091 triggers/UDFs are not a same-privilege SQL sandbox; LAB-087 remains the external single-writable-handle/process/filesystem boundary.
- LAB-090/#169 provider handoff freshness remains separate.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. LAB-086 first: connector-reconstruct exact current PR #165 `migration_guard.py`, `suffix.py`, `final_supported.py` plus the minimal real-schema test import closure on the proven LAB-080→085 stack; execute own/lower cardinality, migration, suffix, final-supported, cross-binding/history, inherited/direct-surface, strict-fence/thaw, restart/concurrency tests; then unsafe seed + full compileall + final audit.
2. If that closure remains tool-limited, execute `SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger` against real LAB-080/LAB-082 dependencies with two actual workers sharing one request, restart, crash rollback, timeout-after-commit/UNKNOWN reconciliation and LAB-087 restricted-worker composition.
3. Keep PR #165 and PR #173 draft until their complete real-stack gates are clean.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; full current-head real-ledger execution gate remains.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; v4 exact-published 9/9 + compileall now proven; real LAB-080/LAB-082 integration gate remains.
