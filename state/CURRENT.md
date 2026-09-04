# Current Lab State

Last updated: 2026-09-04

## Active objective
LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`; observed head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Authoritative pending lineage: predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required composed target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090/#169 PR #175, LAB-092/#176 PR #177, LAB-088/#167 PR #172, LAB-091/#170 PR #173 remain draft/IN_PROGRESS.
- LAB-093/#178 has frozen V1 façade + endpoint lifecycle contracts; exact RED/GREEN pending.
- LAB-094/#179, LAB-095/#180, LAB-096/#181 share one frozen construction-bound retained-authority graph contract; exact RED/GREEN pending.
- LAB-097/#182, LAB-098/#183, LAB-099/#184 now share one frozen authenticated initialization + activation provenance contract; exact RED/GREEN pending.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected live open issue/PR frontier. Fresh `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` again failed before repository access with `Could not resolve host: github.com`, so LAB-086 exact machine composition/source execution remains unavailable. No `strict_fence.py` mutation and no new LAB-086 behavioral PASS are claimed.

Performed the next distinct source-evidence task from the retained handoff: reconciled LAB-097/#182, LAB-098/#183 and LAB-099/#184 into one authenticated initialization/deletion/history-ticket provenance model rather than three independent mutable markers.

Source recheck on LAB-090 draft head confirms `_recover_pending_activation()` returns when the current generation has no activation row, `_verify_activation_records()` validates only rows that exist, and historical activation ticket fields are structurally checked without an authenticated transition commitment to the original ticket. Existing LAB-097 evidence also proves empty provider-history state can be re-bootstrap-written before verification.

Frozen decision: an initialized logical DB has a construction-authenticated `InitializationCertificate` bound to the LAB-094..096 retained authority graph and outside the deletable provider-history rowset. Restart verifies it before any provider-history/bootstrap write; empty/missing history in an initialized DB is corruption, never implicit first initialization. Every LAB-090-governed non-bootstrap provider-generation transition additionally authenticates a domain-separated canonical `activation_ticket_digest` over provider/generation/new-generation/expected-position/activation-id/fence/protocol-version. The activation table becomes operational recovery state whose required cardinality and exact ticket contents are derived from authenticated transitions; it is not its own provenance root.

Supported restart ordering is read/verify before mutation: bind retained authority graph -> classify explicit pristine vs initialized without writes -> authenticate initialization/migration provenance -> verify provider-generation chain -> derive required activation tickets -> verify schema + exact activation rows/digests -> verify runtime provider/head -> only then reconcile/release pending activation. Any pre-recovery provenance failure leaves provider and SQLite state unchanged.

A 38-case combined RED-first matrix is frozen covering true pristine initialization, full/partial provider-history deletion, initialization-certificate deletion, logical-DB rebinding, current/historical activation-row deletion, extra/duplicate activation rows, coherent ticket rebinding, numeric-type confusion, LAB-092 schema provenance, LAB-094..096 construction binding, timeout-after-commit/UNKNOWN recovery, LAB-080/081 compatibility and LAB-087/LAB-093 confinement.

Durable evidence: `research/2026-09-04-lab097-lab099-authenticated-initialization-activation-provenance.md`, main commit `45d41f175f2033ad3769d9f2c87b6ade1c3bcce0`; #182 comment `5535592715`; #183 comment `5535593653`; #184 comment `5535594304`. Verdict: `LAB097_LAB099_AUTHENTICATED_PROVENANCE_CONTRACT_FROZEN`.

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
- LAB-097..099: do not add self-authenticating mutable SQLite markers or three independent patches. Use the single initialization certificate + transition-authenticated activation-ticket provenance model and its 38-case matrix. Production implementation waits for exact executable RED/GREEN.

## Exact next action
LAB-086 first: continue probing only for a genuinely supported machine transform/materialization path that can consume exact GitHub predecessor + patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final security/reconciliation audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, then LAB-091 full supported-surface gates, then the frozen LAB-090/LAB-100 and LAB-092 RED matrices. After those, execute the frozen LAB-094..096 28-case RED matrix and LAB-097..099 38-case RED matrix before writing coherent retained-authority/provenance implementations.

If neither capability appears: next distinct source-evidence task is LAB-100/#185 reconciliation with the frozen LAB-090 activation authority and LAB-094..099 construction/provenance contracts. Determine the supported activation-provider extension model (exact audited implementation vs explicit trusted adapter/capability), and freeze how provider-side fencing semantics are independently authenticated/verified without trusting caller-overridable return values. Do not write production code without executable RED/GREEN.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; unified LAB-090/LAB-100 authority redesign retained; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; consolidated redesign retained; exact regression/full gate pending.
- #178 / LAB-093 — READY; delegation violation proven, LAB-087 broker reuse selected, V1 façade + endpoint lifecycle frozen; exact RED/GREEN pending.
- #179..#181 / LAB-094..096 — READY; unified retained-authority graph contract + 28-case RED matrix frozen; exact RED/GREEN pending.
- #182..#184 / LAB-097..099 — READY; unified authenticated initialization/activation provenance contract + 38-case RED matrix frozen; exact RED/GREEN pending.
- #185 / LAB-100 — READY; activation provider implementation/capability authority follow-up; exact RED/GREEN pending.
