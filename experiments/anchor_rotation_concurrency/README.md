# LAB-039 — Concurrent root activation reference

This standard-library Python/SQLite prototype closes one gap after LAB-038: two proposals can both be threshold-valid relative to the same predecessor, but only one may become the active successor in a shared control-plane store.

## Local serialization rule

Activation is one transaction: begin a write transaction; re-read the active predecessor; verify exact predecessor digest/version/epoch; verify LAB-038 threshold authorization; append one activation record with a unique `predecessor_digest`; conditionally update the singleton active root from that exact predecessor; commit both together.

A retry of the same proposal reconciles to the same receipt. A different proposal from the old predecessor is stale after a winner commits. `proposal_id` is only a lookup key: reconciliation also verifies proposal, candidate, and predecessor digests.

## Anti-equivocation boundary

The SQLite transaction/unique-parent invariant proves one successor only for actors sharing this control-plane database. It does not prove that a malicious or partitioned operator cannot run two independent databases and show different clients different successors.

`TransparencyObserver` models a detection-oriented second layer: independently observed activation evidence for the same predecessor must name the same successor. If two views disagree, equivocation is detected. Local transaction serialization and global view consistency are separate guarantees.

## Run

```bash
PYTHONPATH=. python -m unittest discover -s experiments/anchor_rotation_concurrency/tests -p 'test_protocol.py' -v
python -m compileall -q experiments
```

Unsafe baseline, expected to fail:

```bash
PYTHONPATH=. python -m unittest experiments.anchor_rotation_concurrency.tests.unsafe_split_check_expected_failure -v
```

## Non-goals

- no claim that SQLite represents PostgreSQL production locking/performance;
- no distributed consensus protocol;
- no globally trusted transparency service;
- no public-key implementation (HMAC remains deterministic reference cryptography inherited from LAB-038);
- transparency detection does not prevent a split view before observers exchange evidence.
