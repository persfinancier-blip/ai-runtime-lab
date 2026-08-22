# LAB-077 — Threshold-authorized sink-registry publication

## Question

LAB-076 made registry-authority rotation/recovery threshold-protected, but one active root key could still authenticate one new registry mapping. Can publication itself require a threshold of distinct currently authorized signers while preserving historical verification, broker idempotency and restart semantics?

## Donor mechanism

Primary source: TUF specification v1.0.26, especially roles/PKI and root role metadata:
https://theupdateframework.github.io/specification/v1.0.26/

TUF permits a role to have multiple authorized keys and a threshold; role metadata is trusted only after enough authorized keys sign it. Root rotation continuity and the threshold required for ordinary metadata are separate controls. LAB-077 applies that distinction to sink-registry publication.

## Integrated protocol

One canonical `RegistryEntry.unsigned` payload is bound to exact authority content ID/version. Distinct active signers sign those exact bytes. The threshold proof contains the authority identity/version plus canonical signatures; its digest is bound into the stored entry, while the complete proof remains durable for restart/history verification.

For a new broker request the supported LAB-077 path performs one SQLite `BEGIN IMMEDIATE` transaction that:

1. decides whether the request already exists;
2. authenticates/observes the exact current sink capability;
3. reloads the exact current LAB-076 root;
4. verifies threshold publication proof;
5. writes/rechecks registry entry + proof + registry head;
6. checks credential generation;
7. records broker `INTENT` with exact capability and registry identities.

Any failure rolls the whole mutation back. Root rotation/recovery uses the same SQLite database, so rotation and publication have one local serialization order.

## Audit findings fixed before integration

The integrated audit found several cross-layer defects that the isolated 11-test prototype could not expose:

- publication initially happened before an existing `CONFIRMED` request was recognized, letting a receipt-only retry move the registry head;
- a precheck still left a TOCTOU where another worker could create/confirm the request before publication;
- terminal `CONFIRMED` reads were accidentally forced through current capability authority;
- pending `INTENT` could inherit a later capability generation;
- a too-weak threshold-change test could fail on authority mismatch before exercising the new root's higher threshold.

The final supported surface fixes these as follows:

- one writer transaction decides existing-vs-new before publication;
- `CONFIRMED` returns the already committed receipt without interpreting current capability or caller registry envelope;
- `INTENT` requires the exact capability identity that originally authorized it;
- `UNKNOWN` may accept a newer capability only for reconciliation when `reconcile_by_key is True`, never to create a second execution authority;
- threshold proof and registry row/head are reverified on restart against exact historical root content.

## Observed exact-source evidence

Connector-reconstructed published Git blobs were hash-checked locally before execution.

- LAB-077 corrected discovery suite: **27/27 passed**.
- Root rotation vs publication threaded race: included 20 iterations inside the passing suite.
- LAB-076 regression: **12/12 passed**.
- LAB-075 protocol + audit regression: **43 passing test executions** (the audit class intentionally inherits/repeats base cases).
- LAB-074 capability integration regression: **18/18 passed**.
- Unsafe one-signer expected-failure seed: failed as expected because the deliberately unsafe class accepted one signer under a threshold-2 root.
- `compileall` passed after deleting a stale local `__pycache__` whose permissions came from source-reconstruction execution; the initial compileall failure was `PermissionError`, not a syntax error.

## Historical and migration semantics

A publication already committed under historical root N remains verifiable after root N+1 changes keys or threshold. Historical root material is verification-only; it does not regain current publication authority.

LAB-077 deliberately fails closed for legacy LAB-076 database rows that have only historical single-signature authorization. It does **not** silently convert those rows into threshold history. Seamless in-place migration would require an explicit migration/checkpoint ceremony and is a separate follow-up, not an implicit fallback.

## Non-goals

No distributed signing ceremony, HSM orchestration, remote key management, consensus, global fork prevention, or automatic legacy single-signature history migration. The guarantee here is local authenticated threshold publication + durable restart verification on the existing SQLite authority boundary.
