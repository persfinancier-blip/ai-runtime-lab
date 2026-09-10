# Observer churn, holdout provenance roots, privacy scope, retention proxy fences, and PQ/ECH ticket retirement v1

Date: 2026-09-10
Status: DESIGN FROZEN / RED-FIRST; executable proof still required
Parent: LAB-093/#178 and frozen LAB-094..100 follow-ups
Priority note: LAB-086/#163 remains priority #1; this slice is the recorded fallback while exact-source execution is unavailable.

## Why this slice exists

The previous contracts established observer recovery epochs, holdout exposure lineage, monotonic privacy spend floors, resource-side destructive fences, and staged TLS/PQ/ECH recovery. This slice closes five remaining laundering paths that appear when authority is *repartitioned* rather than simply rotated:

1. observer recovery-authority membership churn can make a compromised quorum look independent again if overlap is measured only by member IDs;
2. holdout datasets/generators can be rolled back or re-derived under fresh identifiers while preserving the same leaked information;
3. privacy spend-witness scopes can be split or merged and accidentally reset local floors;
4. retention execution can be delegated through a proxy/job runner whose own fence generation rolls back independently of the resource;
5. TLS ticket keys can survive certificate/DC replacement, allowing old ancestry to remain spendable after identity recovery unless retirement is explicit and regionally converged.

## Frozen contract

`OBSERVER_CHURN_HOLDOUT_ROOT_PRIVACY_SCOPE_RETENTION_PROXY_PQ_TICKET_RETIREMENT_V1_FROZEN`

### A. Observer recovery-authority churn and compromise overlap

Core distinctions:

- `NEW_MEMBER_IDS != NEW_FAILURE_DOMAINS`
- `NEW_RECOVERY_EPOCH != INDEPENDENT_RECOVERY_AUTHORITY`
- `MEMBER_REMOVED != PRIOR_COMPROMISE_REMOVED_FROM_HISTORY`
- `THRESHOLD_MET != MINIMUM_INDEPENDENT_DOMAIN_THRESHOLD_MET`

Each observer/recovery member carries a stable `authority_lineage_id` and a declared failure-domain vector (operator, credential root/HSM, control plane, storage/log, network/admin domain). Recovery admission computes overlap against the compromised/degraded interval, not merely against the current member list.

A successor recovery epoch is admissible only if:

1. it commits to the predecessor epoch, last uncontested checkpoint, complete known conflict set at the authenticated cutoff, and degraded interval;
2. it satisfies both signer threshold and `min_independent_domains` under the new policy;
3. members whose authority lineage intersects the compromise set do not count as independent replacement domains solely because keys, names, pods, accounts, or machines changed;
4. emergency members have explicit expiry and cannot silently become permanent by ordinary membership churn;
5. removal of a member never removes evidence already signed/observed by that member.

RFC 9162 is the donor for the distinction between authenticated views and global consistency: conflicting signed tree views are misbehavior evidence, while consistency across all query sources requires sharing observations and is not provided by one valid view alone. RFC 5011 is a donor for explicit successor trust-anchor admission/revocation semantics: compromise recovery is a state transition, not a rename of the old authority.

### B. Attestable holdout-provenance roots and generator rollback

Core distinctions:

- `NEW_DATASET_HASH != NEW_INFORMATION`
- `GENERATOR_VERSION_ROLLED_BACK != HOLDOUT_EXPOSURE_ROLLED_BACK`
- `SYNTHETIC_CHILD != INDEPENDENT_CHILD`
- `PROVENANCE_ROOT_SIGNED != PROVENANCE_ROOT_CURRENT`

Every reusable-holdout decision binds to an immutable provenance root containing at least:

- source dataset content identities / source epochs;
- split algorithm and randomness commitment;
- generator/model/checkpoint identity and training-input lineage;
- analyst/controller identity lineage;
- all prior holdout disclosures relevant to that candidate family;
- mechanism/policy generation, query/exposure counters, and confirmation-generation;
- monotonic provenance generation or external freshness anchor.

A generator rollback may recreate byte-different synthetic data while still depending on prior holdout feedback. Therefore derived data inherits exposure lineage unless an independently justified transformation proves an information-separation guarantee. Replaying an old, correctly signed provenance root after later holdout exposure is stale and cannot restore unused exposure budget.

The reusable-holdout literature is the donor for the core risk: adaptively choosing later analyses based on earlier holdout results can overfit the holdout itself; safe reuse depends on controlling information returned to the adaptive analyst, not on renaming datasets or models.

### C. Privacy spend-witness scope split/merge without floor laundering

Core distinctions:

- `SCOPE_SPLIT != BUDGET_MULTIPLICATION`
- `SCOPE_MERGE != FLOOR_MINIMUM`
- `NEW_SCOPE_ID != FRESH_PRIVACY_HISTORY`
- `WITNESS_ROTATED != UNRESOLVED_SPEND_DISAPPEARED`

Each privacy accounting scope has a canonical semantic coverage set (subjects/population, purpose/query family, release channel, jurisdiction/policy domain as applicable), not only a string identifier.

Split rule:

- a parent scope may split only through a signed allocation transition that conserves the parent's remaining budget;
- child budgets are explicit partitions/escrows of parent capacity and their sum cannot exceed the parent available capacity;
- all parent charged/unknown spend remains in ancestry and cannot be allocated again.

Merge rule:

- the merged scope's cumulative floor is at least the composition required by all predecessor scopes plus unresolved reservations/transfers/unknown disclosure;
- overlapping semantic coverage is reconciled conservatively; it is never resolved by taking the minimum local floor;
- merge requires authenticated predecessor set completeness and fences superseded scopes from future spend.

A scope rename, subject regrouping, sharding change, or witness rotation never resets cumulative privacy loss. NIST SP 800-226 is the donor for treating privacy budget/loss as a cumulative composition quantity rather than a per-process counter.

### D. Retention resource-proxy/delegated-fence rollback and destructive retry fencing

Core distinctions:

- `PROXY_FENCE_CURRENT != RESOURCE_FENCE_CURRENT`
- `RESOURCE_FENCE_CURRENT != DELEGATION_CURRENT`
- `JOB_IDEMPOTENCY_KEY_SEEN != DESTRUCTIVE_EFFECT_KNOWN`
- `RETRY_AFTER_TIMEOUT != SAFE_TO_REAUTHORIZE`

A destructive operation may pass through control plane -> proxy/job runner -> resource. Every hop must carry a monotonic generation chain:

`policy_generation -> delegation_generation -> proxy_fence_generation -> resource_fence_generation -> operation_id`.

Rules:

1. the resource validates the complete current chain at execution time; validating only the proxy's local lease is insufficient;
2. rollback/restart of a proxy cannot reduce the resource's accepted fence floor;
3. offline/queued jobs reauthorize immediately before destructive execution and are rejected if any generation is stale/unknown;
4. timeout after dispatch produces `EFFECT_UNKNOWN`; the same operation id is reconciled before any successor destructive authorization is created;
5. a retry may be idempotent only if the resource itself can prove the prior operation's exact effect/result under the same immutable operation id;
6. revocation acknowledgements from intermediaries do not prove the resource can no longer spend the delegated capability.

### E. PQ/ECH ticket-key retirement/re-encryption after certificate/DC replacement

Core distinctions:

- `CERTIFICATE_REPLACED != OLD_TICKET_KEY_RETIRED`
- `DC_EXPIRED_OR_REPLACED != DESCENDANT_TICKET_ANCESTRY_CURRENT`
- `TICKET_REENCRYPTED != TICKET_REAUTHORIZED`
- `REGION_HAS_NEW_KEY != REGION_REJECTS_OLD_ANCESTRY`

TLS 1.3 tickets are bearer-like resumption artifacts governed by server policy. Re-encrypting or wrapping a ticket under a new storage/encryption key does not change the authenticated ancestry that originally authorized resumption.

After certificate, delegated credential, PQ identity, ECH config, service-equivalence policy, or backend authority replacement:

1. ticket admission policy advances a monotonic ancestry generation;
2. old ticket-decryption keys are explicitly retired/fenced; mere certificate/DC replacement is insufficient;
3. descendant tickets inherit the oldest still-security-relevant ancestry floor and cannot refresh it away by repeated resumption;
4. re-encryption preserves ancestry metadata and cannot transform a stale ticket into a current ticket;
5. every eligible region/edge must acknowledge the new admission/revocation floor before PSK resumption is considered converged;
6. a late region rejoins in resumption quarantine until it proves current key-retirement, revocation, identity/ECH/PQ/backend and replay floors;
7. 1-RTT full authentication may be restored earlier than PSK resumption; 0-RTT remains stricter because replay state is additionally required.

RFC 9345 is the donor for delegated-credential validity and resumption: cached DC state should be revalidated on resumption, and DC expiry/revocation semantics do not disappear because a ticket remains decryptable. RFC 8446 is the donor for bounded ticket lifetime and for the fact that repeated ticket issuance can otherwise extend keying-material lifetime; implementations may enforce shorter server-side validity.

## RED-first matrix (40 cases)

### Observer recovery authority (O1-O8)

O1. Replace compromised members with new keys on the same HSM/admin domain -> must not count as independent-domain recovery.
O2. Rename operator accounts and pods but retain same control-plane root -> independence must not increase.
O3. Genuine new signer domains satisfy signer threshold but not minimum independent-domain threshold -> recovery rejected.
O4. New domains satisfy both thresholds and commit predecessor/conflict/degraded evidence -> recovery accepted.
O5. Emergency member expires -> loses future voting authority; its historical evidence remains valid.
O6. Remove a member that observed a conflicting head -> conflict evidence remains in successor root.
O7. Replay an older recovery epoch after later compromise evidence -> rejected as stale.
O8. Partial compromise overlaps only one new domain -> only the non-overlapping domains count toward independence.

### Holdout provenance (H1-H8)

H1. Copy holdout rows into a new file with new dataset ID -> exposure lineage preserved.
H2. Train a synthetic generator using prior holdout feedback, then validate on its output -> not independent by default.
H3. Roll generator checkpoint back before the feedback event but keep controller state learned from feedback -> lineage remains exposed.
H4. Roll both generator and controller artifacts back but replay an old signed provenance root below monotonic generation -> rejected stale.
H5. Independent source dataset with no information/provenance overlap -> may start fresh confirmation generation.
H6. Reveal ranking of candidates instead of pass/fail bit -> charged according to stronger disclosure mechanism, not one-bit semantics.
H7. Analyst identity renamed while same controller state persists -> exposure budget not reset.
H8. Provenance root includes all ancestors but omits one prior disclosure -> completeness verification fails closed.

### Privacy scope split/merge (P1-P8)

P1. Split parent remaining budget 10 into children 6+6 -> rejected.
P2. Split 10 into 4+6 under one authenticated transition -> accepted; parent fenced.
P3. Parent has unresolved possible disclosure before split -> uncertainty carried into children/ancestry before allocation.
P4. Merge two disjoint scopes -> merged accounting composes both predecessor floors.
P5. Merge partially overlapping scopes -> conservative overlap reconciliation required; minimum local floor forbidden.
P6. Rename one child scope after spending -> spend floor follows semantic scope lineage.
P7. Replay pre-spend split transition -> monotonic successor check rejects.
P8. Merge predecessor set omits a still-spendable child -> merge rejected until child is included/fenced.

### Retention proxy/resource fencing (R1-R8)

R1. Proxy restarts with fence generation 3 while resource floor is 5 -> destructive execution rejected.
R2. Proxy fence current but delegation revoked -> rejected at resource.
R3. Delegation current but resource fence stale/unknown -> rejected.
R4. Offline job created under generation 7 executes after policy generation 8 -> reauthorization rejects.
R5. Timeout after resource may have deleted -> state EFFECT_UNKNOWN; no fresh destructive authorization yet.
R6. Retry same operation id and resource proves exact prior completed effect -> idempotent result may be returned without second effect.
R7. Retry uses new operation id after unknown prior effect -> rejected until reconciliation.
R8. Intermediary ACKs revocation but resource never acknowledged/fenced -> capability remains unresolved, not declared unspendable.

### PQ/ECH/TLS ticket retirement (T1-T8)

T1. Replace certificate but keep accepting old ticket-key generation -> resumption rejected by ancestry policy.
T2. Replace/expire DC while ticket decrypts -> DC/identity ancestry revalidation rejects stale resumption.
T3. Re-encrypt old ticket under new storage key without changing ancestry -> still stale.
T4. Full 1-RTT succeeds under new certificate while regional ticket floor has not converged -> 1-RTT allowed, resumption withheld.
T5. All regions converge ticket/revocation floors but replay state is incomplete -> PSK may recover per policy; 0-RTT remains disabled.
T6. Late edge returns with retired key generation -> quarantine until current floors proven.
T7. Resumed connection issues a descendant ticket from stale ancestry -> descendant remains stale; freshness is not reset.
T8. Ticket reaches server's shorter incident lifetime before RFC maximum -> rejected even if encoded ticket_lifetime has not expired.

## Audit notes

- This is an architecture/test contract, not executable GREEN evidence.
- No claim is made that RFC 9162, RFC 5011, reusable-holdout research, NIST SP 800-226, RFC 9345, or RFC 8446 directly specify this runtime design. They are mechanism donors; the concrete authority composition here is a project inference.
- Failure-domain labels themselves are security-sensitive claims. Future implementation must authenticate their provenance rather than trusting self-declared metadata from the authority being evaluated.
- Privacy semantic-scope equivalence is policy-specific and should fail closed when overlap cannot be proven absent.
- Ticket-key cryptographic erasure and ticket admission fencing are separate requirements: destruction of a key is useful evidence, but admission policy must independently reject stale ancestry.

## Primary sources / donors

- RFC 9162, Certificate Transparency Version 2.0 — authenticated tree views, consistency and split-view/misbehavior detection.
- RFC 5011, Automated Updates of DNSSEC Trust Anchors — explicit revocation and successor trust-anchor admission/hold-down concepts.
- Dwork et al., *The reusable holdout: Preserving validity in adaptive data analysis* (Science, 2015) and *Generalization in Adaptive Data Analysis and Holdout Reuse* — adaptive holdout reuse and information leakage/overfitting boundary.
- NIST SP 800-226, Guidelines for Evaluating Differential Privacy Guarantees — privacy loss/budget composition donor.
- RFC 9345, Delegated Credentials for TLS and DTLS — DC expiry/revocation and resumption revalidation.
- RFC 8446, TLS 1.3 — session tickets, bounded lifetime, server shorter validity, SNI/resumption behavior.

## Implementation handoff

When exact executable source becomes available, do not implement all five domains at once. Convert this matrix into tests at the owning abstraction layers and establish RED independently. Prefer monotonic externally anchored generation/floor state over mutable local counters for any authority that must survive rollback. Keep LAB-086 ahead of this work until its retained exact-source gate is complete.