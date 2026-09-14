# Current Lab State

Last updated: 2026-09-15

## Active objective
LAB-086 remains priority #1: finish the exact executable/security gate for asymmetric break-glass history migration. When byte-exact LAB-086 execution cannot be materialized safely, LAB-095/#180 plus composed LAB-096/#181 is the permitted fallback. LAB-099 PREPARED authority waits on LAB-095 completion.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165. Keep draft.
- LAB-095/#180 + LAB-096/#181: branch `lab-095-database-identity-red-intent`, draft PR #187, head `dfef95568179ce45e37beeaec69f86cdd86c4fca`. Keep draft.
- LAB-090/#169: draft PR #175, head `d9a381dd4607a928cd1315adef6431e239995bc1`; composition map recorded.
- LAB-092/#176: draft PR #177, head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`; exact LAB-096 conflict map recorded; shared activation schema prerequisite now exists on PR #187.
- LAB-099: #184 / draft PR #186; PREPARED authority remains blocked on LAB-095.
- Retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173.

## Last completed step
LAB-086 was probed first in the executable runtime. Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` again failed before repository execution with `Could not resolve host: github.com`, exit 128. No LAB-086 PASS is claimed and the complete gate was not weakened.

Fallback then completed the smallest prerequisite from the prior handoff. Conflict-checking PR #175 showed that immutable LAB-090 activation schema inputs were embedded directly in authority-heavy `supported.py`, while PR #187 intentionally uses the LAB-095/LAB-096 topology (`CanonicalDatabaseBinding`, construction-bound private `_provider_history`, private `_history()`, public least-capability inspection view, same-transaction receipt guard).

PR #187 now contains shared non-authority `experiments/provider_generation_history/activation_schema.py` with the exact LAB-090 activation table name/DDL, trigger name/DDL, and SQL normalization only. It contains no connection, ledger, provider, receipt, rotation, or activation mutation authority. Focused `test_activation_schema_contract.py` freezes exact equivalence to PR #175 and checks the helper surface for mutation calls.

Branch commits:
- production extraction `000b9edb1cc3b3af4422f498ab80660a677e814d`;
- focused test/current PR head `dfef95568179ce45e37beeaec69f86cdd86c4fca`.

Published blobs were re-fetched from GitHub:
- `activation_schema.py` `ec6fa59fc947f2d7812ede71617edd3edb511a68`;
- `test_activation_schema_contract.py` `57b5fdd658933b06dcde33fcb56284ef3fff6b22`.

A local reconstruction of the exact authored helper + focused test was executed with pytest and observed `2 passed in 0.08s`. This is focused helper validation only; full PR #187/downstream GREEN is not claimed.

Durable evidence: `research/2026-09-15-lab090-shared-activation-schema-extraction.md`, main commit `de583bcefac899e4d962cb2390535c04106391cd`. Issue/PR threads #169, #176, and #187 were updated.

## Known failures / blockers
- LAB-086 complete real-ledger gate remains unexecuted. Current executable runtime cannot resolve `github.com`; no supported byte-preserving connector -> filesystem bridge is exposed.
- SQLite tests in this runtime must use a journal-capable filesystem; `/dev/shm` was previously observed working.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 focused manifest has authoritative exact content known for all 8/8 files, but the complete eight-file no-stub tree still needs same-run reconstruction/hash verification plus execution.
- LAB-096 whole-object replacement and public live-strategy alias leaks are source-patched on PR #187; exact repository behavioral GREEN remains pending.
- LAB-090 PR #175 is source-incompatible with LAB-096 if its `supported.py`/`integration.py` are selected wholesale; carry activation behavior semantically onto PR #187 authority base.
- LAB-092 PR #177 is source-incompatible with LAB-096 until post-construction strategy replacement is removed and locked calls use `_history()`.
- The prior LAB-092 schema dependency blocker is removed: PR #187 now owns shared immutable activation schema definitions in a non-authority helper. LAB-092 classifier/guard composition can proceed next.
- LAB-092 receipt provenance must override `_guard_receipt_persistence_locked(q)` and classify COMPLETE through the supplied locked connection; overriding `_store_receipt()` with an out-of-transaction precheck is not acceptable because it reopens TOCTOU.
- LAB-092 `_reservation_surface()` one-time construction shape is compatible with canonical path binding/exact initial history installation; this does not authorize later strategy replacement.
- Python reflection/private implementation access remains outside the supported/public API capability claim; process-grade isolation is not claimed.
- Final LAB-090/LAB-092/LAB-095/LAB-096 composition remains security-sensitive: preserve activation fencing, provenance fail-closed behavior, `CanonicalDatabaseBinding`, construction-bound provider-history strategy, least-capability public inspection, and same-transaction provenance guard before receipt persistence.

## Exact next action
LAB-086 first: execute the complete gate only from authoritative executable pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` if a supported byte-preserving materialization path can place exact repository bytes into an executable filesystem. Do not weaken or manually reserialize the large security-critical closure.

If LAB-086 remains transport-blocked, continue PR #187 with the smallest LAB-092 composition slice:
1. inspect PR #177 `activation_schema_provenance.py` and isolate only the persisted activation-schema/provenance classifier semantics that depend on the newly shared `activation_schema.py`;
2. implement the classifier/guard on PR #187 so COMPLETE is checked through the exact `q` supplied to `_guard_receipt_persistence_locked(q)`; do not open a second SQLite connection;
3. route all locked provider-history verification through private `ledger._history()`; never recover mutation authority from public `provider_history`;
4. omit `_bind_live_provider_history_provenance()` and all post-construction replacement of `_provider_history`;
5. add focused fail-closed tests for missing/orphan/mismatched activation schema/provenance and receipt persistence refusal before porting LAB-090 activation mutation/fencing behavior;
6. keep changes small/file-scoped enough for Contents API conflict checking and exact syntax/hash verification.

Composition order remains: PR #187 structural authority base -> shared `activation_schema.py` -> LAB-092 provenance semantics (locked COMPLETE guard through supplied `q`, `_history()` locked calls, no strategy replacement) -> LAB-090 activation fencing semantics. Do not accept PR #175/#177 whole-file conflict resolution that reopens public/internal authority.

If a safe byte-preserving execution bridge becomes available, materialize exact PR #187 head `dfef95568179ce45e37beeaec69f86cdd86c4fca`, verify blobs, run `compileall`, activation-schema contract test, LAB-096 capability/replacement/transaction-guard tests, LAB-095 DB-binding/no-stub gates under `TMPDIR=/dev/shm`, then compose LAB-092 and LAB-090 and run retained LAB-081/LAB-090/LAB-092 downstream gates.

Never replace external authenticated authority with deterministic test vectors, caller-supplied nonce/digest, path hashes, or same-DB self-asserted identifiers.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; authoritative complete-gate pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`; exact executable gate pending.
- #180 / LAB-095 — IN_PROGRESS; path binding implemented; exact/downstream gates pending.
- #181 / LAB-096 — IN_PROGRESS/COMPOSED ON PR #187; strategy replacement + public live-strategy alias patched; receipt guard is same-transaction; exact/downstream validation pending.
- #169 / LAB-090 — retained draft; shared schema-definition extraction now exists on PR #187; activation behavior still must compose semantically.
- #176 / LAB-092 — retained draft; schema prerequisite removed; next work is minimal classifier/locked receipt guard on PR #187 without history replacement.
- #167 / LAB-088, #170 / LAB-091 — retained draft gates pending.
- #178..185 / LAB-093..100 — remaining architecture/security follow-ups.
- #184 / LAB-099 — PREPARED authority waits on LAB-095 completion.
