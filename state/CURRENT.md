# Current Lab State

Last updated: 2026-08-26

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active priority: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `37e219a2d3947112d71306fad21518d81d1dad18`.
- PR is mergeable but remains draft; a new pre-cutoff lower-evidence cardinality blocker is staged but not yet fixed in runtime.
- Parallel LAB-087/#166 remains IN_PROGRESS; its exact authorizer/process/filesystem gate was previously 12/12 PASS.

## Last completed step

Solved the exact-source transport bottleneck: direct shell/raw GitHub transport remains unavailable, but connector `fetch_blob` returns byte-stable source by Git SHA. Exact LAB-080 shared-anchor `protocol.py` (`68834409363c93eee4e9a9a7b9ec076098af0acf`) and `supported.py` (`22a05c04831f65c1d7fe9077df3bb780c4008e09`) were reconstructed locally and matched `git hash-object` exactly. This is now the required reconstruction path; manual line-range copies are not evidence.

A fresh cutoff audit then found a real LAB-086 blocker. LAB-082/LAB-083 durable verification is reference-driven: it verifies the proof/transition required by every known successor but does not reject extra durable rows in the reverse direction. LAB-086 migration projection also does not commit provider transition/threshold-proof rows. Therefore an orphan `asymmetric_provider_transitions` row or orphan `provider_rotation_threshold_proofs` row can remain unexplained while the current pre-cutoff walk sees no referenced row to reject.

A focused SQLite diagnostic reproduced both cases: the current joined threshold walk returned an empty set while the orphan rows remained present; exact set/cardinality comparison detected both. This focused diagnostic is evidence for the SQL relation only, not the real-ledger regression result.

Durable branch work:
- red real-ledger regression `tests/test_pre_cutoff_lower_evidence_cardinality.py`, commit `b9258431f8cbfd87b5c4ead2246e44a84d8b11e5`;
- staged migration-guard patch `research/2026-08-26-lab086-precutoff-lower-evidence-cardinality.patch`, commit `b72879c4918acd81f75a2a83e51d6471e8578bac`;
- rationale note `research/2026-08-26-lab086-precutoff-lower-evidence-cardinality.md`, current branch HEAD `37e219a2d3947112d71306fad21518d81d1dad18`.

The runtime `migration_guard.py` intentionally remains unchanged until the red regression is executed in the exact connector-reconstructed closure and the whole-file patch is byte-audited.

## Evidence produced / reconfirmed

- Exact LAB-086 migration guard integration previously: 11/11 PASS.
- Exact corrected scrubbed-prefix → final-writer → restart regression previously: 1/1 PASS.
- Current unchanged LAB-086 implementation blobs: migration guard `5a5bb928b39a96f93f019b103b483dfb9bf43c6d`, strict fence `5da01e28a9f813a136d138637f855940f04aab46`, suffix `44847bde53b9f7b0e2fbcbab37d36dc992f497b2`, final supported `ceb7f48a55a931ba9923cac77d4ebf6c4cd2cfec`.
- Current `test_suffix.py` blob `14b87522974a365738a56d82923ed9ae377a752e`; successful post-cutoff mutations use the final fenced surface.
- Cumulative exact lower-stack evidence remains: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, asymmetric-custody 8/8, public/final 11/11; lower unsafe baselines failed as intended.
- Fresh source/schema coverage audit found no additional privilege-escalation/stale-supported-writer bypass beyond the new cardinality issue; mutable shared-anchor/new-receipt authorization remains #170 and arbitrary same-privilege DDL/schema control remains #166.
- Last branch/main compare before the new three branch commits was ahead 142 / behind 83 with LAB-086 paths additions-only; re-check before integration.

## Known blockers / constraints

- New merge blocker: LAB-086 must reject unexplained lower provider/root evidence before signing the cutoff. The staged patch requires exact real-ledger execution and byte-audited runtime application.
- Full current-head LAB-086 gate remains incomplete: updated `test_suffix.py` and remaining final-supported/security modules still require one exact reconstructed closure, followed by unsafe seed, full compileall and final audit.
- Direct shell GitHub transport remains unavailable; connector `fetch_blob` is the supported exact-source fallback and is not an owner blocker.
- LAB-086 SQL fences cover audited supported/DML paths, not arbitrary same-privilege schema/DDL authority; LAB-087/#166 owns that boundary.
- LAB-088/#167 signer-noise, LAB-090/#169 provider handoff freshness, and LAB-091/#170 mutable shared-anchor/new-receipt authorization remain separate follow-ups.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Continue connector `fetch_blob` reconstruction of exact LAB-082→085 implementation bytes into one workspace, verifying every executable dependency by `git hash-object`.
2. Execute `test_pre_cutoff_lower_evidence_cardinality.py` against that exact real-ledger closure and confirm the current runtime is red for the two orphan cases.
3. Apply the staged cardinality patch to exact migration-guard blob `5a5bb928b39a96f93f019b103b483dfb9bf43c6d` using the safe whole-file Contents API fallback; inspect the resulting PR file diff/blob and require only the intended cardinality method + preboundary call changes.
4. Re-run the new regression green, then execute current `test_suffix.py` and all remaining LAB-086 real-schema modules, unsafe legacy-promotion seed and full compileall.
5. Perform a final security audit and branch/main conflict check. Fix every blocker before marking PR #165 ready/integrating.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; new pre-cutoff lower-evidence cardinality blocker staged with red regression + patch, runtime not yet changed.
- #166 / LAB-087 — IN_PROGRESS; prior exact current slice 12/12 PASS.
- #167 / LAB-088 — READY; threshold signer-noise robustness.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — READY; mutable/shared-ledger plus new provider-receipt writer authorization.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
