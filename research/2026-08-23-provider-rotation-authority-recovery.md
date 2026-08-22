# LAB-084 — Threshold provider-rotation authority recovery

## Problem

LAB-083 prevents one compromised provider signing key from installing an attacker successor, and normal rotation of that threshold authority requires old+new quorum. It intentionally cannot recover if the active authority quorum is unavailable or compromised.

## Donor mechanism

LAB-038's threshold-root experiment already established the key separation: normal root rotation uses old-root + new-root threshold, while break-glass recovery uses a separately pinned recovery quorum and advances the authority epoch. LAB-084 reuses that rule instead of letting the failed normal authority self-authorize.

## First executable slice

The reference `DurableRecoveryController` operates over LAB-083's `DurableRotationAuthority` SQL store. A recovery intent binds:

- exact predecessor rotation-authority ID/version/generation;
- exact successor authority descriptor;
- exact recovery-authority ID/generation.

Only distinct active recovery signers count. The recovery proof and new authority are committed in one SQLite write transaction, and restart re-verifies the pinned recovery bootstrap plus every stored recovery proof.

Observed local result after audit fix: **9/9 corrected tests passed**. The unsafe baseline fails because a normal authority quorum is incorrectly allowed to recover itself.

## Audit finding

The first slice persisted a recovery head but did not rebind it to the pinned recovery bootstrap on restart. A structurally valid replacement recovery authority could therefore have become the durable head. This was fixed before publication: `verify_durable()` now requires the durable recovery head to match the pinned bootstrap and re-verifies stored recovery transition proofs.

## Known integration gap / exact next step

LAB-083's current `verify_durable_locked()` expects every authority successor to have a normal old+new quorum transition. A break-glass recovery successor is intentionally a different transition type. Therefore this first slice is not yet a supported runtime surface.

The next step is a recovery-aware LAB-083 supported class whose single SQL transaction also excludes unresolved LAB-080 PREPARED work, serializes normal rotation/recovery/provider rotation, and whose restart verifier accepts a mixed authority history only when each edge is proven by exactly one valid normal-rotation proof or recovery proof.

## Non-goals

No HSM/KMS custody, remote ceremony UI, distributed consensus, or recursive recovery after simultaneous loss/compromise of both the normal and recovery quorums.
