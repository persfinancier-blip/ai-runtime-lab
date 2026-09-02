# Current Lab State

Last updated: 2026-09-02

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`; observed head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Authoritative pending LAB-086 lineage remains: live predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 draft PR #175 head `d9a381dd4607a928cd1315adef6431e239995bc1`.
- LAB-092 / #176 draft PR #177 head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`.
- LAB-093 / #178 READY: raw capability exposure + public `attested` authority-slot rebinding + nested mutable AttestedCatchup/provider/verifier/keyring aliasing source-proved; executable RED/GREEN pending.
- LAB-094 / #179 READY: immutable provider-history bootstrap trust-root lifetime contract; executable RED/GREEN pending.
- LAB-095 / #180 READY: database identity must be construction-bound and authenticated logical-history identity; public path rebinding, unchanged-path filesystem substitution, and self-asserted-UUID insufficiency are source/contract covered.
- LAB-096 / #181 READY: provider-history strategy/capability slot publicly rebindable; executable RED/GREEN pending.
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues, and active PRs. LAB-086 was probed first. PR #165 head remains `ee210a47221b6df53f3518aa3af74f76c5b0122b`.

A materially better connector read path was observed: `fetch_blob(d4a6a40f...)` returned the complete 900+ line `strict_fence.py` predecessor through the final function, and `fetch_blob(61841b58...)` returned the complete retained hidden-rowid patch. Therefore the prior broad assumption that connector reads necessarily truncate these blobs is no longer current. The remaining blocker is narrower: there is still no supported machine transformation path that consumes those exact fetched bytes, applies only the retained unified patch, verifies candidate Git blob `b78e7c98...`, and supplies the complete result to the normal Contents API without model/manual reserialization. Direct raw GitHub access from local execution again failed on DNS. `fetch_blob(b78e7c98...)` returned 404, so the known target is not currently reusable as an existing connector-addressable Git blob. No security-critical mutation or behavioral PASS was claimed.

## Evidence produced

- `research/2026-09-02-lab086-full-blob-read-bridge-narrowing.md` — main commit `078b95c81250778af5a6adb7626de81cd9971a1e`; #163 comment `5504307268`.
- Prior retained evidence: LAB-093 nested-alias note `fe484bae...`; LAB-095 self-asserted-ID note `cdb3bd98...`; LAB-095 same-path note `4ea3a667...`; LAB-093 `2892b115...`, `5e81524d...`; LAB-094 `90735fdb...`; LAB-095 original `f74f1422...`; LAB-096 `ab541a60...`.

## Known failures / blockers

- LAB-086 remains first priority. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Exact predecessor and retained patch are now individually retrievable in full via `fetch_blob`; do not waste future runs re-proving generic read truncation unless connector behavior changes.
- Missing capability is a supported byte-preserving predecessor+patch -> complete Contents payload composition bridge with pre-write Git-blob verification.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` + retained patch `61841b58...`, require exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- Exact checkout/source execution remains unavailable in this run; no fresh behavioral PASS is claimed.
- Keep PRs #175/#177 draft until their exact focused/integration/downstream gates execute.
- Do not stage LAB-093/094/095/096 production code before their specified pre-fix REDs execute, or an equivalently strong auditable execution path exists.
- LAB-093 must not be considered fixed by an outer read-only property that returns the raw mutable `AttestedCatchup`; nested provider/verifier/expected/keyring aliases must not be recoverable through delegated introspection.
- For LAB-095, do not accept `_path`/read-only property, `Path.resolve()`, inode/device identity, or a self-asserted database UUID alone. The newly opened target must prove authenticated logical history rooted at construction-bound authority; LAB-094 and LAB-096 must compose so root/verification strategy cannot themselves be rebound.

## Exact next action

LAB-086 first: probe specifically for a supported **machine composition** operation that can consume the already-confirmed complete predecessor blob `d4a6a40f...` and retained patch blob `61841b58...` without model reserialization. If such a bridge appears, compose only that patch, calculate/require candidate Git blob `b78e7c98...`, conflict-check PR #165 still contains predecessor `d4a6a40f...`, publish through the normal Contents API, re-fetch/hash-verify, then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final security/reconciliation audit.

If exact source execution becomes available first, execute PR #175 and #177 full gates, then LAB-093/094/095/096 pre-fix REDs before production changes. LAB-093 RED must include nested A→B provider/verifier/keyring retargeting through any proposed public introspection surface, not only outer `ledger.attested` assignment. LAB-095 must include explicit path rebinding, unchanged-path DB substitution, and same-plain-UUID/invalid-history substitution.

If both remain unavailable, continue retained-authority audit only where it strengthens an existing LAB-093/094/095/096 issue with a concrete distinct trust/capability violation; do not multiply issues for subsumed findings.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact behavioral/full gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact regression/full gate pending.
- #178 / LAB-093 — READY; outer slot and nested authority-alias regressions + implementation pending.
- #179 / LAB-094 — READY; executable RED/GREEN + implementation pending.
- #180 / LAB-095 — READY; authenticated logical database/history identity contract rejects path-only and self-asserted-ID fixes; executable RED/GREEN + implementation pending.
- #181 / LAB-096 — READY; executable RED/GREEN + implementation pending.
