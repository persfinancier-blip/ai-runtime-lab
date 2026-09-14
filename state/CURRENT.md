# Current Lab State

Last updated: 2026-09-14

## Active objective
LAB-086 remains priority #1: finish the exact executable/security gate for asymmetric break-glass history migration. When byte-exact LAB-086 execution cannot be materialized safely, LAB-095/#180 plus composed LAB-096/#181 is the permitted fallback. LAB-099 PREPARED authority waits on LAB-095 completion.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165. Keep draft.
- LAB-095/#180 + LAB-096/#181: branch `lab-095-database-identity-red-intent`, draft PR #187, head `0a14492c280c0fa6ed60ae20c8ea9f04144ade7a`. Keep draft.
- LAB-090/#169: draft PR #175, head `d9a381dd4607a928cd1315adef6431e239995bc1`; exact LAB-096 composition map now recorded.
- LAB-092/#176: draft PR #177; known composition conflict with LAB-096 construction-bound history strategy remains.
- LAB-099: #184 / draft PR #186; PREPARED authority remains blocked on LAB-095.
- Retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173.

## Last completed step
LAB-086 was probed first in the executable runtime. Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` again failed before repository execution with `Could not resolve host: github.com`, exit 128. No LAB-086 PASS is claimed and the complete gate was not weakened.

Fallback work continued by auditing LAB-090 PR #175 against the LAB-095/LAB-096 capability contract already present on PR #187. The exact conflict-resolution map is now durable in `research/2026-09-14-lab090-lab096-history-capability-composition-map.md`, main commit `717458b95b242c2e09b6de9e0844e1b90562d96f`.

Key result: final composition must use PR #187 as the provider-history structural base. Preserve `CoordinatorOnlyProviderHistory(CanonicalDatabaseBinding, IntegratedProviderHistory)`, the construction-bound private `_provider_history`, public `ProviderHistoryInspectionView`, and inherited `_history()` dispatch. Carry LAB-090 activation behavior across semantically rather than accepting its older whole files.

LAB-090 call sites classified:
- internal `current()` decisions in `_recover_pending_activation()`, `_verify_activation_records()`, activation retry handling, and `_reauthenticate()` -> use `self._history().current()`;
- SQL rotation -> mandatory `self._history()._rotate_locked(...)`;
- locked receipt load -> mandatory `self._history()._load_receipt_locked(...)`;
- receipt persistence -> mandatory `self._history().store_receipt(...)`;
- preserve LAB-090's extra runtime-vs-durable generation equality check added to `reserve()` while retaining PR #187's `_history()`-based `integration.py`.

Do not change LAB-090 activation ordering while resolving conflicts: provider PREPARED fence -> SQL generation/activation commit -> provider COMMITTED_FENCED -> durable exact-ticket SQL acknowledgement -> exact-ticket release. Restart fail-closed behavior remains required.

Issue/PR comments were added to #169, PR #175, and PR #187 with this composition result.

## Known failures / blockers
- LAB-086 complete real-ledger gate remains unexecuted. Current executable runtime cannot resolve `github.com`; no supported byte-preserving connector -> filesystem bridge is exposed.
- SQLite tests in this runtime must use a journal-capable filesystem; `/dev/shm` was previously observed working.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 focused manifest has authoritative exact content known for all 8/8 files, but the complete eight-file no-stub tree still needs same-run reconstruction/hash verification plus execution.
- LAB-096 whole-object replacement and public live-strategy alias leaks are source-patched on PR #187; exact repository behavioral GREEN remains pending.
- LAB-090 PR #175 is source-incompatible with LAB-096 if its `supported.py`/`integration.py` are selected wholesale; the durable map now defines the required semantic composition.
- LAB-092 PR #177 is source-incompatible with LAB-096 until its construction/replacement helpers are conflict-resolved without replacing the live history strategy.
- Python reflection/private implementation access remains outside the supported/public API capability claim; process-grade isolation is not claimed.
- Final LAB-090/LAB-092/LAB-095/LAB-096 composition remains security-sensitive: preserve activation fencing, provenance fail-closed behavior, `CanonicalDatabaseBinding`, construction-bound provider-history strategy, and least-capability public inspection.

## Exact next action
LAB-086 first: execute the complete gate only from authoritative executable pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` if a supported byte-preserving materialization path can place exact repository bytes into an executable filesystem. Do not weaken or manually reserialize the large security-critical closure.

If LAB-086 remains transport-blocked, continue the fallback by auditing LAB-092 PR #177 at the same call-site granularity and produce one combined LAB-090 + LAB-092 + LAB-095/LAB-096 implementation order. The implementation order must eliminate LAB-092 post-construction history replacement, move its locked verification to `_history()`/narrower internal helpers, preserve provenance-loss receipt fail-closed behavior, then layer LAB-090 activation fencing without reopening public/internal authority leaks.

After that audit, if the change can be expressed as a small conflict-checked file-scoped patch on PR #187, apply it through the normal Contents API. Do not perform a large security-critical whole-file synthesis through Contents API without exact conflict evidence.

If a safe byte-preserving execution bridge becomes available, materialize exact PR #187 head, run `compileall`, `test_provider_history_capability_surface.py`, `test_database_path_binding.py`, then the retained no-stub LAB-095 recovery/confirmed-finalize/locked-custody suite under `TMPDIR=/dev/shm`. After that run the conflict-resolved LAB-081/LAB-090/LAB-092 downstream gates.

Never replace external authenticated authority with deterministic test vectors, caller-supplied nonce/digest, path hashes, or same-DB self-asserted identifiers.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; authoritative complete-gate pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`; exact executable gate pending.
- #180 / LAB-095 — IN_PROGRESS; path binding implemented; exact/downstream gates pending.
- #181 / LAB-096 — IN_PROGRESS/COMPOSED ON PR #187; strategy replacement + public live-strategy alias patched; exact/downstream validation pending.
- #169 / LAB-090 — retained draft; exact LAB-096 conflict map recorded, composed implementation pending.
- #176 / LAB-092 — retained draft with explicit LAB-096 composition conflict; next detailed call-site audit target.
- #167 / LAB-088, #170 / LAB-091 — retained draft gates pending.
- #178..185 / LAB-093..100 — remaining architecture/security follow-ups.
- #184 / LAB-099 — PREPARED authority waits on LAB-095 completion.
