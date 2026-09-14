# Current Lab State

Last updated: 2026-09-14

## Active objective
LAB-086 remains priority #1: finish the exact executable/security gate for asymmetric break-glass history migration. When byte-exact LAB-086 execution cannot be materialized safely, LAB-095/#180 plus composed LAB-096/#181 is the permitted fallback. LAB-099 PREPARED authority waits on LAB-095 completion.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165. Keep draft.
- LAB-095/#180 + LAB-096/#181: branch `lab-095-database-identity-red-intent`, draft PR #187, head `1c77a2ab361e76cb3c89bfb0918cea130899716d`. Keep draft.
- LAB-090/#169: draft PR #175, head `d9a381dd4607a928cd1315adef6431e239995bc1`; composition map recorded.
- LAB-092/#176: draft PR #177, head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`; exact LAB-096 call-site conflict map now recorded.
- LAB-099: #184 / draft PR #186; PREPARED authority remains blocked on LAB-095.
- Retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173.

## Last completed step
LAB-086 was probed first in the executable runtime. Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` again failed before repository execution with `Could not resolve host: github.com`, exit 128. No LAB-086 PASS is claimed and the complete gate was not weakened.

Fallback work completed the requested LAB-092 call-site audit and produced one combined LAB-090 + LAB-092 + LAB-095/LAB-096 implementation order in `research/2026-09-14-lab092-lab090-lab096-composition-order.md`, main commit `1846af3ea66f80f8089a8ff6cbb201004463629f`.

Concrete LAB-092 conflicts on PR #177:
- `_reservation_surface()` manually assembles ledger/history authority;
- `_verify_confirmation_authority()` and `_install_and_reserve_prepared()` call locked verification through public `ledger.provider_history`;
- `_bind_live_provider_history_provenance()` replaces the live provider-history strategy after supported construction.

The last item directly violates LAB-096. Final composition must retain PR #187 as structural base: canonical DB binding, exact construction-bound private `CoordinatorOnlyProviderHistory`, public inspection-only view, and internal `_history()` dispatch.

A minimal safe seam was implemented directly on PR #187 through the normal Contents API after conflict-checking `supported.py` blob `70c7c7c2515129375de188e575fa04d2c20014f8`:
- new private ledger-owned `_store_receipt(receipt)` delegates to `self._history().store_receipt(receipt)`;
- `_reauthenticate()` now persists through `_store_receipt()`.

This lets LAB-092 preserve post-construction provenance-loss receipt fail-closed behavior by overriding `_store_receipt()` on the owning ledger instead of replacing the provider-history strategy. PR #187 commit `1c77a2ab361e76cb3c89bfb0918cea130899716d`; published blob `51cb036c555ec4ac4365767e97e6b8675e4ea26f`. The exact authored replacement compiled locally with `python -m py_compile`; local `git hash-object` matched the published blob and post-write refetch returned the same SHA. No full repository behavioral GREEN is claimed.

Comments were added to #176, PR #177, and PR #187.

## Known failures / blockers
- LAB-086 complete real-ledger gate remains unexecuted. Current executable runtime cannot resolve `github.com`; no supported byte-preserving connector -> filesystem bridge is exposed.
- SQLite tests in this runtime must use a journal-capable filesystem; `/dev/shm` was previously observed working.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 focused manifest has authoritative exact content known for all 8/8 files, but the complete eight-file no-stub tree still needs same-run reconstruction/hash verification plus execution.
- LAB-096 whole-object replacement and public live-strategy alias leaks are source-patched on PR #187; exact repository behavioral GREEN remains pending.
- LAB-090 PR #175 is source-incompatible with LAB-096 if its `supported.py`/`integration.py` are selected wholesale; carry activation behavior semantically onto PR #187 authority base.
- LAB-092 PR #177 is source-incompatible with LAB-096 until post-construction strategy replacement is removed and locked calls use `_history()`; the durable adaptation map now specifies the replacement.
- LAB-092 explicit migration `_reservation_surface()` still needs composed implementation review: constructor bypass may remain only as a tightly scoped one-time migration surface that establishes canonical path + exact private history once and never rebinds later.
- Python reflection/private implementation access remains outside the supported/public API capability claim; process-grade isolation is not claimed.
- Final LAB-090/LAB-092/LAB-095/LAB-096 composition remains security-sensitive: preserve activation fencing, provenance fail-closed behavior, `CanonicalDatabaseBinding`, construction-bound provider-history strategy, least-capability public inspection, and last-moment provenance guard before receipt persistence.

## Exact next action
LAB-086 first: execute the complete gate only from authoritative executable pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` if a supported byte-preserving materialization path can place exact repository bytes into an executable filesystem. Do not weaken or manually reserialize the large security-critical closure.

If LAB-086 remains transport-blocked, continue the fallback on PR #187 with the smallest safe LAB-092 compatibility slice:
1. add a focused regression proving a subclass can block `_store_receipt()` immediately before persistence without receiving/replacing the private history strategy;
2. audit whether that regression can be expressed as a small file-scoped test without requiring the unmaterialized full branch closure;
3. if safe, publish it through Contents API and verify exact blob/syntax;
4. otherwise stop at durable design evidence and audit LAB-092 `_reservation_surface()` one-time construction semantics against `CanonicalDatabaseBinding` and the exact-type history setter.

When composing LAB-092 proper, use this order: PR #187 structural authority base -> LAB-092 provenance semantics (`_history()` locked calls, no strategy replacement, ledger-owned `_store_receipt()` provenance guard) -> LAB-090 activation fencing semantics. Do not accept PR #175/#177 whole-file conflict resolution that reopens public/internal authority.

If a safe byte-preserving execution bridge becomes available, materialize exact PR #187 head `1c77a2ab361e76cb3c89bfb0918cea130899716d`, verify blobs, run `compileall`, LAB-096 capability/replacement tests, LAB-095 DB-binding/no-stub gates under `TMPDIR=/dev/shm`, then compose LAB-092 and LAB-090 and run retained LAB-081/LAB-090/LAB-092 downstream gates.

Never replace external authenticated authority with deterministic test vectors, caller-supplied nonce/digest, path hashes, or same-DB self-asserted identifiers.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; authoritative complete-gate pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`; exact executable gate pending.
- #180 / LAB-095 — IN_PROGRESS; path binding implemented; exact/downstream gates pending.
- #181 / LAB-096 — IN_PROGRESS/COMPOSED ON PR #187; strategy replacement + public live-strategy alias patched; private receipt-persistence hook added for safe LAB-092 composition; exact/downstream validation pending.
- #169 / LAB-090 — retained draft; exact LAB-096 conflict map recorded, composed implementation pending.
- #176 / LAB-092 — retained draft; exact call-site conflict map + combined composition order recorded; composed implementation pending.
- #167 / LAB-088, #170 / LAB-091 — retained draft gates pending.
- #178..185 / LAB-093..100 — remaining architecture/security follow-ups.
- #184 / LAB-099 — PREPARED authority waits on LAB-095 completion.
