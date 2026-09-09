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

Current-run capability/state probe:
- direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes remain available;
- PR #165 is confirmed `open`, `draft` at exact head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; no draft/merge-state change was attempted;
- retained prior evidence still says the strict/thaw subgate passed 31/31 distinct tests + compileall on pinned executable source; remaining LAB-086 gate is the complete LAB-080→086 real-ledger suite, unsafe expected-failure seed, full compileall and final security/reconciliation/conflict audit;
- no supported automated connector-to-local exact-source materialization path was observed, so no large security-critical source closure was manually/model reserialized and no new LAB-086 behavioral/compile PASS is claimed.

Completed the recorded distinct fallback and froze `WITNESS_TIME_PROOFCLOSURE_ESCROW_ZK_MIGRATION_V1_FROZEN` in `research/2026-09-09-witness-time-proofclosure-escrow-zk-migration-v1.md`, main commit `9ec40e0ced916b29a771d54e7a4c69a6220227d6`; #178 comment `5594296110` records the result.

Key decisions:
- historical witness/checkpoint assurance keeps its original witness-policy denominator, log identity and key epoch. Later witness loss or replacement cannot retroactively shrink historical quorum requirements;
- a survivable historical checkpoint package needs the exact signed checkpoint plus historical policy/denominator and enough consistency ancestry/material to reproduce the append-only relation; retaining only a digest is insufficient for positive anti-GC authority;
- Byzantine multi-time-source aggregation precommits eligible population, denominator, threshold and aggregation policy before observing responses; it evaluates authenticated intervals/order evidence and source independence rather than naively averaging scalar timestamps or adaptively dropping inconvenient sources;
- proof-closure parser/generator migration creates a new immutable generation linked to the exact authenticated source frontier and predecessor. Reproducible output is useful build-relation evidence but does not by itself prove parser/generator semantic correctness; decision-relevant interpretation differences require explicit equivalence adjudication;
- proactive escrow share refresh is epoch-atomic and distinct from membership/threshold reconfiguration. Offline members do not justify post-observation threshold reduction, runtime rollback must not resurrect retired share epochs, and refresh cannot erase recorded prior threshold compromise;
- ZK proof validity is relative to an exact circuit/predicate, verifier policy, proof-system version and parameter/SRS epoch. Credible setup-parameter compromise reopens current reliance; successor parameters/proof systems protect successor evidence only unless the underlying authenticated witness/source survives and is re-proved under a semantically equivalent successor predicate;
- frozen 40-case RED-first matrix across witness/checkpoint survivability, Byzantine time aggregation, proof-closure parser/generator migration, escrow refresh/rollback/offline-member handling, and ZK setup/proof-system migration.

Primary donors: RFC 9162; IETF Roughtime `draft-ietf-ntp-roughtime-19`; NIST Multi-Party Threshold Cryptography; Ethereum KZG ceremony / Perpetual Powers of Tau.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution of the complete real-ledger closure.
- Direct container Git/raw transport is unavailable in this run due DNS resolution failure.
- Connector can read/write repository content, but no supported automated connector-to-local materialization path for the full exact executable closure was observed; manual/model reserialization of the large security-critical closure remains prohibited by the retained byte-hash gate.
- PR #165 must remain draft until branch-local dependency-blob verification, complete real-schema LAB-086 tests, unsafe expected-failure seed, compileall, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093 and LAB-094..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: if an automated exact-source path becomes available, reconstruct/check out pinned executable source `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` / PR head lineage, verify every dependency/test blob against `research/2026-08-27-lab086-exact-gate-manifest.md`, execute every normal LAB-086 real-schema test, run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure, run full compileall, then perform final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **checkpoint-package archival denominator and positive anti-GC proof + Byzantine time-source membership recovery after authority compromise + proof-closure semantic-diff attestation and canonical corpus versioning + escrow refresh concurrency/epoch-fork adjudication + ZK ceremony transcript availability, contributor-independence evidence, and recursive proof renewal across parameter deprecation**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability/evidence architecture now also covers historical witness/checkpoint survivability, Byzantine time-source denominator discipline, immutable parser/generator proof-closure migration, proactive escrow refresh/rollback/offline-member semantics, and ZK setup/parameter/proof-system migration; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen as recorded in their issues; exact executable gates pending.
