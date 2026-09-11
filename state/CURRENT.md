# Current Lab State

Last updated: 2026-09-11

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and current-main conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`. Keep draft.
- Other open drafts inspected this run: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and active PRs; resumed LAB-086 first and re-probed exact source materialization.

Current-run capability/evidence:
- Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`.
- GitHub connector reads/writes and compare remain available, but no supported non-model connector-to-local-filesystem byte-exact materialization primitive is exposed. Manual/model reserialization of the security-critical LAB-086 closure remains prohibited by the retained exact-byte gate.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation or conflict PASS is claimed; PR #165 remains draft/open.
- PR #165 was re-read at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; current compare immediately after the research commit was `diverged`, ahead 195 / behind 830, merge base `d2c9781f5a60dc9b8b94fc8dba651f804a73e509`. This state-file commit moves `main` again, so obtain another fresh compare before any merge/conflict conclusion.

Completed the recorded distinct fallback and froze `RECOVERY_RECOMPROMISE_RETIREMENT_FLOOR_UNLEARNING_RACE_PRIVACY_GENERATION_FINALITY_REVOCATION_GC_COMPACTION_V1_FROZEN` in `research/2026-09-11-recovery-recompromise-retirement-floor-unlearning-race-privacy-generation-finality-revocation-gc-compaction-v1.md`, main research commit `63bd9c831143c56b813a024053073685d6a383dd`; #178 comment `5632295661` records the result.

Key decisions:
- A repaired recovery-policy anchor can itself later be compromised or fork. Same-generation repair heads remain an explicit fork; a higher repair must commit every live head, the last undisputed floor/predecessor and interval-scoped compromise evidence, then satisfy threshold/intersection after canonical failure-domain filtering.
- Retirement compaction may preserve an independently authenticated non-resurrection floor after detailed reconstructed bridge evidence is deleted, but that compact floor cannot claim exact canonical continuity it no longer proves. Pending audit/effect dependencies block deletion.
- Unlearning certificate revalidation is generation/snapshot-linearized. Descendant issuance racing an ancestor transition cannot observe a half-revalidated state; stale prepared descendants fail a status-generation/CAS check, and failed ancestor revalidation invalidates dependent descendants.
- Privacy compensation across participant-set change and coordinator failover keeps one analysis/budget lineage. Participant removal never erases consumed loss/reservations; a transition while forks are open must bridge every fork head and retain a conservative cumulative-loss floor.
- Finality replicas whose catch-up attestations are later revoked/compromised lose affected authority until the exact historical range/checkpoint is independently re-proved under the required joint quorum. Membership history is not silently rewritten and `EFFECT_UNKNOWN` is never upgraded to restore liveness.
- GC audit evidence from retired configurations may be compacted only as explicitly historical/non-authoritative evidence after dependency closure. Compaction records cannot be accepted as live quorum certificates, and unknown retention dependencies fail closed.
- Frozen 48-case RED-first matrix covers all six contracts. This remains architecture/evidence only; exact RED/GREEN is pending.

Primary donors re-verified this run: TUF authenticated threshold/root/rollback discipline; RFC 9162 append-only consistency proofs; NIST SP 800-226 cumulative privacy budgeting; Raft joint consensus/overlapping-majority membership changes.

## Known failures / blockers
- LAB-086 remains priority #1. Exact local execution of the complete real-ledger closure is still unavailable.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read pinned source but cannot byte-exactly materialize the whole pinned closure into the executor in this run.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- PR #165 was 830 commits behind `main` immediately before this state commit; do not infer merge safety from historical conflict observations.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 and subsequent design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **recovery repair-chain trust when both an intermediate repaired anchor and its successor assessment authority are later compromised + export/migration of a compact retirement non-resurrection floor across a trust-root rotation without resurrecting old verifier authority + unlearning descendant/result-cache invalidation after ancestor revalidation changes theorem/profile generation + privacy budget namespace split/merge across participant-set transitions without double-spend or refund + provider/finality effect-ledger replay after membership recovery and cache compaction + GC compact-checkpoint authority loss/revocation while detailed historical evidence has already crossed its retention boundary**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + current-main conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; architecture now additionally covers repaired-anchor re-compromise/fork, retirement-floor survival after bridge compaction, unlearning revalidation/descendant races, privacy participant-generation compensation, finality catch-up revocation, and non-authoritative GC evidence compaction; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
