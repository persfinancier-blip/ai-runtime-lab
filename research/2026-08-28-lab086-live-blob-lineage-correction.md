# LAB-086 — live strict-fence lineage correction

Date: 2026-08-28

## Finding

Fresh direct GitHub reads contradict the current durable handoff/Issue wording.

- PR #165 HEAD is `365c5de5c521ae47ad9dd378a2160f8ce7cde291`.
- `experiments/asymmetric_break_glass_history/strict_fence.py` at that exact HEAD is blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`, not `eb2198354d222ad0ad6b7d751bf5c649157b6b36`.
- Exact commit `05d8e75a636818afcb32e085d464c9fa9171dea5` does contain blob `eb219835...`.
- `05d8e75a...` is an ancestor of HEAD; compare reports HEAD ahead by 13 commits and includes subsequent `strict_fence.py` modification.
- Earlier durable state commit `c180fc2b508d0e9077f8e77b39315e837b7a38d2` explicitly recorded a later executable publication whose runtime blob was again `d4a6a40f...` while fixing provider-receipt NULL identity. Therefore the current branch really reverted away from `eb219835...`; this is not merely a stale connector view.

The current Issue/body and handoff therefore overstate the live alternate-UNIQUE publication state.

## Important correction to the previous rebase conclusion

The durable hidden-rowid patch `research/2026-08-28-lab086-hidden-rowid-replace.patch` already contains the alternate-UNIQUE semantic collision clause for `asymmetric_provider_generations`:

`provider_id IS NEW.provider_id AND generation IS NEW.generation`.

Therefore the earlier statement that a candidate constructed by applying that patch to `d4a6a40f...` necessarily drops the alternate-UNIQUE protection is not supported. The patch itself composes that protection with the rowid collision/sentinel guards.

This does **not** promote historical candidate `b78e7c98...` to current executable evidence. Its exact byte lineage and all retained focused tests still need to be re-established against the actual current branch state before publication.

## Current safety decision

1. Treat live branch runtime as `d4a6a40f...` until a new exact write proves otherwise.
2. Treat alternate-UNIQUE as a **live regression on HEAD** even though it has prior focused GREEN evidence at `eb219835...`.
3. Do not apply the standalone alternate-UNIQUE patch and hidden-rowid patch independently without checking composition; the hidden-rowid patch already contains the semantic-collision clause.
4. Construct one combined candidate from exact current `d4a6a40f...`, then require unchanged tests for:
   - provider-receipt NULL identity;
   - alternate `(provider_id,generation)` replacement;
   - hidden rowid collisions/sentinel behavior;
   - existing PK/history/proof/NULL/minimal-thaw conflicts.
5. Publish only exact tested bytes and re-fetch/hash-verify the returned Git blob.

## Execution limitation observed this run

A fresh local `git clone` probe failed because `github.com` could not be resolved. No exact local combined-candidate test run is claimed in this note.
