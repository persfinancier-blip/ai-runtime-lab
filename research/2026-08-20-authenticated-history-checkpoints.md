# LAB-060 — Authenticated history checkpoints and bounded restart verification

Date: 2026-08-20  
Issue: #111

## Question

How can LAB-059 avoid O(N) bootstrap→head verification on every restart while preserving the exact correctness boundary already established for historical threshold proofs?

## Donor mechanisms

### TUF snapshot/timestamp metadata

The Update Framework separates authenticated snapshot identity from rollback/freeze freshness. Snapshot metadata binds exact versions/hashes of child metadata to prevent mix-and-match; clients reject older trusted versions. Timestamp metadata supplies a fresher signed statement about the snapshot.

Transferable mechanism: a compact authenticated summary can identify a previously verified state, but freshness is a separate monotonic property. LAB-060 therefore authenticates a local history prefix and keeps whole-store rollback detection delegated to LAB-034–037's external monotonic anchor.

Primary source: https://theupdateframework.github.io/specification/draft/

### SQLite atomic transactions / BEGIN IMMEDIATE

SQLite permits one simultaneous write transaction. `BEGIN IMMEDIATE` starts the write transaction before mutation, and atomic commit makes the transaction appear all-or-nothing even across interruption.

Transferable mechanism: checkpoint body plus local checkpoint watermark can be persisted as one atomic local step while excluding concurrent history writers.

Primary sources:
- https://www.sqlite.org/lang_transaction.html
- https://www.sqlite.org/atomiccommit.html

## Protocol

### Checkpoint creation

1. Acquire `BEGIN IMMEDIATE` so another writer cannot change the committed prefix/head.
2. Run LAB-059 full `verify_history()` over the current prefix.
3. Re-read head and require exact equality with the verified terminal pair.
4. Compute a rolling SHA-256 commitment from bootstrap identity through every exact transition row/proof JSON in the verified prefix.
5. Create a checkpoint binding schema version, LAB-059 protocol version, bootstrap-derived history ID, sequence/root/recovery IDs, prefix commitment, external-anchor identity and signer identity.
6. Authenticate the checkpoint and atomically persist it with a local monotonic watermark.

### Restart

1. Strictly parse/authenticate the checkpoint.
2. Require exact current history identity, signer, external-anchor identity and local watermark.
3. Reload checkpoint root/recovery authorities by content ID.
4. Re-verify only rows with `sequence > checkpoint.sequence` using LAB-059 payload reconstruction, threshold signatures, transition digests and predecessor continuity.
5. Require derived terminal state to equal SQL head.

The prefix commitment is intentionally not recomputed on normal restart; doing so would restore O(N) work. Its trust derives from authenticated checkpoint creation and it remains available for external anchoring/audit.

## Failure injection

The corrected suite covers full-replay equivalence, 30+3 bounded restart work, invalid prefix at checkpoint creation, checkpoint tamper, cross-history substitution, stale checkpoint rollback, skipped suffix row, head mismatch, persisted checkpoint-row tamper, wrong external-anchor identity, strict schema types, and an unsafe cache that hides a broken prefix.

## Findings

1. Compaction is safe only when checkpoint creation is downstream of full verification.
2. Authenticity and freshness are separate invariants.
3. Normal restart work becomes O(S), where S is suffix length, plus O(1) checkpoint/authority checks.
4. A mutable unauthenticated derived-state cache can conceal a corrupted prefix.
5. Whole-store rollback remains impossible to detect from an internally self-consistent local database alone; external monotonic evidence is still required.

## Non-goals

No general snapshot database, Merkle proof service, new external-anchor protocol, distributed consensus/fork prevention, or production HMAC key-management claim.

## Audit fixes and observed validation

The first passing version was audited for hidden assumptions:

1. **Restart snapshot race.** Checkpoint validation and suffix/head reads initially used separate SQL snapshots. A concurrent writer could cause a fail-closed but spurious mismatch. The corrected `verify_suffix()` now performs checkpoint, suffix and head validation inside one consistent read transaction.
2. **Archived-prefix integrity versus restart cost.** Normal restart deliberately does not reread the prefix. An explicit `audit_checkpoint_prefix()` recomputes the rolling prefix commitment when forensic verification is required. A regression test mutates an archived prefix proof after checkpoint creation: bounded restart still needs only the suffix, while the explicit prefix audit detects the mutation.
3. **Structural ambiguity.** Checkpoint content IDs, signer ID and signature have strict hexadecimal length/type validation, including rejection of Python `bool` as an integer sequence.

Observed corrected command:

```text
python -m unittest experiments.transition_history_checkpoints.tests.test_protocol -v
Ran 14 tests ... OK
```

Observed unsafe seed:

```text
python -m unittest experiments.transition_history_checkpoints.tests.unsafe_cache_expected_failure -v
FAILED (failures=1)
```

The failure is expected: the unauthenticated cache is accepted as derived authority.

`python -m compileall -q experiments/transition_history_checkpoints` completed successfully.
