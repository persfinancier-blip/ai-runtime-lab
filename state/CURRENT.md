# Current Lab State

Last updated: 2026-08-20

## Active objective

Advance from authenticated CT log-list/operator authority to time-aware eligibility so historical SCT/evidence decisions use authoritative lifecycle/operator facts at the relevant event time without permitting stale-snapshot cherry-picking.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-047.
- Completed Issue #90 / LAB-047; PR #91 remote patch-audited and squash-merged as `5a3afd6fef5474b6b9d8858307fbd63d43917cc5`.
- Active next: Issue #92 / LAB-048 — READY.
- Active branch: none yet.
- Active PR: none.

## Last completed step

LAB-047 implemented authenticated/versioned CT log trust snapshots that bind LogID, immutable verification profile, authoritative operator membership, lifecycle state/timestamp, version/generation, freshness and exact snapshot identity. This run's separate audit found a critical authority-boundary defect: the evaluator could consume an arbitrary unauthenticated snapshot object if the caller also supplied its matching deterministic content hash. The API was corrected so evaluation resolves snapshots only from `TrustLifecycle` history populated by successful authentication/acceptance.

## Evidence produced

- `experiments/ctv2_log_trust_lifecycle/`
- `research/2026-08-20-ctv2-log-trust-lifecycle.md`
- Corrected local deterministic suite after audit fix: 18/18 passed.
- `python -m compileall -q experiments/ctv2_log_trust_lifecycle` passed.
- Unsafe self-asserted trust/operator baseline: expected failure because caller metadata satisfied threshold without authenticated authority.
- Remote patch audit completed on PR #91 before merge.
- Merge SHA: `5a3afd6fef5474b6b9d8858307fbd63d43917cc5`.
- Fresh primary-source recheck in this run: current Chromium CT proto/log-list documentation models timestamped state and operator history plus list version/timestamp; TUF signed metadata uses roles/version/expiry and consistent snapshots to reject rollback/freeze/mix-and-match; Sigstore recommends TUF-backed TrustRoot distribution.

## Known blockers / constraints

- Local shell DNS to GitHub remains unavailable/unreliable; GitHub connector plus local execution is the supported path.
- LAB-047 is a reference authenticated trust-distribution model, not Chrome/browser compliance policy.
- HMAC remains a deterministic stand-in for a production authenticated metadata chain.
- LAB-047 preserves historical snapshots but current evaluation still treats lifecycle state at the selected snapshot as a boolean gate; it does not yet resolve eligibility/operator identity at an explicit SCT/evidence timestamp.

## Exact next action

Start Issue #92 / LAB-048. Research timestamped lifecycle/operator-history semantics using RFC 9162 plus current Chromium CT metadata/policy and one additional primary-source temporal authorization mechanism. Build `experiments/ctv2_temporal_log_eligibility/` consuming authenticated LAB-047 lifecycle history. Define non-overlapping eligibility/operator intervals and deterministic boundary rules, then prove historical decisions are not retroactively rewritten while current/future decisions cannot select stale snapshots to bypass newer distrust.

## Backlog

- #92 / LAB-048 — temporal CT eligibility windows and historical-policy conformance — READY.
- Independent witness/gossip transport reliability and Byzantine consensus remain intentionally out of scope unless later product requirements justify them.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
