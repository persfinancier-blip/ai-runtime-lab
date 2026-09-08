# Current Lab State

Last updated: 2026-09-09

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; keep draft and do not merge without the exact retained gate.
- Other open drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and active PRs; resumed LAB-086 first.

Current-run capability probe:
- direct container network to `raw.githubusercontent.com` failed before repository execution with temporary DNS resolution failure;
- GitHub connector reads/writes are available and can read exact files/recursive Git data at pinned commit `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`;
- PR #165 is confirmed open/draft at exact head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; connector reports `mergeable=false`;
- the retained exact-gate manifest confirms strict/thaw subgate already completed at the pinned source: 31/31 distinct tests PASS + compileall PASS; remaining gate is the complete LAB-080→086 real-ledger suite, unsafe seed, full compileall and final security/reconciliation audit;
- this runtime exposes no supported automated bridge from connector-fetched GitHub blobs into the local filesystem. Reconstructing the remaining 60+ security-critical source/test closure by model/manual reserialization would violate the manifest's byte-exact reconstruction discipline, so no such run was counted and no new LAB-086 behavioral/compile PASS is claimed.

Completed the recorded distinct fallback and froze `WITNESS_MEMBERSHIP_CROSSLOG_RECOVERY_BEACON_OBSERVATION_SEMANTIC_ANTICOPY_COMPROMISE_ADJUDICATION_V1_FROZEN` in `research/2026-09-09-witness-membership-crosslog-recovery-beacon-observation-semantic-anticopy-compromise-adjudication-v1.md`, main commit `e897382ecc7669fabf673975c142727432abf931`; #178 comment `5592056608` records the result.

Key decisions:
- historical witness checkpoints retain the witness membership epoch/denominator under which they were accepted; partition, retirement or later membership shrink cannot silently discard dissent or recalculate old quorum;
- cross-log anchor promises bind an exact destination log/key/trust epoch and deadline; destination compromise/replacement does not cancel the promise, and successor destinations cannot retroactively satisfy it without a pre-deadline independently retained supersession;
- threshold-beacon round failure proves availability failure only; attributable member nonparticipation requires a prior obligation plus a frozen independent collector denominator and authenticated complete observation commitments, with collector equivocation handled explicitly;
- semantic-attester anti-copy uses commit-before-reveal over exact challenge/input/verdict/output/evidence/provenance digests; deterministic convergence remains desirable, while pre-commit collusion remains a separate provenance/control-domain problem;
- compromise effective time is adjudicated independently of the affected provenance authority; moving a boundary later requires stricter recovery/higher-root evidence because it rehabilitates history, and a compromised adjudication threshold requires out-of-band recovery;
- frozen 64-case RED-first matrix across witness membership continuity, cross-log destination recovery, beacon observation completeness, semantic anti-copy timing and compromise-boundary adjudication.

Primary donors: RFC 9162; Chrome CT log lifecycle; transparency.dev witness retained-checkpoint model; drand threshold/catch-up/resharing; Sigstore transparency/TUF compromise-time semantics; TUF out-of-band Root recovery.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution of the complete real-ledger closure.
- Direct container Git/raw transport is unavailable due DNS resolution failure.
- Connector can fetch exact source, but there is no current supported automated connector-to-local materialization path; manual/model reserialization of the large security-critical closure is prohibited by the retained byte-hash gate.
- PR #165 must remain draft until branch-local dependency-blob verification, complete real-schema LAB-086 tests, unsafe expected-failure seed, compileall, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093 and LAB-094..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: if an automated exact-source path becomes available, reconstruct/check out pinned executable source `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` / PR head lineage, verify every dependency/test blob against `research/2026-08-27-lab086-exact-gate-manifest.md`, execute every normal LAB-086 real-schema test, run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure, run full compileall, then perform final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **historical policy snapshot availability and garbage-collection safety + witness/collector identity-key rollover without continuity laundering + cross-log proof survivability under hash/key algorithm migration + challenge/result confidentiality before semantic-attester reveal + appeal/finality semantics for compromise-boundary adjudication**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability/evidence architecture through witness membership continuity, cross-log destination recovery, beacon observation completeness, semantic anti-copy timing and compromise-boundary adjudication frozen; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen as recorded in their issues; exact executable gates pending.
