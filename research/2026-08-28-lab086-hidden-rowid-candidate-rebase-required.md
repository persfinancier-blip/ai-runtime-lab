# LAB-086 — hidden-rowid candidate must be rebased onto the live strict-fence predecessor

Date: 2026-08-28

## Finding

The durable handoff still named hidden-rowid candidate `b78e7c98e35138719f77c482c7f1aab36b702de7` as the byte-exact publication target. That candidate is no longer the correct live target.

The exact RED→GREEN note proves `b78e7c98...` was constructed from predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd` at executable pin `1fa85a0e...`.

Since then PR #165 published the independent alternate-UNIQUE thaw fix. The live `strict_fence.py` blob is now `eb2198354d222ad0ad6b7d751bf5c649157b6b36` at executable commit `05d8e75a636818afcb32e085d464c9fa9171dea5`.

A fresh source read of the live branch confirms the hidden-rowid changes are absent: `_all_provider_receipt_trigger_names()` still returns only `PROVIDER_RECEIPT_HISTORY_FREEZE_TRIGGERS`, `_all_thaw_insert_history_collision_trigger_names()` still emits only the base collision trigger names, and `_install_thaw_insert_history_collision_fences_locked()` does not contain the rowid collision/sentinel clauses from `research/2026-08-28-lab086-hidden-rowid-replace.patch`.

Therefore `b78e7c98...` is a valid historical candidate/evidence artifact, but it must not be published over the newer live runtime because doing so would risk dropping the already-published alternate-UNIQUE hardening.

## Decision

Invalidate `b78e7c98...` as the current publication target while retaining its 3/3 GREEN evidence as proof that the hidden-rowid mechanism works on the older predecessor.

The next executable candidate must be constructed by applying the durable hidden-rowid patch semantics to exact live predecessor `eb219835...`, then:

1. compute and record the new candidate Git blob;
2. execute unchanged `test_thaw_rowid_collision_regression.py` against the live predecessor (expected RED) and the rebased candidate (required GREEN);
3. execute the alternate-UNIQUE regression unchanged against the rebased candidate to prove no regression of `eb219835...`;
4. run the complete strict/thaw conflict subgate plus compileall;
5. publish only those exact tested bytes through a supported byte-preserving path and require GitHub to return the new recorded blob.

PR #165 remains draft until that gate and the full LAB-080→086 real-ledger gate are clean.
