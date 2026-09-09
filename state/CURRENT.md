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
- PR #165 is confirmed `open`, `draft`, `mergeable=false` at exact head `ee210a47221b6df53f3518aa3af74f76c5b0122b`;
- retained prior evidence still says the strict/thaw subgate passed 31/31 distinct tests + compileall on pinned executable source; remaining LAB-086 gate is the complete LAB-080→086 real-ledger suite, unsafe expected-failure seed, full compileall and final security/reconciliation/conflict audit;
- no supported automated connector-to-local exact-source materialization path was observed, so no large security-critical source closure was manually/model reserialized and no new LAB-086 behavioral/compile PASS is claimed.

Completed the recorded distinct fallback and froze `DEPENDENCY_LOG_TIME_PROOFCLOSURE_ESCROW_ZK_LIFECYCLE_V1_FROZEN` in `research/2026-09-09-dependency-log-time-proofclosure-escrow-zk-lifecycle-v1.md`, main commit `b4318732b561ccce27e88a71f4a12b850577821c`; #178 comment `5593804610` records the result.

Key decisions:
- dependency-event truth lives in an authenticated append-only log; the materialized dependency index remains derived. Same-size/different-root checkpoints are equivocation, and recovery after log-key/operator compromise requires a new authenticated epoch/identity rather than silently redefining old history;
- positive anti-omission/GC authority requires a survivable reproducible source frontier. A retained root without complete authenticated event-prefix material is `FRONTIER_AUTHENTIC_BUT_NONEXHAUSTIVELY_REPRODUCIBLE`, not proof of no dependencies;
- consequential effective time uses a `TimeEvidenceSet`: authority/key epoch, nonce/challenge where supported, signed interval/radius, policy and ordering evidence. RFC3161-style overlapping uncertainty without stronger ordering is `TIME_ORDER_AMBIGUOUS`; Roughtime-style chaining is a donor for cryptographic after-order across independently governed sources;
- regenerated evidence is a new immutable object under a versioned `ProofClosureManifest` binding exact source frontier, inputs, parser/schema, algorithm/parameters, generator provenance, policy and predecessor evidence. The generator cannot be sole authority for semantic equivalence;
- proactive escrow share refresh is distinct from threshold/membership reconfiguration. Partial refresh is fail-closed, old/new shares are not assumed mixable, and refresh cannot erase exposure if threshold shares were already compromised;
- adjudication-grade ZK evidence binds exact predicate/circuit, public-input schema, setup/parameter epoch, prover/verifier provenance and verifier policy. `ZK_PROOF_VALID != CLAIM_POLICY_CORRECT`; circuit/verifier upgrades never retroactively reinterpret old proofs;
- frozen 40-case RED-first matrix across dependency-log/frontier, time provenance, proof regeneration, escrow refresh/reconfiguration and ZK lifecycle.

Primary donors: RFC 9162, RFC 3161, IETF Roughtime draft-ietf-ntp-roughtime-19, NIST IR 8214C / Threshold Cryptography.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution of the complete real-ledger closure.
- Direct container Git/raw transport is unavailable in this run due DNS resolution failure.
- Connector can read/write repository content, but no supported automated connector-to-local materialization path for the full exact executable closure was observed; manual/model reserialization of the large security-critical closure remains prohibited by the retained byte-hash gate.
- PR #165 must remain draft until branch-local dependency-blob verification, complete real-schema LAB-086 tests, unsafe expected-failure seed, compileall, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093 and LAB-094..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: if an automated exact-source path becomes available, reconstruct/check out pinned executable source `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` / PR head lineage, verify every dependency/test blob against `research/2026-08-27-lab086-exact-gate-manifest.md`, execute every normal LAB-086 real-schema test, run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure, run full compileall, then perform final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **dependency-log witness/checkpoint survivability and complete-frontier anti-omission under witness loss + Byzantine multi-time-source aggregation/independence denominator + proof-closure reproducible-generator provenance and parser migration + proactive escrow refresh authorization/rollback across offline members + ZK setup-ceremony/parameter compromise and proof-system migration semantics**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability/evidence architecture now also covers dependency-log equivocation/recovery, survivable source frontiers, multi-source authenticated time, versioned regenerated-proof closure, proactive escrow refresh/reconfiguration and ZK predicate/verifier lifecycle; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen as recorded in their issues; exact executable gates pending.
