# Abstract-model / implementation conformance

Date: 2026-08-19  
Issue: #34 / LAB-018

## Question

How do we detect semantic drift between a small correctness model and the executable transactional kernel before either side silently becomes the de-facto specification?

## Donor mechanisms

### Hypothesis stateful testing

Primary documentation: https://hypothesis.readthedocs.io/en/latest/stateful.html

Hypothesis explicitly demonstrates driving the same operations against a real database and a simplified in-memory model, then asserting agreement. Stateful tests generate sequences rather than isolated inputs and shrink failures toward short reproducing programs.

Transfer: use a shared action vocabulary, compare model and system-under-test after every step, and persist the shortest first-divergence prefix as a regression contract.

### Jepsen / Knossos lineage

Primary project: https://jepsen.io/ and https://github.com/jepsen-io/knossos

Jepsen-style checking separates an observed implementation history from a model/specification used to judge allowed behavior. The transferable idea is that implementation observations must be normalized before checking; logs or success strings are not themselves the specification.

Transfer: keep the implementation adapter explicit and inspectable; do not bury semantic normalization inside the model.

### SQLite testing philosophy

Primary documentation: https://www.sqlite.org/testing.html

SQLite documents extensive boundary, fault and differential-style testing as complementary techniques rather than relying on one test family.

Transfer: conformance testing complements, rather than replaces, transactional unit tests and model exploration.

## Experiment

`experiments/model_conformance/` binds the LAB-017 action model to the real LAB-015 SQLite `Kernel`. The adapter normalizes SQL state plus an idempotent external-effect simulator into the abstract state schema and compares after every authoritative action.

The generated depth-3 space contains 1,111 traces including prefixes. Longer corpus traces cover completion, invalidation, duplicate delivery, UNKNOWN reconciliation and stale authority.

Five implementation-only defects are seeded and required to diverge at the exact bad step: terminal reopening, stale-fence mutation, completion on invalid evidence, duplicate UNKNOWN effect, and failure to revoke terminal completion after evidence invalidation.

## Defects found by conformance work

### Abstract model: zero fence accidentally counted as authority

LAB-017 originally allowed `intent` when `fence == max_fence == 0`. The SQLite kernel correctly rejected the unclaimed owner. The model was tightened to require `fence > 0` for authoritative intent/effect transitions.

### Abstract model: INVALID was not fully terminal

The model could accept new intent/evidence after terminal evidence invalidation and completion was not explicitly phase-gated. INVALID is now terminal for intent/evidence and normal completion requires `phase == CONFIRMED`.

### SQLite kernel: invalidating completion evidence did not revoke DONE

`Kernel.invalidate()` originally changed only the evidence row. That left a work item in `DONE` while its completion evidence was invalid. The corrected transaction now moves matching `DONE` work to `INVALID` while invalidating the evidence.

### SQLite kernel: terminal work could be reconfirmed or marked UNKNOWN

`confirm_effect()` and `mark_unknown()` previously checked owner/fence but not terminal phase. They now reject mutation from `DONE`/`INVALID`.

These are cross-representation defects: neither ordinary unit tests nor abstract exploration alone guaranteed discovery.

## Validation evidence

Direct `git clone` of the branch was unavailable because the local runtime could not resolve `github.com`, so exact branch files were fetched through the GitHub connector and materialized locally. Exactness was independently verified by computing Git blob SHA-1 locally and matching GitHub's branch blob SHA for every executable module and test used by the three required suites.

Observed exact-source results:

- `experiments.model_conformance.test_harness`: **8/8 passed**, including all 1,111 action traces through depth 3 and all seeded first-divergence defects.
- `experiments.state_space_kernel.test_model`: **5/5 passed**.
- `experiments.transactional_kernel.tests.test_kernel`: **13/13 passed**.

The exhaustive SQLite replay exceeded the runtime command budget on the default temporary filesystem without producing an assertion failure. Re-running the same exact source with `TMPDIR` on `/dev/shm` completed the conformance suite in 8.232 seconds. This is recorded as an execution-environment performance dependency, not a semantic change or correctness exemption.

## Decision

Adopt model/implementation differential replay as a standing correctness layer:

- every new abstract action needs an implementation adapter mapping;
- compare after each step, not only final state;
- persist first-divergence prefixes;
- disagreement triggers audit of both model and implementation;
- historical production defects become seeded drift variants;
- bounded conformance is falsification evidence, not proof of universal equivalence.

## Non-goals

- no claim of formal refinement proof;
- no replacement for SQL concurrency tests;
- no PostgreSQL equivalence claim from SQLite;
- no automatic assumption that the abstract model wins a disagreement.
