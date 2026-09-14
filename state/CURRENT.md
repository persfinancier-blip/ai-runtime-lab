# Current Lab State

Last updated: 2026-09-15

## Active objective
LAB-086 remains priority #1: finish the exact executable/security gate for asymmetric break-glass history migration. When byte-exact LAB-086 execution cannot be materialized safely, LAB-095/#180 plus composed LAB-096/#181 is the permitted fallback. LAB-099 PREPARED authority waits on LAB-095 completion.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165. Keep draft.
- LAB-095/#180 + LAB-096/#181: branch `lab-095-database-identity-red-intent`, draft PR #187, head `6fd9300a9efab730cb86342cf63a43227ea45406`. Keep draft.
- LAB-090/#169: draft PR #175, head `d9a381dd4607a928cd1315adef6431e239995bc1`; composition map recorded.
- LAB-092/#176: draft PR #177, head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`; locked classifier/receipt-guard slice now composed safely on PR #187.
- LAB-099: #184 / draft PR #186; PREPARED authority remains blocked on LAB-095.
- Retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173.

## Last completed step
LAB-086 was probed first in the executable runtime. Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` again failed before repository execution with `Could not resolve host: github.com`, exit 128. No LAB-086 PASS is claimed and the gate was not weakened.

Fallback then implemented the next smallest LAB-092 composition slice on PR #187. New `experiments/provider_generation_history/activation_schema_provenance.py` imports the shared immutable LAB-090 activation-schema contract and provides only deterministic migration-intent identity, exact locked schema/marker classification, `require_complete_activation_schema_provenance_locked(q)`, and `ActivationSchemaProvenanceReceiptGuardMixin`.

The classifier accepts the caller-owned SQLite connection and never opens, commits, rolls back, or closes another connection. COMPLETE requires exact activation table DDL + exact trigger DDL + exact CONFIRMED migration marker identity/payload digest. PREPARED/CONFIRMED provenance with missing/mismatched DDL and marker substitution fail closed. The mixin checks COMPLETE before delegating to the next receipt guard and contains no provider-history reference or replacement mechanism.

Branch commits:
- production locked classifier/guard: `1620b4e76b474f38e28f022002be486282dd10de`;
- focused regressions/current PR head: `6fd9300a9efab730cb86342cf63a43227ea45406`.

Published production blob was re-fetched from GitHub as `355bb4a32c54a9471a5b296deffa27af6f6ffd30`.

Focused tests added in `test_activation_schema_provenance_guard.py` cover COMPLETE while preserving the caller transaction, confirmed marker + missing DDL, confirmed marker + mismatched DDL, marker substitution, unmarked-schema receipt refusal before downstream guard, and COMPLETE delegation with the exact same connection object.

Exact branch pytest is still unavailable because the repository closure cannot be materialized into the executable filesystem. An isolated SQLite semantic probe executed in this run observed COMPLETE with the transaction still active; missing DDL, mismatched DDL, and marker substitution all failed closed with the transaction still active; unmarked exact DDL classified `DDL_INSTALLED_UNMARKED`; no DDL/marker classified `LEGACY_ABSENT`. A separate MRO probe confirmed fail-before-downstream and same-object delegation after COMPLETE. These are focused semantic probes only, not an exact-repository GREEN.

Durable evidence: `research/2026-09-15-lab092-locked-provenance-receipt-guard.md`, main commit `bc478a7a75aea3124adfc09ddd80d2ab71eed0bf`. Issue #176 and PR #187 were updated.

## Known failures / blockers
- LAB-086 complete real-ledger gate remains unexecuted. Current executable runtime cannot resolve `github.com`; no supported byte-preserving connector -> filesystem bridge is exposed.
- SQLite tests in this runtime must use a journal-capable filesystem; `/dev/shm` was previously observed working.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 focused manifest has authoritative exact content known for all 8/8 files, but the complete eight-file no-stub tree still needs same-run reconstruction/hash verification plus execution.
- LAB-096 whole-object replacement and public live-strategy alias leaks are source-patched on PR #187; exact repository behavioral GREEN remains pending.
- LAB-090 PR #175 remains source-incompatible with LAB-096 if its authority-heavy files are selected wholesale; carry activation behavior semantically onto PR #187.
- LAB-092 PR #177 remains source-incompatible with LAB-096 where it replaces provider-history post-construction or uses public history for locked authority.
- The shared immutable activation-schema prerequisite is present on PR #187, and the locked provenance classifier/receipt guard is now also present. Do not wire the guard into the default supported ledger until explicit LAB-092 migration/startup semantics and LAB-090 activation installation/fencing semantics are composed; otherwise legitimate pre-composition construction would be broken.
- LAB-092 receipt provenance must continue to classify COMPLETE through the supplied locked `q`; overriding `_store_receipt()` with an out-of-transaction precheck is forbidden because it reopens TOCTOU.
- Python reflection/private implementation access remains outside the supported/public API capability claim; process-grade isolation is not claimed.
- Final LAB-090/LAB-092/LAB-095/LAB-096 composition remains security-sensitive: preserve activation fencing, provenance fail-closed behavior, `CanonicalDatabaseBinding`, construction-bound provider-history strategy, least-capability public inspection, and same-transaction provenance guard before receipt persistence.

## Exact next action
LAB-086 first: execute the complete gate only from authoritative executable pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` if a supported byte-preserving materialization path can place exact repository bytes into an executable filesystem. Do not weaken or manually reserialize the large security-critical closure.

If LAB-086 remains transport-blocked, continue PR #187 with the next smallest LAB-092 startup/migration slice:
1. inspect the remainder of PR #177 `activation_schema_provenance.py` and its startup/recovery tests;
2. adapt explicit-migration-only handling for `LEGACY_ABSENT`, `DDL_INSTALLED_UNMARKED`, and `DDL_INSTALLED_PREPARED` onto PR #187 while preserving the new locked classifier;
3. construct any migration reservation surface with one-time canonical path binding and one-time exact `CoordinatorOnlyProviderHistory` installation only;
4. route every locked provider-history verification through private `_history()`; never recover mutation authority from public `provider_history`;
5. omit `_bind_live_provider_history_provenance()` and every post-construction `_provider_history` replacement;
6. add focused startup/migration fail-closed regressions before porting LAB-090 activation mutation/fencing behavior;
7. keep changes small/file-scoped enough for Contents API conflict checking and exact syntax/hash verification.

Composition order remains: PR #187 structural authority base -> shared `activation_schema.py` -> locked LAB-092 classifier/receipt guard -> explicit LAB-092 startup/migration semantics adapted to `_history()` and construction-bound strategy -> LAB-090 activation fencing semantics -> exact/downstream gates.

If a safe byte-preserving execution bridge becomes available, materialize exact PR #187 head `6fd9300a9efab730cb86342cf63a43227ea45406`, verify blobs, run `compileall`, activation-schema/provenance focused tests, LAB-096 capability/replacement/transaction-guard tests, LAB-095 DB-binding/no-stub gates under `TMPDIR=/dev/shm`, then compose LAB-092/LAB-090 and run retained LAB-081/LAB-090/LAB-092 downstream gates.

Never replace external authenticated authority with deterministic test vectors, caller-supplied nonce/digest, path hashes, or same-DB self-asserted identifiers.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; authoritative complete-gate pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`; exact executable gate pending.
- #180 / LAB-095 — IN_PROGRESS; path binding implemented; exact/downstream gates pending.
- #181 / LAB-096 — IN_PROGRESS/COMPOSED ON PR #187; strategy replacement + public live-strategy alias patched; receipt guard is same-transaction; exact/downstream validation pending.
- #169 / LAB-090 — retained draft; shared schema-definition extraction exists on PR #187; activation behavior still must compose semantically.
- #176 / LAB-092 — retained draft; shared schema + locked classifier/receipt guard now composed on PR #187; next work is explicit startup/migration semantics without history replacement.
- #167 / LAB-088, #170 / LAB-091 — retained draft gates pending.
- #178..185 / LAB-093..100 — remaining architecture/security follow-ups.
- #184 / LAB-099 — PREPARED authority waits on LAB-095 completion.
