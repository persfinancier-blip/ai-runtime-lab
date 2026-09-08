# Current Lab State

Last updated: 2026-09-08

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; keep draft and do not merge without the exact retained gate.
- Other open draft/IN_PROGRESS PRs: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected current open PRs and PR #165; resumed LAB-086 first.

Current-run capability probe:
- `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab-auto26` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes and web research remain available;
- PR #165 remains open/draft at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, current connector read `mergeable=false`;
- therefore no new LAB-086 behavioral/compile PASS is claimed and no draft/merge state was changed.

Completed the recorded distinct fallback and froze `SOURCE_INVENTORY_AUTHORITY_KEY_LIFECYCLE_SOURCE_IDENTITY_ROTATION_FRONTIER_FRESHNESS_PROMISE_INDEPENDENCE_V1_FROZEN` in `research/2026-09-08-source-inventory-authority-key-lifecycle-source-identity-rotation-frontier-freshness-promise-independence-v1.md`, main commit `2ea62b4ba5f927f37a7a034e48a8a629cfabd0ac`; #178 comment `5579684546` records the result.

Key decisions:
- `VALID_SIGNATURE != CURRENT_AUTHORITY != SAME_LOGICAL_SOURCE != FRESH_FRONTIER != INDEPENDENT_INGESTION_OBLIGATION`;
- source-inventory authority and per-source identity authority are separate roles; a source cannot sign itself out of the required-source denominator;
- `SOURCE_KEY_ROTATION != SOURCE_RETIREMENT != NEW_LOGICAL_SOURCE`; stable logical source identity is independent of rotating keys, workload instances, hostnames and epochs;
- inventory/source authority rotations use monotonic generations with predecessor+successor authorization; self-authorized and skipped-generation replacements fail closed;
- planned private-key retirement preserves public verification history; compromise intervals downgrade only dependent evidence, and unknown compromise onset cannot silently preserve trusted historical status;
- a new source key/epoch must prove continuity to the same logical source and carry unresolved promises/gaps/contradictions forward; `NEW_EPOCH != CLEAN_SLATE`;
- per-monitor `TrustedSourceFrontierV1` rejects lower authority generations/epochs/frontiers and same-frontier conflicting digests; wall-clock-newer does not mean frontier-fresher;
- monitor catch-up reconstructs inventory authority -> inventory -> source authority chains -> retained frontiers -> promise obligations -> current frontiers -> log coverage, in that order;
- `IngestionPromiseAuthorityV1` is separate from log authority; explicit P0..P3 assurance profiles distinguish self-promise from independent admission/witness authority;
- a retained producer-signed promise can prove breach of that promise, but a producer that controls both log and sole promise issuance can selectively suppress promises, so absence of a promise is not completeness proof;
- frozen a 48-case RED-first matrix spanning inventory/source authority lifecycle, denominator laundering, epoch/frontier rollback/equivocation, promise independence, catch-up/crash and late contradiction reopening.

Primary donors: TUF sequential root rotation + rollback protection; SPIFFE stable trust-domain identity with rotating bundles; NIST SP 800-57 historical verification-key lifecycle; RFC 9162 signed inclusion promises/monitors; RFC 9943 Issuer vs Transparency Service separation.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution.
- Direct git transport failed in this run before repository execution with DNS resolution failure.
- PR #165 must remain draft until branch-local dependency-blob verification, retained strict/thaw subgate, real-schema LAB-086 tests, compileall, unsafe expected-failure seed, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-088 still needs supported-integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 exact implementation must compose all frozen capability/delegation/revocation/lease/handoff/provider-fence/receipt/historical-trust/archive/verifier/conformance/oracle/publication/witness/recovery/freshness/secure-time/rebootstrap/convergence/evidence/continuous-assurance/checkpoint/source-ingestion/source-authority contracts with LAB-087 isolation; none of the design freezes substitute for executable proof.

## Exact next action
LAB-086 first: if exact branch source execution becomes available, check out/reconstruct current PR head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, verify exact branch-local source/blob lineage, then execute the retained strict/thaw subgate (alternate-UNIQUE, primary-key/history/proof replacement, NULL identities, minimal thaw, conflict algorithms), compileall, exact branch-local LAB-080→086 dependency-blob verification, every normal LAB-086 real-schema test, unsafe legacy-promotion expected-failure seed, and final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **source/promise authority transparency and compromise-notification propagation / conflicting authority views / post-facto completeness invalidation**. Define how monitors learn source-inventory, source-identity and ingestion-promise authority revocations/compromise notices with bounded freshness; how same-generation conflicting authority views are exposed through transparency/witnesses rather than resolved by LWW; how offline monitors recover missed revocations; and how a late compromise notice invalidates current reliance on an earlier completeness verdict without rewriting the historical verdict/receipt.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact full executable gate + conflict audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; source-authority/promise-independence plus checkpoint/source-ingestion and prior capability/recovery/convergence/continuous-assurance contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; retained-authority graph contracts frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; activation implementation/capability authority contracts frozen.
