# LAB-037 — Anchor verifier trust-root rotation and compromise recovery

## Question
How can LAB-036 verification keys remain trustworthy across rotation, revocation, rollback and compromise recovery?

## Primary donor mechanisms
- TUF root metadata is versioned; clients must not replace trusted root metadata with a lower version. Root rotation establishes continuity by requiring each new root version to be authenticated by the previously trusted root and the new root configuration. Compromised keys are removed by publishing a new trusted root.
- Sigstore models a complete `TrustedRoot` containing trusted verification material and distributes it through a TUF root-signing repository. Verification selects a subset of that trusted material rather than accepting key material asserted by the object being verified.
- LAB-036 already separates authenticated observation freshness from monotonicity. LAB-037 adds authorization of the verifier key itself; signature validity alone is insufficient if the key is unknown, revoked, stale, cross-provider, or pre-recovery.

Primary sources:
- https://theupdateframework.github.io/specification/v1.0.28/
- https://github.com/theupdateframework/specification/blob/master/tuf-spec.md
- https://github.com/sigstore/protobuf-specs/blob/main/protos/sigstore_trustroot.proto
- https://github.com/sigstore/root-signing

## Reference model
`TrustState` is versioned by `store_version`, scoped to one `provider_id`, carries a current key generation and key identifier, a revoked-key set, and an `authority_epoch`.

Normal rotation is accepted only when:
1. provider identity matches;
2. generation advances exactly by one;
3. authority epoch is unchanged;
4. the new key identifier matches the new key bytes;
5. the rotation statement is authenticated by the currently trusted key.

After rotation the old key is revoked and no longer authoritative. A trust-store snapshot with lower `store_version` or lower `authority_epoch` is rejected as rollback.

Compromise recovery is stronger than normal rotation: it increments `authority_epoch`. Receipts from an older recovery epoch are rejected even when their cryptographic signature still verifies under historical key material.

## Unsafe baseline
A self-asserted-key verifier accepts a forged object when the object supplies both its own verification key and matching MAC. The safety test expects rejection and fails because the unsafe verifier returns `True`.

## Corrected experiment
Observed local corrected suite: **9/9 tests passed**.

Covered scenarios:
- current pinned provider key accepted;
- unknown key rejected;
- old generation rejected after rotation;
- trust-store rollback rejected;
- cross-provider substitution rejected;
- rotation signed by an untrusted key rejected;
- compromise-recovery epoch invalidates old receipts;
- restart restores exactly one current authority state;
- evidence contains public key identifier/generation/epoch, not private signing material.

## Important distinction
Cryptographic validity answers “does this key authenticate these bytes?” Trust-root authorization answers “is this key currently authorized for this provider and authority epoch?” LAB-036 freshness/challenge checks remain a separate layer, and LAB-034/LAB-035 monotonic DB/anchor invariants remain separate again.

## Non-goals
This is a deterministic trust-boundary model, not a general PKI, certificate-transparency system, HSM implementation, or claim that a real external KMS/TPM is available in the current runtime.
