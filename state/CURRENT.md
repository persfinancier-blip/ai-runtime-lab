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
- `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab-auto28` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes and web research remain available;
- PR #165 remains open/draft at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, current connector read `mergeable=false`;
- therefore no new LAB-086 behavioral/compile PASS is claimed and no draft/merge state was changed.

Completed the recorded distinct fallback and froze `AUTHORITY_COMPROMISE_PROVENANCE_ONSET_FALSE_REVOCATION_RECOVERY_INDEPENDENCE_V1_FROZEN` in `research/2026-09-08-authority-compromise-evidence-provenance-onset-adjudication-false-revocation-recovery-independence-v1.md`, main commit `b6399a70aae67265ecdbcf6e6bd69a9da287bbd2`; #178 comment `5580953221` records the result.

Key decisions:
- `COMPROMISE_SIGNAL != COMPROMISE_EVIDENCE != APPRAISED_COMPROMISE != GLOBAL_REVOCATION`; authenticated telemetry/monitor claims are evidence inputs, not automatically global authority changes;
- `NOTICE_TIME != DETECTION_TIME != FIRST_PROVEN_MISUSE != COMPROMISE_ONSET`; RFC 5280-style invalidity semantics are represented as evidence-backed onset intervals (`last_proven_good < onset <= first_proven_bad`) unless an exact instant is genuinely proven;
- freeze `CompromiseEvidenceEnvelopeV1` and `CompromiseAdjudicationV1` with provenance, producer authority generation, evidence/counter-evidence digests, appraisal policy, independent adjudicator set, onset interval and reliance/damage scope;
- a credible single detector may trigger scoped fail-closed `LOCAL_OR_SCOPED_QUARANTINE`, but high-impact global revocation requires an authorized independent threshold adjudication; missed review never auto-restores trust;
- false-revocation resistance is achieved by separating rapid local containment from permanent/global authority mutation, not by weakening fail-closed behavior;
- `COMPROMISED_SOURCE_KEY != COMPROMISE_EVIDENCE_PRODUCER != REVOCATION_ADJUDICATOR != RECOVERY_ROOT`; neither the compromised key nor the evidence producer alleging compromise may alone select/install trusted replacement authority;
- recovery/root custody must remain independent in keys, operators/control domains and preferably offline/threshold storage; if recovery continuity is also lost, compose with the previously frozen external-rebootstrap/new-lineage contract;
- late compromise evidence invalidates *current reliance* over affected dependency/time scope through new append-only generations while historical completeness verdicts and transparency receipts remain immutable;
- frozen 14 contradiction classes and a 48-case RED-first matrix spanning provenance/authorization, onset bounds/conflicts, quarantine/global revocation, false-revocation resistance, recovery independence, and post-facto appraisal/crash durability.

Primary donors: RFC 5280 `invalidityDate` vs revocation date; RFC 6960 authorized/fresh status responder separation; NIST SP 800-57 compromise recovery/damage assessment; TUF/Uptane offline threshold root separation; Sigstore distributed threshold root and compromise-time semantics.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution.
- Direct git transport failed in this run before repository execution with DNS resolution failure.
- PR #165 must remain draft until branch-local dependency-blob verification, retained strict/thaw subgate, real-schema LAB-086 tests, compileall, unsafe expected-failure seed, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-088 still needs supported-integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 exact implementation must compose all frozen capability/delegation/revocation/lease/handoff/provider-fence/receipt/historical-trust/archive/verifier/conformance/oracle/publication/witness/recovery/freshness/secure-time/rebootstrap/convergence/evidence/continuous-assurance/checkpoint/source-ingestion/source-authority/source-transparency/compromise-adjudication contracts with LAB-087 isolation; none of the design freezes substitute for executable proof.

## Exact next action
LAB-086 first: if exact branch source execution becomes available, check out/reconstruct current PR head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, verify exact branch-local source/blob lineage, then execute the retained strict/thaw subgate (alternate-UNIQUE, primary-key/history/proof replacement, NULL identities, minimal thaw, conflict algorithms), compileall, exact branch-local LAB-080→086 dependency-blob verification, every normal LAB-086 real-schema test, unsafe legacy-promotion expected-failure seed, and final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **compromise-adjudication transparency/witness quorum / emergency-quarantine review liveness / recovery-authority rotation ceremonies / adjudicator-compromise recursion**. Define how relying parties detect same-generation/split-view adjudication, how quarantined authority receives bounded independent review without unsafe timer-based restoration, how recovery roots rotate while preserving control-domain independence, and how compromise/replacement works when the revocation/adjudication authority itself is compromised. Preserve append-only historical receipts and compose with the newly frozen provenance/onset/recovery-independence contract.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact full executable gate + conflict audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; compromise provenance/onset/false-revocation/recovery-independence plus prior source/promise authority transparency, source-authority/checkpoint/source-ingestion/capability/recovery/convergence/continuous-assurance contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; retained-authority graph contracts frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; activation implementation/capability authority contracts frozen.
