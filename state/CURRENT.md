# Current Lab State

Last updated: 2026-08-21

## Active objective

LAB-073 — replace LAB-072's trusted external-sink idempotency/reconciliation assumption with an authenticated, behaviorally verified capability contract and fail-closed UNKNOWN policy.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-072.
- Active Issue #137 / LAB-073 — IN_PROGRESS.
- Active branch: `lab/073-sink-capability-contract`.
- Draft PR #138 `[LAB-073] Sink idempotency/reconciliation capability contract`.
- Latest known PR HEAD after fixes/docs: refresh before integration; executable protocol/test commits include `2599f770...` and `1bae0099...`.

## Last completed step

A separate security audit of PR #138 found two defects in the first slice. First, `observed=True` and `behavioral_probe_passed=True` were forgeable structural fields inside an adapter-constructible capability object. Second, `retention_seconds=None` accidentally behaved like an infinite idempotency window.

The protocol now separates adapter/provider capability claims from a trusted `ProbeAuthority`. The authority executes behavioral checks and authenticates the exact claim digest plus probe generation. Planner and broker verify that attestation before deriving retry authority. Claim substitution, forged attestation, stale probe generation, unknown retention and clock rollback fail closed.

## Evidence produced

- Published protocol Git blob: `981b4a39ef3a69a02ebd087f2259077d38fb9270`.
- Published corrected-tests Git blob: `c100506bc0bb6156ef8a4a5b137f1b17c5eb1a81`.
- Local `git hash-object` matched both published blobs exactly.
- Corrected exact executable-byte suite: 16/16 passed.
- Unsafe generic-retry seed failed as intended with 2 side effects instead of 1.
- compileall passed.
- Research/README updated to document the authenticated probe boundary and conservative retention semantics.

## Known blockers / constraints

- No owner-level blocker.
- PR #138 remains draft pending one fresh full remote patch audit after the latest protocol/tests/docs updates.
- Behavioral probing can directly verify same-key deduplication, request binding and reconciliation, but cannot cheaply wait out a provider retention horizon; finite retention remains separately sourced contract material bound into the authenticated claim.
- `SAFE_RETRY_IDEMPOTENT_ONLY` does not automatically repeat an already-UNKNOWN operation inside the generic broker when reconciliation is unavailable.
- This work does not provide universal exactly-once delivery.

## Exact next action

Re-fetch full PR #138 and current HEAD, perform a fresh remote correctness/security audit of all five changed files. Specifically test whether the probe-attestation boundary can be bypassed through claim substitution, stale issuer/generation, same-generation capability mutation, or retention-time edge cases. If no blocker is found and executable blobs are unchanged, mark PR ready and squash-merge it, close Issue #137 DONE, then create the next highest-value issue from LAB-073's remaining concrete integration boundary.

## Backlog

- #137 / LAB-073 — sink idempotency/reconciliation capability contract — IN_PROGRESS.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
