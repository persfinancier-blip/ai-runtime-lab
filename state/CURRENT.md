# Current Lab State

Last updated: 2026-08-28

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- PR #165 HEAD remains `3cc63c2133507fd8d468471e1fe0fe5b3680e12c`; GitHub reports mergeable=false.
- Last fully executed published LAB-086 runtime/test pin before the hidden-rowid blocker: `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`; published `strict_fence.py` blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`.
- Hidden-rowid candidate remains `b78e7c98e35138719f77c482c7f1aab36b702de7`; runtime is intentionally still unpatched until byte-safe publication is possible.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; current HEAD `c095c08f25ec034614c150b104f75f5b1ecfc707`, mergeable=true, draft. Use only as fallback while LAB-086 exact work is concretely tool-limited.

## Last completed step

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected active PRs and resumed LAB-086 first.

Tested a new supported publication fallback: the GitHub connector can fetch repository blobs directly by SHA, so exact hidden-rowid candidate `b78e7c98e35138719f77c482c7f1aab36b702de7` was requested through that high-level endpoint. GitHub returned 404 Not Found. This establishes that the candidate is not already present in the repository object store and therefore cannot be recovered byte-exact by SHA for subsequent Contents API publication.

Separately re-fetched live branch `strict_fence.py`; GitHub still reports exact predecessor blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`. Re-fetched the durable staged rowid patch; `research/2026-08-28-lab086-hidden-rowid-replace.patch` is published as blob `61841b58be42b01b97ca223567cbf9f428f7f0ce` and still describes the tested candidate mechanism. No runtime mutation was attempted because the available Contents API requires complete replacement UTF-8 text and this run still has no supported byte-preserving local-file/reference transfer for the complete ~40 KB candidate. No low-level Git-data/ref manipulation or manual reserialization was used.

Recorded the publication-path result in Issue #163 comment `5451335495`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Previous repinned LAB-086 strict/thaw exact subgate: 31/31 PASS + compileall on pin `1fa85a0e...`; not sufficient for merge because hidden-rowid conflict was not covered.
- Hidden-rowid exact RED→GREEN retained: predecessor RED 3/3, candidate `b78e7c98...` GREEN 3/3 + compileall; runtime publication still pending.
- Current-run branch predecessor check: `strict_fence.py` remains blob `d4a6a40f...`.
- Current-run candidate-object probe: direct GitHub blob lookup for `b78e7c98...` returned 404, confirming it is not recoverable from GitHub object storage.
- Durable hidden-rowid staged patch remains published as blob `61841b58...`.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 adoption-state/domain gate: 23/23 PASS + compileall.
- LAB-091 alternate lower/legacy connection persistence regression: exact published 2/2 PASS + compileall, blob `365688e0...`.
- LAB-091 prior failed-adoption regression is published as blob `a81c3937...`; it covers corruption before the first inherited verifier.
- LAB-091 adoption-TOCTOU regression is published as blob `262834c3...`; no PASS is claimed yet.
- LAB-091 lock-envelope runtime blob `931bd4ad...`: prior exact local hash match + `py_compile` PASS; prior standalone SQLite serialization probe confirmed sibling read allowed and competing write blocked under `BEGIN IMMEDIATE`.

## Known blockers / constraints

- LAB-086 remains first priority. Hidden-rowid fix must be published byte-exact before the full real-ledger gate resumes.
- Direct shell/raw GitHub transport remains unavailable in the executor from prior probes.
- Direct GitHub blob-by-SHA retrieval is not a fallback for the candidate: `b78e7c98...` returns 404 because that object has never been published.
- The available GitHub Contents writer requires complete replacement UTF-8 text rather than a local file/reference; manually transcribing/reformatting the large security-critical LAB-086 file would weaken exact-blob discipline.
- PR #165 must remain draft until rowid fix publication, repinned strict/thaw subgate, complete real-ledger gate, unsafe seed, compileall and final audit are all clean.
- PR #173 must remain draft. The first-adoption TOCTOU has a published lock-envelope runtime fix and a coherent source-level serialization argument, but deterministic regressions still need GREEN execution on exact real LAB-080/LAB-082 dependencies before the blocker is closed.
- LAB-090/#169 provider handoff freshness remains separate.

## Exact next action

1. LAB-086 first: obtain a byte-safe supported transfer path for exact candidate `b78e7c98e35138719f77c482c7f1aab36b702de7` into `experiments/asymmetric_break_glass_history/strict_fence.py` on PR #165. Publish only if branch predecessor remains `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd` and GitHub returns exactly `b78e7c98...`.
2. Re-fetch/hash-verify the published LAB-086 runtime, execute exact `test_thaw_rowid_collision_regression.py` plus the complete strict/thaw conflict subgate and compileall, then repin only after green evidence; resume the complete LAB-080→086 real-ledger gate afterward.
3. If LAB-086 publication remains concretely tool-limited, LAB-091 fallback: execute `test_adoption_toctou_guard_persistence_regression.py` and `test_failed_adoption_no_guard_persistence.py` against exact PR #173 HEAD `c095c08f...` and the complete real LAB-080/LAB-082 dependency closure. Require GREEN before claiming the adoption race fixed.
4. After that GREEN evidence, continue LAB-091's two-worker/crash, timeout-after-commit/UNKNOWN, reentrancy, alternate legacy-write, and LAB-087 composition gates. Keep PR #173 draft until the complete real-stack gate is clean.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; hidden-rowid blocker has exact RED→GREEN candidate evidence; byte-exact runtime publication is next.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173 HEAD `c095c08f...`; first-adoption lock-envelope fix published, exact real-stack regression execution next when LAB-086 remains tool-limited.
