# Current Lab State

Last updated: 2026-09-08

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; keep draft and do not merge without the exact retained gate.
- Other open drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and PR #165; resumed LAB-086 first.

Current-run capability probe:
- `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab-auto37` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes and web research remain available;
- PR #165 remains open/draft at exact head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; connector reports `mergeable=false`;
- no new LAB-086 behavioral/compile PASS is claimed and no draft/merge state was changed.

Completed the recorded distinct fallback and froze `INDEPENDENCE_REGISTRY_CHALLENGE_REPAIR_RENEWAL_PQ_MIGRATION_V1_FROZEN` in `research/2026-09-08-independence-registry-challenge-repair-renewal-pq-migration-v1.md`, main commit `044cbd6352c07286557a0d32ef9947b171ddad90`; #178 comment `5588328738` records the result.

Key decisions:
- `REGISTRY_MEMBERSHIP != INDEPENDENCE_PROVEN`; registry lifecycle authority, domain evidence producers, challenge schedulers/verifiers and recovery roots should remain separable;
- member retirement does not retroactively erase a failed/compromised member from the historical denominator; track historical required denominator, current active denominator and currently verified independent denominator separately;
- replacement domains create a new membership generation and must prove independence rather than inherit the retired member's status;
- challenge population must be committed before randomness disclosure; scheduler-local randomness alone is insufficient when scheduler/operator collusion is in scope;
- high-assurance challenge selection should bind epoch + committed population to independently contributed/unbiasable-after-commit randomness, with at least one contribution unknown to storage before commitment;
- erasure repair has two independent success criteria: reconstructability (`>=k` valid shares) and restoration of the policy-required independent destructive-domain denominator;
- restoring share count under common destructive control yields `RECONSTRUCTABLE_BUT_INDEPENDENCE_DEGRADED`, not full repair;
- renewal-authority compromise recursively reopens current reliance while preserving append-only historical receipts; a compromised renewal authority cannot self-bootstrap a trusted successor;
- long-lived classical -> hybrid/PQ evidence migration must overlap while classical bindings remain trustworthy; hybrid acceptance semantics must be explicit, with AND-style creation/renewal preferred for long-term assurance to avoid downgrade;
- frozen a 48-case RED-first matrix across registry lifecycle, anti-collusion challenges, denominator-safe repair, renewal-authority compromise and PQ/hybrid transition.

Primary donors: RFC 4998 Evidence Record Syntax; current NIST Post-Quantum Cryptography guidance/FIPS 203/204/205; NIST IR 8547 transition terminology; Tahoe-LAFS k-of-N survivability mechanisms.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution.
- Direct git transport failed in this run before repository execution with DNS resolution failure.
- PR #165 must remain draft until branch-local dependency-blob verification, retained strict/thaw subgate, real-schema LAB-086 tests, compileall, unsafe expected-failure seed, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093 and LAB-094..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: if exact branch source execution becomes available, check out/reconstruct PR head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, verify exact branch-local source/blob lineage, execute the retained strict/thaw subgate (alternate-UNIQUE, primary-key/history/proof replacement, NULL identities, hidden-rowid collision/sentinel, minimal thaw, conflict algorithms), compileall, exact branch-local LAB-080→086 dependency-blob verification, every normal LAB-086 real-schema test, unsafe legacy-promotion expected-failure seed, and final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **independence-registry authority compromise recursion / randomness-beacon availability and withholding / concurrent repair and stale-manifest race safety / PQ verifier diversity and hybrid downgrade resistance**. Define how registry authority compromise affects already admitted members, how challenge rounds behave when randomness contributors withhold after population commitment, how concurrent repair jobs avoid placing replacement shares using stale denominator/provenance state, and how verifier/implementation monoculture or a compromised PQ verifier affects hybrid evidence without silently falling back to classical-only acceptance.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact full executable gate + conflict audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability through independence-registry/challenge-anti-collusion/denominator-safe-repair/renewal-PQ-migration contracts frozen; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen as recorded in their issues; exact executable gates pending.
