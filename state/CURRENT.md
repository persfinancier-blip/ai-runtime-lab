# Current Lab State

Last updated: 2026-09-02

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`; observed head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Authoritative pending LAB-086 lineage: predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 draft PR #175 head `d9a381dd4607a928cd1315adef6431e239995bc1`; constructor audit requires runtime-head verification before schema mutation and complete activation-history verification before recovery side effects; fresh-rotation audit also requires failed prepare/validation not to strand a provider-side reservation.
- LAB-092 / #176 draft PR #177 head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`.
- LAB-093 / #178 READY: outer + nested attested/provider/verifier/keyring capability rebinding; executable RED/GREEN pending.
- LAB-094 / #179 READY: immutable provider-history bootstrap trust root; executable RED/GREEN pending.
- LAB-095 / #180 READY: construction-bound authenticated logical database/history identity; executable RED/GREEN pending.
- LAB-096 / #181 READY: provider-history strategy/capability rebinding; executable RED/GREEN pending.
- LAB-097 / #182 READY: provider-history deletion/rebootstrap plus orphan-transition acceptance; executable repository RED/GREEN pending.
- LAB-098 / #183 READY: deleted provider activation records can bypass recovery/history completeness checks; executable repository RED/GREEN pending.
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues and active PRs. LAB-086 remains blocked specifically on a supported byte-preserving machine composition path for `d4a6a40f... + 61841b58... -> b78e7c98...`; no LAB-086 source mutation or behavioral PASS was claimed.

Fallback source audit of PR #175 found a distinct missing-evidence failure: `_recover_pending_activation()` returns when the current durable generation has no activation row, while `_verify_activation_records()` validates only rows that still exist. It never proves that each LAB-090-governed provider-generation transition has exactly one activation record. Deleting a current `SQL_COMMITTED` row can therefore erase the durable ticket, remove the SQL trigger predicate that blocks new intents, and leave an externally PREPARED/COMMITTED_FENCED provider with no coordinator record to reconcile. An isolated file-backed SQLite probe reproduced the exact query omission shape: durable head remained g2, current-generation activation lookup returned `None`, and the verification SELECT returned an empty rowset after deleting only the activation row.

Created LAB-098/#183 and durable research evidence.

## Evidence produced

- `research/2026-09-02-lab098-deleted-activation-row-bypasses-recovery.md` — commit `f46e3759a5e3ad41846036d74625cb57f481a1ca`; issue #183.
- `research/2026-09-02-lab090-malformed-prepare-ticket-reservation-cleanup.md` — commit `2af77704a2f564cfd7b2cdd91fec68f50280f7ee`; #169 comment `5507313237`.
- `research/2026-09-02-lab097-orphan-transition-survives-rebootstrap.md` — commit `6cfe5407800ac14817956cb022b3297f53690d07`; #182 comment `5506608681`.
- Prior LAB-097 evidence: `research/2026-09-02-lab097-provider-history-empty-state-rebootstrap.md` — commit `8a765553fa0219d240868a0e18fef20626c1fd8f`.
- Retained prior evidence: LAB-090 ordering notes `91f133b9...`, `3ca0f755...`; LAB-086 bridge note `078b95c8...`; LAB-093 notes `fe484bae...`, `2892b115...`, `5e81524d...`; LAB-094 `90735fdb...`; LAB-095 `cdb3bd98...`, `4ea3a667...`, `f74f1422...`; LAB-096 `ab541a60...`.

## Known failures / blockers

- LAB-086 remains first priority. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Connector reads expose exact predecessor/patch bytes, but this run still lacks a supported machine transformation bridge that consumes those exact connector payloads, applies only the retained patch, verifies Git blob `b78e7c98...`, and supplies the complete result to the normal Contents API.
- Publish LAB-086 only from `d4a6a40f... + 61841b58...`, require target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- Exact checkout/source execution remains unavailable in this run; no fresh repository behavioral PASS is claimed.
- Keep PRs #175/#177 draft until exact focused/integration/downstream gates execute.
- LAB-090 constructor: reject runtime-head mismatch before activation-schema mutation; verify complete activation history before any recovery mutation.
- LAB-090 fresh activation: prepare must not strand a newly-created provider reservation when ticket/status validation fails before SQL; cleanup must never abort unrelated prior activation state.
- LAB-098: activation-record completeness must be derived from authenticated provider-generation transition history; missing current/historical records must fail closed before provider/SQLite mutation and must never be reconstructed from current runtime state.
- Do not stage LAB-093/094/095/096/097/098 production code before their pre-fix REDs execute or an equivalently strong auditable execution path exists.
- LAB-093: an outer read-only property returning raw mutable `AttestedCatchup` is insufficient; nested provider/verifier/expected/keyring aliases must not leak.
- LAB-095: path-only, `Path.resolve()`, inode/device identity, or a self-asserted database UUID alone are insufficient; newly opened target must prove authenticated logical history rooted at construction-bound authority.
- LAB-097: distinguish genuine first bootstrap from prior-history loss before any bootstrap/history/head write. `COUNT(*) == 0` is insufficient. Verification must also reject orphan transition/history evidence outside the authenticated contiguous chain; surviving transition rows are proof the DB is not a fresh bootstrap target.

## Exact next action

LAB-086 first: probe for a supported byte-preserving machine composition operation for predecessor blob `d4a6a40f...` + retained patch `61841b58...`. If available, compose only that patch, require candidate Git blob `b78e7c98...`, conflict-check PR #165 still contains the predecessor, publish through normal Contents API, re-fetch/hash-verify, then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080->086 real-ledger gate, unsafe legacy-promotion seed, compileall and final security/reconciliation audit.

If exact source execution becomes available first, run LAB-090 pre-fix REDs before PR #175 production changes: (1) runtime-head mismatch must fail before schema installation; (2) invalid historical activation must fail before recovery side effects; (3) failed/malformed prepare-ticket validation must not strand a provider reservation or alter durable generation head. Also run LAB-098 REDs: delete the current activation record while provider remains PREPARED and COMMITTED_FENCED, plus delete a historical COMMITTED activation row; all must fail closed before mutation. Then run PR #175/#177 full gates. Next run LAB-093/094/095/096/097 REDs. LAB-097 RED set must include complete history deletion and orphan-transition survival cases.

If neither becomes available, continue audit only for concrete distinct trust/capability/fail-closed violations not subsumed by existing issues.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact behavioral/full gate pending; three recorded pre-fix regression classes include prepare-reservation cleanup.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact regression/full gate pending.
- #178 / LAB-093 — READY; executable RED/GREEN + implementation pending.
- #179 / LAB-094 — READY; executable RED/GREEN + implementation pending.
- #180 / LAB-095 — READY; executable RED/GREEN + implementation pending.
- #181 / LAB-096 — READY; executable RED/GREEN + implementation pending.
- #182 / LAB-097 — READY; complete-deletion and orphan-transition rebootstrap RED/GREEN + authenticated initialization provenance design pending.
- #183 / LAB-098 — READY; activation-record deletion/completeness RED/GREEN + authenticated transition-to-activation completeness design pending.
