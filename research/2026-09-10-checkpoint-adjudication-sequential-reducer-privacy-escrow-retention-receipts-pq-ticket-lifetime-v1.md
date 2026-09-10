# CHECKPOINT_ADJUDICATION_SEQUENTIAL_REDUCER_PRIVACY_ESCROW_RETENTION_RECEIPTS_PQ_TICKET_LIFETIME_V1_FROZEN

Date: 2026-09-10
Status: design frozen / RED-first; executable integration remains gated by LAB-086 exact-source materialization.

## Scope

Distinct continuation of the checkpoint-equivocation and TLS/PQ incident-recovery line. This slice closes five remaining ambiguity classes:

1. successor/adjudication authority after a checkpoint generation equivocates;
2. sequential-decision bias and rare-event preservation in flaky security reducers;
3. privacy escrow transfer/rebalance during partitions;
4. reconciliation of retention `AUTHORITY_DEGRADED` intervals using independent receipts;
5. PQ/ECH resumption recovery with partial key-erasure evidence, late edge rejoin, and bounded ticket lifetime.

This document is architecture/test-contract evidence only. It does not substitute for the exact executable LAB-086 gate.

## Primary donors and bounded use

- RFC 9162 Certificate Transparency v2: signed heads and consistency proofs are not by themselves a consensus protocol; clients/monitors must detect inconsistent views. Donor use: treat mutually inconsistent authenticated heads as durable evidence and require an explicit successor/adjudication event rather than last-writer selection.
- RFC 5011 DNSSEC trust-anchor update: revocation is explicit/permanent once accepted, and successor anchors require authenticated continuity plus hold-down. Donor use: successor authority after compromised/equivocating generations and delayed re-acceptance, not DNS semantics themselves.
- NIST combinatorial/event-sequence testing guidance: systematic interaction/sequence coverage is needed because failure exposure depends on combinations and ordering. Donor use: rare-event preservation and declared environment/sequence coverage in reducers.
- NIST SP 800-226: privacy budget is cumulative privacy loss across analyses. Donor use: escrow/transfer accounting must preserve a global monotonic upper bound rather than minting budget during partition or rebalance.
- NIST SP 800-88 Rev. 2: cryptographic erase requires an explicit sanitization program and validation; key removal from one location is not automatically complete sanitization. Donor use: partial ticket-key erasure evidence across active, backup, DR, HSM and externally managed domains.
- RFC 8446 TLS 1.3: `NewSessionTicket.ticket_lifetime` MUST NOT exceed 604800 seconds (7 days); clients MUST NOT cache tickets longer than seven days and may discard earlier. Donor use: hard upper bound plus stricter incident-specific ticket-generation policy.
- RFC 9849 ECH: split mode separates client-facing and backend servers; ECH rejection is retry machinery, and repeated inconsistent retry configurations may indicate inconsistent multi-server deployment. Donor use: late-edge/rejoin and backend-generation recovery must not inherit old resumption authority merely because ECH retry succeeds.

## Frozen invariants

### A. Successor/adjudication authority after checkpoint equivocation

**A1 — `EQUIVOCATION_DETECTED != WINNER_SELECTED`.**
Once two incompatible threshold-valid checkpoint heads for the same logical generation/sequence are observed, the generation is terminally marked `EQUIVOCATED`. Ordinary anti-entropy, majority-after-the-fact, timestamps, arrival order and lexicographic digest order cannot select a canonical head.

**A2 — adjudication is a successor transition, not mutation of history.**
Resolution creates a new authenticated successor generation whose transition payload commits to every known conflicting head, their membership/key generations, the last common predecessor and the exact recovery policy used. The old signed heads remain verifiable historical evidence.

**A3 — the accused generation cannot self-adjudicate.**
A witness/key generation that produced incompatible valid heads cannot itself authorize which head is canonical, delete conflict evidence, or define the successor membership. At least one accepted root/recovery authority outside the accused failure domain must participate.

**A4 — `MORE_SIGNATURES_AFTER_EQUIVOCATION != REHABILITATED_GENERATION`.**
Collecting a larger quorum on one old head after conflict discovery does not restore that generation. Its authority is frozen except for narrowly scoped evidence-export/recovery operations.

**A5 — successor transition binds the common floor.**
The recovery event names the last non-conflicting accepted checkpoint, replay/spend floor, compaction boundary, retention/privacy floors and all dependent authority generations. No branch may silently discard effects above that floor unless policy explicitly classifies them as uncertain and requires reconciliation.

**A6 — newly discovered old conflict reopens recovery evidence, not old authority.**
If a third valid conflicting head appears after successor activation, it is appended to the incident evidence set. It may force successor re-evaluation if its effects matter, but it never makes the old generation usable again.

**A7 — adjudication evidence has independent retention.**
The successor generation cannot garbage-collect the conflicting heads until policy-defined external retention/recovery evidence no longer depends on them. The retention decision itself is authenticated under a generation not implicated in the conflict.

**A8 — no cross-generation threshold laundering.**
Votes/signatures from the equivocated generation and successor generation cannot be combined to meet one threshold unless an explicit joint-recovery protocol defines exact roles and quorums.

### B. Sequential-decision bias and rare-event preservation in flaky reducers

**B1 — `STOP_WHEN_FIRST_PASS != UNBIASED_REDUCTION`.**
A reducer that adaptively stops trials after favorable outcomes can systematically retain false candidates or discard true rare failures. Every reduction generation declares its stopping rule before the candidate is evaluated.

**B2 — `ZERO_FAILURES_OBSERVED != ZERO_FAILURE_PROBABILITY`.**
For race/security predicates with low incidence, a finite clean sample only establishes a bounded observation result. The reducer may classify `NOT_OBSERVED_UNDER_BUDGET`; it may not rewrite that as `PREDICATE_ABSENT`.

**B3 — rare-event floor is part of the witness.**
The original case records an empirical or contract-defined minimum reproduction class together with the environment/fault envelope. A candidate whose observed rate collapses below the declared preservation threshold is not accepted merely because it fails once.

**B4 — trial budgets and seeds are committed before outcome-dependent extension.**
Adaptive extension is allowed only by a predeclared sequential policy. Post-hoc adding trials only after surprising failures/passes is recorded as a new evaluation generation, preventing silent optional-stopping bias.

**B5 — reducer objective cannot optimize only for frequency.**
A smaller input with higher failure rate but different causal predicate is a separate finding. Size, predicate identity, event sequence, failure-domain coverage and reproduction class are separate dimensions.

**B6 — sequence/interleaving coverage survives minimization.**
If the original witness depends on a specific ordering class (e.g. commit/timeout/restart/reconcile), the reduced case must preserve the required event partial order or explicitly prove the removed ordering dimension irrelevant.

**B7 — nondeterministic acceptance produces an evidence certificate.**
The certificate records candidate digest, frozen predicate version, trial count, stop rule, successes/failures, seeds, environment ids, event-sequence class, oracle/reducer build digests and final classification.

**B8 — confidence is not independence.**
More trials against the same correlated faulty oracle/build/control-plane do not substitute for an independent verifier. Statistical evidence and provenance independence remain separate gates.

### C. Privacy escrow transfer/rebalance during partitions

**C1 — `ESCROW_TRANSFER_REQUESTED != ESCROW_AVAILABLE_AT_DESTINATION`.**
Budget transfer is a two-sided state machine. Source capacity is reserved/removed before destination capacity becomes spendable; both sides bind one immutable transfer id, subject/purpose/policy lineage and privacy parameters.

**C2 — transfer cannot create overlapping spend authority.**
At no point may the same privacy budget slice be spendable concurrently by source and destination. A transfer may temporarily reduce availability to zero, but may not duplicate capacity to preserve availability.

**C3 — partitioned rebalance is fail-closed without preauthorized ownership.**
If the destination cannot prove source relinquishment at the accepted global/escrow floor, it cannot activate transferred budget. Local timestamps or operator assertions do not substitute for authenticated transfer evidence.

**C4 — timeout after source debit is `TRANSFER_UNKNOWN`, not refund.**
When source has irrevocably removed capacity but destination acknowledgement is lost, reconciliation may complete the same transfer id or retire the slice; it cannot mint a replacement allocation while the original may exist.

**C5 — idempotency spans retries and region failover.**
Retrying the same logical transfer reuses the original transfer id. Same id with a different amount, subject lineage, destination, privacy parameters or policy generation is equivocation/fail-closed evidence.

**C6 — rebalance never lowers global composed spend.**
Moving unused escrow between regions changes where future spend may occur, not historical privacy loss. Already committed or `UNKNOWN/CHARGED` reservations remain globally charged.

**C7 — split/merge of escrow owners preserves conservation.**
One region becoming N regions, or N collapsing into one, requires an authenticated allocation map whose successor capacities sum to no more than the predecessor unspent capacity after all committed/unknown spend.

**C8 — stale restore cannot resurrect transferred-away budget.**
Regional restore below an accepted transfer/escrow checkpoint cannot spend until anti-entropy/recovery proves current ownership and global floor.

### D. Retention degraded-interval reconciliation with independent receipts

**D1 — `DEGRADED_INTERVAL != AUTOMATICALLY_INVALID_HISTORY`.**
Compromise of a retention witness makes authority uncertain, but surviving independent evidence may still prove particular non-destructive or destructive events. Reconciliation is event-specific rather than blanket trust or blanket rollback.

**D2 — independent receipt means independent failure domain.**
A receipt only upgrades confidence if its signing key, storage path, logging path and operator/control plane were outside the compromised witness domain. A second database under the same compromised root is not independent.

**D3 — destructive event reconciliation requires exact payload binding.**
A qualifying receipt binds object/subject scope, action (`hold`, `release`, `delete`, `retain`), policy generation, authority generation, event id, monotonic time/recovery floor and result. A generic audit-line or timestamp is insufficient.

**D4 — absence of receipt does not prove absence of event.**
Missing independent evidence for an event in the degraded interval yields `UNRESOLVED_DEGRADED`, especially for destructive actions. It cannot be normalized to `NOT_EXECUTED` unless the execution mechanism itself provides complete omission-proof logging.

**D5 — conflicting independent receipts are first-class evidence.**
Two independently valid receipts for incompatible outcomes on the same event id trigger `RETENTION_RECONCILIATION_CONFLICT`; no majority or latest-timestamp winner is selected automatically.

**D6 — recovery creates a signed reconciliation map.**
For every event in scope, successor authority records one of `CONFIRMED`, `REJECTED_AS_FORGED`, `UNRESOLVED_DEGRADED`, or `CONFLICT`, with receipt/evidence digests. This map is immutable predecessor evidence for later deletion/hold decisions.

**D7 — unresolved destructive history constrains future deletion.**
If it is unknown whether a hold/release/delete authority transition occurred, the system chooses the non-destructive fail-closed state defined by policy. It does not infer permission to delete from ambiguity.

**D8 — later witness rekey does not erase degraded status.**
Fresh witness keys authorize future decisions; they do not upgrade old events unless the successor reconciliation map cites independent evidence for those exact events.

### E. PQ/ECH recovery: partial key-erasure, late edge rejoin, ticket lifetime

**E1 — `PARTIAL_ERASURE_ATTESTED != TICKET_GENERATION_SAFE`.**
If any eligible restore/decrypt/spend domain can still recover a compromised ticket key, the ticket generation remains revoked. Partial erasure evidence improves incident knowledge but does not reauthorize tickets.

**E2 — ticket lifetime is a hard exposure bound, not a recovery substitute.**
TLS 1.3 tickets have a protocol maximum lifetime of seven days, but incident policy may require much shorter effective lifetimes. Waiting for expiry alone is insufficient when stale edges can restore old clocks/configuration or issue descendants from compromised keying material.

**E3 — descendant ticket issuance is generation-bounded.**
A resumed connection under ticket generation G cannot mint tickets accepted beyond the configured total keying-material ancestry lifetime or across a revocation generation. New tickets carry the current ticket-key, route/backend, ECH and PQ/hybrid policy generations.

**E4 — late edge rejoin begins quarantined.**
An edge returning after partition/recovery may serve neither affected resumption nor 0-RTT until it proves a current revocation floor, ticket-key generation, replay-store recovery floor, route/backend generation and ECH/PQ policy generation.

**E5 — `EDGE_HAS_NEW_SOFTWARE != EDGE_HAS_CURRENT_SECURITY_STATE`.**
Binary/version freshness does not prove state convergence. Rejoin acknowledgement must bind exact state generations and be checked by the admission authority.

**E6 — old ticket decryption is never authority.**
If a late edge still decrypts an old ticket after revocation, the correct result is reject + incident evidence. Successful cryptographic decryption cannot override the revocation floor.

**E7 — partial erasure plus bounded lifetime may permit future generations, not old ones.**
Service can recover by excluding unverified domains from eligibility, converging a successor revocation/ticket generation and issuing fresh tickets. The old generation remains permanently invalid even after its natural lifetime expires.

**E8 — ECH/backend convergence is rechecked on rejoin.**
A late edge that presents stale ECH configuration, stale backend mapping or repeated retry-config inconsistency cannot accept resumption merely because the origin certificate/PSK is otherwise valid. Resumption and 0-RTT remain disabled until current routing/security policy is authenticated.

## 40-case RED-first matrix

| ID | Case | Required result |
|---|---|---|
| A01 | two threshold-valid heads same generation/sequence | mark generation `EQUIVOCATED`; preserve both |
| A02 | one conflicting head later gains larger quorum | no rehabilitation/winner selection |
| A03 | successor recovery references only one known conflicting head | reject incomplete adjudication |
| A04 | recovery root outside accused domain references all conflicts + common floor | accept successor transition |
| A05 | accused generation signs its own winner/adjudication | reject |
| A06 | third old conflicting head discovered after successor activation | append evidence; keep old generation revoked |
| A07 | successor requests GC of conflicts still required by recovery policy | reject GC |
| A08 | old+new generation signatures mixed to meet threshold without joint protocol | reject quorum |
| B01 | reducer accepts candidate after first lucky failure | reject undeclared stopping rule |
| B02 | zero failures in finite rare-event budget | classify `NOT_OBSERVED_UNDER_BUDGET`, not absent |
| B03 | candidate preserves same predicate but reproduction rate below declared floor | reject reduction |
| B04 | predeclared sequential policy extends trials after boundary result | permit and record one evaluation generation |
| B05 | post-hoc trials added selectively after surprising result | new generation / no silent evidence merge |
| B06 | smaller case fails frequently through different invariant | separate finding |
| B07 | required commit-timeout-restart ordering removed | reject unless irrelevance is proven |
| B08 | certificate records trials/seeds/stop rule/predicate/builds | accept evidence form |
| C01 | source escrow debited, partition before destination ack | `TRANSFER_UNKNOWN`; no refund/new allocation |
| C02 | destination activates before proof of source relinquishment | reject |
| C03 | same transfer id retried after failover | idempotent continuation |
| C04 | same transfer id, changed amount/destination | equivocation/fail closed |
| C05 | split one regional escrow into three successors | sum successor unspent <= predecessor unspent |
| C06 | restore source from snapshot before completed transfer | current floor prevents resurrected spend |
| C07 | historical committed privacy spend followed by rebalance | historical spend remains charged |
| C08 | two regions claim same escrow slice after merge | block disclosure pending reconciliation |
| D01 | compromised witness event has exact independent receipt | eligible for successor `CONFIRMED` |
| D02 | receipt stored/signed under same compromised domain | no independent-evidence credit |
| D03 | destructive event has no receipt | `UNRESOLVED_DEGRADED`; no delete permission |
| D04 | two independent receipts bind incompatible outcomes | `RETENTION_RECONCILIATION_CONFLICT` |
| D05 | generic timestamp but no exact action/policy binding | insufficient evidence |
| D06 | successor reconciliation map omits an in-scope event | reject map |
| D07 | fresh rekey tries to mark all old events trusted | reject retroactive trust |
| D08 | unresolved hold/release ambiguity precedes new deletion | enforce policy's non-destructive fail-closed state |
| E01 | primary/HSM erased but DR copy unverified | old ticket generation remains revoked |
| E02 | old ticket naturally exceeds seven-day TLS max | reject; expiry does not erase incident evidence |
| E03 | policy lifetime is shorter than protocol max | enforce shorter policy lifetime |
| E04 | resumed G ticket attempts to mint descendant crossing revocation generation | reject descendant authority |
| E05 | late edge rejoins with current binary but stale revocation floor | quarantine resumption/0-RTT |
| E06 | late edge decrypts revoked old ticket | reject + record incident evidence |
| E07 | unverified recovery domain removed from eligible service set; successor generation converged | permit fresh-ticket issuance only under successor policy |
| E08 | edge has stale ECH/backend generation or retry-config inconsistency | keep resumption/0-RTT disabled |

## Implementation implications

- Add a terminal `EQUIVOCATED` checkpoint-generation state and a distinct successor `ADJUDICATED_RECOVERY` transition that commits to the full conflict set and last common floor.
- Flaky reducer evidence should implement a declared repeated/sequential decision policy and emit `NOT_OBSERVED_UNDER_BUDGET` rather than conflating finite clean runs with absence.
- Privacy escrow moves should use one immutable transfer id and source-debit-before-destination-credit semantics, with `TRANSFER_UNKNOWN` reconciliation rather than optimistic double ownership.
- Retention incident recovery needs an immutable per-event reconciliation map and explicit independence metadata for receipts/failure domains.
- TLS/PQ recovery should model ticket generation, revocation floor, maximum ancestry lifetime, key-erasure coverage and edge rejoin admission separately. Natural ticket expiry and successful decryption must never override a revocation generation.

## Acceptance boundary

This contract becomes executable only after a supported byte-exact repository materialization path exists. It does not justify changing any draft PR state or claiming LAB-086 validation. The next executable work remains the exact pinned LAB-086 real-schema gate when transport/materialization becomes available.