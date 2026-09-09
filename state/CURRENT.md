# Current Lab State

Last updated: 2026-09-09

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; keep draft and do not merge without the exact retained gate.
- Other open drafts remain: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues/open PRs and resumed LAB-086 first.

Current-run capability/state:
- PR #165 remains `open`, `draft`, `mergeable=false` at exact head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; no draft/merge-state change was attempted;
- direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` was re-probed and failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes are available;
- retained prior evidence still says the strict/thaw subgate passed on pinned executable source; remaining LAB-086 gate is complete LAB-080→086 real-ledger execution, unsafe expected-failure seed, full compileall and final security/reconciliation/conflict audit;
- no supported automated connector-to-local exact-source materialization path was observed, so no large security-critical source closure was manually/model reserialized and no new LAB-086 behavioral/compile PASS is claimed.

Completed the recorded distinct fallback and froze `CHALLENGE_BUDGET_PROMISE_WITNESS_BEACON_DEPENDENCY_CONFIDENTIAL_ADJUDICATION_PQ_RESUMPTION_V1_FROZEN` in `research/2026-09-09-challenge-budget-promise-witness-beacon-dependency-confidential-adjudication-pq-resumption-v1.md`, main commit `2d225f1457c0164c1e4974d93036d00c7d74829d`; #178 comment `5601722551` records the result.

Key decisions:
- challenge-budget authority rollover is an authenticated lineage transition. Distributed partitions do not reset global expensive-work budget; allowed partition semantics are predeclared (for example fail-closed or signed preallocated shards), replay spend survives replica changes/restart, and verifier-caused budget exhaustion is not member-loss evidence;
- promise-GC completion requires an independent archive witness quorum over exact predecessor population, mapping and disposition roots. Historical queries name an exact historical generation/root; `CURRENT_NON_MEMBERSHIP != HISTORICAL_NON_EXISTENCE`. Accumulator/tree parameters and verifier/setup provenance are authenticated dependencies, and parameter compromise creates degradation + successor migration rather than history rewrite;
- beacon emergency policy is committed before reveal, cannot rewrite the current sample, and cannot use post-reveal discretionary source removal/enrollment/retry. `N_BEACONS != N_INDEPENDENT_BEACONS`: common cloud/operator/DKG/build/time/network dependencies are explicit independence evidence;
- confidential adjudication commits the complete policy-relevant evidence population before selective opening. Selective proofs establish authenticity of disclosed claims, not completeness/irrelevance of hidden claims. Threshold verdict authority and threshold evidence completeness are separate. Reviewer compromise/revocation degrades or triggers fresh re-audit; successor re-signing alone is not re-audit;
- transparency split-view evidence retains both conflicting signed checkpoints/views plus observation and trust-root lineage even after adjudication. Mirror count is not independent witness count;
- PQ/hybrid/TLS resumption tickets are predecessor-policy credentials. Current minimum crypto policy remains a floor: a ticket issued under an algorithm now below the floor may remain historical evidence but cannot authorize new resumed consequential use. Retry/ticket-key rotation/unknown-ticket fallback goes to a fresh compliant handshake or fail-closed, never below the current floor;
- frozen 40-case RED-first matrix across challenge budget/partition, promise archive/witnesses, beacon governance/dependencies, confidential adjudication/selective opening, and transparency/PQ resumption lifecycle.

Primary donors: RFC 9000 anti-amplification; TUF root rollover/rollback/freeze continuity; RFC 9162 STH/inclusion/consistency/split-view audit model; NIST IR 8213 + drand membership/DKG; RFC 9901 + W3C BBS selective disclosure; NIST threshold cryptography; RFC 9846 TLS resumption; NIST IR 8547 algorithm-transition vocabulary. IR 8213/8547 are draft-status donors; W3C BBS is Candidate Recommendation Draft.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution of the complete real-ledger closure.
- Direct container Git/raw transport is unavailable in this run due DNS resolution failure.
- Connector can read/write repository content, but no supported automated connector-to-local materialization path for the full exact executable closure was observed; manual/model reserialization of the large security-critical closure remains prohibited by the retained byte-hash gate.
- PR #165 must remain draft until branch-local dependency-blob verification, complete real-schema LAB-086 tests, unsafe expected-failure seed, compileall, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093 and LAB-094..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: if an automated exact-source path becomes available, reconstruct/check out pinned executable source `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` / PR head lineage, verify every dependency/test blob against `research/2026-08-27-lab086-exact-gate-manifest.md`, execute every normal LAB-086 real-schema test, run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure, run full compileall, then perform final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **distributed budget lease expiration/clock authority + witness archival availability under witness retirement and archive-domain loss + beacon dependency-attestation authority compromise/revocation + confidential evidence population commitment redaction/deletion requests without audit-history corruption + PQ resumption across cross-cluster ticket-key replication, server identity rotation, and crypto-policy clock/freshness failure**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability/evidence architecture now also covers distributed challenge-budget rollover/partition conservation, independent promise-GC archive witnesses and parameter migration, precommitted beacon emergency/dependency governance, confidential selective-opening/reviewer-revocation semantics, transparency split-view retention, and PQ/TLS resumption lifecycle across algorithm deprecation; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen as recorded in their issues; exact executable gates pending.
