# Current Lab State

Last updated: 2026-09-05

## Active objective
LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; live PR head remains `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Authoritative pending lineage: predecessor blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required composed target blob `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- Draft/IN_PROGRESS stack remains open: LAB-088/#167 PR #172; LAB-090/#169 PR #175; LAB-091/#170 PR #173; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and all active PRs. GitHub connector is healthy; PRs #165/#172/#173/#175/#177 remain open/draft.

Re-probed the preferred direct byte-exact LAB-086 path with a real `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git`; it again failed before repository access with `Could not resolve host: github.com` (exit 128). The connector still exposes repository state but this runtime has no supported operation that mechanically consumes the exact predecessor blob plus retained unified patch and emits a byte-verified complete replacement payload for the Contents API. Manual/model reserialization of security-critical `strict_fence.py` remains prohibited. No LAB-086 branch mutation or new behavioral PASS is claimed.

Completed the recorded distinct fallback: froze `PROVIDER_WIRE_REQUEST_REPLAY_CAPSULE_DETERMINISTIC_ADAPTER_COMPATIBILITY_V1_FROZEN` in `research/2026-09-05-provider-wire-request-replay-capsule-deterministic-adapter-compatibility-v1.md`, main commit `2773b95add5ea423a40873369d30df944dc21e89`; #178 comment `5552778769` records the result.

Key decisions: a historical retry reuses one immutable provider-semantic replay capsule pinned before original `SEND_STARTED`; it does not replay stale HTTP/auth bytes and does not reconstruct history from current SDK defaults. The capsule binds exact provider token, semantic payload/effective defaults, provider/API/version, endpoint/account/region/zone scope, provider-capability generation, adapter/serializer/token-mapping generations and global provenance. Only transport/auth material proven non-semantic (fresh signatures, timestamps, OAuth/session credentials, nonces, tracing/framing) may be refreshed. Every newer adapter needs an authenticated directional replay-compatibility declaration plus deterministic semantic-digest verification before and after final request signing. Credential rotation is allowed only when it preserves the provider idempotency/account/principal scope. If semantic identity cannot be proven, mutation replay is denied and recovery falls to read-only oracle/manual reconciliation. An 80-case RED-first matrix is frozen. No production code or behavioral PASS is claimed.

Primary donors recorded: AWS EC2 client-token same-token/same-parameter idempotency and regional/zonal scope; AWS Signature V4 time-bound request authentication showing transport signatures are not durable business identity; Stripe API/account/window-scoped idempotency; Google long-running operation read-only polling.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Exact predecessor and retained patch bytes are observable through the connector, but no supported byte-preserving transform/materialization bridge to a Contents API replacement has been observed.
- Direct git transport in this run failed before repository access because `github.com` DNS resolution failed.
- Normal Contents API requires complete replacement text and is not a predecessor+patch transform.
- Authoritative lineage remains `d4a6a40f...` + `61841b58...` -> `b78e7c98...`.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 must use the frozen shared canonical V1 encoding, parent-linked chain, atomic append/recovery protocol, durable SQL storage, verifier/planner, external evidence continuity, recovery executor and finite broker startup machine; no independent locally-valid provenance islands.
- LAB-093 must implement the frozen least-capability façade, session/request/effect registry, application-idempotency/result delivery, authenticated retention/archive/DR/escrow/re-root/epoch/provider-capability/UNKNOWN-oracle/manual-resolution/canonical-evidence/challenge/quarantine/authority-manifest/effective-authority-lease/retry-authority/replay-capsule contracts; production implementation waits for executable RED/GREEN.
- LAB-093..100 production implementation waits for exact executable RED/GREEN.
- No production post-reroot cutover, re-admission after trust discontinuity, or manual consequential re-attempt may be activated without required explicit product/security/business authorization bound to the exact payload/effect.

## Exact next action
LAB-086 first: probe only for a genuinely supported machine transform/materialization path that can consume the exact connector-returned predecessor blob plus retained patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement tests first for the frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

If neither capability appears: next distinct evidence task is to freeze a **provider semantic-request extractor / post-signing equivalence attestation + golden conformance fixture contract**. Define a provider/adapter-specific pure function that extracts the authority-relevant semantic request from both the replay capsule and the final transport-authenticated wire request; require domain-separated digest equality immediately before I/O; define treatment of query/header/body fields, canonical endpoint identity, content encodings, SDK-generated defaults, streaming/chunked requests, presigned URLs, multipart uploads, compression, protobuf unknown fields, and auth middleware. Define signed golden fixtures for each admitted adapter generation so compatibility declarations are executable evidence rather than prose, including negative fixtures that prove semantic mutations are detected. Keep this read-only/offline until executable RED/GREEN exists.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + global provenance/recovery contracts; exact RED/full gate pending.
- #178 / LAB-093 — READY; façade/session/request/effect/registry/application-idempotency/install-retention/bounded-capacity/archive/DR/escrow/human-reroot/post-reroot/client/provider-capability/UNKNOWN-oracle/manual-resolution/canonical-evidence/challenge/quarantine/authority-manifest/effective-authority-lease/retry-authorization/replay-capsule contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade/global provenance/recovery contracts frozen.
