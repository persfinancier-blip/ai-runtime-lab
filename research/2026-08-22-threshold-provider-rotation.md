# LAB-083 — Threshold-authorized asymmetric provider rotation

## Problem

LAB-082 removes private signing power from historical storage, but old+new provider signatures alone do not contain compromise of the current provider signer: an attacker holding the old private key can choose and possess an attacker-controlled successor key.

## Mechanism

Reuse the threshold/root pattern already exercised in the lab: count only distinct, active signer identities and bind quorum signatures to one canonical transition. LAB-083 stores a content-addressed rotation authority, its version/generation, and the full threshold proof. The provider-rotation intent commits the exact provider predecessor, proposed successor, and threshold-authority identity/version/generation.

The threshold proof is verified and stored inside the same SQLite write transaction that checks for PREPARED shared-anchor work and advances the LAB-082 provider head. A racing authority rotation either commits first, making old quorum signatures stale, or commits after the provider transition, whose proof preserves the exact authority that authorized it.

Historical LAB-082 transitions that predate LAB-083 are explicitly behind a start boundary and remain verification-only; the experiment does not retroactively promote them to threshold-authorized transitions.

## Initial evidence

The isolated deterministic authorization/storage suite passed 10/10. The unsafe LAB-082-like baseline failed as expected because `old signer valid + attacker new signer valid` was accepted without a threshold quorum. Compileall passed for the new package.

## Boundary

This slice proves the authorization/storage primitive and publishes the real LAB-082 integration surface. Exact-source regression of the integrated surface against merged LAB-082/LAB-080 remains required before LAB-083 can be declared done. This is local compromise containment, not HSM/KMS custody, distributed consensus, or remote ceremony orchestration.
