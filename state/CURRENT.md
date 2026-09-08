# Current Lab State

Last updated: 2026-09-08

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; keep draft and do not merge without the exact retained gate.
- Other open drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and active PRs; resumed LAB-086 first.

Current-run capability probe:
- `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab-auto12` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes and web research remain available;
- PR #165 is confirmed open/draft at exact head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; connector reports `mergeable=false`;
- no new LAB-086 behavioral/compile PASS is claimed and no draft/merge state was changed.

Completed the recorded distinct fallback and froze `TRANSPARENCY_WITNESS_CROSSLOG_MULTIBEACON_SEMANTIC_REPAIR_PROVENANCE_AUTHORITY_V1_FROZEN` in `research/2026-09-08-transparency-witness-authority-cross-log-multibeacon-semantic-repair-provenance-authority-v1.md`, main commit `bf456f0af40c2d8c8c18aa9f8faf5b117eef704d`; #178 comment `5590519905` records the result.

Key decisions:
- log-authority validity, witness membership, transparent publication, semantic truth and latestness are separate assurance classes;
- a log/witness set cannot establish its own successor solely through self-publication/cosigning; compromised authority requires independently retained recovery/higher-root authority or explicit new lineage;
- same lineage/generation + conflicting authenticated digest is equivocation, never LWW/newest/fastest-mirror resolution;
- cross-log anchoring gives positive existence/staleness/equivocation/survivability evidence when an independently retained destination proves a source checkpoint, but absence of a newer anchor does not prove source latestness;
- multi-beacon safety requires population/selection/combination/fallback rules frozen before values are knowable; adaptive post-value fallback, dropping a committed last revealer, or same-round reselection is a bias channel;
- semantic repair quorum counts independent reproductions of the exact manifest/predecessor/canonical reconstruction, not multiple signatures over one copied result; deterministic divergence is a conflict requiring fail-closed/adjudication;
- verifier-provenance independence cannot be self-certified by the verifier; identity/attestation/policy/revocation/adjudication roles are versioned separately;
- late compromise/common-mode provenance disclosure re-appraises current reliance without erasing historical evidence;
- frozen 64-case RED-first matrix across authority lifecycle, cross-log evidence, multi-beacon anti-bias, semantic repair reproduction and provenance authority/revocation.

Primary donors: RFC 9162 CT consistency/auditing; transparency.dev witness semantics; drand threshold/public randomness; in-toto functionary/threshold verification; Sigstore transparency + TUF trust-root/revocation boundary; SLSA provenance semantics.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution.
- Direct git transport failed in this run before repository execution with DNS resolution failure.
- PR #165 must remain draft until branch-local dependency-blob verification, retained strict/thaw subgate, real-schema LAB-086 tests, compileall, unsafe expected-failure seed, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093 and LAB-094..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: if exact branch source execution becomes available, check out/reconstruct PR head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, verify exact branch-local source/blob lineage, execute the retained strict/thaw subgate (alternate-UNIQUE, primary-key/history/proof replacement, NULL identities, hidden-rowid collision/sentinel, minimal thaw, conflict algorithms), compileall, exact branch-local LAB-080→086 dependency-blob verification, every normal LAB-086 real-schema test, unsafe legacy-promotion expected-failure seed, and final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **witness-gossip partition recovery / cross-log anchor-obligation completeness + threshold-beacon liveness certificates / semantic-attester independence challenge protocol / provenance-authority transparency and key-compromise effective-time semantics**. Define how a long network partition rejoins without accepting selectively truncated witness history; how mandatory cross-log anchoring can produce positive omission evidence when a promised anchor is withheld; how to distinguish beacon unavailability from malicious withholding with signed liveness evidence; how to challenge semantic attesters for independent reconstruction rather than copied outputs; and how revocation effective-time interacts with artifacts/attestations created before versus after a provenance-authority key compromise.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact full executable gate + conflict audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability through transparency/witness authority lifecycle, cross-log anchoring, multi-beacon anti-bias, semantic repair quorum and verifier-provenance authority/revocation frozen; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen as recorded in their issues; exact executable gates pending.
