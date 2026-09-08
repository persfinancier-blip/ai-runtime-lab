# Current Lab State

Last updated: 2026-09-08

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; keep draft and do not merge without the exact retained gate.
- Other open drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected active PRs and #178; resumed LAB-086 first.

Current-run capability probe:
- `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab-auto35` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes and web research remain available;
- PR #165 remains open/draft at exact head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; connector reports `mergeable=false`;
- no new LAB-086 behavioral/compile PASS is claimed and no draft/merge state was changed.

Completed the recorded distinct fallback and froze `ADMISSION_RETENTION_RECEIPT_AUTHORITY_DOMAIN_PROVENANCE_OMISSION_MONITOR_SURVIVABILITY_V1_FROZEN` in `research/2026-09-08-admission-retention-receipt-authority-domain-provenance-omission-monitor-survivability-v1.md`, main commit `acf9dc71f82ebcd2d637d4f47710681e7bc9a95c`; #178 comment `5586660798` records the result.

Key decisions:
- retention receipt authority authenticates retention facts, not admission existence; receipt revocation/supersession changes current reliance but cannot erase independently proven admission existence;
- receipt authority lifecycle is monotonic/thresholded; threshold compromise cannot self-bootstrap a trusted successor and requires separately trusted recovery or new-lineage/out-of-band recovery;
- `REPLICA_COUNT != INDEPENDENT_DESTRUCTIVE_DOMAIN_COUNT`; independence is evaluated against shared delete/control credentials, cloud accounts, KMS roots, operators, replication automation, backup roots, software/firmware and other common-mode dependencies;
- late common-mode discovery reopens current survivability assessment while preserving historical receipts;
- omission monitors are deterministic evidence producers, not semantic/root authorities;
- positive semantic absence for a dense append-only log requires an authenticated checkpoint after deadline, complete prefix retrieval, root reconstruction, frozen canonical parser/predicate, exhaustive zero matches, and an independently retained reconstruction manifest;
- monitor/archive loss does not invalidate a proof that remains independently reproducible; if the original monitor/archive held the only necessary prefix bytes and the source no longer serves them, the proof becomes historically issued but currently nonreproducible;
- late monitor/archive/common-mode compromise triggers append-only re-appraisal, not history rewrite;
- frozen a 48-case RED-first matrix covering receipt authority lifecycle, destructive-domain provenance, exhaustive-prefix proof, and monitor/archive survivability/re-appraisal.

Primary donors: RFC 9162 monitor full-prefix/consistency semantics, RFC 9943 issuer/Transparency-Service separation and multiple independent receipts, TUF role/threshold recovery separation.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution.
- Direct git transport failed in this run before repository execution with DNS resolution failure.
- PR #165 must remain draft until branch-local dependency-blob verification, retained strict/thaw subgate, real-schema LAB-086 tests, compileall, unsafe expected-failure seed, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093 and LAB-094..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: if exact branch source execution becomes available, check out/reconstruct PR head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, verify exact branch-local source/blob lineage, execute the retained strict/thaw subgate (alternate-UNIQUE, primary-key/history/proof replacement, NULL identities, hidden-rowid collision/sentinel, minimal thaw, conflict algorithms), compileall, exact branch-local LAB-080→086 dependency-blob verification, every normal LAB-086 real-schema test, unsafe legacy-promotion expected-failure seed, and final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **retention-domain attestation authority compromise / hidden common-control discovery incentives and challenge protocol / erasure-coded archive survivability versus independently verifiable full-prefix reconstruction / long-term cryptographic agility for archived omission evidence**. Define who attests destructive-domain provenance when that attester can itself be compromised, how relying parties can challenge nominally independent stores to expose hidden common control, whether erasure-coded fragments across domains preserve positive exhaustive-prefix reproducibility without reintroducing a single reconstruction root, and how old omission evidence remains verifiable across hash/signature deprecation and key compromise.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact full executable gate + conflict audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability through admission-retention-receipt-authority/destructive-domain-provenance/omission-monitor-survivability contracts frozen; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen as recorded in their issues; exact executable gates pending.
