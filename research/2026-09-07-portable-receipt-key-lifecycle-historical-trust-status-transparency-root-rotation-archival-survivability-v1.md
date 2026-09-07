# Portable receipt key lifecycle / historical trust-status / transparency-root rotation / archival survivability v1

Status: `PORTABLE_RECEIPT_KEY_LIFECYCLE_HISTORICAL_TRUST_STATUS_TRANSPARENCY_ROOT_ROTATION_ARCHIVAL_SURVIVABILITY_V1_FROZEN`

Date: 2026-09-07
Related: LAB-093/#178, LAB-086/#163, provider-fence portable receipt follow-up

## Problem

`PortableProviderReceiptV1` requires an independently verifiable provider-origin receipt plus retained trust material. A remaining failure exists if a verifier silently evaluates an old receipt using *today's* key status, CA/root set, transparency-log key set, provider account state, or live OCSP/CRL endpoint.

That is incorrect in both directions:

- a key/certificate legitimately trusted when the receipt was produced may expire or be retired later without invalidating the historical event;
- a key discovered to have been compromised *before* or at the event must not remain historically trusted merely because the signature verifies mathematically;
- a compromise discovered later may or may not invalidate earlier receipts depending on the authenticated compromise/invalidity interval and policy;
- provider/account/log decommission can make online status unavailable without making authentic archived evidence false;
- conversely, missing historical status evidence must not be filled in from current mutable control-plane state.

The trust question is therefore time-indexed:

`TRUST(receipt, event_time, policy_generation)`, not `TRUST(receipt, now)`.

## Security objective

A historical provider receipt may support E2/E3/E4 closure only when an offline verifier can reconstruct enough authenticated evidence to decide whether the receipt signer, chain, transparency-log key and timestamp authority were acceptable at the relevant historical time under the frozen verifier policy.

If the required historical state cannot be reconstructed, the verdict is `UNKNOWN_HISTORICAL_TRUST`, not success and not automatic failure.

## Core distinction: expiry, revocation, compromise and retirement

The verifier MUST distinguish these states.

### `EXPIRED_AFTER_EVENT`

The receipt signing certificate/key was valid at event time and later expired normally.

Effect: expiration alone does not invalidate an otherwise valid historical receipt. Historical verification uses the event/timestamp time and retained chain/status evidence.

### `REVOKED_AFTER_EVENT_NON_COMPROMISE`

The certificate/key was later revoked for cessation, supersession, administrative retirement or equivalent reason with no authenticated evidence that the private key was compromised at the event time.

Effect: earlier receipts remain potentially valid if policy permits and retained evidence proves the receipt predates the effective invalidity boundary.

### `COMPROMISED_AFTER_EVENT_WITH_BOUNDED_INVALIDITY`

The key was compromised later, and authoritative evidence supplies an invalidity/compromise time later than the receipt's independently established event time.

Effect: pre-compromise receipts may remain valid under policy; receipts at/after the invalidity boundary fail.

### `COMPROMISED_AT_OR_BEFORE_EVENT`

Authoritative revocation/status evidence indicates the key was invalid at or before the receipt event time.

Effect: historical receipt signature is not trusted even if mathematically correct.

### `STATUS_UNKNOWN`

No retained evidence is sufficient to establish signer status at the relevant event time.

Effect: `UNKNOWN_HISTORICAL_TRUST` for claims that require revocation/compromise checking.

RFC 5280 is the key donor distinction: `invalidityDate` may identify when a key became compromised/invalid and may be earlier than the CRL processing/revocation date. Current-date path validation and historical validation are distinct operations.

## Time anchors

A local `capture_time` is never sufficient to decide historical trust. At least one authenticated time/order anchor is required when later revocation/compromise could affect the verdict.

Accepted evidence, strongest first where applicable:

1. provider-native signed commit/order time with semantics that independently bind the receipt;
2. RFC 3161 timestamp over the exact receipt/signature digest;
3. transparency-log integrated time plus signed inclusion promise/checkpoint when the log semantics and trusted key establish the time bound;
4. independently signed append-only provider digest-chain/checkpoint;
5. weaker observations only for reconciliation, not historical validity.

RFC 3161 explicitly supports the case where a signature is timestamped before later certificate revocation: verification checks that the timestamp falls inside certificate validity and that revocation occurred after the timestamp. A timestamp proves a datum existed by a time; it does not prove provider business semantics by itself.

## `HistoricalTrustBundleV1`

For every R2+ receipt retained for consequential closure, archive a self-contained bundle containing:

- exact raw receipt bytes and media/type identifier;
- exact provider signing certificate/public key and key identifier;
- complete certificate chain used by the frozen policy, including intermediates;
- trust-anchor/root generation and authenticated rotation lineage;
- certificate validity intervals;
- frozen verifier policy generation and digest;
- exact historical semantic schema/revision;
- authenticated event-time evidence;
- CRL and/or OCSP evidence used for signer status, including raw signed bytes;
- `thisUpdate`, `nextUpdate`, `producedAt`, CRL number/base/delta references and issuer identity as applicable;
- `invalidityDate` or equivalent compromise-effective-time evidence when available;
- OCSP `archiveCutoff` when present;
- timestamp token, TSA chain and TSA historical status evidence when an RFC 3161 time anchor is used;
- transparency-log entry, inclusion proof/promise, signed checkpoint/tree head, log identity/key generation and validity window;
- consistency proof or successor checkpoint evidence needed by policy;
- provider/account/service identity at event time;
- archive renewal records protecting the bundle itself against future algorithm/key obsolescence;
- content digests over every retained component.

The bundle MUST remain interpretable without the original SDK and without a live provider/account.

## Historical status evaluation

For receipt `R`, event time `t_e`, signer certificate/key `K`, and policy `P`:

1. verify exact receipt bytes and typed semantics under the frozen schema;
2. verify signature under `K`;
3. reconstruct the certificate/key chain using the retained historical trust-root generation, not today's root set;
4. prove `t_e` using accepted authenticated time/order evidence;
5. verify `t_e` lies inside the signer credential's permitted validity interval;
6. evaluate retained CRL/OCSP/provider-native status evidence according to `P`;
7. if an authenticated invalidity/compromise time `t_i` exists, require `t_e < t_i` for pre-compromise acceptance;
8. if status evidence only says "revoked" but cannot establish whether invalidity preceded `t_e`, return `UNKNOWN_HISTORICAL_TRUST` unless policy explicitly defines a conservative fail-closed result;
9. verify all time-anchor authorities (TSA/log/checkpoint keys) recursively under their own historical trust evidence;
10. verify transparency/checkpoint key generation valid at the log event time;
11. verify no authenticated contradiction/equivocation proof exists in retained evidence;
12. emit a typed verdict rather than collapsing uncertainty into boolean success.

## Verdicts

- `HISTORICALLY_TRUSTED`: all required authenticity, time, status, root lineage and semantic checks pass.
- `HISTORICALLY_UNTRUSTED_PRE_EVENT_COMPROMISE`: signer was invalid/compromised at or before event.
- `HISTORICALLY_UNTRUSTED_ROOT`: no authenticated root lineage authorizes the signer at event time.
- `HISTORICALLY_UNTRUSTED_LOG_KEY`: transparency/checkpoint proof uses a key not authorized for the relevant log interval.
- `HISTORICALLY_CONTRADICTED`: retained authentic evidence contains incompatible trust/status statements that cannot be reconciled under policy.
- `UNKNOWN_HISTORICAL_TRUST`: required historical evidence is missing, ambiguous, outside retention, or cannot be interpreted safely.
- `INVALID`: signature, digest, inclusion proof, chain or typed binding is cryptographically invalid.

## OCSP and CRL retention

Live OCSP is not a historical archive. RFC 6960 defines `archiveCutoff` specifically so an OCSP responder can indicate historical status retention beyond certificate expiry. Therefore:

- retain exact signed OCSP responses used for consequential proof;
- bind them to the target certificate and responder authorization;
- retain their validity/freshness fields and archive-cutoff semantics;
- do not query today's OCSP endpoint and infer past status from a current `good` response;
- do not interpret an OCSP `unknown` as historically good;
- if the historical event predates the response's supported archive window, return `UNKNOWN_HISTORICAL_TRUST` unless another retained source proves status.

For CRLs, retain the exact signed CRL/delta chain needed by policy. `invalidityDate`, where present and authenticated, is materially different from CRL publication/revocation processing time and must be preserved.

## Transparency-log key rotation

Transparency evidence survives key rotation only if the verifier retains the historical log-key generation and authenticated mapping from event/checkpoint time to that generation.

Rules:

- log keys are interval-bound, not timeless;
- planned rotation is additive: old verification keys remain retained for old entries;
- overlapping validity windows are legal and must be handled explicitly;
- a new root/log key does not retroactively re-sign or reinterpret old checkpoints;
- retired log instances remain historical verification authorities for entries they previously authenticated;
- key ID alone is insufficient unless collision/domain semantics are fixed; bind log origin/instance/key generation according to the frozen trust schema;
- if an old checkpoint key is removed from today's trust distribution, historical verification continues using the retained authenticated historical root bundle;
- if no authenticated root lineage connects the historical log key to a trusted generation, return `UNKNOWN`/untrusted according to policy.

Sigstore's trust-root schema is a useful donor: it requires previously used transparency logs/CAs to remain represented for verification of past signatures and explicitly allows overlapping validity windows during rotations.

## Root/CA rotation

Root rotation is append-only for history.

`HistoricalRootGenerationV1` binds:

- root generation ID;
- predecessor digest;
- authorized roots/intermediates/log keys/TSAs;
- validity interval per authority;
- threshold/rotation authorization evidence;
- semantic policy digest;
- successor reference when known.

Current roots cannot silently replace historical roots. A root removed because it is obsolete is different from a root removed because it was discovered compromised. The latter requires an authenticated compromise statement with effective-time semantics; absent that distinction, historical receipts depending on the root become `UNKNOWN` or fail closed according to frozen policy.

## Provider/account decommission

Provider account deletion, tenancy removal, API shutdown or service retirement does not by itself invalidate archived provider-origin receipts. It does, however, remove a potential online reconciliation source.

Before decommission for any resource whose history may support E2/E3/E4 claims, freeze:

- all raw provider receipts;
- provider identity/account/resource bindings;
- public keys/cert chains and historical status material;
- API/receipt schema and verifier conformance corpus;
- final provider checkpoint/readback where meaningful;
- transparency/digest-chain proofs;
- migration/handoff proof to successor provider where one exists.

If a required item cannot be retained, dependent destructive-GC/finalization claims must remain rooted or become `UNKNOWN`.

## Archive survivability and cryptographic renewal

Long-lived proof cannot assume today's signature/hash algorithms remain secure forever. RFC 4998 Evidence Record Syntax provides the reusable mechanism: before a timestamp/signature/hash becomes unreliable, renew evidence with a new archive timestamp; when hash-tree security becomes inadequate, perform hash-tree renewal. RFC 6283 likewise describes preserving certificates/CRLs/OCSP evidence and protecting prior timestamp material with successive archive timestamps.

For this lab:

- archival renewal is additive; never rewrite old receipt bytes;
- new archive evidence covers the prior receipt bundle plus its historical trust/status material;
- renewal occurs before known algorithm/key invalidation when possible;
- timestamp/key compromise discovered after renewal is evaluated against the time of the successor archive timestamp;
- if the evidence chain cannot bridge an algorithm/key transition safely, historical verification becomes `UNKNOWN_ARCHIVE_CHAIN` rather than trusting current crypto retroactively;
- use independent TSAs/algorithms for high-value E3/E4 archives where practical to reduce common-mode failure.

## Compromise discovered after the fact

Policy must distinguish *discovery time* from *effective invalidity time*.

Example:

- receipt authenticated at independent time `t0`;
- key compromise is discovered at `t3`;
- authoritative CA/provider statement says compromise effective `t2`, with `t0 < t2 < t3`.

The receipt may remain historically trusted if all other checks pass.

If the authoritative statement instead says invalid since `t-1 < t0`, the receipt fails historical trust.

If only discovery at `t3` is known and no reliable effective invalidity bound exists, a high-assurance policy cannot infer that the key was safe at `t0`; result is `UNKNOWN_HISTORICAL_TRUST` (or explicitly configured conservative untrusted), not latest-state substitution.

## Trust-status non-equivocation

A CA/provider/status authority can issue contradictory authentic status statements. Therefore historical trust bundles should preserve enough sequence/order evidence to detect:

- overlapping CRLs with incompatible state under the same issuer/number domain;
- contradictory OCSP responses for the same certificate/time interval;
- transparency checkpoints that cannot be connected by valid consistency history where policy requires it;
- provider key-registry statements that roll back key generation;
- root metadata forks.

Authenticity is not non-equivocation. Contradictions invalidate dependent closure until reconciled by a stronger authenticated proof.

## Fraud/contradiction proofs

### `HistoricalTrustSubstitutionProofV1`
A historical receipt was evaluated using a current root/key/status generation without authenticated lineage to the event-time generation.

Effect: verdict invalid; rerun from retained historical bundle.

### `PreEventCompromiseProofV1`
Authentic revocation/provider evidence establishes signer invalidity at or before the independently proven receipt event time.

Effect: receipt cannot support closure.

### `StatusEvidenceOmissionProofV1`
Policy required historical revocation/status evidence but the archive omitted it before provider/CA decommission or retention expiry.

Effect: dependent claim becomes `UNKNOWN_HISTORICAL_TRUST` and remains rooted.

### `TransparencyRootRollbackProofV1`
A verifier maps an old log entry to a later/older unauthorized log-key generation or accepts a checkpoint under a root with no valid rotation lineage.

Effect: transparency proof invalid.

### `ArchiveRenewalGapProofV1`
The evidence chain crosses a known algorithm/key invalidation boundary without a successor archive timestamp established beforehand.

Effect: receipts beyond the last safe archive boundary become `UNKNOWN_ARCHIVE_CHAIN`.

### `HistoricalStatusEquivocationProofV1`
Two authentic status artifacts assert incompatible signer status for the same policy-relevant interval and cannot be ordered/reconciled.

Effect: dependent historical trust is contradicted; no latest-wins resolution.

## RED-first matrix (80 cases)

### A. Basic historical time/status (1-16)
1. valid-at-event certificate later expires: accept historically.
2. receipt event outside certificate validity: reject.
3. local capture time only: insufficient where revocation timing matters.
4. valid RFC3161 token over exact receipt digest: usable time anchor.
5. RFC3161 token over different digest: reject.
6. provider signed event time with no semantics guaranteeing ordering: insufficient for high assurance.
7. revocation date after event, no earlier invalidity: policy-eligible.
8. invalidityDate before event: reject.
9. invalidityDate after event: policy-eligible.
10. revocation known but effective invalidity unknown: `UNKNOWN` under high-assurance policy.
11. current OCSP good used for old event: reject historical substitution.
12. retained OCSP good covering required interval: accept input.
13. OCSP unknown: `UNKNOWN`, never good.
14. stale/out-of-window OCSP: reject as status proof.
15. CRL signature invalid: reject.
16. wrong certificate serial/status binding: reject.

### B. OCSP/CRL archival semantics (17-32)
17. OCSP archiveCutoff covers event: eligible.
18. event earlier than archiveCutoff support: `UNKNOWN` absent other proof.
19. responder unauthorized for target certificate: reject.
20. OCSP response bytes reserialized before signature check: reject unless canonical provider format permits.
21. CRL issuer mismatch: reject.
22. delta CRL without required base: `UNKNOWN`/invalid per policy.
23. CRL number rollback: contradiction.
24. two authentic incompatible CRLs same order domain: contradiction.
25. two authentic incompatible OCSP responses same interval: contradiction.
26. retained status proof deleted after GC: dependent closure stale/unknown.
27. provider status endpoint decommissioned but complete retained evidence exists: historical verify still works.
28. provider status endpoint decommissioned and evidence missing: `UNKNOWN`.
29. certificate expired before OCSP query but archiveCutoff proves retained history: eligible.
30. status artifact timestamp after event but semantically covers event: eligible if policy allows.
31. status artifact only proves state at later instant, not event interval: insufficient.
32. forged invalidityDate in unsigned metadata: ignored/reject.

### C. Root/CA/key rotation (33-48)
33. planned root rotation with authenticated predecessor lineage: old receipt verifies under old root.
34. old root absent from today's store but retained historically: still verifiable.
35. current root silently substituted for historical root: reject.
36. rotation lineage broken: `UNKNOWN_HISTORICAL_TRUST`.
37. intermediate rotated after event: old chain retained and verifies.
38. old signer key retired normally: historical receipt remains eligible.
39. signer key compromised before event: reject.
40. signer key compromised after event with bounded invalidity: pre-boundary eligible.
41. compromise discovered later, effective time unknown: `UNKNOWN` high assurance.
42. root compromise effective before event: reject dependent chain.
43. root compromise effective after independently archived successor timestamp: prior chain may survive under renewal policy.
44. root metadata fork: contradiction.
45. duplicate key ID under different authority domain: reject ambiguous lookup.
46. expired root evaluated only against current time: historical-substitution regression.
47. key algorithm later deprecated but archive renewal predates deprecation: verify through renewal chain.
48. key algorithm deprecated with no safe renewal bridge: `UNKNOWN_ARCHIVE_CHAIN`.

### D. Transparency-log rotation (49-64)
49. historical log key retained with event validity window: verify.
50. planned log rotation with overlapping windows: both accepted only in their authorized windows.
51. old log key removed from live TUF but preserved in authenticated historical root: verify offline.
52. old log key removed everywhere: `UNKNOWN`.
53. checkpoint signed by unauthorized future key for old event: reject.
54. checkpoint key ID collision/ambiguous log instance: reject.
55. inclusion proof valid but checkpoint signature invalid: reject.
56. valid inclusion promise but no policy-required inclusion proof/checkpoint: insufficient.
57. transparency inclusion proves existence but not provider fencing semantics: do not upgrade claim.
58. two checkpoints with valid consistency path: eligible.
59. incompatible checkpoints with no consistency reconciliation: contradiction.
60. log retired after event with complete checkpoint archive: historical verification works.
61. log retired with missing historical key: `UNKNOWN`.
62. log root rotated without authenticated lineage: reject.
63. current log key used to reinterpret old signed entry: reject.
64. historical log semantic schema unavailable: `UNKNOWN_UNVERIFIABLE_SCHEMA`.

### E. Decommission, offline archive and renewal (65-80)
65. provider account deleted after complete freeze: verify offline.
66. account deleted before key/status material retained: `UNKNOWN`.
67. provider A→B migration with authenticated handoff and retained A history: both domains verifiable.
68. migration without retained A schema: old receipts unknown.
69. archive timestamp renewal before TSA certificate expiry: chain eligible.
70. renewal after predecessor TSA key known compromised before renewal: reject chain.
71. timestamp renewal uses new TSA but omits predecessor evidence: insufficient.
72. hash algorithm weakens; hash-tree renewal completed beforehand: chain eligible.
73. hash algorithm weakens with only same-hash timestamp renewal: insufficient when hash itself is the broken primitive.
74. archive object bytes mutated after timestamp: reject digest binding.
75. historical CRL/OCSP added after an archive timestamp without later timestamp covering addition: do not treat as protected historical evidence.
76. successor archive timestamp covers added historical status material before prior evidence invalidates: eligible.
77. archive bundle replicated to offline storage with exact digests: verification unchanged.
78. archive loses frozen verifier policy: `UNKNOWN` for policy-sensitive claim.
79. archive loses semantic schema but retains signatures: authenticity may be mathematical, claim semantics unknown.
80. complete self-contained bundle survives provider/CA/log shutdown and verifies with independent implementation: `HISTORICALLY_TRUSTED`.

## Acceptance criteria for production use

A provider receipt set may be called `ARCHIVAL_SURVIVABLE` only if:

- exact receipt/provider-origin bytes are retained;
- event time/order is independently anchored where historical status requires it;
- historical signer chain/root generation is retained with authenticated lineage;
- required CRL/OCSP/provider-native status evidence is retained as signed raw bytes;
- compromise-effective time is distinguished from discovery/processing time where policy depends on that distinction;
- transparency-log key generations/checkpoints are retained for old entries;
- frozen schemas and verifier policies remain available offline;
- provider/account decommission does not require a live lookup for authenticity/status already claimed;
- cryptographic archive renewal is performed before known proof primitives become unsafe, or the result becomes `UNKNOWN`;
- contradictory authentic trust/status evidence is surfaced rather than latest-wins resolved.

## Primary donors and reusable mechanisms

- **RFC 5280** — historical certificate validation is distinct from current-time validation; `invalidityDate` records when a key/certificate became invalid and can precede CRL processing time.
- **RFC 6960** — signed OCSP status plus `archiveCutoff` for retained historical revocation information.
- **RFC 3161** — independently timestamp a signature/digest so later verification can compare signing time with certificate revocation time.
- **RFC 4998 / RFC 6283** — Evidence Record Syntax, archive timestamp renewal and hash-tree renewal for long-term proof survivability; preserve certificates/CRLs/OCSP evidence inside renewed chains.
- **Sigstore trust-root / bundle model** — historical CAs/transparency logs must remain represented for past verification; validity windows may overlap during rotations; bundles retain transparency/time verification material for offline verification.

## Frozen decision

`PORTABLE_RECEIPT_KEY_LIFECYCLE_HISTORICAL_TRUST_STATUS_TRANSPARENCY_ROOT_ROTATION_ARCHIVAL_SURVIVABILITY_V1_FROZEN`.

No LAB-093 production implementation may equate current trust state with historical trust, discard old root/log-key generations after rotation, treat certificate expiry as retroactive invalidation, assume later key compromise necessarily invalidates all earlier receipts, or preserve receipts without the historical status/time/schema/policy evidence required to verify them independently after provider decommission.
