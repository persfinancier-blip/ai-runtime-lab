# Observer domain attestation, compact holdout provenance, semantic privacy scope, replica fencing, and ticket-retirement convergence

Date: 2026-09-10
Status: FROZEN DESIGN / RED-FIRST CONTRACT
Contract: `OBSERVER_DOMAIN_ATTESTATION_HOLDOUT_COMPACTION_PRIVACY_SCOPE_OVERLAP_RETENTION_REPLICA_FENCE_TICKET_RETIREMENT_V1_FROZEN`

## Why this slice exists

LAB-086 remains the executable priority, but the exact byte-materialization gate is unavailable in this run. This document advances the next distinct evidence task recorded in `state/CURRENT.md` without claiming executable proof.

The common failure mode across the five domains below is identity laundering: creating a new member id, dataset hash, privacy scope id, proxy/replica acknowledgement, certificate, delegated credential, ticket key, or regional recovery generation and then treating the new identifier as if it erased security ancestry. The safe contract is the opposite: successor authority inherits every unresolved predecessor floor until there is authenticated evidence that permits a monotonic transition.

## Primary donors

- RFC 9162, Certificate Transparency Version 2.0: authenticated tree heads, consistency proofs, monitors/auditors, and signed evidence of inconsistent views. https://www.rfc-editor.org/rfc/rfc9162
- Nakkiran & Błasiok, The Generic Holdout: limited holdout disclosure is the core defense against adaptive overfitting. https://arxiv.org/abs/1809.05596
- Dwork et al., Generalization in Adaptive Data Analysis and Holdout Reuse: repeated adaptive reuse can overfit the holdout itself. https://arxiv.org/abs/1506.02629
- NIST SP 800-226, Guidelines for Evaluating Differential Privacy Guarantees: privacy budget is an upper bound on cumulative privacy loss and composes across analyses of the same sensitive data. https://doi.org/10.6028/NIST.SP.800-226
- RFC 9345, Delegated Credentials for TLS and DTLS: DCs are short-lived, are bound to the certificate, cannot be independently revoked early, and should be revalidated when resuming cached sessions. https://www.rfc-editor.org/rfc/rfc9345
- RFC 8446, TLS 1.3: session tickets are PSK-bearing resumable authority, ticket lifetime is at most 7 days, SNI continuity is constrained, and chains of replacement tickets can otherwise extend original keying-material lifetime. https://www.rfc-editor.org/rfc/rfc8446
- RFC 9325, secure TLS/DTLS use: ticket-encryption keys should rotate and old keys must be destroyed at the end of validity. https://www.rfc-editor.org/rfc/rfc9325

## 1. Authenticate observer failure-domain and authority-lineage claims

### Boundary

`MEMBER_ID_UNIQUE != FAILURE_DOMAIN_INDEPENDENT`

A quorum that depends on independent failure domains cannot accept self-asserted labels such as `region=west`, `operator=B`, or a fresh signer id as proof of independence. The recovery record must bind every voter to an authenticated authority-lineage record and an authenticated failure-domain claim whose issuer is itself outside the authority being evaluated.

Recommended canonical observer admission record:

- observer key / member id;
- stable authority-lineage id;
- failure-domain ids at the dimensions required by policy (operator, control plane, storage, region, root/recovery authority);
- attestation issuer and attestation-root generation;
- validity interval / lease expiry;
- predecessor membership epoch and admission digest;
- revocation generation and reason where applicable.

The threshold evaluator counts independent domains, not ids. Multiple members descending from one compromised recovery root count as one compromised lineage for the dimensions affected by that compromise.

### Attestation-root rollback

`ATTESTATION_SIGNATURE_VALID != ATTESTATION_ROOT_CURRENT`

A cryptographically valid domain assertion rooted in an old generation is stale after root rotation/recovery. Observer-set recovery therefore carries a monotonic `domain_attestation_root_generation`. A snapshot or regional rollback that presents an older but valid root must not make previously revoked/merged lineages independent again.

RFC 9162 is a donor for the distinction between a valid signed view and a globally consistent view: signed conflicting views remain evidence rather than being overwritten by later preference.

### Recovery rule

A successor observer epoch MUST preserve:

1. the last uncontested checkpoint/root;
2. all known conflicting authenticated views;
3. the predecessor observer-set digest;
4. the current domain-attestation-root generation;
5. all unresolved compromised-lineage flags;
6. the new threshold policy and its minimum independent-domain requirements.

Changing member ids or keys without changing authenticated lineage/domain ancestry does not restore independence.

## 2. Compact reusable-holdout provenance without losing disclosure ancestry

### Boundary

`COMPACT_PROVENANCE_ROOT != FRESH_HOLDOUT`

The raw provenance DAG may become too large to retain forever, but compaction may not discard the facts needed to know whether a holdout has already influenced adaptive selection.

A compact root should commit to at least:

- source dataset lineage set and subject/sample provenance class;
- generator/transformation lineage and code/config digest;
- analyst/controller lineage;
- disclosure-generation counter;
- cumulative disclosure class/budget (boolean accept/reject, score, ranking, residuals, examples, etc.);
- candidate-family lineage roots touched by those disclosures;
- predecessor compact-root digest;
- monotonic freshness / recovery generation.

Raw nodes may be garbage-collected only after their disclosure ancestry is represented in an authenticated successor root. A rollback to a pre-disclosure compact root is not a fresh holdout; it is stale state.

### Synthetic and derived datasets

`SYNTHETIC_ROWS_DIFFER != INFORMATION_INDEPENDENT`

If a generator was fit, calibrated, filtered, selected, or validated using the holdout or a disclosure-descendant dataset, its output inherits that disclosure lineage. Dataset hashes and generator version changes are identifiers, not independence proofs.

This follows the reusable/generic-holdout donor logic: the risk is information flowing back into adaptive selection, not filename or row identity.

## 3. Define semantic privacy-scope overlap/equivalence

### Boundary

`SCOPE_IDS_DIFFER != SUBJECT_SETS_DISJOINT`

Privacy capacity cannot be safely split or merged using administrative scope ids alone. If two scopes may contain the same protected subjects or records, their privacy-loss accounting overlaps unless there is authenticated evidence of disjointness or a formally supported composition rule.

Canonical scope ancestry should bind:

- semantic subject-set definition / selector digest;
- data-source lineage;
- time/window semantics;
- inclusion uncertainty state;
- predecessor/successor scope ids;
- accountant/mechanism class;
- charged, reserved, and `unknown-after-possible-disclosure` floors.

### Changing or ambiguous subject sets

`SUBJECT_NOT_OBSERVED_NOW != SUBJECT_NEVER_INCLUDED`

For mutable populations, deletion, late arrival, deduplication changes, identity resolution, or partitioned ingestion can alter the apparent set. Budget reconciliation must therefore distinguish:

- proven disjoint;
- proven overlap;
- potentially overlapping / unresolved;
- semantically equivalent successor.

When overlap is unresolved, conservative composition applies. Split operations conserve total remaining capacity; merge operations carry the composed predecessor loss floor rather than selecting the minimum or resetting to a fresh scope.

NIST SP 800-226 is the donor for treating privacy budget as cumulative loss across repeated analyses of the same sensitive data.

## 4. Extend destructive retention fencing across multi-hop proxies and replicas

### Boundary

`PROXY_ACK_CURRENT != REPLICA_FENCE_CURRENT`

A destructive request can cross scheduler -> proxy -> queue -> storage router -> replica. A current control-plane decision or first-hop acknowledgement is insufficient if a downstream replica can execute with an older resource fence.

Each destructive operation should carry an immutable operation id and monotonic execution authority tuple such as:

`(policy_epoch, delegation_generation, operation_generation, proxy_fence, replica_set_epoch, resource_fence)`.

Every destructive-capable hop must either validate the tuple against a current authenticated floor or fail closed. The final resource replica performs the decisive check immediately before effect.

### Replica and acknowledgement rollback

`ACK_RECORDED != EFFECT_GLOBALLY_FENCED`

A replica acknowledgement is scoped to the replica identity/epoch that produced it. Restoring a replica from an old snapshot, reusing an id, or rejoining after partition requires a current fence reconciliation before destructive authority resumes. An acknowledgement set is complete only against the canonical destructive-writer/replica inventory for that membership epoch.

Timeout after dispatch remains `EFFECT_UNKNOWN`; retry cannot authorize a second destructive generation until the predecessor effect is reconciled or all possible executors are fenced beyond it.

## 5. Durable ticket-key retirement and regional convergence after PQ/ECH/DC recovery

### Boundary

`NEW_CERT_OR_DC_OR_PQ_KEY != OLD_RESUMPTION_AUTHORITY_RETIRED`

TLS 1.3 session tickets are resumable PSK authority. Replacing a certificate, delegated credential, PQ/hybrid identity configuration, ECH config, backend identity, or ticket-encryption key does not by itself prove that all old tickets have become unspendable.

RFC 9345 specifically warns that a cached DC should be revalidated on resumption; otherwise a connection may resume after that DC expires. RFC 8446 additionally warns that issuing successor tickets indefinitely can extend the lifetime of keying material derived from the original full handshake.

### Retirement acknowledgement durability

A ticket generation is `RETIRED_CONFIRMED` only when the recovery control plane has durable evidence for every eligible ticket-spend authority at the relevant membership epoch:

- old generation rejected/fenced;
- current ticket-key generation installed;
- current certificate/DC/PQ/ECH/backend identity floors installed;
- current revocation floor installed;
- current replay floor installed where 0-RTT is enabled;
- acknowledgement is itself bound to region/edge lineage and recovery generation.

A late/rejoining region whose acknowledgement is absent or stale is `RESUMPTION_QUARANTINED`, not implicitly converged.

### Regional partial rollback

`REGION_HAS_NEW_KEYS != REGION_REJECTS_OLD_TICKETS`

After snapshot rollback, an edge may possess both a fresh key/config and a stale ticket admission database. Admission therefore compares ticket ancestry against monotonic retirement/revocation floors, not merely key availability.

Recovery may be staged:

1. current full-auth 1-RTT after identity verification;
2. PSK resumption only after ticket-retirement/revocation convergence;
3. 0-RTT only after the additional replay-state convergence gate.

Re-encrypting or reissuing a ticket preserves the oldest unresolved security ancestry. A descendant ticket cannot wash away compromise of its certificate/DC/PQ/ECH/backend/ticket/replay ancestors.

## 40-case RED-first matrix

### Observer/domain attestation

1. Two unique member ids share one authenticated operator lineage -> count as one operator domain.
2. New keys under the same compromised recovery lineage -> independence is not restored.
3. Valid domain assertion under stale attestation root -> reject for current quorum.
4. Snapshot rollback restores revoked domain assertion -> reject by root-generation floor.
5. Emergency member expires after witnessing conflict -> future vote removed, evidence retained.
6. Membership churn removes conflicting observer -> historical conflict remains in successor root.
7. Domain claim issuer equals evaluated authority -> reject self-attested independence.
8. Successor epoch omits unresolved compromised-lineage flag -> fail closed.

### Holdout provenance compaction

9. Compact root includes all disclosure ancestry -> raw DAG GC allowed after authenticated successor commit.
10. Compaction omits score disclosure lineage -> reject root as incomplete.
11. Rollback to compact root before a disclosure -> stale, not fresh holdout.
12. New dataset hash generated from disclosed holdout-derived model -> inherits lineage.
13. Generator version rollback -> does not decrement disclosure generation.
14. New analyst account uses same adaptive controller state -> inherits exposure lineage.
15. Candidate-family rename after score disclosure -> no fresh budget.
16. Boolean-only confirmation followed by score disclosure -> exposure class monotonically widens.

### Privacy semantic-scope overlap

17. Different scope ids select overlapping subjects -> compose loss.
18. Proven disjoint subject sets -> allow partitioned capacity under explicit allocator.
19. Subject identity resolution later reveals overlap -> reconcile to conservative composed floor.
20. Split one scope into two without allocator debit -> reject budget duplication.
21. Merge scopes by taking minimum predecessor spend -> reject laundering.
22. Potential late-arriving subjects make disjointness uncertain -> treat as unresolved overlap.
23. Deleted records disappear from current query but were previously disclosed -> retain charged ancestry.
24. Scope-equivalent rename/repartition -> preserve predecessor spend/reservation/unknown floors.

### Retention proxy/replica fencing

25. Current scheduler lease + stale proxy fence -> reject before dispatch.
26. Current proxy + stale storage-router fence -> reject.
27. Current router + one stale destructive-capable replica -> do not claim global fence convergence.
28. Rejoined replica restored before revocation floor -> destructive quarantine.
29. Replica id reused with new process but old lineage -> requires new authenticated membership/fence transition.
30. Timeout after possible delete at one replica -> `EFFECT_UNKNOWN`, no blind retry generation.
31. Ack set omits a replica in canonical writer inventory -> incomplete.
32. Old queued job reaches resource after policy/fence advance -> final resource rejects.

### TLS/PQ/ECH/DC ticket retirement

33. Certificate replaced while old ticket generation remains accepted in one region -> retirement incomplete.
34. DC expires but cached ticket would otherwise resume -> require DC ancestry revalidation/floor.
35. Ticket key rotated but old key retained in DR -> not erased/retired globally.
36. Region installs new PQ/ECH config but admission floor rolls back -> reject old ancestry by monotonic floor.
37. Descendant ticket issued from stale ancestor -> descendant remains stale.
38. All regions converge on identity/ticket floors but one lacks replay floor -> allow eligible 1-RTT/PSK policy, keep 0-RTT disabled there.
39. Late edge rejoins with old tickets and valid current cert -> resumption quarantine until acknowledgement/convergence proof.
40. Re-encrypted old ticket under new ticket key -> ancestry unchanged; no reauthorization by ciphertext freshness.

## Implementation implications

These are design contracts, not executable PASS claims. When exact source execution is restored, implementation should proceed RED-first at the owning subsystem boundaries, favoring monotonic authenticated successor records over mutable booleans. Every compacted or rotated authority needs an explicit predecessor digest and unresolved-floor carry-forward rule.

## Decision

Freeze `OBSERVER_DOMAIN_ATTESTATION_HOLDOUT_COMPACTION_PRIVACY_SCOPE_OVERLAP_RETENTION_REPLICA_FENCE_TICKET_RETIREMENT_V1_FROZEN` for future executable work. It composes with LAB-093..100 but does not change their readiness or LAB-086 priority.