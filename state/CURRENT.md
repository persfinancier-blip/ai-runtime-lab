# Current Lab State

Last updated: 2026-09-13

## Active objective
LAB-086 remains priority #1: finish the exact executable/security gate for asymmetric break-glass history migration. When byte-exact LAB-086 execution cannot be materialized safely, LAB-095/#180 is the permitted fallback prerequisite. LAB-099 PREPARED authority waits on LAB-095 authenticated logical database/history identity.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165. Keep draft.
- LAB-095 prerequisite: #180 / branch `lab-095-database-identity-red-intent` / draft PR #187, current head `ed0e3baeba6be964ae05f33063c8073bcd15d2d6`; mergeable, still draft.
- LAB-099: #184 / draft PR #186; PREPARED authority remains blocked on LAB-095.
- Retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.

## Last completed step
Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues and active PR state. Re-probed LAB-086 first, then advanced LAB-095 only after exact materialization remained unavailable.

### LAB-086 current-run evidence
- Executable pin remains `1f90830fca21e2f43fc241012cdd34fd187ba96d`.
- Fresh direct clone failed before repository execution: `Could not resolve host: github.com` / exit 128.
- No byte-exact complete dependency closure was materialized.
- No new LAB-086 unittest/security/compile/conflict PASS is claimed. PR #165 remains draft.

### LAB-095 production custody/classifier slice
First independent production module is now on PR #187:
- `experiments/provider_generation_history/database_identity.py`
- published/audited blob `96be3e6fd17a86a3f7fb133a68b9b88741ad4070`
- production commit `c943e9bbd56989258ce919a578a54a50ff32aa88`

The module does not import `tests/lab095_*` and does not synthesize external authority. It implements:
- frozen-compatible logical identity and parent-chain derivation;
- exact local custody DDL;
- fail-closed persisted states `ABSENT`, `PREPARED`, `CONFIRMED_NEEDS_FINALIZE`, `COMPLETE`, `CORRUPT`;
- custody payload/request cross-binding to the persisted shared-anchor identity intent;
- confirmed identity recomputation from persisted CONFIRMED intent/receipt evidence;
- exact custody-schema verification and a table-type check for `shared_anchor_intents`;
- side-effect-free missing-path classification.

Focused execution against the published production bytes plus a locally reconstructed frozen-reference helper: **5/5 PASS, exit 0**. Covered canonical derivation equality, state progression, digest tamper -> `CORRUPT`, orphan custody -> `CORRUPT`, no DB file creation for missing path, and altered same-name custody schema -> `CORRUPT`.

Audit finding fixed before handoff: the first classifier version called `sqlite3.connect()` on a missing path and therefore created an empty DB despite claiming read-only behavior. The final published blob checks path existence/type before connect and exact-checks custody DDL.

Durable evidence:
- `research/2026-09-13-lab095-production-custody-classifier-slice.md`, main commit `bb3ea5bf8826fedfaac5c39ff65b31671627edaa`;
- issue #180 comment `5653539250`;
- PR #187 description updated with actual production state and validation limits.

This is not a full exact-repository LAB-095 GREEN. Complete repository closure and LAB-080/081/090/092 downstream gates were not materialized in this runtime.

## Known failures / blockers
- LAB-086 exact complete real-ledger gate remains unexecuted because direct git transport cannot resolve `github.com`; do not manually reconstruct the 50+ file closure or weaken byte-exact evidence requirements.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until their retained exact gates execute.
- LAB-095 migration/execution is not implemented yet: no production internal CSPRNG nonce generation, no atomic custody + PREPARED reservation, no same-request external reconciliation/finalization, and no construction-bound physical DB reference yet.
- `DurableProviderHistory.path` and `SharedAnchorLedger.path` remain mutable/public; DB-A -> DB-B rebinding acceptance is not fixed yet.
- LAB-099 migration/resume remains intentionally fail-closed and must not derive authority from `tests/lab095_*` or LAB-099 fixtures.

## Exact next action
LAB-086 first: re-probe for a supported byte-preserving materialization path. If available, reconstruct only executable pin `1f90830fca21e2f43fc241012cdd34fd187ba96d`, require local `git hash-object` match for every manifest/test/helper/transitive file, then run the full retained LAB-086 gate including unsafe expected-failure separately, compileall, security/reconciliation, and current-main conflict audit.

If exact LAB-086 materialization is still unavailable, continue LAB-095 on PR #187 with **explicit installation/recovery**:
1. add an explicit migration API that opens `BEGIN IMMEDIATE`, re-reads persisted state, and only for true `ABSENT` generates exactly 32 random bytes internally via CSPRNG;
2. atomically persist nonce/bootstrap/payload custody and the one deterministic PREPARED shared-anchor identity reservation before any external provider call;
3. on `PREPARED`, reuse/reconcile the same persisted request only — never generate a second nonce/request;
4. on externally CONFIRMED but locally PREPARED state, reauthenticate the persisted receipt/evidence and finalize the local identity without another increment;
5. add crash-before/after-commit, UNKNOWN, confirmed-restart, partial-state, concurrent-installer, and legacy-history regressions;
6. then make the physical DB reference private/non-rebindable across `DurableProviderHistory` + `SharedAnchorLedger` and add DB-A -> DB-B regression;
7. only after these pass, integrate identity/parent-chain authority into downstream LAB-099.

Never use deterministic test vectors, caller-supplied nonce/digest, filesystem path hashes, or a same-DB self-asserted UUID as production authority.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact executable gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #180 / LAB-095 — IN_PROGRESS on draft PR #187; production custody/classifier now published; explicit migration/recovery + immutable physical binding next.
- #178..185 / LAB-093..100 — remaining architecture/security follow-ups with executable gates pending.
- #184 / LAB-099 — classifier/startup slice published; PREPARED authority waits on LAB-095 production identity completion.
