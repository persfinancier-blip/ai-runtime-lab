# Current Lab State

Last updated: 2026-08-24

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `7ac5b4153b0804a6fd623bfbe55d6af1f60ac41d`.
- PR remains draft/mergeable; the full current-head merged-stack regression gate has not passed.

## Last completed step

Fresh current-head audit found a new durable cutoff-authority gap. `migration_guard.verify_locked()` authenticated the saved migration cutoff with whichever historical Ed25519 public-recovery authority the durable boundary named. The existing stale-public-quorum regression protected fresh `establish()` because establishment always loads the current public head, but it did not independently protect a later durable boundary/projection rebind by a compromised historical public quorum.

A first root-version activation-window idea was implemented and focused-tested, then deliberately removed: public recovery can legitimately rotate later at the same normal-root version, so root-version windows alone cannot unambiguously establish which public quorum authorized the original cutoff.

The stronger current candidate now requires two independent threshold authorizations over the exact same canonical migration payload: the current Ed25519 public-recovery quorum and the current normal/root quorum. `migration_payload` is v4 and explicitly requires root coauthorization. `establish(public_signatures, root_signatures)` verifies both under one `BEGIN IMMEDIATE`, persists a singleton `provider_asymmetric_break_glass_root_proof` atomically with projection/boundary persistence and HMAC scrubbing, and restart/durable verification re-verifies the exact historical root signatures and exact boundary digest. Missing/orphan/substituted/noncanonical root proof fails closed. All known LAB-086 migration test call sites were updated to supply root quorum evidence.

## Evidence produced

- Current published `migration_guard.py` Git blob: `332995323d8d74fcc0f377d0e74bb0f30b8735c1` (commit `92e196d2b9949fcf631167ca9908db0ceabb39e6`). Local authored bytes matched this blob exactly.
- Focused exact root-coauthorization execution: 4/4 passed — valid root threshold accepted; below-threshold rejected; an invalid signature using a known signer ID cannot suppress a later valid signature from that signer; changing public authority identity changes the canonical payload/root MAC.
- Exact `migration_guard.py` `py_compile` returned success. Python emitted an unrelated artifact-tool spreadsheet warmup timeout warning after startup; compile result remained rc=0.
- Updated migration integration test blob: `a3f539c9a7a4558fb86ba8b14288a57599280de5`.
- Updated suffix integration test blob: `351982fcd75f2c34d0ab6e8cbb5a966b40b76476`.
- Updated scrubbed-prefix integration test blob: `4a4628fa53537c24a18e29cac515ccd5e7046713`.
- Temporary `cutoff_activation.py` / focused tests were removed because that mechanism is not used as authority.
- Earlier current-branch focused evidence still stands for unchanged SQL-fence paths: exact strict-fence suite 10/10 passed before this cutoff change; DELETE/REPLACE/UPSERT, forged-proof and stale-writer paths were covered.
- Direct shell Internet/GitHub transport remains unavailable (`Could not resolve host`); GitHub connector is healthy and remains the supported source/control-plane path.

## Known blockers / constraints

- Remaining LAB-086 merge gate: exact current-head LAB-086 real-schema tests plus merged LAB-085/084/083/082/080 regressions have not yet been executed together from one connector-reconstructed dependency closure after the new v4 cutoff/root-proof change.
- The new root coauthorization must receive a fresh full patch/restart audit; focused 4/4 evidence is not a substitute for the merged-stack gate.
- LAB-086 trigger fences protect against stale/alternate supported mutation paths; they are not protection from an arbitrary same-privilege raw SQLite DDL writer. That broader boundary is LAB-087 / #166.
- Logical SQLite scrubbing is not forensic erasure; WAL/filesystem remnants remain outside the claim.
- Whole-store rollback freshness remains delegated to the external monotonic-anchor layer. No live HSM/KMS is claimed.
- Re-check branch/main divergence immediately before integration.

## Exact next action

1. Reconstruct the exact current PR HEAD `7ac5b4153b0804a6fd623bfbe55d6af1f60ac41d` LAB-086 implementation/tests into the already identified merged LAB-080/082/083/084/085 dependency closure, verifying executable files by Git blob identity.
2. Execute all current LAB-086 real-schema tests, prioritizing migration v4 root coauthorization/restart, missing/tampered/orphan root proof, stale-public cutoff rebinding, scrubbed-prefix + asymmetric suffix, forged-proof/stale-writer/direct-suffix, strict-fence conflict algorithms, trigger upgrade, final-supported rotation, and temporary-fence rollback.
3. Execute merged LAB-085/084/083/082/080 regressions, unsafe legacy-promotion seed, and compileall from the same closure.
4. Perform a fresh full audit focused on cutoff/public/root proof substitution, same-root public rotations, alternate supported mutation entry points, transaction-scoped fence removal, predecessor/root binding, restart snapshots, and rotation races. Keep arbitrary raw SQLite DDL authority explicitly out of the LAB-086 claim and tracked in #166.
5. Re-check branch/main divergence. Keep PR #165 draft until the full gate is clean; only then mark ready and integrate.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; new cutoff root-coauthorization is implemented with focused evidence, full merged-stack exact-source gate remains.
- #166 / LAB-087 — READY; establish/enforce the SQLite schema-control trust boundary behind post-cutoff authority fences.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
