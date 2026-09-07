# Current Lab State

Last updated: 2026-09-07

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 remains open at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; GitHub currently reports `mergeable=false`; do not change draft/merge status without the exact retained gate.
- Other open draft/IN_PROGRESS PRs retained from current repository state: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; re-inspected open issues and active PRs. PR #165 remains open/draft at exact head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, `mergeable=false`, and still requires the full exact branch execution gate before ready/merge.

Current-run capability probe:
- `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab-auto11` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes remain available;
- therefore no new LAB-086 behavioral/compile PASS is claimed and PR #165 remains draft.

Completed the recorded distinct fallback and froze `ORACLE_ADJUDICATION_THRESHOLD_REVIEWER_INDEPENDENCE_NORMATIVE_CONFLICT_GOVERNANCE_V1_FROZEN` in `research/2026-09-07-oracle-adjudication-threshold-reviewer-independence-normative-conflict-governance-v1.md`, main commit `1ab965dda2b92675f46924966cfd39977634ee15`; #178 comment `5571564502` records the result.

Key decisions:
- numeric `t-of-n` signatures are insufficient without claim-relative independence-domain coverage for organization/control, implementation/parser/canonicalizer provenance, normative-source provenance and key custody;
- `OracleThresholdPolicyV1` binds eligible adjudicators, cryptographic threshold, required independence coverage, claim scope, dissent/recusal rules, key lifecycle and policy rotation;
- recusal/conflict never silently lowers the threshold; an unsatisfied policy yields `UNKNOWN_INSUFFICIENT_INDEPENDENT_QUORUM`;
- `APPROVE`, `REJECT`, `ABSTAIN`, `RECUSED`, `UNAVAILABLE`, and `KEY_UNTRUSTED` are distinct states;
- material authenticated normative dissent cannot be erased by a raw signer majority; unresolved applicable-source contradiction yields `UNKNOWN_NORMATIVE_CONFLICT`;
- `NormativeConflictV1` retains incompatible source clauses/propositions explicitly; precedence may come only from a frozen recognized precedence/supersession/scope rule or authorized corrigendum/adjudication, not source recency, implementation popularity, or current-maintainer preference;
- historical adjudications bind immutable governance policy generations and historical key status; current maintainers cannot rewrite old expected verdicts by changing today's reviewer set;
- adjudicator key compromise is evaluated against an authenticated effective-time boundary;
- P -> P+1 governance rotation requires both old-policy and new-policy threshold authorization plus monotonic generation evidence; old policy remains archived;
- emergency governance may suspend current operational acceptance but cannot silently mint normative validity when normal oracle quorum is unavailable;
- oracle governance/key/conflict/source evidence is part of archival replay closure;
- introduced `AdjudicatorIdentityV1`, `AdjudicatorIndependenceProfileV1`, `OracleThresholdPolicyV1`, `AdjudicatorDecisionV1`, `NormativeConflictV1`, `OraclePolicyRotationProofV1`, `OracleGovernanceClosureProofV1`, fraud proofs, and an 80-case RED-first matrix.

Primary donors: TUF explicit role/key thresholds and root-chain model; Sigstore distributed/offline threshold root + compromise-time semantics; IETF recusal/appeal model; W3C consensus/sustained-objection model; NIST IR 8214C distributed threshold trust.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution.
- Direct git transport failed in this run before repository execution with DNS resolution failure.
- PR #165 must remain draft until branch-local dependency-blob verification, retained strict/thaw subgate, real-schema LAB-086 tests, compileall, unsafe expected-failure seed, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-088 still needs supported-integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 implementation must compose capability inventory/delegation/revocation/lease/handoff/provider-fence/portable-receipt/historical-trust/archive-capture/archive-durability/verifier-durability/conformance-corpus/oracle-independence/oracle-governance contracts with LAB-087 isolation. It must not treat current trust state, adapter assertions, one-region readback, session consistency, eventual convergence, timestamps alone, a single authentic receipt, quiet periods, archive-builder-selected Merkle roots, WORM/object existence, source-only retention, mutable package/runtime identity, corpus pass rate, code coverage, parser majority vote, verifier-generated expected outputs, mutable standards text, numeric reviewer threshold alone, current reviewer membership, or unresolved normative majority vote as global proof.

## Exact next action
LAB-086 first: if exact branch source execution becomes available, check out/reconstruct current PR head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, verify exact branch-local source/blob lineage, then execute the retained strict/thaw subgate (alternate-UNIQUE, primary-key/history/proof replacement, NULL identities, minimal thaw, conflict algorithms), compileall, exact branch-local LAB-080→086 dependency-blob verification, every normal LAB-086 real-schema test, unsafe legacy-promotion expected-failure seed, and final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **oracle decision anti-equivocation / publication transparency / appeal finality and fork-reconciliation semantics**. Define how one adjudicator or threshold group is prevented/detected from signing conflicting decisions for the same `(case, profile, oracle generation)`; how adjudications and policy rotations gain an append-only externally witnessed publication order; how offline verifiers detect split-view/fork/rollback; how appeals supersede rather than erase prior decisions; and what finality means when an appeal is still open or a later contradiction proof appears.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact full executable gate + conflict audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration/provenance contracts frozen; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability delegation + descendant revocation + D2 lease + issuer handoff + external-provider fence + portable receipt + historical trust + archival capture/completeness + archive durability/custody/restore-verifiability + hermetic verifier durability + scoped verifier conformance/differential-equivalence + oracle-independence/provenance + oracle-governance/threshold/normative-conflict contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; retained-authority graph contracts frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; activation implementation/capability authority contracts frozen.
