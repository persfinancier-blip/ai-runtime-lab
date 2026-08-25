# Current Lab State

Last updated: 2026-08-26

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `66786dea59809fc070006dc911cc6e4822687ed3`.
- Parallel unblocked work: Issue #166 / LAB-087 — IN_PROGRESS, branch `lab/087-sqlite-authorizer-boundary`, draft PR #171.

## Last completed step

The previously tool-blocked LAB-086 least-privilege transaction-thaw fix is now actually published. A newly available connector `fetch_blob` path returned the complete exact `strict_fence.py` blob, so the Contents API replacement was made from the exact source rather than a manually reconstructed/truncated file. GitHub returned content blob `5da01e28a9f813a136d138637f855940f04aab46`, exactly matching the previously tested candidate; publication commit `66786dea59809fc070006dc911cc6e4822687ed3`.

The fix narrows the final-writer thaw: only creation operations and the exact singleton-head UPDATE guards required by verified final writers are removed. Existing authenticated-history UPDATE/DELETE guards and unnecessary singleton INSERT/DELETE guards remain active during the transaction. Prior focused 13/13 evidence was produced on the exact same candidate blob, so the branch runtime is now byte-identical to those tested bytes. The full current-head real-ledger gate still remains before merge.

While LAB-086 full connector reconstruction remains expensive, LAB-087 advanced in parallel. Draft PR #171 now contains a broker-owned SQLite boundary: restricted workers receive a `mode=ro` connection plus connection-scoped authorizer; DML, DDL, ATTACH/DETACH, write PRAGMAs, VACUUM/meta-write forms are denied; selected read-only PRAGMAs and SELECT are allowed. A negative control opens another unrestricted writable connection, drops a trigger and mutates authority state successfully, proving the authorizer is defense-in-depth and the real outer boundary is process/file/writable-handle ownership.

## Evidence produced / reconfirmed

- LAB-086 published `strict_fence.py` blob: `5da01e28a9f813a136d138637f855940f04aab46` — exactly the previously tested minimal-thaw candidate.
- LAB-086 publication commit: `66786dea59809fc070006dc911cc6e4822687ed3`.
- Prior focused minimal-thaw candidate suite: 13/13 PASS on those exact bytes.
- Cumulative exact lower-stack evidence remains: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, asymmetric-custody 8/8, public/final 11/11; lower unsafe baselines failed as intended.
- LAB-087 exact published `protocol.py` blob: `5c999166c2155baa5ce3f644c36efe0e01e4e3fe`.
- LAB-087 exact published `tests/test_protocol.py` blob: `3f795d22d844293d62a09a0c1285764443db2279`.
- LAB-087 exact published suite: 7/7 PASS; compileall PASS.
- LAB-087 audit fix: normalize SQLite `authorization denied` alongside `not authorized`; regressions cover VACUUM, `PRAGMA writable_schema=ON`, CTE->UPDATE and TEMP DDL.
- LAB-087 unrestricted-connection negative control successfully changed the DB despite another connection's authorizer, confirming the selected trust boundary.

## Known blockers / constraints

- LAB-086 full current-head real-ledger migration/suffix/final-supported exact-source gate is still incomplete. Do not mark PR #165 ready until it passes, followed by unsafe seed, full compileall and final security audit.
- The published minimal-thaw blob is no longer a publication blocker.
- LAB-087 authorizer/wrapper is not a same-process sandbox and cannot protect the DB file from an actor that can open a separate writable connection or replace the privileged connection's authorizer. Process separation + filesystem/handle ownership is the real boundary.
- LAB-088/#167 signer-noise; LAB-090/#169 provider handoff freshness; LAB-091/#170 mutable shared-anchor/new-receipt writer authorization remain READY.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Resume LAB-086: connector-reconstruct the exact current PR HEAD `migration_guard + suffix + final_supported` and current real-schema tests on the already proven LAB-080->085 dependency closure.
2. Execute thaw-minimality plus migration v4/root coauthorization/restart, scrubbed-prefix/asymmetric-suffix, orphan/partial state, full lower/public-history guards, public-rotation cross-binding/history, inherited/direct surfaces, rotation races and final single-snapshot verification.
3. Run unsafe legacy-promotion seed and full compileall; perform a fresh full security audit and branch/main divergence check. Only then mark PR #165 ready/integrate.
4. If LAB-086 reconstruction is again tool-expensive, continue LAB-087 with an outer process/filesystem ownership experiment (worker process cannot reopen DB writable under deployment permissions) rather than strengthening the Python wrapper beyond its intended boundary.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; minimal-thaw runtime now published exactly; full current-head real-ledger gate remains.
- #166 / LAB-087 — IN_PROGRESS; draft PR #171, exact 7/7 first slice, outer process/file ownership experiment remains.
- #167 / LAB-088 — READY; threshold signer-noise robustness.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — READY; mutable/shared-ledger plus new provider-receipt ordinary-DML writer authorization.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
