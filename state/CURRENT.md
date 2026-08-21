# Current Lab State

Last updated: 2026-08-22

## Active objective

LAB-075 — authenticate and persist the mapping from logical `sink_id` to the concrete adapter/code profile and endpoint/origin used by LAB-074, so a caller cannot satisfy capability binding while substituting a different implementation or destination.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-074.
- Completed Issue #139 / LAB-074.
- Merged PR #140 / LAB-074 as `05ce952fa98f64d78ee6fc7765d1be6457630609`.
- Active: Issue #141 / LAB-075 — IN_PROGRESS.
- Active branch: `lab/075-sink-registry-binding`.
- Active PR: none yet.

## Last completed step

LAB-074's last exact-source gate was closed in this run. The exact published PR `capability.py` blob `0cfe0e2e555a234df96393abdf3e14b75ccff2f6`, exact PR integration tests, exact LAB-072/LAB-073 regressions and unsafe seed were reconstructed through the GitHub connector and executed locally. The combined corrected suite passed 49/49; compileall passed; the unsafe split-authority seed failed as intended because a journal without capability binding executed one external effect when zero was expected.

A fresh four-file remote patch audit found no unresolved blocker. The research note and PR evidence were updated, PR #140 was marked ready and squash-merged, and Issue #139 was closed DONE.

With no remaining open issue, the next correctness boundary was promoted to LAB-075: LAB-074 authenticates the capability of logical sink `sink-A`, but the runtime still supplies a configured `sink_id` plus an arbitrary adapter object. LAB-075 will make the logical-to-concrete adapter/endpoint mapping itself authenticated, versioned and restart-persistent.

## Evidence produced

- LAB-074 exact `capability.py` blob: `0cfe0e2e555a234df96393abdf3e14b75ccff2f6`.
- LAB-074 exact integration-test blob: `d6f003b07484775e62e8da93b3574f8eb484ea7e`.
- LAB-074 unsafe-seed blob: `4c5aef361082cfe8c6feaea97df5bc3cf31a3ee3`.
- Exact LAB-072 protocol/tests: `6817459fca8ac37c11cce71865937b8f65567d83` / `656284062a96b7915e3283b181c58bd7a8e9281d`.
- Exact LAB-073 protocol/tests: `fc05d27d5512ece585d7d6313e079ae6a234f737` / `55e42d5027fbbe1c7b66b11f08162765eba90a25`.
- Exact-source corrected suite: 49/49 passed.
- Unsafe seed: failed as expected with one unauthorized external effect.
- Compileall: passed.
- PR #140 merge SHA: `05ce952fa98f64d78ee6fc7765d1be6457630609`.
- Issue #141 / LAB-075 created and moved to IN_PROGRESS on branch `lab/075-sink-registry-binding`.

## Known blockers / constraints

- No active owner/product blocker.
- Direct shell checkout of GitHub was unavailable in this run; connector-based exact reconstruction remains a proven safe fallback.
- `sink_id -> adapter/code/endpoint` is the active unresolved trusted boundary.
- LAB-075 must reuse rather than duplicate LAB-022–025 destination/transport enforcement; the registry establishes authenticated mapping identity, while those layers remain responsible for DNS/TLS/proxy/credential transport correctness.
- Python object identity is not a production code identity; the reference experiment should use stable declared implementation/profile digests and explicitly state that production needs a signed artifact/package/build identity.
- Universal exactly-once external effects and distributed registry consensus remain non-goals.

## Exact next action

Resume Issue #141 / LAB-075. Inspect the existing LAB-074 `CapabilityBoundJournal` plus the LAB-022–025 transport/destination contracts and define the smallest registry entry that binds `sink_id`, registry generation, exact entry digest, adapter implementation/profile identity, canonical endpoint/origin, operation profile and reconciliation lineage. Build the unsafe baseline where an attacker adapter reuses a trusted `sink_id`, then add an authenticated/versioned durable registry and persist the exact registry entry identity with new LAB-074 reservations. Close the registry-update ↔ reservation race at the same SQL authority boundary, add restart/rollback/substitution/UNKNOWN/CONFIRMED tests, run LAB-074/LAB-073/LAB-072 regressions, audit independently, and only then open/integrate a PR.

## Backlog

- #141 / LAB-075 — authenticated sink-adapter and endpoint registry binding — IN_PROGRESS.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
