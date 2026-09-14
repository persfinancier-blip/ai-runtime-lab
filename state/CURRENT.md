# Current Lab State

Last updated: 2026-09-14

## Active objective
LAB-086 remains priority #1: finish the exact executable/security gate for asymmetric break-glass history migration. When byte-exact LAB-086 execution cannot be materialized safely, LAB-095/#180 plus composed LAB-096/#181 is the permitted fallback. LAB-099 PREPARED authority waits on LAB-095 completion.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165. Keep draft.
- LAB-095/#180 + LAB-096/#181: branch `lab-095-database-identity-red-intent`, draft PR #187, head `c66961c71a962ce69fb8d506c88c450c8291b44b`. Keep draft.
- LAB-090/#169: draft PR #175, head `d9a381dd4607a928cd1315adef6431e239995bc1`; composition map recorded.
- LAB-092/#176: draft PR #177, head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`; exact LAB-096 conflict map recorded.
- LAB-099: #184 / draft PR #186; PREPARED authority remains blocked on LAB-095.
- Retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173.

## Last completed step
LAB-086 was probed first in the executable runtime. Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` again failed before repository execution with `Could not resolve host: github.com`, exit 128. No LAB-086 PASS is claimed and the complete gate was not weakened.

Fallback work found and fixed a TOCTOU weakness in the prior LAB-092 receipt-provenance seam on PR #187. A subclass-level provenance check followed by `super()._store_receipt()` was not sufficient because the check and provider-history receipt persistence occurred in separate SQLite transactions.

PR #187 now makes receipt persistence ledger-owned and transaction-atomic:
- `_store_receipt()` opens one `BEGIN IMMEDIATE`;
- `_guard_receipt_persistence_locked(q)` executes first inside that transaction;
- private construction-bound history verifies the receipt through `_verify_receipt_locked(q, receipt)` on the same connection;
- idempotency/substitution comparison and INSERT occur before the same commit;
- guard failure rolls back before history verification or mutation.

Production commit: `7400348c670b0bdcb52547a871b6ee71eb61544f`; focused regression/current PR head: `c66961c71a962ce69fb8d506c88c450c8291b44b`.
Published blobs exactly matched local `git hash-object`:
- `supported.py` `c478f7e8676b09a2b891f1e1eafd36e0b77224ca`;
- `test_store_receipt_guard_hook.py` `8a06ed8bcea2f85ff85c6b4fe6395b467c714c0b`.
Both passed local `py_compile`. An isolated execution of the exact authored bytes with inert import stubs ran the focused regression 2/2 PASS: successful guard/verify/select/insert/commit used one identical connection, and provenance loss produced rollback before verification/insert.

Durable evidence: `research/2026-09-14-lab096-transaction-atomic-receipt-provenance-guard.md`, main commit `869d3a3cb0c52aefd9c2fdf5754dfef044bdf46e`. Comments added to #181, #176, and PR #187.

## Known failures / blockers
- LAB-086 complete real-ledger gate remains unexecuted. Current executable runtime cannot resolve `github.com`; no supported byte-preserving connector -> filesystem bridge is exposed.
- SQLite tests in this runtime must use a journal-capable filesystem; `/dev/shm` was previously observed working.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 focused manifest has authoritative exact content known for all 8/8 files, but the complete eight-file no-stub tree still needs same-run reconstruction/hash verification plus execution.
- LAB-096 whole-object replacement and public live-strategy alias leaks are source-patched on PR #187; exact repository behavioral GREEN remains pending.
- LAB-090 PR #175 is source-incompatible with LAB-096 if its `supported.py`/`integration.py` are selected wholesale; carry activation behavior semantically onto PR #187 authority base.
- LAB-092 PR #177 is source-incompatible with LAB-096 until post-construction strategy replacement is removed and locked calls use `_history()`.
- LAB-092 receipt provenance must override `_guard_receipt_persistence_locked(q)` and classify COMPLETE through the supplied locked connection; overriding `_store_receipt()` with an out-of-transaction precheck is no longer acceptable because it reopens TOCTOU.
- LAB-092 `_reservation_surface()` one-time construction shape is audited as compatible with canonical path binding/exact initial history installation; this does not authorize later strategy replacement.
- Python reflection/private implementation access remains outside the supported/public API capability claim; process-grade isolation is not claimed.
- Final LAB-090/LAB-092/LAB-095/LAB-096 composition remains security-sensitive: preserve activation fencing, provenance fail-closed behavior, `CanonicalDatabaseBinding`, construction-bound provider-history strategy, least-capability public inspection, and same-transaction provenance guard before receipt persistence.

## Exact next action
LAB-086 first: execute the complete gate only from authoritative executable pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` if a supported byte-preserving materialization path can place exact repository bytes into an executable filesystem. Do not weaken or manually reserialize the large security-critical closure.

If LAB-086 remains transport-blocked, continue the PR #187 fallback with the smallest LAB-092 composed implementation slice:
1. add a PR-#187-compatible provenance layer that overrides `_guard_receipt_persistence_locked(q)` and classifies exact activation-schema COMPLETE using that supplied transaction connection;
2. route LAB-092 locked provider-history verification through private `_history()`;
3. do **not** add `_bind_live_provider_history_provenance()` or any post-construction history replacement;
4. preserve `_reservation_surface()` only as a tightly scoped one-time migration constructor binding canonical path + exact private history once;
5. keep the slice small/file-scoped enough for Contents API conflict checking plus exact syntax/hash verification. If exact LAB-090 activation constants/DDL dependencies make the slice non-local, stop at a concrete file/line patch map rather than copying a large security-critical file.

When composing LAB-092 proper, use this order: PR #187 structural authority base -> LAB-092 provenance semantics (locked COMPLETE guard through supplied `q`, `_history()` locked calls, no strategy replacement) -> LAB-090 activation fencing semantics. Do not accept PR #175/#177 whole-file conflict resolution that reopens public/internal authority.

If a safe byte-preserving execution bridge becomes available, materialize exact PR #187 head `c66961c71a962ce69fb8d506c88c450c8291b44b`, verify blobs, run `compileall`, LAB-096 capability/replacement/transaction-guard tests, LAB-095 DB-binding/no-stub gates under `TMPDIR=/dev/shm`, then compose LAB-092 and LAB-090 and run retained LAB-081/LAB-090/LAB-092 downstream gates.

Never replace external authenticated authority with deterministic test vectors, caller-supplied nonce/digest, path hashes, or same-DB self-asserted identifiers.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; authoritative complete-gate pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`; exact executable gate pending.
- #180 / LAB-095 — IN_PROGRESS; path binding implemented; exact/downstream gates pending.
- #181 / LAB-096 — IN_PROGRESS/COMPOSED ON PR #187; strategy replacement + public live-strategy alias patched; receipt guard is now same-transaction; exact/downstream validation pending.
- #169 / LAB-090 — retained draft; exact LAB-096 conflict map recorded, composed implementation pending.
- #176 / LAB-092 — retained draft; one-time reservation-surface construction audited compatible; post-construction replacement/locked-call composition still pending; receipt provenance must use locked guard hook.
- #167 / LAB-088, #170 / LAB-091 — retained draft gates pending.
- #178..185 / LAB-093..100 — remaining architecture/security follow-ups.
- #184 / LAB-099 — PREPARED authority waits on LAB-095 completion.
