# Current Lab State

Last updated: 2026-09-11

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and current-main conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`. Keep draft.
- Other open drafts inspected this run: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues/PRs; resumed LAB-086 first and re-probed exact materialization.

Current-run capability/evidence:
- Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`.
- GitHub connector reads/writes/compare remain available, but no supported byte-exact connector-to-local-executor materialization primitive is exposed. Manual/model reserialization of the security-critical LAB-086 closure remains prohibited.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation or conflict PASS is claimed; PR #165 remains draft/open.
- Fresh compare before the research commit: PR #165 was `diverged`, ahead 195 / behind 847, merge base `d2c9781f5a60dc9b8b94fc8dba651f804a73e509`, base/main `09fe0a3c962f51a44dfe4f001715a4de29627efa`. Research + this state commit advance main again; refresh compare immediately before any integration decision.

Completed the recorded distinct fallback and froze `RECOVERY_REVOCATION_RETIREMENT_THRESHOLD_UNLEARNING_MIGRATION_PRIVACY_MERKLE_PROVIDER_REPLAY_GC_PROOF_RETENTION_V1_FROZEN` in `research/2026-09-11-recovery-revocation-retirement-threshold-unlearning-migration-privacy-merkle-provider-replay-gc-proof-retention-v1.md`, main research commit `f72a20b6e35b527dae4abd39ffaf8cc673fd66e1`; #178 comment `5638054744` records the result.

Key decisions:
- Compact recovery authority binds recovery generation, exact signer set/threshold, independence/failure-domain commitment and revocation-policy generation. Revoking a signer/domain after issuance does not rewrite history, but an old compact certificate cannot silently authorize new recovery under the new policy. Same-generation revocation views fork until a later authenticated resolver commits all known heads.
- Retirement bridges bind both the monotonic non-resurrection floor and the witness-policy generation/set commitment. Threshold changes create new bridge generations; signatures collected under one policy are not reinterpreted under another. Witness revocation never resurrects a retired verifier.
- Result-store migration must preserve immutable unlearning result IDs, theorem/profile generation, invalidation frontier and descendant-closure commitment. Missing closure evidence becomes `UNLEARNING_CLOSURE_INCOMPLETE`/`UNLEARNING_DEPENDENCY_UNKNOWN`, never a positive cache result.
- Privacy accountant rotation preserves one released-event lineage. Compact checkpoints bind event-set root/range/count, method/profile and cumulative bound; a successor needs authenticated predecessor continuity plus event-set consistency. Compaction or raw-event deletion never refunds already incurred privacy loss.
- Provider original/compensation/repair effects retain separate immutable identities. Provider rollback after an authenticated completion receipt creates state/evidence divergence; replayed contradictory terminal receipts yield `PROVIDER_EFFECT_FORK`. Idempotency retention expiry never proves no prior effect or authorizes blind redispatch.
- GC snapshots must retain the membership configuration and commit/finality proof effective at the last included consensus index. Snapshot presence of `C_new` is not proof it committed; if truncated history cannot reconstruct disputed membership finality, destructive GC is blocked as `GC_MEMBERSHIP_FINALITY_UNKNOWN`.
- Frozen 48-case RED-first matrix covers all six contracts. Architecture/evidence only; exact RED/GREEN pending.

Primary donors re-verified this run: TUF root succession/revocation and rollback protection; RFC 9162 Merkle consistency; NIST SP 800-226 cumulative privacy composition; AWS idempotent mutation guidance; Raft snapshot membership retention and joint consensus.

## Known failures / blockers
- LAB-086 remains priority #1. Exact local execution of the complete real-ledger closure is still unavailable.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read pinned source but cannot byte-exactly materialize the whole pinned closure into the executor in this run.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- PR #165 was 847 commits behind at the latest compare before two new main commits; refresh compare before integration.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 and subsequent design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **recovery revocation-policy succession after the revocation authority itself rotates/compromises + retirement bridge quorum intersection when witness sets are disjoint across generations + unlearning migration rollback after the source store has been retired + privacy Merkle checkpoint split/merge with independently advanced branches + provider effect reconciliation when receipts are valid but provider generation lineage forks + GC snapshot-install/recovery when membership proof spans a truncated joint-consensus boundary**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + current-main conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; architecture now additionally covers recovery revocation after compact issuance, retirement witness-threshold evolution, unlearning closure retention across result-store migration, privacy event-set/Merkle compaction across accountant rotation, provider receipt rollback/replay, and GC membership-proof retention across snapshot/log compaction; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
