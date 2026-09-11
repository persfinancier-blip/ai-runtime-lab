# Current Lab State

Last updated: 2026-09-12

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
- GitHub connector reads/writes remain available, but no supported byte-exact connector-to-local-executor materialization primitive is exposed. Manual/model reserialization of the security-critical LAB-086 closure remains prohibited.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation or conflict PASS is claimed.
- PR #165 was freshly fetched and remains `open`, `draft=true`, `mergeable=false`, head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Fresh compare after the research commit: `diverged`, ahead 195 / behind 860, merge-base `d2c9781f5a60dc9b8b94fc8dba651f804a73e509`, main/base commit `c9af032b6ce9a175cb99b49c3db440b127ade3f9`.

Completed the recorded fallback and froze `RECOVERY_SUCCESSOR_FORK_RETIREMENT_MULTIREVOKE_UNLEARNING_FANOUT_PRIVACY_NESTED_LEASE_PROVIDER_OBSERVER_ROTATION_GC_CERT_REPLACEMENT_V1_FROZEN` in `research/2026-09-12-recovery-successor-fork-retirement-multirevoke-unlearning-fanout-privacy-nested-lease-provider-observer-rotation-gc-certificate-replacement-v1.md`, main research commit `c9af032b6ce9a175cb99b49c3db440b127ade3f9`; #178 comment `5641742661` records the result.

Key decisions:
- A recovery common successor whose own compromise evidence later forks is not self-authorizing. Conflicting authenticated compromise histories make successor authority ambiguous until a later common successor/order proof covers both branches; historical statement validity remains distinct from prospective authority.
- Multi-generation retirement revocation keeps a monotonic non-resurrection floor. Prospective revocation does not erase historical statements; retroactive historical-statement revocation needs its own pre-authorized authority/order proof and cannot revive retired mutation authority.
- When S4 fans out into independently compacted S5/S6 stores, unlearning obligations follow the lineage. Missing ancestry/detail yields `DEPENDENCY_UNKNOWN`; local compaction or remigration cannot silently clear it.
- Nested privacy leases form one authenticated budget tree. Allocator rotation, wall-clock expiry, partitions, result deletion, or child delegation cannot duplicate/reclaim budget without authenticated closure proving unused remainder and no unresolved descendants.
- Provider transport outcome, provider receipt, observer statement and external effect remain separate evidence. Observer rotation/compromise is ordered by authenticated authority intervals; late arrival is not authority, and receipt-retention expiry means proof unavailable rather than no effect.
- Compact GC membership certificates must preserve every truncated joint-consensus transition obligation. Revocation/replacement of a certificate requires authenticated predecessor continuity; newest snapshot/terminal membership alone cannot prove safe succession.
- Frozen 48-case RED-first matrix covers all six contracts. Architecture/evidence only; exact RED/GREEN pending.

Primary donors re-verified this run: TUF 1.0.36 root/key succession, threshold and revocation semantics; RFC 9162 Merkle consistency proofs; NIST SP 800-226 cumulative privacy-budget composition; AWS idempotency-token semantics and finite retention example; Raft joint consensus and snapshot/log-compaction model.

## Known failures / blockers
- LAB-086 remains priority #1. Exact local execution of the complete real-ledger closure is unavailable in this run.
- Direct shell transport cannot resolve `github.com`.
- Connector can read pinned source but cannot byte-exactly materialize the whole pinned closure into the executor in this run.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 and subsequent design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and choose the highest-value distinct evidence task from the READY backlog rather than extending an already-frozen contract by repetition. Current preferred fallback: **LAB-100/#185 — statically audit the actual LAB-090 provider construction/rotation/recovery surfaces on PR #175 and freeze the trusted provider implementation/adapter capability boundary, including subclass-overridden prepare/status/commit/release methods and restart evidence.** Use connector source reads and primary-source research; do not claim exact behavior unless executed.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + current-main conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; architecture now additionally covers successor-compromise evidence forks, retirement historical-statement multirevocation, independently compacted unlearning fan-out, nested privacy leases, observer authority rotation/compromise and compact GC certificate replacement; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending. Preferred non-executable fallback after LAB-086 is now LAB-100/#185 source-level provider authority audit rather than another broad LAB-093 extension.
