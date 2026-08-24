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

Continued the one-shot exact-source merged-stack gate at LAB-083. Reconstructed exact merge-base LAB-083 core files `provider_threshold_rotation/{protocol,enablement,strict}.py` plus `test_protocol.py`, `test_enablement.py`, and `test_strict_enablement_types.py`. Every file matched the GitHub blob using local `git hash-object` before execution. Executed those exact bytes locally: **16/16 PASS** with unittest rc=0.

This is partial LAB-083 evidence only. `integration.py`, `supported.py`, and `test_supported_integration.py` still require the exact reconstructed LAB-080/LAB-082 dependency closure in the same workspace before LAB-083 can be counted complete. The previously discovered invalid-known-signer noise issue remains isolated in LAB-088 / #167 and is not folded into this gate.

## Evidence produced / reconfirmed

- Prior exact LAB-080 corrected regression run: 18/18 PASS.
- Prior exact LAB-082 corrected regression run: 28/28 PASS; LAB-036/080/082 compileall PASS.
- Exact LAB-083 core implementation blobs matched local bytes:
  - `protocol.py` `688f3961afd9e7593fbe14c308453cfde67d23a8`
  - `enablement.py` `49e9a79dfa53268ce1eb32404f488ee720b41df9`
  - `strict.py` `9e96b19e4e83f045b1155b9b41894fd26762227e`
- Exact LAB-083 core test blobs matched:
  - `test_protocol.py` `6bb44ab9708c8d5d44d3f05186aeb6d1ccf7024a`
  - `test_enablement.py` `374c89343ee605e6d1f71e3afb1bd0102362f8ef`
  - `test_strict_enablement_types.py` `779cdf7e86a821423d2a5fa1c4e5464b4f06c14a`
- Exact LAB-083 core corrected run: **16/16 PASS**.
- Python emitted an unrelated artifact-tool spreadsheet warmup timeout warning during startup; unittest completed normally and returned rc=0.
- Remaining LAB-083 implementation blobs are already identified: `integration.py` `045070fea664952e8a001258f62ea64390f818e1`, `supported.py` `59337e73f157dbb2f8437c74b3f496507a0ce989`; `test_supported_integration.py` blob `1a01e19254140864156a27580de51989db1595a3`.
- LAB-083 signer-noise counterexample remains tracked in #167: invalid signature for a known signer can consume signer identity before MAC verification and suppress a later valid signature; this is fail-closed availability, not authority escalation.
- Previous current-implementation LAB-086 evidence remains relevant: exact standalone 12/12 PASS; strict-fence/conflict-algorithm focused evidence and v4 cutoff/root-coauthorization evidence remain recorded in PR/Issue #163.

## Known blockers / constraints

- Remaining LAB-086 merge gate: finish exact LAB-083 supported integration, then LAB-084, LAB-085 and current-head LAB-086 real-schema tests from one dependency closure; unsafe seed + compileall + final audit remain.
- File-by-file connector reconstruction is slower because shell GitHub transport is unavailable, but it is working and is not an owner blocker.
- LAB-083 signer-noise issue #167 is fail-closed DoS/robustness and is not a reason to stop LAB-086 verification unless exact downstream tests show it invalidates the candidate.
- LAB-086 SQL fences protect against stale/alternate supported mutation paths, not arbitrary same-privilege raw SQLite DDL. That broader trust boundary is LAB-087 / #166.
- Logical SQL scrubbing is not forensic erasure; WAL/filesystem remnants remain outside the claim.
- Whole-store rollback freshness remains delegated to the external monotonic-anchor layer. No live HSM/KMS is claimed.

## Exact next action

1. Reconstruct the exact LAB-080/LAB-082 dependency closure in the current workspace, then add LAB-083 `integration.py`, `supported.py`, and `test_supported_integration.py`; verify every executable/test file by Git blob identity and run the complete LAB-083 corrected suite. Do not fold LAB-088 changes into this gate.
2. Repeat cumulatively for LAB-084 provider-rotation recovery and LAB-085 provider-recovery-authority lifecycle.
3. Fetch the then-current PR #165 HEAD LAB-086 executable/tests, verify blob identities, and execute all real-schema migration/fence/suffix/final-supported tests including direct-surface, forged-proof, strict-fence conflict algorithms, cutoff/root coauthorization, scrubbed-prefix/asymmetric-suffix, restart and rotation-race cases.
4. Run unsafe legacy-promotion seed and `python -m compileall` over the complete reconstructed closure.
5. Perform a fresh full audit focused on final single-snapshot verification, cutoff/root/public proof substitution, alternate supported mutation entry points, transaction-scoped fence removal/restoration, predecessor/root binding, restart snapshots and rotation races. Re-check branch/main divergence and integrate only after the full gate is clean.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; cumulative exact merged-stack evidence now includes LAB-080 18/18 + LAB-082 28/28 + LAB-083 core 16/16. LAB-083 supported integration → LAB-086 remain.
- #166 / LAB-087 — READY; establish/enforce the SQLite schema-control trust boundary behind post-cutoff authority fences.
- #167 / LAB-088 — READY; fix LAB-083 invalid-known-signer noise consuming signer identity before cryptographic validation.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
