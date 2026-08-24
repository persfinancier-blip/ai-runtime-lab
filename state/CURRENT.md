# Current Lab State

Last updated: 2026-08-24

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `21d762c473d3525eb85762dfc782a7c58321b3cb`.
- PR remains draft/mergeable; full current-head merged-stack regression gate has not passed.

## Last completed step

Resumed the current PR and audited the final proof-first SQL-fence boundary against the exact published `final_supported.py`, `strict_fence.py`, `suffix.py`, and alternate-surface regressions. No new bypass was found inside the stated stale/supported-writer model: the final writer verifies old/new Ed25519 quorums plus current-root quorum before transactionally removing the deny triggers, performs the custody mutation under the same `BEGIN IMMEDIATE`, reinstalls/asserts the fence, and verifies public recovery history before commit.

The audit did identify a broader trust-boundary fact that must not be hidden: SQLite triggers cannot be a security boundary against an actor/process that retains arbitrary DDL access to the same database, because such an actor can drop/replace triggers (or invoke the trigger-removal helper) and commit before using an older writer. This is broader than the current LAB-086 stale-supported-writer acceptance model, so it was split into follow-up Issue #166 / LAB-087 rather than silently expanding LAB-086. LAB-087 will determine whether the enforceable boundary should be a broker-owned DB handle/process, sqlite authorizer policy, filesystem permissions, or an explicitly documented same-privilege DDL limitation.

## Evidence produced

- Exact published `final_supported.py` inspected at blob `518297c1191c444478efabe8081ec5b1bf533952`.
- Exact published `strict_fence.py` inspected at blob `eb9f3d60f9bda56de9d71aa3aa406a7d6a99ae78`.
- Exact direct-suffix denial regression inspected at blob `b0625ee6507ce7d7cf0d08579698f9a20feb05d2`.
- Exact stale-trigger-upgrade regression inspected at blob `e136dd636e4d9c0483595f3f4051c1c07080c5ea`.
- New follow-up: Issue #166 / LAB-087 `SQLite schema-control boundary for post-cutoff authority fences` — READY.
- Existing focused evidence remains: strict-fence exact-source suite 10/10 passed on the current branch before this audit; merged implementation dependency closure through LAB-085 had been connector-reconstructed and imported in the prior run.
- Direct shell Internet/GitHub transport remains unavailable; GitHub connector is healthy and is the supported source/control-plane path.

## Known blockers / constraints

- Remaining LAB-086 merge gate: exact current-head LAB-086 real-schema tests plus merged LAB-085/084/083/082/080 regressions have not yet been executed together from one connector-reconstructed dependency closure.
- LAB-086 trigger fences protect against stale/alternate supported mutation paths; they must not be described as protection from an arbitrary same-privilege raw SQLite DDL writer. That broader boundary is now LAB-087 / #166.
- Logical SQLite scrubbing is not forensic erasure; WAL/filesystem remnants remain outside the claim.
- Whole-store rollback freshness remains delegated to the external monotonic-anchor layer. No live HSM/KMS is claimed.
- Branch divergence was previously ahead 61 / behind 19 with all LAB-086 paths additions; re-check immediately before integration.

## Exact next action

1. Finish reconstructing the exact current PR HEAD `21d762c473d3525eb85762dfc782a7c58321b3cb` LAB-086 implementation/tests into the connector-reconstructed merged LAB-080/082/083/084/085 dependency closure, verifying executable files by Git blob identity.
2. Execute all current LAB-086 real-schema tests: migration guard, public-only suffix/restart, scrubbed-prefix + asymmetric suffix, forged-proof and stale-writer regressions, direct-suffix denial, strict fence/trigger upgrade, final-supported rotation, and temporary-fence rollback.
3. Execute merged LAB-085/084/083/082/080 regressions, unsafe legacy-promotion seed, and compileall from the same closure.
4. Perform a fresh full audit focused on alternate supported mutation entry points, transaction-scoped fence removal, proof substitution/orphans, predecessor/root binding, historical-root authorization windows, restart snapshots, and rotation races. Keep arbitrary raw SQLite DDL authority explicitly out of the LAB-086 claim and tracked in #166.
5. Re-check branch/main divergence. Keep PR #165 draft until the full gate is clean; only then mark ready and integrate.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; focused fence evidence is clean, full merged-stack exact-source gate remains.
- #166 / LAB-087 — READY; establish/enforce the SQLite schema-control trust boundary behind post-cutoff authority fences.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
