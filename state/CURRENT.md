# Current Lab State

Last updated: 2026-09-14

## Active objective
LAB-086 remains priority #1: finish the exact executable/security gate for asymmetric break-glass history migration. When byte-exact LAB-086 execution cannot be materialized safely, LAB-095/#180 plus composed LAB-096/#181 is the permitted fallback. LAB-099 PREPARED authority waits on LAB-095 completion.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165. Keep draft.
- LAB-095/#180 + LAB-096/#181: branch `lab-095-database-identity-red-intent`, draft PR #187, head `0a14492c280c0fa6ed60ae20c8ea9f04144ade7a`. Keep draft.
- LAB-092/#176: draft PR #177; now has a known composition conflict with LAB-096's construction-bound history strategy.
- LAB-099: #184 / draft PR #186; PREPARED authority remains blocked on LAB-095.
- Retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175.

## Last completed step
LAB-086 was probed first in the executable runtime. Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`, exit 128. No LAB-086 PASS is claimed and the complete gate was not weakened.

Fallback work continued on PR #187. Exact branch-source audit found no remaining direct `self.provider_history` use in the inspected LAB-081/internal security-sensitive paths: runtime/head checks, reservation, rotation, receipt storage/load, and durable verification dispatch through `_history()`. The public `provider_history` remains a least-capability inspection view without connection, locked-helper, receipt-mutation, path/bootstrap, or rotation authority.

A concrete downstream conflict was found in LAB-092 PR #177. `activation_schema_provenance.py` currently constructs a live history object through `ledger.provider_history = history`, invokes locked verification through `ledger.provider_history._verify_durable_locked(q)`, and later replaces the live strategy in `_bind_live_provider_history_provenance()`. That mechanism is incompatible with LAB-096 and would reopen the whole-object strategy replacement class LAB-096 exists to close.

Decision: do not weaken LAB-096 and do not patch PR #177 independently yet. Final LAB-090/LAB-092 + LAB-095/LAB-096 composition must preserve one construction-bound private history strategy, route LAB-092 locked/internal checks through `_history()` or narrower internal helpers, and preserve provenance-loss receipt fail-closed behavior without strategy replacement.

Durable evidence: `research/2026-09-14-lab096-lab092-provider-history-composition-audit.md`, main commit `a55b6b1ddbc21614a743e8e7c7e42bf4febf989c`. Issue comments added to #181 and #176 and PR #187.

Current direct GitHub PR resource reports PR #187 `mergeable=true`, `rebaseable=true`, `mergeable_state=clean`; a generic metadata wrapper transiently returned `mergeable=false`, so the direct PR resource is treated as the current observation. PR remains draft because behavioral/downstream gates are not complete.

## Known failures / blockers
- LAB-086 complete real-ledger gate remains unexecuted. Current executable runtime cannot resolve `github.com`; no supported byte-preserving connector -> filesystem bridge is exposed.
- SQLite tests in this runtime must use a journal-capable filesystem; `/dev/shm` was previously observed working.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 focused manifest has authoritative exact content known for all 8/8 files, but the complete eight-file no-stub tree still needs same-run reconstruction/hash verification plus execution.
- LAB-096 whole-object replacement and public live-strategy alias leaks are source-patched on PR #187; exact repository behavioral GREEN remains pending.
- LAB-092 PR #177 is source-incompatible with LAB-096 until its construction/replacement helpers are conflict-resolved as described above.
- Python reflection/private implementation access remains outside the supported/public API capability claim; process-grade isolation is not claimed.
- LAB-090/LAB-095/LAB-096 conflict resolution remains security-sensitive: preserve activation fencing, `CanonicalDatabaseBinding`, construction-bound provider-history strategy, and least-capability public inspection.

## Exact next action
LAB-086 first: execute the complete gate only from authoritative executable pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` if a supported byte-preserving materialization path can place exact repository bytes into an executable filesystem. Do not weaken or manually reserialize the large security-critical closure.

If LAB-086 remains transport-blocked, continue the PR #187 fallback by auditing the LAB-090 PR #175 call sites against the `_history()` contract and produce the exact conflict-resolution map needed for the final LAB-090 + LAB-092 + LAB-095/LAB-096 composed tree. In particular, every LAB-090 direct `self.provider_history.current()` / `_rotate_locked()` / receipt call must be classified as public-inspection vs internal-authority use, with internal authority moved to `_history()` while preserving activation ordering/fencing.

If a safe byte-preserving execution bridge becomes available, materialize exact PR #187 head, run `compileall`, `test_provider_history_capability_surface.py`, `test_database_path_binding.py`, then the retained no-stub LAB-095 recovery/confirmed-finalize/locked-custody suite under `TMPDIR=/dev/shm`. After that run the conflict-resolved LAB-081/LAB-090/LAB-092 downstream gates.

Never replace external authenticated authority with deterministic test vectors, caller-supplied nonce/digest, path hashes, or same-DB self-asserted identifiers.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; authoritative complete-gate pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`; exact executable gate pending.
- #180 / LAB-095 — IN_PROGRESS; path binding implemented; exact/downstream gates pending.
- #181 / LAB-096 — IN_PROGRESS/COMPOSED ON PR #187; strategy replacement + public live-strategy alias patched; exact/downstream validation pending.
- #176 / LAB-092 — retained draft with explicit LAB-096 composition conflict now documented.
- #167 / LAB-088, #169 / LAB-090, #170 / LAB-091 — retained draft gates pending.
- #178..185 / LAB-093..100 — remaining architecture/security follow-ups.
- #184 / LAB-099 — PREPARED authority waits on LAB-095 completion.
