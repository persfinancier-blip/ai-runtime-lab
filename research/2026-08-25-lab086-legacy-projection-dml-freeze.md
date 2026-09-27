# LAB-086 — Legacy projection DML freeze

## Finding

The authenticated LAB-086 migration projection is the durable replacement for the scrubbed LAB-084/LAB-085 HMAC recovery authority. Before this fix, the post-cutoff policy blocked several *new* legacy INSERT paths, but ordinary SQL UPDATE/DELETE could still alter or remove rows whose semantics were committed by the signed projection.

A focused pre-fix SQLite reproduction showed the distinction directly:

- a new `provider_rotation_recovery_transitions` INSERT was rejected;
- changing an existing legacy recovery edge's `old_rotation_version` succeeded;
- deleting that legacy recovery edge succeeded;
- changing/deleting a `provider_recovery_custody_bindings` row succeeded.

Those mutations do not grant new authority because the verifier later detects divergence. They are still a correctness/security defect at the LAB-086 DML boundary: a stale/raw-DML path can commit persistent fail-closed state and convert an otherwise healthy public-only history into a restart failure.

## Corrected contract

Every SQL row represented by the signed legacy projection is frozen after the authenticated boundary exists.

Four tables require one special transition during the cutoff transaction itself: durable HMAC material is scrubbed. Their UPDATE triggers therefore allow only the exact canonical scrub while requiring all semantic fields to remain identical:

- `provider_rotation_recovery_transitions`: only `signatures_json -> []`;
- `provider_rotation_recovery_authorities`: only `keys_json -> {}`;
- `provider_recovery_lifecycle_authorities`: only `keys_json -> {}`;
- `provider_recovery_lifecycle_transitions`: only the three signature sets -> `[]`.

All other projected legacy tables reject INSERT/UPDATE/DELETE after cutoff:

- compatibility recovery head;
- lifecycle head;
- custody bindings;
- custody break-glass proofs;
- custody enablement and its proof.

The legacy-projection freeze is intentionally **not** removed by the final LAB-086 writer's transaction-scoped thaw. New root/provider/public-recovery operations have no legitimate reason to modify the signed prefix.

## Evidence

- Published `strict_fence.py` blob: `0b9e4dfea254723e65ffb33ccb5c082e1d0c09ad`.
- Published regression `test_legacy_projection_dml_fence.py` blob: `e1df33304cb9808dd099cf8342770f879084d8bb`.
- Exact published focused regression: 4/4 PASS.
- Exact existing `test_strict_fence.py` plus new regression: 14/14 PASS.
- Focused compileall: PASS.
- Production LAB-084/LAB-085 table schemas were re-read after the fix; every scrub-aware trigger references the actual durable column names.

## Boundary

This closes the audited ordinary-DML/stale-writer boundary. It does **not** claim that SQLite triggers can protect against a same-privilege actor with unrestricted schema control (`DROP TRIGGER`, arbitrary DDL, direct database-file replacement). That stronger authority boundary remains LAB-087 / Issue #166.
