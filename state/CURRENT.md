# Current Lab State

Last updated: 2026-09-07

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 remains open at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; do not change draft/merge status without the exact retained gate.
- The alternate-UNIQUE `strict_fence.py` fix is already published byte-exact: commit `05d8e75a636818afcb32e085d464c9fa9171dea5`, blob `eb2198354d222ad0ad6b7d751bf5c649157b6b36`. Do not redo that publication task.
- Other open draft/IN_PROGRESS PRs observed: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff, and `prompts/SELF_RESUME.md`; re-inspected open PRs, branches, issue #178, and PR #165 directly. PR #165 remains open/draft at head `ee210a47221b6df53f3518aa3af74f76c5b0122b` with the remaining gate stated in the PR body.

Current-run capability probe:
- `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab-run13` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes remain available;
- therefore no new LAB-086 behavioral/compile PASS is claimed and PR #165 remains draft.

Completed the recorded distinct fallback and froze `PORTABLE_RECEIPT_KEY_LIFECYCLE_HISTORICAL_TRUST_STATUS_TRANSPARENCY_ROOT_ROTATION_ARCHIVAL_SURVIVABILITY_V1_FROZEN` in `research/2026-09-07-portable-receipt-key-lifecycle-historical-trust-status-transparency-root-rotation-archival-survivability-v1.md`, main commit `176fba3af05555ab457a2ca8141c686e295c1d78`; #178 comment `5566726480` records the result.

Key decisions:
- historical receipt trust is time-indexed: `TRUST(receipt,event_time,policy_generation)`, never today's mutable trust state;
- normal expiry/retirement after an independently proven event does not retroactively invalidate a receipt;
- compromise/revocation discovery time is distinct from authenticated effective invalidity time; pre-event invalidity rejects, post-event bounded invalidity can preserve earlier receipts, unknown effective time becomes `UNKNOWN_HISTORICAL_TRUST` under high-assurance policy;
- defined `HistoricalTrustBundleV1` retaining exact receipt bytes, historical chain/root generation, signed OCSP/CRL status, event-time anchors, frozen schema/policy, transparency checkpoints/log-key generations and archival-renewal evidence;
- live/current OCSP, current trust stores, current provider account state or current log keys cannot substitute for missing historical evidence;
- old CA/transparency instances remain historical verification authorities across planned rotations; rotations are additive for history;
- provider/account/log decommission is survivable only if required proof is self-contained before shutdown;
- archival proof must support additive RFC4998/6283-style timestamp/hash renewal before primitive invalidation; a renewal gap becomes `UNKNOWN_ARCHIVE_CHAIN`;
- authenticity does not imply trust-status/root/log non-equivocation; contradictory authentic historical status evidence invalidates dependent closure rather than latest-wins;
- added an 80-case RED-first matrix for historical status, OCSP/CRL retention, root/key rotation, transparency rotation, decommission and long-term archive renewal.

Primary donors: RFC 5280 historical validation + `invalidityDate`; RFC 6960 OCSP `archiveCutoff`; RFC 3161 timestamp-before-revocation validation; RFC 4998/RFC 6283 long-term Evidence Record renewal; Sigstore trust-root/log validity-window model.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution, not `strict_fence.py` publication.
- Direct git transport failed in this run before repository execution with DNS resolution failure.
- PR #165 must remain draft until branch-local dependency-blob verification, retained strict/thaw subgate, real-schema LAB-086 tests, compileall, unsafe expected-failure seed, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-088 still needs supported-integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 implementation must compose capability inventory/delegation/revocation/lease/handoff/provider-fence/portable-receipt/historical-trust contracts with LAB-087 isolation. It must not treat current trust state, adapter assertions, one-region readback, session consistency, eventual convergence, timestamps alone, or a single authentic receipt as global historical/non-equivocation proof.

## Exact next action
LAB-086 first: if exact branch source execution becomes available, check out/reconstruct current PR head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, verify expected `strict_fence.py` blob lineage includes `eb2198354d222ad0ad6b7d751bf5c649157b6b36`, then execute the retained strict/thaw subgate (alternate-UNIQUE, primary-key/history/proof replacement, NULL identities, minimal thaw, conflict algorithms), compileall, exact branch-local LAB-080→086 dependency-blob verification, every normal LAB-086 real-schema test, unsafe legacy-promotion expected-failure seed, and final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **historical trust-bundle capture atomicity / pre-decommission freeze / completeness-proof semantics**. Define how provider receipts, CRL/OCSP/status, timestamp/checkpoint evidence, historical roots/schemas/policies and final provider readbacks are captured as one causally closed archival cut before key/provider/log/account decommission or retention expiry; specify partial-capture crash recovery, manifest completeness, missing-evidence `UNKNOWN`, and fraud proofs for a decommission that discards still-required verification material.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; publication fixed; exact full executable gate + conflict audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration/provenance contracts frozen; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability delegation + descendant revocation + D2 lease + issuer handoff + external-provider fence + portable receipt + historical trust/archive-survivability contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; retained-authority graph contracts frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; activation implementation/capability authority contracts frozen.
