# Autonomous Software-Engineering Loop

Deterministic reference experiment for LAB-010.

The coordinator models only the lifecycle boundary:

`NEW -> REPRODUCED -> PATCHED -> VALIDATED -> AUDITED -> COMPLETE`

Unsafe or incomplete trajectories move to `HOLD` or `BLOCKED`. An audit regression explicitly returns the task to `PATCHED`.

## Reuse map

This experiment deliberately does not replace earlier mechanisms:

- LAB-005 owns durable run-state, attempt/version/fencing and side-effect recovery semantics.
- LAB-006 owns claim/evidence completion verification semantics.
- LAB-007 owns append-only evidence identity/provenance/invalidation semantics.
- LAB-008 owns per-run capability eligibility, safety filtering and fallback selection.
- LAB-009 owns memory eligibility/supersession/causal retrieval; memory is advisory context, not proof of completion.

The local `Evidence`, `Route`, artifact-version and lifecycle fields are thin stand-ins that expose where those established mechanisms connect.

## Completion gate

Completion requires all of the following for the current artifact version:

1. the bug was actually reproduced;
2. the patch satisfies every declared requirement;
3. a safe available validation route produced observed passing evidence;
4. that evidence matches the current artifact version;
5. a separate audit produced clean evidence for the current version;
6. no unresolved failure class remains.

A plausible patch or an agent-authored success statement is never sufficient.

## Run

```bash
python -m unittest discover -s experiments/software_engineering_loop/tests -p 'test_*.py' -v
python -m compileall -q experiments/software_engineering_loop
```

## Seeded failure taxonomy

- `unreproduced_bug`
- `validation_failed`
- `partial_fix`
- `stale_evidence`
- `audit_regression`
- `no_safe_validation_route`
- `missing_evidence`

The tests include successful safe fallback and explicitly reject a high-preference unsafe route.

## Non-goals

This is not a coding agent, repository sandbox, workflow engine, evidence ledger, memory system, or replacement for real test execution. It is a composition experiment for lifecycle gates and failure classification.
