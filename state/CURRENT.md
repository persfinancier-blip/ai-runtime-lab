# Current Lab State

Last updated: 2026-08-20

## Active objective

Advance from authenticated temporal policy selection/replay to authenticating policy delivery itself and binding policy + CT trust metadata into one atomic authoritative bundle so independently valid but mismatched histories cannot be mixed.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-049.
- Completed Issue #94 / LAB-049; PR #95 remote patch-audited and squash-merged as `3eaf582e211b425e7798421105608f360fe1b1b2`.
- Active next: Issue #96 / LAB-050 — READY.
- Active branch: none yet.
- Active PR: none.

## Last completed step

LAB-049 made compliance policy itself versioned, time-bounded, automatically selected by `policy_time`, cross-bound to the exact LAB-048 trust generation, and persisted into each decision by exact policy identity/version/generation/content digest/effective interval plus exact trust identity. Historical replay re-evaluates exact recorded policy+trust+evidence and cannot downgrade a new current decision.

A separate remote audit added two fail-closed fixes before integration: successor policy snapshots must preserve stable `policy_id` lineage, and policy metadata cannot be published retroactively (`issued_at > effective_from`) or expire before becoming effective.

## Evidence produced

- `experiments/ctv2_temporal_policy_lifecycle/`
- `research/2026-08-20-authenticated-temporal-policy-lifecycle.md`
- Corrected local deterministic suite: 14/14 passed.
- Unsafe caller-selected weak-policy baseline: expected failure demonstrating stale weaker policy can falsely accept evidence if callers choose policy directly.
- `python -m compileall -q experiments/ctv2_temporal_policy_lifecycle` passed.
- PR #95 remote patch audit completed after fixes.
- Merge SHA: `3eaf582e211b425e7798421105608f360fe1b1b2`.
- Primary donors: TUF version/expiry/rollback/freeze + mix-and-match protection; Chromium CT metadata version/timestamp/compatibility and PKI Metadata freshness rejection; RFC 5280 explicit temporal authority interval as comparison mechanism.

## Known blockers / constraints

- Local shell DNS to GitHub remains unavailable/unreliable; GitHub connector plus local execution is the supported path.
- LAB-049 still treats `AuthenticatedPolicyHistory.add_accepted()` as an upstream authentication boundary; it does not itself prove who authorized policy metadata.
- Policy/trust compatibility is currently a generation range, not proof that both snapshots were issued in the same authoritative release.
- Local LAB-049 tests used an interface-compatible LAB-048 shadow after inspection of the exact remote LAB-048 implementation; remote patch audit found no interface mismatch.

## Exact next action

Start Issue #96 / LAB-050. Research TUF snapshot/targets consistent-snapshot and mix-and-match protections, Sigstore/TUF TrustedRoot-style authenticated distribution, and one primary-source atomic multi-object update mechanism. Build `experiments/ctv2_policy_trust_bundle/` so an authenticated bundle binds exact policy digest + exact trust snapshot digest under one release identity/generation. Prove stale/rollback/substitution, policy/trust mix-and-match, partial update/crash, retry/idempotency, historical replay and signer/authority rotation behavior with deterministic tests. Keep general configuration-service design out of scope.

## Backlog

- #96 / LAB-050 — authenticated policy delivery + atomic trust-policy bundle — READY.
- Independent witness/gossip transport reliability and Byzantine consensus remain intentionally out of scope unless later product requirements justify them.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
