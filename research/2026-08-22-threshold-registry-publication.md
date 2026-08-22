# LAB-077 — Threshold-authorized sink-registry publication

## Question

LAB-076 made registry-authority rotation/recovery threshold-protected, but one active root key can still authenticate one new registry mapping. Can publication itself require a threshold of distinct currently authorized signers without breaking historical verification?

## Donor mechanism

Primary source: TUF specification v1.0.26, especially roles/PKI and root role metadata:
https://theupdateframework.github.io/specification/v1.0.26/

TUF explicitly permits roles to have multiple authorized keys and a `threshold`; metadata for a role is trusted only after enough of that role's keys sign it. Root rotation continuity and the signature threshold required for ordinary role metadata are separate concerns. That distinction maps directly onto the LAB-076 gap: threshold-protecting root evolution does not by itself threshold-protect each registry publication.

## First protocol slice

The isolated prototype defines one canonical registry-entry payload bound to the exact authority content ID and version. Multiple signers sign those exact same bytes. A threshold proof contains the exact authority identity/version plus a canonical signature set; its digest is bound into the stored entry and the full proof is retained for historical verification.

Verification is deliberately strict:
- signer IDs must be distinct;
- every supplied signer must be known and active in the exact root snapshot;
- every supplied signature must be structurally valid and cryptographically valid for the exact entry bytes;
- number of valid distinct signatures must meet the historical root threshold;
- entry, proof and root authority IDs/versions must agree exactly.

Historical acceptance is evaluated against the root snapshot that accepted the entry, so a later root threshold change does not rewrite old acceptance semantics. The old root remains verification-only; it does not regain current publication authority.

## Observed experiment

Local corrected suite: **11/11 passed**.

The unsafe compatibility baseline intentionally treats any one active root key as sufficient publication authority. Its expected-failure test failed because one signer under a threshold-2 root was accepted.

`python -m compileall -q experiments/sink_registry_threshold_publication` passed.

Covered cases include one-signer rejection, duplicate signer inflation, unknown/revoked signers, malformed/invalid signatures, entry/proof mix-and-match, stale authority generation, historical verification under a later threshold change, and stored proof corruption.

## Current limitation / next gate

This first slice is intentionally isolated and does **not** claim that LAB-076's supported journal has already removed its single-signature publication path. Next work must integrate threshold proof storage/verification into the same SQLite transaction that currently binds LAB-076 authority + LAB-075 registry row/head, then exact-type gate the supported worker so a caller cannot fall back to the old single-signature surface.

## Non-goals

No redesign of LAB-076/057 root and recovery lifecycle, distributed signing ceremony, HSM orchestration, remote key management, consensus, or network protocol.
