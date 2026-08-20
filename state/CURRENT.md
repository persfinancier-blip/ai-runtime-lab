# Current Lab State

Last updated: 2026-08-20

## Active objective

LAB-054 — remove cross-observer wall-clock trust from gossip freeze attribution using authenticated causal sequence/predecessor evidence and explicit observer credibility/quorum rules.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-053.
- Active: Issue #103 / LAB-054 — IN_PROGRESS.
- Active branch: `lab/054-causal-gossip`.
- Active PR: none yet.

## Last completed step

Created the LAB-054 branch, researched RFC 9162 and C2SP witness/proof mechanisms, and implemented the first causal-gossip prototype plus deterministic tests and an unsafe wall-clock baseline. Local prototype validation passed 11/11 corrected tests; the unsafe wall-clock baseline failed as expected. Compileall passed.

A separate audit then found a consequential authority defect before integration: the current `Obs` object signs `peer/view_id/event_ids`, but `accept()` verifies only the observer signature. A malicious/compromised observer can therefore invent peer event content without carrying the peer's original signature. This would let observer narrative bytes masquerade as authenticated peer evidence. LAB-054 is intentionally NOT marked done.

## Evidence produced

- Branch `lab/054-causal-gossip` is ahead of main by 5 commits / behind by 0; all current paths are new.
- `experiments/ctv2_bundle_causal_gossip/protocol.py`
- `experiments/ctv2_bundle_causal_gossip/tests/test_protocol.py`
- `experiments/ctv2_bundle_causal_gossip/tests/unsafe_wallclock_expected_failure.py`
- `research/2026-08-20-causal-gossip-ordering.md`
- Local first-pass corrected suite: 11/11 passed.
- Unsafe wall-clock baseline: failed as expected (`FREEZE_SUSPECTED` from attacker-chosen times).
- `python -m compileall -q experiments/ctv2_bundle_causal_gossip` passed.
- Primary donors: RFC 9162 distributed consistency auditing; C2SP witness exact predecessor + atomic durable progression; C2SP proof/cosignature identity/quorum semantics.

## Known blockers / constraints

- No external blocker. The current blocker is a self-found correctness defect in the branch implementation.
- Local shell DNS to GitHub remains unavailable/unreliable; GitHub connector plus local execution is supported.
- Reliable gossip delivery, Byzantine consensus, global total ordering, and fork prevention remain out of scope.
- Silence/non-delivery remains unknown availability state, not proof of malice.

## Exact next action

Fix LAB-054 before any PR/integration: make every causal observation carry or reference the exact peer-authenticated `SignedView` material (including peer signature), and have `accept()` reconstruct and verify the peer view plus exact `view_id` binding before accepting observer evidence. Add a regression where an observer signs fabricated event_ids/view_id without a valid peer signature and prove rejection. Re-run corrected suite, unsafe seed, compileall, then perform exact remote-source/patch audit. Only after that decide DONE/integration.

## Backlog

- #103 / LAB-054 — causal gossip ordering and observer-credibility conformance — IN_PROGRESS.
- Reliable gossip transport, Byzantine consensus, and fork prevention remain out of scope unless evidence makes them the next correctness bottleneck.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
