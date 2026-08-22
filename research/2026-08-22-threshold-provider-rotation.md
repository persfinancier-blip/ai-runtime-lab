# LAB-083 — Threshold-authorized asymmetric provider rotation

## Problem

LAB-082 removes private signing power from historical storage, but old+new provider signatures alone do not contain compromise of the current provider signer: an attacker holding the old private key can choose and possess an attacker-controlled successor key.

## Mechanism

Reuse the threshold/root pattern already exercised in the lab: count only distinct, active signer identities and bind quorum signatures to one canonical transition. LAB-083 stores a content-addressed rotation authority, its version/generation, and the full threshold proof. The provider-rotation intent commits the exact provider predecessor, proposed successor, and threshold-authority identity/version/generation.

The threshold proof is verified and stored inside the same SQLite write transaction that checks for PREPARED shared-anchor work and advances the LAB-082 provider head. A racing authority rotation either commits first, making old quorum signatures stale, or commits after the provider transition, whose proof preserves the exact authority that authorized it.

Historical LAB-082 transitions that predate LAB-083 are explicitly behind a quorum-signed enablement boundary and remain verification-only; the experiment does not retroactively promote them to threshold-authorized transitions.

## Exact-source evidence

The final supported surface and its merged LAB-082/LAB-080/LAB-036 dependencies were reconstructed from GitHub connector bytes after direct git networking failed in the runtime. Executed files were checked with `git hash-object` against their GitHub blob identities.

Observed corrected results on the current executable PR head before this documentation-only update:

- LAB-083 threshold/storage suite: **10/10 passed**;
- LAB-083 signed enablement suite: **3/3 passed**;
- LAB-083 strict enablement type/canonicalization suite: **3/3 passed**;
- LAB-083 real supported integration suite: **8/8 passed**;
- LAB-082 supported regression: **2/2 passed**;
- LAB-080 supported regression: **4/4 passed**;
- unsafe old+attacker-new baseline failed as expected because old+new-only authorization accepted compromise;
- `compileall` passed for the reconstructed executable package slice, including the retained prototype module.

The remote audit also confirmed the supported surface uses the signed `ThresholdEnablement`; the earlier `integration.py` remains prototype/audit evidence and is not the intended authority surface.

## Recovery boundary

LAB-083 deliberately stops at normal threshold-authority rotation and current-provider compromise containment. Break-glass recovery of the threshold rotation authority is a separate trust problem: a failed/compromised authority must not be able to self-authorize its replacement. This work is explicitly deferred to Issue #159 / LAB-084, which will reuse the lab's already-tested separate recovery-quorum patterns rather than weakening the LAB-083 normal path.

## Boundary

This is local compromise containment, not HSM/KMS custody, distributed consensus, remote ceremony orchestration, or break-glass recovery. The reference threshold keys are a local experiment mechanism; production custody remains a separate integration concern.
