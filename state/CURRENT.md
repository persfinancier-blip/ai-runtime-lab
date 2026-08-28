# Current Lab State

Last updated: 2026-08-28

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Exact live `strict_fence.py` blob: `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`.
- Exact retained hidden-rowid candidate: `b78e7c98e35138719f77c482c7f1aab36b702de7` (tested previously, not published).
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; fallback only while LAB-086 exact publication/execution is concretely tool-limited.

## Last completed step

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open PRs and resumed LAB-086 first. The exact branch runtime remains `strict_fence.py` blob `d4a6a40f...`; PR #165 body is stale relative to this handoff and still describes the older `eb219835...` executable snapshot. Hidden-rowid hardening remains unpublished because no supported byte-preserving bridge from the exact connector payload to the execution filesystem/Contents API candidate is available in this run; no manual reserialization of the ~40 KB security-critical file was attempted.

Per fallback policy, advanced LAB-091 and found a second weakened-schema first-adoption gap. The previous fix rejected duplicate identities already present at adoption, but `CREATE TABLE IF NOT EXISTS` also does not restore missing legacy PK/UNIQUE constraints. A clean snapshot with no current duplicates could therefore be admitted and later reintroduce ambiguous identities under otherwise-authorized transitions.

Fixed on branch `lab/091-mutable-shared-anchor-writer`:
- validator commit `19502cb3a81887732c95f07ed17fb9763d38dd87`, blob `c45142317c405748060a8d7d81587b14be89fc81`;
- regression commit `059bfc1bf544f683277f8cf5b00b37a84e3249b5`, blob `e87c550282ac455e4ca5bedeb9de4f6626d563a4`.

First adoption now requires canonical identity constraints for meta singleton, intent ID, intent position, intent request ID, watermark component ID and provider-receipt request ID before row validation/guard installation. A focused exact-target harness accepted the canonical schema and rejected six clean-looking missing-constraint variants: 2 unittest methods PASS including all six subcases. Exact local Git blobs matched the published branch blobs.

Durable note: `research/2026-08-28-lab091-adoption-schema-contract.md`, main commit `5b8d3a24bdad44b47861c516e8647d745d1db12f`. Issue #170 comment `5456160878` and PR #173 comment `5456162044` record the same result.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Alternate-UNIQUE and provider-receipt NULL protections are present in live `d4a6a40f...`.
- Hidden-rowid RED→GREEN evidence retained: exact predecessor `d4a6a40f...` -> candidate `b78e7c98...`; candidate remains unpublished. Rowid collision regression and explicit `rowid=-1` sentinel regression are durable on PR #165.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 one-shot/state-machine/restart/concurrency focused evidence remains retained; WAL adoption-lock mechanism is verified; weakened-schema existing-row identity ambiguity and missing-identity-constraint admission are both now hardened with focused evidence.

## Known blockers / constraints

- LAB-086 remains first priority.
- The current live security delta is rowid-only hardening. Do not reapply alternate-UNIQUE or provider-receipt NULL patches.
- Direct shell/raw GitHub transport remains unavailable in this executor.
- Connector reads are exact but do not mount the complete candidate into the execution filesystem; large responses are truncated. Publication through Contents API is allowed only after exact candidate bytes are materialized and tested; do not hand-rewrite the security-critical runtime.
- PR #165 must remain draft until candidate publication/hash verification, complete strict/thaw gate, LAB-080→086 real-ledger gate, unsafe seed, compileall and final security/reconciliation audit are clean.
- LAB-091 schema-contract hardening is focused target-file evidence only; PR #173 remains draft pending its complete real-stack gate.
- LAB-090/#169 provider handoff freshness remains separate.

## Exact next action

1. LAB-086 first: obtain a supported byte-preserving publication path for exact candidate `b78e7c98e35138719f77c482c7f1aab36b702de7` over predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; do not manually reserialize the file.
2. Require GitHub returned blob == `b78e7c98...`, then re-fetch/hash-verify.
3. Execute unchanged focused regressions: provider-receipt NULL identity, alternate UNIQUE, hidden-rowid collision, and explicit `rowid=-1` sentinel; then full strict/thaw conflict subgate + compileall and repin.
4. Resume complete LAB-080→086 real-ledger gate, unsafe legacy-promotion expected-failure seed, full compileall, security/reconciliation audit and branch/main conflict check.
5. If LAB-086 remains concretely transport-limited, continue LAB-091 complete real-stack integration. Include both weakened-schema regressions in the adoption gate and audit whether any remaining legacy DDL property (NOT NULL/CHECK/type/domain or index semantics) is assumed rather than structurally/semantically revalidated.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid candidate tested but unpublished; publication/execution transport remains blocker.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173; adoption lock + weakened-schema row-cardinality + canonical identity-constraint hardening have focused evidence, full real-stack gate still open.
