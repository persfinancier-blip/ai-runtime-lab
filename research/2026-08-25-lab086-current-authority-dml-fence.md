# LAB-086 — Current-authority DML fence

## Finding

After the authenticated LAB-086 cutoff, the candidate fenced canonical transition/proof writes and the normal-root head, but it still allowed ordinary DML directly against several current authority tables:

- `provider_rotation_authorities`;
- `asymmetric_provider_generations`;
- `asymmetric_provider_head`;
- `provider_rotation_threshold_enablement`.

The already-published regression `test_current_authority_dml_fence.py` exposed the mismatch. A focused pre-fix execution reproduced both failures: a new root authority row could be inserted directly, and an already authenticated root authority row could be updated during the transaction-scoped thaw.

These writes do not create a valid cryptographic history; later verification fails closed. They are still a LAB-086 DML-boundary defect because a stale/raw-DML path can persistently corrupt authority state before the verifier gets another chance to reject it.

## Corrected contract

Current authority state is split into two classes.

Final-writer operations are temporarily thawed only inside the verified `BEGIN IMMEDIATE` transaction:

- create the next root authority row;
- create the next provider generation row;
- insert/update/delete the provider-head singleton as needed by the canonical provider transition;
- the already-existing root-head thaw remains unchanged.

Historical authority state is never thawed:

- existing root authority rows are immutable/non-deletable;
- existing provider generation rows are immutable/non-deletable;
- threshold-enablement is insert/update/delete frozen after cutoff.

The final writer therefore cannot accidentally require a weaker historical policy in order to rotate current authority.

## Conflict algorithms

Focused SQLite execution also attacked the corrected boundary with:

- `INSERT OR REPLACE` on root authority;
- UPSERT `DO UPDATE` on root authority;
- `INSERT OR REPLACE` on provider generation;
- UPSERT `DO UPDATE` on provider generation;
- `INSERT OR REPLACE` on provider head;
- `INSERT OR REPLACE` on threshold enablement.

All were blocked while the fence was installed and the original root/provider heads remained unchanged. These cases are now durable regressions in `test_current_authority_dml_fence.py`.

## Evidence

- Pre-fix focused regression: 0/2 (both expected protections missing).
- Corrected local semantic candidate: existing strict-fence + current-authority regression 12/12 PASS; compileall PASS.
- Additional conflict-algorithm probe: all six attacks blocked.
- Published implementation commit: `4f5bf750a0978616fe6b48b0bc683744ad2ad97a`.
- Published regression commit: `8b52d732f3640ebf657b3ea5048eb670526d6471`.
- Implementation change relative to the prior branch HEAD is one file, +138/-4.

The full current-head LAB-086 real-ledger gate remains mandatory before merge; this focused evidence is not a substitute for that gate.

## Boundary

This closes ordinary post-cutoff DML through stale/alternate supported paths for these authority rows. It does not claim protection against an arbitrary same-privilege actor with unrestricted SQLite schema control; that broader boundary remains LAB-087 / Issue #166.
