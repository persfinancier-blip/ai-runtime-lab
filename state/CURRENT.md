# Current Lab State

Last updated: 2026-08-27

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Current observed PR #165 HEAD: `9b2b08502af0e4230f20b55f4fef9a209dcd2081`; draft=true. Runtime `strict_fence.py` is still published blob `cea0ca3b42723790971ba9415b70a7e9fa0c7368`.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; fallback only while LAB-086 exact execution/publication is concretely tool-limited.

## Last completed step

Closed the previous byte-reconstruction bottleneck for the current LAB-086 thaw-key fix. The published `strict_fence.py` was reconstructed locally from connector line ranges and `git hash-object` matched GitHub blob `cea0ca3b42723790971ba9415b70a7e9fa0c7368` exactly.

Applied the already-reviewed combined staged change mechanically to those exact bytes:

- NULL-safe proof-key collision semantics: `NEW.key IS NULL OR EXISTS(... key IS NEW.key)`;
- permanent NULL-safe existing-key collision triggers for all seven other authenticated-history tables whose ordinary INSERT-deny is removed during final-writer thaw;
- those permanent collision triggers are included in full reinstall cleanup but are never removed by `remove_public_mutation_fence_locked()`;
- `assert_public_mutation_fence_locked()` requires every applicable collision trigger.

The resulting exact local candidate has Git blob `080eb9454437932a8ab419d66a4f2a69ed17c7ce`; `py_compile` passed and the diff is limited to the staged combined change.

Reconstructed four exact published regression files and verified each by `git hash-object` before execution:

- `test_strict_fence.py` `97048a325c4cc1ed78612bdbb4cfec42146a43f6`;
- `test_thaw_null_proof_key_regression.py` `fce5c57c8cfaa18f6761ae9b47c211813801aae0`;
- `test_thaw_history_key_collision_regression.py` `88ba35e933c123d10af65597d6bb51f4f11068ec`;
- `test_thaw_proof_replace_regression.py` `c511ccfc4b88b050910561b3b8f7e99be5f33e93`.

Focused result on candidate `080eb945...`: **14/14 PASS**. Package compileall also passed. New unique non-NULL keys remain creatable by legitimate thaw; existing keys and NULL identities fail closed.

Durable verification note added on PR branch: `research/2026-08-27-lab086-combined-thaw-candidate-verification.md`, commit `9b2b08502af0e4230f20b55f4fef9a209dcd2081`. Issue #163 also contains the exact evidence.

## Evidence retained

- LAB-086 lower-stack exact evidence: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, asymmetric custody 8/8, public/final 11/11; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Current combined thaw candidate `080eb945...`: exact focused **14/14 PASS** + compileall on byte-verified current runtime source and byte-verified published tests.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 retained evidence remains fallback only.

## Known blockers / constraints

- PR #165 must remain draft. The combined candidate is exact and focused-green but runtime `strict_fence.py` has not yet been replaced on GitHub.
- Available high-level GitHub write action accepts whole UTF-8 text only and exposes no mounted-file/patch parameter. Low-level tree/ref manipulation is prohibited by `AGENTS.md`. Do not hand-transcribe the ~37 KB candidate without an exact transfer path.
- Focused 14/14 is not the complete branch-local LAB-080→086 real-ledger gate.
- Direct shell/raw GitHub transport remains unavailable; connector exact reads work.
- LAB-090/#169 provider handoff freshness remains separate. Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Publish only a byte-identical `strict_fence.py` candidate whose resulting GitHub content blob is `080eb9454437932a8ab419d66a4f2a69ed17c7ce`; immediately re-fetch it and rerun the exact 14-test focused gate.
2. Repin `research/2026-08-27-lab086-exact-gate-manifest.md` to the post-fix executable commit/blob.
3. Reconstruct that exact branch-local LAB-080→086 closure and execute every normal LAB-086 real-schema module, then unsafe legacy-promotion seed separately, full compileall and final security/reconciliation audit.
4. Keep PR #165 draft until the entire post-fix gate is clean; only then mark ready/reconcile/integrate.
5. If the exact runtime publication path remains unavailable, continue LAB-091 real-stack fallback rather than weakening LAB-086 byte-integrity requirements.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact combined thaw candidate `080eb945...` focused-green 14/14; runtime publication + full gate remain.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; fallback only while LAB-086 exact gate is tool-limited.
