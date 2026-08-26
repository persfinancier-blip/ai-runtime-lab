# Current Lab State

Last updated: 2026-08-26

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `4d3da21ef2f8c0f782f5ce0146a04aaea0b62251`.
- PR remains draft; exact real-ledger current-head gate is incomplete.
- LAB-087 / Issue #166 is DONE; PR #171 squash-merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- LAB-088 / Issue #167 is now IN_PROGRESS on branch `lab/088-threshold-signer-noise`, draft PR #172.

## Last completed step

LAB-086 focused audit was continued while the full connector-only dependency closure remains expensive to reconstruct. The new `_verify_lower_evidence_cardinality_locked()` rule was compared with exact LAB-083 enablement semantics; both use the same strict `new_generation > start_provider_generation` boundary. A focused SQLite execution of the exact current cardinality logic observed valid history PASS and rejected orphan provider transition, orphan threshold proof, orphan root transition, and duplicate normal+recovery proof type for one root successor. Migration scrub ordering was also checked against the current semantic-freeze triggers; the intended one-way HMAC scrub remains allowed while semantic fields remain frozen. No new LAB-086 blocker was established in that pass. Issue #163 comment `5421940902` records this evidence.

Because LAB-086 bulk exact reconstruction is still tool-expensive but not owner-blocked, the isolated LAB-088 follow-up was advanced without mixing it into PR #165. Exact current LAB-083 source reproduced invalid-known-signer poisoning in all four affected collectors: live provider threshold proof, threshold enablement, authority rotation and persisted/restart authority-transition verification. The fix is uniform: a signer enters `seen` only after successful MAC verification.

LAB-088 is published in draft PR #172. Exact published blobs were reconstructed and executed:
- `provider_threshold_rotation/protocol.py` `c596310401007e8c99374d638811cd72397d2d2f`;
- `provider_threshold_rotation/enablement.py` `a894d85274f7987cbcae7dcf5bacd6a6984e9ef9`;
- `tests/test_signer_noise.py` `1835991225820497660402dfc41581837c8380e6`.

The exact published signer-noise suite passed 6/6 and compileall passed. Existing exact LAB-083 core/type tests on the modified source also passed 16/16 (10 protocol + 3 enablement + 3 strict-type), so the combined focused/core gate is 22/22 PASS. A first published regression blob was caught with a syntax error during byte-exact verification and was corrected before being counted; only blob `183599...` is evidence.

## Evidence produced / reconfirmed

LAB-086 focused evidence:
- exact LAB-083 supported verifier uses `WHERE g.generation > enablement.start_provider_generation`, matching the LAB-086 cardinality rule;
- focused cardinality semantic harness: valid PASS; orphan provider/proof/root and double root-proof-type cases rejected; later enablement boundary PASS;
- migration scrub ordering is compatible with current legacy semantic-freeze triggers;
- nested LAB-085 public-custody verifier uses a read transaction, not a competing writer lock.

Cumulative exact lower-stack evidence for LAB-086 remains:
- LAB-080 18/18 PASS.
- LAB-082 28/28 PASS.
- LAB-083 24/24 PASS on pre-LAB-088 main source.
- LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS, asymmetric-custody 8/8 PASS, public/final 11/11 PASS.
- Exact standalone LAB-086 corrected suite previously passed 12/12; focused migration/fence evidence remains recorded in Issue #163 / PR #165.
- Current LAB-086 migration guard blob: `2ae3df05271385f1a0dd03d7ed85b86ec0ff72e2`.
- Current LAB-086 least-privilege fence blob: `5da01e28a9f813a136d138637f855940f04aab46`.
- Current LAB-086 suffix blob: `44847bde53b9f7b0e2fbcbab37d36dc992f497b2`.

LAB-088 exact evidence:
- exact reproduction confirmed all four invalid-known-signer poisoning paths on old main source;
- exact published corrected signer-noise suite 6/6 PASS;
- existing exact LAB-083 protocol/enablement/strict-type regressions 16/16 PASS on corrected source;
- combined 22/22 PASS + compileall PASS;
- draft PR #172 HEAD observed at creation: `bf44f2c38b86704661eb29e0d54eb34e493e5240`.

LAB-087 final exact evidence remains 14/14 PASS + compileall PASS and is merged/DONE.

## Known blockers / constraints

- LAB-086 remaining merge gate: execute current `test_pre_cutoff_lower_evidence_cardinality.py`, then the full current-head real-schema migration/suffix/final-supported/security suite from one exact LAB-080→086 dependency closure; run unsafe seed, compileall and final audit.
- Direct shell/raw GitHub transport remains unavailable. GitHub connector reads work; its archive endpoint is not supported. File-by-file exact reconstruction remains the safe execution path.
- The focused LAB-086 cardinality execution validates the formula but is not the exact real-ledger test module and is not counted as the merge gate.
- PR #165 is currently reported non-mergeable by GitHub and is substantially diverged from current `main`; do not reconcile/integrate until the complete test/security gate is clean.
- LAB-088 PR #172 must remain draft until existing LAB-083 supported integration and downstream LAB-084/085/086 compatibility regressions pass. The fix is availability/robustness only and does not change authority semantics.
- LAB-086 fences cover audited supported/DML paths. LAB-087 supplies the separate process/filesystem/write-handle boundary; root, broker UID, `CAP_DAC_OVERRIDE`, ACL/capability policy outside mode bits and privileged namespace replacement remain outside that claim.
- LAB-090/#169 provider handoff freshness and LAB-091/#170 mutable shared-anchor/new-receipt authorization remain separate follow-ups.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Resume LAB-086 as the primary task: continue file-by-file connector reconstruction of the exact LAB-080→086 closure required by `test_pre_cutoff_lower_evidence_cardinality.py`; verify reconstructed executable files by Git blob and execute the real test against migration guard `2ae3df05271385f1a0dd03d7ed85b86ec0ff72e2`.
2. On that same closure execute current `test_suffix.py` and all remaining LAB-086 migration/final-supported/security modules, then unsafe legacy-promotion seed and full compileall.
3. Perform the final LAB-086 security audit and branch/main reconciliation only after tests are clean; keep PR #165 draft until then.
4. LAB-088 follow-up after/alongside that closure: run the existing LAB-083 supported-integration suite and downstream LAB-084/085/086 regressions on branch #172. If clean, final audit and integrate PR #172; if not, fix before merge.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact current-head real-ledger gate remains primary.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172, exact 22/22 focused/core PASS, supported/downstream gate remains.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — READY; mutable shared-ledger plus new provider-receipt writer authorization.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
