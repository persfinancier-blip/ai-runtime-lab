# Current Lab State

Last updated: 2026-09-15

## Active objective
LAB-086 remains priority #1: execute the exact asymmetric break-glass history migration gate from authoritative executable pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. When byte-exact materialization remains unavailable, continue LAB-095/#180 + LAB-096/#181 composition on draft PR #187. LAB-099 PREPARED authority waits on LAB-095 completion.

## Active issue / branch / PR
- #163 / LAB-086: draft PR #165; keep draft.
- #180 LAB-095 + #181 LAB-096: branch `lab-095-database-identity-red-intent`, draft PR #187, current head `af4baae16f4f4cc9110f23a1d58cf7dddde534e2`; keep draft.
- #169 LAB-090: draft PR #175; activation behavior still must be ported semantically.
- #176 LAB-092: draft PR #177 retained as donor; shared schema, locked provenance/receipt guard, read-only startup gate, and explicit migration writer are adapted onto PR #187.
- #184 LAB-099: draft PR #186; blocked on LAB-095 completion.
- Retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173.

## Last completed step
LAB-086 was probed first. Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`, exit 128. No LAB-086 PASS is claimed.

Fallback work added opt-in `activation_schema_migration.py` to PR #187. It adapts PR #177 `_install_and_reserve_prepared` without its authority-heavy composition: migration-only construction binds canonical path once and exact `CoordinatorOnlyProviderHistory` once; durable locked verification uses private `_history()`; one `BEGIN IMMEDIATE` covers runtime-generation check, exact DDL installation, deterministic PREPARED marker reservation, and `shared_anchor_meta` advance; partial/mismatched/CONFIRMED-corrupt states and unrelated PREPARED intents fail closed; no `_bind_live_provider_history_provenance()` or post-construction history replacement exists.

Initial commit `f4ff3713addf71a8f7b95c15afa86c6622e3e07d` was immediately audited. The audit found PREPARED-resume did not explicitly reject an unrelated second PREPARED row. Fixed before handoff in current head `af4baae16f4f4cc9110f23a1d58cf7dddde534e2`, blob `fd3e676008ca28ff7070559579d76509a79a8262`.

Durable evidence: `research/2026-09-15-lab092-explicit-atomic-migration-writer.md`, main commit `9a2f3d8d87df3a7b3be86e622668711eba0cab71`. #176 and PR #187 updated.

## Known failures / blockers
- LAB-086 complete real-ledger gate remains unexecuted because shell DNS cannot resolve GitHub and no supported connector-to-filesystem byte-preserving bridge is exposed.
- Exact PR #187 repository pytest/compileall remains unavailable for the same materialization reason; do not claim whole-branch GREEN.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 complete eight-file no-stub tree still needs same-run reconstruction/hash verification plus execution.
- LAB-096 construction-bound history strategy, least-capability public view, and same-transaction receipt guard are source-patched on PR #187 but still need exact repository behavioral gates.
- LAB-090 PR #175 and LAB-092 PR #177 remain source-incompatible with LAB-096 if authority-heavy files are selected wholesale. Port semantics only.
- LAB-092 startup/migration writer remains intentionally opt-in until LAB-090 activation fencing/recovery semantics are composed.
- LAB-092 receipt provenance must remain checked through supplied locked `q` inside the receipt transaction; no out-of-transaction precheck.
- Final composition must preserve activation fencing, provenance fail-closed behavior, `CanonicalDatabaseBinding`, construction-bound provider-history strategy, least-capability public inspection, and same-transaction provenance guard.

## Exact next action
Probe LAB-086 first. Execute its complete gate only if authoritative pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` can be placed byte-for-byte into an executable filesystem; do not manually reserialize the large security-critical closure.

If LAB-086 remains transport-blocked, add focused regressions for the new PR #187 migration writer: partial DDL, unrelated PREPARED intent (including PREPARED resume), stale runtime generation, exact PREPARED resume, and CONFIRMED-corrupt DDL. Keep the writer opt-in. After those regressions, port the smallest LAB-090 activation fencing/recovery semantics from PR #175 while retaining private `_history()`, canonical DB binding, and no post-construction strategy replacement.

Composition order: PR #187 structural authority base -> shared `activation_schema.py` -> locked LAB-092 classifier/receipt guard -> read-only startup gate -> explicit migration writer -> focused migration regressions -> LAB-090 activation fencing semantics -> exact/downstream gates.

## Backlog
- #163 LAB-086 — IN_PROGRESS; exact executable gate pending.
- #180 LAB-095 — IN_PROGRESS; DB binding implemented; exact/downstream gates pending.
- #181 LAB-096 — IN_PROGRESS/COMPOSED ON PR #187; source fixes present; exact/downstream validation pending.
- #169 LAB-090 — retained draft; activation behavior semantic port pending.
- #176 LAB-092 — retained draft; migration writer now composed on PR #187; focused writer regressions next.
- #167 LAB-088, #170 LAB-091 — retained draft gates pending.
- #178..185 LAB-093..100 — architecture/security follow-ups.
- #184 LAB-099 — PREPARED authority waits on LAB-095 completion.
