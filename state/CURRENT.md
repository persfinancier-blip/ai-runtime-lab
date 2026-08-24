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

Continued the one-shot exact-source merged-stack gate. Exact LAB-082 `asymmetric_provider_history/{protocol,integration,supported}.py` and all three corrected LAB-082 tests were reconstructed from the byte-stable merge base `d2c9781f5a60dc9b8b94fc8dba651f804a73e509` on top of the already reconstructed LAB-036/LAB-080 workspace. Every executable/test file was checked with local `git hash-object` against its GitHub blob before execution. The cumulative corrected LAB-082 regression set passed 28/28; compileall over LAB-036/LAB-080/LAB-082 passed.

Started LAB-083 reconstruction/audit. Directory/test manifests and exact blob identities are recorded for `provider_threshold_rotation`. A fresh source audit found a separate fail-closed availability defect: `verify_threshold()` and `verify_enablement()` add a known signer to `seen` before MAC verification, so an invalid signature naming a real signer can suppress a later valid signature from that signer and turn a valid 2-of-N quorum into rejection. An executable counterexample reproduced the counting failure. This does not grant authority and does not invalidate the LAB-086 candidate, so it was moved to follow-up LAB-088 / Issue #167 rather than interrupting the LAB-086 merged-stack gate.

## Evidence produced / reconfirmed

- Prior exact LAB-080 corrected regression run: 18/18 PASS.
- Exact LAB-082 implementation blobs matched local bytes:
  - `protocol.py` `a2fc3456233930d94aaaca5fe57b1debd50cbdab`
  - `integration.py` `23ae688c22a1b74bde49ac506544778b2659bad6`
  - `supported.py` `d61bcd544c001de7108de42aafdc54069d0029bf`
- Exact LAB-082 corrected test blobs matched:
  - `test_protocol.py` `f737f71559e90e9a748fc3bd3d3e0cf90872a898`
  - `test_integration.py` `b659bca2a6c05999a13c6e6c84131039f337ee5d`
  - `test_supported.py` `cf5fd028f27b312aba98d8d74c300c8858e97a4a`
- Exact cumulative LAB-082 corrected regression run: 28/28 PASS.
- Compileall for reconstructed LAB-036/LAB-080/LAB-082 packages: PASS.
- LAB-083 exact source audit evidence: `provider_threshold_rotation/protocol.py` blob `688f3961afd9e7593fbe14c308453cfde67d23a8`, `enablement.py` blob `49e9a79dfa53268ce1eb32404f488ee720b41df9`; both place `seen.add(signer_id)` before MAC validity. Counterexample `[invalid(signer0), valid(signer0), valid(signer1)]` at threshold=2 counted only signer1. Follow-up Issue #167 created.
- LAB-083 expected remaining implementation blobs identified: `integration.py` `045070fea664952e8a001258f62ea64390f818e1`, `strict.py` `9e96b19e4e83f045b1155b9b41894fd26762227e`, `supported.py` `59337e73f157dbb2f8437c74b3f496507a0ce989`; corrected tests listed in GitHub directory manifest.
- Previous current-implementation LAB-086 evidence remains relevant: exact standalone 12/12 PASS; strict-fence/conflict-algorithm focused evidence and v4 cutoff/root-coauthorization evidence remain recorded in PR/Issue #163.

## Known blockers / constraints

- Remaining LAB-086 merge gate: finish exact LAB-083, then LAB-084, LAB-085 and current-head LAB-086 real-schema tests from one dependency closure; unsafe seed + compileall + final audit remain.
- File-by-file connector reconstruction is slower because shell GitHub transport is unavailable, but it is working and is not an owner blocker.
- LAB-083 signer-noise issue #167 is fail-closed DoS/robustness and is not a reason to stop LAB-086 verification unless exact downstream tests show it invalidates the candidate.
- LAB-086 SQL fences protect against stale/alternate supported mutation paths, not arbitrary same-privilege raw SQLite DDL. That broader trust boundary is LAB-087 / #166.
- Logical SQL scrubbing is not forensic erasure; WAL/filesystem remnants remain outside the claim.
- Whole-store rollback freshness remains delegated to the external monotonic-anchor layer. No live HSM/KMS is claimed.

## Exact next action

1. Finish exact connector reconstruction of LAB-083 `provider_threshold_rotation/{protocol,enablement,integration,strict,supported}.py` and corrected tests at merge-base `d2c9781f5a60dc9b8b94fc8dba651f804a73e509`; verify every executable/test file by Git blob identity and run its corrected suite on top of the already proven LAB-080/082 layers. Do not fold LAB-088 changes into this gate.
2. Repeat cumulatively for LAB-084 provider-rotation recovery and LAB-085 provider-recovery-authority lifecycle.
3. Fetch the then-current PR #165 HEAD LAB-086 executable/tests, verify blob identities, and execute all real-schema migration/fence/suffix/final-supported tests including direct-surface, forged-proof, strict-fence conflict algorithms, cutoff/root coauthorization, scrubbed-prefix/asymmetric-suffix, restart and rotation-race cases.
4. Run unsafe legacy-promotion seed and `python -m compileall` over the complete reconstructed closure.
5. Perform a fresh full audit focused on final single-snapshot verification, cutoff/root/public proof substitution, alternate supported mutation entry points, transaction-scoped fence removal/restoration, predecessor/root binding, restart snapshots and rotation races. Re-check branch/main divergence and integrate only after the full gate is clean.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; cumulative exact merged-stack gate currently has LAB-080 18/18 + LAB-082 28/28 + compileall; LAB-083→086 remain.
- #166 / LAB-087 — READY; establish/enforce the SQLite schema-control trust boundary behind post-cutoff authority fences.
- #167 / LAB-088 — READY; fix LAB-083 invalid-known-signer noise consuming signer identity before cryptographic validation.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
