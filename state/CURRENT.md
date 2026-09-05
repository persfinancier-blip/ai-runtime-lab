# Current Lab State

Last updated: 2026-09-06

## Active objective
LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; live head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Authoritative pending lineage: predecessor blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required composed target blob `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- Draft/IN_PROGRESS stack remains open: LAB-088/#167 PR #172; LAB-090/#169 PR #175; LAB-091/#170 PR #173; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected current open issues and live PR #165. LAB-086 remains first priority and is not superseded.

Probed LAB-086 first with a real `git clone --no-checkout`. Git transport again failed before repository access with `Could not resolve host: github.com` (exit 128). The GitHub connector is readable/writable, but no supported machine bridge was observed that can consume exact connector-returned predecessor bytes plus retained patch bytes and mechanically emit the byte-verified composed target without model reserialization. Security-critical `strict_fence.py` therefore remains untouched; no new LAB-086 behavioral PASS is claimed.

Completed the recorded distinct fallback: froze `EVIDENCE_MINIMIZATION_POLICY_COMPILER_FIELD_TAINT_SELECTIVE_DISCLOSURE_V1_FROZEN` in `research/2026-09-06-evidence-minimization-policy-compiler-field-taint-selective-disclosure-v1.md`, main commit `cdff102e7ab1cf387963dd6a2408456e9281a186`; #178 comment `5555470609` records the result.

Key decisions:
- evidence minimization is a compiled closed-schema boundary, not final-string/regex redaction;
- every canonical field path binds sensitivity, evidence purpose, sink classes, durable representation, retention and disclosure policy; unknown fields are rejected;
- arbitrary `metadata` / `extra` / SDK extension bags / exception dictionaries may not be durably serialized wholesale;
- taint propagates through nested objects, serialization, formatting, URL/query/header construction, exceptions, encoding/compression and derived observability; `UNKNOWN_UNCLASSIFIED` is contagious and fail-closed;
- sink policies are separate for authority DB, recovery journal, replay/manual capsules, logs, traces, metrics, search/index, archive and selective-disclosure export;
- pre-I/O durability accepts only a validated closed projection bound to the current policy generation, never arbitrary dict/SDK/exception objects;
- provider adapter generations must map request/default/auth/error/metadata model fields into LAB canonical paths and revalidate on SDK drift;
- commitment representation is selected by policy; callers cannot downgrade sensitive/low-entropy fields to plain hashes;
- selective-disclosure exports are deterministic, bind source evidence + policy/commitment generation + exact disclosed paths, and cannot omit authority-critical validity fields required by the verifier;
- policy generations are authenticated/monotonic/directional; plaintext-expanding changes require explicit admission and field-reducing upgrades do not retroactively prove old copies erased;
- first implementation slice should make dangerous interfaces structurally unavailable with closed typed DTOs, provider extractors, sink-specific serializers and closed exception projections before broad dynamic/static taint tooling.

An 80-case RED-first matrix is frozen across schema/compiler validation, nested taint propagation, exceptions, logs/traces/metrics, provider/SDK drift, commitment selection, selective disclosure and policy-generation/derived-store behavior. No production compiler, taint engine, provider-model classification, selective-disclosure implementation or behavioral PASS is claimed. Primary mechanism donors: Smithy `sensitive`, OpenTelemetry sensitive-data/allowlist guidance, Cedar schema validation, OPA signed/versioned bundles, CodeQL source-to-sink taint analysis and RFC 9901 selective-disclosure validity rules.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Exact predecessor and retained patch bytes are observable through the connector, but no supported byte-preserving transform/materialization bridge to a Contents API replacement has been observed.
- Direct git transport in this run failed before repository access with DNS resolution failure.
- Normal Contents API requires complete replacement text and is not a predecessor+patch transform.
- Authoritative lineage remains `d4a6a40f...` + `61841b58...` -> `b78e7c98...`.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 must use the frozen shared canonical V1 encoding, parent-linked chain, atomic append/recovery protocol, durable SQL storage, verifier/planner, external evidence continuity, recovery executor and finite broker startup machine; no independent locally-valid provenance islands.
- LAB-093 must implement the frozen least-capability façade and retained session/request/effect/idempotency/retention/archive/DR/escrow/reroot/provider-capability/UNKNOWN/manual-resolution/evidence/challenge/quarantine/authority/retry/replay/transport-observer/capacity-compaction/archive/privacy-minimization/policy-compiler contracts; production implementation waits for executable RED/GREEN.
- LAB-093..100 production implementation waits for exact executable RED/GREEN.
- No production post-reroot cutover, re-admission after trust discontinuity, manual consequential re-attempt, retention/privacy exception or plaintext-expanding evidence-policy upgrade may be activated without required explicit product/security/business/legal authority bound to the exact decision.

## Exact next action
LAB-086 first: probe only for a genuinely supported machine transform/materialization path that can consume the exact connector-returned predecessor blob plus retained patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

If neither capability appears: next distinct evidence task is to freeze a **provider evidence-schema registry / generated closed DTO / SDK drift admission contract**. Define how provider model snapshots, canonical field mappings, exception schemas and sink DTO generators are content-addressed and versioned; how unknown/new SDK fields block consequential admission; how generated serializers prove they cannot traverse arbitrary object graphs; how provider capability/replay/extractor generations bind the exact evidence-schema generation; and a RED-first compatibility matrix for SDK upgrades, generated defaults, nested errors, extension fields and rollback/downgrade.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + global provenance/recovery contracts; exact RED/full gate pending.
- #178 / LAB-093 — READY; privacy-minimization/cryptographic-erasure + evidence policy compiler/taint/selective-disclosure contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade/global provenance/recovery contracts frozen.
