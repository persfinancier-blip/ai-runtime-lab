# LAB-092 — explicit activation-schema provenance slice

Date: 2026-08-31

## Objective

Implement the smallest isolated follow-up to LAB-090 that distinguishes legitimate first activation-schema installation from post-install deletion without introducing an unauthenticated local marker or silently repairing durable evidence.

## Published candidate

Branch: `lab-092-activation-schema-provenance`

Base: LAB-090 draft head `d9a381dd4607a928cd1315adef6431e239995bc1`

Commits:
- `5dc92792fd3dc6bcbd5cec14c8b2b6d1cf5f6bd1` — regressions first;
- `ce6fcbedeb838473d68071321df449d339ede290` — implementation.

Draft PR: #177, based on `lab-090-provider-activation-fencing`.

Files added:
- `experiments/provider_generation_history/activation_schema_provenance.py`;
- `experiments/provider_generation_history/tests/test_activation_schema_provenance.py`.

LAB-090 source itself was not modified.

## Contract implemented

The candidate uses one deterministic shared-anchor `migration` intent as the authenticated completion marker:

- component: `provider-generation-activation-schema`;
- intent id: `migration:provider-generation-activation-schema:v1`;
- payload: schema identity + version 1.

Ordering is deliberately DDL-first, marker-second:

1. inherited LAB-090 installs and verifies the canonical activation table + trigger atomically under `BEGIN IMMEDIATE`;
2. only after exact DDL exists does the coordinator reserve/execute the deterministic authenticated migration completion intent;
3. ordinary LAB-092 startup requires exact DDL + CONFIRMED completion marker and then re-authenticates that marker against the external anchor.

State classification:

- table absent + trigger absent + marker absent -> legitimate legacy, explicit migration required;
- exact table + exact trigger + marker absent -> interrupted before marker reservation, explicit migration can resume;
- exact table + exact trigger + PREPARED marker -> explicit migration resumes authenticated completion;
- exact table + exact trigger + CONFIRMED marker -> ordinary startup allowed;
- any partial/mismatched DDL -> fail closed;
- PREPARED/CONFIRMED marker with missing/mismatched DDL -> fail closed, never recreate automatically.

## Regressions published first

1. Legitimate legacy database: ordinary startup raises migration-required; explicit migration succeeds; subsequent ordinary startup succeeds.
2. After completed migration, deleting the activation trigger+table causes both ordinary startup and explicit migration to fail closed, and the table remains absent.

## Validation actually executed

Exact branch checkout / unittest execution was attempted with:

`git clone --branch lab-092-activation-schema-provenance --single-branch https://github.com/persfinancier-blip/ai-runtime-lab.git ...`

It failed before repository code execution because the current shell runtime could not resolve `github.com` (`Could not resolve host: github.com`). No branch-level unittest GREEN is claimed.

Two local checks were actually executed:

- authored implementation syntax: `py_compile` PASS;
- file-backed SQLite state-machine probe: produced `LEGACY_ABSENT`, `DDL_INSTALLED_UNMARKED`, `DDL_INSTALLED_PREPARED`, `COMPLETE`, and `FAIL_CLOSED` after post-completion deletion.

These are mechanism-level checks only, not substitutes for the exact repository behavioral gate.

## Audit notes

- No unauthenticated side table or standalone local marker was added.
- Completion provenance reuses LAB-080's authenticated `migration` intent mechanism.
- No marker-before-DDL ambiguity remains.
- Post-completion deletion cannot enter the legacy installation path.
- The implementation is isolated from LAB-090 pending behavioral proof.

## Next gate

When exact branch execution becomes available, run `experiments.provider_generation_history.tests.test_activation_schema_provenance` first. If GREEN, add/execute the remaining LAB-092 matrix: trigger-only post-completion deletion, partial DDL with absent/PREPARED marker, concurrent writer during explicit migration, and PREPARED-marker recovery. Then audit interaction with unresolved LAB-090 activation records before considering PR #177 ready.
