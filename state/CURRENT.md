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
- LAB-097/#182, LAB-098/#183, LAB-099/#184 share one frozen authenticated initialization + activation provenance contract; exact RED/GREEN pending.
- LAB-100/#185 has frozen supported activation-authority extension model plus exact construction/restart/upgrade API; exact RED/GREEN pending.

## Last completed step
Re-read `AGENTS.md`, this handoff, and `prompts/SELF_RESUME.md`; inspected the live open issue/PR frontier. Fresh `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` again failed before repository access with `Could not resolve host: github.com`, so LAB-086 exact machine composition/source execution remains unavailable. No `strict_fence.py` mutation and no new LAB-086 behavioral PASS are claimed.

Completed the next pre-recorded distinct evidence task for LAB-090/LAB-100. Fresh PR #175 source inspection confirms `SupportedHistoricalSharedAnchorLedger(path, attested, bootstrap)` currently derives activation authority indirectly from `attested.provider`; startup recovery and rotation accept it using `isinstance(FencedActivationProvider)`. `FencedActivationProvider` accepts caller-owned mutable `ActivationState`, exposes it publicly, is subclassable, and provider-generation identity currently does not retain activation implementation/version metadata.

Frozen V1 decision: `ActivationAuthority` is a first-class construction-bound trust root. A trusted factory constructs it from provider descriptor, registered implementation id/version, protocol version, and broker/provider-owned durable state handle. The LAB-094..096 retained-authority graph records an immutable activation-authority descriptor. Ordinary restart must reconstruct the exact same registered semantics and verify provider identity, monotonic fence state, LAB-097..099 provenance, unresolved activation, and durable ledger/history in fail-closed order before LAB-093 worker delegation opens.

Changing implementation id/version/protocol or incompatible provider authority is an explicit authenticated authority replacement/upgrade transition. Quiescent upgrades must preserve the fence cursor/history exactly; unresolved upgrades must prove exact pending-ticket/fence continuity. Object-reference swaps, arbitrary subclasses/duck typing, caller-owned mutable activation state, registry alias rebinding, dynamic class paths, and self-reported implementation strings are unsupported.

A 15-case RED-first construction/restart extension matrix is frozen covering exact restart, implementation/version/protocol drift, state injection, subclass/duck types, registry rebinding, quiescent and unresolved upgrades, fence rollback, altered pending ticket, missing provider-owned state, mutation-free reconstruction failure, and LAB-093 restricted-worker confinement.

Durable evidence: `research/2026-09-04-lab090-lab100-activation-authority-construction-restart-api.md`, main commit `b2282430ef89d0bfb39feed15992c542b1385ad5`; #185 comment `5536527755`. Verdict: `LAB090_LAB100_ACTIVATION_AUTHORITY_CONSTRUCTION_RESTART_API_FROZEN`.

## Known failures / blockers
- LAB-086 remains first priority. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Live predecessor remains blob `d4a6a40f...`; predecessor and retained patch bytes are connector-retrievable, but no supported connector-response-to-filesystem/Python machine materialization bridge has been observed.
- Normal Contents `update_file` requires complete replacement UTF-8 and does not perform predecessor+patch transformation; required target blob `b78e7c98...` is not already present in the Git object database.
- Fresh direct Git clone again failed DNS before repository access. No fresh exact repository behavioral PASS is claimed.
- Keep PRs #165/#175/#177/#172/#173 draft until retained exact gates execute.
- LAB-088 still needs supported-integration + downstream LAB-084/085/086 execution compatibility.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 restricted-worker composition and exact full regression/compile gates.
- LAB-090/LAB-100 must use the frozen sealed/registered construction-bound `ActivationAuthority`; do not fix with `isinstance`->exact-type alone and do not trust authenticated return strings from arbitrary provider code.
- LAB-092 should use the retained domain-separated certificate + authority-schema/trigger + serialization-bound redesign.
- LAB-093 transport architecture is sufficiently frozen; do not elaborate it further without new source/RED evidence.
- LAB-094..096: do not implement three independent underscore/property fixes. Use one construction-bound graph and retain separate issue-level regressions for root, DB identity and strategy replacement. Production implementation waits for exact executable RED/GREEN.
- LAB-097..099: do not add self-authenticating mutable SQLite markers or three independent patches. Use the single initialization certificate + transition-authenticated activation-ticket provenance model and its 38-case matrix. Production implementation waits for exact executable RED/GREEN.
- LAB-100 production implementation also waits for exact executable RED/GREEN; custom-provider extensibility crosses an explicit trusted adapter/registration boundary rather than inheritance.

## Exact next action
LAB-086 first: continue probing only for a genuinely supported machine transform/materialization path that can consume exact GitHub predecessor + patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final security/reconciliation audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, then LAB-091 full supported-surface gates, then execute the frozen LAB-090/LAB-100 and LAB-092 RED matrices. After those, execute the frozen LAB-094..096 28-case RED matrix and LAB-097..099 38-case RED matrix before writing coherent retained-authority/provenance implementations.

If neither capability appears: next distinct source-evidence task is to reconcile LAB-092 migration provenance with the newly frozen activation-authority construction/restart order: define exactly which authority descriptor/provenance fields a migration certificate commits to, how legacy DBs enter the new authority graph, and what upgrade/migration ordering prevents migration from becoming an authority-rebinding bypass. Keep it minimal and do not write production code without executable RED/GREEN.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; sealed/registered construction-bound activation authority frozen with LAB-100; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; consolidated redesign retained; exact regression/full gate pending.
- #178 / LAB-093 — READY; delegation violation proven, LAB-087 broker reuse selected, V1 façade + endpoint lifecycle frozen; exact RED/GREEN pending.
- #179..#181 / LAB-094..096 — READY; unified retained-authority graph contract + 28-case RED matrix frozen; exact RED/GREEN pending.
- #182..#184 / LAB-097..099 — READY; unified authenticated initialization/activation provenance contract + 38-case RED matrix frozen; exact RED/GREEN pending.
- #185 / LAB-100 — READY; supported sealed/registered activation-authority model + construction/restart/upgrade API + RED matrices frozen; exact RED/GREEN pending.
