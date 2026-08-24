# Current Lab State

Last updated: 2026-08-24

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `376d1ed454c60d869605769473d903da2bb51f6f`.
- PR remains draft; full current-head merged-stack exact-source regression gate has not passed.

## Last completed step

Completed the exact LAB-083 layer of the one-shot merged-stack gate. The same local workspace now contains byte-verified merge-base implementations for LAB-036, LAB-080, LAB-082 and LAB-083. Added exact LAB-083 `integration.py`, `supported.py` and `test_supported_integration.py` on top of the previously verified core files. Every executable/test file was checked against its GitHub blob using local `git hash-object` before execution.

Executed the complete corrected LAB-083 suite: **24/24 PASS**. Compileall across reconstructed LAB-036/LAB-080/LAB-082/LAB-083 packages also passed. The recurring artifact-tool spreadsheet warmup warning is unrelated startup noise; unittest and compileall returned rc=0.

Started LAB-084 handoff by inspecting the exact merge-base `provider_rotation_recovery` directory and corrected-test manifest. No LAB-084 test result is claimed yet.

## Evidence produced / reconfirmed

- Exact LAB-080 corrected regression run: 18/18 PASS.
- Exact LAB-082 corrected regression run: 28/28 PASS.
- Exact LAB-083 full corrected regression run: **24/24 PASS**.
- Compileall across exact LAB-036/080/082/083 closure: PASS.
- Exact LAB-083 implementation blobs used:
  - `protocol.py` `688f3961afd9e7593fbe14c308453cfde67d23a8`
  - `enablement.py` `49e9a79dfa53268ce1eb32404f488ee720b41df9`
  - `strict.py` `9e96b19e4e83f045b1155b9b41894fd26762227e`
  - `integration.py` `045070fea664952e8a001258f62ea64390f818e1`
  - `supported.py` `59337e73f157dbb2f8437c74b3f496507a0ce989`
- Exact LAB-083 corrected test blobs used:
  - `test_protocol.py` `6bb44ab9708c8d5d44d3f05186aeb6d1ccf7024a`
  - `test_enablement.py` `374c89343ee605e6d1f71e3afb1bd0102362f8ef`
  - `test_strict_enablement_types.py` `779cdf7e86a821423d2a5fa1c4e5464b4f06c14a`
  - `test_supported_integration.py` `1a01e19254140864156a27580de51989db1595a3`
- LAB-083 signer-noise counterexample remains tracked separately in #167; it is fail-closed availability/robustness and was not mixed into this gate.
- LAB-084 exact implementation manifest at merge-base `d2c9781f5a60dc9b8b94fc8dba651f804a73e509`:
  - `provider_rotation_recovery/protocol.py` `d464e1335b0cdda9b0387d345e293d766aa0d199`
  - `provider_rotation_recovery/supported.py` `f0b45f52df3182091874694365536b44cda3de4b`
- LAB-084 corrected tests identified:
  - `test_protocol.py` `bd093f753fe942e54eafe394591c142b78fb8608`
  - `test_recovery_head_binding.py` `ab3279be5aec948e56aa7ba92e15230fc1810f80`
  - `test_supported_integration.py` `6e2b5757c1a63c79836392ee4f4e7aebb1b936af`
  - `test_concurrency.py` `cf9f528ce51eb5213dd2949466146268a4f23385`
  - unsafe seed `unsafe_self_recovery_expected_failure.py` `223cdaee3a94f633ec137110f4095246f9914873`
- Previous current-implementation LAB-086 evidence remains relevant: exact standalone 12/12 PASS; strict-fence/conflict-algorithm focused evidence and v4 cutoff/root-coauthorization evidence remain recorded in PR/Issue #163.

## Known blockers / constraints

- Remaining LAB-086 merge gate: exact LAB-084, then LAB-085 and current-head LAB-086 real-schema tests from the same dependency closure; unsafe seed + compileall + final audit remain.
- File-by-file connector reconstruction is slower because shell GitHub transport is unavailable. The tested local proxy endpoint is also unavailable. Connector reconstruction works and is not an owner blocker.
- LAB-083 signer-noise issue #167 is fail-closed DoS/robustness and is not a reason to stop LAB-086 verification unless downstream tests show it invalidates the candidate.
- LAB-086 SQL fences protect against stale/alternate supported mutation paths, not arbitrary same-privilege raw SQLite DDL. That broader trust boundary is LAB-087 / #166.
- Logical SQL scrubbing is not forensic erasure; WAL/filesystem remnants remain outside the claim.
- Whole-store rollback freshness remains delegated to the external monotonic-anchor layer. No live HSM/KMS is claimed.

## Exact next action

1. Reconstruct exact LAB-084 `provider_rotation_recovery/{protocol,supported}.py` and the four corrected tests listed above into the existing LAB-036/080/082/083 workspace; verify every executable/test file by Git blob identity and execute the complete corrected LAB-084 suite. Keep the unsafe seed separate as expected-failure evidence.
2. Repeat cumulatively for LAB-085 provider-recovery-authority lifecycle.
3. Fetch the then-current PR #165 HEAD LAB-086 executable/tests, verify blob identities, and execute all real-schema migration/fence/suffix/final-supported tests including final single-snapshot verification, direct-surface, forged-proof, strict-fence conflict algorithms, cutoff/root coauthorization, scrubbed-prefix/asymmetric-suffix, restart and rotation-race cases.
4. Run unsafe legacy-promotion seed and `python -m compileall` over the complete reconstructed closure.
5. Perform a fresh full audit focused on cutoff/root/public proof substitution, alternate supported mutation entry points, transaction-scoped fence removal/restoration, predecessor/root binding, restart snapshots and rotation races. Re-check branch/main divergence and integrate only after the full gate is clean.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; cumulative exact merged-stack gate now has LAB-080 18/18 + LAB-082 28/28 + LAB-083 24/24 + compileall. LAB-084→086 remain.
- #166 / LAB-087 — READY; establish/enforce the SQLite schema-control trust boundary behind post-cutoff authority fences.
- #167 / LAB-088 — READY; fix LAB-083 invalid-known-signer noise consuming signer identity before cryptographic validation.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
