# Current Lab State

Last updated: 2026-09-13

## Active objective
LAB-086 remains priority #1: finish the exact executable/security gate for asymmetric break-glass history migration. LAB-095 is the permitted fallback prerequisite when byte-exact LAB-086 execution cannot be materialized safely; LAB-099 PREPARED authority waits on LAB-095 logical identity.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165. Keep draft.
- LAB-092: #176 / draft PR #177, pinned head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`.
- LAB-095 prerequisite: #180 / branch `lab-095-database-identity-red-intent` / draft PR #187, current head `aa7ae4eeb2d1f8228dae30c15fa9621a2b51550e`.
- LAB-099: #184 / branch `lab-099-precursor-cutover-red-intent` / draft PR #186, head includes first production slice `d40aea8c48efe587b273650a3756ca782ba81472`.
- Other retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175.

## Last completed step
Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues and active PR state. Resumed LAB-086 first, then advanced LAB-095 only after exact materialization remained unavailable.

### LAB-086 current-run evidence
- Executable pin remains `1f90830fca21e2f43fc241012cdd34fd187ba96d`.
- Fresh direct clone again failed before repository execution: `Could not resolve host: github.com` / exit 128.
- No byte-exact complete dependency closure was materialized in this run.
- No new LAB-086 unittest/security/compile/conflict PASS is claimed. PR #165 remains draft.

### LAB-095 identity installation/recovery state machine
Source-audited the LAB-092 migration path as the nearest production precedent: explicit migration establishes local state plus a deterministic shared-anchor PREPARED marker atomically under `BEGIN IMMEDIATE`, then performs external confirmation; ordinary startup remains read-only/fail-closed.

The LAB-095 crash/retry contract is now frozen test-only on draft PR #187:
- `experiments/provider_generation_history/tests/lab095_identity_installation_reference.py`, commit `d3832c3672e1f54b61e0507f48d88358fba43531`, published blob `91b69a16d1a8d25d4c0af15becd320fdad95d682`;
- `experiments/provider_generation_history/tests/test_lab095_identity_installation_reference.py`, commit/current PR head `aa7ae4eeb2d1f8228dae30c15fa9621a2b51550e`.

Authored-source validation completed locally before publication:
- both files passed `py_compile`;
- the standalone state-machine unittest ran 5/5 PASS, exit 0;
- the reference source local `git hash-object` matched the published blob exactly;
- the standalone regression source was adjusted only to use the repository package import before publication, so its earlier standalone blob hash is not asserted for the published file.

This is not a full repository behavioral GREEN/RED claim because the exact repository dependency closure was not materialized.

Frozen states/actions:
- `LEGACY_ABSENT` -> `BEGIN_INSTALL`;
- `PREPARED` -> `RECONCILE_SAME_REQUEST`;
- `CONFIRMED_NEEDS_FINALIZE` -> `FINALIZE_LOCALLY`;
- `COMPLETE` -> `VERIFY_ONLY`;
- any contradictory/asymmetric state -> `CORRUPT` / `FAIL_CLOSED`.

Frozen installation/recovery semantics:
- runtime physical binding and logical lineage identity remain separate requirements;
- generate exactly 32 random bytes internally with a CSPRNG only inside `BEGIN IMMEDIATE` after re-reading and confirming `LEGACY_ABSENT`; caller-supplied nonce or logical identity digest is forbidden;
- persist nonce/bootstrap/payload custody and the one deterministic shared-anchor PREPARED identity intent in the same SQLite transaction before any external call;
- crash before that transaction commits leaves `LEGACY_ABSENT`; crash after commit leaves `PREPARED`;
- provider timeout/UNKNOWN must reconcile the same deterministic request and must never generate another nonce/request;
- if external confirmation is durable but local identity finalization did not complete, restart must reauthenticate the CONFIRMED shared-anchor row plus receipt and derive/finalize locally without another provider increment;
- custody without matching intent, intent without custody, payload mismatch, local CONFIRMED before external CONFIRMED, missing confirmed receipt, or receipt/digest evidence while the intent is still PREPARED all fail closed;
- `BEGIN IMMEDIATE` serializes concurrent installers; a loser re-reads and resumes the winner's PREPARED request instead of generating a second nonce;
- legacy valid history reserves exactly the next shared-anchor position under the currently verified provider generation;
- a backup/clone after completed identity installation keeps the same path-independent logical lineage identity; this does not authorize concurrent writable forks, whose freshness boundary remains external/monotonic.

Durable evidence:
- `research/2026-09-13-lab095-identity-installation-recovery-state-machine.md`
- main research commit `76f6b57f7d7dcbd6cad3d909866c74ef4825a461`
- issue #180 updated with the state-machine decision and execution limits
- draft PR #187 head `aa7ae4eeb2d1f8228dae30c15fa9621a2b51550e`

## Known failures / blockers
- LAB-086 exact complete real-ledger gate remains unexecuted because byte-exact repository materialization is unavailable in this run; do not manually reconstruct the 50+ file closure.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until their retained exact gates execute.
- LAB-095 exact repository RED/GREEN is not yet executed; production `experiments.provider_generation_history.database_identity` does not exist and current `DurableProviderHistory.path` remains mutable/public.
- LAB-095 production custody/classifier/migration and the exact runtime physical-binding mechanism remain to be implemented independently of the test reference.
- LAB-099 migration/resume remains intentionally fail-closed and waits on LAB-095 authenticated logical identity. Production LAB-099 must not import or derive authority from `tests/lab095_*` or LAB-099 test vectors.

## Exact next action
LAB-086 first: re-probe for a supported byte-preserving materialization path. If available, reconstruct only executable pin `1f90830fca21e2f43fc241012cdd34fd187ba96d`, require local `git hash-object` match for every manifest/test/helper/transitive file, then run all normal LAB-086 tests, unsafe expected-failure separately, downstream/helper tests, compileall, `*_for_test_only` audit, security/reconciliation audit, and current-main conflict audit.

If exact LAB-086 materialization is still unavailable, do not repeat manual closure reconstruction. Continue LAB-095 on PR #187 with the smallest independent production slice, without importing `tests/lab095_*`:
1. define the minimal identity-custody table/DDL and independent production persisted-state classifier;
2. implement explicit identity migration under `BEGIN IMMEDIATE`;
3. generate the 32-byte CSPRNG nonce only after lock acquisition plus absent-state recheck;
4. atomically persist custody plus the deterministic PREPARED shared-anchor identity reservation before external execution;
5. recover `PREPARED` only by same-request reconciliation and recover `CONFIRMED_NEEDS_FINALIZE` only by reauthenticating the persisted external receipt/evidence then finalizing locally;
6. bind the physical DB reference privately/immutably across the shared ledger/provider-history ownership boundary;
7. add real repository RED/GREEN regressions for crash-before/after-commit, UNKNOWN, confirmed restart, corrupt partial states, concurrent installers, DB-A -> DB-B rebinding, and legacy migration.

Only after LAB-095 production identity authority is independently implemented and verified should LAB-099 consume it. Never use `tests/lab095_*`, deterministic test vectors, or fixture nonce/payload values as production authority.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact executable gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #180 / LAB-095 — IN_PROGRESS on draft PR #187; logical identity + crash/recovery contracts frozen test-only; independent production custody/classifier/migration next.
- #178..185 / LAB-093..100 — remaining design/source follow-ups with executable gates pending.
- #184 / LAB-099 — classifier/startup slice published; PREPARED authority waits on LAB-095 production identity prerequisite.
