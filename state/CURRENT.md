# Current Lab State

Last updated: 2026-09-08

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; keep draft and do not merge without the exact retained gate.
- Other open draft/IN_PROGRESS PRs: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and PR #165; resumed LAB-086 first.

Current-run capability probe:
- `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab-auto31` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes and web research remain available;
- PR #165 remains open/draft at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, connector read `mergeable=false`;
- therefore no new LAB-086 behavioral/compile PASS is claimed and no draft/merge state was changed.

Completed the recorded distinct fallback and froze `AUTHORITATIVE_LATEST_GENERATION_DISCOVERY_ANTI_FREEZE_MIRROR_WITNESS_AVAILABILITY_V1_FROZEN` in `research/2026-09-08-authoritative-latest-generation-discovery-anti-freeze-mirror-witness-availability-v1.md`, main commit `a5a94b68d8b45fa16511111e2985a929c740b9a9`; #178 comment `5583588306` records the result.

Key decisions:
- `VALID_CHAIN != CURRENT_CHAIN != LATEST_CHAIN_KNOWN`; `NO_NEWER_GENERATION_OBSERVED != NO_NEWER_GENERATION_EXISTS`;
- a valid retained authority chain proves only an authenticated prefix, not that its terminal generation is latest; a mirror can freeze a client by serving a perfectly valid stale prefix without forging signatures;
- frozen explicit latestness states: `CURRENT_AUTHORITY_LATESTNESS_PROVEN_WITHIN_BOUND`, `CURRENT_AUTHORITY_LATESTNESS_UNKNOWN`, `CURRENT_AUTHORITY_STALE_PROVEN`, `CURRENT_AUTHORITY_EQUIVOCATION_CONFLICT`;
- introduced `AuthorityFreshnessStatementV1`, `DiscoveryObservationV1`, `TrustedLatestnessFrontierV1`, and versioned `DiscoveryPolicyV1`;
- offline catch-up must chain from the relying party's retained frontier, reconstruct semantic authority/witness/quorum/key/compromise/checkpoint continuity, then appraise freshness/latestness; attacker-selected fresh starting checkpoints are insufficient;
- anti-freeze dissemination uses heterogeneous independent origin/mirror/transparency/witness/(optional cross-log)/time paths; endpoint count is not control-domain independence;
- a newer authenticated independent observation positively proves an older candidate stale; silence, 404, timeout, or lack of a newer observation does not prove no newer state exists;
- weak/unavailable trusted time does not collapse expiration into signature validity: time classes `T0..T4` are explicit and `T4_UNTRUSTED_OR_UNKNOWN_TIME` cannot support expiration-based latestness proof;
- mirrors distribute authenticated bytes but do not become semantic authority; witness/checkpoint freshness remains distinct from semantic adjudication truth;
- higher-generation hints create durable unresolved obligations; consequential mutation/authorization must not coerce `LATESTNESS_UNKNOWN` to current;
- frozen a 48-case RED-first matrix covering mirror withholding, weak time, freshness-role compromise, witness/checkpoint dissemination, offline selective truncation, discovery-denominator manipulation, and crash-safe latestness-frontier persistence.

Primary donors: TUF sequential root/rollback/expiration/freeze/mirror semantics; Uptane secure-time anti-freeze guidance; RFC 9162 checkpoint/monitor consistency; RFC 9943 multi-Transparency-Service receipt/dissemination semantics; RFC 8915 authenticated network time.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution.
- Direct git transport failed in this run before repository execution with DNS resolution failure.
- PR #165 must remain draft until branch-local dependency-blob verification, retained strict/thaw subgate, real-schema LAB-086 tests, compileall, unsafe expected-failure seed, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-088 still needs supported-integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 exact implementation must compose all frozen capability/delegation/revocation/lease/handoff/provider-fence/receipt/historical-trust/archive/verifier/conformance/oracle/publication/witness/recovery/freshness/secure-time/rebootstrap/convergence/evidence/continuous-assurance/checkpoint/source-ingestion/source-authority/source-transparency/compromise-adjudication/adjudicator-recovery-recursion/offline-catchup/anti-freeze-latestness contracts with LAB-087 isolation; none of the design freezes substitute for executable proof.

## Exact next action
LAB-086 first: if exact branch source execution becomes available, check out/reconstruct current PR head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, verify exact branch-local source/blob lineage, then execute the retained strict/thaw subgate (alternate-UNIQUE, primary-key/history/proof replacement, NULL identities, minimal thaw, conflict algorithms), compileall, exact branch-local LAB-080→086 dependency-blob verification, every normal LAB-086 real-schema test, unsafe legacy-promotion expected-failure seed, and final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **freshness-publication obligation / latestness-evidence issuance completeness / authenticated-time quorum and discovery-registry lifecycle**. Define how to prevent a compromised freshness producer from avoiding anti-freeze evidence simply by not issuing a new freshness statement, whether a bounded publication/MMD-like promise can make omission positively detectable, how discovery-channel membership/retirement is authenticated without denominator laundering, and how multiple authenticated time sources are appraised under disagreement/Byzantine outliers without allowing one bad clock to cause either permanent DoS or stale-current acceptance. Preserve the frozen rules that silence is generally `UNKNOWN`, not proof of safety; availability evidence is not semantic authority truth; and post-facto compromise invalidates current reliance without rewriting historical receipts.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact full executable gate + conflict audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; anti-freeze latestness plus prior offline authority/witness/quorum catch-up, adjudication transparency/recovery recursion/compromise provenance/source/transparency/checkpoint/convergence/capability contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; retained-authority graph contracts frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; activation implementation/capability authority contracts frozen.
