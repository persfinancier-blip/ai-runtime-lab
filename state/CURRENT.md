# Current Lab State

Last updated: 2026-08-24

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Last durable observed PR HEAD: `2f8b4e4cd9a77470c4c9caddbd7d62a686d11429`; connector PR metadata was briefly stale during this run, so re-fetch HEAD before any integration action.
- PR remains draft; full current-head merged-stack exact-source regression gate has not passed.

## Last completed step

A fresh consequential-writer audit found a cross-layer gap after the earlier inherited-writer fence work. Final root/provider/public writers verified LAB-086 root/recovery proofs but did not first run the lower LAB-080/082 durable verifier, so a new successor could commit over already-corrupt shared-anchor/provider history that only a later full restart would notice. In addition, a retained direct `SupportedAsymmetricBreakGlassLedger` could still call `recover_rotation_authority_asymmetric()` and update the normal-root head outside the final wrapper.

The branch now closes both paths. `final_supported.py` performs lower committed-history verification while already holding `BEGIN IMMEDIATE` before every consequential writer; provider rotation additionally verifies the uncommitted asymmetric-provider history before commit. The final surface now owns asymmetric recovery itself with pre/post verification. `strict_fence.py` adds a post-cutoff root-head UPDATE fence so a direct suffix recovery rolls back; only the final writer temporarily removes/reinstalls that fence inside its verified transaction.

The exact updated SQL-fence layer was reconstructed and executed: existing strict/conflict tests + inherited-writer tests + root-head tests passed **14/14**; focused compileall passed.

This run also materially advanced the one-workspace dependency reconstruction required for the remaining LAB-085/LAB-086 gate. Exact connector-sourced files were materialized locally and verified by `git hash-object`: LAB-036 `anchor_attestation/protocol.py`; LAB-080 `shared_anchor_intent_ledger/{protocol,supported}.py`; LAB-082 `asymmetric_provider_history/{protocol,integration,supported}.py`. Compileall/import smoke for this exact reconstructed subset passed. A manually compacted LAB-083 file did not match its Git blob and was immediately deleted; it is explicitly not evidence.

The cumulative exact lower-stack regression evidence from prior completed runs remains: LAB-080 18/18 PASS, LAB-082 28/28 PASS, LAB-083 24/24 PASS, LAB-084 17/17 PASS, LAB-085 core 12/12 PASS plus LAB-085 asymmetric-custody 8/8 PASS.

## Evidence produced / reconfirmed

- Exact updated `strict_fence.py` blob `57cf5b11d927d5cd90f029f3db6dfbf9a9effd7e`.
- Exact `test_strict_fence.py` blob `4b651db3638c8b9f2341d52b512f075c4b3c31d2`.
- Exact `test_inherited_sql_fence.py` blob `e946b40d17a57f88421bb80a50bafed2ca27a728`.
- Exact `test_root_head_fence.py` blob `376f70bafc26325d3710e536cf7f060105bbcdcb`.
- Updated SQL-fence modules: **14/14 PASS**; focused compileall PASS.
- Current-run exact dependency reconstruction blobs:
  - `anchor_attestation/protocol.py` `15d8b7cf8ff093490ccb75679030d3a0fe41e401`
  - `shared_anchor_intent_ledger/protocol.py` `68834409363c93eee4e9a9a7b9ec076098af0acf`
  - `shared_anchor_intent_ledger/supported.py` `22a05c04831f65c1d7fe9077df3bb780c4008e09`
  - `asymmetric_provider_history/protocol.py` `a2fc3456233930d94aaaca5fe57b1debd50cbdab`
  - `asymmetric_provider_history/integration.py` `23ae688c22a1b74bde49ac506544778b2659bad6`
  - `asymmetric_provider_history/supported.py` `d61bcd544c001de7108de42aafdc54069d0029bf`
- Compileall/import smoke for those exact reconstructed files: PASS.
- Rejected non-evidence: a manually reformatted LAB-083 protocol produced a different Git blob and was deleted before use.
- Cumulative exact lower stack remains: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, LAB-085 asymmetric-custody 8/8; recorded lower unsafe baselines failed as expected.
- Exact standalone LAB-086 corrected suite previously passed 12/12; unsafe legacy-auto-promotion seed failed as intended.
- #168 remains a verification question, not an established defect: the earlier toy same-root counterexample omitted mandatory normal-root N→N+1 advancement by asymmetric recovery.

## Known blockers / constraints

- Full LAB-086 merge gate remains incomplete: finish exact LAB-085 final/public-custody tests in one connector-reconstructed closure, then execute all current LAB-086 real-schema tests including the new lower-history/final-recovery regressions, unsafe seed, full compileall and final audit.
- The 14/14 result closes only the current SQL-fence subgate; it is not a substitute for current-head real-schema integration execution.
- Shell GitHub transport and tested direct proxy paths are unavailable in this run; connector reconstruction works and is not an owner blocker.
- LAB-083/LAB-084 signer-noise issue #167 is fail-closed DoS/robustness and remains separate unless downstream results invalidate LAB-086.
- LAB-089 / #168 is a verification question; run real supported-writer serializations before adding protocol complexity.
- LAB-086 SQLite fences protect against stale/alternate supported mutation paths, not arbitrary same-privilege raw SQLite DDL. That broader trust boundary is LAB-087 / #166.
- Logical SQL scrubbing is not forensic erasure; WAL/filesystem remnants remain outside the claim. Whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Continue the current-run exact dependency closure from the first missing layer: reconstruct LAB-083 `provider_threshold_rotation/{protocol,enablement,strict,supported}.py` from connector bytes (do not use reformatted source), verify each with `git hash-object`, then LAB-084 and LAB-085 implementation files required by `test_public_custody_supported.py` and `test_final_supported.py`.
2. Execute exact LAB-085 `test_public_custody_supported.py` + `test_final_supported.py`; record only observed results.
3. Re-fetch the then-current PR #165 HEAD and reconstruct current LAB-086 `final_supported.py` plus all real-schema test dependencies. Execute the complete suite including lower-history/final-recovery, migration v4 root coauthorization/restart, scrubbed-prefix/asymmetric-suffix, forged-proof/stale-writer/direct-surface, inherited/root-head fences, final verification snapshot, public-rotation history guard and rotation races.
4. Include a real supported-writer regression for #168 ordering; close #168 as invalid if both serial orders restart cleanly.
5. Run LAB-086 unsafe legacy-promotion seed and compileall over the full closure, then perform final security audit and branch/main divergence check. Keep PR #165 draft until the entire current-head gate is clean; only then mark ready and integrate.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact SQL-fence 14/14 PASS; exact dependency reconstruction now materialized through LAB-082 in current workspace; full gate remains.
- #166 / LAB-087 — READY; SQLite schema-control trust boundary.
- #167 / LAB-088 — READY; signer-noise robustness in LAB-083/LAB-084 threshold collectors.
- #168 / LAB-089 — VERIFY premise against real supported-writer serializations before implementation.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
