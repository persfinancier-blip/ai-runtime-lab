# Current Lab State

Last updated: 2026-09-07

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; keep draft and do not merge without the exact retained gate.
- Other open draft/IN_PROGRESS PRs observed this run: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected current open issues/PRs; resumed LAB-086 first.

Current-run capability probe:
- `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab-auto17` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes and web research remain available;
- therefore no new LAB-086 behavioral/compile PASS is claimed and PR #165 remains draft.

Completed the recorded distinct fallback and froze `TIME_FLOOR_RECOVERY_AUTHORITY_KEY_LIFECYCLE_POLICY_ROTATION_POISON_ADJUDICATION_EMERGENCY_GOVERNANCE_V1_FROZEN` in `research/2026-09-07-time-floor-recovery-authority-key-lifecycle-policy-rotation-poison-adjudication-emergency-governance-v1.md`, commit `0c85ea29cc5fe780f6c9df4f8902ee8f8f0bb239`; #178 comment `5575274582` records the result.

Key decisions:
- `VALID_RECOVERY_SIGNATURE != AUTHORIZED_RECOVERY_POLICY != PROVEN_POISONING != SAFE_REPLACEMENT_FLOOR`;
- `TimeFloorRecoveryPolicyV1` rotation requires threshold authorization under both predecessor and successor policy generations; successor self-authorization is forbidden;
- recovery key compromise/retirement is append-only historical status; unknown compromise onset yields `UNKNOWN_HISTORICAL_RECOVERY_AUTHORITY` wherever safety depends on that key;
- far-future/panic-sized discrepancy is a poison-suspicion trigger only; it cannot itself lower `TrustedTimeFloorV1`;
- `POISONING_PROVEN` requires reconstruction and defeat of the original floor-advance authority basis plus independently controlled replacement time evidence and adjudicator threshold closure;
- emergency recovery governance must be pre-bootstrapped, multi-party and control-domain independent; urgency does not authorize one-admin break glass;
- two incompatible fully valid recovery artifacts create `RECOVERY_FORK_DISPUTE_NO_MUTATION`; min/max/LWW/first-seen selection is forbidden;
- successful recovery creates a new authenticated generation and explicit supersession while retaining the poisoned decision/history;
- added a 60-case RED-first matrix across policy/key lifecycle, poison adjudication, replacement safety, emergency governance, fork/equivocation and crash/publication semantics.

Primary donors: TUF root-key rotation and fast-forward recovery; NIST SP 800-57 Pt1 Rev5 key lifecycle/compromise; RFC 3628 TSA compromise and dual-control recovery; RFC 5905 panic-offset behavior.

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

If exact execution remains unavailable, next distinct evidence task is **recovery-policy transparency bootstrap / offline root custody / total-loss governance-root reconstitution semantics**. Define whether and how `TimeFloorRecoveryAuthorityV1` can recover after loss/destruction/compromise of every ordinary and emergency recovery signer; distinguish legitimate organizational reconstitution from hostile root replacement; define offline root custody, archived predecessor evidence, transparency/publication requirements, out-of-band bootstrap, survivor/witness/court-or-charter style governance evidence if applicable, and the fail-closed state when no continuity proof remains. Do not silently invent a new root of trust.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact full executable gate + conflict audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; time-floor recovery-authority governance/key-lifecycle/poison-adjudication contract now also frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; retained-authority graph contracts frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; activation implementation/capability authority contracts frozen.
