# Source / Promise Authority Transparency, Compromise Propagation, Conflicting Views, and Post-Facto Completeness Invalidation — V1 Frozen

Date: 2026-09-08
Status: `SOURCE_PROMISE_AUTHORITY_TRANSPARENCY_COMPROMISE_PROPAGATION_POST_FACTO_INVALIDATION_V1_FROZEN`
Parent: LAB-093 / #178
Execution status: architecture/research only. Exact repository execution remained unavailable in this run because direct `git clone --no-checkout` failed before repository access with DNS `Could not resolve host: github.com` (exit 128). No behavioral or compile PASS is claimed here.

## Problem

The previous source-ingestion contracts separated logical sources, source-inventory authority, per-source identity authority, and ingestion-promise authority. That still leaves a current-validity gap:

1. an offline monitor may miss a source/inventory/promise authority revocation or compromise notice;
2. two monitors may be shown different authority metadata for the same generation;
3. a previously valid `PREFIX_COMPLETE_PROVEN` / convergence-completeness verdict may later depend on a key whose compromise interval is discovered only after the verdict was issued;
4. a transparency receipt can prove that a statement was registered, but cannot by itself decide which of several contradictory authenticated authority statements should be trusted now.

This contract freezes the missing propagation and re-appraisal semantics.

## Primary invariants

`AUTHENTICATED_AUTHORITY_STATEMENT != CURRENT_AUTHORITY_VIEW`

`TRANSPARENCY_RECEIPT != AUTHORITY_TRUTH`

`HISTORICAL_COMPLETENESS_VERDICT != CURRENTLY_RELIABLE_COMPLETENESS_VERDICT`

`LATE_COMPROMISE_NOTICE != HISTORY_REWRITE`

`SAME_GENERATION_CONFLICT != LAST_WRITER_WINS`

`OFFLINE_MONITOR_CATCHUP != ACCEPT_NEWEST_DOCUMENT`

## Donors and factual basis

### TUF

The Update Framework uses versioned root metadata and requires clients to walk intermediate root versions. A new root must be authorized by both the immediately preceding root threshold and its own threshold; rollback/freeze protection is explicit. If a threshold of root keys is compromised, normal in-band continuity is no longer sufficient and out-of-band recovery is required.

Donor mechanism: monotonic authority generations, predecessor+successor authorization, client-retained trusted version/freshness state, and explicit failure of rollback/skip attempts.

Source: https://theupdateframework.github.io/specification/latest/

### RFC 9943 / SCITT

SCITT separates Issuers from Transparency Services. A receipt proves registration of a Signed Statement in a verifiable data structure; transparency provides auditability/accountability and can expose equivocation, but it does not prevent a compromised Issuer from making a false statement. Relying parties decide which Issuers/Transparency Services they trust. RFC 9943 also explicitly treats notification/discovery of changes as outside the architecture.

Donor mechanism: issuer-authenticated statements + independent transparency registration + auditor detection of equivocation. Important negative lesson: a receipt is evidence that an assertion existed, not proof that its semantic authority was valid.

Source: https://www.rfc-editor.org/rfc/rfc9943.html

### RFC 9162 / Certificate Transparency

Certificate Transparency uses append-only Merkle history, signed tree checkpoints and consistency proofs. Monitors/auditors can detect inconsistent views; signed inclusion promises/checkpoints create durable evidence for later contradiction analysis.

Donor mechanism: immutable checkpoint history, consistency proofs, gossip/witness-style comparison, and durable evidence that cannot be silently rewritten after a compromise notice.

Source: https://www.rfc-editor.org/rfc/rfc9162.html

## Contract objects

### `AuthorityTransparencyStatementV1`

Canonical signed statement for any of:
- `SOURCE_INVENTORY_AUTHORITY_GENERATION`
- `SOURCE_IDENTITY_AUTHORITY_GENERATION`
- `INGESTION_PROMISE_AUTHORITY_GENERATION`
- `AUTHORITY_REVOCATION`
- `AUTHORITY_COMPROMISE_NOTICE`
- `AUTHORITY_RETIREMENT`
- `AUTHORITY_REPLACEMENT`

Required fields:
- `authority_kind`
- `authority_lineage_id`
- `generation`
- `statement_kind`
- `subject_key_ids`
- `valid_from`
- `valid_until` when bounded
- `compromise_interval_start` / `compromise_interval_end` when known
- `predecessor_statement_digest`
- `policy_digest`
- `statement_digest`
- signatures satisfying the authority-transition policy

A compromise notice with unknown onset MUST encode that uncertainty explicitly; it must not silently default onset to notice publication time.

### `AuthorityTransparencyReceiptSetV1`

Contains one or more independent transparency receipts for the exact `AuthorityTransparencyStatementV1` digest.

Assurance profiles:
- `T0_NONE`: signed authority statement only;
- `T1_SINGLE_LOG`: one transparency service;
- `T2_MULTI_LOG`: receipts from independently operated transparency services;
- `T3_WITNESSED_MULTI_LOG`: independent logs plus consistency/witness evidence.

Receipt presence never upgrades an unauthorized statement into an authorized authority transition.

### `TrustedAuthorityFrontierV1`

Per monitor / relying party retained state:
- authority kind + lineage;
- highest accepted generation;
- accepted statement digest;
- accepted compromise/revocation frontier;
- transparency checkpoints / witness frontier;
- freshness deadline;
- unresolved conflicting-view set.

Rules:
- lower generation is rollback;
- same generation + different authenticated statement digest is equivocation/conflict;
- higher generation is not accepted merely because it is newer: predecessor continuity and authorization must verify;
- a newer wall-clock timestamp never defeats a lower trusted generation rule;
- unresolved conflict blocks current positive completeness reliance for evidence depending on that authority.

### `CompletenessRelianceReappraisalV1`

Records re-evaluation of an earlier completeness verdict after authority status changes.

Fields:
- historical verdict digest/generation;
- dependency authority/key set;
- newly learned revocation/compromise/conflict statement digests;
- affected evidence interval;
- appraisal result;
- new current-reliance state;
- predecessor reappraisal digest.

Possible results:
- `CURRENT_RELIANCE_RETAINED`
- `CURRENT_RELIANCE_INVALIDATED`
- `CURRENT_RELIANCE_UNKNOWN_COMPROMISE_ONSET`
- `CURRENT_RELIANCE_UNKNOWN_AUTHORITY_CONFLICT`
- `HISTORICAL_ONLY_NOT_CURRENTLY_RELIABLE`

The original verdict and transparency receipt remain immutable historical facts.

## Compromise-notification semantics

### Known compromise onset

If key K is proven compromised over `[t0, t1]`, every source/frontier/promise/inventory statement whose authority depends on K during that interval must be re-appraised.

Statements provably issued before `t0` may retain historical/current reliance subject to normal freshness and successor-policy checks. Statements inside the interval cannot remain current-trusted solely because their signatures still verify cryptographically.

### Unknown compromise onset

If onset is unknown, the system MUST NOT pretend only post-notice statements are affected.

Any current completeness verdict whose proof critically depends on that key and cannot establish issuance outside the possible compromise interval becomes:

`CURRENT_RELIANCE_UNKNOWN_COMPROMISE_ONSET`

This is fail-closed for consequential current-completeness claims, while preserving historical receipts.

### Compromise notice publication

The notice itself must be authorized according to a separate compromise/recovery policy. A compromised ordinary source key cannot unilaterally declare its own compromise state authoritative if that would let an attacker manipulate validity windows.

For high-assurance profiles, compromise notices should be independently transparent and, where practical, witnessed/multi-log registered.

## Conflicting authority views

### Same generation, different authenticated contents

If two validly signed statements claim the same `(authority_lineage_id, authority_kind, generation)` but different digests, state becomes:

`AUTHORITY_EQUIVOCATION_CONFLICT_NO_CURRENT_POSITIVE_RELIANCE`

Forbidden conflict resolvers:
- newest timestamp;
- last writer wins;
- first seen wins;
- majority CDN response;
- lexicographically smaller/larger digest;
- higher transparency-log count when the underlying authority statements themselves conflict.

Transparency/witness infrastructure is used to make both statements durable and cross-visible, not to invent semantic precedence.

Resolution requires an explicitly authorized later generation that consumes/references the conflict, or a governed recovery/rebootstrap mechanism from the prior frozen authority lifecycle contracts.

### Split transparency views

If the same transparency service exposes incompatible checkpoints, preserve both checkpoint proofs as equivocation evidence. Do not discard the losing view after choosing one.

If independent logs disagree only because one is delayed, freshness policy may classify one as stale after consistency/catch-up succeeds. If they commit to incompatible statements under the same required authority generation, treat it as authority conflict rather than replication lag.

## Offline monitor recovery

An offline monitor MUST NOT recover by fetching only the latest authority document.

Catch-up order:
1. start from retained `TrustedAuthorityFrontierV1`;
2. obtain every missing sequential authority generation or a cryptographically valid checkpoint/proof-of-prefix covering them;
3. obtain all revocation/compromise notices whose applicability intersects the missed interval;
4. verify transparency checkpoint consistency against the retained checkpoint frontier;
5. compare independent log/witness views where the assurance profile requires them;
6. reconstruct current source-inventory / source-identity / promise-authority chains;
7. re-appraise completeness verdicts that depended on any affected key/generation;
8. only then advance the trusted frontier.

If retained checkpoint continuity cannot be reconstructed because required history has expired/disappeared, state becomes:

`AUTHORITY_CURRENT_STATUS_UNKNOWN_MISSED_INTERVAL`

A fresh latest checkpoint can re-establish a new local bootstrap only under an explicitly defined rebootstrap policy; it cannot prove that no relevant revocation occurred during the missing interval.

## Post-facto completeness invalidation

Example:

- `g7 PREFIX_COMPLETE_PROVEN` is issued using source-authority key K;
- later, a valid compromise notice proves K was compromised before evidence supporting g7 was issued;
- g7's receipt remains historically valid as proof that the system once asserted completeness;
- current reliance changes to `CURRENT_RELIANCE_INVALIDATED` or `UNKNOWN_COMPROMISE_ONSET`;
- remediation produces a new verdict generation after reconstructing evidence under uncompromised authority.

History must be represented as an append-only chain, for example:

`PROVEN(g7) -> COMPROMISE_DISCOVERED(g8) -> RELIANCE_INVALIDATED(g9) -> REAPPRAISED/PROVEN(g10)`

Never rewrite g7 to say it never existed.

## Freshness and notification bounds

Every current-trust policy MUST define:
- maximum authority-metadata age;
- maximum compromise-notice propagation age;
- maximum transparency checkpoint age;
- offline grace window by consequence class.

Past the bound, absence of a revocation notice is not proof of no revocation. Current positive reliance becomes stale/unknown until catch-up completes.

This intentionally separates availability from integrity: a partition may deny current positive decisions without granting stale authority.

## Independence requirements

A high-assurance compromise propagation design should avoid a single actor controlling all of:
- authority key issuance;
- compromise-notice issuance;
- transparency registration;
- transparency checkpoint signing;
- witness/auditor operation;
- completeness appraisal.

Distinct keys under the same operator/control plane are not automatically independent control domains.

## Fraud / contradiction proof classes

1. `AUTHORITY_GENERATION_ROLLBACK_PROOF`
2. `AUTHORITY_SAME_GENERATION_EQUIVOCATION_PROOF`
3. `AUTHORITY_SKIPPED_PREDECESSOR_PROOF`
4. `UNAUTHORIZED_COMPROMISE_NOTICE_PROOF`
5. `COMPROMISE_INTERVAL_DEPENDENCY_PROOF`
6. `UNKNOWN_COMPROMISE_ONSET_RELIANCE_PROOF`
7. `TRANSPARENCY_CHECKPOINT_SPLIT_VIEW_PROOF`
8. `TRANSPARENCY_HISTORY_ROLLBACK_PROOF`
9. `MISSED_REVOCATION_INTERVAL_PROOF`
10. `STALE_AUTHORITY_METADATA_PROOF`
11. `POST_FACTO_COMPLETENESS_INVALIDATION_PROOF`
12. `CONFLICT_SUPPRESSION_PROOF`

## RED-first matrix (48 cases)

### Authority lifecycle / transparency — 1..12
1. valid sequential source-inventory authority rotation;
2. valid sequential source-identity authority rotation;
3. valid sequential promise-authority rotation;
4. lower generation replay rejected;
5. skipped generation rejected;
6. successor lacking predecessor authorization rejected;
7. predecessor-authorized successor lacking self-threshold rejected;
8. same generation/same digest replay idempotent;
9. same generation/different digest -> conflict;
10. one transparent conflicting statement does not defeat another valid conflict;
11. T2 multi-log identical statement accepted at stronger assurance;
12. receipt for unauthorized statement does not authorize it.

### Compromise propagation — 13..24
13. known compromise onset after statement issuance leaves prior evidence eligible;
14. known onset before evidence issuance invalidates current reliance;
15. unknown onset yields UNKNOWN for dependent evidence;
16. late notice reopens an already closed completeness verdict;
17. historical receipt retained after invalidation;
18. compromised ordinary key cannot self-authorize validity-window manipulation;
19. authorized emergency compromise notice accepted;
20. stale monitor missing notice cannot continue positive reliance past freshness bound;
21. duplicate identical compromise notice idempotent;
22. conflicting compromise intervals at same notice generation -> conflict;
23. retirement without compromise does not retroactively invalidate valid historical signatures;
24. later proof narrowing a previously unknown interval requires a new reappraisal generation, not history rewrite.

### Offline monitor catch-up — 25..34
25. sequential catch-up through all missing generations succeeds;
26. catch-up using valid proof-of-prefix/checkpoint succeeds where policy allows;
27. latest-only document without continuity rejected;
28. missed revocation discovered during catch-up invalidates dependent verdict;
29. transparency checkpoint rollback rejected;
30. same checkpoint generation/different root -> split view;
31. archive gap with no proof of continuity -> UNKNOWN;
32. after explicit rebootstrap, new trust lineage is marked as such;
33. offline monitor cannot resurrect superseded key from cached state;
34. freshness expires during catch-up -> no positive decision until completion.

### Post-facto verdict semantics — 35..42
35. uncompromised dependency set retains current reliance;
36. one compromised required authority invalidates composite completeness;
37. compromised non-required auxiliary signer does not invalidate unrelated verdict;
38. unknown-onset required dependency -> UNKNOWN not INVALIDATED-as-proven;
39. reclosure creates a new verdict generation;
40. reclosure must reference intervening contradiction/invalidation;
41. old receipt remains verifiable after reclosure;
42. deletion of invalidation event detected by checkpoint/prefix reconciliation where evidence exists.

### Crash / conflict / independence — 43..48
43. crash after notice registration before local frontier update recovers idempotently;
44. crash after local quarantine before transparency receipt retrieval remains fail-closed;
45. same operator two logs does not satisfy two-control-domain profile;
46. witness disagreement blocks current positive reliance until resolved;
47. notification channel outage does not imply absence of compromise;
48. LWW/newest-timestamp conflict resolver is explicitly rejected.

## Engineering consequences for future executable LAB-093 work

When exact source execution becomes available, implementation should not begin by adding more mutable flags to the existing ledger. The contract belongs in the authority/evidence boundary and must compose with LAB-087 process isolation.

Minimum executable slice should be tests first:
1. trusted frontier rejects same-generation conflicting authority views;
2. offline monitor cannot accept latest-only authority state after a missed interval;
3. late compromise notice reclassifies current reliance on an earlier completeness verdict without deleting or mutating the historical verdict;
4. transparency receipt for an unauthorized/conflicting authority statement does not make it current authority;
5. reclosure requires a fresh verdict generation and explicit dependency on the intervening invalidation.

## Decision

Freeze `SOURCE_PROMISE_AUTHORITY_TRANSPARENCY_COMPROMISE_PROPAGATION_POST_FACTO_INVALIDATION_V1_FROZEN`.

This is a design/evidence freeze only. It does not substitute for executable RED/GREEN proof, LAB-086 completion, or LAB-087 isolation composition.

## Next distinct research slice if exact execution remains unavailable

`authority-compromise evidence provenance / compromise-onset adjudication / false-revocation resistance / recovery-key independence`:

Define who can prove a compromise, how conflicting compromise-onset claims are appraised, how to prevent a malicious monitor/operator from weaponizing revocation to cause permanent denial of service, and how recovery/replacement authority remains independent from both the compromised source key and the evidence producer that alleges compromise.
