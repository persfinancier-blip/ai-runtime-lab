# LAB-052 — Multi-replica root+bundle convergence

Reference model for distributing the authenticated root+bundle state produced by
LAB-050/051 across multiple replicas.

The model deliberately separates three properties:

1. **Local authentication/continuity** — each replica can validate its own root
   and bundle history.
2. **Safe catch-up/detection** — when two authenticated histories meet, a strict
   prefix may catch up; stale input cannot roll a newer replica back; divergent
   histories raise `SplitViewDetected`.
3. **Consensus/prevention** — **not provided**. Two isolated replicas can retain
   locally valid forks until an exchange/witness path compares the views.

Run:

```bash
python -m unittest discover -s experiments/ctv2_bundle_replica_convergence/tests -p 'test_*.py' -v
```

The unsafe isolated-replica baseline is intentionally outside normal discovery:

```bash
python -m unittest experiments.ctv2_bundle_replica_convergence.tests.unsafe_isolated_expected_failure -v
```
