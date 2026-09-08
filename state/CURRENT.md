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
- `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab-auto34` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes and web research remain available;
- PR #165 remains open/draft at exact head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; connector reports `mergeable=false`;
- no new LAB-086 behavioral/compile PASS is claimed and no draft/merge state was changed.

Completed the recorded distinct fallback and froze `PROMISE_AUTHORITY_LOSS_ADMISSION_JOURNAL_SURVIVABILITY_SEMANTIC_ABSENCE_V1_FROZEN` in `research/2026-09-08-promise-authority-loss-admission-journal-survivability-semantic-absence-v1.md`, main commit `593da5e3d204b662865252a48bb45e5c2df24590`; #178 comment `5585818678` records the result.

Key decisions:
- total ordinary promise-authority unavailability after PREPARED is fail-closed but not forgetful: retain the obligation, return no external ACCEPTED, do not silently cancel it, and do not extend the original deadline;
- promise-authority threshold compromise cannot self-authorize a trustworthy successor; recovery requires a separately trusted higher/offline recovery root or explicit out-of-band/new-lineage rebootstrap;
- already-issued historical promises remain independently verifiable when private signing keys are merely lost, subject to later compromise appraisal;
- `AdmissionJournalEnvelopeV1` + independent `AdmissionRetentionReceiptV1` make admission existence reconstructible after loss of one destructive/control domain; endpoint/replica count under one credential/domain does not create independence;
- local SQLite transaction atomicity is not cross-domain atomicity; remote retention is an idempotent recoverable receipt protocol;
- complete local journal deletion must not silently fresh-bootstrap while independent retained admission lineage exists;
- `404`, empty query, timeout, or one mirror returning no row are observations only and produce `NON_PUBLICATION_UNKNOWN`;
- bounded semantic absence in a dense append-only log can be positively established only relative to an authenticated complete prefix whose every leaf is retrieved/verified and evaluated by a frozen canonical predicate;
- compact future negative proof should use an authenticated/log-backed sparse verifiable map keyed by obligation id; its root must be anchored into append-only history;
- `PROVABLE_OMISSION = VALID_RETAINED_OBLIGATION + DEADLINE_PROVEN_ELAPSED + AUTHENTICATED_STATE_AFTER_DEADLINE + POSITIVE_NON_PUBLICATION_EVIDENCE`;
- frozen a 48-case RED-first matrix covering authority loss/recovery, cross-domain admission-journal survivability, semantic absence/non-publication proof, crash/offline catch-up, and post-facto re-appraisal.

Primary donors: RFC 9162 SCT/MMD and complete-prefix monitoring, RFC 9943 SCITT multi-Transparency-Service receipts, TUF threshold-root/out-of-band recovery boundary, SQLite atomic commit/WAL scope, Trillian verifiable log/map semantics.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution.
- Direct git transport failed in this run before repository execution with DNS resolution failure.
- PR #165 must remain draft until branch-local dependency-blob verification, retained strict/thaw subgate, real-schema LAB-086 tests, compileall, unsafe expected-failure seed, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093 and LAB-094..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: if exact branch source execution becomes available, check out/reconstruct PR head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, verify exact branch-local source/blob lineage, execute the retained strict/thaw subgate (alternate-UNIQUE, primary-key/history/proof replacement, NULL identities, hidden-rowid collision/sentinel, minimal thaw, conflict algorithms), compileall, exact branch-local LAB-080→086 dependency-blob verification, every normal LAB-086 real-schema test, unsafe legacy-promotion expected-failure seed, and final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **admission-retention receipt authority lifecycle / destructive-domain provenance and independence attestation / omission-evidence monitor authority and exhaustive-prefix reconstruction survivability**. Define who can issue/revoke/supersede retention receipts without erasing prior admission existence, how independence claims for storage/retention domains are authenticated and re-appraised after common-mode dependency discovery, and how an exhaustive-prefix absence proof remains reproducible when one monitor/archive disappears or is later found compromised.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact full executable gate + conflict audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability through promise-authority-loss/admission-journal-survivability/semantic-absence contracts frozen; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen as recorded in their issues; exact executable gates pending.
