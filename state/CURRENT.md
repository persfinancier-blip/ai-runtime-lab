# Current Lab State

Last updated: 2026-09-13

## Active objective
LAB-086 remains priority #1: finish the exact executable/security gate for asymmetric break-glass history migration. LAB-095 is now the permitted fallback prerequisite when byte-exact LAB-086 execution cannot be materialized safely; LAB-099 PREPARED authority waits on LAB-095 logical identity.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165. Keep draft.
- LAB-092: #176 / draft PR #177, pinned head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`.
- LAB-095 prerequisite: #180 / branch `lab-095-database-identity-red-intent` / draft PR #187, head `992c1541e6060a5fb122c54cac0a314c80f2b977`.
- LAB-099: #184 / branch `lab-099-precursor-cutover-red-intent` / draft PR #186, head includes first production slice `d40aea8c48efe587b273650a3756ca782ba81472`.
- Other retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175.

## Last completed step
Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues and active PR state. Resumed LAB-086 first, then advanced LAB-095 only after exact materialization remained unavailable.

### LAB-086 current-run evidence
- Executable pin remains `1f90830fca21e2f43fc241012cdd34fd187ba96d`.
- Fresh direct clone again failed before repository execution: `Could not resolve host: github.com` / exit 128.
- Connector can read pinned UTF-8 blobs, but there is still no supported programmatic connector->filesystem byte stream for the complete exact dependency closure in this run.
- No new LAB-086 unittest/security/compile/conflict PASS is claimed. PR #165 remains draft.

### LAB-095 regression-first slice
Source-audited current shared-anchor/provider-history path ownership plus LAB-092 migration provenance. A private path fix alone is insufficient for downstream LAB-099 because LAB-099 also needs a path-independent authenticated logical database/history identity.

Created draft PR #187 with test-only authority only:
- `experiments/provider_generation_history/tests/lab095_database_identity_reference.py`, blob `9f02ddf64cff5b245cfa7a58e188ff9792b3eb18`;
- `experiments/provider_generation_history/tests/red_intent_lab095_database_identity.py`, blob `b1499243e8452daadf97fdb9ff97e29a9ce82e28`.

Both authored files passed local `py_compile`; local `git hash-object` values exactly matched the published GitHub blobs. This is compile/blob evidence only, not repository behavioral RED.

Frozen semantics:
- runtime physical binding and logical lineage identity are separate requirements;
- constructed supported history/ledger objects must not be redirectable from DB A to DB B by public path rebinding;
- v1 logical identity uses a fresh 32-byte nonce + bootstrap generation identity in a migration intent, but the nonce is not authority by itself;
- `logical_database_identity_digest` is derived only from the exact externally CONFIRMED shared-anchor row/receipt evidence;
- logical identity is path-independent; a post-confirmation backup/clone remains the same logical lineage, while independently initialized DBs must receive distinct confirmed identities;
- deterministic domain-separated genesis/transition parent-chain links are rooted in the logical identity and exact provider transition proof.

Rejected unsafe identity sources: `hash(path)`, mutable SQLite self-hash, caller-supplied root digest, plain UUID stored only in the same DB, or LAB-092's deterministic completion payload by itself.

Durable evidence:
- `research/2026-09-13-lab095-database-identity-red-intent.md`
- main commit `923f9325978c9155c689a25cb91cf48757ec40eb`
- #180 comment `5652932968`
- draft PR #187 head `992c1541e6060a5fb122c54cac0a314c80f2b977`

## Known failures / blockers
- LAB-086 exact complete real-ledger gate remains unexecuted because byte-exact repository materialization is unavailable; do not manually reconstruct the 50+ file closure.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until their retained exact gates execute.
- LAB-095 exact repository RED is not yet executed; production `experiments.provider_generation_history.database_identity` does not exist and current `DurableProviderHistory.path` remains mutable/public.
- LAB-095 still needs identity-installation crash/retry semantics, legacy migration ordering, and the exact runtime physical-binding mechanism before production implementation.
- LAB-099 migration/resume remains intentionally fail-closed and waits on LAB-095 authenticated logical identity.

## Exact next action
LAB-086 first: re-probe for a supported byte-preserving materialization path. If available, reconstruct only pin `1f90830fca21e2f43fc241012cdd34fd187ba96d`, require local `git hash-object` match for every manifest/test/helper/transitive file, then run all normal LAB-086 tests, unsafe expected-failure separately, downstream/helper tests, compileall, `*_for_test_only` audit, security/reconciliation audit, and current-main conflict audit.

If exact LAB-086 materialization is still unavailable, do not repeat manual source-transfer attempts. Continue LAB-095 on PR #187: source-audit and freeze the identity installation/recovery state machine covering fresh install, PREPARED crash, provider timeout/UNKNOWN, confirmed restart, partial local marker states, legacy migration, and concurrent writer behavior. Resolve nonce generation/retry custody without caller-supplied authority. Only after that contract is frozen implement the smallest production identity primitive + construction-bound physical DB reference. Then return to LAB-099 PREPARED authority; do not import or derive production authority from test references.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact executable gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #180 / LAB-095 — IN_PROGRESS on draft PR #187; RED-intent identity contract frozen, crash/recovery contract next.
- #178..185 / LAB-093..100 — remaining design/source follow-ups with executable gates pending.
- #184 / LAB-099 — classifier/startup slice published; PREPARED authority waits on LAB-095 identity prerequisite.
