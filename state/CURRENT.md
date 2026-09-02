# Current Lab State

Last updated: 2026-09-02

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`; observed head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Authoritative pending LAB-086 lineage remains: live predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 draft PR #175 head `d9a381dd4607a928cd1315adef6431e239995bc1`; fresh source audit found restart recovery side effects occur before complete activation-history verification.
- LAB-092 / #176 draft PR #177 head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`.
- LAB-093 / #178 READY: raw capability exposure + public `attested` authority-slot rebinding + nested mutable AttestedCatchup/provider/verifier/keyring aliasing source-proved; executable RED/GREEN pending.
- LAB-094 / #179 READY: immutable provider-history bootstrap trust-root lifetime contract; executable RED/GREEN pending.
- LAB-095 / #180 READY: database identity must be construction-bound and authenticated logical-history identity; public path rebinding, unchanged-path filesystem substitution, and self-asserted-UUID insufficiency are source/contract covered.
- LAB-096 / #181 READY: provider-history strategy/capability slot publicly rebindable; executable RED/GREEN pending.
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues, and active PR #165. LAB-086 was probed first. PR #165 head remains `ee210a47221b6df53f3518aa3af74f76c5b0122b`. Direct local `git clone` again failed before repository execution because `github.com` could not be resolved, so no byte-preserving predecessor+patch composition bridge became available and no security-critical mutation or behavioral PASS was claimed.

Fallback audit of PR #175 found a distinct restart fail-closed ordering defect: `SupportedHistoricalSharedAnchorLedger.__init__()` calls `_recover_pending_activation()` before `_verify_activation_records()`. Recovery is mutating: it may `provider.commit_activation()`, persist `SQL_COMMITTED -> COMMITTED`, and release the external provider activation fence. Complete historical activation verification runs only afterwards. A database that must be rejected because a different historical activation row is malformed/orphaned can therefore already cause durable/external recovery side effects before constructor failure.

The new regression contract requires a recoverable current activation plus a separate invalid historical activation row; restart must fail without changing durable current activation status and without committing/releasing the provider fence. Also cover durable `COMMITTED` + provider `COMMITTED_FENCED`: failed full-history verification must not release the fence. Preferred fix direction is a side-effect-free complete activation-history preflight before recovery mutation, with required re-checks across the external-provider boundary.

## Evidence produced

- `research/2026-09-02-lab090-recovery-before-history-verification-ordering.md` — main commit `3ca0f75560cd865da9256fb2c92bbb24088dd8d7`; #169 comment `5504756454`.
- `research/2026-09-02-lab086-full-blob-read-bridge-narrowing.md` — main commit `078b95c81250778af5a6adb7626de81cd9971a1e`; #163 comment `5504307268`.
- Prior retained evidence: LAB-093 nested-alias note `fe484bae...`; LAB-095 self-asserted-ID note `cdb3bd98...`; LAB-095 same-path note `4ea3a667...`; LAB-093 `2892b115...`, `5e81524d...`; LAB-094 `90735fdb...`; LAB-095 original `f74f1422...`; LAB-096 `ab541a60...`.

## Known failures / blockers

- LAB-086 remains first priority. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Exact predecessor and retained patch are individually retrievable in full via connector reads, but this run still lacks a supported machine transformation path that consumes those exact bytes, applies only the retained patch, verifies candidate Git blob `b78e7c98...`, and supplies the complete result to the normal Contents API.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` + retained patch `61841b58...`, require exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- Exact checkout/source execution remains unavailable in this run; no fresh behavioral PASS is claimed.
- Keep PRs #175/#177 draft until their exact focused/integration/downstream gates execute.
- LAB-090 restart recovery must not mutate provider/durable activation state before complete activation-history verification; add the regression described above before changing production code.
- Do not stage LAB-093/094/095/096 production code before their specified pre-fix REDs execute, or an equivalently strong auditable execution path exists.
- LAB-093 must not be considered fixed by an outer read-only property that returns the raw mutable `AttestedCatchup`; nested provider/verifier/expected/keyring aliases must not be recoverable through delegated introspection.
- For LAB-095, do not accept `_path`/read-only property, `Path.resolve()`, inode/device identity, or a self-asserted database UUID alone. The newly opened target must prove authenticated logical history rooted at construction-bound authority; LAB-094 and LAB-096 must compose so root/verification strategy cannot themselves be rebound.

## Exact next action

LAB-086 first: probe specifically for a supported machine composition operation that can consume the already-confirmed complete predecessor blob `d4a6a40f...` and retained patch blob `61841b58...` without model reserialization. If such a bridge appears, compose only that patch, calculate/require candidate Git blob `b78e7c98...`, conflict-check PR #165 still contains predecessor `d4a6a40f...`, publish through the normal Contents API, re-fetch/hash-verify, then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final security/reconciliation audit.

If exact source execution becomes available first, run LAB-090's new pre-fix restart-ordering regression before any PR #175 production change: current recoverable activation + separate invalid historical activation row must fail construction with zero provider/durable recovery side effects. Then execute the existing PR #175 and #177 full gates, followed by LAB-093/094/095/096 pre-fix REDs before production changes.

If both remain unavailable, continue retained-authority/recovery-ordering audit only where it strengthens an existing issue with a concrete distinct trust/capability/fail-closed violation; do not multiply issues for subsumed findings.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact behavioral/full gate pending; restart recovery-before-full-history-verification regression newly required.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact regression/full gate pending.
- #178 / LAB-093 — READY; outer slot and nested authority-alias regressions + implementation pending.
- #179 / LAB-094 — READY; executable RED/GREEN + implementation pending.
- #180 / LAB-095 — READY; authenticated logical database/history identity contract rejects path-only and self-asserted-ID fixes; executable RED/GREEN + implementation pending.
- #181 / LAB-096 — READY; executable RED/GREEN + implementation pending.
