# Current Lab State

Last updated: 2026-09-14

## Active objective
LAB-086 remains priority #1: finish the exact executable/security gate for asymmetric break-glass history migration. When byte-exact LAB-086 execution cannot be materialized safely, LAB-095/#180 is the permitted fallback prerequisite. LAB-099 PREPARED authority waits on LAB-095 authenticated logical database/history identity plus lifetime physical DB binding.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165. Keep draft.
- LAB-095: #180 / branch `lab-095-database-identity-red-intent` / draft PR #187, head `835a81914c5234e68ef436e30c9837331d262432`. Keep draft.
- LAB-099: #184 / draft PR #186; PREPARED authority remains blocked on LAB-095.
- Retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.

## Last completed step
No new supported byte-preserving GitHub-connector -> executable-filesystem materialization path is exposed in this run, so no exact executable gate was fabricated. Connector-side static/security work therefore audited LAB-095 lifetime DB binding against retained LAB-090/LAB-092 constructors and MROs.

Findings: LAB-095 `SupportedSharedAnchorLedger(CanonicalDatabaseBinding, SharedAnchorLedger)` and `CoordinatorOnlyProviderHistory(CanonicalDatabaseBinding, IntegratedProviderHistory)` are compatible with inherited constructors because the existing first `self.path = ...` becomes the canonical bind. LAB-092 `object.__new__` reservation/provenance helper surfaces also assign `path` exactly once on fresh instances; `_bind_live_provider_history_provenance()` creates a fresh history object and performs one first-bind assignment. No duplicate constructor assignment or static rebinding bypass was found there.

A security-sensitive integration conflict is confirmed: retained LAB-090 `supported.py` defines `CoordinatorOnlyProviderHistory(IntegratedProviderHistory)` while LAB-095 requires the `CanonicalDatabaseBinding` mixin on that same class. Eventual conflict resolution must preserve LAB-090 activation fencing/recovery behavior and LAB-095 binding MRO simultaneously; choosing the LAB-090 file wholesale would silently remove provider-history lifetime DB binding. Fresh PR #187 API state remains `mergeable=true`, `rebaseable=true`, `mergeable_state=clean`, but that does not exercise cross-draft integration.

Durable report: `research/2026-09-14-lab095-lab090-lab092-constructor-binding-conflict-audit.md`, main commit `59fdca830bc7e41efeb8af9ef1288683445e5354`. Issue #180 comment `5663146638`; PR #187 comment `5663145499`.

Previously established evidence remains valid: LAB-086 authoritative complete-gate pin is `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`; direct executable-runtime GitHub transport was previously shown blocked at DNS and TCP/443. All eight focused LAB-095 manifest blobs have authoritative exact content known across runs; cross-generation COMPLETE reauth exact closure passed 1/1; object.__new__ binding exact regression passed 1/1; recovery/tamper behavior passed 6/6 previously with exact LAB-095 production/test blobs but protocol stubs.

## Known failures / blockers
- LAB-086 complete real-ledger gate remains unexecuted. Direct executable-runtime GitHub transport is blocked; no new supported byte-preserving connector -> filesystem bridge is exposed in this run.
- SQLite tests in this runtime must use a journal-capable filesystem; `/dev/shm` is observed working.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 focused manifest has authoritative exact content known for all 8/8 files, but the complete eight-file no-stub tree still needs same-run reconstruction/hash verification plus execution.
- LAB-090/LAB-095 `supported.py` conflict resolution is security-sensitive: preserve LAB-090 activation semantics and `CanonicalDatabaseBinding` on both supported ledger/history MROs.

## Exact next action
LAB-086 first: execute the complete gate only from authoritative executable pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` if a newly exposed supported byte-preserving materialization path can place exact repository bytes into an executable filesystem. Do not weaken or manually reserialize the large security-critical closure.

If no such LAB-086 bridge exists, probe once for a supported connector/file materialization route for LAB-095. If available, reconstruct all eight focused LAB-095 files from PR #187 head `835a81914c5234e68ef436e30c9837331d262432`, require same-run 8/8 `git hash-object` matches, run `compileall`, and execute recovery/confirmed-finalize/locked-custody tests with no protocol stubs under `TMPDIR=/dev/shm`. Then execute DB-A -> DB-B and downstream LAB-080/LAB-081/LAB-090/LAB-092 gates using a conflict-resolved tree that preserves both LAB-090 activation fencing and LAB-095 `CanonicalDatabaseBinding` MRO.

If no safe byte-preserving execution bridge is exposed, continue only with auditable connector-side research/static security work and record the exact blocker; do not fabricate executable evidence or manually reserialize large security-critical sources as a substitute for byte-exact materialization.

Never replace external authenticated authority with deterministic test vectors, caller-supplied nonce/digest, path hashes, or same-DB self-asserted identifiers.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; authoritative complete-gate pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`; exact executable gate pending.
- #180 / LAB-095 — IN_PROGRESS; 8 focused manifest blobs have exact authoritative content established across runs; same-run 8/8 no-stub reconstruction and behavioral execution pending; downstream LAB-090/LAB-092 constructor audit clean with binding-preserving conflict rule recorded.
- #167 / LAB-088, #169 / LAB-090, #170 / LAB-091, #176 / LAB-092 — retained draft gates pending.
- #178..185 / LAB-093..100 — remaining architecture/security follow-ups.
- #184 / LAB-099 — PREPARED authority waits on LAB-095 completion.
