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
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues, active PRs and PR #165 directly. LAB-086 remains first priority and PR #165 remains open/draft on `ee210a47221b6df53f3518aa3af74f76c5b0122b`.

Probed the currently available GitHub integration for the exact publication need. It exposes exact UTF-8 repository reads, PR patches/comparisons and normal Contents API replacement writes, but no supported machine transform/materialization bridge that can consume exact connector-returned predecessor bytes plus retained patch bytes and mechanically emit a byte-verified composed target without model reserialization. Security-critical `strict_fence.py` therefore remains untouched; no new LAB-086 behavioral PASS is claimed.

Completed the recorded distinct fallback: froze `COMPATIBILITY_PROOF_FIXTURE_SYNTHESIZER_MINIMAL_DISTINGUISHING_CORPUS_HISTORICAL_EDGE_COVERAGE_V1_FROZEN` in `research/2026-09-06-compatibility-proof-fixture-synthesizer-minimal-distinguishing-corpus-historical-edge-coverage-v1.md`, main commit `1a30d1da5e926075546a301de7ccf61109477954`; #178 comment `5556581397` records the result.

Key decisions:
- compatibility proof requires distinguishing power, not merely A/B equality on a convenient corpus;
- every consequential typed semantic delta creates dimension-specific witness obligations;
- every obligation requires a positive fixture and a controlled negative mutant that the retained fixture set can kill;
- fixture synthesis targets semantic predicates and impact-cone nodes, not source lines;
- presence/default changes require absent / explicit-default / non-default witnesses where representable;
- enum/open-world changes require zero/default plus unknown/future values, not only currently named values;
- request-effect, historical replay, evidence, reconciliation and disclosure use separate oracles; serialized-byte equality cannot stand in for all of them;
- auth/signing, retry/idempotency and error-classification changes receive effect/authority-aware witnesses;
- deterministic corpus minimization happens only after full obligation coverage and mutation validation, and emits an auditable subsumption trace;
- the sole distinguisher for an obligation, historical rarity-pinned fixture, semantic boundary state, or distinct impact-cone path cannot be minimized away;
- correlated deltas require targeted interaction witnesses when they share a semantic predicate or impact-cone node;
- rare historical enum/error/presence/UNKNOWN/replay states are authenticated and privacy-minimized but protected from frequency-biased eviction;
- historical compatibility edges remain bound to their original fixture proof generation; newly discovered obligations force `REVALIDATION_REQUIRED` rather than silent reinterpretation;
- rollback to an older generator/fixture engine cannot erase obligations recognized at a newer authenticated registry frontier.

An explicit 80-case RED-first matrix is frozen across vacuous fixtures/reachability, presence/defaults, enum/union/open-world behavior, wire/effect/auth/retry, errors/reconciliation, impact-cone/partial regeneration, correlated mutations/minimization and historical/toolchain/frontier integrity. No production fixture synthesizer, minimizer or compatibility PASS is claimed.

Primary donors: Smithy model breaking-change/diff semantics; Protocol Buffers documented field-presence, enum/open-world and schema-evolution behavior; JSON Schema official test-suite/Bowtie cross-implementation fixture mechanism. These are donor mechanisms only; LAB's consequential proof remains stricter and multi-dimensional.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Exact predecessor and retained patch bytes are observable through the connector, but no supported byte-preserving transform/materialization bridge to a Contents API replacement has been observed in this run.
- Normal Contents API requires complete replacement text and is not a predecessor+patch transform.
- Authoritative lineage remains `d4a6a40f...` + `61841b58...` -> `b78e7c98...`.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 must use the frozen shared canonical V1 encoding, parent-linked chain, atomic append/recovery protocol, durable SQL storage, verifier/planner, external evidence continuity, recovery executor and finite broker startup machine; no independent locally-valid provenance islands.
- LAB-093 must implement the frozen least-capability façade and retained session/request/effect/idempotency/retention/archive/DR/escrow/reroot/provider-capability/UNKNOWN/manual-resolution/evidence/challenge/quarantine/authority/retry/replay/transport-observer/capacity-compaction/archive/privacy-minimization/policy-compiler/evidence-schema-registry/model-normalization/model-semantic-diff/fixture-proof contracts; production implementation waits for executable RED/GREEN.
- LAB-093..100 production implementation waits for exact executable RED/GREEN.
- No production post-reroot cutover, re-admission after trust discontinuity, manual consequential re-attempt, retention/privacy exception, plaintext-expanding evidence-policy upgrade or provider evidence-schema widening may be activated without required explicit product/security/business/legal authority bound to the exact decision.

## Exact next action
LAB-086 first: probe only for a genuinely supported machine transform/materialization path that can consume the exact connector-returned predecessor blob plus retained patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

If neither capability appears: next distinct evidence task is to freeze a **compatibility proof oracle independence / mutant soundness / metamorphic relation contract**. Define how negative mutants are constrained so they represent one prohibited semantic interpretation rather than arbitrary broken code; require independent oracles that are not generated from the same faulty transformation under test; define metamorphic relations for presence/default, enum openness, signing scope, idempotency/retry, error classification and historical replay; detect equivalent mutants that cannot be killed because they are semantically identical; prevent oracle-generator common-mode failure; bind mutant catalog and oracle provenance to source/artifact generations; freeze RED cases for self-fulfilling oracles, overpowered mutants, equivalent mutants, mutant masking, correlated oracle+implementation bugs, nondeterministic provider observations and stale historical oracle expectations.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + global provenance/recovery contracts; exact RED/full gate pending.
- #178 / LAB-093 — READY; provider evidence/privacy/policy/schema/model-normalization/model-semantic-diff/fixture-proof contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade/global provenance/recovery contracts frozen.
