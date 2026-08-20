# LAB-051 — Threshold-authorized bundle signer lifecycle

Date: 2026-08-20  
Issue: #98  
Branch: `lab/051-bundle-authority-lifecycle`

## Question

How can LAB-050's authenticated policy/trust release bundle derive its signer authority from the durable threshold/recovery root lifecycle, so restart or a stale caller cannot replace the release-verification key?

## Donors reused

### LAB-037–039

The lab already proved three relevant primitives:

- trust-root verification must distinguish a cryptographically valid signature from current authorization;
- normal rotation needs old-root and new-root threshold authorization, while break-glass recovery uses a separate recovery quorum;
- competing root successors must serialize at one authoritative store boundary.

LAB-051 composes those mechanisms with LAB-050 rather than inventing another root system.

### TUF root update semantics

Primary source: https://theupdateframework.github.io/specification/v1.0.26/

Transferable mechanisms:

- root N+1 must be verified by a threshold from currently trusted root N **and** a threshold from candidate root N+1;
- root versions advance monotonically and intermediate roots preserve a trusted continuity path;
- once trusted, root metadata is persisted to non-volatile storage;
- role keys are derived from trusted root metadata rather than self-asserted by the object being verified.

## Reference protocol

The durable root contains provider identity, root version, authority epoch, threshold root-verification keys, currently authorized bundle-signing keys, and revoked key identities. Each release commits to bundle lineage/version/generation, exact root version + epoch + digest, exact signer identity, and payload digest.

Publication starts `BEGIN IMMEDIATE`, reloads the active root from SQLite, rehashes stored root JSON, then verifies the bundle signer against that active root. Normal root transition and bundle publication therefore share one write-serialization boundary. Historical replay loads the exact historical root used by the stored bundle, but that old root cannot authorize a new publication after rotation.

Recovery authority is persisted separately and reloaded from durable storage; caller-provided recovery configuration after restart is not allowed to replace it.

## Observed experiment

Corrected suite: **12/12 passed**. `compileall` also passed.

Covered: current signer acceptance; stale signer rejection; candidate signer rejection before commit; break-glass epoch change; restart reload; historical attribution without current authority; real two-thread transition/publication serialization; substituted key material; partial-transition rollback; dual threshold requirement; recovery-authority restart substitution; and stored-root tamper detection.

### Unsafe seed

The retained unsafe model exposes `rotate_authority(signer_id, key)` as a trusted setter. An attacker-controlled caller successfully replaces the verifier key without threshold proof, so the safety assertion fails as expected.

## Decisions

- Bundle signer authority is data inside the authenticated durable root, not an independent mutable object.
- Every new release binds exact root digest/version/epoch and verifies against the active root inside the publication transaction.
- Historical verification is distinct from current authorization.
- Recovery quorum is durable authority and cannot be replaced by restart input.
- Root bytes are rehashed on load; an adjacent digest is not enough unless recomputed.

## Non-goals / remaining boundary

No general PKI/HSM service, no multi-replica consensus claim, and no claim that HMAC models production key custody. SQLite is only a single-node serializable authority boundary.

The next material gap is multi-replica distribution/convergence: replicas can each have locally coherent root+bundle histories yet temporarily expose different current releases. That requires a separate cross-replica protocol rather than weakening this authority boundary.
