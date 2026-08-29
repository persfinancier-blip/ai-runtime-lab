# Current Lab State

Last updated: 2026-08-29

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Live LAB-086 `strict_fence.py` blob remains `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`.
- Exact unpublished hidden-rowid candidate remains `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; fallback only while LAB-086 exact publication/execution is concretely tool-limited.

## Last completed step

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues/PRs. LAB-086 branch conflict-check reconfirmed `strict_fence.py` is still exact predecessor blob `d4a6a40f...`. Current shell `git ls-remote` still fails before transfer with `Could not resolve host: github.com`; the GitHub Contents writer still requires the full UTF-8 replacement body and offers no mounted-file/file-reference bridge, so exact candidate `b78e7c98...` was not manually reserialized or published.

Used the permitted LAB-091 fallback. Static audit of the final v2/v3/v4 trigger stack found a first-adoption field-domain gap: identity PK/UNIQUE and existing rows were validated, but `CREATE TABLE IF NOT EXISTS` cannot repair missing canonical `NOT NULL` declarations. Concrete case: a legacy `shared_anchor_intents.component_id TEXT` (instead of canonical `TEXT NOT NULL`) can admit a PREPARED row with `component_id=NULL` when a one-shot permit is crafted over the exact NULL-bearing row token and the deterministic request ID is computed over JSON `null`.

Executed a local SQLite reproduction using the exact relevant published semantics: one-shot permit consumption, v2 exact intent insert guard, v3 current-tail/current-provider guard, and v4 deterministic request-id guard. The NULL-component PREPARED insert succeeded, proving a future-state gap rather than a cosmetic schema difference.

Published the minimal fail-closed fix on `lab/091-mutable-shared-anchor-writer`:
- `adoption_schema_domains.py` commit `620fda8a0c022d1d0074fbd4cc1b4f7fa3f61664`, blob `1abef5360fc57f5a863e8665556cbdb9dee6f012`;
- regression commit `ff3134924ebd020fa19713bf90d5eecf42a756a6`, blob `4b00c0953f1c8095b7432aa78a1c2cb8041d0350`;
- final supported-class wiring commit `5b720fba666d8e412d04ae77ad7e7dc640a93637`, `history_bound_operation_scoped.py` blob `69c6b1070b1f65bb7c00b31a5c3cfce1c5d4a51f`.

Focused regression executed before publication: canonical NOT NULL contract accepted; clean DB missing only `component_id NOT NULL` rejected; 2/2 PASS. Post-publication re-fetch matched the exact locally executed helper/test blobs. Durable note: `research/2026-08-29-lab091-not-null-adoption-schema-gap.md`, main commit `d5d73c09b0f5886350c70bc24a06b4bc6a2f4857`. Issue #170 comment `5459464015`; PR #173 comment `5459464521`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Alternate-UNIQUE and provider-receipt NULL protections are present in live LAB-086 predecessor `d4a6a40f...`.
- LAB-086 hidden-rowid RED->GREEN evidence retained; exact predecessor `d4a6a40f...` -> candidate `b78e7c98...` was byte-rederived and focused mechanism-tested.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 exact published expression/partial/missing-constraint adoption-index suites: prior 4/4 PASS + compileall; non-BINARY collation focused gate PASS.
- LAB-091 weakened NOT NULL schema-domain regression: 2/2 PASS on exact published helper/test blobs; NULL-component pre-fix mechanism reproduced.

## Known blockers / constraints

- LAB-086 remains first priority. Current live security delta is rowid-only hardening; do not reapply alternate-UNIQUE or provider-receipt NULL patches.
- LAB-086 read-side reconstruction is solved; publication remains blocked by data-plane separation. Do not use low-level blob/tree/ref manipulation, force updates, or manual lossy rewrites.
- PR #165 mergeability remains unresolved/stale unless branch/main changes; previous direct API reported `mergeable_state=unknown`.
- PR #165 remains draft until exact candidate publication/hash verification, four focused regressions, complete strict/thaw subgate, LAB-080->086 real-ledger gate, unsafe seed, compileall and final security/reconciliation audit are clean.
- PR #173 remains draft. Existing timeout-after-commit and process concurrency/crash tests still use stubs and do not prove the final supported class against exact real LAB-080/LAB-082 dependencies.
- The new NOT NULL validation is intentionally a first slice: it checks canonical non-identity NOT NULL fields for the shared-anchor mutable tables. CHECK/type-affinity equivalence has not yet been claimed.
- LAB-090/#169 provider handoff freshness remains separate.

## Exact next action

1. LAB-086 first: conflict-check branch `strict_fence.py` remains `d4a6a40f...`. If a supported byte-preserving Contents path appears, publish only exact candidate `b78e7c98...`, require returned/re-fetched blob equality, then run the four focused regressions + strict/thaw subgate + compileall + LAB-080->086 real-ledger gate.
2. If LAB-086 publication remains concretely tool-limited, LAB-091: re-run the prior adoption identity/index/collation suites together with the new NOT NULL-domain regression against branch head after `5b720fba...`.
3. Then replace the stub-only proof gap with a real-stack regression around `SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger`: timeout-after-commit/UNKNOWN retry convergence first, then two-worker confirmation/crash semantics, using exact real LAB-080/LAB-082 dependencies.
4. Audit remaining first-adoption schema equivalence only where it can affect future reachable state (especially CHECK/type-affinity semantics); do not require textual schema identity without a demonstrated behavioral gap.
5. Keep PRs #165/#173 draft until their complete gates are clean.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact rowid candidate re-derived + focused mechanism PASS, publication/full gate pending.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173; identity/index/collation plus new NOT NULL first-adoption hardening published; combined regression re-run and full supported real-stack gate pending.
