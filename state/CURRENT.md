# Current Lab State

Last updated: 2026-09-03

## Active objective
LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`; observed head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Authoritative pending lineage: predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required composed target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 draft PR #175, LAB-092 / #176 draft PR #177 (observed head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`), LAB-088 / #167 draft PR #172, and LAB-091 / #170 draft PR #173 remain IN_PROGRESS.
- LAB-093/#178 through LAB-100/#185 remain READY follow-ups.

## Last completed step
Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, and fresh open issue/PR state. Re-probed LAB-086 direct repository execution: `git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD` failed before repository execution with `Could not resolve host: github.com`. The GitHub connector still exposes normal file reads/writes but no byte-preserving machine handoff that can safely compose the complete security-critical predecessor plus retained patch without model/manual reserialization. No LAB-086 branch mutation and no fresh behavioral PASS were claimed.

Because LAB-086 remains concretely tool-limited, inspected current PR #175 exact source (`activation.py`, `integration.py`, `supported.py`) and consolidated the retained LAB-090/LAB-100 defects into one regression-first provider-authority redesign contract. The contract treats split activation state, provider identity/key, anchor position/CAS, request-idempotency state, fencing-token allocation and synchronization as one root cause rather than independent local bugs. It requires one construction-bound coherent provider authority (or independently verifiable trusted remote adapter capability), immediate trusted recovery ownership after successful prepare, unified outage semantics, full exact-ticket durable binding, monotonic fence allocation across reconstruction, and removal/serialization of generic identity/key rotation while activation is non-quiescent. A 16-case exact-source RED matrix is frozen before any production rewrite.

## Evidence produced
- `research/2026-09-03-lab090-lab100-unified-provider-authority-redesign-contract.md` — main commit `4d303c94f4dcca95176e3e4653ade23b1c8cce0f`; #169 comment `5529408502`.
- `research/2026-09-03-lab092-minimal-safe-redesign-contract.md` — main commit `c215b3ab0ac5bb1c78dcd373077bac8174e3282f`; #176 comment `5528679972`.
- `research/2026-09-03-lab092-extra-trigger-authority-not-authenticated.md` — main commit `c06e8511acb262275b4e90a581454f50c4697b59`; #176 comment `5527945001`.
- `research/2026-09-03-lab092-explicit-migration-trusts-unverified-shared-ledger-tail.md` — main commit `15af8e1cfb8e15f712318ec890fd8e20e49f2adf`; #176 comment `5527186826`.
- `research/2026-09-03-lab092-preseedable-migration-marker-confused-deputy.md` — main commit `4a64f764bdf4859a9d1d9cfac440d36ebc43b329`; #176 comment `5526435082`.
- `research/2026-09-03-lab092-provenance-carrier-schema-not-authenticated.md` — main commit `71829f371ee250d0dc16d83e007f7a79e3d82cfb`; #176 comment `5525609997`.
- Retained LAB-092 evidence also includes explicit-migration, constructor/restart, and post-construction TOCTOU findings.
- Retained LAB-100 evidence: provider subclass authority, inherited rotate bypass, caller-owned activation state, reconstructed provider position/request-result split, rejected-ticket orphan reservation, and reconstructed fence-counter reuse.
- Retained LAB-086 machine-handoff evidence: `research/2026-09-03-lab086-container-download-handoff-probe.md` commit `3cc6187748211c8800a6a39d387aa5043f59b96d`; full-blob connector reprobe commit `159ad6ed9edab9ab870e8cb9fc244df53bed43b8`.
- Retained LAB-090 evidence includes post-prepare status/connection leaks, unavailable abort/status semantics, activation-id collision recovery, duplicate-release race, and pre-SQL external-commit orphan fence.

## Known failures / blockers
- LAB-086 remains first priority. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Exact predecessor and patch bytes are connector-readable, but no supported machine transform/handoff currently composes connector blob + unified diff into exact candidate bytes/blob SHA for a normal Contents write; direct filesystem network access again failed DNS in this run.
- Exact checkout/source execution remains unavailable; no fresh repository behavioral PASS is claimed.
- Keep PRs #165/#175/#177/#172/#173 draft until their retained exact gates execute.
- LAB-090/LAB-100 should no longer be patched as unrelated lifecycle conditionals. The retained unified contract requires one coherent construction-bound authority over identity/key/position/request-results/activation/fence allocation/synchronization, or one independently verifiable remote adapter capability. Successful prepare must immediately establish trusted recovery ownership; provider outage must not synthesize lifecycle evidence; exact SQL recovery evidence must match every authority-relevant ticket field; generic rotate must not bypass non-quiescent activation state.
- LAB-092 should no longer be patched as independent `_classify()`/marker checks. The retained redesign contract requires a non-preseedable domain-separated installation certificate, canonical authority-schema + complete relevant trigger manifest, inherited durable-state authentication, serialization-bound authorization, and a recoverable external-confirmation state machine.
- LAB-100 provider authority must bind identity/key/position/request-results/activation state/synchronization and the monotonic fence allocator epoch into one coherent durable authority.

## Exact next action
LAB-086 first: probe for a supported byte-preserving machine composition/materialization path for predecessor blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd` + retained patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`. If available, apply only that patch, require candidate Git blob `b78e7c98e35138719f77c482c7f1aab36b702de7`, conflict-check PR #165 still contains the predecessor, publish through normal Contents API, re-fetch/hash-verify, then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080->086 real-ledger gate, unsafe legacy-promotion seed, compileall and final security/reconciliation audit.

If exact source execution becomes available first, run the 16-case LAB-090/LAB-100 RED matrix from `research/2026-09-03-lab090-lab100-unified-provider-authority-redesign-contract.md` against PR #175 before changing production code. Require preservation assertions for provider position, fence state, generation head, durable acknowledgement and trusted recovery handle. Then implement one coherent provider-authority boundary and run existing LAB-090 focused/restart/concurrency plus LAB-080/081/092/098/099 downstream gates. After that execute the LAB-092 regression matrix from `research/2026-09-03-lab092-minimal-safe-redesign-contract.md` before production changes there.

If neither exact composition nor exact source execution becomes available, continue only with concrete distinct trust/capability/fail-closed evidence or consolidation that materially strengthens an existing issue; do not create duplicate narrow findings.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact behavioral/full gate pending; unified LAB-090/LAB-100 authority redesign contract now recorded.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact regression/full gate pending; consolidated redesign contract recorded.
- #178..#185 / LAB-093..LAB-100 — READY regression-first follow-ups; LAB-100 now composes into the unified PR #175 authority redesign contract.
