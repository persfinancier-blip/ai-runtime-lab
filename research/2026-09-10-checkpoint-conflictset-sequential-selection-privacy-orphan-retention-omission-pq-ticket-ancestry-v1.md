# Checkpoint conflict-set completeness, sequential-selection bias, privacy orphan reclamation, retention omission coverage, and PQ/ECH ticket ancestry

Date: 2026-09-10
Status: DESIGN_FROZEN / RED-FIRST; no executable LAB-086 PASS claimed in this run.
Contract id: `CHECKPOINT_CONFLICTSET_SEQUENTIAL_SELECTION_PRIVACY_ORPHAN_RETENTION_OMISSION_PQ_TICKET_ANCESTRY_V1_FROZEN`

## Run boundary

LAB-086 remains priority #1. In this run direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository code execution with `Could not resolve host: github.com`. GitHub connector read/write operations were available, but no supported non-model connector-to-local-filesystem byte materializer was exposed. The retained byte-exact execution gate therefore remains unmet; this note is a distinct evidence/design slice only.

## Primary donors

1. RFC 9162, Certificate Transparency Version 2 — inclusion proofs, consistency proofs, signed tree heads, final/frozen log behavior. https://www.rfc-editor.org/rfc/rfc9162.html
2. NIST SP 800-226, Guidelines for Evaluating Differential Privacy Guarantees — cumulative privacy loss and privacy budgeting/composition. https://csrc.nist.gov/pubs/sp/800/226/final
3. RFC 8446, TLS 1.3 — PSK/ticket semantics, SNI on resumption, seven-day ticket maximum, distinct ticket nonces, and recommendation to bound the total lifetime of keying material derived from an original authenticated handshake. https://www.rfc-editor.org/rfc/rfc8446.html
4. RFC 9849, TLS Encrypted Client Hello — ECH rejection/retry semantics; authentication of the public name does not authenticate the origin and session tickets/session IDs from the rejection connection must be ignored. https://www.rfc-editor.org/rfc/rfc9849.html

## 1. Checkpoint adjudication: conflict-set completeness and successor-root compromise/replay

### Facts / donor mechanisms

RFC 9162 distinguishes an authenticated tree head from proofs about inclusion and append-only consistency. Inclusion proof verifies that a chosen entry is committed by a chosen tree root; consistency proof verifies append-only relation between two roots. These are narrower than a proof that the observer has discovered every conflicting root ever signed by a compromised/equivocating authority.

A final STH is useful as a durable frozen commitment when a CT log is shut down, but finalization does not retroactively prove that the log never produced another incompatible STH to a different observer.

### Derived failure boundary

`ADJUDICATION_CONTAINS_ALL_KNOWN_HEADS != ADJUDICATION_PROVES_NO_UNKNOWN_CONFLICTING_HEAD_EXISTS`.

An adjudicating successor must commit to the complete conflict set *known to the recovery authority at decision time*, plus a discovery/observation envelope. It must not claim universal completeness unless the system has a separate mechanism that can prove it.

If the successor-root key is later compromised, replaying a previously valid `ADJUDICATED_RECOVERY` statement under that key must not authorize a new transition. The transition identity must bind at least:

- predecessor generation/root id;
- last common authenticated floor;
- canonical sorted digest set of every known conflicting head;
- conflict-set observation cutoff/window;
- successor generation/root id and key generation;
- policy generation;
- unique transition id / monotonic sequence;
- freshness/expiry semantics;
- coauthorization/quorum identity.

A root/key rollover after compromise is a successor event; it cannot mutate or delete the historical fact that the prior generation was equivocated or compromised.

### Decision

Introduce three explicit states/events in later executable design:

- `EQUIVOCATED(conflict_set_digest, known_count, observation_cutoff)`;
- `ADJUDICATED_RECOVERY(predecessor, successor, full_known_conflict_set_digest, last_common_floor, transition_id)`;
- `SUCCESSOR_ROOT_REKEY(predecessor_successor_root, new_root, compromise_boundary, transition_id)`.

Unknown-conflict risk remains metadata/evidence, not silently collapsed to `CLEAN`.

## 2. Flaky reducers: multiple-candidate and sequential-selection bias

### Problem

A reducer often evaluates many candidate simplifications and keeps whichever candidate reproduces the target failure most convincingly. If each candidate is tested until a convenient success/failure threshold and the search adaptively chooses the best-looking candidate, the selected candidate's apparent reproduction rate is biased upward. Running a sequential stopping rule per candidate does not remove the bias introduced by searching/selecting across many candidates.

### Derived boundary

`PER_CANDIDATE_STOPPING_RULE_VALID != SELECTED_CANDIDATE_INFERENCE_VALID`.

And:

`BEST_OBSERVED_REPRODUCER != MOST_FAITHFUL_CAUSAL_REPRODUCER`.

The runtime does not need to become a general statistical package, but the security evidence must distinguish search from confirmation.

### Decision

For flaky/security delta debugging:

1. Freeze the target security predicate and admissible environment/event-order envelope before candidate search.
2. During adaptive search, treat reproduction scores only as *ranking evidence*.
3. After selection, run a fresh confirmation phase with a predeclared independent seed stream/trial budget and no candidate replacement based on those confirmation outcomes.
4. Record number of candidates evaluated, search budget, selection rule, confirmation budget and all stopping conditions.
5. A candidate that changes failure class/security predicate is a new finding, not a successful reduction.
6. If confirmation does not meet the predeclared reproduction criterion, classify `SELECTED_BUT_NOT_CONFIRMED` rather than silently resuming search with the same evidence budget.

This preserves the earlier `ZERO_FAILURES_OBSERVED != ZERO_FAILURE_PROBABILITY` rule while adding a separate selection-bias boundary.

## 3. Privacy escrow: reclaiming orphaned transfers without double ownership

### Facts / donor mechanism

NIST SP 800-226 defines privacy budget as an upper bound on cumulative privacy loss across analyses and explains that repeated interactive queries incur additional loss that counts against the total budget. Composition is therefore global to the protected dataset/subject semantics; accounting cannot legitimately create capacity merely because distributed bookkeeping is uncertain.

### Failure case

Region A irreversibly debits escrow slice X and sends transfer X to region B. B may have durably accepted/credited X, but the acknowledgement is lost during a partition. A sees an old local record saying `TRANSFER_UNKNOWN` and later wants to reclaim X.

Naive reclamation can produce two simultaneous owners if B actually credited X. Conversely, permanently burning every ambiguous transfer can cause unbounded availability loss.

### Boundary

`TRANSFER_ACK_MISSING != DESTINATION_CREDIT_ABSENT`.

`ORPHAN_TIMEOUT_EXPIRED != SAFE_TO_RECLAIM`.

### Decision

Reclamation must be a successor protocol over the immutable transfer id:

- transfer state machine: `AVAILABLE -> DEBIT_RESERVED -> DEBIT_IRREVOCABLE -> CREDITED | TRANSFER_UNKNOWN`;
- an orphaned slice is never directly returned to source `AVAILABLE`;
- recovery obtains either (a) authenticated destination non-credit proof at a freshness/epoch boundary, or (b) an authenticated global reconciliation decision that fences destination spend authority for that transfer before source re-credit;
- destination must reject duplicate credit for a transfer id already finalized/revoked;
- source re-credit creates a new allocation generation linked to the retired transfer, never resurrects the original allocation token;
- any disclosure whose egress may have happened remains charged/unknown and cannot be reclaimed as unused privacy loss.

This permits eventual availability recovery without ever allowing two spend authorities for one privacy-budget slice.

## 4. Retention receipts: omission-proof and coverage guarantees

### Facts / donor mechanism

RFC 9162 inclusion proofs can establish that a particular committed item is included in a particular authenticated Merkle root, while consistency proofs can establish append-only growth between roots. These are positive membership/append-only proofs; they do not by themselves prove that no event was omitted before the log commitment was formed.

### Boundary

`RECEIPT_INCLUSION_PROVEN != EVENT_COVERAGE_COMPLETE`.

`NO_RECEIPT_FOUND != NO_DESTRUCTIVE_EVENT_OCCURRED`.

Independent receipts for retention/deletion decisions therefore need a coverage contract, not just cryptographically valid individual receipts.

### Decision

A retention receipt stream that is used to reconcile a degraded interval must bind:

- source/event sequence or monotonic operation id;
- covered interval `[start_seq, end_seq]` or authenticated predecessor/successor boundary;
- explicit event count or gap-free sequence commitment;
- receipt class and destructive/non-destructive semantics;
- signer identity/key generation;
- storage/log root and inclusion proof where applicable;
- independent failure-domain metadata;
- checkpoint/finalization root.

To claim `RECONCILED`, every authority capable of destructive action during the degraded interval must either:

1. provide a gap-free authenticated event sequence covering that interval; or
2. be independently fenced from destructive authority for the whole interval with evidence of that fence.

If any sequence gap, unaccounted writer, or unverifiable omission remains, state stays `UNRESOLVED_DEGRADED` even if every *present* receipt is valid.

## 5. PQ/ECH/TLS: ticket ancestry lifetime, late-edge admission, descendant-ticket revocation

### Facts / donor mechanisms

RFC 8446 limits `NewSessionTicket.ticket_lifetime` to at most 604800 seconds (7 days), allows shorter server policy, derives a distinct PSK from each ticket nonce, and warns that repeatedly issuing new tickets could otherwise extend keying material from an original authenticated handshake indefinitely. It recommends bounding total lifetime of that ancestry with certificate lifetime/revocation and time since the online CertificateVerify signature in mind.

RFC 8446 also requires the application-visible SNI on resumption to come from the resumption ClientHello; a server can reject PSK identities that are inconsistent with current SNI policy.

RFC 9849 states that an ECH-rejection/public-name-authenticated connection does not authenticate the origin and its session tickets/session IDs must be ignored; it is retry machinery only.

### Boundaries

`CHILD_TICKET_IS_FRESH != TICKET_ANCESTRY_IS_CURRENT`.

`TICKET_WITHIN_7_DAYS != INCIDENT_POLICY_AUTHORIZES_RESUMPTION`.

`LATE_EDGE_DECRYPTS_TICKET != LATE_EDGE_HAS_CURRENT_REVOCATION_FLOOR`.

`ECH_RETRY_CONNECTION_AUTHENTICATED_FOR_PUBLIC_NAME != ORIGIN_RESUMPTION_AUTHORITY`.

### Decision

Every resumption ticket generation used by this runtime should carry or map to an authenticated ancestry record containing at minimum:

- original full-handshake/authentication generation;
- parent ticket generation/id or ancestry root;
- issuance time and policy-effective expiry;
- current certificate/server identity generation;
- SNI/inner-service binding and ALPN;
- ECH configuration/policy generation where ECH is required;
- PQ/hybrid policy generation/floor;
- backend/route authority generation;
- ticket-key generation;
- revocation generation;
- replay/0-RTT authority generation.

A child ticket cannot reset the maximum ancestry lifetime. Runtime policy should calculate effective expiry as the minimum of protocol ticket expiry, local ticket policy, ancestry-root lifetime, certificate/identity constraints, and incident/revocation boundaries.

Descendant-ticket revocation propagates by generation/floor, not by enumerating only tickets known at the incident coordinator. If ancestry root or ticket-key generation G is revoked at revocation floor R, any child/descendant whose authority transitively depends on G and predates R is rejected even if the child ticket decrypts and has a later nominal expiry.

A late/rejoining edge enters `RESUMPTION_QUARANTINED`. Before accepting 1-RTT PSK resumption it must prove current ticket-key/revocation/identity/ECH/PQ/backend policy floors. Before accepting 0-RTT it must additionally prove current replay/spend authority. Unknown/stale floor means fail closed for the affected resumption class; a full fresh handshake may remain available under current policy.

## Frozen RED-first matrix (40 cases)

### A. Checkpoint conflict-set / successor-root (A1-A8)

A1. Two conflicting authenticated heads are known; adjudication commits to both -> accept successor only if canonical conflict-set digest includes both.
A2. Three conflicts are known but adjudication lists two -> reject as incomplete known conflict set.
A3. Conflicting head discovered after adjudication -> preserve original adjudication, append `LATE_CONFLICT_DISCOVERED`, require successor reconciliation; never rewrite history.
A4. Later larger quorum signs one old conflicting head -> old generation remains `EQUIVOCATED`.
A5. Replay old valid adjudication transition id against a newer predecessor state -> reject.
A6. Successor-root key compromised; attacker signs fresh-looking re-adjudication without valid recovery bridge -> reject.
A7. Legitimate successor-root rekey references compromise boundary and prior adjudication digest -> accept without cleaning predecessor history.
A8. Conflict-set order changes but members equal -> canonical sorted-set digest remains stable; duplicate/member substitution changes digest and is rejected.

### B. Sequential/multiple-candidate reducer selection (B1-B8)

B1. Search 100 candidates; one passes a weak reproduction threshold by chance -> search score may rank it, but it is not confirmed.
B2. Selected candidate fails independent confirmation budget -> classify `SELECTED_BUT_NOT_CONFIRMED`.
B3. Candidate replacement after observing confirmation failures -> reject evidence as confirmation/search contamination.
B4. Search and confirmation share deterministic seed sequence -> reject independence claim.
B5. Candidate reproduces crash but not the frozen security predicate -> classify new finding, not reduction success.
B6. Rare-event predicate absent in finite confirmation budget -> `NOT_OBSERVED_UNDER_BUDGET`, not `ABSENT`.
B7. Environment/event-order envelope widened only for selected candidate after results -> reject as post-selection rule change.
B8. Fresh confirmation meets predeclared criterion under independent seeds and same predicate -> accept minimized witness with recorded candidate-count/search budget.

### C. Privacy escrow orphan reclamation (C1-C8)

C1. Source debit irreversible, destination credit confirmed -> source cannot reclaim.
C2. Source debit irreversible, destination non-credit proof fresh and authenticated -> recovery may create successor allocation at source after fencing transfer id.
C3. Ack lost and destination unreachable -> remain `TRANSFER_UNKNOWN`; no source re-credit.
C4. Destination credited before partition, source receives stale pre-credit non-credit proof -> reject due epoch/freshness mismatch.
C5. Reconciliation fences destination spend, then re-credits source in new allocation generation -> accept.
C6. Destination later receives original transfer after it was globally retired -> reject duplicate credit by immutable transfer id/revocation generation.
C7. Egress may have occurred but commit record unknown -> privacy loss remains charged/unknown; no unused-budget reclamation.
C8. Subject/delegation identity changes during orphan recovery -> transfer ownership follows logical protected budget identity, not credential name.

### D. Retention receipt omission/coverage (D1-D8)

D1. Every present receipt verifies but sequence 41 is missing -> cannot mark interval reconciled.
D2. Gap is covered by independent proof writer lacked destructive authority during that exact interval -> gap may be closed.
D3. Receipt inclusion proof valid against authenticated root -> proves membership, not completeness; require coverage metadata.
D4. Two receipt logs share same compromised operator/control plane -> do not count as independent coverage domains.
D5. Destructive writer existed but produced no receipts and has no fence evidence -> `UNRESOLVED_DEGRADED`.
D6. Gap-free sequence and event count cover all capable writers -> allow reconciliation if signatures/roots are current.
D7. Sequence restarts after restore without authenticated recovery epoch -> reject apparent gap-free coverage across restart.
D8. Late receipt for previously unresolved destructive event arrives with valid inclusion and lineage -> append evidence and recompute reconciliation; never delete prior uncertainty record.

### E. PQ/ECH ticket ancestry / late edge / descendant revocation (E1-E8)

E1. Child ticket freshly issued from parent whose ancestry root exceeded runtime max lifetime -> reject child resumption.
E2. Ticket nominally within 7 days but revocation generation advanced after incident -> reject affected ticket.
E3. Parent ticket revoked; child minted before revocation but expires later -> child rejected by ancestry floor.
E4. New full authenticated handshake after incident mints ticket under new ancestry/revocation generation -> may accept according to current policy.
E5. Late edge can decrypt old ticket but has stale revocation floor -> quarantine/reject resumption.
E6. Late edge has current 1-RTT floors but replay state unknown -> allow policy-valid full/1-RTT path, keep 0-RTT disabled.
E7. ECH rejection connection authenticates only `public_name` and supplies session ticket -> ignore ticket for origin authority as required by RFC 9849.
E8. Resumption ticket has current cryptographic key but stale SNI/inner service, ECH, PQ, backend or ALPN generation -> reject PSK/resumption and require fresh policy-valid handshake.

## Audit

- No claim here depends on GitHub Actions or background workers.
- No LAB-086 executable test result is inferred from source inspection or standards research.
- RFC mechanisms are used as donor invariants, not as claims that CT/TLS/DP standards directly specify this runtime's private state machine.
- The conflict-set design deliberately distinguishes known completeness from universal completeness.
- The reducer design separates adaptive search from confirmation to avoid turning search success into false statistical confidence.
- Privacy reclamation never creates a second simultaneous spend authority.
- Receipt verification is separated from omission/coverage guarantees.
- Ticket validity is separated from ancestry, incident, route/service, ECH/PQ and replay authorization.

## Next engineering step when exact execution is available

Return to LAB-086 first and execute the retained byte-exact gate. Once the pending executable line clears, translate these frozen cases into tests before production implementation in the relevant LAB-093+ follow-up surface. Until then this contract is research/evidence only.