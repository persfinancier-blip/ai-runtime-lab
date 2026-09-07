# Current Lab State

Last updated: 2026-09-07

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; current `get_pr_info` reports open/draft, `mergeable=false`; do not change draft/merge status without the exact retained gate.
- Other open draft/IN_PROGRESS PRs observed: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected current open PRs and PR #165.

Current-run capability probe:
- `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab-auto15` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes and web research remain available;
- therefore no new LAB-086 behavioral/compile PASS is claimed and PR #165 remains draft.

Completed the recorded distinct fallback and froze `FRESHNESS_CLOCK_AUTHORITY_SECURE_TIME_ROLLBACK_SUSPEND_LONG_OFFLINE_V1_FROZEN` in `research/2026-09-07-freshness-clock-authority-secure-time-rollback-suspend-long-offline-v1.md`, commit `43109203b1458f6da6e7029b0b877c2e539b38a6`; #178 comment `5574367954` records the result.

Key decisions:
- `AUTHENTICATED_TIME_SAMPLE != LOCAL_WALL_CLOCK != MONOTONIC_ELAPSED_TIME != CURRENT_AUTHORITY`;
- persist a nondecreasing `TrustedTimeFloorV1` atomically with the trusted activation/publication frontier; local wall time below the floor is rollback and cannot lower it;
- authenticated network time such as NTS may advance the floor only with retained uncertainty/delay bounds and policy-approved source identity/independence; it is not itself a durable anti-rollback store;
- suspend-aware elapsed time is required for freshness expiry, so a clock that pauses during suspend cannot extend authority;
- VM/filesystem snapshot restore invalidates local-only time continuity unless an external newer monotonic frontier/time source re-establishes it;
- RTC loss and long-offline operation retain historical verification but return current-authority unknown until fresh authenticated continuation is proved;
- once E+1 is authenticated, no clock rollback can revive E;
- crash recovery must preserve activation frontier + time floor + sample/checkpoint evidence atomically or fail closed;
- added an 80-case RED-first matrix for wall-clock rewind, snapshot rollback, suspend/resume, RTC loss, years-long offline, source disagreement/delay, crash atomicity and stale-epoch revival.

Primary donors: RFC 8915 NTS authenticated time/bootstrap guidance; RFC 3161 trusted timestamps; TUF monotonic version + expiration/freeze semantics; Linux `CLOCK_BOOTTIME` versus `CLOCK_MONOTONIC` suspend behavior.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution.
- Direct git transport failed in this run before repository execution with DNS resolution failure.
- PR #165 must remain draft until branch-local dependency-blob verification, retained strict/thaw subgate, real-schema LAB-086 tests, compileall, unsafe expected-failure seed, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-088 still needs supported-integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 exact implementation must compose all frozen capability/delegation/revocation/lease/handoff/provider-fence/receipt/historical-trust/archive/verifier/conformance/oracle/publication/witness/recovery/freshness/secure-time contracts with LAB-087 isolation; none of the design freezes substitute for executable proof.

## Exact next action
LAB-086 first: if exact branch source execution becomes available, check out/reconstruct current PR head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, verify exact branch-local source/blob lineage, then execute the retained strict/thaw subgate (alternate-UNIQUE, primary-key/history/proof replacement, NULL identities, minimal thaw, conflict algorithms), compileall, exact branch-local LAB-080→086 dependency-blob verification, every normal LAB-086 real-schema test, unsafe legacy-promotion expected-failure seed, and final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **secure-time source key lifecycle / time-source quorum independence / far-future poisoning recovery semantics**. Define authenticated time-source identity/key rotation and compromise-time history; independence/correlation requirements across time authorities and network paths; how a malicious or erroneous far-future sample that advanced `TrustedTimeFloorV1` can be recovered without permitting ordinary rollback; and whether recovery must require an explicit higher-order governance/appeal artifact rather than routine time samples.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact full executable gate + conflict audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; secure-time freshness/rollback/suspend/offline contract now also frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; retained-authority graph contracts frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; activation implementation/capability authority contracts frozen.
