# Current Lab State

Last updated: 2026-09-08

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; keep draft and do not merge without the exact retained gate.
- Other open drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and all active PRs; resumed LAB-086 first.

Current-run capability probe:
- `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab-auto33` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes and web research remain available;
- PR #165 remains open/draft at exact head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; connector reports `mergeable=false`;
- no new LAB-086 behavioral/compile PASS is claimed and no draft/merge state was changed.

Completed the recorded distinct fallback and froze `FRESHNESS_OBLIGATION_AUTHORITY_ATOMICITY_OMISSION_TRANSPARENCY_TIME_PROVENANCE_V1_FROZEN` in `research/2026-09-08-freshness-obligation-authority-atomicity-omission-transparency-time-provenance-v1.md`, main commit `13ad3962512ebc77c8a97b80ce3e95af054ec371`; #178 comment `5585014618` records the result.

Key decisions:
- `VALID_PROMISE_SIGNATURE != CURRENT_PROMISE_AUTHORITY != VALID_CANCELLATION != VALID_SUPERSESSION`; a subject publisher cannot erase an already-retained obligation by self-cancellation.
- `EVENT_ACCEPTED && NO_INDEPENDENTLY_RETAINED_PROMISE` is forbidden. Admission and signed promise creation are one recoverable logical transition; external ACCEPTED is returned only after the promise is durably recoverable.
- post-deadline promise supersession cannot launder a missed deadline; default effective bound is the minimum still-applicable independently retained deadline unless a bounded renewal mechanism was already authorized.
- omission evidence has an independent transparency/witness path; a transparency receipt proves registration/survivability/equivocation evidence, not semantic truth of the omission claim.
- `TIME_ENDPOINT_COUNT != INDEPENDENT_TIME_CONTROL_DOMAINS`; common upstream reference, signer/operator account, firmware/chipset, cloud/admin domain, or other dependency collapses independence for the affected threat dimension.
- consequential time quorum evaluates authenticated intervals plus a provenance-backed assurance vector; stale/unknown provenance cannot count toward high-assurance freshness quorum.
- key/DNS/region rotation does not manufacture a new independent time source.
- later discovery of common-mode time dependency reopens current reliance for affected historical freshness decisions without rewriting historical receipts.
- frozen a 48-case RED-first matrix covering promise-authority lifecycle, admission/promise crash atomicity, omission-proof transparency, time common-mode provenance, and offline/recovery composition.

Primary donors: RFC 9162 SCT/MMD, SCITT Issuer/Transparency-Service separation, RFC 8633 diverse time-source/common-element guidance, RFC 5905 falseticker selection/clustering, Roughtime nonce-bound signed midpoint/radius intervals.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution.
- Direct git transport failed in this run before repository execution with DNS resolution failure.
- PR #165 must remain draft until branch-local dependency-blob verification, retained strict/thaw subgate, real-schema LAB-086 tests, compileall, unsafe expected-failure seed, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093 and LAB-094..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: if exact branch source execution becomes available, check out/reconstruct PR head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, verify exact branch-local source/blob lineage, execute the retained strict/thaw subgate (alternate-UNIQUE, primary-key/history/proof replacement, NULL identities, hidden-rowid collision/sentinel, minimal thaw, conflict algorithms), compileall, exact branch-local LAB-080→086 dependency-blob verification, every normal LAB-086 real-schema test, unsafe legacy-promotion expected-failure seed, and final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **obligation/admission authority recovery after total promise-authority loss / cross-domain durable admission-journal survivability / semantic negative-proof construction where the underlying log exposes no canonical absence proof**. Define fail-closed behavior when the promise-authority threshold is unavailable or compromised after PREPARED admission, how independently retained admission evidence survives loss of one administrative/destructive domain, and what positive evidence can establish bounded non-publication without pretending that a bare 404/empty query is a cryptographic absence proof.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact full executable gate + conflict audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability through freshness-obligation atomicity/omission-transparency/time-common-mode-provenance contracts frozen; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen as recorded in their issues; exact executable gates pending.
