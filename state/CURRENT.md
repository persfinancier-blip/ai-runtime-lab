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
- `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab-auto24` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes and web research remain available;
- PR #165 remains open/draft at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, current connector read `mergeable=false`;
- therefore no new LAB-086 behavioral/compile PASS is claimed and no draft/merge state was changed.

Completed the recorded distinct fallback and froze `CONTINUOUS_ASSURANCE_CHECKPOINT_AUTHORITY_ARCHIVE_SURVIVABILITY_SPLIT_VIEW_PREFIX_COMPLETENESS_V1_FROZEN` in `research/2026-09-08-continuous-assurance-checkpoint-authority-archive-survivability-split-view-prefix-completeness-v1.md`, main commit `ebf673bfe39626768055401501fc7d81767e3393`; #178 comment `5578616256` records the result.

Key decisions:
- `VALID_CHECKPOINT_SIGNATURE != CURRENT_CHECKPOINT_ISSUER_AUTHORITY != CONSISTENT_APPEND_ONLY_CHECKPOINT != COMPLETE_PREFIX_CHECKPOINT != AVAILABLE_ARCHIVE`;
- checkpoint authority is first-class generation/freshness-governed authority; routine rotation requires predecessor+successor authorization and compromise intervals affect issuance-time trust;
- a compact checkpoint binds both a historical statement root and an ordered event-chain commitment; append-only consistency alone does not prove semantic ingestion completeness;
- completeness states explicitly distinguish `PREFIX_COMPLETE_PROVEN`, `PREFIX_CONSISTENT_BUT_COMPLETENESS_UNPROVEN`, proven incompleteness/equivocation, and archive-unavailable audit degradation;
- archive replica independence is counted by destructive/control domain, not bucket/endpoint count; losing one primary may be recoverable, losing all independently recoverable policy-critical evidence yields `ARCHIVE_PROVENANCE_UNRECOVERABLE`;
- archive timeout/unavailability is not pruning proof; positive contradiction evidence is required before claiming selective pruning;
- same lineage + same checkpoint generation/prefix + different authenticated roots is equivocation/fail-closed, never newest/LWW/majority-CDN selection;
- witness cosignatures prove independently tracked append-only consistency, not semantic event-ingestion completeness;
- GC must not delete the last independently recoverable copy of unresolved contradictions, losing forks, authority lifecycle evidence, or checkpoint-chain links;
- frozen a 52-case RED-first matrix spanning checkpoint authority, prefix consistency/completeness, archive survivability, split views/witnesses, archive manifests and recovery.

Primary donors: RFC 9162 CT consistency/monitor semantics; RFC 9943 SCITT append-only auditor/receipt model; transparency-dev witness/Sigsum checkpoint witnessing; RFC 4998/6283 Evidence Record hash-tree preservation and cryptographic renewal.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution.
- Direct git transport failed in this run before repository execution with DNS resolution failure.
- PR #165 must remain draft until branch-local dependency-blob verification, retained strict/thaw subgate, real-schema LAB-086 tests, compileall, unsafe expected-failure seed, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-088 still needs supported-integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 exact implementation must compose all frozen capability/delegation/revocation/lease/handoff/provider-fence/receipt/historical-trust/archive/verifier/conformance/oracle/publication/witness/recovery/freshness/secure-time/rebootstrap/convergence/evidence/continuous-assurance/checkpoint contracts with LAB-087 isolation; none of the design freezes substitute for executable proof.

## Exact next action
LAB-086 first: if exact branch source execution becomes available, check out/reconstruct current PR head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, verify exact branch-local source/blob lineage, then execute the retained strict/thaw subgate (alternate-UNIQUE, primary-key/history/proof replacement, NULL identities, minimal thaw, conflict algorithms), compileall, exact branch-local LAB-080→086 dependency-blob verification, every normal LAB-086 real-schema test, unsafe legacy-promotion expected-failure seed, and final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **semantic event-ingestion completeness / source-inventory authority / omission detection / monitor catch-up and challenge semantics**. Define how a checkpoint can prove not merely append-only consistency of what was logged but coverage of every event source that policy says MUST be logged; how event-source membership/retirement is authenticated without letting a producer silently shrink the denominator; how independent monitors detect an authority-relevant event that occurred but was never admitted to the checkpoint log; how sequence gaps, delayed ingestion, duplicate/reordered events and source partitions affect `PREFIX_COMPLETE_PROVEN`; and what bounded challenge/reconciliation protocol can turn omission suspicion into positive fraud evidence without assuming the log is its own source of completeness truth.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact full executable gate + conflict audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; rebootstrap, convergence, authenticated evidence, verifier-independence/topology/negative-probe, continuous-assurance invalidation/reclosure/authority/event-loss/compaction, and checkpoint-authority/archive-survivability/split-view/prefix-completeness contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; retained-authority graph contracts frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; activation implementation/capability authority contracts frozen.
