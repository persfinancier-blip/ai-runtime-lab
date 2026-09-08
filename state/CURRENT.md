# Current Lab State

Last updated: 2026-09-08

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; keep draft and do not merge without the exact retained gate.
- Other open draft/IN_PROGRESS PRs: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected current open issues and PR #165; resumed LAB-086 first.

Current-run capability probe:
- `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab-auto29` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes and web research remain available;
- PR #165 remains open/draft at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, current connector read `mergeable=false`;
- therefore no new LAB-086 behavioral/compile PASS is claimed and no draft/merge state was changed.

Completed the recorded distinct fallback and froze `COMPROMISE_ADJUDICATION_TRANSPARENCY_WITNESS_QUORUM_QUARANTINE_REVIEW_RECOVERY_ROTATION_RECURSION_V1_FROZEN` in `research/2026-09-08-compromise-adjudication-transparency-witness-quorum-quarantine-review-recovery-rotation-recursion-v1.md`, main commit `bd87abdf493bdb31accb44ebf67154c164af2a3c`; #178 comment `5581694319` records the result.

Key decisions:
- `VALID_ADJUDICATION_SIGNATURE != CURRENT_ADJUDICATION_AUTHORITY != GLOBALLY_CONSISTENT_ADJUDICATION_VIEW != SEMANTICALLY_CORRECT_ADJUDICATION`;
- high-impact adjudications bind canonical immutable statements into append-only transparency; policy-required witness quorum is counted only after independence appraisal;
- witnesses establish checkpoint consistency/non-equivocation evidence, not truth of adjudication content; same-generation/different-digest is `ADJUDICATION_EQUIVOCATION_CONFLICT`, never LWW/newest-timestamp/majority-CDN resolution;
- post-facto witness compromise may reduce current usable quorum and force current-reliance re-appraisal while preserving historical receipts;
- a credible single detector may trigger scoped fail-closed quarantine, but quarantine deadline/TTL expiry never restores trust; independent bounded review is the liveness/anti-permanent-DoS path;
- normal recovery-root rotation requires predecessor-threshold + successor-threshold authorization, monotonic generation, predecessor-digest continuity and preserved control-domain independence; fresh keys under one compromised control domain do not constitute independent recovery;
- once predecessor threshold is suspected/proven compromised, normal predecessor authorization is no longer sufficient; use separately established exceptional recovery authority;
- a compromised adjudicator cannot self-attest health or self-authorize a trusted successor; affected prior adjudications are re-appraised over the evidence-backed compromise interval;
- recovery-root threshold compromise with no independent higher/out-of-band recovery anchor means same-lineage recovery is unproven and composes with external rebootstrap/new-lineage semantics rather than fabricated continuity;
- frozen 18 contradiction classes and a 48-case RED-first matrix spanning transparency/split views, quarantine review liveness, recovery ceremonies, and adjudicator/recovery-root compromise recursion.

Primary donors: RFC 9162 monitor/audit + consistency semantics; transparency.dev witness checkpoint cosigning/non-equivocation model; TUF versioned two-sided threshold root rotation/offline root custody; Sigstore threshold/distributed root and compromise/freshness threat model.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution.
- Direct git transport failed in this run before repository execution with DNS resolution failure.
- PR #165 must remain draft until branch-local dependency-blob verification, retained strict/thaw subgate, real-schema LAB-086 tests, compileall, unsafe expected-failure seed, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-088 still needs supported-integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 exact implementation must compose all frozen capability/delegation/revocation/lease/handoff/provider-fence/receipt/historical-trust/archive/verifier/conformance/oracle/publication/witness/recovery/freshness/secure-time/rebootstrap/convergence/evidence/continuous-assurance/checkpoint/source-ingestion/source-authority/source-transparency/compromise-adjudication/adjudicator-recovery-recursion contracts with LAB-087 isolation; none of the design freezes substitute for executable proof.

## Exact next action
LAB-086 first: if exact branch source execution becomes available, check out/reconstruct current PR head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, verify exact branch-local source/blob lineage, then execute the retained strict/thaw subgate (alternate-UNIQUE, primary-key/history/proof replacement, NULL identities, minimal thaw, conflict algorithms), compileall, exact branch-local LAB-080→086 dependency-blob verification, every normal LAB-086 real-schema test, unsafe legacy-promotion expected-failure seed, and final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **adjudication/recovery authority freshness distribution and offline relying-party catch-up under witness/key rotations**. Define witness-set membership authority, quorum-policy rotation, witness-key lifecycle and stale checkpoint handling, cross-log/checkpoint anchoring, missed-generation reconstruction and selectively truncated-history resistance. Preserve the frozen rule that witness consistency is not semantic truth, and compose with adjudicator-compromise recursion so an offline relying party cannot accept a selectively served healthy-looking branch after compromise/recovery events.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact full executable gate + conflict audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; adjudication transparency/witness quorum/quarantine review/recovery rotation/adjudicator-compromise recursion plus prior compromise provenance/onset/source/transparency/checkpoint/convergence/capability contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; retained-authority graph contracts frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; activation implementation/capability authority contracts frozen.
