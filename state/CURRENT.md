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

Advanced the one-shot connector-reconstructed regression gate through all of LAB-084 and into LAB-085 core.

LAB-084: reconstructed the exact lower supported dependency closure (`anchor_attestation`, shared-anchor ledger, LAB-082 asymmetric history, LAB-083 enablement/strict/supported, LAB-084 supported/tests), verified executable/test bytes by local `git hash-object`, executed the remaining supported/concurrency tests **7/7 PASS**, then re-ran the complete corrected LAB-084 set **17/17 PASS**. The exact unsafe self-recovery seed failed as expected. Compileall across the reconstructed LAB-036/080/082/083/084 closure passed.

LAB-085 core: reconstructed exact `provider_recovery_authority_lifecycle/protocol.py` from connector chunks and matched Git blob `c59723c018da6ce49ff19073697d859d5a9be709`. Exact `tests/test_protocol.py` matched `de9f2232051df89553e0f76b7bb7f8637c287698` and executed **12/12 PASS**. Exact unsafe self-swap seed matched `c5eb95ad40d824c1a1f5d050a2ec0a485799420c` and failed as expected because the unsafe baseline lets the old recovery quorum self-replace. Compileall for reconstructed LAB-085 core passed.

Current PR #165 was rechecked and is still draft at HEAD `62dc131c888f36a48eab3b750235518d60597eac`. A source-level transaction audit then re-read the new full-history public-recovery rotation guard in `final_supported.py` and compared its verification composition with exact lower LAB-082/LAB-085 implementations. The final verifier holds an outer `BEGIN IMMEDIATE` while lower verifiers use independent read transactions. An executed SQLite harness confirmed that an independent reader can complete while the outer transaction is held, while a competing `BEGIN IMMEDIATE` writer fails with `OperationalError: database is locked`. No new mixed-writer snapshot bypass was established in this pass; this is supporting lock-semantics evidence, not a substitute for the remaining exact merged-stack tests.

## Evidence produced / reconfirmed

- Cumulative exact gate already proven: LAB-080 **18/18 PASS**, LAB-082 **28/28 PASS**, LAB-083 **24/24 PASS**.
- LAB-084 exact corrected full suite: **17/17 PASS**.
- LAB-084 exact unsafe seed `223cdaee3a94f633ec137110f4095246f9914873`: **FAILED as expected**.
- LAB-084 closure compileall: PASS.
- LAB-084 exact implementation/test identities include:
  - `provider_rotation_recovery/protocol.py` `d464e1335b0cdda9b0387d345e293d766aa0d199`
  - `provider_rotation_recovery/supported.py` `f0b45f52df3182091874694365536b44cda3de4b`
  - `test_protocol.py` `bd093f753fe942e54eafe394591c142b78fb8608`
  - `test_recovery_head_binding.py` `ab3279be5aec948e56aa7ba92e15230fc1810f80`
  - `test_supported_integration.py` `6e2b5757c1a63c79836392ee4f4e7aebb1b936af`
  - `test_concurrency.py` `cf9f528ce51eb5213dd2949466146268a4f23385`
- LAB-085 exact core implementation `protocol.py` `c59723c018da6ce49ff19073697d859d5a9be709`: local blob MATCH.
- LAB-085 exact core test `test_protocol.py` `de9f2232051df89553e0f76b7bb7f8637c287698`: local blob MATCH; **12/12 PASS**.
- LAB-085 exact unsafe seed `c5eb95ad40d824c1a1f5d050a2ec0a485799420c`: local blob MATCH; **FAILED as expected**.
- LAB-085 core compileall: PASS.
- LAB-085 remaining exact implementation manifest at merge-base:
  - `asymmetric_custody.py` `771e2ae8cde15ce06297a9cf4a94c4b3f0d81dd4`
  - `custody_break_glass.py` `f49139d80d13a3716817b79f0733cc0bc5d5bcac`
  - `supported.py` `df4f17152cddefb66dc7f4e7f76f3112d3ab4733`
  - `public_custody_supported.py` `4c338c75f1c61420438fcfe462955bd1a7ed9c92`
  - `final_supported.py` `3baf405499c5d996cd5b4f08d8a710c121247daf`
- LAB-085 remaining corrected tests identified: `test_asymmetric_custody.py`, `test_custody_break_glass.py`, `test_supported_integration.py`, `test_public_custody_supported.py`, `test_final_supported.py`.
- Current PR #165 full-history guard evidence inspected in this pass:
  - `asymmetric_break_glass_history/final_supported.py` `066b4a09652b4c331c693ce9a5275d84fe303036`.
  - `test_public_rotation_history_guard.py` `3586b909aa9bd52b4d0c58f393a698a7a592e10d`.
  - Executed SQLite lock probe: outer `BEGIN IMMEDIATE` + independent read succeeds; competing writer receives `database is locked`, supporting one write-excluding verification interval across multi-connection read verifiers.
- Issue #163 has durable comments recording the completed LAB-084 gate, LAB-085 core evidence, and the current transaction-semantics audit.
- Python emitted unrelated artifact-tool spreadsheet warmup warnings during startup; unittest/compileall return codes/results above were observed directly and are the evidence counted.

## Known blockers / constraints

- Remaining LAB-086 merge gate: finish exact LAB-085 public-custody/supported/final tests, then current-head LAB-086 real-schema tests in the same dependency closure; unsafe LAB-086 seed + full compileall + final audit remain.
- File-by-file connector reconstruction is slower because shell GitHub transport is unavailable; connector reconstruction is working and is not an owner blocker.
- LAB-083/LAB-084 signer-noise issue #167 is fail-closed DoS/robustness and does not grant authority; keep it separate unless downstream results invalidate LAB-086.
- LAB-086 SQL fences protect against stale/alternate supported mutation paths, not arbitrary same-privilege raw SQLite DDL. That broader boundary is LAB-087 / #166.
- Logical SQL scrubbing is not forensic erasure; WAL/filesystem remnants remain outside the claim.
- Whole-store rollback freshness remains delegated to the external monotonic-anchor layer. No live HSM/KMS is claimed.

## Exact next action

1. Continue in one reconstructed closure with exact LAB-085 `asymmetric_custody.py`, `custody_break_glass.py`, `supported.py`, `public_custody_supported.py`, `final_supported.py` and their five corrected test modules; verify every file by Git blob identity and execute the remaining LAB-085 corrected suite. Re-run all LAB-085 corrected tests together and compileall.
2. Fetch then-current PR #165 HEAD executable/tests and run the complete LAB-086 real-schema suite, including public-rotation complete-history guard, migration v4 root coauthorization/restart, stale-public rebinding, scrubbed-prefix/asymmetric-suffix, forged-proof/stale-writer/direct-surface, strict-fence conflict algorithms, final single-snapshot verification and rotation races.
3. Run LAB-086 unsafe legacy-promotion seed and `python -m compileall` over the complete closure.
4. Perform a fresh full audit of all consequential writers and restart paths, focused on cutoff/root/public proof substitution, alternate supported mutation entry points, transaction-scoped fence removal/restoration, predecessor/root binding, restart snapshots and rotation races.
5. Re-check branch/main divergence and integrate only after the full gate is clean.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; cumulative exact gate now has LAB-080 18/18 + LAB-082 28/28 + LAB-083 24/24 + LAB-084 17/17 + LAB-085 core 12/12, with unsafe baselines failing as expected. LAB-085 public/final -> LAB-086 remain.
- #166 / LAB-087 — READY; establish/enforce the SQLite schema-control trust boundary behind post-cutoff authority fences.
- #167 / LAB-088 — READY; signer-noise robustness confirmed in LAB-083 and LAB-084 threshold collectors.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
