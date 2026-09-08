# Current Lab State

Last updated: 2026-09-08

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; keep draft and do not merge without the exact retained gate.
- Other open drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and all active PRs; resumed LAB-086 first.

Current-run capability probe:
- `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab-auto32` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes and web research remain available;
- PR #165 remains open/draft at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, connector read `mergeable=false`;
- therefore no new LAB-086 behavioral/compile PASS is claimed and no draft/merge state was changed.

Completed the recorded distinct fallback and froze `FRESHNESS_PUBLICATION_OBLIGATION_LATESTNESS_EVIDENCE_COMPLETENESS_AUTHENTICATED_TIME_QUORUM_DISCOVERY_REGISTRY_V1_FROZEN` in `research/2026-09-08-freshness-publication-obligation-latestness-evidence-completeness-authenticated-time-quorum-discovery-registry-v1.md`, main commit `7fc094eb0f31ad5225de9983a8c4b9ed5f2eb38e`; #178 comment `5584359058` records the result.

Key decisions:
- `NO_FRESHNESS_STATEMENT_OBSERVED != FRESHNESS_OMISSION_PROVEN`; bounded non-publication becomes positive misbehavior evidence only after a retained independently provable publication promise/deadline (CT/MMD-style).
- Silence before admission/promise remains `LATESTNESS_EVIDENCE_ISSUANCE_UNKNOWN`; a compromised self-publisher can suppress before issuing its own promise, so critical transitions should separate admission from publication authority.
- periodic freshness schedules are authenticated/versioned and cannot be weakened retroactively; a missed deadline can prove publication-liveness failure but not reveal the hidden semantic generation.
- `DiscoveryRegistryV1` is the authenticated denominator for discovery/mirror/witness channels; timeout, endpoint/key rotation or local config deletion is not retirement, and endpoint count is not independent control-domain count.
- `AUTHENTICATED_TIME != CORRECT_TIME`; consequential expiry/deadline appraisal uses a versioned quorum of independent time-control domains over authenticated uncertainty intervals.
- NTS/signatures authenticate provenance/integrity, while RFC 8633/RFC 5905-style diverse-source clustering/outlier rejection supplies the separate semantic robustness layer; no valid quorum => `CURRENT_AUTHORITY_LATESTNESS_UNKNOWN` for consequential operations.
- one far-future/far-past source must not alone force global expiry/freeze when the active quorum policy is designed to tolerate that failure domain.
- post-facto time-key compromise reopens current reliance for dependent freshness decisions without rewriting historical receipts.
- frozen a 48-case RED-first matrix covering publication obligations, issuance completeness, discovery-registry denominator laundering, time-source rollback/equivocation/outliers, and offline catch-up composition.

Primary donors: RFC 9162 SCT/MMD, TUF freeze/rollback/expiration, Uptane secure-time compromise guidance, RFC 8915 NTS, RFC 8633/RFC 5905 multi-source/falseticker selection, Roughtime nonce-bound signed uncertainty intervals/chaining.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution.
- Direct git transport failed in this run before repository execution with DNS resolution failure.
- PR #165 must remain draft until branch-local dependency-blob verification, retained strict/thaw subgate, real-schema LAB-086 tests, compileall, unsafe expected-failure seed, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093 and LAB-094..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: if exact branch source execution becomes available, check out/reconstruct PR head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, verify exact branch-local source/blob lineage, execute the retained strict/thaw subgate (alternate-UNIQUE, primary-key/history/proof replacement, NULL identities, minimal thaw, conflict algorithms), compileall, exact branch-local LAB-080→086 dependency-blob verification, every normal LAB-086 real-schema test, unsafe legacy-promotion expected-failure seed, and final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **freshness obligation authority lifecycle / admission-publication atomicity / omission-proof transparency / time-quorum membership rotation and cross-source common-mode provenance**. Define who can issue/cancel/supersede `FreshnessPublicationPromiseV1`, how admission and promise creation survive crash/partition without creating unprovable accepted events, how omission proofs themselves are transparently/witnessed so a publisher cannot selectively show breach evidence, and how time-source independence is authenticated when nominally separate clocks share upstream reference, signer, cloud/account, firmware or operator control. Preserve `silence -> UNKNOWN` unless an independently retained bounded obligation exists.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact full executable gate + conflict audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability through anti-freeze/freshness-publication/time-quorum contracts frozen; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen as recorded in their issues; exact executable gates pending.
