# Current Lab State

Last updated: 2026-09-15

## Active objective
LAB-086 remains priority #1: finish the exact executable/security gate for asymmetric break-glass history migration. When byte-exact LAB-086 execution cannot be materialized safely, LAB-095/#180 plus composed LAB-096/#181 is the permitted fallback. LAB-099 PREPARED authority waits on LAB-095 completion.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165. Keep draft.
- LAB-095/#180 + LAB-096/#181: branch `lab-095-database-identity-red-intent`, draft PR #187, head `c66961c71a962ce69fb8d506c88c450c8291b44b`. Keep draft.
- LAB-090/#169: draft PR #175, head `d9a381dd4607a928cd1315adef6431e239995bc1`; composition map recorded.
- LAB-092/#176: draft PR #177, head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`; exact LAB-096 conflict map + minimal PR-#187 composition patch map recorded.
- LAB-099: #184 / draft PR #186; PREPARED authority remains blocked on LAB-095.
- Retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173.

## Last completed step
LAB-086 was probed first in the executable runtime. Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` again failed before repository execution with `Could not resolve host: github.com`, exit 128. No LAB-086 PASS is claimed and the complete gate was not weakened.

Fallback work then re-read the exact PR #187 authority base, PR #177 LAB-092 provenance module, and PR #175 LAB-090 activation DDL/constants. The requested smallest LAB-092 implementation slice is currently non-local: PR #177's classifier imports exact activation table/trigger names, DDL, and SQL normalization from LAB-090 `supported.py`, while PR #187 intentionally does not yet contain LAB-090. Copying the LAB-092 module now would either duplicate schema authority or force wholesale LAB-090 `supported.py` conflict resolution that reopens the public/live provider-history topology already removed by LAB-095/LAB-096.

A concrete conflict-safe patch map was therefore recorded instead of copying a large security-critical closure. It freezes these composition rules:
- PR #187 remains the structural authority base (`CanonicalDatabaseBinding`, construction-bound private `_provider_history`, public inspection view, `_history()`, same-transaction receipt guard);
- LAB-090 activation schema constants/DDL + `_normalized_sql` should first move to one shared schema-definition-only production owner used by LAB-090 and LAB-092;
- LAB-092 locked durable-history checks must use `ledger._history()`;
- LAB-092 receipt provenance must override `_guard_receipt_persistence_locked(q)` and classify through that supplied transaction connection, not via a second connection;
- `_reservation_surface()` is allowed only as first/one-time canonical path + exact private history installation on a fresh object;
- `_bind_live_provider_history_provenance()` and all post-construction history replacement remain forbidden;
- LAB-090 behavior must later be ported semantically while preserving PREPARED -> SQL commit -> COMMITTED_FENCED -> durable acknowledgement -> release ordering.

Durable evidence: `research/2026-09-15-lab092-pr187-minimal-composition-patch-map.md`, main commit `c3052fe1ff7422dd25dd8a75e216a94b9c18d7b9`.

## Known failures / blockers
- LAB-086 complete real-ledger gate remains unexecuted. Current executable runtime cannot resolve `github.com`; no supported byte-preserving connector -> filesystem bridge is exposed.
- SQLite tests in this runtime must use a journal-capable filesystem; `/dev/shm` was previously observed working.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 focused manifest has authoritative exact content known for all 8/8 files, but the complete eight-file no-stub tree still needs same-run reconstruction/hash verification plus execution.
- LAB-096 whole-object replacement and public live-strategy alias leaks are source-patched on PR #187; exact repository behavioral GREEN remains pending.
- LAB-090 PR #175 is source-incompatible with LAB-096 if its `supported.py`/`integration.py` are selected wholesale; carry activation behavior semantically onto PR #187 authority base.
- LAB-092 PR #177 is source-incompatible with LAB-096 until post-construction strategy replacement is removed and locked calls use `_history()`.
- LAB-092 cannot yet be safely copied as a local one-file PR-#187 slice because its exact schema classifier depends on LAB-090 activation constants/DDL. First extract those immutable schema definitions to a shared non-authority production module; do not duplicate them.
- LAB-092 receipt provenance must override `_guard_receipt_persistence_locked(q)` and classify COMPLETE through the supplied locked connection; overriding `_store_receipt()` with an out-of-transaction precheck is not acceptable because it reopens TOCTOU.
- LAB-092 `_reservation_surface()` one-time construction shape is compatible with canonical path binding/exact initial history installation; this does not authorize later strategy replacement.
- Python reflection/private implementation access remains outside the supported/public API capability claim; process-grade isolation is not claimed.
- Final LAB-090/LAB-092/LAB-095/LAB-096 composition remains security-sensitive: preserve activation fencing, provenance fail-closed behavior, `CanonicalDatabaseBinding`, construction-bound provider-history strategy, least-capability public inspection, and same-transaction provenance guard before receipt persistence.

## Exact next action
LAB-086 first: execute the complete gate only from authoritative executable pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` if a supported byte-preserving materialization path can place exact repository bytes into an executable filesystem. Do not weaken or manually reserialize the large security-critical closure.

If LAB-086 remains transport-blocked, continue PR #187 fallback with the smallest prerequisite to LAB-092 composition:
1. extract only LAB-090 immutable activation schema definitions (`_ACTIVATION_TABLE_NAME`, `_ACTIVATION_TABLE_SQL`, `_ACTIVATION_TRIGGER_NAME`, `_ACTIVATION_TRIGGER_SQL`, `_normalized_sql`) into one shared schema-definition-only production module, without moving mutation/rotation authority;
2. conflict-check the extraction against PR #187 and PR #175 exact source before writing;
3. add focused tests proving the extracted definitions are byte/normalization-equivalent to current LAB-090 authority and contain no ledger/provider mutation surface;
4. after that extraction exists, add the small LAB-092 classifier/guard layer on PR #187 using `_guard_receipt_persistence_locked(q)` + `_history()` and no strategy replacement;
5. keep each change small/file-scoped enough for Contents API conflict checking and exact syntax/hash verification.

When composing LAB-092 proper, use this order: PR #187 structural authority base -> shared LAB-090 schema-definition helper -> LAB-092 provenance semantics (locked COMPLETE guard through supplied `q`, `_history()` locked calls, no strategy replacement) -> LAB-090 activation fencing semantics. Do not accept PR #175/#177 whole-file conflict resolution that reopens public/internal authority.

If a safe byte-preserving execution bridge becomes available, materialize exact PR #187 head `c66961c71a962ce69fb8d506c88c450c8291b44b`, verify blobs, run `compileall`, LAB-096 capability/replacement/transaction-guard tests, LAB-095 DB-binding/no-stub gates under `TMPDIR=/dev/shm`, then compose LAB-092 and LAB-090 and run retained LAB-081/LAB-090/LAB-092 downstream gates.

Never replace external authenticated authority with deterministic test vectors, caller-supplied nonce/digest, path hashes, or same-DB self-asserted identifiers.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; authoritative complete-gate pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`; exact executable gate pending.
- #180 / LAB-095 — IN_PROGRESS; path binding implemented; exact/downstream gates pending.
- #181 / LAB-096 — IN_PROGRESS/COMPOSED ON PR #187; strategy replacement + public live-strategy alias patched; receipt guard is same-transaction; exact/downstream validation pending.
- #169 / LAB-090 — retained draft; activation behavior must compose semantically; shared schema-definition extraction is now the next prerequisite.
- #176 / LAB-092 — retained draft; exact composition patch map recorded; wait for shared LAB-090 schema-definition owner, then compose locked classifier/guard without history replacement.
- #167 / LAB-088, #170 / LAB-091 — retained draft gates pending.
- #178..185 / LAB-093..100 — remaining architecture/security follow-ups.
- #184 / LAB-099 — PREPARED authority waits on LAB-095 completion.
