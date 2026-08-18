# Current Lab State

Last updated: 2026-08-19

## Active objective

Execute LAB-019: prove that durable state, evidence, action traces, and kernel semantics remain safe across explicit version/schema migration and rolling overlap between old and new workers.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-018.
- Completed LAB-018 issue: #34.
- Merged LAB-018 PR: #35, squash merge `774915bff73a489a32227320ef03c54740bfc0d4`.
- Active issue: #36 / LAB-019 cross-version state/schema migration and rolling-upgrade conformance — IN_PROGRESS.
- Active branch: `lab/019-versioned-kernel`.
- Active PR: none yet.

## Last completed step

LAB-018 exact-source validation was completed without `git clone`: branch files were fetched through the GitHub connector, materialized locally, and verified byte-for-byte by matching local `git hash-object` output against the GitHub branch blob SHA for every executable module/test used by the required suites.

Observed exact-source results:
- model-conformance suite: 8/8 passed, including all 1,111 depth-3 traces;
- LAB-017 model suite: 5/5 passed;
- LAB-015 transactional-kernel suite: 13/13 passed.

The exhaustive SQLite replay exceeded the runtime command budget on the default temporary filesystem; the same exact source completed in 8.232s with `TMPDIR` on `/dev/shm`. PR #35 was then remote patch-audited and squash-merged. Issue #34 was closed DONE.

LAB-019 was then created as Issue #36 and branch `lab/019-versioned-kernel` was created from current `main`.

## Evidence produced

- `experiments/model_conformance/`
- `research/2026-08-19-model-implementation-conformance.md`
- exact branch blob-SHA equality for the six executed LAB-018 source/test files;
- PR #35 merge SHA `774915bff73a489a32227320ef03c54740bfc0d4`;
- Issue #36 / LAB-019 and branch `lab/019-versioned-kernel`.

## Known blockers / constraints

- Local shell DNS to GitHub is unreliable/unavailable; GitHub connector + local blob-hash verification is an acceptable exact-source path when needed.
- Exhaustive SQLite trace replay is sensitive to temporary-filesystem latency; use a fast temporary filesystem when available, without changing source semantics.
- PostgreSQL-specific locking/performance validation remains deferred until representative PostgreSQL is available.
- Open-model serving efficiency remains deferred pending representative hardware/runtime.

## Exact next action

On `lab/019-versioned-kernel`, research at least three primary-source schema/protocol evolution mechanisms, then implement a bounded versioned-kernel experiment with explicit accept/migrate/translate/reject rules, migration idempotency, old-worker fencing, and model/implementation conformance before and after migration. Demonstrate at least one unsafe migration failure before correcting it. Run deterministic tests, audit, persist evidence, and integrate only after validation.

## Backlog

- #36 / LAB-019 — IN_PROGRESS, highest-value executable task.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
