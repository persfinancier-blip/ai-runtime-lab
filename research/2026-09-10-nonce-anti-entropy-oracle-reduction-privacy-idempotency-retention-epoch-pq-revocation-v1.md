# NONCE_ANTI_ENTROPY_ORACLE_REDUCTION_PRIVACY_IDEMPOTENCY_RETENTION_EPOCH_PQ_REVOCATION_V1_FROZEN

Date: 2026-09-10
Status: design frozen / RED-first; executable integration remains gated by LAB-086 exact-source materialization.

## Scope

Distinct follow-up to the prior witness nonce/recovery slice. This freeze closes five remaining recovery ambiguities:

1. nonce checkpoint/compaction anti-entropy under stale replica promotion;
2. adaptive-oracle state poisoning and failure-preserving corpus minimization;
3. privacy reservation idempotency/double-commit and compensating-disclosure semantics;
4. retention membership-epoch rollback and monotonic recovery counters;
5. PQ/ECH ticket-key compromise, generation revocation propagation, and 0-RTT disablement through multi-region recovery.

This is architecture/test-contract evidence only. It does not substitute for exact LAB-086 executable RED/GREEN proof.

## Primary donors

- etcd disaster recovery: snapshot restore can make revisions go backwards; revision bump + mark-compacted is recommended to preserve monotonic client-visible revision semantics and invalidate stale watchers/caches.
- etcd compaction: compaction intentionally makes old revisions inaccessible; therefore absence from a compacted local history is not evidence that an authority event never occurred.
- RFC 5011: trust-anchor revocation is explicit and permanent once validly observed; successor acceptance uses authenticated continuity and hold-down, not mere key freshness.
- RFC 9846 (TLS 1.3): single-use ticket state is the strongest simple 0-RTT anti-replay design; distributed deployments are strongest when one storage zone is authoritative per ticket; freshly started anti-replay state should reject 0-RTT while the recording window overlaps startup.
- RFC 9849 (ECH): retry/config inconsistency can arise from caching, incomplete rollout, key loss, rollback, or inconsistent multi-server configuration; retries are repair machinery rather than proof that prior resumption authority remains valid.
- SLSA provenance/reproducibility guidance: independent evidence must account for the transitive trusted build/control-plane closure; correlated builders/oracles are not independent assurance.
- NIST SP 800-226: privacy loss composes across releases; accounting must be global to the protected subject/purpose boundary rather than reset by local executor identity.

## Frozen invariants

### A. Nonce checkpoint, compaction, and anti-entropy

**A1 — `NONCE_NOT_IN_LOCAL_LOG != NONCE_UNSPENT`.**
A node may have compacted the event, restored before it, or been promoted from a stale replica. Spend authority must therefore consult a monotonic spend/checkpoint lineage, not infer freshness from local absence.

**A2 — checkpoint root is authority state.**
Each checkpoint authenticates at minimum: `checkpoint_generation`, `covered_through_sequence`, prior checkpoint digest, membership epoch, key/policy generation, spend-set accumulator/digest (or equivalent durable summary), compaction boundary, and creation/finalization evidence.

**A3 — compaction cannot erase replay evidence semantically.**
Raw nonce rows may be GC'd only after their spend semantics are represented in an authenticated successor checkpoint whose continuity survives restore/failover.

**A4 — stale replica promotion is fail-closed.**
A replica whose highest authenticated checkpoint is behind the globally required floor cannot authorize consequential spends. It must anti-entropy to an accepted floor or enter `SPEND_AUTHORITY_STALE`.

**A5 — restore creates a new logical recovery generation.**
Restored storage never silently reuses the pre-restore spend-authority generation. Recovery binds the restored snapshot digest and predecessor checkpoint to a successor generation plus explicit gap policy.

**A6 — contradictory checkpoints are split-view evidence.**
Two valid checkpoint heads for the same generation/sequence that commit to different spend summaries are retained as incident evidence; last-writer-wins is forbidden.

### B. Adaptive oracle poisoning and corpus minimization

**B1 — `MINIMIZED_FAILURE_REPRODUCES != MINIMIZED_FAILURE_PRESERVES_SECURITY_CAUSE`.**
Reducer acceptance requires the original security predicate/failure class, not merely any non-zero exit, exception, or oracle disagreement.

**B2 — oracle state is part of provenance.**
Authenticated evidence binds oracle binary/artifact digest, builder/control-plane identity, configuration, dependency set, seed/state snapshot, mutation engine, reward function, stopping rule, and semantic predicate version.

**B3 — adaptive learning cannot silently poison the baseline.**
Inputs discovered by the search process may enter the canonical corpus only through a separate review/promotion event. Search-state updates cannot rewrite oracle expectations for already frozen seeds.

**B4 — differential peers need failure-domain independence.**
Two implementations sharing the same parser library, generator, canonicalizer, builder control plane, or mutable expectation store do not count as two independent votes for the shared surface.

**B5 — minimization is two-phase.**
First preserve the security predicate; then optimize size/complexity. A smaller artifact that changes the violated invariant is a new finding, not the minimized witness for the original one.

**B6 — poisoned-oracle recovery is non-retroactive.**
A successor oracle/corpus generation may reclassify future acceptance, but previously certified results produced during a proven poisoned interval are marked degraded and re-run; they are not silently blessed by the successor.

### C. Privacy reservation idempotency and double commit

**C1 — `RESERVATION_RETRY != NEW_PRIVACY_BUDGET`.**
Every intended disclosure has a globally stable idempotency key derived from protected subject lineage + purpose/policy epoch + request identity + disclosure class.

**C2 — reserve/commit is monotonic accounting.**
A reservation transitions through authenticated states such as `RESERVED -> COMMITTED`, `RESERVED -> EXPIRED_UNKNOWN`, or `RESERVED -> ABORTED_BEFORE_DISCLOSURE`. Duplicate reserve/commit for the same idempotency key cannot consume twice or mint fresh capacity.

**C3 — ambiguous delivery is not free.**
If the system cannot prove that no disclosure left the trusted boundary, timeout/crash produces `EXPIRED_UNKNOWN` and remains charged/reserved until reconciliation. It must not auto-refund merely because the caller did not receive an acknowledgement.

**C4 — compensating disclosure is accounting, not erasure.**
A corrective follow-up disclosure can be separately authorized and charged; it cannot undo privacy loss from already released information.

**C5 — split/merge lineage preserves spend.**
Subject identifier split, merge, pseudonym rotation, verifier migration, or storage restore carries predecessor spend forward through authenticated lineage.

**C6 — double-commit disagreement fails closed.**
Conflicting commits for one reservation id (different disclosure digests, epsilon/delta or policy generation) are retained as equivocation evidence and block additional consequential disclosure for that lineage until reconciled.

### D. Retention membership epoch rollback

**D1 — `VALID_OLD_TIME_ATTESTATION != CURRENT_RETENTION_AUTHORITY`.**
Time/retention attestations bind membership epoch, authority key generation, policy generation, uncertainty/holdover metadata, monotonic recovery counter, and predecessor digest.

**D2 — membership rollback cannot roll policy time backward.**
After observing epoch `E+1` or recovery counter `R+1`, a node restored to `E/R` cannot authorize deletion simply because its local quorum is internally consistent.

**D3 — epoch transition is authenticated and non-mixable.**
Votes from old and new membership sets cannot be combined into one quorum unless the transition contract explicitly defines a joint-consensus phase and binds both sets.

**D4 — recovery counter is externalized from rollback-prone storage.**
At least one accepted monotonic witness/anchor for the counter must survive the same snapshot/restore domain as the retention database, or deletion remains unavailable after ambiguous rollback.

**D5 — holdover expiration fails closed.**
If time sources are unavailable beyond the authenticated uncertainty/holdover budget, state becomes `RETENTION_TIME_UNCERTAIN`; destructive actions remain blocked even if the local clock advances.

**D6 — conflicting policy precedence is explicit.**
Deletion eligibility requires a versioned precedence decision across retention/hold/legal/privacy policies. Clock or membership recovery cannot invent precedence.

### E. PQ/ECH ticket-key compromise and multi-region revocation

**E1 — `TICKET_KEY_ROTATED != OLD_TICKETS_REVOKED_GLOBALLY`.**
Rotation only creates a successor generation. Compromise recovery additionally requires an authenticated revocation generation propagated to every edge/mesh/DR authority able to decrypt or spend predecessor tickets.

**E2 — `CAN_DECRYPT != MAY_RESUME`.**
Ticket decryption is necessary but insufficient. Current authorization rechecks ticket generation, service/backend identity, ALPN, inner-name/ECH context, PQ/hybrid policy floor, route generation, and replay/spend authority.

**E3 — compromised generation disables 0-RTT before convergence.**
Any region that cannot prove it has observed the required revocation floor rejects 0-RTT for affected generations. It may fall back only to a handshake satisfying current crypto and application policy.

**E4 — restart/DR anti-replay gap is explicit.**
Fresh or restored replay stores reject 0-RTT during the overlap/uncertainty window rather than assuming empty state means no prior use.

**E5 — ECH retry does not revive compromised tickets.**
Retry configs repair ECH advertisement/server inconsistency; they never authorize reuse of a ticket from a revoked key/policy/backend generation.

**E6 — multi-region convergence has a floor, not a majority shortcut.**
A ticket is consequentially spendable only where the authoritative revocation/replay floor is known. Majority availability cannot override a missing required floor for a particular ticket generation.

## 40-case RED-first matrix

| ID | Case | Required result |
|---|---|---|
| A01 | spent nonce compacted locally | reject replay via checkpoint summary |
| A02 | snapshot restored before spend | reject until successor recovery generation proves floor |
| A03 | stale replica promoted | `SPEND_AUTHORITY_STALE`, no spend |
| A04 | anti-entropy brings replica to current floor | permit only after verified checkpoint continuity |
| A05 | contradictory same-generation checkpoints | split-view/fail closed |
| A06 | raw nonce GC before successor checkpoint finalizes | reject GC/authorization transition |
| A07 | checkpoint chain missing predecessor | fail closed |
| A08 | restored replica presents lower recovery generation | fail closed |
| B01 | reducer preserves crash but loses security predicate | reject minimization |
| B02 | reducer preserves exact violated invariant | accept minimized witness |
| B03 | adaptive search mutates oracle expectation for frozen seed | provenance violation/fail |
| B04 | two oracles share vulnerable parser dependency | do not count as independent quorum |
| B05 | oracle state restored to older expectations | generation rollback detected |
| B06 | poisoned oracle later replaced | mark affected prior certifications degraded |
| B07 | minimized case exposes a different invariant | record as new finding, retain original witness |
| B08 | corpus promotion lacks source/search provenance | reject promotion |
| C01 | retry same reservation id after timeout | no new budget allocation |
| C02 | duplicate identical commit | idempotent single charge |
| C03 | duplicate commit with different disclosure digest | equivocation/fail closed |
| C04 | crash after possible disclosure before ack | `EXPIRED_UNKNOWN`, no automatic refund |
| C05 | proved no egress before abort | allow `ABORTED_BEFORE_DISCLOSURE` refund policy |
| C06 | corrective disclosure requested | separately authorize/charge; no erasure |
| C07 | subject split then retry | predecessor spend remains composed |
| C08 | accounting snapshot rollback | monotonic spend floor prevents budget reset |
| D01 | old epoch quorum after E+1 observed | reject |
| D02 | restored old recovery counter | reject deletion |
| D03 | mixed old/new votes without joint transition | reject quorum |
| D04 | authenticated joint transition | accept only contract-defined combination |
| D05 | holdover exceeds uncertainty | block destructive action |
| D06 | local clock advances during authority outage | still block deletion |
| D07 | conflicting retention/legal precedence absent | unresolved/fail closed |
| D08 | successor epoch proves lineage and higher counter | resume authority under successor policy |
| E01 | compromised ticket key rotated only in one region | old generation 0-RTT rejected elsewhere until floor known |
| E02 | edge decrypts revoked-generation ticket | reject resumption/0-RTT |
| E03 | restored replay DB is empty | reject 0-RTT during uncertainty window |
| E04 | replay floor recovered and ticket generation current | allow only policy-valid 0-RTT |
| E05 | ECH retry changes backend/config | old ticket not reauthorized by retry |
| E06 | ALPN/service identity changed | reject ticket despite decryption success |
| E07 | PQ/hybrid floor raised after ticket issue | old weaker ticket cannot bypass current floor |
| E08 | one region lacks revocation-generation evidence | region rejects consequential ticket spend |

## Implementation implications

- Treat replay/spend checkpoints as a first-class authenticated ledger, not an optimization around raw nonce rows.
- Give every security-relevant state machine an explicit generation/recovery counter that cannot silently regress with local storage.
- Separate search discovery state from frozen oracle/corpus truth; reductions must name the exact predicate they preserve.
- Use globally stable privacy reservation identifiers and durable `UNKNOWN` states for ambiguous egress.
- Bind retention quorum membership and recovery counters into deletion authorization evidence.
- Bind TLS/PQ resumption to a current ticket-policy/revocation floor independent of whether legacy keys can still decrypt for controlled migration.

## Acceptance boundary

This contract is ready to become tests only after an exact executable repository checkout/materialization path exists. No production refactor or PR status change is justified by this document alone.
