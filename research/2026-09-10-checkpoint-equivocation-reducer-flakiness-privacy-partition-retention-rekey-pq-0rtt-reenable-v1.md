# CHECKPOINT_EQUIVOCATION_REDUCER_FLAKINESS_PRIVACY_PARTITION_RETENTION_REKEY_PQ_0RTT_REENABLE_V1_FROZEN

Date: 2026-09-10
Status: design frozen / RED-first; executable integration remains gated by LAB-086 exact-source materialization.

## Scope

Distinct continuation of the nonce anti-entropy and ticket-revocation work. This slice closes five remaining incident-recovery ambiguities:

1. checkpoint quorum equivocation, anti-entropy and compaction-proof survivability;
2. nondeterministic predicate-preserving delta debugging and reducer evidence;
3. privacy reservation reconciliation across cross-region partitions;
4. retention recovery-counter witness compromise and authenticated rekey;
5. PQ/ECH revocation-floor acknowledgement, ticket-key erasure evidence and strict 0-RTT re-enable criteria.

This document is architecture/test-contract evidence only. It does not substitute for the exact executable LAB-086 gate.

## Primary donors and bounded use

- etcd disaster recovery: restored revisions can go backwards; revision bump plus mark-compacted is used to prevent stale client-visible history from masquerading as current history and to invalidate stale watchers. Donor use: monotonic recovery floors and compaction semantics, not a claim that etcd implements the proposed witness protocol.
- RFC 9162 Certificate Transparency v2: append-only consistency and cross-observer view consistency are separately auditable properties; inconsistent signed heads are durable evidence of log misbehavior. Donor use: split-view evidence retention and checkpoint consistency proofs.
- SLSA provenance/reproducibility guidance: multiple results are stronger only when their trusted build/control-plane domains are actually independent. Donor use: reducer/oracle provenance and failure-domain independence.
- RFC 5011: valid revocation is explicit and permanent, while successor trust-anchor acceptance requires authenticated continuity and hold-down. Donor use: compromised retention-witness key recovery/rekey semantics.
- NIST SP 800-226: privacy loss composes across releases; distributed accounting cannot reset merely because execution moves to another local authority. Donor use: conservative cross-region privacy-budget reconciliation.
- NIST SP 800-88 Rev. 2: cryptographic erase is a sanitization technique with explicit key-sanitization/validation considerations. Donor use: distinguish key-rotation claims from evidence that old key material is no longer recoverable in the relevant storage/backup domains.
- RFC 9846 TLS 1.3: 0-RTT has weaker replay properties; a single authoritative storage zone per ticket provides the strongest simple distributed anti-replay design, and freshly started implementations should reject 0-RTT while the recording window overlaps startup. Donor use: post-incident re-enable gate.
- RFC 9849 ECH: retry configurations repair ECH configuration inconsistency and may expose inconsistent multi-server rollout; they do not by themselves re-establish old resumption authority. Donor use: bind resumption recovery to current ECH/backend generation.

## Frozen invariants

### A. Checkpoint quorum equivocation, anti-entropy and compaction-proof survivability

**A1 — `QUORUM_SIGNED_CHECKPOINT != UNIQUE_CHECKPOINT_HISTORY`.**
A threshold-signed checkpoint is not enough if two threshold-valid heads for the same logical generation/sequence can exist. The verifier must check predecessor lineage and retain contradictory heads as split-view evidence.

**A2 — checkpoint acknowledgement binds exact semantics.**
Each witness acknowledgement binds at minimum: checkpoint digest, predecessor digest, covered-through sequence, membership epoch, witness/key generation, compaction boundary, spend accumulator root, recovery generation, transition id and freshness/nonce lineage.

**A3 — anti-entropy cannot choose by arrival time.**
If peers present incompatible threshold-valid heads, `latest_received`, wall-clock timestamp, lexical digest order, or majority-after-the-fact cannot adjudicate history. State becomes `CHECKPOINT_EQUIVOCATION` until an authenticated successor recovery transition explicitly references the conflicting evidence.

**A4 — compaction proof must outlive compacted rows.**
Before raw nonce/event history is discarded, an authenticated successor checkpoint must commit to the semantics needed to reject replay and prove the compaction boundary. The proof material required to validate this commitment must survive the same storage retirement that removes the raw rows.

**A5 — `COMPACTION_COMPLETED != COMPACTION_PROOF_DURABLE`.**
Deleting source rows before the successor proof is independently durable is forbidden. Backups, replicas and DR images capable of later reintroducing pre-compaction state remain in the recovery universe.

**A6 — restore is bounded by an external accepted floor.**
A restored node whose local head is below an already accepted checkpoint/recovery floor cannot vote, spend or authorize destructive transitions until anti-entropy establishes authenticated continuity to that floor or a successor recovery transition supersedes it.

**A7 — equivocation evidence is non-garbage-collectable by the accused generation.**
A generation whose keys/witnesses produced conflicting heads cannot itself authorize deletion of those conflicts. Retention requires an independent successor policy/root.

**A8 — checkpoint membership transition is explicit.**
Old and new witness sets cannot be mixed opportunistically to reach threshold. Joint-consensus, if supported, must be a named authenticated transition with exact quorum rules for both sets.

### B. Nondeterministic predicate-preserving delta debugging

**B1 — `ONE_REPRODUCTION != STABLE_REPRODUCTION`.**
For a flaky/security-race finding, reducer acceptance requires a declared statistical/repetition policy and preservation of the same security predicate, not one lucky failing run.

**B2 — predicate identity is frozen before reduction.**
The failure witness names the violated invariant, observable classification, expected/forbidden state transition and evidence extraction rule. Reducers may simplify input only while this predicate remains satisfied.

**B3 — environment is part of the reduction input.**
Scheduler seeds, time source, process topology, concurrency level, fault-injection state, dependency versions and relevant hardware/runtime parameters are provenance, not incidental metadata.

**B4 — `HIGH_FAILURE_RATE != SAME_CAUSAL_FAILURE`.**
A minimized case that fails more frequently but through a different predicate is a new finding. It must not replace the original witness.

**B5 — nondeterministic reducer decisions are auditable.**
Every keep/drop decision records trial count, successes, failures, confidence/decision threshold, seeds/environment ids and reducer/oracle artifact digests.

**B6 — oracle and reducer cannot silently co-adapt.**
Adaptive reducer state cannot rewrite the frozen predicate or expected outputs. Oracle-generation change requires a new attested evaluation generation and reclassification of prior certificates as needed.

**B7 — independence is measured by failure domains.**
Two repeated test harnesses sharing parser/oracle/build/control-plane bugs do not count as independent confirmation merely because they have different process ids or hosts.

**B8 — minimization must preserve a replayable envelope.**
The final artifact includes the smallest known predicate-preserving input plus the environment/fault envelope required to reproduce the probability class; removing that envelope is not successful minimization.

### C. Privacy reservation reconciliation after cross-region partition

**C1 — `REGION_B_DID_NOT_SEE_COMMIT != DISCLOSURE_DID_NOT_HAPPEN`.**
During partition, absence of a remote commit is not evidence that another region did not disclose. Consequential budget allocation requires knowledge of the global accepted spend/reservation floor.

**C2 — reservation ids are globally stable.**
Retries, failover and routing changes reuse the same logical idempotency lineage for one intended disclosure. Region migration does not mint a fresh budget identity.

**C3 — partition policy is conservative by construction.**
A region unable to prove current global budget state may either reject new disclosure or consume from a pre-authorized, non-overlapping regional escrow allocation whose total is already charged against the global budget. It may not optimistically oversubscribe and reconcile later.

**C4 — `LOCAL_ESCROW_AVAILABLE != GLOBAL_ESCROW_UNSPENT` after rollback.**
Escrow state itself requires monotonic checkpoint/recovery lineage; restored regional state cannot resurrect capacity already spent before the snapshot.

**C5 — ambiguous delivery remains charged/unknown.**
If a region emitted data but lost the commit acknowledgement during partition, reconciliation must not refund merely because another region cannot observe delivery evidence.

**C6 — conflicting commits are preserved.**
Same reservation id with different disclosure digest, privacy parameters, subject lineage or policy generation is equivocation evidence and blocks further spend for that lineage pending authenticated resolution.

**C7 — merge after partition is monotonic.**
Reconciliation unions committed/unknown spend semantics and consumes the maximum authoritative predecessor floor; it never averages or last-writer-wins privacy loss downward.

**C8 — emergency availability mode cannot weaken privacy semantics silently.**
Any degraded mode that permits disclosure during control-plane partition must be explicitly versioned, pre-budgeted and auditable; otherwise fail closed.

### D. Retention recovery-counter witness compromise and rekey

**D1 — `NEW_WITNESS_KEY != CLEAN_HISTORY`.**
Rekey after compromise creates a successor trust generation; it does not retroactively authenticate retention/deletion decisions signed during the compromised interval.

**D2 — recovery bridge names the compromised interval.**
The successor attestation binds predecessor key/witness generation, last unquestionably accepted recovery counter/checkpoint, compromise declaration, excluded/uncertain interval, successor membership/key generation and policy epoch.

**D3 — revoked witness material stays revoked.**
Once a witness/key generation is validly revoked by an accepted successor recovery process, restore or stale replica state cannot make it authoritative again.

**D4 — successor acceptance has continuity, not freshness-only semantics.**
A newly generated key is not trusted solely because it is newer. It must be introduced by an already accepted recovery/root path or an explicitly defined offline-root process.

**D5 — uncertain destructive history is quarantined.**
Deletion/retention actions from a proven compromised interval are not silently retained as trusted nor silently rolled back. They are marked `AUTHORITY_DEGRADED` and reconciled against surviving independent evidence.

**D6 — recovery counter cannot be self-certified by the compromised domain.**
At least one accepted counter/root witness must lie outside the storage/key/control-plane failure domain being recovered; otherwise destructive authority remains unavailable.

**D7 — rekey quorum membership cannot be availability-selected after compromise.**
The recovery policy fixes eligible roots/witnesses before observing which subset is easiest to reach, preventing attacker-shaped quorum selection.

**D8 — revocation evidence survives key retirement.**
Deleting old private material does not permit deletion of public revocation/lineage evidence needed to reject stale restored attestations.

### E. PQ/ECH revocation-floor acknowledgement, erasure evidence and 0-RTT re-enable

**E1 — `REVOCATION_PUBLISHED != REVOCATION_OBSERVED_BY_ALL_SPEND_AUTHORITIES`.**
Incident closure requires acknowledgements from every currently eligible edge/mesh/DR authority that can decrypt or consequentially spend affected ticket generations, or those authorities must be cryptographically/policy-removed from service.

**E2 — acknowledgement binds exact floor.**
Each authority attests to revocation generation, ticket-key generations disabled, replay-store recovery generation, route/backend generation, ECH config generation, ALPN/service policy and current PQ/hybrid floor.

**E3 — `KEY_ROTATED != OLD_KEY_ERASED`.**
Rotation only stops normal issuance. Erasure evidence separately covers active memory, persistent stores, HSM slots/replicas, backups/snapshots, DR material and externally managed copies within the declared threat/recovery universe.

**E4 — `ERASURE_AT_PRIMARY != ERASURE_FROM_RECOVERY_UNIVERSE`.**
Old ticket authority cannot be considered irrecoverable while any supported restore path can reintroduce the compromised key or pre-revocation policy without a higher external revocation floor.

**E5 — proof of erasure is evidence-bounded, not metaphysical.**
The system records which key domains were zeroized/sanitized, by what mechanism, validation result, operator/provider attestation and remaining unprovable domains. Missing assurance keeps the ticket generation revoked and 0-RTT disabled; it does not claim impossible certainty.

**E6 — 0-RTT re-enable is a new generation transition.**
It requires: current revocation floor acknowledged by every eligible spend authority; replay stores at a known recovery generation; startup/recording-window overlap elapsed or otherwise proven safe; compromised ticket generations rejected; current SNI/inner ECH/backend/ALPN/PQ policy bound; and issuance under a new accepted ticket-key generation.

**E7 — 1-RTT availability does not imply 0-RTT readiness.**
Services may resume full policy-valid handshakes while 0-RTT remains disabled. Availability pressure cannot collapse the two states.

**E8 — ECH retry/config repair does not bypass incident floor.**
Retry configs may repair stale ECH advertisements, but any resumed connection still satisfies the current revocation, backend, service identity and PQ/hybrid policy generation.

## 40-case RED-first matrix

| ID | Case | Required result |
|---|---|---|
| A01 | two threshold-valid checkpoint heads same generation/sequence | `CHECKPOINT_EQUIVOCATION`, preserve both |
| A02 | peer offers later timestamp on conflicting head | no last-writer adjudication |
| A03 | raw nonce rows compacted after durable successor proof | replay rejected from checkpoint semantics |
| A04 | raw rows deleted before proof durability | block compaction completion |
| A05 | restored backup reintroduces pre-compaction state | external floor blocks spend/vote |
| A06 | equivocation evidence GC requested by compromised generation | reject |
| A07 | old/new witness votes mixed without joint transition | reject quorum |
| A08 | authenticated joint-consensus transition | accept only exact declared quorum semantics |
| B01 | flaky predicate reproduces 1/1 once | insufficient stability evidence |
| B02 | repeated runs meet declared predicate probability threshold | candidate reduction accepted |
| B03 | minimized case crashes via different invariant | retain as new finding, not replacement |
| B04 | scheduler seed omitted and result no longer replayable | reduction evidence incomplete |
| B05 | reducer mutates oracle expected output | reject provenance generation |
| B06 | two harnesses share same compromised oracle artifact | no independent-vote credit |
| B07 | reduction decision lacks trials/seeds | reject audit record |
| B08 | smaller case preserves predicate plus required environment envelope | accept minimized witness |
| C01 | region A commits disclosure while partitioned; B sees absence | B cannot infer unspent budget |
| C02 | retry routed from A to B with same reservation id | no new allocation |
| C03 | pre-authorized non-overlapping regional escrow | permit only within authenticated escrow |
| C04 | restored regional escrow predates spend | monotonic floor blocks resurrected capacity |
| C05 | disclosure possibly emitted, commit ack lost | `UNKNOWN/CHARGED`, no refund |
| C06 | same reservation id, different disclosure digest | equivocation/fail closed |
| C07 | partition reconciliation sees A commit + B unknown | compose conservatively, never reduce spend |
| C08 | emergency mode lacks pre-budgeted policy | reject disclosure |
| D01 | witness key compromise followed by fresh key generation only | no restored destructive authority |
| D02 | successor recovery bridge names compromised interval | allow successor evaluation, preserve degraded interval |
| D03 | stale snapshot presents revoked witness generation | reject |
| D04 | successor key introduced only by compromised domain | reject trust transition |
| D05 | deletion signed inside compromised interval | quarantine/reconcile, no silent trust |
| D06 | recovery counter stored only in compromised DB | block deletion authority |
| D07 | recovery chooses convenient post-incident quorum not pre-authorized | reject |
| D08 | public revocation evidence retained after private-key destruction | stale signatures remain rejectable |
| E01 | revocation published but one eligible edge unacknowledged | keep 0-RTT disabled there/global policy as declared |
| E02 | edge ack names wrong revocation generation | reject acknowledgement |
| E03 | ticket key rotated but backup still restores old key | generation remains revoked; no erasure claim |
| E04 | HSM zeroization validated but external replica unverified | erasure incomplete, fail closed for 0-RTT |
| E05 | all eligible spend authorities acknowledge floor; fresh replay generation established | pass revocation-convergence prerequisite |
| E06 | 1-RTT healthy before recording-window safety | allow policy-valid 1-RTT, keep 0-RTT off |
| E07 | old ticket decrypts after incident | reject regardless of decryption success |
| E08 | ECH retry reaches new backend but old ticket generation supplied | reject resumption/0-RTT |

## Implementation implications

- Model checkpoint equivocation as a first-class incident state; never let anti-entropy silently pick a winner among incompatible authenticated heads.
- Persist compaction proofs and split-view evidence outside the lifecycle of the rows they summarize.
- Give flaky security reducers a frozen predicate plus reproducibility envelope and auditable statistical decision log.
- Use global reservations or pre-accounted non-overlapping escrow for partition-tolerant privacy release; optimistic oversubscription is prohibited.
- Treat retention witness rekey as trust recovery with an explicit degraded interval, not as key rotation alone.
- Separate TLS ticket issuance, decryption capability, revocation-floor convergence, key-erasure evidence, 1-RTT availability and 0-RTT authorization into distinct state transitions.

## Acceptance boundary

This contract is ready to become executable tests only after a supported byte-exact repository materialization path exists. No PR should leave draft and no production refactor should be represented as validated based on this freeze alone.
