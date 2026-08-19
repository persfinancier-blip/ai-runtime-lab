# LAB-039 — Concurrent threshold-rotation serialization and anti-equivocation

Date: 2026-08-19  
Issue: #75  
Branch: `lab/039-rotation-concurrency`

## Question

LAB-038 proved that one proposed root transition can be cryptographically authorized by the required threshold(s). It did not answer a concurrency question: if proposals A and B are both valid successors of root N, what prevents both from being accepted by racing workers, retries, crash recovery, or separate views?

## Primary-source mechanisms

### TUF — successor continuity is versioned but concurrency still needs an activation authority

The Update Framework requires root N+1 to be signed by both the trusted-root N threshold and the candidate N+1 threshold, and clients advance roots in version order. This establishes cryptographic continuity and rollback resistance at the client update boundary. It does not by itself choose between two differently signed candidate files that both claim to be version N+1; an authoritative activation mechanism still has to serialize the successor.

Primary source: https://theupdateframework.github.io/specification/draft/

Transferable rule: activation must bind the exact predecessor identity, not merely check `candidate.version == N+1` outside the commit boundary.

### PostgreSQL Serializable / row locking — conflicting commits serialize or retry

PostgreSQL documents Serializable isolation as equivalent to some serial execution for committed transactions; conflicting transactions may be rolled back with serialization failure and must be retried from the beginning. Row-level `FOR UPDATE` locking similarly prevents concurrent writers from simultaneously owning the same row.

Primary sources:
- https://www.postgresql.org/docs/current/transaction-iso.html
- https://www.postgresql.org/docs/current/explicit-locking.html

Transferable rule: read-current-root, validate predecessor, append activation evidence, and change active root belong in one transaction/CAS boundary. A stale retry must re-read and fail against the winner rather than reuse its pre-race check.

### Certificate Transparency / verifiable logs — local serialization is not global anti-equivocation

RFC 9162 uses append-only Merkle trees and consistency proofs so a later tree can prove it contains an earlier view. It explicitly notes that a misbehaving log can attempt inconsistent views to different clients; checking consistency across query sources requires sharing/monitoring log views. Transparency.dev likewise stresses retaining and publishing checkpoints to make divergent histories observable.

Primary sources:
- https://www.rfc-editor.org/rfc/rfc9162.html
- https://transparency.dev/verifiable-data-structures/

Transferable rule: a transaction can guarantee one successor inside one shared authoritative store. Global anti-equivocation is a separate evidence/distribution problem: activation checkpoints/receipts must be externally comparable, witnessed, or logged if split-view detection is required.

## Reference protocol

`experiments/anchor_rotation_concurrency/` uses SQLite as a deterministic transactional approximation.

Durable state contains a singleton active root with exact digest/version/authority epoch, append-only activation rows, unique proposal identity and proposal digest, unique `predecessor_digest` so one local predecessor can have only one committed successor, and hash-chained activation evidence.

Activation performs threshold verification and predecessor CAS inside one `BEGIN IMMEDIATE` write transaction. The active-root update includes exact predecessor digest/version/epoch in its `WHERE` clause. A committed winner therefore turns every competing old-parent proposal into `StalePredecessor`.

## Failure / race matrix

Observed corrected suite: **11/11 passed**.

Covered:
1. two threshold-valid root rotations from one predecessor -> one winner;
2. real two-thread race -> one committed activation;
3. normal rotation vs break-glass recovery -> one winner;
4. crash before commit -> no activation/evidence, retry succeeds;
5. timeout after commit -> unknown to caller, retry reconciles same receipt;
6. restart -> winner reconstructed, old loser remains stale;
7. same-version substitution after winner -> rejected by predecessor identity;
8. repeated loser retry -> cannot overwrite winner;
9. activation evidence identity remains stable across retry;
10. reuse of a winning `proposal_id` with different transition bytes -> rejected;
11. two independent stores can fork, and an observer that sees both activation records detects equivocation.

Unsafe seed: split check-then-write allowed both proposals to pass the initial predecessor check and then accepted **two successors** (`2 != 1`).

## Audit finding and correction

The first corrected prototype treated `proposal_id` as sufficient for idempotent reconciliation. A caller could reuse an already committed proposal ID with different candidate bytes and receive the old success receipt, creating evidence confusion even though the active root did not change.

Correction: reconciliation now revalidates committed `proposal_digest`, `candidate_digest`, and `predecessor_digest` before returning the receipt. Mismatched reuse raises `ProposalSubstitution`.

The earlier branch draft also represented authorization as a structural list of signer IDs. That would have weakened LAB-038 by treating claimed signers as proof. The final protocol restores deterministic threshold-signature verification for old-root/new-root rotation and separately pinned recovery quorum before activation.

## Decision

Use two distinct guarantees:

1. **Authoritative local serialization** — exactly one successor per exact predecessor through a transactional CAS/unique-parent invariant. Production PostgreSQL should use Serializable or explicit row locking/conditional update and retry the whole transaction on serialization conflict.
2. **Externally observable anti-equivocation** — publish/witness activation evidence/checkpoints so independently served histories can be compared. Transparency evidence detects a split view; it does not replace transactional activation, and transactional activation alone does not prove global consistency if the authority itself forks.

## Non-goals / limits

- SQLite is a correctness reference, not a PostgreSQL concurrency/performance claim.
- The experiment does not implement consensus between independent authorities.
- The observer detects conflicting views once both are observed; it cannot guarantee prevention before gossip/witness exchange.
- HMAC key material remains reference-only; LAB-038 records the production requirement for proper public-key/offline trust-root handling.

## Stop-condition assessment

The required concurrency, retry, crash/restart and anti-equivocation distinction is demonstrated. Remaining work is exact-source validation, remote patch audit, and integration.
