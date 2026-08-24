# LAB-086 — migration cutoff root coauthorization

## Finding

The pre-fix migration boundary was authenticated only by the Ed25519 public-recovery authority named inside the durable boundary. Fresh `establish()` was safe against stale signers because it loaded the current public head before signature verification, but restart verification later loaded the historical authority referenced by the saved row and accepted a valid threshold from that authority.

That leaves a durable rebinding problem under the LAB-086 corruption/compromise model: a compromised historical public-recovery quorum can sign a substituted boundary/projection naming itself. Signature validity alone does not prove that the signer was the live authority that authorized the original migration.

## Rejected weaker fix

A first experiment derived lower-inclusive / upper-exclusive public-authority windows from the normal-root version that coauthorized each public recovery rotation. That is useful lifecycle reasoning but is not a sufficient cutoff authority on its own: public recovery may legitimately rotate later while the normal/root authority remains at the same version. A restart verifier cannot infer ordering between an earlier cutoff and a later same-root-version recovery rotation from the root version alone.

The temporary helper implementing this rule was therefore removed rather than promoted into the supported boundary.

## Current candidate

The migration cutoff now requires two independent thresholds over one exact canonical payload:

1. current public-recovery Ed25519 threshold;
2. current normal/root threshold.

`migration_payload` is version `provider-asymmetric-break-glass-boundary-v4` and binds:

- exact legacy projection digest;
- cutoff root id/version/generation;
- exact public recovery authority id/version/generation;
- explicit HMAC-scrubbed state;
- explicit root-coauthorization requirement.

`establish(public_signatures, root_signatures)` verifies both quorums while holding the existing `BEGIN IMMEDIATE`. The same transaction persists the projection, boundary, canonical public signatures, singleton root proof, and performs HMAC scrubbing.

The root proof records the exact boundary digest, root id/version/generation and canonical accepted root signatures. Restart verification requires exactly that proof, reloads the exact historical root by content identity, reconstructs the same migration payload, re-verifies the root threshold and rejects missing/orphan/substituted/noncanonical proof state.

This makes a stale public-recovery quorum insufficient by itself to rewrite migration authority. Rebinding public authority identity changes the canonical payload and therefore invalidates the independently stored root proof unless the corresponding normal/root quorum also authorizes the substituted boundary.

## Focused evidence

Published `migration_guard.py` Git blob after this change: `332995323d8d74fcc0f377d0e74bb0f30b8735c1`.

Exact locally authored bytes matched that blob. Focused execution against those bytes observed 4/4 checks passing:

- valid root threshold accepted;
- below-threshold root signatures rejected;
- an invalid signature using a known signer ID does not suppress a later valid signature from that signer;
- changing the public authority identity changes the canonical cutoff payload and root MAC.

`py_compile` returned success for the exact authored `migration_guard.py` bytes. This focused evidence does **not** replace the remaining full LAB-086 + LAB-085/084/083/082/080 merged-stack gate.

## Boundary

Root coauthorization is continuity evidence for the migration cutoff. It is not whole-store rollback protection; that remains the external monotonic-anchor responsibility. It also does not make SQLite triggers a security boundary against an arbitrary same-privilege DDL writer; that separate trust-boundary question is LAB-087 / Issue #166.
