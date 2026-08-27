# LAB-086 alternate-UNIQUE thaw regression — byte-exact RED→GREEN verification

Date: 2026-08-27

## Scope

Verify the current blocker in `asymmetric_provider_generations` without weakening the established byte-integrity gate.

## Exact reconstruction

The current published `experiments/asymmetric_break_glass_history/strict_fence.py` was reconstructed locally from GitHub connector line ranges. Before any modification:

- expected Git blob: `080eb9454437932a8ab419d66a4f2a69ed17c7ce`
- local `git hash-object`: `080eb9454437932a8ab419d66a4f2a69ed17c7ce`

The staged patch in `research/2026-08-27-lab086-thaw-alternate-unique-collision.patch` was then applied programmatically to that exact source. The resulting local candidate blob is:

- `eb2198354d222ad0ad6b7d751bf5c649157b6b36`

`py_compile` passed for the candidate.

## Regression harness correction

The initially published regression created only the migration boundary and `asymmetric_provider_generations`. That fixture was incomplete because `install_public_mutation_fence_locked()` always installs public recovery authority/transition/head triggers. The test therefore raised `sqlite3.OperationalError` before reaching the intended attack.

The fixture was corrected to create minimal `provider_recovery_public_authorities`, `provider_recovery_public_transitions`, and `provider_recovery_public_head` tables. Corrected test blob:

- `a767e6bbb5e164a846c93d04b9c8c3f7980bba38`

## Executed RED→GREEN evidence

Using the corrected exact test bytes:

1. Exact published runtime `080eb945...`: **RED as intended** — `INSERT OR REPLACE` using a new `generation_id` but existing `(provider_id,generation)` did not raise `IntegrityError`.
2. Programmatically patched candidate `eb219835...`: **GREEN 1/1** — the alternate semantic collision was blocked and the original authenticated row remained unchanged.
3. The same GREEN run confirmed that a legitimate genuinely new successor `(generation_id, provider_id, generation)` remains insertable during verified thaw.

## Broader schema audit

Reviewed the SQL schemas for every table whose normal INSERT guard is removed during LAB-086 thaw. Among those authenticated-history tables, the only secondary SQL UNIQUE identity found is:

- `asymmetric_provider_generations`: `UNIQUE(provider_id,generation)` in addition to `generation_id TEXT PRIMARY KEY`.

The other inspected thawed tables use their successor/content primary key without an additional UNIQUE constraint. Therefore the staged semantic collision predicate can remain narrowly scoped to `asymmetric_provider_generations`; no broader speculative policy change is required for this class of SQLite REPLACE bypass.

## Publication status

The runtime candidate is **not yet published**. Available GitHub write tooling still replaces the ~935-line security-critical file as one complete text payload. The exact local reconstruction removes uncertainty about the candidate bytes, but a safe publication step must still ensure that the complete replacement submitted to GitHub is exactly the locally verified candidate, not a manually retyped approximation.

PR #165 must remain draft until the candidate is published, its GitHub blob is verified, the strict/thaw subgate passes on published bytes, a new executable snapshot is pinned, and the full LAB-080→086 real-ledger gate is clean.
