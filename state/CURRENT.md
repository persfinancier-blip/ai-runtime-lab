# Current Lab State

Last updated: 2026-09-09

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; keep draft and do not merge without the exact retained gate.
- Other open drafts remain visible: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and PR #165; resumed LAB-086 first.

Current-run capability/state probe:
- direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes remain available;
- PR #165 is confirmed `open`, `draft`, `mergeable=false` at exact head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; no draft/merge-state change was attempted;
- retained prior evidence still says the strict/thaw subgate passed on pinned executable source; remaining LAB-086 gate is the complete LAB-080→086 real-ledger suite, unsafe expected-failure seed, full compileall and final security/reconciliation/conflict audit;
- no supported automated connector-to-local exact-source materialization path was observed, so no large security-critical source closure was manually/model reserialized and no new LAB-086 behavioral/compile PASS is claimed.

Completed the recorded distinct fallback and froze `REPLICA_AUTHORITY_RECEIPT_GOSSIP_REAUDIT_DESTRUCTION_PQ_DOWNGRADE_V1_FROZEN` in `research/2026-09-09-replica-authority-receipt-gossip-reaudit-destruction-pq-downgrade-v1.md`, main commit `be13f355bf2ed5d5445a6635d9612baef3db66de`; #178 comment `5596860806` records the result.

Key decisions:
- replica-audit authority is versioned by authenticated epoch. Later compromise degrades affected audit generations but cannot rewrite historical denominator/topology evidence; fresh challenges bind unpredictable nonce, exact replica, purpose, authority epoch, policy and deadline, so old responses cannot be replayed as fresh evidence;
- receipt acceptance is a signed promise bound to exact request, ingress/log key epochs and inclusion deadline. Positive omission requires a sufficiently late authenticated checkpoint plus canonical non-inclusion/exhaustive evidence. Witness quorum is evaluated against the historical witness-policy denominator; gossip exposes incompatible signed views but is not consensus. Log retirement cannot extinguish outstanding promises without fulfilled/archived evidence or authenticated supersession preserving their lineage;
- confidential re-audit counts independent re-executions/control domains, not signatures. A compromised set sharing one control domain does not multiply independence; auditor denominator is frozen before result observation; exact committed population including hidden cases carries forward; compromise of enough challenge custodians before reveal yields `CHALLENGE_SECRECY_COMPROMISED`;
- destruction completeness requires authenticated discovery of copy-generating domains across operational stores, backups, snapshots, archives, replicas, caches and export/wrap histories. `ALL_ENUMERATED_COPIES_DESTROYED != ALL_COPY_DOMAINS_ACCOUNTED_FOR`; later discovery of an omitted copy degrades the historical completeness claim rather than rewriting it;
- PQ migration attestation binds exact predecessor/successor crypto policies, hybrid combiner, effective boundary, verifier implementation/policy, independent verification evidence and predecessor degradation. Historical verification of an old algorithm is distinct from new consequential authorization; archived evidence cannot roll policy back or reinterpret a stronger combiner as a weaker one. Full renewal must carry original semantic payload, lineage and degradation;
- frozen 40-case RED-first matrix across replica authority anti-replay, receipt-log witness/gossip/retirement, confidential re-audit, destruction inventory anti-omission and PQ rollback/downgrade.

Primary donors: RFC 9162; NIST SP 800-57 Part 1 Rev. 5; FIPS 203/204/205; NIST IR 8547; NIST CSWP 39.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution of the complete real-ledger closure.
- Direct container Git/raw transport is unavailable in this run due DNS resolution failure.
- Connector can read/write repository content, but no supported automated connector-to-local materialization path for the full exact executable closure was observed; manual/model reserialization of the large security-critical closure remains prohibited by the retained byte-hash gate.
- PR #165 must remain draft until branch-local dependency-blob verification, complete real-schema LAB-086 tests, unsafe expected-failure seed, compileall, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093 and LAB-094..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: if an automated exact-source path becomes available, reconstruct/check out pinned executable source `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` / PR head lineage, verify every dependency/test blob against `research/2026-08-27-lab086-exact-gate-manifest.md`, execute every normal LAB-086 real-schema test, run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure, run full compileall, then perform final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **replica-audit authority recovery quorum and authority-policy rollback protection + receipt-log key rollover/witness-compromise recovery while preserving old promises + confidential challenge-generator provenance/anti-bias and leakage accounting + destruction-inventory source-authority compromise and negative-space coverage + PQ migration-attestation supply-chain provenance, verifier implementation compromise and algorithm-negotiation transcript downgrade resistance**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability/evidence architecture now also covers replica-audit authority rollover/anti-replay, receipt-log witness/gossip/retirement promise survivability, independent confidential re-audit, destruction-inventory anti-omission and PQ verifier rollback/downgrade boundaries; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen as recorded in their issues; exact executable gates pending.
