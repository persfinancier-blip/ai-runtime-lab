# Current Lab State

Last updated: 2026-08-24

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `62dc131c888f36a48eab3b750235518d60597eac`.
- PR remains draft; full current-head merged-stack exact-source regression gate has not passed.

## Last completed step

Continued the one-shot merged-stack regression gate at LAB-084. Reconstructed exact merge-base core sources through the GitHub connector, verified every executable/test file with local `git hash-object`, and executed the LAB-084 core tests directly.

Exact results: `provider_rotation_recovery.tests.test_protocol` **9/9 PASS** and `test_recovery_head_binding` **1/1 PASS** — LAB-084 core **10/10 PASS**. This is exact-source evidence, not a compatibility harness. It does not yet claim the supported/concurrency layer; `supported.py`, `test_supported_integration.py`, and `test_concurrency.py` remain the next reconstruction/execution step.

A fresh LAB-084 source audit found the same invalid-first known-signer noise pattern already tracked in LAB-088/#167: recovery and historical normal-edge collectors mark a signer seen before MAC success. This is fail-closed availability/robustness, not authority escalation. #167 was updated rather than interrupting LAB-086.

Current PR #165 was re-inspected: latest HEAD is `62dc131c888f36a48eab3b750235518d60597eac`; the final public-recovery writer includes the complete-history pre/post mutation guard. Current branch/main compare is diverged ahead 77 / behind 32; all 24 LAB-086 paths remain additions with no path overlap against main.

## Evidence produced / reconfirmed

- Previously proven cumulative gate: LAB-080 **18/18 PASS**, LAB-082 **28/28 PASS**, LAB-083 **24/24 PASS**.
- New exact LAB-084 core: **10/10 PASS**.
- Exact files used for LAB-084 core:
  - `experiments/provider_threshold_rotation/protocol.py` `688f3961afd9e7593fbe14c308453cfde67d23a8`
  - `experiments/provider_rotation_recovery/protocol.py` `d464e1335b0cdda9b0387d345e293d766aa0d199`
  - `experiments/provider_rotation_recovery/tests/test_protocol.py` `bd093f753fe942e54eafe394591c142b78fb8608`
  - `experiments/provider_rotation_recovery/tests/test_recovery_head_binding.py` `ab3279be5aec948e56aa7ba92e15230fc1810f80`
  - supporting exact LAB-036/080 files used in the reconstruction include `anchor_attestation/protocol.py` `15d8b7cf8ff093490ccb75679030d3a0fe41e401`, `shared_anchor_intent_ledger/protocol.py` `68834409363c93eee4e9a9a7b9ec076098af0acf`, and `shared_anchor_intent_ledger/supported.py` `22a05c04831f65c1d7fe9077df3bb780c4008e09`.
- Exact LAB-084 supported manifest reconfirmed:
  - `provider_rotation_recovery/supported.py` `f0b45f52df3182091874694365536b44cda3de4b`
  - `test_supported_integration.py` `6e2b5757c1a63c79836392ee4f4e7aebb1b936af`
  - `test_concurrency.py` `cf9f528ce51eb5213dd2949466146268a4f23385`
  - unsafe seed `223cdaee3a94f633ec137110f4095246f9914873`.
- LAB-088/#167 updated with the LAB-084 invalid-first signer-noise extension.
- Current PR compare: ahead 77 / behind 32; 24 LAB-086 paths are additions only.
- Direct shell GitHub transport remains unavailable in this runtime; the GitHub connector is healthy and remains the exact durable source/control path.

## Known blockers / constraints

- Remaining LAB-086 merge gate: finish exact LAB-084 supported/concurrency tests, then LAB-085 and current-head LAB-086 real-schema tests in one connector-reconstructed dependency closure; unsafe seed + compileall + final audit remain.
- LAB-084 core 10/10 is real exact-source evidence but is not a substitute for its supported/concurrency tests.
- LAB-083/LAB-084 signer-noise issue #167 is fail-closed DoS/robustness and does not grant authority; keep it separate unless downstream results invalidate LAB-086.
- LAB-086 SQL fences protect against stale/alternate supported mutation paths, not arbitrary same-privilege raw SQLite DDL. That broader boundary is LAB-087 / #166.
- Logical SQL scrubbing is not forensic erasure; WAL/filesystem remnants remain outside the claim.
- Whole-store rollback freshness remains delegated to the external monotonic-anchor layer. No live HSM/KMS is claimed.

## Exact next action

1. Finish exact LAB-084 supported/concurrency closure in the current reconstruction: add exact `asymmetric_provider_history/{protocol,integration,supported}.py`, `provider_threshold_rotation/{enablement,strict,supported}.py`, `provider_rotation_recovery/supported.py`, `test_supported_integration.py`, and `test_concurrency.py`; verify Git blob identities and execute them. Run LAB-084 unsafe seed separately as expected-failure evidence.
2. Repeat cumulatively for LAB-085 provider-recovery-authority lifecycle.
3. Fetch then-current PR #165 HEAD executable/tests and run the complete LAB-086 real-schema suite, including public-rotation history guard, migration v4 root coauthorization/restart, stale-public rebinding, scrubbed-prefix/asymmetric-suffix, forged-proof/stale-writer/direct-surface, strict-fence conflict algorithms, final single-snapshot verification and rotation races.
4. Run unsafe legacy-promotion seed and `python -m compileall` over the complete closure.
5. Perform a fresh full audit of all consequential writers and restart paths; re-check branch/main divergence and integrate only after the full gate is clean.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; cumulative exact gate now has LAB-080 18/18 + LAB-082 28/28 + LAB-083 24/24 + LAB-084 core 10/10. LAB-084 supported/concurrency -> LAB-085 -> LAB-086 remain.
- #166 / LAB-087 — READY; establish/enforce the SQLite schema-control trust boundary behind post-cutoff authority fences.
- #167 / LAB-088 — READY; signer-noise robustness now confirmed in LAB-083 and LAB-084 threshold collectors.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
