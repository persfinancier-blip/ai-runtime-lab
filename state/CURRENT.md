# Current Lab State

Last updated: 2026-09-11

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and current-main conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`. Keep draft.
- Other open drafts inspected this run: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and active PR metadata; resumed LAB-086 first and re-probed exact source materialization.

Current-run capability/evidence:
- Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`.
- GitHub connector reads/writes and compare remain available, but no supported non-model connector-to-local-filesystem byte-exact materialization primitive is exposed. Manual/model reserialization of the security-critical LAB-086 closure remains prohibited by the retained exact-byte gate.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation or conflict PASS is claimed; PR #165 remains draft/open.
- PR #165 was re-read at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; fresh compare after this run's research commit is `diverged`, ahead 195 / behind 836, merge base `d2c9781f5a60dc9b8b94fc8dba651f804a73e509`.

Completed the recorded distinct fallback and froze `COMPACT_CUTSET_ROTATION_RETIREMENT_REEXPORT_UNLEARNING_HEAL_PRIVACY_LINEAGE_PROVIDER_LATE_COMPLETION_GC_SCOPE_V1_FROZEN` in `research/2026-09-11-compact-cutset-rotation-retirement-reexport-unlearning-heal-privacy-lineage-collision-provider-late-completion-gc-scope-rotation-v1.md`, main research commit `dc9e0ad8e8c06a44c206baca2c18584ccd82b91c`; #178 comment `5634307153` records the result.

Key decisions:
- Rotation of compact recovery cut-set authority must commit predecessor evidence and preserve unknown/shared-domain floors. Re-signing a compact certificate under a new key is authority migration, not re-proof. If detailed evidence has crossed retention and the predecessor issuer is later compromised without surviving independent proof, state becomes `CUTSET_AUTHORITY_UNCERTAIN`.
- Exported verifier-retirement floors are monotonic non-resurrection state stronger than one destination store. Older signed exports after a surviving high-water mark are rollback; same-generation alternate exports are forks; source deletion plus destination compromise plus loss of all independent checkpoints yields `RETIREMENT_FLOOR_UNRECOVERABLE`, never fresh verifier authority.
- Compact distributed unlearning invalidation checkpoints are monotonic authority floors. Partitioned incomparable checkpoints form a fork; heal is conservative union; stale replicas cannot serve positive authority-bearing cached results before catch-up; membership changes during an unresolved fork require overlapping old/new authorization and exact checkpoint catch-up.
- Independently restored privacy roots retain one immutable logical budget lineage. Consumed loss cannot decrease; unresolved reservations union; identical immutable analysis IDs deduplicate; conflicting payload reuse forks; coordinator/shard/namespace/root renaming cannot mint fresh budget.
- Provider mutations retain one immutable effect/idempotency identity beyond provider deduplication TTL. After TTL expiry or unknown retention, blind retry is prohibited; late authenticated completion may resolve only the original effect and conflicts with authenticated no-effect evidence rather than authorizing a second dispatch.
- Compact GC checkpoints form a scope-aware succession DAG. Split/merge must explicitly bind all parent scopes and preserve union safety floors across authority rotation; retained coverage gaps block destructive GC; revocation of a newer checkpoint does not revive retired older authority.
- Frozen 48-case RED-first matrix covers all six contracts. This remains architecture/evidence only; exact RED/GREEN is pending.

Primary donors re-verified this run: TUF predecessor+successor threshold/root rollback discipline; RFC 9162 append-only consistency proofs; NIST SP 800-226 cumulative privacy budgeting; Raft joint-consensus membership changes; AWS idempotency-token semantics and finite deduplication retention.

## Known failures / blockers
- LAB-086 remains priority #1. Exact local execution of the complete real-ledger closure is still unavailable.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read pinned source but cannot byte-exactly materialize the whole pinned closure into the executor in this run.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- PR #165 is now 836 commits behind `main`; do not infer merge safety from historical conflict observations.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 and subsequent design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **successor-compromise/fork recovery for rotated compact cut-set authority + cross-destination retirement-floor fork reconciliation when multiple independently recovered stores exist + authority/root rotation of compact unlearning invalidation checkpoints during an unresolved partition + privacy-lineage merge after both restored branches have independently spent budget + late authenticated provider no-effect/completion conflicts after a separately authorized compensating effect + tombstone/retention compaction for split/merged GC scope succession without losing non-resurrection or coverage floors**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + current-main conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; architecture now additionally covers rotated compact recovery cut-set authority, retirement-floor destination recovery, distributed unlearning invalidation partition/heal, logical privacy-lineage collisions, provider late completion after idempotency TTL, and GC scope split/merge across authority rotation; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
