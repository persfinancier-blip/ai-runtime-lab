# Current Lab State

Last updated: 2026-09-07

## Active objective
LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; recorded head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Authoritative pending hidden-rowid lineage: predecessor blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required composed target blob `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- Draft/IN_PROGRESS stack remains open: LAB-088/#167 PR #172; LAB-090/#169 PR #175; LAB-091/#170 PR #173; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and open PRs. LAB-086 remains the highest-priority unfinished task.

Re-probed the exact LAB-086 capability in this run:
- `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- connector read/write remains available but no supported byte-preserving machine transform from exact predecessor+patch bytes to the exact candidate was observed;
- manual/model reserialization of security-critical `strict_fence.py` remains prohibited;
- therefore `strict_fence.py` was not mutated and no new LAB-086 behavioral PASS is claimed.

Completed the recorded distinct fallback: froze `CAPABILITY_ENVELOPE_TRANSITIVE_DELEGATION_PREOPENED_HANDLE_PROVENANCE_AMBIENT_AUTHORITY_ELIMINATION_V1_FROZEN` in `research/2026-09-07-capability-envelope-transitive-delegation-preopened-handle-provenance-ambient-authority-elimination-v1.md`, main commit `1500bf615842c1e7d72b6d42dbd3cafbcfd3d413`; #178 comment `5563684438` records the result.

Key decisions:
- registered consequential capability existence is not sufficient after delegation; every concrete consequential handle/session/task instance requires authenticated lineage;
- introduced `CapabilityEnvelopeV1` with stable capability/instance/delegation identities, ancestor digest, issuer/recipient epochs, object/session binding independent of local FD/pointer number, rights/resource/temporal scope, explicit re-delegation authority, causal parent, revocation domain/generation, trust/schema/inventory frontiers and enforcement binding;
- fork/exec, `SCM_RIGHTS`, plugin handoff, queued work, broker/provider-session transfer and recovery are explicit delegation events rather than ambient continuation;
- descendant authority must monotonically attenuate; possessing mutate authority does not imply duplicate/transfer/re-delegation authority;
- pre-opened/inherited consequential handles require trusted launcher/broker provenance; unknown handles are not valid authority merely because a sandbox inherited them;
- ambient credentials/default credential chains/provider sessions must not silently satisfy consequential authority requirements;
- queued work freezes a causal authority reference but revalidates current recipient epoch, revocation generation, expiry and policy/trust frontiers at execution;
- revocation propagates over the logical descendant DAG; restart cannot promote a descendant into a fresh root;
- physical and logical revocation are distinct. Unmediated transferred capabilities that remain physically usable and cannot be clawed back are `REVOCATION_UNENFORCEABLE` for claims requiring descendant revocation;
- same-process Python encapsulation cannot establish a hostile least-authority boundary; production LAB-093 claims compose with LAB-087 process/broker isolation or equivalent;
- froze `DelegationAttenuationProofV1`, undeclared-delegation / attenuation-violation / revoked-descendant fraud proofs and an 80-case RED-first matrix.

Primary donors: Linux `SCM_RIGHTS` open-file-description transfer semantics and `O_PATH`; Linux Landlock pre-existing-FD limitations; FreeBSD Capsicum explicit capability mode + non-expanding `cap_rights_limit`; Fuchsia handle rights with separate DUPLICATE/TRANSFER rights and trusted-history limits; Linux locked socket-filter delegation.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Direct git transport failed in this run before repository execution with DNS resolution failure.
- Exact predecessor + retained patch remain readable through connector history, but no supported byte-preserving composition bridge has been observed.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 production implementation must compose all frozen authority/evidence/privacy/policy/schema/model/proof/adjudicator/trust-frontier/monitoring/non-inclusion/mapper/bootstrap-compaction/GC/schema-repair/materiality/substitution/verifier-agility/sunset-refresh/concurrent-inventory/federated-barrier/producer-manifest/schema-authority/effect-capability-inventory/capability-delegation contracts instead of creating locally valid authority islands.
- New audit risk: revocation cannot be declared complete merely because all currently known descendants were invalidated. Offline recipients, partitioned queues, duplicated handles and unregistered descendants can later reappear; some raw OS capabilities cannot be physically clawed back.

## Exact next action
LAB-086 first: probe only for a genuinely supported byte-preserving machine transform/materialization path that consumes exact connector-returned predecessor + retained patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

If neither capability appears: next distinct evidence task is **descendant-discovery completeness / revocation-set closure / offline-delegate resurrection semantics**. Define how to prove a revocation campaign has discovered every still-live descendant without assuming a central registry is complete; handle offline workers, partitioned queues, duplicated/transferred OS handles, provider sessions, crash recovery and delayed task resurrection; distinguish mechanically enumerable descendants from logically discoverable/independently observable ones; define safe completion horizons/leases or permanent `UNKNOWN` where clawback is impossible; bind finalization/GC to revocation-set closure evidence; and freeze RED cases for omitted descendants, late reconnect, duplicate-handle resurrection, stale queues, split-brain brokers, epoch rollover, lease expiry, physical-vs-logical revocation and recovery.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + global provenance/recovery contracts; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability-envelope transitive delegation/pre-opened provenance/ambient-authority elimination contract now frozen in addition to prior contracts; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade/global provenance/recovery contracts frozen.
