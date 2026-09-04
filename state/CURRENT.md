# Current Lab State

Last updated: 2026-09-04

## Active objective
LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`; observed head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Authoritative pending lineage: predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required composed target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090/#169 PR #175, LAB-092/#176 PR #177, LAB-088/#167 PR #172, LAB-091/#170 PR #173 remain draft/IN_PROGRESS.
- LAB-093/#178 has frozen V1 façade + endpoint lifecycle contracts; exact RED/GREEN pending.
- LAB-094/#179, LAB-095/#180, LAB-096/#181 now share one frozen construction-bound retained-authority graph contract; exact RED/GREEN pending.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issue/PR frontier. Fresh `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` again failed before repository access with `Could not resolve host: github.com`, so LAB-086 exact machine composition/source execution remains unavailable. No `strict_fence.py` mutation and no new LAB-086 behavioral PASS are claimed.

Performed the next distinct source-evidence task from the retained handoff: reconciled LAB-094/#179, LAB-095/#180 and LAB-096/#181 into one lifetime construction/restart authority graph instead of three independent public-alias patches.

Current source proves that `DurableProviderHistory` retains public mutable `path` and `bootstrap`, `HistoricalSharedAnchorLedger` separately retains public mutable `provider_history`, and the LAB-080 base ledger separately retains its own public mutable `path`. Supported operations then mix these references: locked helpers consume the ledger-opened connection while ordinary `current()/load_receipt()/store_receipt()` reopen the history object's path, and durable verification consumes the history object's bootstrap root. Therefore database identity, bootstrap root and provider-history strategy jointly determine authority and can split after construction.

Frozen decision: one conceptual `RetainedAuthorityGraph(database_identity, bootstrap_root, provider_history_strategy)` is established and fully verified at supported broker construction/restart, then remains invariant for that object lifetime. All internal ledger/history connections use one canonical DB identity; all durable history verification uses one retained bootstrap root; all security-relevant history dispatch uses one retained audited strategy. Public compatibility/introspection views may be value-only but must not feed authority decisions. This is an API/correctness boundary inside the trusted LAB-087 broker domain, not a claim that Python private attributes resist hostile same-process introspection.

The intended composition is: construction-bound private authority graph inside the LAB-087 broker + closed value-only LAB-093 worker endpoint outside it. A 28-case RED-first combined matrix is frozen, including root rebinding, ledger/history path divergence, DB-B matching-head-but-invalid-history, fake and legitimate DB-B strategy replacement, restart/full verification, LAB-097 deletion provenance, LAB-092 provenance, LAB-090 activation compatibility, LAB-080/081 regression compatibility, LAB-087 confinement and LAB-093 delegation.

Durable evidence: `research/2026-09-04-lab094-lab096-construction-bound-retained-authority-graph.md`, main commit `2b516765b119f0f2d90010021874219e9750ab28`; #179 comment `5535166701`; #180 comment `5535167515`; #181 comment `5535168101`. Verdict: `LAB094_LAB096_RETAINED_AUTHORITY_GRAPH_CONTRACT_FROZEN`.

## Known failures / blockers
- LAB-086 remains first priority. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Live predecessor remains blob `d4a6a40f...`; predecessor and retained patch bytes are connector-retrievable, but no supported connector-response-to-filesystem/Python machine materialization bridge has been observed.
- Normal Contents `update_file` requires complete replacement UTF-8 and does not perform predecessor+patch transformation; required target blob `b78e7c98...` is not already present in the Git object database.
- Fresh direct Git clone again failed DNS before repository access. No fresh exact repository behavioral PASS is claimed.
- Keep PRs #165/#175/#177/#172/#173 draft until retained exact gates execute.
- LAB-088 still needs supported-integration + downstream LAB-084/085/086 execution compatibility.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 restricted-worker composition and exact full regression/compile gates.
- LAB-090/LAB-100 should use the retained coherent provider-authority redesign contract; LAB-092 should use the retained domain-separated certificate + authority-schema/trigger + serialization-bound redesign.
- LAB-093 transport architecture is sufficiently frozen; do not elaborate it further without new source/RED evidence.
- LAB-094..096: do not implement three independent underscore/property fixes. Use one construction-bound graph and retain separate issue-level regressions for root, DB identity and strategy replacement. Production implementation waits for exact executable RED/GREEN.

## Exact next action
LAB-086 first: continue probing only for a genuinely supported machine transform/materialization path that can consume exact GitHub predecessor + patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final security/reconciliation audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, then LAB-091 full supported-surface gates, then the frozen LAB-090/LAB-100 and LAB-092 RED matrices. After those, execute the frozen LAB-094..096 28-case RED matrix before writing the coherent retained-authority implementation.

If neither capability appears: next distinct source-evidence task is LAB-097/#182 through LAB-099/#184 reconciliation with the frozen LAB-092/LAB-094..096 construction contract. Determine one authenticated first-initialization/deletion/history-ticket provenance model that prevents provider-history rebootstrap, missing activation-row acceptance and historical ticket rebinding without introducing self-authenticating mutable markers. Freeze the combined RED matrix; do not write production code without executable RED/GREEN.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; unified LAB-090/LAB-100 authority redesign retained; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; consolidated redesign retained; exact regression/full gate pending.
- #178 / LAB-093 — READY; delegation violation proven, LAB-087 broker reuse selected, V1 façade + endpoint lifecycle frozen; exact RED/GREEN pending.
- #179..#181 / LAB-094..096 — READY; unified retained-authority graph contract + 28-case RED matrix frozen; exact RED/GREEN pending.
- #182..#185 / LAB-097..100 — READY regression-first follow-ups.
