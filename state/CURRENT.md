# Current Lab State

Last updated: 2026-09-04

## Active objective
LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`; observed head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Authoritative pending lineage: predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required composed target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 draft PR #175, LAB-092 / #176 draft PR #177, LAB-088 / #167 draft PR #172, and LAB-091 / #170 draft PR #173 remain IN_PROGRESS.
- LAB-093/#178 through LAB-100/#185 remain READY follow-ups.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected current open issues and PRs. Fresh direct repository execution was re-probed with `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git`; it again failed before repository access with `Could not resolve host: github.com`.

LAB-086 machine-handoff was probed one level further: the available Files materialization action accepts only Files `file_id` references and cannot consume a GitHub connector response/blob/base64 payload as machine input. The exact connector-response -> filesystem/Python bridge therefore still does not exist in this runtime. No `strict_fence.py` mutation and no new LAB-086 behavioral PASS are claimed.

Because repeating that blocker would add no value, performed a distinct LAB-093 capability-boundary audit on exact current LAB-090 source. The audit proves a concrete property violation: a narrower component delegated only the ledger can recover the raw external mutation capability through `ledger.attested` (`catch_up_one`, `provider.increment`, and LAB-090 activation surfaces). This is different from the original constructor caller already owning the provider. It therefore violates least-capability delegation if ledger objects are intended to be delegated across trust levels.

The audit also records that renaming `attested` to `_attested` or using a read-only property is not a real security boundary in one Python process. A supported least-capability model needs a façade/proxy whose reachable object graph contains no raw provider/activation mutation handle, preferably composed with LAB-087's broker/process boundary; otherwise the project must explicitly declare all in-process ledger holders fully trusted with the provider.

Durable evidence: `research/2026-09-04-lab093-delegated-ledger-capability-exposure.md`, main commit `994ada0ff1a5ec0c4b2a4dd8efa6f2e33dfca5b3`, #178 comment `5533390673`. Verdict: `LAB093_CONCRETE_DELEGATION_PROPERTY_PROVEN` (source-level only; exact RED/GREEN pending).

## Evidence produced
- `research/2026-09-04-lab093-delegated-ledger-capability-exposure.md` — main commit `994ada0ff1a5ec0c4b2a4dd8efa6f2e33dfca5b3`; #178 comment `5533390673`; concrete delegated least-capability violation proven; façade/process-boundary target defined.
- `research/2026-09-04-lab086-base64-range-fetch-capability.md` — main commit `ea105eb63cdbc8db2054b0c4cf8b6dd8d3e1c522`; #163 comment `5532852452`; exact line-range/base64 retrieval capability observed, but no machine handoff.
- `research/2026-09-04-lab091-fresh-reentrancy-write-surface-audit.md` — main commit `fa4c01c0334f9efc721127e24d6b76ab8a19d9f5`; #170 comment `5532300065`; fresh static reentrancy/write-surface audit PASS only.
- `research/2026-09-03-lab088-fresh-patch-authority-audit.md` — main commit `5bb50ffd122aa47ba83f54f494656906a1282ac3`; #167 comment `5531622222`; fresh authority audit PASS only.
- `research/2026-09-03-lab086-target-blob-object-database-probe.md` — main commit `bb3536ef482500073132abb1a3d05edb19d9972a`; target blob absent from repository object database.
- `research/2026-09-03-lab090-lab100-unified-provider-authority-redesign-contract.md` — main commit `4d303c94f4dcca95176e3e4653ade23b1c8cce0f`; #169 comment `5529408502`.
- `research/2026-09-03-lab092-minimal-safe-redesign-contract.md` — main commit `c215b3ab0ac5bb1c78dcd373077bac8174e3282f`; #176 comment `5528679972`.

## Known failures / blockers
- LAB-086 remains first priority. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Live predecessor remains blob `d4a6a40f...`; predecessor and retained patch bytes are connector-retrievable, but no supported connector-response-to-filesystem/Python materialization bridge exists.
- Files `materialize` cannot consume GitHub connector responses; it accepts only Files `file_id` references.
- Normal Contents `update_file` requires complete replacement UTF-8 and does not perform predecessor+patch transformation.
- Required target blob `b78e7c98...` is not already present in the Git object database.
- Exact checkout/source execution remains unavailable; fresh direct Git clone again failed DNS before repository access. No fresh repository behavioral PASS is claimed.
- Keep PRs #165/#175/#177/#172/#173 draft until their retained exact gates execute.
- LAB-088 fresh static authority audit is complete; supported-integration + downstream LAB-084/085/086 execution compatibility remain.
- LAB-091 fresh static reentrancy/write-surface audit is complete; real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 restricted-worker composition and exact full regression/compile gates remain.
- LAB-090/LAB-100 should use the retained coherent provider-authority redesign contract rather than unrelated lifecycle conditionals.
- LAB-092 should use the retained domain-separated certificate + authority-schema/trigger + serialization-bound redesign rather than more independent `_classify()` checks.
- LAB-093 now has the concrete property required to justify implementation if narrower ledger delegation is a supported trust model. Cosmetic Python privacy is explicitly insufficient.

## Exact next action
LAB-086 first: continue probing only for a genuinely supported machine transform/materialization path that can consume exact GitHub predecessor + patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final security/reconciliation audit.

If exact source execution becomes available first, run LAB-088's existing LAB-083 supported-integration suite plus downstream LAB-084/LAB-085/LAB-086 compatibility gates on exact PR #172 head; then LAB-091 final supported-class real LAB-080/LAB-082 integration + two-worker/crash + timeout-after-commit/UNKNOWN + LAB-087 restricted-worker composition. Then run the frozen 16-case LAB-090/LAB-100 RED matrix before production changes, followed by the retained LAB-092 regression matrix.

If neither exact composition nor exact source execution becomes available, continue only with concrete distinct trust/capability/fail-closed evidence or consolidation that materially strengthens an existing issue. LAB-093's next useful non-execution step is to map the supported delegation surface that must become a façade and identify whether any current cross-process boundary already provides it; do not implement mere `_attested` renaming.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending; bounded base64 source retrieval observed, machine handoff still missing.
- #167 / LAB-088 — IN_PROGRESS; fresh patch authority audit PASS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact behavioral/full gate pending; unified LAB-090/LAB-100 authority redesign contract recorded.
- #170 / LAB-091 — IN_PROGRESS; fresh static reentrancy/write-surface audit PASS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact regression/full gate pending; consolidated redesign contract recorded.
- #178 / LAB-093 — READY; concrete delegated least-capability property now proven; exact RED/GREEN and supported façade/process-boundary decision pending.
- #179..#185 / LAB-094..LAB-100 — READY regression-first follow-ups; LAB-100 composes into unified PR #175 authority redesign contract.
