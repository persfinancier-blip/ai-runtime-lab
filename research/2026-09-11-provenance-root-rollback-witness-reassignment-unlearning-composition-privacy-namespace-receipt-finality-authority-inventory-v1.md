# Provenance-root rollback, witness identity reassignment, unlearning composition, privacy namespace rotation, receipt finality, and recursive authority inventory

Date: 2026-09-11
Status: DESIGN FROZEN / RED-first contract; executable RED/GREEN still pending
Primary follow-up: LAB-093 / #178

## Why this slice exists

LAB-086 remains the highest-priority executable gate, but the current runtime cannot materialize the pinned repository snapshot into the local executor without model-mediated reserialization. Direct `git clone --no-checkout` failed before repository execution with `Could not resolve host: github.com`. The retained exact-byte security gate therefore forbids claiming new LAB-086 test evidence in this run.

This document executes the next distinct evidence task recorded in `state/CURRENT.md` rather than weakening that gate.

## Frozen contract

`PROVENANCE_ROOT_ROLLBACK_WITNESS_REASSIGNMENT_UNLEARNING_COMPOSITION_PRIVACY_NAMESPACE_RECEIPT_FINALITY_AUTHORITY_INVENTORY_V1_FROZEN`

The contract adds six monotonic authority boundaries.

### 1. Assessment provenance roots: rollback and split-view

**Boundary:** `VALID_PROVENANCE_SIGNATURE != CURRENT_CANONICAL_PROVENANCE_ROOT`.

A compromise/recovery assessment must bind to an authenticated provenance-root tuple:

- stable assessment-policy identity + policy version;
- evidence-set digest / transitive input closure;
- issuer identity + signing-key epoch;
- trusted collector/control-plane identity;
- event cutoff / observation interval;
- predecessor root digest and monotonic root generation;
- transparency checkpoint(s) or equivalent append-only inclusion evidence when available;
- canonical root floor already accepted by the verifier.

A later object that is correctly signed but descends from an older root generation MUST NOT lower the accepted provenance-root floor. Two valid signed roots at the same generation with incompatible evidence closure or predecessor lineage are `PROVENANCE_ROOT_EQUIVOCATION`, not two interchangeable truths.

Recovery may advance from the last uncontested root or from an explicitly adjudicated successor root. It may not silently discard a conflicting branch merely because a newer key signs one side.

**Donor mechanisms.** SLSA explicitly models false provenance that is signed by a trusted control plane; signature validity therefore cannot substitute for trustworthy provenance inputs. Sigstore Rekor provides append-only consistency/inclusion evidence and requires monitoring for long-term trust, which is a useful donor for detecting history mutation/split-view rather than treating one signed checkpoint as globally canonical.

### 2. Witness canonical identity: collision and reassignment across epochs

**Boundary:** `KEY_IDENTITY_CHANGED != FAILURE_DOMAIN_CHANGED` and `CANONICAL_ID_REASSIGNED != NEW_INDEPENDENT_WITNESS`.

Quorum counting operates on stable witness/failure-domain lineage, not certificate names, key IDs, process IDs, account IDs, regions, or cross-signatures alone.

Each quorum proof binds:

- stable witness subject identity;
- failure-domain identity and independence evidence;
- membership epoch;
- authorized key set and validity interval for that epoch;
- predecessor/successor witness mapping;
- canonical-identity namespace generation;
- collision/reassignment status.

If an identifier is reassigned to a different physical/administrative subject, the system must create an explicit lineage break rather than allowing the new subject to inherit old authority automatically. If two live subjects collide on one canonical identity, quorum counting deduplicates them until the collision is resolved; it never counts both merely because they possess different valid keys.

Cross-signing is continuity evidence only when rooted in previously authorized membership. Circular cross-signing between unauthorized successors cannot bootstrap quorum authority.

### 3. Exact vs approximate unlearning through ensembles and distillation

**Boundary:** `UNLEARNING_ATTESTED != HOLDOUT_INFLUENCE_PROVEN_ABSENT`.

An unlearning attestation has an explicit guarantee class:

- `EXACT_DELETION_PROOF`: a sound mechanism proves the specified influence is unreachable under the defined system/model state;
- `CERTIFIED_BOUND`: a formal residual-influence bound under stated assumptions;
- `EMPIRICAL_APPROXIMATION`: evaluation-only evidence such as membership-inference, canary, loss, or behavioral tests;
- `UNKNOWN`.

Guarantees compose conservatively through model transformations. Ensemble, merge, routing, adapter fusion, quantization, pruning, distillation, retrieval augmentation, approximate indexes, cached features/embeddings, and checkpoint averaging inherit the union of predecessor holdout/exposure lineages unless every contributing path has an equal-or-stronger deletion proof.

An `EMPIRICAL_APPROXIMATION` cannot be promoted to `EXACT_DELETION_PROOF` by combining many empirical tests. A derived model cannot claim a stronger deletion class than its weakest contributing path unless a new independent proof covers the complete derived artifact and all reachable side stores.

Deletion of a visible component does not reset an adaptive holdout exposure counter when information has already propagated into weights, caches, teacher outputs, statistics, indexes, or controller decisions.

### 4. Privacy tombstone namespace rotation and collision recovery

**Boundary:** `TOMBSTONE_NAMESPACE_ROTATED != PRIVACY_ACCOUNTING_RESET`.

Privacy accounting binds to stable semantic subject lineage and cumulative loss, not a mutable pseudonym namespace.

A namespace rotation records:

- predecessor namespace generation;
- rotation reason and cutoff;
- deterministic or privacy-preserving mapping evidence where permitted;
- unresolved collision set;
- unresolved split/relink set;
- monotonic cumulative spend/reservation/unknown-loss floor.

Collision recovery MUST NOT expose identity histories merely to reconcile accounting. Conservative accounting may temporarily merge ambiguous subjects; later disambiguation may separate future reservations, but already incurred or conservatively attributed cumulative loss is not minted back as fresh budget.

A false relink and a false split are both safety-sensitive: relink can leak identity association, while split can duplicate budget. Therefore uncertain identity resolution uses quarantine / conservative composition rather than irreversible public identity joins or new-budget creation.

### 5. Provider receipt forks: fork-choice, finality and compact proofs

**Boundary:** `VALID_SIGNED_RECEIPT != FINAL_CANONICAL_EXTERNAL_EFFECT_HISTORY`.

Provider receipts require a semantic operation identity containing at least provider domain, resource, operation kind, canonical payload digest, idempotency token/nonce where supported, provider sequence/epoch, and predecessor receipt reference.

If one provider authority produces incompatible valid receipts from the same predecessor/sequence position, the state is `PROVIDER_SEQUENCE_FORK`. Local arrival order, local wall-clock timestamp, or newest signing key alone MUST NOT select a winner.

Finality requires an explicit provider-specific rule, for example:

- a later authenticated canonical checkpoint covering the disputed sequence;
- an independently authenticated provider ledger head;
- a quorum/consensus proof when the provider exposes one;
- a reconciled external read proving exactly one surviving semantic state and fencing all competing mutations.

Until finality is established, destructive retries are blocked or fenced and the operation remains unresolved.

Receipt compaction may replace old receipts only with a compact proof that preserves:

- predecessor/canonical checkpoint ancestry;
- all unresolved sequence gaps;
- all known fork/equivocation markers;
- resource + semantic operation bindings;
- signing-key epochs and revocation status relevant to verification;
- compensation/reversal relationships.

A compensation is a new sequenced effect. It does not erase the historical fact that the original effect occurred.

### 6. Ticket-security-epoch GC: authority-inventory compromise and recursive enumeration

**Boundary:** `INVENTORY_ATTESTED != AUTHORITY_UNIVERSE_COMPLETE`.

Before retiring/GCing a ticket-security epoch, the runtime needs an authenticated authority-domain inventory whose own authority and completeness are recursively auditable.

Inventory classes include at least:

- online KMS key versions and replicas;
- HSM slots / partitions / clusters;
- wrapped/exported key material;
- backup and disaster-recovery snapshots;
- escrow / break-glass stores;
- offline recovery media;
- regional replicas and dormant regions;
- deployment secrets/configuration that can recover predecessor keys;
- replay/anti-replay state relevant to 0-RTT;
- credential roots capable of re-authorizing predecessor key recovery;
- inventory-signing / discovery services themselves.

Each inventory assertion binds issuer identity/key epoch, collector/discovery mechanism version, scope, observed domains, explicitly excluded domains, cutoff, predecessor inventory digest and a monotonic inventory generation.

If the inventory issuer or discovery plane is later compromised, every GC decision depending solely on that assertion becomes `EXTINCTION_PROOF_REOPENED`. The already advanced `ticket_security_epoch_floor` never decreases, but affected restore/resumption domains are quarantined until re-enumeration proves predecessor authority is still extinct.

Recursive recovery stops only at a configured trust anchor whose compromise handling is independently defined; a self-signed inventory saying "there are no other recovery authorities" is not completeness proof.

NIST SP 800-88 Rev. 2 is a donor for cryptographic-erase assurance: sanitization requires validation, and externally managed cryptographic keys require explicit trust/assurance treatment. This supports treating local key deletion as insufficient when recoverable copies or external management domains may still exist.

## Cross-domain invariants

1. **Monotonic uncertainty:** later evidence can resolve uncertainty but cannot silently rewrite the historical floor that caused a fail-closed decision.
2. **Stable semantic identity over administrative labels:** key/account/namespace/provider identifiers are metadata; authority and privacy accounting bind to semantic lineage.
3. **Transitive closure:** proofs cover all reachable contributing inputs/authority domains, not merely the visible object.
4. **No authority from circular assertion:** successor entities cannot manufacture trust solely by cross-signing or attesting to one another.
5. **Compaction preserves negative evidence:** unresolved gaps, forks, collisions, revocations, compromise intervals and unknown-loss floors survive GC/compaction.
6. **Fail closed at destructive boundaries:** unresolved external-effect history, uncertain predecessor authority or incomplete proof blocks destructive retry/resumption/GC rather than guessing.

## 40-case RED-first matrix

### Provenance-root rollback / split-view
1. Accept root generation N; replay valid signed N-1 -> reject rollback.
2. Present two valid incompatible roots at generation N -> explicit equivocation.
3. Successor key signs branch descending from stale root -> no automatic recovery.
4. One root has transparency inclusion, conflicting root lacks consistency ancestry -> quarantine conflict.
5. Re-sign poisoned evidence closure under fresh key -> evidence remains poisoned.
6. Change policy version without binding it into successor root -> reject.
7. Compact old roots while unresolved split-view exists -> reject GC.

### Witness canonical identity reassignment
8. Rotate key for same witness/failure domain -> count one vote.
9. Cross-sign two overlapping keys for same witness -> count one vote.
10. Reassign canonical witness ID to new operator without lineage-break record -> reject.
11. Two live witnesses collide on canonical ID -> deduplicate/quarantine, never count two.
12. Rename region/account while operator/failure domain unchanged -> no new independence.
13. Circular cross-signing among unauthorized successor witnesses -> cannot bootstrap quorum.
14. Historical proof evaluated with current membership rather than event membership epoch -> reject.

### Unlearning composition
15. Exact deletion proof for one ensemble member, untreated second member -> ensemble retains lineage.
16. Empirical MIA success after deletion -> class remains empirical, not exact.
17. Distill from a supposedly unlearned teacher plus untreated teacher cache -> inherit union lineage.
18. Merge exact-deleted model with approximate-deleted model -> resulting guarantee no stronger than approximate unless new proof covers whole merge.
19. Rebuild ANN index but retain old embeddings -> exposure persists.
20. Delete adapter but base weights were adapted through shared controller feedback -> lineage persists.
21. Quantize/prune after approximate unlearning -> transformation does not upgrade deletion class.

### Privacy tombstone namespace rotation
22. Rotate tombstone namespace -> cumulative spend floor unchanged.
23. Collision maps two subjects to one tombstone -> isolate identity, conservatively compose spend.
24. Later disambiguate collision -> no refund of already composed loss.
25. False split creates two pseudonyms for one subject -> no duplicate budget.
26. False relink joins distinct subjects -> quarantine relation without exposing both identity histories.
27. Rotate namespace while unresolved reservations exist -> reservations migrate or remain charged.
28. Delete mapping table then relink through new resolver -> predecessor accounting lineage still required.

### Provider receipt fork/finality
29. Same predecessor/sequence produces two valid incompatible receipts -> fork state.
30. Later-arriving receipt has newer wall clock -> not sufficient for fork choice.
31. Receipt signed by newer key conflicts with old-key receipt valid at event time -> rotation alone gives no finality.
32. Sequence gap followed by later valid receipt -> keep gap unresolved; no blind retry.
33. Compact receipts while fork marker unresolved -> reject compaction.
34. Compensation succeeds after original effect -> preserve both sequenced effects.
35. Same idempotency token with different canonical payload -> semantic conflict, not dedup success.

### Recursive authority inventory / ticket epoch GC
36. All listed KMS domains acknowledge erasure but inventory omitted escrow -> reject extinction proof.
37. Inventory issuer later compromised -> reopen dependent extinction proof; do not lower epoch floor.
38. Restore dormant backup containing predecessor wrapped key -> quarantine restore domain/resumption.
39. Inventory recursively depends on recovery credential not included in enumeration -> incomplete proof.
40. Re-enumeration proves predecessor authority extinct after compromise -> allow new forward progress while retaining historical compromise/audit record.

## Implementation guidance for future RED/GREEN work

Do not create six unrelated subsystems. Prefer shared primitives for:

- monotonic authenticated generations and predecessor digests;
- stable semantic identity + epoch-scoped aliases;
- typed proof-strength lattice (`EXACT`, `CERTIFIED_BOUND`, `EMPIRICAL`, `UNKNOWN`);
- unresolved-negative-evidence retention through compaction;
- explicit quarantine states rather than implicit booleans;
- transitive provenance / authority-set digests.

Tests should be written at the same real-schema abstraction level as the consuming ledger/security boundary. Synthetic classifiers may help design, but they do not substitute for exact RED/GREEN execution.

## Evidence and donor notes

Primary/near-primary donors consulted on 2026-09-11:

- SLSA v1.1 Threats & mitigations — https://slsa.dev/spec/v1.1/threats — explicitly covers false provenance signed by a trusted control plane and cache poisoning/transitive-input requirements.
- Sigstore Rekor overview — https://docs.sigstore.dev/logging/overview/ — append-only consistency/inclusion monitoring model.
- Sigstore Security Model — https://docs.sigstore.dev/about/security/ — Rekor entries/tree heads provide cryptographic transparency evidence; long-term trust depends on monitoring.
- Sigstore log sharding — https://docs.sigstore.dev/logging/sharding/ — donor for freezing a log shard while rotating signing keys without treating the new key as a rewritten history.
- NIST SP 800-88 Rev. 2 — https://csrc.nist.gov/pubs/sp/800/88/r2/final — sanitization assurance, validation, cryptographic erase, and externally managed key considerations.

Inference vs fact: the exact state machines and invariants in this document are repository design decisions synthesized from the cited donor mechanisms; the donor standards do not prescribe these AI Runtime Lab field names or state labels.

## Decision

Freeze this contract for later exact RED/GREEN implementation. It does not supersede LAB-086 and must not be used as a claim of executable proof. The next run must probe LAB-086 exact materialization first.