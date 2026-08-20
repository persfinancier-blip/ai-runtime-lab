# LAB-056 — Threshold-authenticated observer-registry root lifecycle

## Question

How should LAB-055's observer registry remove its final single static root-key assumption without inventing a separate authority system?

## Donors

LAB-038 already demonstrated versioned root state, unique signer counting, revoked signer exclusion, old+new threshold rotation, and separate recovery authority. LAB-056 reuses those semantics.

The TUF specification requires root version N+1 to be signed by both a threshold of keys trusted by root N and a threshold of keys declared by root N+1, with exactly sequential root versions. That mechanism transfers directly to observer-registry authority rotation.

Primary source: https://theupdateframework.github.io/specification/v1.0.32/

The C2SP witness protocol defines a witness by a name and public key, reinforcing the separation between membership identity/key material and the authority that authorizes membership.

Primary source: https://c2sp.org/tlog-witness@main

## Protocol

- `RootState`: registry identity, version, authority epoch, threshold, signer keys, revocations, content-derived `root_id`.
- Normal rotation: exact `version+1`, same authority epoch, old-root threshold and new-root threshold over one canonical transition.
- Break-glass recovery: separate pinned recovery quorum, exact `version+1`, `authority_epoch+1`.
- Registry snapshots bind exact `root_id + root_version + authority_epoch` and threshold signatures from that root.
- New registry state may only be signed by the current root; historical roots only verify historical state/evidence.
- Observer evidence binds both registry snapshot and root identity.
- Restart revalidates bootstrap root, durable transition proofs, root IDs, registry chain/current pointers, and pinned recovery-authority identity.

## Audit finding

The first corrected implementation persisted root states but not the cryptographic proof of each root transition. A fabricated but structurally plausible root history could therefore have survived restart. The final design persists each old/new threshold proof or recovery-quorum proof and re-verifies the complete root chain at load time.

## Boundary

Threshold authentication reduces single-signer compromise risk but is not consensus and does not prevent malicious actions after threshold compromise. HMAC is a deterministic reference signature primitive; production requires real asymmetric signing/HSM-equivalent custody.
