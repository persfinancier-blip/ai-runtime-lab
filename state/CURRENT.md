# Current Lab State

Last updated: 2026-09-14

## Active objective
LAB-086 remains priority #1: finish the exact executable/security gate for asymmetric break-glass history migration. When byte-exact LAB-086 execution cannot be materialized safely, LAB-095/#180 plus composed LAB-096/#181 is the permitted fallback. LAB-099 PREPARED authority waits on LAB-095 completion.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165. Keep draft.
- LAB-095/#180 + LAB-096/#181: branch `lab-095-database-identity-red-intent`, draft PR #187, head `fe2c39e964d3abd5b4028053b0828febe54307ba`. Keep draft.
- LAB-090/#169: draft PR #175, head `d9a381dd4607a928cd1315adef6431e239995bc1`; composition map recorded.
- LAB-092/#176: draft PR #177, head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`; exact LAB-096 conflict map recorded.
- LAB-099: #184 / draft PR #186; PREPARED authority remains blocked on LAB-095.
- Retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173.

## Last completed step
LAB-086 was probed first in the executable runtime. Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` again failed before repository execution with `Could not resolve host: github.com`, exit 128. No LAB-086 PASS is claimed and the complete gate was not weakened.

Fallback work advanced PR #187 with a focused regression for the ledger-owned `_store_receipt()` compatibility seam:
- new `experiments/provider_generation_history/tests/test_store_receipt_guard_hook.py`;
- branch commit `fe2c39e964d3abd5b4028053b0828febe54307ba`;
- exact blob `d00af7540cc23410859fbb62f34bffd349020ba8`;
- local `python -m py_compile` PASS;
- local `git hash-object` exactly matched the post-publication GitHub blob.

The regression proves a LAB-092-style subclass can fail closed immediately before receipt persistence without being handed, exposing, or replacing the private provider-history strategy: the test overrides `_history()` to raise if touched and confirms the provenance guard raises first.

LAB-092 PR #177 `_reservation_surface()` was separately audited against PR #187. Its `object.__new__` + first manual `path` assignments are compatible with `CanonicalDatabaseBinding`: each first assignment canonicalizes/binds once, later rebinding is rejected, and the exact `CoordinatorOnlyProviderHistory` setter accepts the one initial exact-type strategy. The already-published `test_database_binding_object_new_surface.py` covers this path shape. The remaining incompatibility is post-construction `_bind_live_provider_history_provenance()` strategy replacement plus locked calls through public `ledger.provider_history`.

Durable evidence: `research/2026-09-14-lab096-receipt-guard-seam-and-lab092-reservation-surface-audit.md`, main commit `0bb74bcc746c9866861499e0ea39b7b2c38cbb72`. Comments added to #181 and PR #187.

## Known failures / blockers
- LAB-086 complete real-ledger gate remains unexecuted. Current executable runtime cannot resolve `github.com`; no supported byte-preserving connector -> filesystem bridge is exposed.
- SQLite tests in this runtime must use a journal-capable filesystem; `/dev/shm` was previously observed working.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 focused manifest has authoritative exact content known for all 8/8 files, but the complete eight-file no-stub tree still needs same-run reconstruction/hash verification plus execution.
- LAB-096 whole-object replacement and public live-strategy alias leaks are source-patched on PR #187; exact repository behavioral GREEN remains pending.
- LAB-090 PR #175 is source-incompatible with LAB-096 if its `supported.py`/`integration.py` are selected wholesale; carry activation behavior semantically onto PR #187 authority base.
- LAB-092 PR #177 is source-incompatible with LAB-096 until post-construction strategy replacement is removed and locked calls use `_history()`.
- LAB-092 `_reservation_surface()` one-time construction shape is now audited as compatible with canonical path binding/exact initial history installation; this does not authorize later strategy replacement.
- Python reflection/private implementation access remains outside the supported/public API capability claim; process-grade isolation is not claimed.
- Final LAB-090/LAB-092/LAB-095/LAB-096 composition remains security-sensitive: preserve activation fencing, provenance fail-closed behavior, `CanonicalDatabaseBinding`, construction-bound provider-history strategy, least-capability public inspection, and last-moment provenance guard before receipt persistence.

## Exact next action
LAB-086 first: execute the complete gate only from authoritative executable pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` if a supported byte-preserving materialization path can place exact repository bytes into an executable filesystem. Do not weaken or manually reserialize the large security-critical closure.

If LAB-086 remains transport-blocked, continue the PR #187 fallback by designing the smallest LAB-092 composed implementation slice rather than another audit-only note:
1. add a PR-#187-compatible provenance subclass that overrides ledger-owned `_store_receipt()` and checks COMPLETE immediately before persistence;
2. route the minimal LAB-092 locked verification call(s) through private `_history()`;
3. do **not** add `_bind_live_provider_history_provenance()` or any post-construction history replacement;
4. preserve `_reservation_surface()` only as a tightly scoped one-time migration constructor that binds canonical path + exact private history once;
5. publish only if the slice remains small/file-scoped enough for Contents API conflict checking and exact syntax/hash verification; otherwise stop at a concrete patch map rather than reserializing a large security-critical file.

When composing LAB-092 proper, use this order: PR #187 structural authority base -> LAB-092 provenance semantics (`_history()` locked calls, no strategy replacement, ledger-owned `_store_receipt()` provenance guard) -> LAB-090 activation fencing semantics. Do not accept PR #175/#177 whole-file conflict resolution that reopens public/internal authority.

If a safe byte-preserving execution bridge becomes available, materialize exact PR #187 head `fe2c39e964d3abd5b4028053b0828febe54307ba`, verify blobs, run `compileall`, LAB-096 capability/replacement/receipt-guard tests, LAB-095 DB-binding/no-stub gates under `TMPDIR=/dev/shm`, then compose LAB-092 and LAB-090 and run retained LAB-081/LAB-090/LAB-092 downstream gates.

Never replace external authenticated authority with deterministic test vectors, caller-supplied nonce/digest, path hashes, or same-DB self-asserted identifiers.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; authoritative complete-gate pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`; exact executable gate pending.
- #180 / LAB-095 — IN_PROGRESS; path binding implemented; exact/downstream gates pending.
- #181 / LAB-096 — IN_PROGRESS/COMPOSED ON PR #187; strategy replacement + public live-strategy alias patched; receipt guard seam regression added; exact/downstream validation pending.
- #169 / LAB-090 — retained draft; exact LAB-096 conflict map recorded, composed implementation pending.
- #176 / LAB-092 — retained draft; one-time reservation-surface construction audited compatible; post-construction replacement/locked-call composition still pending.
- #167 / LAB-088, #170 / LAB-091 — retained draft gates pending.
- #178..185 / LAB-093..100 — remaining architecture/security follow-ups.
- #184 / LAB-099 — PREPARED authority waits on LAB-095 completion.
