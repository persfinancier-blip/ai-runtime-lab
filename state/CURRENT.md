# Current Lab State

Last updated: 2026-08-30

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Authoritative LAB-086 `strict_fence.py` predecessor: `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`.
- Retained hidden-rowid patch: `research/2026-08-28-lab086-hidden-rowid-replace.patch`, blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; exact previously derived target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-091 / #170 is the allowed fallback while LAB-086 publication/execution is concretely tool-limited; draft PR #173, branch `lab/091-mutable-shared-anchor-writer`.
- Current LAB-091 PR head: `2297ad975b6e4ea03a90efa531a477119fdc301e`.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172. LAB-090 / #169 remains READY.

## Last completed step

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues/PRs. LAB-086 remains first priority. Current-run executable transport was re-probed and remains unavailable: `git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD` failed with `Could not resolve host: github.com`. No supported machine-to-machine byte-preserving composition path for the exact 949-line LAB-086 predecessor plus retained patch was observed, so no LAB-086 mutation was attempted.

Continued the LAB-091 fallback static/reproduction audit and found a reachable first-adoption write-compatibility defect. A legacy `intent_id TEXT COLLATE NOCASE PRIMARY KEY` plus a separate BINARY UNIQUE overlay passed the previous canonical-identity check. Final BINARY lookup correctly treats existing `Alpha` and requested `alpha` as distinct, but the retained NOCASE primary key still rejects the supported-shape `alpha` INSERT with `UNIQUE constraint failed`. Adoption therefore accepted a schema unable to implement LAB-091 byte-exact identity semantics.

Published on PR #173:
- `bbe3b62858366f1c40bc7364b78596ee15ac2a56` — `adoption_schema_domains.py` blob `db16ee7783e259b7d9f2764f9fae593b8e69c1f7`; schema-domain validation now rejects partial/expression/extra/non-BINARY UNIQUE constraints that can make canonical supported writes fail;
- `2297ad975b6e4ea03a90efa531a477119fdc301e` — regression `test_adoption_restrictive_unique_regression.py`; PR re-fetch confirms this as current head and PR remains DRAFT.

Executed local SQLite mechanism gate:
- canonical unique contract accepted;
- NOCASE PK + BINARY overlay rejected;
- extra UNIQUE payload constraint rejected;
- `Alpha` followed by otherwise supported-shape `alpha` reproduced the legacy NOCASE uniqueness failure.

This is mechanism evidence only; exact branch pytest was not executed because executable GitHub transport is unavailable in this run.

Static follow-up on remaining v2/v4 trigger `IS NOT` / default-collation comparisons found case-only differences can inherit NOCASE, but no supported writer path was found that mutates those identity columns; unknown persisted triggers are rejected at adoption. No speculative trigger patch was added.

Durable analysis: `research/2026-08-30-lab091-restrictive-unique-adoption-gap.md`, main commit `fd87538314e9249e87ff163c8f431524aa3c2ad9`; issue #170 comment `5465468023`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- LAB-086 hidden-rowid RED→GREEN evidence retained; exact predecessor `d4a6a40f...` -> candidate `b78e7c98...` previously byte-rederived and mechanism-tested; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 earlier adoption hardening combined focused gate 17/17 PASS before later affinity/collation fixes.
- LAB-091 receipt affinity, receipt collation, identity lookup, constructor ordering and receipt-orphan collation defects have published fixes with local focused semantic/mechanism evidence; latest exact regressions remain pending executable transport.
- LAB-091 restrictive UNIQUE adoption gap now reproduced and patched on `2297ad97...`; local SQLite mechanism gate PASS; exact published pytest pending.
- LAB-091 timeout/UNKNOWN regression blob `92133cdc54fd8b95eb9e3270b5e69d4b85a4b05` and process concurrency/crash regression blob `938877479d4c4b997ea52e8b5857bf89e5c3e246` remain pending full final-surface execution.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only by conflict-checking exact predecessor `d4a6a40f...`, applying only the retained hidden-rowid patch through a byte-preserving supported path, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- PR #165 remains draft until exact rowid publication/hash verification and full strict/thaw + LAB-080→086 real-ledger + compileall/security audit pass.
- PR #173 remains draft. Latest exact pytest regressions, timeout/UNKNOWN, process concurrency/crash, receipt-affinity and receipt-collation final-surface gates remain pending exact branch execution.
- Do not represent local focused mechanism reproductions as byte-for-byte branch execution.
- Do not add speculative SQLite guards without a reproduced reachable supported compatibility/security failure.

## Exact next action

1. LAB-086 first: if a supported byte-preserving composition/transfer bridge appears, re-fetch predecessor `d4a6a40f...`, apply only retained hidden-rowid patch, require exact target `b78e7c98...`, publish through normal Contents API, re-fetch/hash-verify, then run rowid + receipt-NULL + alternate-UNIQUE + complete strict/thaw + compileall + LAB-080→086 real-ledger gates.
2. If LAB-086 remains tool-limited, execute the exact PR #173 branch gate on head `2297ad975b6e4ea03a90efa531a477119fdc301e` when executable transport is available, starting with `test_adoption_restrictive_unique_regression.py`, then the identity/collation/constructor regressions, timeout/UNKNOWN, process concurrency/crash, receipt-affinity and receipt-collation gates through `SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger`.
3. If exact execution remains unavailable, continue the LAB-091 first-adoption compatibility audit for accepted legacy schema features that can still reject or reinterpret a normal supported write; patch only after reproducing a reachable failure.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS fallback; draft PR #173; restrictive-UNIQUE hardening published, exact branch/full behavioral gates pending.
