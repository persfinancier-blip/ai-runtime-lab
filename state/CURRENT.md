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
- direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes remain available;
- PR #165 is confirmed open/draft at exact head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; connector reports `mergeable=false`;
- retained prior evidence still says the strict/thaw subgate passed 31/31 distinct tests + compileall on the pinned executable source; the remaining LAB-086 gate is the complete LAB-080→086 real-ledger suite, unsafe expected-failure seed, full compileall and final security/reconciliation/conflict audit;
- no supported automated connector-to-local exact-source materialization path was observed, so no large security-critical source closure was manually/model reserialized and no new LAB-086 behavioral/compile PASS is claimed.

Completed the recorded distinct fallback and froze `POLICY_SNAPSHOT_ROLLOVER_CROSSLOG_MIGRATION_CONFIDENTIAL_REVEAL_ADJUDICATION_FINALITY_V1_FROZEN` in `research/2026-09-09-policy-snapshot-key-rollover-crosslog-migration-confidential-reveal-adjudication-finality-v1.md`, main commit `75e2b0d1ea6fd25b7ad6eda77016ee63ba0681f5`; #178 comment `5592621577` records the result.

Key decisions:
- historical consequential evidence binds exact immutable policy bytes/digest; `SUPERSEDED != GC_ELIGIBLE`; policy GC requires an authenticated complete dependency census and independently durable migration/retention evidence, and missing historical policy bytes fail closed rather than substituting current policy;
- witness/collector logical identity is distinct from key epoch; normal rollover requires predecessor+successor authorization, exact effective boundary and transparent non-equivocating publication; rollover/retirement never recomputes historical quorum denominators;
- cross-log proof packages retain source/destination log IDs, key epochs, parameters, checkpoints, proof bytes and crypto-policy lineage; signature/timestamp renewal is distinct from hash-tree renewal, and post-break rehashing without a pre-break independent anchor cannot restore historical authenticity;
- semantic commit-before-reveal now has explicit confidentiality phases, hiding commitments and optional independently governed threshold-decryption escrow; a committed non-reveal contributes no semantic verdict unless the predeclared escrow path opens the exact committed value;
- compromise-boundary adjudication now has immutable provisional/final/superseded/reopened/void states; ordinary appeal does not erase the prior decision, and moving a boundary later (rehabilitating distrusted history) requires stricter independent new evidence plus recovery/higher-root authorization;
- frozen 64-case RED-first matrix across policy snapshot/GC safety, identity-key rollover, cross-log crypto migration, confidential semantic reveal and adjudication appeal/finality.

Primary donors: TUF trust-chain/key-migration retention; RFC 9162 append-only checkpoint/log identity; RFC 4998 timestamp vs hash-tree renewal; NIST SP 800-57 key lifecycle/archive guidance.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution of the complete real-ledger closure.
- Direct container Git/raw transport is unavailable in this run due DNS resolution failure.
- Connector can read/write repository content, but no supported automated connector-to-local materialization path for the full exact executable closure was observed; manual/model reserialization of the large security-critical closure remains prohibited by the retained byte-hash gate.
- PR #165 must remain draft until branch-local dependency-blob verification, complete real-schema LAB-086 tests, unsafe expected-failure seed, compileall, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093 and LAB-094..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: if an automated exact-source path becomes available, reconstruct/check out pinned executable source `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` / PR head lineage, verify every dependency/test blob against `research/2026-08-27-lab086-exact-gate-manifest.md`, execute every normal LAB-086 real-schema test, run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure, run full compileall, then perform final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **policy-dependency index authority and positive anti-omission proof + key-rollover effective-time clock provenance + cross-log migration completeness under partial archive loss + threshold-decryption escrow compromise/abort semantics + adjudication evidence-disclosure confidentiality/selective disclosure**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability/evidence architecture now also covers historical policy/GC safety, identity-key rollover, cross-log crypto migration, confidential semantic reveal, and compromise-boundary adjudication appeal/finality; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen as recorded in their issues; exact executable gates pending.
