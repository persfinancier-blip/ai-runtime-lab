# Current Lab State

Last updated: 2026-08-27

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Current PR #165 HEAD: `e6bf48d81129914b8dbe3e23a2b1a416fab11e24`; current executable pin: `05d8e75a636818afcb32e085d464c9fa9171dea5`.
- GitHub currently reports PR #165 mergeable=false; this is not itself a security/test result and must not substitute for the execution gate.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; fallback only if LAB-086 exact reconstruction/execution is concretely tool-limited.

## Last completed step

Resumed the repinned post-publication LAB-086 gate after the alternate-UNIQUE thaw fix was published byte-exact. The pinned runtime remains `strict_fence.py` blob `eb2198354d222ad0ad6b7d751bf5c649157b6b36` at executable commit `05d8e75a636818afcb32e085d464c9fa9171dea5`.

Performed a fresh schema-level audit of every authenticated-history table whose normal INSERT-deny is temporarily removed by `remove_public_mutation_fence_locked()`. Exact pinned schemas show:
- public recovery authorities: PK `authority_id`, no secondary UNIQUE;
- public recovery transitions: PK `new_authority_id`, no secondary UNIQUE;
- normal root authorities: PK `authority_id`, no secondary UNIQUE;
- normal root transitions: PK `new_authority_id`, no secondary UNIQUE;
- provider threshold proofs: PK `new_provider_generation_id`, no secondary UNIQUE;
- asymmetric provider transitions: PK `new_generation_id`, no secondary UNIQUE;
- asymmetric provider generations: PK `generation_id` plus `UNIQUE(provider_id,generation)`.

Therefore `asymmetric_provider_generations` is the only INSERT-thawed history table with an alternate SQL UNIQUE identity. The published runtime explicitly protects both its content key and the semantic `(provider_id,generation)` identity, and the collision guards are not removed by transaction-scoped thaw. No additional secondary-UNIQUE REPLACE bypass was established in this audit.

Fresh branch/main compare: ahead 180 / behind 129; all 75 PR paths remain additions relative to `main`, so observed divergence remains historical/path-disjoint at this point.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Predecessor published LAB-086 thaw/fence exact subgate: 14/14 PASS + compileall.
- Corrected alternate-UNIQUE regression blob `a767e6bbb5e164a846c93d04b9c8c3f7980bba38`.
- Published `strict_fence.py` blob `eb2198354d222ad0ad6b7d751bf5c649157b6b36` is byte-identical to the corrected candidate that passed the focused alternate-UNIQUE regression 1/1 + `py_compile` before publication.
- This run's exact pinned schema audit found no second alternate-UNIQUE surface among the seven INSERT-thawed authenticated-history tables. This is source/schema audit evidence, not a replacement for execution.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.

## Known blockers / constraints

- LAB-086 remains first priority. Remaining work is the exact published execution gate, not more protocol redesign unless a new executable/source audit blocker appears.
- The retained predecessor 14/14 thaw/fence result must be rerun on the repinned `05d8e75a...` snapshot after the semantic-identity change.
- Direct shell/raw GitHub transport remains unavailable. Connector reconstruction is byte-exact but file-by-file; the per-file PR-patch/blob path is the safe source mechanism.
- PR #165 must remain draft until the repinned strict/thaw subgate, complete branch-local LAB-080→086 real-ledger tests, unsafe seed, compileall and final security/reconciliation audit are all clean.
- LAB-090/#169 provider handoff freshness remains separate. Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Reconstruct exact `strict_fence.py` and strict/thaw test modules from executable pin `05d8e75a...`, verify every local file with `git hash-object`, and execute the repinned subgate: alternate-UNIQUE, primary/history/proof replacement, NULL identities, transaction-scoped thaw minimality, conflict/current-authority/root-head tests + compileall.
2. Reconstruct the complete branch-local LAB-080→086 dependency closure from the same executable pin, hash-verify every file, execute every normal LAB-086 real-schema module, unsafe legacy-promotion expected-failure seed and full compileall.
3. Perform the final security/reconciliation audit and fresh branch/main compare. Only a completely clean gate may make PR #165 ready/integratable.
4. Use LAB-091 fallback only if exact LAB-086 reconstruction/execution is concretely tool-limited again.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; alternate-UNIQUE fix published byte-exact; secondary-UNIQUE audit complete with no additional surface; repinned execution gate next.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173; fallback only while LAB-086 is tool-limited.
