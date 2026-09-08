# Authority-compromise evidence provenance, onset adjudication, false-revocation resistance, and recovery-key independence v1

Date: 2026-09-08
Status: `AUTHORITY_COMPROMISE_PROVENANCE_ONSET_FALSE_REVOCATION_RECOVERY_INDEPENDENCE_V1_FROZEN`
Scope: LAB-093 design follow-up; composes with source/promise authority transparency, post-facto completeness invalidation, continuous assurance, recovery/rebootstrap, and LAB-087 isolation contracts.

## 1. Question

The previous freeze established that a late compromise notice can invalidate *current reliance* on an earlier completeness verdict without rewriting its historical receipt. The remaining ambiguity was more fundamental: who is allowed to assert compromise, how to appraise conflicting/uncertain compromise-onset claims, how to prevent revocation from becoming a permanent denial-of-service primitive, and how recovery/replacement authority remains independent from both the compromised source key and the evidence producer alleging compromise.

This note freezes that boundary. It is a design/evidence result only; no executable RED/GREEN is claimed because exact repository execution is unavailable in this run.

## 2. Primary donors and reusable mechanisms

### RFC 5280 — distinguish revocation processing time from invalidity/compromise time

RFC 5280 CRLs distinguish the revocation processing date from `invalidityDate`, which is the date the private key is known or suspected to have been compromised or the certificate otherwise became invalid. The invalidity date may precede the revocation publication date.

Reusable mechanism: never equate `notice_published_at` or `revocation_processed_at` with compromise onset. Preserve separate temporal claims and their provenance.

Source: https://www.rfc-editor.org/rfc/rfc5280.html, §5.3.2.

### RFC 6960 — status authority is delegated authority, not arbitrary telemetry

OCSP requires a responder signing certificate status to be the issuer or an explicitly authorized responder. It also separates `thisUpdate`, `nextUpdate`, `producedAt`, and `revocationTime`.

Reusable mechanism: compromise/revocation statements require explicit authority and freshness semantics; merely observing an error, outage, anomaly, or unsigned monitor signal cannot create globally authoritative revocation state.

Source: https://www.rfc-editor.org/rfc/rfc6960.html, §§2.4, 4.2.2.2.

### NIST SP 800-57 Part 1 Rev. 5 — compromise recovery and damage appraisal

NIST states that compromised private/secret keys must be revoked, affected keys replaced as needed, and damage assessment performed. It emphasizes that compromise of broadly trusted/root keys has widespread consequences.

Reusable mechanism: key compromise is not only a key-lifecycle bit. It creates a scoped damage-assessment problem over every dependent statement/process during the affected interval.

Source: NIST SP 800-57 Part 1 Rev. 5, §9.5.4.

### TUF / Uptane — threshold and offline root as recovery separation

TUF treats threshold compromise of root keys as a severe event requiring out-of-band recovery. Uptane recommends root/offline keys separated from repository compromise domains and threshold control so one compromised online/repository key cannot authorize recovery metadata by itself.

Reusable mechanism: recovery/replacement authority must be a separate, independently controlled authority with threshold/offline custody appropriate to impact.

Sources:
- https://theupdateframework.github.io/specification/draft/
- https://uptane.org/docs/latest/deployment/best-practices

### Sigstore trust-root threat model — distributed root, compromise time, auditable rotation

Sigstore documents threshold root signing, offline root keys, rotation/revocation, compromise-time metadata, freshness, and geographically/organizationally distributed root key holders.

Reusable mechanism: compromise-time claims and recovery metadata should be auditable while recovery root custody remains organizationally/control-domain independent.

Source: https://github.com/sigstore/docs/blob/main/content/en/about/threat-model.md

## 3. Frozen semantic boundaries

### 3.1 Evidence is not authority

`COMPROMISE_SIGNAL != COMPROMISE_EVIDENCE != APPRAISED_COMPROMISE != GLOBAL_REVOCATION`

A monitor alarm, provider outage, forensic observation, anomalous signature, leaked credential report, or operator assertion is input evidence. It does not become a globally authoritative revocation solely because it is authenticated by the evidence producer.

### 3.2 Notice time is not compromise onset

`NOTICE_TIME != DETECTION_TIME != FIRST_PROVEN_MISUSE != COMPROMISE_ONSET`

Every compromise record MUST keep these concepts separate when known:

- `observed_at`: when the evidence producer observed the fact;
- `asserted_at`: when the signed claim was created;
- `published_at`: when the claim became available to relying parties;
- `last_proven_good`: latest authenticated point at which the authority/key state is positively evidenced as uncompromised/controlled under the relevant policy;
- `first_proven_bad`: earliest independently evidenced unauthorized use or custody failure;
- `onset_lower_bound_exclusive` / `onset_upper_bound_inclusive`: adjudicated interval in which onset may have occurred;
- `exact_onset`: optional and permitted only when evidence actually supports an exact instant.

The common bounded case is:

`last_proven_good < COMPROMISE_ONSET <= first_proven_bad`

If either bound is absent, the interval remains open. A publication timestamp MUST NOT be substituted for an unknown earlier onset.

### 3.3 Positive misuse proof does not backdate itself

A cryptographically valid unauthorized signature proves that signing capability was misused no later than that event. It does not, by itself, prove how much earlier compromise began.

Conversely, loss-of-custody/HSM audit evidence can justify an earlier suspected interval without proving every signature inside that interval was malicious. The appraisal result therefore affects *reliance* over the uncertain interval rather than fabricating a precise attack time.

## 4. Evidence provenance model

Freeze `CompromiseEvidenceEnvelopeV1`:

```text
claim_id
subject_authority_id
subject_key_id / generation
claim_type
producer_identity
producer_authority_generation
evidence_digest
evidence_class
observed_at
asserted_at
source_clock_evidence
related_event_ids[]
transparency_receipts[]
signatures[]
```

Minimum evidence classes:

1. `CRYPTOGRAPHIC_UNAUTHORIZED_USE` — valid signature/MAC/proof over a canonical object that policy proves the legitimate authority did not authorize.
2. `CUSTODY_CONTROL_LOSS` — HSM/key-custody audit, key export, theft, unauthorized role access, or equivalent control-plane evidence.
3. `PROVIDER_ATTESTED_INCIDENT` — independently authenticated incident statement by the key/HSM/provider authority.
4. `FORENSIC_CORRELATION` — incident-response evidence correlating host/account compromise to key accessibility.
5. `OPERATOR_ASSERTION` — authorized human/operator claim without stronger machine-verifiable evidence.
6. `MONITOR_ANOMALY` — detection signal only; never sufficient alone for global final revocation.
7. `COUNTER_EVIDENCE` — evidence supporting continued legitimate custody/use, used to bound or dispute onset.

Evidence producers are themselves versioned authorities with compromise/freshness history. A compromised evidence producer cannot bootstrap its own trustworthiness merely by signing a new claim.

## 5. Compromise adjudication

Freeze `CompromiseAdjudicationV1`:

```text
adjudication_generation
subject_authority_id
subject_key_id / generation
evidence_claim_ids[]
counter_evidence_claim_ids[]
appraisal_policy_id / version
adjudicator_set[]
independence_profile
result
onset_interval
reliance_scope
damage_assessment_scope
supersedes_generation
transparency_receipts[]
```

Allowed results:

- `NO_COMPROMISE_PROVEN`
- `COMPROMISE_SUSPECTED_LOCAL_QUARANTINE`
- `COMPROMISE_PROVEN_ONSET_BOUNDED`
- `COMPROMISE_PROVEN_ONSET_EXACT`
- `COMPROMISE_PROVEN_ONSET_UNKNOWN_LOWER_BOUND`
- `COMPROMISE_CLAIMS_CONFLICT_UNRESOLVED`
- `FALSE_REVOCATION_CLAIM_PROVEN`

### Conflicting onset claims

Conflicts MUST NOT be resolved by newest timestamp, LWW, majority telemetry, or the most pessimistic/optimistic single producer.

Adjudication compares provenance and independence. If strong evidence proves only `t_good < onset <= t_bad`, the result remains that interval. If two authenticated high-authority claims produce non-overlapping intervals and neither dominates under the frozen appraisal policy, result is `COMPROMISE_CLAIMS_CONFLICT_UNRESOLVED`; consequential positive reliance remains fail-closed for the disputed scope until independent adjudication resolves it.

## 6. False-revocation resistance without weakening containment

A single detector must be able to protect itself quickly, but must not have unilateral power to permanently revoke global authority.

Freeze two distinct control planes:

### Tier Q — immediate scoped quarantine

A sufficiently credible single signal MAY trigger `LOCAL_OR_SCOPED_QUARANTINE` for the relying party or bounded service scope. Consequential use of the disputed key fails closed locally.

Tier Q:
- does not rewrite global authority metadata;
- does not rotate/rebootstrap trust roots;
- does not erase prior receipts;
- carries claim provenance and review deadline;
- remains removable by an independent adjudication proving the claim false or non-applicable.

The review deadline is **not** automatic unrevocation. A real compromise must not become valid merely because a timer expired. Missed review yields `QUARANTINE_REVIEW_OVERDUE`, not restored trust.

### Tier R — global revocation / authority replacement

Global revocation requires an authorized `CompromiseAdjudicationV1` under a threshold policy whose control domains are independent of the single evidence producer/monitor whenever feasible for the impact class.

A single monitor/operator therefore cannot convert an anomaly into permanent ecosystem-wide denial of service.

For high-impact authorities, require at least:
- threshold adjudicator authorization;
- control-domain independence appraisal;
- explicit subject/key/generation binding;
- evidence/counter-evidence digests;
- onset result and affected reliance interval;
- append-only transparency publication;
- recovery/replacement authorization separate from the compromised key.

## 7. Recovery/replacement authority independence

Freeze `RecoveryAuthorityProfileV1` with these non-equivalence rules:

`COMPROMISED_SOURCE_KEY != COMPROMISE_EVIDENCE_PRODUCER != REVOCATION_ADJUDICATOR != RECOVERY_ROOT`

For high-impact source/promise/inventory/checkpoint authorities:

1. The compromised subject key cannot authorize its own trusted replacement.
2. The evidence producer alleging compromise cannot alone select or install the replacement authority.
3. The revocation adjudicator may authorize removal/quarantine under its policy but must not automatically possess signing capability for the replacement lineage.
4. Recovery/root authority should use separate keys, custody, operators/control domains, and preferably offline/threshold storage consistent with TUF/Uptane/Sigstore donor practice.
5. Recovery-key availability must not depend on the same online repository, HSM tenant, cloud account, CI identity, or operator credential whose compromise is being recovered from.
6. A recovery action that cannot demonstrate the required independence becomes `RECOVERY_AUTHORITY_INDEPENDENCE_UNPROVEN` and cannot claim continuous trusted replacement.

Where all recovery/root authority is also compromised or continuity cannot be authenticated, compose with the previously frozen total-loss rule: recovery is external rebootstrap into a new lineage, not an in-band rotation.

## 8. Post-facto reliance invalidation

Late compromise evidence does not mutate history. It appends a new appraisal generation.

Example:

```text
COMPLETENESS_PROVEN(g17)
-> COMPROMISE_EVIDENCE_PUBLISHED(g18)
-> COMPROMISE_ADJUDICATED(onset in (t4,t7], g19)
-> CURRENT_RELIANCE_INVALIDATED_FOR_DEPENDENCIES_IN_INTERVAL(g20)
-> REAPPRAISED_AFTER_RECOVERY(g21)
```

`COMPLETENESS_PROVEN(g17)` and its receipt remain historical facts about what was concluded with evidence available then. They are no longer sufficient for current reliance over affected dependency/time scope.

If onset has an unknown lower bound, current reliance on all historical statements whose validity depends on the possibly compromised key before the first-proven-bad point becomes `UNKNOWN` back to the last independently proven-good point, or further if no such point exists.

## 9. Fraud / contradiction proof classes

Freeze at least these classes:

1. `COMPROMISE_NOTICE_SELF_AUTHORIZED_BY_SUBJECT_KEY`
2. `UNAUTHORIZED_REVOCATION_ISSUER`
3. `SAME_GENERATION_ADJUDICATION_EQUIVOCATION`
4. `NOTICE_TIME_LAUNDERED_AS_ONSET`
5. `ONSET_INTERVAL_EXCLUDES_PROVEN_BAD_EVENT`
6. `ONSET_INTERVAL_PRECEDES_STRONGER_PROVEN_GOOD_BOUND`
7. `EVIDENCE_PRODUCER_COMPROMISED_DURING_CLAIM`
8. `GLOBAL_REVOCATION_FROM_MONITOR_ONLY_SIGNAL`
9. `RECOVERY_KEY_CONTROL_DOMAIN_OVERLAPS_COMPROMISED_DOMAIN`
10. `RECOVERY_SELECTED_SOLELY_BY_EVIDENCE_PRODUCER`
11. `COUNTER_EVIDENCE_SUPPRESSED_FROM_ADJUDICATION`
12. `FALSE_REVOCATION_CLAIM_REPLAY_AFTER_DISMISSAL`
13. `ADJUDICATION_GENERATION_ROLLBACK`
14. `RECOVERY_LINEAGE_PRESENTED_AS_CONTINUOUS_WITHOUT_PROOF`

## 10. RED-first executable matrix

The later LAB-093 executable implementation should start with failures for at least these 48 cases.

### Provenance/authorization
1. unsigned compromise signal cannot globally revoke;
2. ordinary source key cannot self-revoke globally;
3. unauthorized monitor cannot create Tier R revocation;
4. expired evidence-producer authority rejected;
5. revoked evidence-producer generation rejected;
6. valid evidence producer under wrong subject scope rejected;
7. evidence digest substitution rejected;
8. claim replay at lower authority generation rejected.

### Temporal/onset semantics
9. notice time later than first misuse does not truncate affected interval;
10. exact onset rejected when only bounded interval is proven;
11. bounded `(last_good, first_bad]` accepted;
12. missing last-good produces unknown lower bound;
13. counter-evidence moves lower bound forward only when independently authenticated;
14. conflicting non-overlapping strong onset claims become unresolved conflict;
15. newest timestamp does not win conflict;
16. wall-clock skew cannot produce impossible onset outside authenticated event order.

### Quarantine vs global revocation
17. single credible monitor signal triggers local quarantine;
18. same signal cannot rotate root globally;
19. quarantine review deadline expiry does not auto-unrevoke;
20. independent dismissal restores local use only through new adjudication generation;
21. malicious repeated monitor alarms cannot overwrite dismissal generation;
22. global revocation requires configured independent threshold;
23. duplicate identities in one control domain do not satisfy independence threshold;
24. unavailable adjudicators preserve quarantine/UNKNOWN rather than accepting disputed key.

### False-revocation resistance
25. forged evidence claim rejected;
26. authenticated but out-of-scope operator assertion cannot revoke;
27. proven false claim appended, not deleted;
28. false-claim producer loses authority only through separate lifecycle policy;
29. counter-evidence cannot silently erase original allegation receipt;
30. same-generation conflicting revocation/dismissal yields equivocation;
31. stale cached revocation cannot override newer dismissal frontier;
32. stale cached dismissal cannot override newer proven compromise frontier.

### Recovery independence
33. replacement signed only by compromised subject key rejected;
34. replacement selected/signed only by evidence producer rejected;
35. recovery threshold sharing one destructive control domain fails independence;
36. offline threshold across independent domains accepted;
37. recovery key stored in same compromised online repository marked unproven;
38. recovery authority generation rollback rejected;
39. root/recovery compromise invokes total-loss/rebootstrap contract;
40. new lineage cannot be labelled continuous without predecessor/continuity proof.

### Post-facto appraisal/crash durability
41. late bounded compromise invalidates current reliance only for dependent interval/scope;
42. historical receipt remains addressable after invalidation;
43. crash after evidence persistence but before adjudication resumes deterministically;
44. crash after adjudication but before reliance-frontier update cannot resurrect old positive current state;
45. offline verifier catching up sees compromise before accepting later recovery;
46. missing compromise interval during catch-up yields UNKNOWN;
47. same-generation different adjudication digest is fatal conflict;
48. re-appraisal after clean independent recovery creates a new generation without rewriting prior verdicts.

## 11. Decision

Freeze:

`AUTHORITY_COMPROMISE_PROVENANCE_ONSET_FALSE_REVOCATION_RECOVERY_INDEPENDENCE_V1_FROZEN`

Core invariants:

```text
COMPROMISE_SIGNAL != GLOBAL_REVOCATION
NOTICE_TIME != COMPROMISE_ONSET
SINGLE_MONITOR_QUARANTINE != GLOBAL_REVOCATION_AUTHORITY
COMPROMISED_KEY != TRUSTED_RECOVERY_AUTHORITY
EVIDENCE_PRODUCER != SOLE_RECOVERY_SELECTOR
HISTORICAL_RECEIPT != CURRENT_RELIANCE
```

The design preserves rapid fail-closed containment while preventing a lone monitor/operator from obtaining permanent global denial-of-service or replacement-authority power. It also represents compromise onset honestly as an evidence-backed interval when exact dating is impossible.

## 12. Exact next research fallback if executable source remains unavailable

Define **compromise-adjudication transparency/witness quorum, emergency-quarantine expiry/review liveness, recovery-authority rotation ceremonies, and adjudicator-compromise recursion**: how an ecosystem detects split-view adjudication, how a quarantined authority can obtain bounded independent review without automatic unsafe restoration, how recovery roots rotate without collapsing control-domain independence, and what happens when the revocation/adjudication authority itself is compromised.
