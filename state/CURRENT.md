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

Completed the recorded distinct fallback and froze `REPLICA_AUDIT_RECEIPT_TRANSPARENCY_CONFIDENTIAL_REAUDIT_DESTRUCTION_PQ_RENEWAL_V1_FROZEN` in `research/2026-09-09-replica-audit-receipt-transparency-confidential-reaudit-destruction-pq-renewal-v1.md`, main commit `dce31af98ee2457065ddef27014a6a27ae3a56f7`; #178 comment `5596240437` records the result.

Key decisions:
- replica labels and fresh possession challenges do not prove destructive/control-domain independence. Independence is an authenticated topology claim with a freshness interval; later proof of shared domain marks the affected historical interval `FALSE_INDEPENDENCE_PROVEN`. A later clean audit can restore future eligibility but cannot erase historical co-failure evidence or rewrite the old denominator;
- ingress acceptance receipts are themselves consequential evidence and must be transparently logged/cross-logged. Positive omission requires an authentic receipt/promise, sufficiently late authenticated checkpoint, canonical non-inclusion/exhaustive monitor evidence, and consistency ancestry. 404, timeout, failed lookup, stale checkpoint, or partial-mirror absence remain `NONINCLUSION_NOT_PROVEN`;
- confidential corpus auditor compromise creates immutable audit generations. Same-corpus re-audit must bind the exact predecessor committed population, including hidden cases; replacement auditors signing an old result without independent re-execution do not count as re-audit; a successor pass never erases predecessor compromise evidence;
- destruction evidence is retained separately from secret material. Assurance classes distinguish logical deletion, device sanitization, crypto-erasure and all-copy-domain accounting; signed deletion assertion alone cannot prove all copies unrecoverable. Privacy/secrets minimization narrows authenticated audit metadata rather than deleting evidence while retention/dependency obligations remain;
- PQ hybrid combiner semantics are authenticated and explicit (`BOTH_REQUIRED`, PQ-required/classical-optional, etc.); `HYBRID_PRESENT != HYBRID_STRONG`. Algorithm deprecation has authenticated effective-time semantics, and long-term renewal must bind original semantic payload, predecessor lineage, current policy and propagated degradation. A PQ wrapper over invalid predecessor semantics/provenance does not repair truth;
- frozen 40-case RED-first matrix across replica audit/revocation, receipt transparency/non-inclusion, confidential re-audit, destruction evidence/minimization and PQ hybrid/deprecation/renewal.

Primary donors: RFC 9162; NIST SP 800-57 Part 1; NIST FIPS 203/204/205; NIST PQ transition guidance; NIST CSWP 39 crypto-agility guidance.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution of the complete real-ledger closure.
- Direct container Git/raw transport is unavailable in this run due DNS resolution failure.
- Connector can read/write repository content, but no supported automated connector-to-local materialization path for the full exact executable closure was observed; manual/model reserialization of the large security-critical closure remains prohibited by the retained byte-hash gate.
- PR #165 must remain draft until branch-local dependency-blob verification, complete real-schema LAB-086 tests, unsafe expected-failure seed, compileall, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093 and LAB-094..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: if an automated exact-source path becomes available, reconstruct/check out pinned executable source `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` / PR head lineage, verify every dependency/test blob against `research/2026-08-27-lab086-exact-gate-manifest.md`, execute every normal LAB-086 real-schema test, run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure, run full compileall, then perform final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **replica-audit authority compromise/rollover and challenge-transcript anti-replay + receipt-log witness quorum/gossip and log-retirement promise survivability + confidential re-audit independence/challenge secrecy under compromised auditor sets + destruction-inventory anti-omission and backup-domain discovery + PQ migration-attestation verifier diversity, algorithm-policy rollback protection and composite/hybrid downgrade across archived evidence**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability/evidence architecture now also covers replica-audit freshness/false-independence revocation, transparent receipt/non-inclusion evidence, confidential re-audit generations, destruction-evidence minimization/assurance classes, and PQ hybrid/deprecation/long-term renewal boundaries; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen as recorded in their issues; exact executable gates pending.
