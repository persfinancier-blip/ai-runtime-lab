# LAB-092 migration writer focused regressions — 2026-09-15

## Scope

Follow-up validation for the opt-in `activation_schema_migration.py` composed on draft PR #187.

## Runtime observation

LAB-086 was probed first with direct `git clone --no-checkout`. Shell transport failed before repository execution with `Could not resolve host: github.com`, exit 128. No LAB-086 PASS is claimed.

The GitHub connector remained available as the durable control-plane fallback. Exact branch materialization into the executable filesystem was still unavailable, so whole-repository pytest/compileall is not claimed.

## Regression added

PR #187 now contains `tests/test_activation_schema_migration_writer.py`, current branch commit `4174376b6b48459ce62e009c1c44e5ea67ed33fc`.

The focused harness isolates the migration writer from unrelated provider cryptography while retaining real file-backed SQLite transaction/DDL behavior. It covers:

1. partial activation DDL fails closed and does not auto-repair the missing trigger;
2. an unrelated PREPARED intent blocks a fresh migration before activation DDL is installed;
3. an unrelated PREPARED intent also blocks exact migration-marker PREPARED resume;
4. stale runtime generation versus durable history fails before activation DDL installation;
5. exact activation DDL + exact PREPARED marker resumes idempotently without advancing `reserved_position` or adding another marker;
6. a CONFIRMED marker with subsequently corrupt/missing activation DDL fails closed and does not repair the corruption.

## Audit

The first authored test slice covered unrelated PREPARED only in the PREPARED-resume state. A separate audit against `state/CURRENT.md` found that the requested fresh-install variant was not explicit. The test file was revised immediately to cover both fresh and resume cases before handoff.

No production code changed in this run. The writer remains opt-in and its authority contract is unchanged: one `BEGIN IMMEDIATE`, private `_history()` durable verification, exact shared activation DDL, deterministic marker, canonical path/history construction, and no post-construction provider-history replacement.

## Validation status

The regression source was written and re-fetched from GitHub. It has **not** been executed against the exact repository closure in this runtime because no supported byte-preserving connector-to-filesystem bridge is exposed. Therefore these tests are committed coverage, not a GREEN claim.

## Next engineering step

After the mandatory LAB-086 probe, inspect LAB-090 PR #175 and port the smallest activation fencing/recovery semantic slice onto PR #187. Preserve the PR #187 authority base: canonical DB binding, construction-bound private provider-history strategy, locked calls through `_history()`, least-capability public inspection, and same-transaction LAB-092 provenance guard. Do not select PR #175 `supported.py` wholesale.
