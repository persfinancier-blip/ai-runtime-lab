# Current Lab State

Last updated: 2026-09-02

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`; observed head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Authoritative pending LAB-086 lineage remains: live predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 draft PR #175 head `d9a381dd4607a928cd1315adef6431e239995bc1`; constructor audit covers activation-schema mutation before runtime-head verification and recovery side effects before complete activation-history verification.
- LAB-092 / #176 draft PR #177 head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`.
- LAB-093 / #178 READY: raw capability exposure + public `attested` authority-slot rebinding + nested mutable AttestedCatchup/provider/verifier/keyring aliasing source-proved; executable RED/GREEN pending.
- LAB-094 / #179 READY: immutable provider-history bootstrap trust-root lifetime contract; executable RED/GREEN pending.
- LAB-095 / #180 READY: database identity must be construction-bound and authenticated logical-history identity; public path rebinding, unchanged-path filesystem substitution, and self-asserted-UUID insufficiency are source/contract covered.
- LAB-096 / #181 READY: provider-history strategy/capability slot publicly rebindable; executable RED/GREEN pending.
- LAB-097 / #182 READY: provider-history empty-state rebootstrap can normalize complete durable-history deletion into a fresh bootstrap-only history before verification; executable repository RED/GREEN pending.
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues, and active PRs. LAB-086 was probed first. Direct `git clone` again failed before repository execution with `Could not resolve host: github.com`; connector reads still expose the predecessor but no supported machine bridge in this run can consume exact predecessor bytes + retained patch bytes, verify the required Git blob, and write the exact result without model reserialization. No LAB-086 branch mutation or new behavioral PASS was claimed.

Fallback audit found a separate provider-history fail-closed/provenance defect. `DurableProviderHistory.__init__()` runs `_init()` before `verify_durable()`. `_init()` treats an empty `provider_generation_head` as fresh initialization and writes the caller-supplied bootstrap generation/head. A previously initialized g1->g2+ history whose provider-history rows are completely deleted can therefore be rewritten to g1 before verification; the subsequent verifier sees a valid bootstrap-only one-generation history and cannot observe the deleted later generations/receipts.

A file-backed SQLite semantics probe reproduced the critical transition: valid g1->g2 state -> complete history-row deletion -> current empty-head initialization -> reconstructed g1 head/history -> terminal verification conditions all true. This is LAB-097/#182 and is distinct from LAB-092 activation-schema provenance, LAB-094 bootstrap-slot rebinding, LAB-095 database identity, and LAB-096 strategy rebinding. The fix must compose with LAB-095 authenticated logical-history identity rather than add another plain self-asserted marker.

## Evidence produced

- `research/2026-09-02-lab097-provider-history-empty-state-rebootstrap.md` — main commit `8a765553fa0219d240868a0e18fef20626c1fd8f`; issue #182 created.
- `research/2026-09-02-lab090-schema-install-before-runtime-verification.md` — main commit `91f133b95192bdeb0134483ad47b05bb139f39a1`; #169 comment `5505346708`.
- `research/2026-09-02-lab090-recovery-before-history-verification-ordering.md` — main commit `3ca0f75560cd865da9256fb2c92bbb24088dd8d7`; #169 comment `5504756454`.
- `research/2026-09-02-lab086-full-blob-read-bridge-narrowing.md` — main commit `078b95c81250778af5a6adb7626de81cd9971a1e`; #163 comment `5504307268`.
- Prior retained evidence: LAB-093 nested-alias note `fe484bae...`; LAB-095 self-asserted-ID note `cdb3bd98...`; LAB-095 same-path note `4ea3a667...`; LAB-093 `2892b115...`, `5e81524d...`; LAB-094 `90735fdb...`; LAB-095 original `f74f1422...`; LAB-096 `ab541a60...`.

## Known failures / blockers

- LAB-086 remains first priority. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Exact predecessor and retained patch are connector-readable, but this run still lacks a supported machine transformation path that consumes those exact bytes, applies only the retained patch, verifies candidate Git blob `b78e7c98...`, and supplies the complete result to the normal Contents API.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` + retained patch `61841b58...`, require exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- Exact checkout/source execution remains unavailable in this run; no fresh repository behavioral PASS is claimed.
- Keep PRs #175/#177 draft until their exact focused/integration/downstream gates execute.
- LAB-090 constructor preflight must reject runtime-head mismatch before activation-schema creation/commit. Recovery must also not mutate provider/durable activation state before complete activation-history verification; add both regressions before changing production code.
- Do not stage LAB-093/094/095/096/097 production code before their specified pre-fix REDs execute, or an equivalently strong auditable execution path exists.
- LAB-093 must not be considered fixed by an outer read-only property that returns the raw mutable `AttestedCatchup`; nested provider/verifier/expected/keyring aliases must not be recoverable through delegated introspection.
- For LAB-095, do not accept `_path`/read-only property, `Path.resolve()`, inode/device identity, or a self-asserted database UUID alone. The newly opened target must prove authenticated logical history rooted at construction-bound authority; LAB-094/LAB-096/LAB-097 must compose with that root rather than create independent aliases/markers.
- LAB-097 must distinguish genuine first bootstrap from previously initialized history loss before any bootstrap/history/head write; `COUNT(*) == 0` and a plain deletable SQLite marker are insufficient.

## Exact next action

LAB-086 first: probe specifically for a supported machine composition operation that can consume the already-confirmed predecessor blob `d4a6a40f...` and retained patch blob `61841b58...` without model reserialization. If such a bridge appears, compose only that patch, calculate/require candidate Git blob `b78e7c98...`, conflict-check PR #165 still contains predecessor `d4a6a40f...`, publish through the normal Contents API, re-fetch/hash-verify, then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final security/reconciliation audit.

If exact source execution becomes available first, run LAB-090 constructor pre-fix regressions before any PR #175 production change: (1) stale/mismatched runtime on a valid pre-LAB-090 DB must fail before activation-schema mutation; (2) current recoverable activation + separate invalid historical activation row must fail construction with zero provider/durable recovery side effects. Then execute PR #175/#177 full gates. Next run LAB-093/094/095/096/097 pre-fix REDs, including LAB-097 g1->g2 complete-history deletion -> restart with original bootstrap, which must reproduce pre-fix silent rebootstrap before any production fix.

If both remain unavailable, continue audit only for concrete distinct trust/capability/fail-closed violations that are not subsumed by existing issues.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact behavioral/full gate pending; schema-before-runtime-verification and recovery-before-full-history-verification regressions required.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact regression/full gate pending.
- #178 / LAB-093 — READY; outer slot and nested authority-alias regressions + implementation pending.
- #179 / LAB-094 — READY; executable RED/GREEN + implementation pending.
- #180 / LAB-095 — READY; authenticated logical database/history identity contract rejects path-only and self-asserted-ID fixes; executable RED/GREEN + implementation pending.
- #181 / LAB-096 — READY; executable RED/GREEN + implementation pending.
- #182 / LAB-097 — READY; provider-history deletion/rebootstrap RED/GREEN + authenticated initialization provenance design pending.
