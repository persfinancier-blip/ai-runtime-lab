# Current Lab State

Last updated: 2026-08-27

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Current observed PR #165 HEAD: `95fa5da3c457e3431cd596ec969d5939b0a1d925`; mergeable=false; full current-head LAB-080→086 real-ledger execution gate remains outstanding.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; current observed HEAD `56e0a64af7055ca89d8bd6bd662afdf5cc8ca95c`, mergeable=true, draft.

## Last completed step

Re-read AGENTS.md, CURRENT and SELF_RESUME and resumed LAB-086 first. PR #165 is still draft/non-mergeable and its exact full real-ledger closure was not safely reconstructed in this runtime; no new LAB-086 PASS or merge claim was made.

Used the recorded fallback to harden LAB-091 where CURRENT had two explicit unresolved invariants: deterministic LAB-080 request identity and watermark/history binding. Published additive v4 files on PR #173:

- `state_machine_udfs.py` — deterministic `shared-anchor:{position}:{sha256(canonical fields)}` request-id UDF, blob `8c1d6d0cd075285aed3a90ac337b60b60c1d608b`;
- `history_binding_guards.py` — blob `bd1f8fe16d3cdeaaa0f96bca1406e1edb02cfe0f`;
- `history_bound_operation_scoped.py` — supported additive candidate composing v2 exact-row + v3 cross-table + v4 history guards;
- `test_history_binding_guards.py` — updated focused regression;
- research note `research/2026-08-27-lab091-request-id-watermark-history-binding.md`.

The v4 guards enforce:

1. intent INSERT uses the deterministic LAB-080 request_id;
2. watermark INSERT/UPDATE cannot cross PREPARED, missing or malformed-predecessor history and requires complete CONFIRMED rows with receipt bindings;
3. PREPARED->CONFIRMED requires a persisted RECONCILE provider receipt matching request/provider/generation/position/stable_binding.

Focused local candidate execution passed **9/9** and compileall passed. The final Contents API rewrite changed the published regression/guard blob identities, so this 9/9 is deliberately **not yet promoted to exact-published-source evidence**. Reconstruct/rerun the published bytes before counting it.

## Evidence retained

- LAB-086 lower-stack exact evidence: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, asymmetric custody 8/8, public/final 11/11; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 reference layer exact 11/11 PASS + compileall; unsafe raw-DML seed failed as intended.
- LAB-091 one-shot primitive exact 6/6 PASS + compileall.
- LAB-091 full mutable-row guards + legacy persistence exact 12/12 PASS.
- LAB-091 v3 cross-table state-machine published-source regression exact 6/6 PASS + compileall.
- LAB-091 v4 focused candidate 9/9 PASS + compileall; exact-published rerun still required.

## Known blockers / constraints

- LAB-086 remains first priority. Merge gate is exact current-head execution on one LAB-080→086 closure: own/lower cardinality + migration + suffix + final-supported/security suites, unsafe seed, compileall and final audit. Do not reconcile/integrate before that gate is clean.
- Direct shell GitHub transport remains unavailable; connector reconstruction works but the full LAB-080→086 closure remains file-by-file/expensive.
- LAB-091 final candidate is now `SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger`; it still needs exact published v4 rerun and real LAB-080/LAB-082 execution across restart, actual concurrent workers, crash rollback, timeout/UNKNOWN reconciliation and LAB-087 restricted-worker composition.
- LAB-091 triggers/UDFs are not a same-privilege SQL sandbox; LAB-087 remains the external single-writable-handle/process/filesystem boundary.
- LAB-090/#169 provider handoff freshness remains separate.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. LAB-086 first: connector-reconstruct exact current PR #165 `migration_guard.py`, `suffix.py`, `final_supported.py` plus the minimal real-schema test import closure on the proven LAB-080→085 stack; execute own/lower cardinality, migration, suffix, final-supported, cross-binding/history, inherited/direct-surface, strict-fence/thaw, restart/concurrency tests; then unsafe seed + full compileall + final audit.
2. If that closure remains tool-limited, exact-reconstruct the published LAB-091 v4 files (`operation_permit.py`, `state_machine_udfs.py`, `history_binding_guards.py`, `test_history_binding_guards.py`) and rerun before promoting 9/9 to exact evidence.
3. Then execute `SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger` on real LAB-080/LAB-082 with two actual workers sharing one request, restart, crash rollback, timeout-after-commit/UNKNOWN reconciliation and LAB-087 restricted-worker composition. Keep PR #173 draft until clean.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; full current-head real-ledger execution gate remains.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; v4 deterministic request-id/history-binding layer published, focused 9/9 candidate green, exact-published rerun + real-stack gate remain.
