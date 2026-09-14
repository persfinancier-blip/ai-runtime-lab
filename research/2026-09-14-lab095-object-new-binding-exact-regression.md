# LAB-095 / LAB-092 object.__new__ canonical binding exact regression

Date: 2026-09-14

## Scope

This run resumed LAB-086 first. Direct shell Git materialization still failed before repository execution with `Could not resolve host: github.com`, exit 128. No LAB-086 gate was weakened and no new LAB-086 GREEN is claimed.

The permitted LAB-095 fallback then executed a small, byte-exact downstream binding regression from PR #187 head `835a81914c5234e68ef436e30c9837331d262432`.

## Exact materialized closure

Two repository files were reconstructed from the GitHub connector into `/dev/shm/lab095_small` and verified with `git hash-object` before execution:

- `experiments/database_binding.py`
  - expected blob: `c6bf05b3a5579e076142300aefbc9d785cc6354a`
  - observed blob: `c6bf05b3a5579e076142300aefbc9d785cc6354a`
- `experiments/provider_generation_history/tests/test_database_binding_object_new_surface.py`
  - expected blob: `25cd1d53fece40ab71a78ff4838381950505ce0d`
  - observed blob: `25cd1d53fece40ab71a78ff4838381950505ce0d`

Result: 2/2 blob identities matched exactly.

## Execution

Command:

```text
TMPDIR=/dev/shm python -m unittest -v experiments.provider_generation_history.tests.test_database_binding_object_new_surface
```

Observed result:

```text
test_object_new_surface_gets_one_canonical_binding_then_cannot_rebind ... ok
Ran 1 test in 0.001s
OK
```

A subsequent `python -m compileall -q experiments` also completed successfully.

## Security meaning

The regression models the LAB-092-style `object.__new__` construction surface. It confirms the exact published `CanonicalDatabaseBinding` implementation allows one first canonical path assignment, rejects reads before initialization, rejects later public `path` rebinding, rejects direct reassignment of `_canonical_database_path`, and continues resolving to the original canonical DB path.

This is useful downstream evidence for the LAB-095 lifetime physical DB binding requirement, but it is not the full DB-A -> DB-B integration regression and does not close LAB-095.

## Remaining gates

Keep PR #187 draft. Still required:

1. exact execution of confirmed-finalize / locked-custody tamper and migration recovery regressions;
2. exact DB-A -> DB-B lifetime binding regression;
3. LAB-080/LAB-081/LAB-090/LAB-092 focused/downstream gates;
4. fresh conflict/security audit before integration.
