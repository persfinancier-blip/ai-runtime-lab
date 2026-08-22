# Current Lab State

Last updated: 2026-08-22

## Active objective

LAB-076 — remove LAB-075's remaining static single-key sink-registry `RegistryAuthority` assumption by making registry signing authority versioned, restart-persistent, rotation/revocation-aware, and bound to historical registry entries without reviving old signing authority.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-075.
- LAB-075 Issue #141 — DONE.
- LAB-075 PR #142 squash-merged as `d16b7a14f33090cb57b4b1b241a5e279a1b979df`.
- Active: Issue #143 / LAB-076 — IN_PROGRESS.
- Active branch: `lab/076-registry-authority-lifecycle`.
- Active PR: none yet.

## Last completed step

LAB-075 exact published source was reconstructed through the GitHub connector and matched locally by Git blob identity. The final combined LAB-075/LAB-074/LAB-073/LAB-072 regression contour passed 89/89; compileall passed; the unsafe string-only adapter baseline failed as expected because the unsafe design executed one attacker side effect.

The final audit found two additional blockers before merge and both were fixed and retested. First, the supported worker used `isinstance`, so a subclass of the audited journal could override `_capability_fields` and restore the legacy unauthenticated capability path; exact-type gating now rejects that composition before request processing. Second, terminal CONFIRMED receipt lookup did not authenticate the stored historical registry reference; the receipt-only path now reloads and verifies the exact signed historical entry and its sink/generation binding before returning the durable receipt. New regressions cover both cases.

After those fixes, exact published blobs `audit_fixes.py=2afdca0619a0bc6c6de2581c598c8d7f50f58b52` and `test_audit_fixes.py=8b7b8cd8feac81fa82d751b3106f776eb278c261` were executed in the same 89/89 regression contour. PR #142 was marked ready and squash-merged normally.

## Evidence produced

- PR #142 validated HEAD: `989e414f2fb7a6d6c2f175ca509767a7c4ea9a26`.
- Final merge: `d16b7a14f33090cb57b4b1b241a5e279a1b979df`.
- Exact-source combined regression suite: 89/89 passed.
- Unsafe LAB-075 seed: expected failure `1 != 0` because attacker adapter executed in the unsafe string-only design.
- Compileall: passed.
- Issue #141 updated with final acceptance/evidence and closed DONE.
- No other open issue existed after LAB-075; Issue #143 / LAB-076 was created as the next correctness gap.

## Known blockers / constraints

- No owner/product blocker.
- Direct GitHub clone/raw download was unavailable in the LAB-075 validation runtime due DNS; connector reconstruction is a proven supported fallback.
- LAB-075's registry entries are authenticated, but `RegistryAuthority` is still supplied as one ambient static HMAC key/generation. That key lifecycle is the active correctness gap.
- Reuse the repository's existing threshold/root/recovery work where possible; do not create an unrelated self-signed replacement mechanism.
- Historical authority must remain available for verification of already-bound entries without granting it authority to sign new entries.
- Distributed PKI/consensus, service discovery, and transport security remain out of scope for LAB-076.

## Exact next action

On branch `lab/076-registry-authority-lifecycle`, inspect the reusable threshold/root/recovery mechanisms from LAB-037/LAB-038/LAB-057 and the merged LAB-075 supported registry surface. Define the smallest durable authority state and transition contract that binds each registry entry to an exact historical authority generation. Build a deterministic prototype/failure matrix covering static-key substitution, restart rollback, same-generation key replacement, old-signer use after revocation, historical CONFIRMED verification, missing/corrupt historical authority, authority-rotation vs registry-publication races, and unsafe self-asserted recovery. Reuse existing threshold/recovery primitives rather than duplicating them. Run tests, audit, and publish the first coherent slice to the active branch before opening a draft PR.

## Backlog

- #143 / LAB-076 — sink-registry authority lifecycle, rotation, and restart conformance — IN_PROGRESS.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
