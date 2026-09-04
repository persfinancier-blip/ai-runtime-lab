# Current Lab State

Last updated: 2026-09-04

## Active objective
LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`; observed head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Authoritative pending lineage: predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required composed target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- Draft/IN_PROGRESS stack: LAB-088/#167 PR #172; LAB-090/#169 PR #175; LAB-091/#170 PR #173; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected the live open issue/PR frontier. Fresh direct `git clone --no-checkout` again failed before repository access with `Could not resolve host: github.com`; LAB-086 exact machine composition/source execution remains unavailable. No `strict_fence.py` mutation and no new LAB-086 behavioral PASS are claimed. #163 updated with this observation.

Completed the pre-recorded distinct fallback: froze one canonical byte-level provenance encoding shared by LAB-092 migration certificates, LAB-097 initialization certificates, LAB-099 activation-ticket digests, and LAB-100 activation-authority descriptors/transitions.

V1 uses a tiny standard-library-friendly TLV envelope (`YTIMPRV1` magic; ASCII domain; strictly increasing u16 field ids; explicit type; u32 length; value), SHA-256 over the complete domain-bearing bytes, exact required field sets, and four primitive types: strict UTF-8, raw bytes, U64 and 32-byte digest. U64 requires `type(value) is int`, rejects bool/float/text coercion, and is encoded as eight-byte big-endian. Unknown/extra/missing/reordered fields, trailing bytes, malformed Unicode and digest/nonce length mismatch fail closed. Schema evolution requires a new domain/version.

Frozen domains include LAB-092 migration, LAB-097 initialization, LAB-099 activation ticket, LAB-100 authority descriptor/transition, provider-generation head, and schema-definition records. SQLite is storage, not the canonical type system: security verification must reject REAL/text/BLOB/NULL representation confusion before canonicalization. Repository-owned exact DDL bytes are the canonical source for schema-definition digests; SQLite-rendered SQL text is not.

LAB-099 ticket binding now explicitly includes `new_generation_id` in addition to provider id/generation, expected position, activation id, fence and protocol version. LAB-097 initialization certificate additionally binds the LAB-100 activation-authority descriptor. LAB-092 migration certificate consumes exact authority/head/schema digests under the same encoding. LAB-100 implementation/protocol versions are semantic U64 values in V1, not free-form display strings.

Frozen a 32-case serialization RED matrix covering reference vectors, framing/domain/type errors, bool/float/text numeric confusion, SQLite storage-class confusion, cross-domain replay, DB/head/authority rebinding, old/new descriptor swap, generation replay and one-byte DDL changes.

Durable evidence: `research/2026-09-04-provenance-canonical-byte-encoding-v1.md`, main commit `386f2701f3cb158743e26fe94024b990eec71369`; issue comments #176 `5537738231`, #182 `5537739332`, #184 `5537740539`, #185 `5537741612`, #163 `5537746349`. Verdict: `PROVENANCE_CANONICAL_BYTE_ENCODING_V1_FROZEN`.

An isolated local Python calculation also exercised the frozen framing mechanically (not repository code): sample LAB-099 ticket bytes length 147 produced SHA-256 `f05ee0c7f767a7250a73013945effb2f8ff5bc42e34fd290a90af226343e07b1`; sample LAB-100 authority descriptor bytes length 149 produced SHA-256 `a09d3f3732d0036a5d15e16d0f7269e69c3924731cf4529d746603f97a46330c`. These are provisional design vectors until committed as executable exact-source tests.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Live predecessor/patch/target remain `d4a6a40f...` + `61841b58...` -> `b78e7c98...`; no supported connector-response-to-filesystem/Python machine transform has been observed.
- Normal Contents API requires complete replacement text and is not a predecessor+patch transform.
- Direct Git transport currently fails DNS before repository access; no fresh exact repository behavioral PASS is claimed.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100 must use the frozen sealed/registered construction-bound `ActivationAuthority` and shared V1 canonical descriptor/transition encoding.
- LAB-092 must use the retained authority graph plus shared V1 migration/schema/head encoding; do not patch only `_MIGRATION_PAYLOAD` while keeping caller-controlled `_reservation_surface` authority construction.
- LAB-097..099 must consume the same V1 canonicalization; no self-authenticating row hash or mixed JSON/TLV protocol under the same version.
- LAB-093..100 production implementation waits for exact executable RED/GREEN.

## Exact next action
LAB-086 first: continue probing only for a genuinely supported machine transform/materialization path that can consume exact GitHub predecessor + patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement the canonical encoder tests first and execute frozen LAB-090/LAB-100, LAB-092, LAB-094..096 and LAB-097..099 RED matrices before production refactors.

If neither capability appears: next distinct evidence task is to freeze the exact authenticated chain/link schema between initialization provenance, provider-generation transitions, migration certificates and LAB-100 authority transitions, including epoch monotonicity/replay rules and which parent digest each transition must consume. Do not write production code without executable RED/GREEN.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority model + canonical descriptor/transition encoding frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + canonical V1 serialization; exact RED/full gate pending.
- #178 / LAB-093 — READY; broker façade + endpoint lifecycle frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + 28-case RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated initialization/activation provenance + canonical V1 encoding + 38-case provenance matrix frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade API + canonical V1 descriptors frozen.
