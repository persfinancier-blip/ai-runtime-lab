# Current Lab State

Last updated: 2026-08-24

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `96c436f4571dc5149cf127b23334245fd18a1f59`.
- PR remains draft; full current-head merged-stack regression gate has not passed.

## Last completed step

A fresh audit of exact PR-head `migration_guard.py`, `suffix.py`, and `final_supported.py` found a new merge-blocker in the post-cutoff public-recovery SQL fence. The authority/transition/head triggers currently authorize mutation from the existence and metadata fields of `provider_asymmetric_recovery_public_root_proofs`; the trigger cannot cryptographically verify the stored root signatures or intent digest. A forged/corrupted/orphan proof row with matching predecessor/successor/current-root metadata can therefore satisfy the fence and allow a stale mutation-first LAB-085/LAB-086 writer to commit state; only a later durable verifier rejects it. That is persistent fail-closed DoS and violates the fence objective.

The finding is recorded on Issue #163. PR #165 remains draft.

## Evidence produced

- Exact current PR metadata observed: HEAD `96c436f4571dc5149cf127b23334245fd18a1f59`, open/draft/mergeable, 17 changed files.
- Audited current `migration_guard.py`: cutoff installs SQL triggers that test `provider_asymmetric_recovery_public_root_proofs` metadata but do not authenticate `root_signatures_json` in SQL.
- Audited current `suffix.py`: the underlying mutation-first public recovery rotation remains directly callable; its own cryptographic root verification occurs before it writes a proof, but a stale LAB-085 writer does not perform LAB-086 root coauthorization.
- Audited current `final_supported.py`: the intended path validates root quorum and writes the proof first, but the durable proof row is also accepted by stale writers solely through trigger predicates.
- Prior exact standalone LAB-086 suite remains 12/12 and stale-trigger regression 1/1; those do not cover the newly identified forged-proof-row authorization case.
- Direct shell GitHub transport was not required in this run; GitHub connector remained healthy as source/control plane.

## Known blockers / constraints

- New merge blocker: durable proof-row existence is currently a forgeable/corruptible capability for stale public-recovery writers.
- Full merged LAB-085/084/083/082/080 regression gate still remains after this blocker is fixed.
- Logical SQLite scrubbing is not forensic erasure; WAL/filesystem remnants remain outside the claim.
- Whole-store rollback freshness remains delegated to the external monotonic-anchor layer. No live HSM/KMS is claimed.

## Exact next action

1. Reproduce the forged-proof-row case as an executable regression: after cutoff insert a structurally matching `provider_asymmetric_recovery_public_root_proofs` row with invalid root signatures, invoke the stale LAB-085/public suffix mutation path, and assert zero authority/transition/head mutation.
2. Change the fence so proof-row existence is not itself mutation authority. Preferred design: stale/underlying public writers are unconditionally denied after cutoff; the final supported writer, after cryptographic old/new/root quorum verification under one `BEGIN IMMEDIATE`, uses a transaction-scoped controlled mutation path and reinstalls/verifies the deny policy before commit. Do not introduce a durable boolean/token that can itself be forged into authority.
3. Make the new regression green and verify the legitimate final public-recovery rotation remains atomic and restart-verifiable.
4. Reconstruct/execute the exact current-head LAB-086 real-schema tests plus merged LAB-085/084/083/082/080 regressions, unsafe seed, and compileall.
5. Perform a final audit focused on alternate mutation entry points, forged/orphan proofs, trigger replacement/upgrade, proof ordering, predecessor/root binding, restart and rotation races.
6. Re-check divergence and integrate only after a clean gate.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; forged-proof SQL-fence blocker must be fixed before the full merged-stack gate and merge.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
