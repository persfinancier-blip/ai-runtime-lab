# LAB-084 — Threshold provider-rotation authority recovery

## Problem

LAB-083 prevents one compromised provider signing key from installing an attacker successor, and normal rotation of that threshold authority requires old+new quorum. It intentionally cannot recover if the active authority quorum is unavailable or compromised.

## Donor mechanism

LAB-038's threshold-root experiment established the key separation reused here: normal root rotation uses old-root + new-root threshold, while break-glass recovery uses a separately pinned recovery quorum and advances authority version/generation. LAB-084 applies that rule instead of letting the failed normal authority self-authorize.

## Supported mechanism

`SupportedRecoveryThresholdProviderLedger` integrates the recovery controller directly with the LAB-083/LAB-082/LAB-080 SQLite authority boundary. A recovery intent binds:

- exact predecessor rotation-authority ID/version/generation;
- exact successor authority descriptor;
- exact recovery-authority ID/generation.

Only distinct active recovery signers count. Recovery proof, successor rotation authority, and authority-head update occur in one SQLite write transaction. Normal authority rotation and break-glass recovery both fail closed while LAB-080 has unresolved `PREPARED` work.

Restart verification accepts mixed authority history only when every adjacent authority edge has exactly one proof type: a LAB-083 old+new normal quorum proof or a LAB-084 recovery proof. Historical provider-generation threshold proofs are then reverified against the exact historical authority generation that authorized them.

## Audit findings fixed before integration

1. The first slice persisted a recovery head but did not rebind it to the pinned recovery bootstrap on restart. A structurally valid replacement recovery authority could therefore become durable head. Restart now requires the head to match the pinned recovery bootstrap.
2. A later audit found that a persisted recovery transition could reference a separately inserted, non-head recovery authority. Its signatures could be internally valid while bypassing the authoritative recovery head. `verify_recovery_transition_locked()` now requires every LAB-084 recovery edge to bind the exact current recovery-head identity and generation before accepting its proof.
3. Restart initialization originally allowed LAB-083's normal-only verifier to run before the recovery-aware verifier was installed. The supported constructor now keeps that initialization window internal and requires full mixed-history verification before returning a usable object.
4. Explicit concurrency regressions verify serialization of normal-authority rotation versus recovery and provider-generation rotation versus recovery. Missing recovery proof rows fail restart verification.

## Validation

Exact GitHub bytes for the LAB-084 executable/test surface and the LAB-083/LAB-082/LAB-080 dependencies were reconstructed through the GitHub connector and checked with `git hash-object` before execution.

Observed corrected results after the final audit fix:

- LAB-084 protocol + recovery-head binding + supported integration + concurrency: **17/17 passed**;
- LAB-083 threshold-rotation regressions: **24/24 passed**;
- LAB-082 asymmetric-history regressions: **28/28 passed**;
- LAB-080 shared-anchor regressions: **18/18 passed**;
- total corrected checks: **87/87 passed**;
- compileall across LAB-084/083/082/080 plus LAB-036 dependency: passed;
- unsafe self-recovery seed: failed as expected because a normal quorum incorrectly authorizes its own recovery.

The runtime emitted an unrelated spreadsheet-runtime warmup warning during Python startup; unittest execution continued and the listed suites completed successfully.

## Boundary and follow-up

LAB-084 intentionally pins the recovery-authority generation to bootstrap. Recovery-authority lifecycle/rotation is not smuggled into this issue; it is tracked separately as LAB-085 / Issue #161.

If both the normal threshold authority and the pinned recovery quorum are lost or compromised, LAB-084 fails closed rather than recursively inventing another recovery path.

## Non-goals

No HSM/KMS custody, remote ceremony UI, distributed consensus, or recursive recovery after simultaneous loss/compromise of both the normal and recovery quorums.
