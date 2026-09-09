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
- direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` was re-probed and failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes are available;
- PR #165 remains `open`/`draft` at exact head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; no draft/merge-state change was attempted;
- retained prior evidence still says the strict/thaw subgate passed on pinned executable source; remaining LAB-086 gate is complete LAB-080→086 real-ledger execution, unsafe expected-failure seed, full compileall and final security/reconciliation/conflict audit;
- no supported automated connector-to-local exact-source materialization path was observed, so no large security-critical source closure was manually/model reserialized and no new LAB-086 behavioral/compile PASS is claimed.

Completed the recorded distinct fallback and froze `EMERGENCY_ROOT_ANTI_AMPLIFICATION_PROMISE_GC_MULTIBEACON_GOVERNANCE_ADJUDICATOR_CONFIDENTIALITY_PQ_STATE_MACHINE_V1_FROZEN` in `research/2026-09-09-emergency-root-anti-amplification-promise-gc-multibeacon-governance-adjudicator-confidentiality-pq-state-machine-v1.md`, main commit `3bf8335bf93eba50fc75cc630693d57a25a3edee`; #178 comment `5600996424` records the result.

Key decisions:
- an authentic dormant-root liveness challenge is not automatically safe to execute: accepted challenges also bind cost/rate-limit class and anti-replay state; duplicate/replayed challenges must not trigger repeated expensive ceremonies, quota survives restart/reconnect, and verifier-caused rate exhaustion cannot become member-loss evidence;
- simultaneous member compromise does not authorize the incumbent compromised quorum to declare itself clean. Recovery freezes an independent recovery denominator before observing availability; threshold cannot be lowered after seeing which members responded;
- promise GC requires immutable predecessor population roots, exact conservation, terminal/carried commitments, namespace/version binding and archive-sufficient historical proof. `CURRENT_NON_MEMBERSHIP != HISTORICAL_NON_EXISTENCE`;
- beacon enrollment/removal is a versioned governance action with a precommitted future boundary. Correlated source outage cannot cause post-reveal source removal, denominator laundering, convenient retries or emergency-source enrollment for the same decision;
- copy-domain adjudication itself uses fixed independent quorum and confidentiality-aware evidence handling. Inaccessible required confidential evidence yields insufficient assurance, not silent denominator reduction; appeals create successor generations rather than rewriting old verdicts;
- transparency mirror count is not witness independence. Historical verification must retain entry/inclusion/checkpoint/consistency/trust-root/witness lineage across Rekor sharding/retirement. TUF-style metadata expiry remains a freshness boundary offline; lack of clock becomes `FRESHNESS_UNPROVEN`, not expiry bypass;
- PQ/hybrid retry/resumption/0-RTT uses the rule `RETRY != AUTHORITY_TO_WEAKEN_CRYPTO_POLICY`: a failed 0-RTT attempt may retry 1-RTT, but the logical operation retains its required PQ/hybrid floor; old resumption tickets cannot override a stricter current policy and consequential 0-RTT requires exact replay-safe semantics;
- frozen 40-case RED-first matrix across emergency-root anti-amplification/recovery, promise GC/historical non-membership, beacon governance/correlated outage, adjudicator independence/confidentiality, and transparency/TUF/PQ retry-state downgrade.

Primary donors: RFC 8446 / TLS 1.3 and RFC 9846 0-RTT replay/retry semantics; Sigstore Rekor security/sharding/auditing docs; TUF metadata expiry/rollback model; drand resharing specification and 2025 v2 DKG-control post-mortem.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution of the complete real-ledger closure.
- Direct container Git/raw transport is unavailable in this run due DNS resolution failure.
- Connector can read/write repository content, but no supported automated connector-to-local materialization path for the full exact executable closure was observed; manual/model reserialization of the large security-critical closure remains prohibited by the retained byte-hash gate.
- PR #165 must remain draft until branch-local dependency-blob verification, complete real-schema LAB-086 tests, unsafe expected-failure seed, compileall, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093 and LAB-094..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: if an automated exact-source path becomes available, reconstruct/check out pinned executable source `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` / PR head lineage, verify every dependency/test blob against `research/2026-08-27-lab086-exact-gate-manifest.md`, execute every normal LAB-086 real-schema test, run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure, run full compileall, then perform final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **challenge-budget authority rollover and distributed rate-limit consistency under partition + promise-GC archive witness quorum and accumulator parameter compromise/migration + beacon governance emergency-policy abuse and cross-beacon dependency attestation + confidential adjudication threshold-privacy/selective-opening and reviewer revocation + transparency gossip split-view evidence retention and PQ resumption-ticket key/algorithm lifecycle across policy deprecation**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability/evidence architecture now also covers challenge anti-amplification and independent recovery under simultaneous compromise, GC-safe historical promise non-membership, versioned multi-beacon governance/correlated-outage handling, confidential independent adjudication, transparency/TUF offline survivability, and PQ retry/resumption/0-RTT downgrade resistance; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen as recorded in their issues; exact executable gates pending.
