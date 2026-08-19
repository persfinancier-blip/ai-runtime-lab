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

After rotation the old key is revoked and no longer authoritative. A trust-store snapshot with lower `store_version` or lower `authority_epoch` is rejected as rollback. A same-version snapshot with different contents is rejected as substitution rather than accepted as an equivalent restart image.

Compromise recovery is stronger than normal rotation: it increments `authority_epoch`. Receipts from an older recovery epoch are rejected even when their cryptographic signature still verifies under historical key material.

## Unsafe baseline
A self-asserted-key verifier accepts a forged object when the object supplies both its own verification key and matching MAC. The safety test expects rejection and fails because the unsafe verifier returns `True`.

## Corrected experiment
Exact published-source SHA checks matched the branch blobs for protocol, corrected tests, and unsafe seed. Observed corrected suite: **11/11 tests passed**; `compileall` passed. The unsafe seed failed as expected.

Covered scenarios:
- current pinned provider key accepted;
- unknown key rejected;
- old generation rejected after rotation;
- lower trust-store generation/epoch rollback rejected;
- same-version trust-store content substitution rejected;
- explicit revocation blocks the compromised current key;
- cross-provider substitution rejected;
- rotation signed by an untrusted key rejected;
- compromise-recovery epoch invalidates old receipts;
- restart restores exactly one current authority state;
- evidence contains key identifier/generation/epoch, not private signing material.

## Audit finding
The first corrected implementation checked only `candidate.store_version < current.store_version`. Remote patch audit showed that an attacker could therefore replace the trust-store contents while preserving the same version number. This violated the task's silent-key-substitution requirement. The implementation now requires same-version state to be identical or fails closed with `SnapshotSubstitution`.

## Important distinction
Cryptographic validity answers “does this key authenticate these bytes?” Trust-root authorization answers “is this key currently authorized for this provider and authority epoch?” LAB-036 freshness/challenge checks remain a separate layer, and LAB-034/LAB-035 monotonic DB/anchor invariants remain separate again.

Full storage rollback after a process restart cannot be defeated by an in-memory version comparison alone; an external/independently protected freshness floor is still required. LAB-034/LAB-035 provide that architectural layer and should remain separate from key authorization.

## Non-goals
This is a deterministic trust-boundary model, not a general PKI, certificate-transparency system, HSM implementation, or claim that a real external KMS/TPM is available in the current runtime. The HMAC reference key models verification authority; production public-key verification should not store provider private signing material in the verifier.
