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

Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues/PRs, #163, and PR #165 metadata. LAB-086 was probed first. PR #165 head remains `ee210a47221b6df53f3518aa3af74f76c5b0122b`. Connector base64 fetch of `strict_fence.py` is still truncated at the presentation boundary, while Contents writes require complete replacement text. Direct local clone again failed before repository execution with `Could not resolve host: github.com`; no behavioral execution or security-critical source mutation was claimed.

With LAB-086 exact publication/execution blocked, strengthened LAB-093 rather than creating a new issue. An outer-slot-only fix is insufficient: `AttestedCatchup` itself publicly retains mutable `provider` and `verifier`, while `AttestationVerifier` publicly retains mutable `expected` and `keyring`. Therefore `_attested` plus a read-only `attested` property returning the raw object would still leak nested aliases that can retarget the provider/verifier authority without assigning a new object to the ledger slot. LAB-093 must expose only immutable/value introspection and keep raw provider/verifier/keyring aliases unreachable from a delegated supported ledger.

## Evidence produced

- `research/2026-09-02-lab093-nested-attested-authority-aliasing.md` — main commit `fe484bae42537e01295374fe210beafd36ed0a50`; #178 comment `5503823854`.
- Prior retained evidence: LAB-095 self-asserted-ID note `cdb3bd98...`; LAB-095 same-path note `4ea3a667...`; LAB-093 `2892b115...`, `5e81524d...`; LAB-094 `90735fdb...`; LAB-095 original `f74f1422...`; LAB-096 `ab541a60...`.

## Known failures / blockers

- LAB-086 remains first priority. Do not manually/model-reserialize security-critical `strict_fence.py`.
- This run still lacks a supported byte-preserving predecessor+patch -> complete Contents payload composition bridge; connector source/base64 presentation truncation is not a safe substitute.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` + retained patch `61841b58...`, require exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- Exact checkout/source execution is unavailable in this run; no fresh behavioral PASS is claimed.
- Keep PRs #175/#177 draft until their exact focused/integration/downstream gates execute.
- Do not stage LAB-093/094/095/096 production code before their specified pre-fix REDs execute, or an equivalently strong auditable execution path exists.
- LAB-093 must not be considered fixed by an outer read-only property that returns the raw mutable `AttestedCatchup`; nested provider/verifier/expected/keyring aliases must not be recoverable through delegated introspection.
- For LAB-095, do not accept `_path`/read-only property, `Path.resolve()`, inode/device identity, or a self-asserted database UUID alone. The newly opened target must prove authenticated logical history rooted at construction-bound authority; LAB-094 and LAB-096 must compose so root/verification strategy cannot themselves be rebound.

## Exact next action

LAB-086 first: re-check PR #165 head and probe for a supported byte-preserving transformation/write path that can consume exact `strict_fence.py` predecessor blob `d4a6a40f...` plus retained unified patch `61841b58...`. If available, conflict-check exact predecessor, compose only that patch, require candidate Git blob `b78e7c98...`, publish/re-fetch/hash-verify, then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final security/reconciliation audit.

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
