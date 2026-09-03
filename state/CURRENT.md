# Current Lab State

Last updated: 2026-09-03

## Active objective
LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`; observed head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Authoritative pending lineage: predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required composed target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 draft PR #175 remains IN_PROGRESS; LAB-092 / #176 draft PR #177 remains IN_PROGRESS; LAB-088 / #167 draft PR #172 and LAB-091 / #170 draft PR #173 remain IN_PROGRESS.
- LAB-093/#178 through LAB-100/#185 remain READY follow-ups as previously recorded.

## Last completed step
Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues and active PRs. LAB-086 was probed first. Direct `git ls-remote` again failed before repository access with `Could not resolve host: github.com`. The GitHub connector returned both authoritative blobs (`d4a6a40f...` predecessor and `61841b58...` retained patch) in full, but there is still no supported byte-preserving connector-to-file/patch-engine composition path, so security-critical `strict_fence.py` was not model-reserialized or mutated and no fresh LAB-086 behavioral PASS is claimed.

Fallback source audit returned to exact PR #175 and found a distinct SQL-exception reconciliation defect. After authentic `prepare_activation()` succeeds, a SQLite failure causes `rotate_provider()` to re-query `provider_generation_activations` by only `activation_id`; any same-id row with status `SQL_COMMITTED` or `COMMITTED` sets `sql_committed=True`, even if its target generation/provider/position/fence fields do not match the provider ticket. The original SQL exception is then swallowed and `_commit_or_reconcile_activation(provider, ticket)` can commit the external provider fence before `_mark_activation_committed(ticket)` later detects that SQLite never durably recorded this exact activation. Exception recovery must infer own commit only from an exact durable ticket/target match; same-id evidence alone is insufficient.

## Evidence produced
- `research/2026-09-03-lab090-activation-id-collision-misclassified-as-own-sql-commit.md` — main commit `e30bf413755555d81408e2f2f9dca050f77a4ae9`; #169 comment `5520287826`.
- `research/2026-09-03-lab090-post-prepare-status-probe-reservation-leak.md` — main commit `9674243bb4e75f55f51ddd2dfa74aa8fecdb0fe7`; #169 comment `5519804399`.
- `research/2026-09-03-lab090-activation-status-ignores-provider-unavailability.md` — main commit `b088b506fb34f04e5adc597747e9c78eaa29fc67`; #169 comment `5519350023`.
- `research/2026-09-03-lab090-abort-ignores-provider-unavailability.md` — commit `758d50d932b06b021427c10dcd2120bd5903e225`; #169 comment `5518855627`.
- `research/2026-09-03-lab100-rejected-ticket-leaves-provider-reservation.md` — commit `1955d8a6a253820158e713263e66e1ae8af9805f`; #185 comment `5518378276`.
- Retained LAB-086 connector capability evidence: `research/2026-09-03-lab086-full-blob-connector-capability-reprobe.md` — commit `159ad6ed9edab9ab870e8cb9fc244df53bed43b8`; #163 comment `5517818297`.
- Retained recent evidence: LAB-100 reconstructed-provider authority split `a610744c...`; LAB-090 concurrent duplicate release race `91ceccbb...`; COMMITTED-before-release audit `6e1e69b0...`; post-prepare connection leak `4c488991...`; caller-owned activation state `ee7b6ae0...`; inherited provider rotate `25297f0b...`; provider subclass authority `8b1abf6f...`; LAB-086 rowid semantics probe `04bdef2f...`; LAB-098 `6ac5525c...`; LAB-099 `3b6e311b...`.

## Known failures / blockers
- LAB-086 remains first priority. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Exact predecessor and patch bytes are connector-readable, but this run still lacks a supported machine transform/handoff from connector blob + unified diff -> exact candidate bytes/blob SHA -> normal Contents write. Direct Git transport is transiently unavailable by DNS.
- Exact checkout/source execution remains unavailable; no fresh repository behavioral PASS is claimed.
- Keep PRs #165/#175/#177/#172/#173 draft until their retained exact gates execute.
- LAB-090 outage semantics must be coherent for both mutation and status/reconciliation: unavailable provider must not allow `abort_activation()` to claim cleanup or `activation_status()` to provide live authoritative evidence. A durable/recoverable state machine must preserve unresolved activation evidence until provider reachability returns; simply throwing on abort/status without preserving recovery state is insufficient.
- Every fallible operation after successful `prepare_activation()` must be inside a trusted ownership cleanup/recovery scope. Current code has at least two pre-durability leak sites: the immediate `activation_status(ticket)` probe and the later post-prepare SQLite connection acquisition. Do not fix only one call site.
- SQL exception recovery must not classify a same-`activation_id` row as this rotation's durable commit unless the entire authority-relevant row exactly matches the provider ticket and target generation. Otherwise it can commit an external fence against unrelated/corrupt durable evidence.
- LAB-100 malformed-ticket regression still requires provider-side reservation cleanup/no-stranding after rejection; do not implement that as a blind abort of an untrusted returned ticket.

## Exact next action
LAB-086 first: probe for a supported byte-preserving machine composition operation or connector-to-file handoff for predecessor blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd` + retained patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`. If available, apply only that patch, require candidate Git blob `b78e7c98e35138719f77c482c7f1aab36b702de7`, conflict-check PR #165 still contains the predecessor, publish through normal Contents API, re-fetch/hash-verify, then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080->086 real-ledger gate, unsafe legacy-promotion seed, compileall and final security/reconciliation audit.

If exact source execution becomes available first, run retained LAB-090 REDs before PR #175 production changes. Add exact-provider tests covering one ownership scope from the instant prepare succeeds: (1) genuine PREPARED reservation + failure on the first post-prepare `activation_status(ticket)` probe leaves no untracked reservation post-fix; (2) failure opening the first post-prepare SQLite connection likewise leaves no untracked reservation; (3) PREPARED + provider unavailable + pre-SQL failure must not claim successful abort and must preserve recoverable orphan evidence; (4) durable SQL_COMMITTED + provider unavailable on restart/reconcile must not accept `activation_status()` evidence or mutate durable state; (5) COMMITTED_FENCED and durable COMMITTED/release outage windows remain fail closed and resume idempotently only after provider reachability returns; (6) a conflicting durable row with the same deterministic `activation_id` but non-matching ticket/target fields must not be treated as proof that this rotation's SQL transaction committed and must not trigger provider commit/reconcile. Also include strengthened malformed-ticket and duplicate-release regressions. Cleanup must be ownership-bound/trusted; do not blindly abort an untrusted returned ticket.

If neither becomes available, continue audit only for concrete distinct trust/capability/fail-closed violations not subsumed by existing issues; strengthen existing issues rather than creating duplicates.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact behavioral/full gate pending; outage semantics, post-prepare ownership scope, and exact-row SQL reconciliation regressions expanded.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact regression/full gate pending.
- #178..#185 / LAB-093..LAB-100 — READY regression-first follow-ups; #185 includes rejected-ticket stranded-reservation cleanup coverage.
