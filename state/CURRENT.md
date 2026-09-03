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
Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues and active PRs. LAB-086 was probed first. The GitHub connector successfully returned both authoritative LAB-086 blobs in full, but the available connector surface still has no file/stream handoff into a local patch engine; manually/model-reserializing the 900+ line security-critical source remains prohibited. A fresh direct `git ls-remote` again failed before repository access with `Could not resolve host: github.com`, so no LAB-086 source mutation or fresh behavioral PASS is claimed.

Fallback source audit returned to PR #175 and found a distinct LAB-090 lifecycle inconsistency. Exact `FencedActivationProvider.abort_activation()` is the only provider-side lifecycle mutation that ignores `self.available`: prepare/commit/release and inherited provider I/O fail when unavailable, but abort directly clears provider-owned `ActivationState.pending`. The coordinator calls abort when SQL rotation fails before durable activation commit, so the current model can claim external reservation cleanup while that same external provider is declared unreachable. This masks the real `prepare succeeded -> SQL never committed -> provider unavailable` recovery problem and is distinct from LAB-100 implementation/capability authority.

## Evidence produced
- `research/2026-09-03-lab090-abort-ignores-provider-unavailability.md` — commit `758d50d932b06b021427c10dcd2120bd5903e225`; #169 comment `5518855627`.
- `research/2026-09-03-lab100-rejected-ticket-leaves-provider-reservation.md` — commit `1955d8a6a253820158e713263e66e1ae8af9805f`; #185 comment `5518378276`.
- Retained LAB-086 connector capability evidence: `research/2026-09-03-lab086-full-blob-connector-capability-reprobe.md` — commit `159ad6ed9edab9ab870e8cb9fc244df53bed43b8`; #163 comment `5517818297`.
- Retained recent evidence: LAB-100 reconstructed-provider authority split `a610744c...`; LAB-090 concurrent duplicate release race `91ceccbb...`; COMMITTED-before-release audit `6e1e69b0...`; post-prepare connection leak `4c488991...`; caller-owned activation state `ee7b6ae0...`; inherited provider rotate `25297f0b...`; provider subclass authority `8b1abf6f...`; LAB-086 rowid semantics probe `04bdef2f...`; LAB-098 `6ac5525c...`; LAB-099 `3b6e311b...`.

## Known failures / blockers
- LAB-086 remains first priority. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Exact predecessor and patch bytes are connector-readable, but this run still lacks a supported machine transform/handoff from connector blob + unified diff -> exact candidate bytes/blob SHA -> normal Contents write. Direct Git transport is transiently unavailable by DNS.
- Exact checkout/source execution remains unavailable; no fresh repository behavioral PASS is claimed.
- Keep PRs #165/#175/#177/#172/#173 draft until their retained exact gates execute.
- LAB-090 cleanup semantics now require a recoverable fail-closed contract for `prepare succeeded + SQL did not commit + provider unavailable`; simply making `abort_activation()` raise `ProviderUnavailable` is insufficient because there would still be no durable coordinator row proving the external reservation can later be reconciled.
- LAB-100 malformed-ticket regression still requires provider-side reservation cleanup/no-stranding after rejection; do not implement that as a blind abort of an untrusted returned ticket.

## Exact next action
LAB-086 first: probe for a supported byte-preserving machine composition operation or connector-to-file handoff for predecessor blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd` + retained patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`. If available, apply only that patch, require candidate Git blob `b78e7c98e35138719f77c482c7f1aab36b702de7`, conflict-check PR #165 still contains the predecessor, publish through normal Contents API, re-fetch/hash-verify, then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080->086 real-ledger gate, unsafe legacy-promotion seed, compileall and final security/reconciliation audit.

If exact source execution becomes available first, run the retained LAB-090 pre-fix RED set before PR #175 production changes. Add the new exact-provider unavailable-abort RED: prepare authentic reservation while available, make provider unavailable before injected SQL failure, prove pre-fix cleanup clears the reservation anyway; post-fix must not claim successful external abort while unreachable and must preserve enough durable/recoverable state to reconcile the orphan reservation before normal writes resume. Also include the strengthened malformed-ticket RED from LAB-100 and the previously retained LAB-090 concurrency/connection-failure regressions.

If neither becomes available, continue audit only for concrete distinct trust/capability/fail-closed violations not subsumed by existing issues; strengthen existing issues rather than creating duplicates.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact behavioral/full gate pending; unavailable-abort recovery contract added.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact regression/full gate pending.
- #178..#185 / LAB-093..LAB-100 — READY regression-first follow-ups; #185 includes rejected-ticket stranded-reservation cleanup coverage.
