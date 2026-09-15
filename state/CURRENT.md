# Current Lab State

Last updated: 2026-09-15

## Active objective
LAB-086 remains priority #1: execute the exact asymmetric break-glass history migration gate from authoritative executable pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. When byte-exact materialization remains unavailable, continue the LAB-095/#180 + LAB-096/#181 composition fallback on draft PR #187. LAB-099 PREPARED authority waits on LAB-095 completion.

## Active issue / branch / PR
- #163 / LAB-086: draft PR #165; keep draft.
- #180 LAB-095 + #181 LAB-096: branch `lab-095-database-identity-red-intent`, draft PR #187, current head `0e6a56ec7e68b962344f8f8f797960456b99bd21`; keep draft.
- #169 LAB-090: draft PR #175; activation behavior still must be ported semantically.
- #176 LAB-092: draft PR #177 retained as donor; shared schema, locked provenance/receipt guard, and read-only startup gate are now adapted onto PR #187.
- #184 LAB-099: draft PR #186; blocked on LAB-095 completion.
- Retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173.

## Last completed step
LAB-086 was probed first in the current executable runtime. Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`, exit 128. No LAB-086 PASS is claimed.

Fallback work then inspected PR #177 startup/migration semantics and added the next small LAB-092 slice to PR #187:
- `activation_schema_startup.py` provides a path-level read-only wrapper over `classify_activation_schema_provenance_locked(q)`;
- ordinary startup accepts only `COMPLETE`;
- `LEGACY_ABSENT`, `DDL_INSTALLED_UNMARKED`, and `DDL_INSTALLED_PREPARED` raise `ActivationSchemaMigrationRequired` and therefore require the explicit migration path;
- unknown/non-contract states fail closed;
- `ActivationSchemaProvenanceStartupMixin` performs the gate before inherited constructor side effects;
- it contains no DDL installation, migration-marker write, provider-history reference, mutation-authority recovery, or post-construction history replacement.

Branch commits: production `a97f37a5af49cc3e475660b0f98d46982a9d37c4`; initial regression `53a56e90ab382cf0e18772e01c389fed478b80f4`; corrected regression/current head `0e6a56ec7e68b962344f8f8f797960456b99bd21`. The initial regression incorrectly inspected `Connection.in_transaction` after the wrapper closed the connection; it was corrected to assert classifier invocation and unchanged schema. No production change was required.

Durable evidence: `research/2026-09-15-lab092-read-only-startup-gate.md`, main commit `3262d76c37d035a3d064299eb3a5e1c598050b96`. #176 and PR #187 were updated.

## Known failures / blockers
- LAB-086 complete real-ledger gate remains unexecuted because shell DNS cannot resolve GitHub and no supported connector-to-filesystem byte-preserving bridge is exposed.
- Exact PR #187 repository pytest/compileall remains unavailable for the same materialization reason; do not claim whole-branch GREEN.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 complete eight-file no-stub tree still needs same-run reconstruction/hash verification plus execution.
- LAB-096 construction-bound history strategy, least-capability public view, and same-transaction receipt guard are source-patched on PR #187 but still need exact repository behavioral gates.
- LAB-090 PR #175 and LAB-092 PR #177 remain source-incompatible with LAB-096 if authority-heavy files are selected wholesale. Port semantics only.
- The new startup mixin intentionally remains opt-in. Do not wire it into the default supported ledger until the explicit LAB-092 migration writer and LAB-090 activation installation/fencing semantics are composed.
- LAB-092 receipt provenance must remain checked through the supplied locked `q` inside the receipt transaction; no out-of-transaction precheck.
- Final composition must preserve activation fencing, provenance fail-closed behavior, `CanonicalDatabaseBinding`, construction-bound provider-history strategy, least-capability public inspection, and same-transaction provenance guard.

## Exact next action
Probe LAB-086 first. Execute its complete gate only if authoritative pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` can be placed byte-for-byte into an executable filesystem; do not manually reserialize the large security-critical closure.

If LAB-086 remains transport-blocked, continue PR #187 with the smallest explicit LAB-092 migration-writer slice adapted from PR #177 `_install_and_reserve_prepared`:
1. construct the migration reservation surface with one-time canonical path binding and one-time exact `CoordinatorOnlyProviderHistory` installation only;
2. route durable locked history verification through private `_history()` only;
3. under one `BEGIN IMMEDIATE`, require an existing shared-anchor ledger, accept only exact legacy-absent or exact already-installed activation DDL with ABSENT/PREPARED marker, reject partial/mismatched/CONFIRMED-corrupt states, reject another PREPARED anchor intent, install exact DDL only when absent, reserve the deterministic migration marker, and advance `shared_anchor_meta` atomically;
4. never use `_bind_live_provider_history_provenance()` and never replace `_provider_history` after construction;
5. add focused fail-closed regressions for partial DDL, existing unrelated PREPARED intent, stale runtime generation, PREPARED resume, and CONFIRMED-corrupt DDL;
6. keep this writer opt-in until LAB-090 activation fencing semantics are ported;
7. keep changes small/file-scoped for Contents API conflict checking.

Composition order: PR #187 structural authority base -> shared `activation_schema.py` -> locked LAB-092 classifier/receipt guard -> read-only LAB-092 startup gate -> explicit LAB-092 migration writer -> LAB-090 activation fencing semantics -> exact/downstream gates.

## Backlog
- #163 LAB-086 — IN_PROGRESS; exact executable gate pending.
- #180 LAB-095 — IN_PROGRESS; DB binding implemented; exact/downstream gates pending.
- #181 LAB-096 — IN_PROGRESS/COMPOSED ON PR #187; source fixes present; exact/downstream validation pending.
- #169 LAB-090 — retained draft; activation behavior semantic port pending.
- #176 LAB-092 — retained draft; shared schema + locked classifier/receipt guard + read-only startup gate composed on PR #187; explicit migration writer is next.
- #167 LAB-088, #170 LAB-091 — retained draft gates pending.
- #178..185 LAB-093..100 — architecture/security follow-ups.
- #184 LAB-099 — PREPARED authority waits on LAB-095 completion.
