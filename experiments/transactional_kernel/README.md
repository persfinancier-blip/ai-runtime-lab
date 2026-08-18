# Transactional Correctness Kernel

LAB-015 reference prototype. Standard-library SQLite is used only to execute and falsify transaction/concurrency invariants; it is not claimed equivalent to PostgreSQL or a distributed lease service.

## Invariants
- claim advances `generation` and `fence` atomically;
- only the current owner/fence may mutate state;
- effect intent and outbox identity are committed together;
- terminal completion checks evidence validity in the same write transaction that commits `DONE`;
- duplicate delivery reuses one logical `effect_key`/outbox dedupe key;
- rollback leaves no partial authoritative state;
- restart reads only committed state.

Run corrected matrix:

```bash
python -m unittest discover -s experiments/transactional_kernel/tests -p 'test_*.py' -v
```

Run deliberately unsafe split-transaction baseline:

```bash
python -m unittest experiments.transactional_kernel.tests.unsafe_seed_expected_failure
```

The unsafe baseline is expected to fail because it validates evidence, then permits invalidation, then commits `DONE` in a separate transaction.
