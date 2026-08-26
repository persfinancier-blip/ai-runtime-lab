# Current Lab State

Last updated: 2026-08-26

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: Issue #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Current observed PR #165 HEAD: `95fa5da3c457e3431cd596ec969d5939b0a1d925`; mergeable=false; full current-head LAB-080→086 real-ledger execution gate remains outstanding.
- Fresh compare: branch is ahead 154 / behind 105. All 59 PR files are additions relative to current main; no path-level overlap is observed, so the reported non-mergeability is currently history divergence rather than an established content conflict.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; current observed PR #173 HEAD `0287d961c64dbf4dedf7cab8f97ffe61dc4223fc`, mergeable=true, draft.

## Last completed step

Re-read AGENTS.md, CURRENT and SELF_RESUME, inspected PR #165/#173 and resumed LAB-086 first. Direct shell GitHub transport remains unavailable, and the full exact LAB-080→086 dependency closure was not safely reconstructed in this runtime. Fresh source audit of current `migration_guard.py`, `suffix.py`, `final_supported.py` and `strict_fence.py` did not establish a new LAB-086 privilege-escalation/stale-writer blocker. No new LAB-086 PASS or merge claim was made.

Per the recorded fallback, audited LAB-091 beyond exact row-token binding. Found a real state-machine gap: the v2 one-shot guards proved that a permit matched the exact row requested, but did not prove that the row was a legal successor of current durable LAB-080/LAB-082 state. Focused executable counterexamples accepted:
- a PREPARED intent with `provider_id='attacker'`, generation 999 while the durable provider head was anchor-A generation 1;
- an orphan asymmetric provider receipt with no matching intent.

Published additive v3 fix on PR #173:
- `cross_table_guards.py` — exact runtime blob `b73c7ae95669a561a13c5fc2c1eca752721fe8a4`;
- `state_machine_operation_scoped.py` — exact runtime blob `b359a9a191ea9632e97c227193b3bde886f904dc`;
- `test_cross_table_state_machine_guards.py` — published blob `7ab5b406e3a1c1b45ac2f171a6e02fe6503777f6`;
- research note `research/2026-08-26-lab091-cross-table-state-machine-binding.md`.

The v3 guards add cross-table invariants in a distinct trigger namespace: intent predecessor must equal the current shared-anchor tail; intent provider ID/generation must equal the current asymmetric provider head; meta advancement requires its matching PREPARED intent; provider-receipt creation requires RECONCILE evidence matching an existing PREPARED intent's request/provider/generation/position. `SupportedStateMachineOperationScopedAsymmetricSharedAnchorLedger` installs v2 exact-row guards + v3 state-machine guards atomically.

Focused candidate execution passed **6/6**: wrong provider, wrong tail, missing intent for meta advance, orphan receipt, READ-vs-RECONCILE, and provider-generation rotation. The two runtime modules above are byte-identical to the locally executed candidate. The published regression file differs in formatting from the earlier local harness, so the 6/6 result is focused candidate evidence, not exact execution of the published test blob.

## Evidence retained

- LAB-086 lower-stack exact evidence remains LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, asymmetric custody 8/8, public/final 11/11; lower unsafe baselines failed as expected.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- LAB-087 is merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 reference layer exact 11/11 PASS + compileall; unsafe raw-DML seed failed as intended.
- LAB-091 one-shot permit primitive exact 6/6 PASS + compileall.
- LAB-091 full mutable-row guards exact 12/12 PASS including legacy-surface persistence.
- LAB-091 identical-worker confirmation convergence focused exact-byte candidate: 4/4 PASS.
- LAB-091 v3 cross-table state-machine candidate: focused 6/6 PASS; published runtime blobs exactly match executed candidate, published regression blob itself not yet exact-executed.

## Known blockers / constraints

- LAB-086 remains first priority. Merge gate is exact current-head execution on one LAB-080→086 closure: own/lower cardinality + migration + suffix + final-supported/security suites, unsafe seed, compileall and final audit. PR #165 reports mergeable=false; do not reconcile/integrate before that gate is clean.
- Direct shell GitHub transport is unavailable; connector reconstruction works but full closure assembly is still file-by-file/expensive.
- LAB-091 final candidate is now the additive `SupportedStateMachineOperationScopedAsymmetricSharedAnchorLedger`; it still needs exact real LAB-080/LAB-082 execution across restart, actual concurrent workers, crash rollback, timeout/UNKNOWN reconciliation and LAB-087 restricted-worker composition.
- The v3 guards reduce damage from an incorrectly issued permit by enforcing key cross-table invariants; they do not turn SQLite triggers/UDFs into a boundary against arbitrary same-privilege DDL/UDF control. LAB-087 remains the external writable-handle/process/filesystem boundary.
- Further LAB-091 hardening to evaluate in the real-stack gate: whether SQL should also recompute LAB-080 deterministic `request_id`, and whether watermark jumps should be additionally tied to exact verified history rather than trusted permit issuance.
- LAB-090/#169 provider handoff freshness remains separate.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. LAB-086 first: connector-reconstruct exact current PR #165 `migration_guard.py`, `suffix.py`, `final_supported.py` and the minimal import-closure of their real-schema tests on the proven LAB-080→085 stack; execute own/lower cardinality, migration, suffix, final-supported, cross-binding/history, inherited/direct-surface, strict-fence/thaw, restart/concurrency tests; then unsafe seed + full compileall + final audit.
2. If that exact closure remains tool-limited, continue LAB-091 from PR #173 using the new `SupportedStateMachineOperationScopedAsymmetricSharedAnchorLedger`: exact-execute the published v3 regression, then run against real LAB-080/LAB-082 with two actual workers sharing one intent/request and prove exactly one confirmation plus identical receipt convergence.
3. Add exact restart, crash rollback, timeout-after-commit/UNKNOWN reconciliation and LAB-087 restricted-worker composition tests. Audit deterministic request-id and watermark/history binding before declaring LAB-091 supported. Keep PR #173 draft until that complete gate is clean.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; full current-head real-ledger execution gate remains.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; one-shot/v2 guards, legacy downgrade and identical-worker convergence are tested; v3 cross-table runtime guards are published and focused-tested, but exact real-stack restart/concurrency/crash/UNKNOWN/LAB-087 gate remains.
