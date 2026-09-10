# Conflict gossip, post-selection holdout, privacy reconciliation replay, retention writer inventory, and PQ/ECH ticket rotation — v1

Date: 2026-09-10
Status: DESIGN FROZEN / RED-FIRST
Parent: LAB-093/#178
Execution note: LAB-086 exact executable gate remains priority #1. In this run direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`; no new LAB-086 behavioral/compile/security PASS is claimed.

## Frozen contract

`CONFLICT_NOT_GOSSIPED != CONFLICT_DID_NOT_EXIST`

`SUCCESSOR_COSIGNED != OBSERVER_UNIVERSE_COMPLETE`

`HOLDOUT_WAS_UNUSED_ONCE != HOLDOUT_REMAINS_INDEPENDENT_AFTER_REUSE`

`RECONCILIATION_ROOT_VALID != ORPHAN_RECLAMATION_AUTHORITY_CURRENT`

`WRITER_NOT_IN_INVENTORY != WRITER_COULD_NOT_MUTATE`

`NEW_CERT_OR_PQ_POLICY_ACTIVE != OLD_TICKET_ANCESTRY_REAUTHORIZED`

`REGION_LOCAL_REVOCATION_FLOOR_CURRENT != GLOBAL_RESUMPTION_FLOOR_CONVERGED`

## 1. Censored / gossip-partitioned conflict discovery and adjudication co-signing

### Donor boundary
RFC 9162 requires checking consistency of the log view presented to query sources, but explicitly says this is difficult because it requires sharing responses among CT-using entities; gossip is not specified by the RFC. Inclusion/consistency proofs establish properties relative to observed signed tree heads, not universal visibility of all signed heads.

### Decision
A successor adjudication MUST distinguish:

- `known_conflict_set`: canonical digests of all conflicting heads admitted before an authenticated observation cutoff;
- `observer_set`: identities/failure domains whose views were solicited;
- `missing_observers`: expected observers without fresh authenticated response;
- `cutoff`: monotonic/adjudication epoch, not wall-clock alone;
- `common_floor`: last authenticated predecessor state common to every admitted head;
- `cosigners`: successor authorities attesting only to this exact package.

A valid successor quorum proves agreement on the package above. It MUST NOT be interpreted as proof that no censored or partition-hidden head exists.

A later authenticated conflicting head is appended as `LATE_CONFLICT_DISCOVERED`; it does not retroactively make the earlier package fraudulent if that package accurately committed to its observation universe and cutoff. It does reopen finality for any policy that required universal/qualified observer coverage.

If an observer or successor signer is compromised, replay of an old cosignature over a different conflict set/cutoff is invalid because the signature payload binds the full canonical package plus membership/key generation and transition id.

## 2. Post-selection inference and holdout reuse boundaries for flaky reducers

Adaptive search is discovery/ranking evidence. Confirmation is a separate phase.

For candidate C selected after adaptive trials:

1. freeze candidate bytes/config, security predicate, environment/fault envelope and decision rule;
2. allocate a fresh confirmation sample budget not inspected during search;
3. record every confirmation attempt including timeouts/inconclusive outcomes;
4. report only the predeclared confirmation decision;
5. if confirmation data is then used to modify or rank a new candidate, that data becomes training/search evidence and is no longer an independent holdout for the modified candidate.

`PASS_ON_REUSED_HOLDOUT != INDEPENDENT_CONFIRMATION_PASS`.

Repeatedly testing candidates on the same finite holdout creates selection leakage even if each candidate individually has a valid stopping rule. Reuse is permitted only under an explicitly budgeted reusable-validation mechanism whose guarantee is itself part of the evidence; absent that, allocate a new independent holdout generation.

Rare-event failures are preserved as `NOT_OBSERVED_UNDER_BUDGET` when absent during finite confirmation; they are not converted into `IMPOSSIBLE`.

## 3. Privacy orphan-reclamation authority compromise and reconciliation-root replay

NIST SP 800-226 defines privacy budget as an upper bound on cumulative privacy loss. Therefore an orphaned escrow reservation cannot be reclaimed merely because a destination acknowledgement is missing.

Frozen state machine:

`RESERVED_SOURCE_DEBITED -> DESTINATION_CREDIT_PROVEN | DESTINATION_NONCREDIT_PROVEN | TRANSFER_UNKNOWN`.

Reclamation requires either:

- a current authenticated non-credit proof from the destination authority for the transfer id and epoch; or
- fencing/revoking every destination authority able to credit that transfer, followed by a successor reconciliation root covering the fenced universe.

A reconciliation root binds transfer ids, cumulative charged/unknown spend, membership/key generation, predecessor root, and fencing evidence. Replaying an old valid reconciliation root after membership/key/policy rotation is rejected even if all signatures still verify cryptographically.

Compromise of the reclamation signer cannot mint budget: reclamation authority is conjunctive with destination non-credit/fencing evidence and monotonic cumulative-spend lineage.

`OLD_RECONCILIATION_SIGNATURE_VALID != CURRENT_RECLAMATION_AUTHORITY`.

## 4. Retention writer-inventory completeness across membership changes

Receipt inclusion cannot prove omission-free history unless the verifier knows the complete set of authorities that could have performed destructive mutation during the interval.

Each retention epoch MUST commit to a canonical writer inventory containing at least:

- writer/capability identity;
- mutation classes authorized;
- key/capability generation;
- activation and revocation/fence positions;
- failure/control-plane domain;
- predecessor/successor membership transition digest.

A membership transition is not complete until every removed writer is fenced/revoked and every added writer is bound to the successor inventory before use.

`WRITER_MISSING_FROM_CURRENT_CONFIG != WRITER_FENCED_FOR_HISTORICAL_INTERVAL`.

Reconciliation may claim `COMPLETE` only when every destructive-capable writer for the interval has either gap-free authenticated receipts or independent authenticated evidence proving it could not mutate for each uncovered range. Discovery of a previously omitted writer downgrades affected intervals to `INVENTORY_INCOMPLETE` and reopens reconciliation.

## 5. PQ/ECH ticket ancestry after certificate/PQ-policy rotation

TLS resumption PSKs are derived from a prior handshake. RFC 8446/8446bis notes that repeated issuance can indefinitely extend keying material ancestry and recommends bounding total lifetime with certificate lifetime, revocation likelihood and time since an online CertificateVerify signature in mind. The current TLS 1.3 revision also requires clients to resume only when the new SNI is valid for the certificate from the original session and limits individual ticket use to at most seven days.

Frozen runtime policy is stricter than protocol validity:

A ticket/descendant lineage records immutable ancestry floors for:

- original full-handshake identity/certificate generation;
- PQ/hybrid policy generation and negotiated mode;
- ECH config source/generation where applicable;
- backend/service authorization generation;
- ticket-key generation;
- revocation floor;
- replay-state generation for 0-RTT;
- absolute ancestry expiry independent of descendant ticket issue times.

`DESCENDANT_ISSUED_AFTER_ROTATION != DESCENDANT_ANCESTRY_RESET`.

After certificate or PQ policy rotation, an old lineage MAY be rejected immediately by local policy even if the underlying TLS library could cryptographically resume it. If authorization-relevant policy changed, resumption authority must be reevaluated; if a safe decision cannot be made, perform a full handshake.

ECH rejection/public-name authenticated connections never authorize origin resumption and all tickets/session IDs from them are ignored, per RFC 9849.

## 6. Cross-region revocation-floor divergence and late descendant issuance

A region MAY accept 1-RTT/full handshakes while its resumption state is quarantined.

To accept PSK resumption, the region must prove:

- current service/backend/identity policy floor;
- current ticket-key and ancestor revocation floor;
- current certificate/PQ/ECH admission policy;
- no local issuance after its acknowledged revocation floor was stale.

For 0-RTT, current replay authority is additionally required.

A region that continues issuing descendant tickets while behind the revocation floor creates tainted descendants. Later convergence does not cleanse those tickets; all descendants whose issuance ancestry intersects the stale interval are invalidated.

`REGION_CAUGHT_UP_NOW != TICKETS_ISSUED_WHILE_STALE_BECAME_SAFE`.

Cross-region global convergence is a set of authenticated acknowledgements from every currently eligible spend/issuance authority, bound to one revocation generation and membership inventory. Missing eligible regions keep resumption fail-closed unless independently fenced.

## RED-first matrix — 40 cases

### A. Conflict gossip / adjudication (8)
1. Two observers see head A; partitioned observer saw incompatible B before cutoff -> package cannot claim universal completeness.
2. Missing observer explicitly recorded -> qualified package valid but marked incomplete.
3. Late B appears after honest cutoff -> append `LATE_CONFLICT_DISCOVERED`, preserve prior evidence, reopen required finality.
4. Successor quorum signs A-only package while known B omitted -> reject canonical package.
5. Replay old cosignature over new cutoff -> reject.
6. Replay old cosignature after membership/key generation change -> reject.
7. Same conflicting heads in different input order -> canonical package digest identical.
8. Compromised observer supplies unverifiable head -> reject head without letting it erase valid conflicts.

### B. Flaky reducer / post-selection (8)
9. Search selects best of 100 candidates; same trials reused as confirmation -> not independent confirmation.
10. Fresh frozen-candidate holdout meets predeclared rule -> confirmation admissible.
11. Holdout result used to edit candidate, then same holdout rerun -> holdout generation burned.
12. Candidate times out; timeout excluded post hoc -> reject evidence accounting.
13. Rare event absent in finite holdout -> `NOT_OBSERVED_UNDER_BUDGET`, not zero probability.
14. Candidate fails by a different predicate during confirmation -> new finding, original predicate not confirmed.
15. Environment/fault envelope changes between search and confirmation -> incomparable evidence.
16. Independent new holdout generation after modification -> admissible if frozen before observation.

### C. Privacy orphan / reconciliation (8)
17. Destination ack missing, destination still live -> no reclamation.
18. Current non-credit proof for exact transfer id/epoch -> reclaim in successor allocation generation.
19. Destination fenced after partition, all credit-capable replicas covered -> reconciliation may reclaim.
20. One forgotten destination replica remains credit-capable -> `TRANSFER_UNKNOWN`.
21. Old reconciliation root replayed after destination membership rotation -> reject.
22. Reclamation signer compromised but no non-credit/fence proof -> cannot mint budget.
23. Destination may have disclosed before crash -> spend remains charged/unknown even after reclamation fencing.
24. Same transfer id replayed -> idempotent, no second credit or source refund.

### D. Retention writer inventory (8)
25. Removed writer absent from current config but not fenced historically -> interval incomplete.
26. Removed writer has authenticated fence before interval -> omission can be ruled out for later range.
27. Added writer mutates before successor inventory commits it -> fail closed / invalid epoch transition.
28. Gap-free receipts from listed writers but hidden destructive writer discovered -> downgrade reconciliation.
29. Writer identity rotates key without membership transition -> old/new receipts cannot be silently merged.
30. Writer loses receipt storage but independent fence covers exact gap -> completeness can remain provable.
31. Membership inventories reorder entries only -> canonical digest stable.
32. Writer capability expands mutation classes without new inventory generation -> reject destructive use.

### E. PQ/ECH ticket ancestry / regional divergence (8)
33. Certificate rotates; old-lineage ticket still cryptographically decrypts -> runtime may reject and require full handshake.
34. PQ floor increases; non-PQ ancestor issues fresh descendant -> descendant remains below floor and is rejected.
35. Fresh descendant ticket has issue time after rotation but ancestry crosses stale predecessor -> reject.
36. ECH public-name rejection handshake yields ticket -> ignore ticket for origin resumption.
37. Region R1 current, R2 stale but still eligible -> global resumption convergence not reached.
38. R2 fenced before convergence -> remaining eligible-region acknowledgements can satisfy floor.
39. R2 issued descendants while stale then catches up -> stale-window descendants remain revoked.
40. 1-RTT/full handshake allowed after recovery while replay authority not current -> 0-RTT remains disabled.

## Implementation requirements for future RED/GREEN

- Tests first; preserve exact frozen predicates above.
- Canonical serialization must be deterministic and bind membership/key/policy generations.
- Never infer global observer/writer completeness from currently reachable nodes alone.
- Never let a fresh descendant ticket reset absolute ancestry or incident floors.
- Keep 1-RTT/full-handshake recovery separate from 0-RTT re-enable.
- All fail-open proposals require an explicit security proof and separate issue; default is fail closed.

## Primary sources / donors

1. RFC 9162, Certificate Transparency Version 2.0 — log-view consistency and the explicit limitation that cross-entity gossip is required and not specified by the RFC: https://www.rfc-editor.org/rfc/rfc9162.html
2. NIST SP 800-226 / NIST privacy-budget glossary — privacy budget is an upper bound on cumulative privacy loss: https://csrc.nist.gov/glossary/term/privacy_budget
3. RFC 8446, TLS 1.3 — resumption PSK ancestry, SNI/certificate constraints, seven-day ticket maximum, and recommendation to bound total lifetime of repeatedly refreshed keying material: https://www.rfc-editor.org/rfc/rfc8446.html
4. RFC 9846, current TLS 1.3 revision — resumption PSK transcript ancestry and current forward/recovery security guidance: https://www.rfc-editor.org/rfc/rfc9846.html
5. RFC 9849, Encrypted Client Hello — public-name authentication is not origin authentication; retry connections' session tickets/session IDs must be ignored; persisted ECH state is scoped to its ECHConfig source: https://www.rfc-editor.org/rfc/rfc9849.html
6. RFC 9813 — operational donor for reevaluating authorization/policy at resumption when original-session information may have changed; full handshake if a safe decision is not possible: https://www.rfc-editor.org/rfc/rfc9813.html

## Frozen result

`CONFLICT_GOSSIP_HOLDOUT_PRIVACY_REPLAY_RETENTION_INVENTORY_PQ_TICKET_ROTATION_V1_FROZEN`

This is a design/evidence freeze only. It does not substitute for executable RED/GREEN proof.