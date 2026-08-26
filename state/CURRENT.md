# Current Lab State

Last updated: 2026-08-27

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Current observed PR #165 HEAD: `95fa5da3c457e3431cd596ec969d5939b0a1d925`; GitHub currently reports mergeable=true; full current-head LAB-080→086 real-ledger execution gate remains outstanding.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; current observed HEAD `56e0a64af7055ca89d8bd6bd662afdf5cc8ca95c`; mergeable=true; draft.

## Last completed step

Resumed LAB-086 first and narrowed the remaining exact reconstruction gate to a branch-local dependency closure. The GitHub connector can return the recursive tree for PR HEAD `95fa5da...` and full exact file contents by blob SHA, so the correct gate is now explicit: reconstruct LAB-080→085 from the **same PR HEAD commit tree**, not from current `main`, then execute LAB-086 on those exact bytes. No repository archive/export action is exposed by the connector; workflow artifacts are not an acceptable execution substitute under AGENTS.md.

Recorded the relevant branch-local lower blob identities, including LAB-080 shared-anchor `68834409.../22a05c04...`, LAB-082 `a2fc3456.../23ae688c.../d61bcd54...`, LAB-083 `688f3961.../49e9a79d.../9e96b19e.../59337e73...`, LAB-084 `d464e133.../f0b45f52...`, and LAB-085 lifecycle/custody/final sources including final `3baf4054...`.

Re-audited exact current LAB-086 `migration_guard.py` (`1a9209b...`), `strict_fence.py` (`5da01e28...`), `suffix.py` (`44847bde...`) and `final_supported.py` (`ceb7f48a...`). No new confirmed privilege-escalation/stale-supported-writer blocker was established.

Investigated a suspected incompatibility where post-cutoff LAB-086 might require threshold proofs for pre-enablement LAB-082 provider transitions. The suspicion was rejected after exact-source comparison: LAB-086 `_verify_provider_thresholds_locked()` consumes `_provider_transitions_locked()`, and that helper selects only transitions whose new generation is strictly after the authenticated LAB-083 `start_provider_generation`, exactly matching LAB-083 supported verifier semantics. No runtime change was made.

Fallback LAB-091 audit also reconfirmed that timeout/UNKNOWN handling matches LAB-080: LAB-036 `AttestedCatchup.catch_up_one()` internally reconciles `UnknownOutcome`, and the operation-scoped surface does not introduce a different timeout contract. Constructor dispatch was checked: the most-derived v2/v3/v4 `_install_guards()` executes, so the legacy transaction-wide trigger installer is not reintroduced on the final candidate.

## Evidence retained

- LAB-086 lower-stack exact evidence: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, asymmetric custody 8/8, public/final 11/11; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Current-head LAB-086 exact-source audit on `95fa5da...`: no new blocker established; no new PASS claimed in this run.
- Branch-local exact reconstruction mechanism confirmed: recursive PR-HEAD tree + full connector `fetch_blob` content by SHA.
- PR #165 currently mergeable=true at HEAD `95fa5da3...`; draft remains mandatory until execution gate is clean.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 reference layer exact 11/11 PASS + compileall; unsafe raw-DML seed failed as intended.
- LAB-091 one-shot primitive exact 6/6 PASS + compileall.
- LAB-091 full mutable-row guards + legacy persistence exact 12/12 PASS.
- LAB-091 v3 cross-table state-machine published-source regression exact 6/6 PASS + compileall.
- LAB-091 v4 deterministic request-id/history-binding published-source regression exact 9/9 PASS + compileall.

## Known blockers / constraints

- LAB-086 remains first priority. Merge gate is exact current-head execution on one branch-local LAB-080→086 closure: own/lower cardinality + migration + suffix + final-supported/security suites, unsafe seed, compileall and final audit. Do not reconcile/integrate before that gate is clean.
- Direct shell GitHub transport remains unavailable and the connector exposes no repository archive/export action. Exact reconstruction is possible from PR-head blobs but remains file-by-file/expensive.
- LAB-091 final candidate is `SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger`; it still needs execution against real LAB-080/LAB-082 across restart, actual concurrent workers, crash rollback, timeout/UNKNOWN reconciliation and LAB-087 restricted-worker composition.
- LAB-091 triggers/UDFs are not a same-privilege SQL sandbox; LAB-087 remains the external single-writable-handle/process/filesystem boundary.
- LAB-090/#169 provider handoff freshness remains separate.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. LAB-086 first: reconstruct the minimal import closure from the **same PR HEAD `95fa5da...` tree** using exact blob SHAs, starting from LAB-080 `anchor_attestation/shared_anchor_intent_ledger`, LAB-082 asymmetric history, LAB-083 threshold rotation, LAB-084 recovery, LAB-085 custody/final and then current LAB-086 implementation/tests. Verify local files with `git hash-object` before execution.
2. Execute current own/lower cardinality, migration/root-coauthorization/restart, scrubbed-prefix/suffix, orphan/partial-state, public-rotation cross-binding/history, inherited/direct-surface, least-privilege thaw, final single-snapshot and concurrency/rotation-race regressions; then unsafe seed + full compileall + final audit.
3. If the exact LAB-086 closure still cannot be completed safely in the runtime, continue LAB-091 real-stack execution with two actual workers sharing one request, restart, crash rollback, timeout/UNKNOWN reconciliation and LAB-087 restricted-worker composition.
4. Keep PR #165 and PR #173 draft until their complete real-stack gates are clean.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; full current-head branch-local real-ledger execution gate remains.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; v4 exact-published 9/9 + compileall proven; real LAB-080/LAB-082 integration gate remains.
