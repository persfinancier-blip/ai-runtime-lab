# LAB-097 — provider-history empty-state rebootstrap can erase deletion evidence

Date: 2026-09-02

## Finding

`DurableProviderHistory.__init__()` runs `_init()` before `verify_durable()`. `_init()` creates the provider-history tables if needed, then treats `COUNT(*) == 0` in `provider_generation_head` as a fresh database and inserts the caller-supplied bootstrap generation/head before verification.

That is safe only if an empty provider-history state can occur *only* on first legitimate initialization. The current durable state carries no authenticated installation/provenance marker proving that provider history existed previously.

Consequently, if a previously initialized database has its provider-history rows deleted completely (head, generations, transitions, and any receipts), restart with the original bootstrap can reconstruct generation 1 and then pass `verify_durable()`. The verifier sees a valid one-generation history rooted at the expected bootstrap; the prior generation-2+ history and its deletion are no longer observable.

This is the provider-history analogue of LAB-092 activation-schema provenance, but it is a separate authority surface and must not be fixed only in LAB-092.

## Source proof

`experiments/provider_generation_history/protocol.py`:

- constructor order: `self._init()` then `self.verify_durable()`;
- `_init()` uses `CREATE TABLE IF NOT EXISTS` and, when `provider_generation_head` is empty, inserts `self.bootstrap` into `provider_generations` and `provider_generation_head`;
- `verify_durable()` accepts a one-generation history when its first descriptor equals `self.bootstrap` and the head points at that descriptor.

Because the repair happens before verification, complete deletion of the old history can be normalized into a valid bootstrap-only history.

## Executable SQLite probe

A file-backed SQLite probe reproduced the exact state transition relevant to the constructor:

1. create valid generation 1 -> generation 2 history and head at generation 2;
2. delete all rows from `provider_generation_head`, `provider_generation_transitions`, `provider_generations`, and `historical_provider_receipts`;
3. apply the current `_init()` empty-head logic with the original generation-1 bootstrap;
4. observe a reconstructed one-row generation-1 history/head;
5. evaluate the same terminal verification conditions: non-empty history, first generation equals bootstrap, final descriptor equals head.

Observed output:

```text
rows 1 1 True
head 1 True
verification conditions after repair: True
```

This probe is a database-semantics reproduction, not a claim that the repository test suite executed in this run. Direct Git checkout remained unavailable because `github.com` DNS resolution failed before repository execution.

## Security/correctness consequence

A durable-history verifier that claims rollback/substitution detection cannot distinguish a genuinely fresh database from complete deletion of previously committed provider history. The failure mode is stronger than ordinary missing-row detection: restart actively writes a new bootstrap-only state before the verifier has a chance to reject the loss.

This can erase evidence of prior provider generations and historical receipts and can make generation rollback appear to be legitimate first initialization.

## Regression-first contract

Before production changes, add a file-backed restart regression:

- initialize provider history at g1;
- rotate durably to g2 (or later) and retain at least one historical artifact;
- simulate complete durable provider-history row deletion while leaving the database otherwise recognizable as previously initialized;
- reconstruct `DurableProviderHistory` / supported historical ledger with the original bootstrap;
- pre-fix: demonstrate restart silently recreates g1 and accepts it;
- post-fix: fail closed before inserting any bootstrap/history/head row and leave the tampered state unchanged.

Also cover partial deletion separately: head-only, generations-only, transition-only, and receipt-history loss must not be silently normalized.

## Design direction

Do not solve this with `COUNT(*) == 0` heuristics alone. First initialization needs an explicit, durable provenance contract that cannot itself be erased or recreated by the same startup path without detection.

Candidate direction: compose provider-history installation provenance with the construction-bound authenticated database/history identity being developed in LAB-095, so startup can distinguish:

- a genuinely uninitialized database eligible for bootstrap installation; from
- a previously initialized logical history whose provider-history state is now missing or inconsistent.

The marker/identity must be installed atomically with the initial provider-history bootstrap and verified before any repair/rebootstrap write on restart. A plain self-asserted UUID stored only inside the same deletable SQLite state is insufficient by the LAB-095 reasoning.

## Relationship to existing work

- LAB-092/#176 concerns activation-schema installation provenance after provider history already exists.
- LAB-094/#179 concerns bootstrap trust-root rebinding in a live provider-history object.
- LAB-095/#180 concerns construction-bound authenticated logical database/history identity.
- LAB-096/#181 concerns rebinding the provider-history strategy object.
- LAB-097 concerns **loss of the provider-history durable state itself being rewritten as fresh initialization before verification**.

LAB-086 remains priority #1. LAB-097 should be regression-first and should compose with LAB-095 rather than adding another independent mutable authority marker.
