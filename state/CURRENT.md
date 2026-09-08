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

Completed the recorded distinct fallback and froze `POLICY_DEPENDENCY_ANTIOMISSION_CLOCK_MIGRATION_ESCROW_SELECTIVE_DISCLOSURE_V1_FROZEN` in `research/2026-09-09-policy-dependency-antiomission-clock-migration-escrow-selective-disclosure-v1.md`, main commit `f626639bfeb7c67b037f5d379c9d569f11eb9b35`; #178 comment `5593193924` records the result.

Key decisions:
- dependency index is a derived authenticated view over append-only evidence dependency events, not sole truth; policy GC requires a positive anti-omission proof against an authenticated complete admission/event frontier and CAS/serialization against concurrent evidence admission;
- effective-time boundaries use authenticated interval/order evidence (RFC 3161-style `genTime + accuracy + ordering` semantics), not ambient wall clock; overlapping uncertainty intervals without separate ordering evidence are `BOUNDARY_TIME_AMBIGUOUS`;
- partial archive recovery is judged against an explicit `ProofDependencyClosure`; redundant/regenerable derivative loss may be tolerated only when regeneration derives from authenticated retained state, while loss of non-regenerable historical bindings/policy bytes/pre-break renewal inputs blocks migration;
- threshold-decryption escrow share releases are append-only exposure events; abort after any valid share is `ESCROW_ABORTED_PARTIAL_EXPOSURE`, ciphertext threshold/membership cannot be lowered/reinterpreted after commitment, and pre-reveal threshold compromise downgrades confidential anti-copy assurance;
- adjudication selective disclosure must remain cryptographically linked to a complete authenticated evidence manifest; commitments/hashes prove binding rather than hidden semantics, and hidden decision-relevant evidence carries an explicit confidential-review assurance limitation;
- frozen 64-case RED-first matrix across dependency anti-omission, authenticated effective time, partial archive/migration closure, escrow compromise/abort, and selective disclosure/adjudication confidentiality.

Primary donors: RFC 9162, RFC 3161, RFC 4998, NIST Multi-Party Threshold Cryptography / NIST IR 8214C, RFC 9901.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution of the complete real-ledger closure.
- Direct container Git/raw transport is unavailable in this run due DNS resolution failure.
- Connector can read/write repository content, but no supported automated connector-to-local materialization path for the full exact executable closure was observed; manual/model reserialization of the large security-critical closure remains prohibited by the retained byte-hash gate.
- PR #165 must remain draft until branch-local dependency-blob verification, complete real-schema LAB-086 tests, unsafe expected-failure seed, compileall, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093 and LAB-094..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: if an automated exact-source path becomes available, reconstruct/check out pinned executable source `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` / PR head lineage, verify every dependency/test blob against `research/2026-08-27-lab086-exact-gate-manifest.md`, execute every normal LAB-086 real-schema test, run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure, run full compileall, then perform final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **dependency-event log equivocation/recovery and source-frontier survivability + multi-time-source anti-backdating/clock-authority rollover + proof-closure authority/versioning for regenerated evidence + proactive escrow share refresh/reconfiguration across key epochs + selective-disclosure/ZK predicate circuit provenance and verifier-policy lifecycle**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability/evidence architecture now also covers positive policy-dependency anti-omission, authenticated effective-time provenance, partial-loss proof-closure migration, escrow compromise/abort semantics, and selective-disclosure confidentiality; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen as recorded in their issues; exact executable gates pending.
