# LAB-039 — Concurrent threshold-root activation and anti-equivocation

Date: 2026-08-19
Issue: #75
Branch: `lab/039-rotation-concurrency`

## Question

How can a threshold-authorized root transition remain single-valued when two independently valid proposals race from the same predecessor, and what part of anti-equivocation can be guaranteed locally versus only made globally observable through transparency?

## Primary-source donors

### SQLite transaction serialization

- SQLite isolation: https://www.sqlite.org/isolation.html
- SQLite transactions: https://www.sqlite.org/lang_transaction.html
- SQLite atomic commit: https://www.sqlite.org/atomiccommit.html

Transferable mechanism: SQLite serializes writes; `BEGIN IMMEDIATE` acquires write ownership before the application re-reads and mutates state. Atomic commit ensures a crash before commit leaves no partially activated root. A compare-and-swap condition over predecessor digest plus transition sequence makes the activation condition explicit rather than depending only on lock timing.

### PostgreSQL Serializable transactions

- PostgreSQL current transaction isolation: https://www.postgresql.org/docs/current/transaction-iso.html
- Serialization failure handling: https://www.postgresql.org/docs/current/mvcc-serialization-failure-handling.html

Transferable mechanism: successful Serializable transactions have an effect consistent with a one-at-a-time ordering; conflicting transactions may abort and must be retried from the beginning. A production SQL implementation can therefore serialize root activation with either row-level CAS/locking or Serializable transactions, while treating serialization failures as retryable rather than as permission to reuse stale reads.

### Certificate Transparency consistency / public audit

- RFC 9162 Certificate Transparency v2: https://datatracker.ietf.org/doc/rfc9162/

Transferable mechanism: signed tree heads and Merkle consistency proofs make append-only history externally checkable. A local transactional winner is not equivalent to globally observable non-equivocation: independent observers need a shared transparency/consistency mechanism (or equivalent consensus/monotonic anchor) to detect split views across storage replicas or trust domains.

### Threshold authority dependency

LAB-038/TUF-style dual-threshold authorization remains upstream of this experiment. LAB-039 does not replace signature verification; the `signer_ids` accepted by the prototype represent already-validated threshold evidence.

## Protocol

Each candidate proposal binds:

- stable `proposal_id` and canonical `proposal_digest`;
- predecessor root digest, version, and authority epoch;
- candidate root digest/version/epoch;
- transition kind (`rotation` or `recovery`);
- validated signer identities.

Activation is performed inside `BEGIN IMMEDIATE`:

1. persist an idempotent proposal observation;
2. re-read the current active root inside the write transaction;
3. reject if predecessor digest/version/epoch no longer match;
4. enforce exactly-one version increment and rotation/recovery epoch rule;
5. append one transition row with unique predecessor digest;
6. CAS-update the singleton active root using predecessor digest + transition sequence;
7. commit transition and active-root update atomically.

The transition row provides idempotent reconciliation after `UNKNOWN`/timeout: retrying the same `proposal_id` returns the existing receipt; reusing that ID for different content is rejected.

## Unsafe baseline

The retained unsafe design performs `validate()` and `write()` as separate steps. Two proposals both validate against the same predecessor, then both writes are accepted; the second silently overwrites the first. The expected-failure test observed two accepted activations (`2 != 1`).

## Corrected observed results

Executed locally from the prototype source before publication:

- corrected suite: **10/10 passed**;
- unsafe race baseline: **expected failure**, `2 != 1` accepted successors;
- `python -m compileall -q experiments` passed.

Covered scenarios:

1. two concurrently valid normal rotations -> exactly one commit;
2. losing proposal retry cannot overwrite winner;
3. recovery racing normal rotation -> one authority transition;
4. crash before commit -> no transition reservation/half-root;
5. timeout after commit -> reconcile existing receipt, no re-apply;
6. restart reconstructs one active root and monotonic sequence;
7. same-version different-root substitution rejected;
8. proposal ID/content substitution rejected;
9. receipt records proposal/root digests and signer IDs without private material;
10. both competing validated proposals remain locally observable and overlapping signer identities can be surfaced.

## Audit finding

The first corrected implementation serialized activation but only persisted the winner. That is sufficient for local single-valued state but insufficient for investigating signer equivocation: a losing but valid proposal could disappear from evidence. The implementation was amended with an idempotent `proposal_observations` append before activation plus `equivocation_candidates()` that reports conflicting proposal digests and overlapping signer identities.

This does **not** claim global anti-equivocation. A single local database can still be rolled back, forked, or replaced. Global observability requires a separately trusted append-only transparency/consistency mechanism, consensus service, or external monotonic anchor. LAB-034/035 remain the rollback/freshness layer; RFC 9162 is the donor for public consistency evidence rather than a component implemented here.

## Integration implications

- LAB-038 threshold validation decides whether a proposal is authorized.
- LAB-039 transactional activation decides which authorized successor wins.
- LAB-034/035 preserve monotonic freshness/rollback resistance of the durable transition sequence.
- A future transparency layer may publish proposal/transition digests and consistency checkpoints so independent observers can detect equivocation across replicas.

## Non-goals

- no general consensus implementation;
- no production transparency log;
- no replacement of LAB-038 cryptographic threshold verification;
- no claim that SQLite approximates PostgreSQL performance or distributed behavior;
- no claim of global non-equivocation from one transactional database.

## Stop-condition assessment

The required bounded race/crash/retry matrix passes, the unsafe lost-update behavior is reproduced, and local serialization versus globally observable anti-equivocation is explicitly separated. Remaining work is exact-source verification, remote patch audit, integration, and next-gap selection.
