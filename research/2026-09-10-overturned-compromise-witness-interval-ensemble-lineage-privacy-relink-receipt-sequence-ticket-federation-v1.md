# Overturned compromise evidence, ambiguous witness intervals, ensemble lineage, probabilistic relink, receipt sequence gaps, and federated ticket authority

Date: 2026-09-10
Status: DESIGN FROZEN / RED-FIRST; **not executable proof**
Contract: `OVERTURNED_COMPROMISE_WITNESS_INTERVAL_ENSEMBLE_PRIVACY_RELINK_RECEIPT_SEQUENCE_TICKET_FEDERATION_V1_FROZEN`

## Why this slice exists

LAB-086 remains priority #1, but this run again could not materialize the exact executable closure: direct `git clone --no-checkout` failed before repository execution with `Could not resolve host: github.com`. Connector reads/writes remain available. No LAB-086 behavioral, unsafe-seed, compileall, reconciliation, or conflict PASS is claimed here.

This note executes the distinct fallback named in `state/CURRENT.md`. It extends LAB-093-family authority/provenance design without substituting for later RED/GREEN implementation.

## Primary donors / facts

1. RFC 9162, Certificate Transparency v2 — append-only consistency is proved between authenticated tree heads, while consistency of the view presented to all entities requires sharing observations; an individually valid signed view is not itself a proof of global consistency. https://www.rfc-editor.org/rfc/rfc9162.html
2. NIST SP 800-57 Part 1 (key-compromise guidance) — compromise of a signing key makes signatures under that key suspect unless independent mechanisms establish trustworthy timing/protection before compromise. This motivates interval-aware authority rather than timeless `key_valid=true/false`. https://csrc.nist.gov/publications/detail/sp/800-57-part-1/rev-5/final
3. NIST SP 800-102 was withdrawn in 2025, but its narrow observation remains useful as a donor rather than a normative dependency: a self-asserted signing time does not establish when a signature was generated; trusted time evidence or verifier-supplied data is required. Current status: https://csrc.nist.gov/pubs/sp/800/102/final
4. Jagielski et al., *Students Parrot Their Teachers: Membership Inference on Model Distillation* — distillation alone provides limited privacy and can preserve training-membership signal indirectly. https://arxiv.org/abs/2303.03446
5. NIST SP 800-226, differential privacy guidance — privacy accounting is cumulative; administrative reshaping of identity/scope cannot safely mint fresh budget. https://csrc.nist.gov/pubs/sp/800/226/final
6. RFC 8446 / RFC 9846 TLS 1.3 — 0-RTT has weaker replay properties; fresh startup should reject 0-RTT while the replay-recording window overlaps startup, and implementations should bound total lifetime of resumption keying-material ancestry. https://www.rfc-editor.org/rfc/rfc8446.html and https://www.rfc-editor.org/rfc/rfc9846.html
7. RFC 9813 adds a useful operational rule: if cached authorization data for resumption cannot be securely retrieved, do not resume; perform a full handshake. https://www.rfc-editor.org/rfc/rfc9813.html

## Frozen invariants

### A. Recovery-transition authority when compromise evidence is later revoked or overturned

`COMPROMISE_EVIDENCE_REVOKED != PREVIOUS_AUTHORIZATION_AUTOMATICALLY_VALID`

A compromise finding is itself versioned evidence. Later revocation/overturning creates a successor assessment; it does not erase that an earlier safety decision was made under uncertainty. Recovery-transition history records:

- subject authority / key / failure-domain lineage;
- alleged compromise interval `[from, until?]`;
- evidence root and assessment epoch;
- assessment status: `ALLEGED | CONFIRMED | OVERTURNED | SUPERSEDED`;
- successor assessment reference;
- quorum authorization evaluated at transition time;
- monotonic `authorization_uncertainty_floor`.

If a transition was quarantined because the remaining independently trustworthy quorum fell below threshold, a later `OVERTURNED` finding may authorize a **new** recovery evaluation. It MUST NOT silently rewrite historical transition acceptance or decrement the uncertainty floor. If two active assessments are incomparable, result is `COMPROMISE_ASSESSMENT_CONFLICT`, not majority-by-arrival-time.

### B. Compact-root anti-rollback under ambiguous/overlapping witness validity intervals

`SIGNATURE_VERIFIES_NOW != WITNESS_AUTHORIZED_AT_EVENT_CUTOFF`

For every compact root, retain enough authenticated data to reconstruct witness authority at the exact event cutoff:

- stable witness identity and failure-domain lineage;
- key epoch;
- validity interval;
- revocation/compromise interval evidence;
- membership epoch;
- threshold;
- predecessor root/checkpoint;
- conflict/equivocation set;
- evidence cutoff / trusted ordering anchor.

Overlapping witness-key validity intervals are allowed only when an authenticated transition defines whether both keys are aliases of one voting identity or whether one supersedes the other. They MUST NOT count twice toward quorum. If event ordering cannot determine whether a witness was authorized, compact-root reconstruction returns `WITNESS_INTERVAL_AMBIGUOUS` and fails closed.

GC is forbidden until every retained compact root can reproduce the same or stricter authority decision without consulting mutable current membership state.

### C. Holdout exposure lineage through ensemble aggregation, model merging, and retrieval-cache regeneration

`MULTIPLE_MODELS != MULTIPLE_INDEPENDENT_HOLDOUTS`

A model/ensemble/cache artifact inherits holdout exposure lineage whenever its parameters, weights, selection, routing, thresholds, candidate ranking, distillation targets, embeddings, features, ANN topology, cached scores, or acceptance decisions were influenced by prior holdout feedback.

Union rule:

`artifact.exposure_lineage = union(all reachable predecessor exposure lineages)`

This applies to:

- weighted/voted ensembles;
- checkpoint averaging / model soups;
- adapters merged into a base model;
- teacher -> student distillation;
- retrieval indexes rebuilt from holdout-influenced embeddings/features;
- regenerated caches whose source model/controller retains the same exposure lineage.

Deleting raw holdout rows, rebuilding the ANN index, changing artifact IDs, quantizing, pruning, distilling, or averaging does not create a fresh exposure budget. A lineage can be retired only when no adaptive controller can reach information derived from it and the retirement proof itself is monotonic/auditable.

### D. Privacy accounting across irreversible identifier redaction and probabilistic relink

`IDENTIFIER_REDACTED != ACCOUNTING_SUBJECT_FORGOTTEN`

The runtime may irreversibly redact direct identifiers while retaining a privacy-safe accounting tombstone that cannot reconstruct the identifier but can prevent known prior spend from being reset. A later probabilistic relink never creates spend credit.

For a new identity candidate `n` linked to predecessor tombstones `{p_i}` with non-zero supported match probability or unresolved ambiguity:

- preserve each predecessor cumulative spend / reservations / unknown-loss floor;
- compose the conservative union for overlapping candidate sets;
- record resolver/model version, evidence cutoff, graph epoch, confidence semantics, and expiry;
- if a reliable proof of disjointness is unavailable, do not split the budget merely because confidence is below 1.0;
- graph split -> merge -> split oscillation never decreases any previously composed privacy-loss floor.

A resolver result is evidence, not authority to erase accounting lineage.

### E. Provider-receipt canonicalization under clock skew, sequence gaps, delayed arrival, and recovered-key compromise

`ARRIVAL_ORDER != EFFECT_ORDER`
`SIGNED_TIMESTAMP != TRUSTED_EFFECT_TIME`
`SEQUENCE_GAP != SAFE_TO_INFER_NO_EFFECT`

Every external-effect receipt is canonicalized over authority-relevant fields, including provider identity, provider key epoch, logical operation ID, effect ID, predecessor effect/sequence where supported, semantic payload digest, result class, and provider-owned sequence/epoch. Local receipt time is metadata only.

Rules:

- canonical effect order uses provider-authenticated sequence/ancestry, not wall-clock arrival;
- clock skew alone cannot reorder or invalidate a sequence-consistent history;
- a missing sequence creates `RECEIPT_SEQUENCE_GAP`; no blind retry of an effect whose outcome could occupy the gap;
- a receipt arriving after key compromise is evaluated against the key's event-time authorization interval and independent trusted ordering evidence, not merely whether the signature verifies today;
- recovering an old provider signing key from backup does not make it current authority again;
- incompatible valid receipts for one logical effect lineage create `PROVIDER_EQUIVOCATION` even when they use different key epochs;
- compensation/reversal is a separately authorized effect referencing the predecessor; it never edits the predecessor out of history.

### F. Ticket-security-epoch convergence with federated KMS/escrow authority

`REGIONAL_EPOCH_ACK != GLOBAL_PREDECESSOR_AUTHORITY_EXTINCT`

Model ticket resumption authority as a federation of independently administered domains: active KMS/HSM, standby regions, backup/DR, import/export stores, escrow/recovery services, and operators able to restore wrapped predecessor keys.

A global `ticket_security_epoch_floor` is monotonic. A region may serve fresh full-auth 1-RTT after current identity/policy verification while remaining `RESUMPTION_QUARANTINED` until it proves convergence.

Retiring epoch `e` requires an authenticated convergence record covering:

- complete known authority-domain membership at cutoff;
- per-domain state `ABSENT | DESTROYED_VALIDATED | QUARANTINED | UNKNOWN`;
- backup/escrow restore generations and delayed-discovery channel;
- revocation/cutoff for credentials that can recover predecessor keys;
- replay-state epoch for 0-RTT;
- maximum permitted keying-material ancestry lifetime.

`UNKNOWN` never counts as extinction. A late-discovered escrow/KMS authority reopens the extinction proof for affected domains but MUST NOT lower the global epoch floor; affected resumption stays quarantined. Loss of replay state additionally blocks 0-RTT even when PSK 1-RTT is otherwise safe. If resumption authorization context cannot be securely reconstructed, fall back to full authentication rather than guessing.

## 40-case RED-first matrix

### Recovery / compromise assessment (1-7)
1. confirmed predecessor compromise intersects transition -> historical authorization re-evaluates;
2. later `OVERTURNED` assessment does not mutate prior record in place;
3. overturned evidence permits a new recovery evaluation with successor assessment ID;
4. incomparable active assessments -> `COMPROMISE_ASSESSMENT_CONFLICT`;
5. renamed/rekeyed predecessor retains same failure-domain vote identity;
6. uncertainty floor never decreases after assessment reversal;
7. stale assessment epoch cannot authorize a new transition.

### Witness interval / compact root (8-14)
8. overlapping keys for one stable witness count once;
9. authenticated key handoff resolves event-time authority;
10. ambiguous event cutoff vs validity interval -> fail closed;
11. later key expiry does not erase previously proven evidence;
12. later key compromise triggers interval-aware reconstruction;
13. compact-root GC rejected when predecessor membership epoch is unavailable;
14. reconstruction result cannot depend on mutable current witness membership.

### Ensemble / holdout lineage (15-21)
15. weighted ensemble unions member exposure lineage;
16. majority-vote ensemble unions member exposure lineage;
17. model soup/checkpoint averaging preserves union lineage;
18. adapter merge into clean base imports adapter exposure lineage;
19. distilled student preserves teacher-derived exposure lineage;
20. ANN/retrieval cache regeneration from exposed embeddings preserves lineage;
21. delete-and-regenerate IDs do not reset exposure budget.

### Privacy redaction / relink (22-27)
22. direct identifier deletion keeps non-reconstructive accounting tombstone;
23. probabilistic relink composes predecessor spend conservatively;
24. confidence <1 is not proof of subject disjointness;
25. resolver version change invalidates stale disjointness proof but not spend;
26. graph split->merge->split never decreases spend floor;
27. unresolved multiple predecessor candidates retain union/unknown-loss floor.

### Provider receipts (28-34)
28. delayed earlier receipt is ordered by provider sequence, not arrival;
29. wall-clock skew cannot override authenticated sequence;
30. sequence gap yields `RECEIPT_SEQUENCE_GAP` and blocks blind retry;
31. recovered old signing key cannot mint current-authority receipt;
32. delayed receipt under later-compromised key requires event-time evidence;
33. contradictory receipts across key epochs -> `PROVIDER_EQUIVOCATION`;
34. compensation is a new sequenced effect, not deletion of predecessor.

### Federated ticket authority (35-40)
35. one region's key deletion is insufficient for global extinction;
36. unknown escrow/backup domain blocks retirement proof;
37. late-discovered predecessor authority re-quarantines affected resumption without lowering global floor;
38. full-auth 1-RTT can recover before PSK resumption when policy permits;
39. lost replay-state epoch blocks 0-RTT independently of PSK 1-RTT;
40. inability to securely retrieve original resumption authorization context forces full handshake.

## Implementation direction when exact execution returns

Do not add all six domains as one implementation patch. Convert this matrix into narrow regression-first slices attached to the owning LAB issues. Prefer immutable/versioned evidence records, monotonic floors, explicit uncertainty states, authenticated predecessor links, and exact event-cutoff evaluation over mutable booleans such as `valid`, `revoked`, `deleted`, or `current`.

For every slice, first reproduce the unsafe/ambiguous pre-fix behavior on exact published bytes, then implement the smallest fail-closed change and run upstream/downstream gates. This design freeze is evidence planning only and does not change any draft PR readiness.
