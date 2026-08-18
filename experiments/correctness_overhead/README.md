# Correctness overhead benchmark

LAB-016 measures local SQLite/runtime overhead of the LAB-015 transactional correctness path. It is a microbenchmark, not a production/PostgreSQL forecast.

Variants:

- `minimal`: one transaction that writes a terminal result with no fencing, outbox, evidence or completion validation;
- `full`: current LAB-015 path (`ensure + claim`, intent/outbox, confirmation, evidence append, completion) using six write transactions per task;
- `batched2`: safe candidate using two transactions: `(claim + intent + outbox)` **before** the external effect, then `(confirmation + evidence + fresh evidence/fence completion decision)` after a receipt is observed.

The second variant deliberately does **not** batch across the side-effect boundary. Doing so would lose the durable intent needed to recover an unknown outcome.

Run:

```bash
PYTHONPATH=. python -m unittest discover -s experiments/correctness_overhead/tests -p 'test_*.py' -v
PYTHONPATH=. python experiments/correctness_overhead/benchmark.py --output experiments/correctness_overhead/results.json --repetitions 120
```

The benchmark warms each database before measurement, runs small (32 B) and larger (64 KiB) evidence payloads, and adds a 4-worker SQLite contention case for `full` and `batched2`.
