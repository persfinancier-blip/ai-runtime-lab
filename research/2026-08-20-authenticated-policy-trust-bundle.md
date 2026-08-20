# LAB-050 — Authenticated policy delivery and atomic policy/trust bundle

Date: 2026-08-20  
Issue: #96  
Branch: `lab/050-policy-trust-bundle`

## Question

How should a long-running agent authenticate compliance policy delivery and prove that policy metadata and CT trust metadata came from the same authoritative release, rather than merely being two independently valid histories with overlapping compatibility ranges?

## Primary donor mechanisms

### TUF snapshot metadata

The Update Framework snapshot role records version and optionally length/hash information for delegated metadata. A client checks targets metadata against the already authenticated snapshot metadata; the specification explicitly describes this as protection against mix-and-match. The transferable mechanism is an authenticated parent manifest that commits to the exact child metadata objects expected in one update view.

Primary source: https://theupdateframework.github.io/specification/draft/

### Sigstore TrustedRoot distribution

Sigstore's root-signing repository maintains the TUF repository used to deliver `trusted_root.json` to clients. Sigstore's `TrustedRoot` is the global set of trusted verification material; TUF provides the authenticated distribution/update layer around that object.

Primary sources:
- https://github.com/sigstore/root-signing
- https://github.com/sigstore/protobuf-specs/blob/main/protos/sigstore_trustroot.proto

### Atomic multi-object activation

SQLite transactions provide an executable reference mechanism for making multiple related writes appear atomically committed, including crash rollback. The lab uses a single database transaction to persist manifest, policy, trust and active-release pointer so no reader can observe a half-advanced release.

Primary source: https://www.sqlite.org/atomiccommit.html

## Synthesized protocol

One `BundleManifest` is the authoritative release object. It contains stable bundle lineage id, strict version/generation, publication/expiry interval, authority generation, SHA-256 digest of exact policy bytes, and SHA-256 digest of exact trust-snapshot bytes. The authority authenticates the canonical manifest. Child policy/trust documents become authoritative only when their canonical digests equal the manifest commitments.

Activation is a single transaction: validate content binding; authenticate manifest; reject expiry/future metadata, rollback, gaps and substitution; begin write transaction; recheck active predecessor; insert manifest, policy and trust; update singleton active pointer; commit. Any injected failure before commit rolls back the whole release.

## Failure-injection results

The unsafe baseline advanced policy and trust independently and accepted policy release 2 with trust release 1; the expected-safety assertion failed.

Corrected suite after audit: **15/15 tests passed**. `python -m compileall -q experiments/ctv2_policy_trust_bundle` also passed.

Covered scenarios include valid exact-pair authentication, policy/trust mix-and-match rejection, bad signature, rollback, same-coordinate substitution, four partial-update crash points, idempotent retry, historical replay, stored-digest tamper, stored-document tamper, manifest/object rebinding tamper, authority rotation, skipped release coordinates, and future/expired bundle rejection.

## Audit finding and correction

The first implementation of historical replay trusted digest columns stored next to policy/trust JSON. That was insufficient: storage corruption could alter document bytes while leaving the digest column untouched. The corrected read/replay boundary reparses stored JSON, recomputes manifest/policy/trust digests, verifies manifest coordinates, and rechecks manifest → policy/trust digest binding before returning a historical `DecisionBinding`.

A digest stored beside an object is not evidence of the object's current bytes unless the verifier recomputes it.

## Integration implications

LAB-049 policy and LAB-047/048 CT trust snapshots should no longer enter compliance evaluation through independent “already authenticated” append calls. A production adapter should consume one accepted release/bundle identity and materialize the exact policy and trust documents committed by it.

Each compliance decision should persist bundle lineage id/version/generation, bundle content digest, policy digest and trust digest. Historical replay should resolve the exact tuple and verify bytes again.

## Non-goals / remaining trust boundaries

- HMAC is a deterministic reference authenticator, not production key management.
- Authority-root rotation itself is supplied as a trusted higher-level operation; LAB-037/038-style root lifecycle is the production donor.
- SQLite proves transaction semantics, not universal configuration distribution.
- No gossip, Byzantine consensus or general configuration service is built here.
- Atomic local activation does not prove all replicas see the same release.

## Decision

Use an authenticated release manifest that commits to exact policy and trust object identities/digests, and make activation of the entire tuple atomic. Reject independent policy/trust advancement even when each object is valid in isolation.
