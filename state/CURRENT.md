# Current Lab State

Last updated: 2026-08-31

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Exact LAB-086 `strict_fence.py` predecessor remains blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch `research/2026-08-28-lab086-hidden-rowid-replace.patch`, blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; exact target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 remains the current allowed fallback while LAB-086 byte-preserving publication/execution is tool-limited. Draft PR #175; branch `lab-090-provider-activation-fencing`; current head `c09e07c5bf96f9bc1fa12771fd54b0b5567fefb6`.
- LAB-091 / #170 remains IN_PROGRESS fallback on draft PR #173.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.

## Last completed step

Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues and active PRs. LAB-086 remained first priority. Direct `git ls-remote` again failed before repository-code execution with `Could not resolve host: github.com`. The GitHub connector can fetch exact blobs and perform normal Contents writes, but no supported byte-preserving predecessor+retained-patch composition primitive was found; no LAB-086 mutation was attempted.

Resumed the permitted LAB-090 narrow audit. Found a durable state-poisoning bug after a lost activation release: SQL provider rotation and activation acknowledgement can already be durable (`COMMITTED`) while `release_activation()` fails before `self.attested` swaps to the new runtime. The old `HistoricalSharedAnchorLedger.reserve()` could then insert a new PREPARED intent using the new durable provider head even though the live runtime was still the old generation; only after commit would `execute()` detect the stale runtime. That leaves a blocking PREPARED tail despite no external effect running.

Published the minimal atomic fix in PR #175 commit `982bc588be0acc05b4218ce4caf49b214816b86b`, `experiments/provider_generation_history/integration.py` blob `bd3f093637b4c619709bdc2d289af17417202697`: under the existing `BEGIN IMMEDIATE`, immediately after loading the durable provider head and before tail mutation/intent INSERT, reservation now derives the live runtime descriptor and requires exact generation-id equality.

Published focused regression in current head `c09e07c5bf96f9bc1fa12771fd54b0b5567fefb6`, `test_activation_integration.py` blob `17f8783291efe1b6a4d0cbbf5977694f707a836f`: `test_failed_release_stale_runtime_cannot_poison_next_intent` reproduces the release outage, requires `CurrentGenerationRequired`, unchanged tail, and no persisted intent.

Executed an independent SQLite ordering mechanism check: old ordering persisted `[('must-not-persist','PREPARED')]` and tail `1`; new ordering failed before mutation and left no intent rows with tail `0`. This validates the transaction-ordering claim but is not an exact PR-head unittest PASS. PR #175 remains draft and mergeable.

Issue #169 updated in comment `5472522420`. Durable evidence: `research/2026-08-31-lab090-stale-runtime-reservation-poisoning.md`, main commit `b689cd715dde0dec1fafb06739a7f1b5978dbc91`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact published signer-noise/core evidence remains 22/22 PASS + compileall; supported/downstream execution pending.
- LAB-091 accumulated adoption hardening/focused reproduced evidence retained; whole-branch timeout/UNKNOWN and process concurrency/crash gates pending.
- LAB-090 provider primitive, premature-release, overlapping-rotation, historical-retry, historical-unresolved restart, orphan-activation restart, provider-state concurrency, and stale-runtime reservation hardening are published. Provider primitive/concurrency exact-byte slice remains 10/10 PASS + compileall. The newest stale-runtime fix has source-level + SQLite mechanism evidence only; integration/restart/downstream exact execution remains pending.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only by conflict-checking exact predecessor `d4a6a40f...`, applying only retained patch `61841b58...` through a byte-preserving supported path, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- Direct git/raw network transport remains unavailable due DNS in this run; treat this as a per-run observation.
- PR #175 remains draft. Exact provider primitive/concurrency slice is validated, but the new stale-runtime regression and broader integration/restart/downstream gates have not yet been executed from exact published bytes.

## Exact next action

LAB-086 first: probe for a supported byte-preserving composition/transfer bridge; if one exists, conflict-check predecessor `d4a6a40f...`, compose only retained patch `61841b58...`, require target blob `b78e7c98...`, publish/re-fetch/hash-verify, then run the full LAB-086 security gate. Otherwise resume LAB-090 PR #175 and reconstruct/hash-verify the exact dependency closure required for `test_activation_integration.py`; execute the new stale-runtime regression plus the existing activation integration/restart set. If the full dependency closure still cannot be reconstructed safely, continue only a narrow source audit for a concrete restart/concurrency defect; do not expand the protocol speculatively.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending on draft PR #172.
- #169 / LAB-090 — IN_PROGRESS; stale-runtime reservation poisoning fix/regression published on draft PR #175; exact integration/restart/downstream gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; draft PR #173; exact whole-branch/full behavioral gates pending.
