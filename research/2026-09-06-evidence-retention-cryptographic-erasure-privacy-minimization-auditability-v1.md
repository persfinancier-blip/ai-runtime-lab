# Evidence retention / cryptographic-erasure / privacy minimization versus auditability V1

Status: `EVIDENCE_RETENTION_CRYPTOGRAPHIC_ERASURE_PRIVACY_MINIMIZATION_AUDITABILITY_V1_FROZEN`

Date: 2026-09-06

Scope: LAB-093 retained-authority evidence plane and all dependent retry / UNKNOWN / manual-resolution / archive / DR / transport-observer contracts.

## Problem

The evidence plane must remain strong enough to prove authority, retry identity, crash ambiguity, quarantine/recovery history and manual reconciliation without becoming a second durable copy of provider payloads, credentials, tokens, personal data or commercial secrets.

The previous capacity/archive contract freezes when evidence may be physically reclaimed. This contract freezes **what may enter durable evidence in the first place**, what may be represented only by commitments, and when cryptographic erasure is valid without destroying authority-critical continuity.

## Primary-source donors

1. **GDPR Article 5**: personal data must be adequate, relevant and limited to what is necessary; identifiable data may be retained no longer than necessary; processing must preserve integrity/confidentiality. This is used as a minimization/storage-limitation donor, not as a legal determination for any specific deployment.
   - https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32016R0679
2. **EDPB data-protection basics**: process only necessary/proportionate personal data and define retention/deletion procedures by purpose.
   - https://www.edpb.europa.eu/sme/learn-the-basics/data-protection-basics_en
3. **OWASP Logging Cheat Sheet**: access tokens, passwords, DB connection strings, encryption keys and sensitive personal data should generally not be logged directly; use removal, masking, sanitization, hashing or encryption where appropriate.
   - https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html
4. **NIST SP 800-88 Rev. 2**: sanitization must make target data recovery infeasible for the required effort level; cryptographic erase is key sanitization applied to keys protecting encrypted target data. CE therefore depends on complete key/copy coverage and is not equivalent to deleting an application row.
   - https://csrc.nist.gov/pubs/sp/800/88/r2/final
   - https://csrc.nist.gov/glossary/term/cryptographic_erase

## Frozen invariants

### 1. Raw provider material is denied by default

The durable evidence schema MUST be allowlist-based. Unknown fields are `DO_NOT_PERSIST`, not `LOG_FOR_DEBUG`.

The following classes MUST NOT enter durable authority evidence in plaintext or reversibly encoded form:

- passwords, API keys, bearer/access/refresh/session tokens;
- private signing/encryption keys, seed material, recovery secrets;
- database connection strings or credentials;
- cookie/session values unless transformed into a non-reversible correlation commitment;
- raw Authorization / Proxy-Authorization headers;
- complete raw provider request or response bodies by default;
- provider body/header fields classified by the deployment as personal, payment, health, identity, customer-secret or commercially sensitive data unless an explicit field-level retention contract proves necessity;
- ephemeral signing values whose exact value is not part of provider business/idempotency semantics.

No debug mode may widen this set on a consequential production path.

### 2. Minimize before the pre-I/O durability barrier

Redaction/tokenization/commitment derivation MUST happen **before** `SINK_ENTERED` or equivalent pre-I/O durable evidence is written.

A system is non-conformant if it writes the raw request to SQLite/WAL/journal/tmp/spool first and redacts it later. Post-write scrubbing does not repair backups, WAL pages, crash dumps, snapshots or prior archive copies.

The allowed flow is:

`request -> field classifier -> minimizer -> canonical authority projection -> commitments/selective fields -> durable barrier -> provider I/O`

If classification/minimization cannot prove the output satisfies the current evidence policy generation, consequential I/O fails closed.

### 3. Authority-critical evidence is a canonical projection, not a raw payload copy

For each consequential attempt, persist the minimum set required to reconstruct authority decisions and prove retry identity:

- operation/effect/attempt IDs;
- provider/account/region/API/surface identifiers required by the admitted provider capability contract;
- exact idempotency/provider-request identity when it is non-secret and safe to retain, otherwise a keyed commitment plus the separately protected replay capsule reference;
- immutable authority/replay-capsule/extractor/profile generations;
- canonical semantic-request commitment;
- selected non-sensitive semantic fields whose plaintext value is required for deterministic recovery or human reconciliation;
- lifecycle/evidence states (`SEND_STARTED`, `SINK_ENTERED`, `UNKNOWN`, provider terminal result, etc.);
- authenticated parent/global evidence frontier bindings;
- timestamps/sequence numbers required for ordering, without copying unrelated transport metadata.

The projection schema itself is versioned and authenticated. A future implementation may add a field only by changing the policy generation and proving why the field is necessary.

### 4. Commitments must not become offline secret-recovery oracles

A plain unsalted hash is insufficient for low-entropy sensitive values such as short IDs, emails, phone numbers, tokens with recognizable structure or small enumerated fields.

Use one of:

- canonical digest only for high-entropy/non-sensitive material where offline enumeration is not a meaningful risk;
- domain-separated keyed commitment/HMAC under a dedicated evidence-commitment key for sensitive or enumerable values;
- random tokenization mapping stored in a separately protected vault when later plaintext recovery is explicitly required.

Commitment keys MUST be separate from provider credentials, encryption-at-rest keys, recovery signing keys and database keys. Their authority is verification only; possession must not allow provider mutation.

### 5. Equality and replay proofs are purpose-specific

The system MUST NOT retain plaintext merely because it may be useful later.

For each retained field define one of four evidence purposes:

- `ORDER_ONLY`: sequence/state evidence; no value retention;
- `EQUALITY_ONLY`: commitment proves same semantic value across attempts;
- `RECOVERY_REQUIRED`: plaintext/tokenized value is required to reconstruct the exact admitted provider request;
- `HUMAN_RECONCILIATION_REQUIRED`: selectively disclosed value is required to resolve an `UNKNOWN` case.

`EQUALITY_ONLY` fields are never promoted to plaintext retention for convenience.

### 6. Replay material and audit evidence are split

If exact request reconstruction requires sensitive material, store it in a separately encrypted **replay capsule**, not in the general audit log.

The general evidence plane stores only:

- replay-capsule content digest;
- capsule policy/key generation;
- creation/expiry state;
- provider-semantic binding;
- authorization/consumption state.

Replay capsule read/decrypt authority is strictly narrower than evidence verification authority. Routine audit/query access cannot decrypt it.

### 7. Envelope encryption and cryptographic erasure

Sensitive replay/manual-resolution material that must temporarily remain recoverable MUST be envelope-encrypted with per-object or narrow-cohort data-encryption keys (DEKs). DEKs are wrapped by a key-encryption key (KEK) or external KMS/HSM key.

Cryptographic erasure is valid only when all of the following are proven:

1. every retained plaintext/reversible copy is covered by the erased key hierarchy;
2. no plaintext exists in WAL/journal/tmp/crash-dump/export/archive/backup/object-store copies outside that coverage;
3. all wrapped copies of the relevant DEK and any escrow/export copies are destroyed or rendered unusable;
4. the cryptographic algorithm/key size and implementation remain approved for the confidentiality requirement;
5. the sanitized object cannot be reconstructed from derived stores, search indexes, analytics replicas or debug captures;
6. deletion/erase is durably recorded as an authenticated evidence transition without preserving the erased secret itself.

Deleting a row, deleting one DEK wrapper while another survives, or dropping a KMS alias is **not** sufficient evidence of CE.

### 8. Authority evidence survives secret erasure

Erasing sensitive material MUST NOT erase the authenticated evidence required to prove:

- that an attempt existed;
- which authority/policy/profile generation admitted it;
- its semantic commitment;
- whether provider I/O may have occurred;
- whether it is unresolved `UNKNOWN`/manual-resolution;
- what evidence was destroyed, under which authorized retention transition, and at which global frontier.

After CE, the record becomes intentionally non-replayable/non-recoverable unless another authorized copy is explicitly part of the retention contract. CE can remove the ability to resend while preserving proof that the original attempt occurred.

### 9. UNKNOWN/manual-resolution pinning is field-specific, not raw-record pinning

An unresolved `UNKNOWN` does not automatically authorize indefinite retention of a raw payload.

Before first send, the provider capability contract MUST declare the minimum reconciliation projection needed for an UNKNOWN case. Only those fields/commitments become security-pinned.

If human reconciliation genuinely requires a sensitive value, it belongs in the separately encrypted manual-resolution/replay capsule with explicit access logging, expiry and destruction semantics.

### 10. Legal/privacy hold cannot silently mint effect authority

A legal/privacy/business retention hold may extend evidence retention, but MUST NOT:

- reactivate an expired retry capsule;
- re-enable a consumed/revoked provider token;
- bypass quarantine;
- convert an audit-only copy into SEND authority;
- restore cryptographically erased provider credentials.

Retention authority and consequential-effect authority are disjoint capabilities.

Conversely, a privacy deletion request cannot automatically delete evidence that remains necessary for a genuine unresolved security/financial/legal obligation; that conflict requires the applicable policy/legal decision layer, not silent runtime improvisation.

### 11. Archives/backups inherit classification and erasure scope

Every archive, backup, replica and exported investigation bundle carries the evidence-policy/key-generation metadata of its source.

Backup completion does not permit the live system to forget where sensitive encrypted material was copied. A CE operation is complete only when the erasure manifest proves coverage of every in-scope copy or proves that those copies are independently inaccessible under an equivalent destruction schedule.

### 12. No reversible redaction

Masking such as `abcd****wxyz`, truncation, base64, reversible substitution or deterministic encryption is not anonymization and does not count as erasure.

Such transformations may be used only when their residual disclosure/re-identification risk is explicitly accepted by the field policy and they serve a concrete recovery purpose.

### 13. Search/index/telemetry containment

Authority evidence MUST NOT be automatically mirrored into general-purpose logs, traces, metrics labels, exception strings, search indexes or analytics systems.

Derived observability systems receive only approved non-sensitive identifiers/aggregates. Exception handling must sanitize provider response/request fragments before recording them.

### 14. Policy generations are monotonic and fail closed

Every evidence record binds `evidence_minimization_policy_generation` and `commitment_scheme_generation`.

A process with an unknown/older policy may verify old records according to their historical rules but may not create new consequential evidence under an unrecognized generation.

A policy upgrade that reduces retained fields is directional: it cannot claim old raw copies disappeared until archival/backup/CE continuity proves destruction.

## Canonical evidence object sketch

```text
EvidenceRecordV1 {
  evidence_id
  parent_evidence_digest
  global_frontier
  operation_id
  effect_id
  attempt_id
  provider_scope_projection
  provider_request_identity_commitment
  semantic_request_commitment
  replay_capsule_digest?
  selected_reconciliation_fields[]
  authority_generations
  transport_profile_generation
  evidence_minimization_policy_generation
  commitment_scheme_generation
  lifecycle_state
  retention_class
  pin_reasons[]
  crypto_erasure_state
}
```

No generic `raw_request`, `raw_response`, `headers_json`, `body_blob`, `debug_context` or arbitrary `metadata` map is admitted.

## Retention classes

- `AUTHORITY_CORE`: authenticated ordering/authority/state commitments; retained according to audit/security contract.
- `RECONCILIATION_PINNED`: minimal UNKNOWN/manual-resolution fields; pinned until authorized terminal resolution.
- `REPLAY_SECRET`: separately encrypted exact reconstruction material; short-lived and one-shot where possible.
- `DIAGNOSTIC_EPHEMERAL`: non-authority diagnostic data; no consequential path may require it and it must not contain denied fields.
- `ERASED_COMMITMENT_ONLY`: secret material destroyed; authority commitment/history remains.

## RED-first matrix — 72 cases

### A. Pre-persistence minimization (1-12)
1. Authorization header never reaches SQLite.
2. Access token never reaches WAL/journal.
3. Password field removed before `SINK_ENTERED`.
4. Private key/seed field denied.
5. DB connection string denied.
6. Unknown request field fails closed.
7. Debug flag cannot widen allowlist.
8. Exception string containing token is sanitized.
9. Provider raw response body denied by default.
10. Temp/spool path cannot receive pre-redaction body.
11. Crash between minimizer and barrier leaves no raw durable copy.
12. Policy-generation mismatch blocks send.

### B. Commitment safety (13-24)
13. High-entropy non-sensitive equality digest accepted.
14. Low-entropy PII plain hash rejected.
15. Domain-separated keyed commitment accepted.
16. Cross-field commitment substitution rejected.
17. Cross-provider-domain reuse rejected.
18. Cross-policy-generation replay rejected.
19. Commitment-key possession cannot authorize provider send.
20. Commitment-key rotation preserves historical verification.
21. Destroyed historical commitment key obeys declared verification policy rather than silently accepting unverifiable evidence.
22. Tokenization mapping access is separately authorized.
23. Arbitrary metadata cannot smuggle secret plaintext.
24. Canonicalization ambiguity fails closed.

### C. Replay/audit separation (25-36)
25. General auditor cannot decrypt replay capsule.
26. Replay worker cannot rewrite authority history.
27. Capsule digest mismatch blocks recovery.
28. Capsule expiry prevents resend but retains audit proof.
29. Capsule CE prevents replay.
30. UNKNOWN pin retains minimum reconciliation projection only.
31. Human reconciliation decrypt is access-logged.
32. Decrypt authority does not mint SEND authority.
33. Retention hold does not extend one-shot lease.
34. Retry identity can be proven from commitment without raw body.
35. Same semantic payload under different volatile auth verifies correctly.
36. Different semantic payload with same provider token is detected.

### D. Cryptographic erasure coverage (37-48)
37. Single live encrypted object + unique DEK can be CE'd with manifest proof.
38. Surviving backup DEK wrapper makes CE incomplete.
39. Surviving plaintext WAL copy makes CE incomplete.
40. Surviving tmp/crash-dump copy makes CE incomplete.
41. Search-index plaintext copy makes CE incomplete.
42. Analytics replica plaintext copy makes CE incomplete.
43. KMS alias deletion without key destruction is rejected as CE proof.
44. Destroyed DEK with surviving plaintext export is rejected.
45. CE transition is authenticated and parent-linked.
46. CE preserves semantic commitment and attempt history.
47. Post-CE replay fails closed.
48. Restore of pre-CE backup cannot silently resurrect erased material.

### E. Archive/backup/privacy continuity (49-60)
49. Archive inherits sensitivity/policy/key generation.
50. Archive read-after-write verification does not imply permission to retain secrets forever.
51. Backup inventory is required before CE completion.
52. Restored old policy generation cannot emit new raw fields.
53. Retention TTL cannot delete unresolved authority-core evidence.
54. UNKNOWN pin cannot retain unrelated raw body.
55. Legal hold extends retention but not effect authority.
56. Privacy deletion cannot silently bypass unresolved-security pin policy.
57. Archive object with erased DEK remains commitment-only.
58. Export bundle uses selective disclosure, not DB dump by default.
59. Replica lag cannot resurrect already erased replay authority.
60. DR copy must prove the same erase frontier before becoming active.

### F. Derived observability / operational failures (61-72)
61. Metrics labels contain no sensitive field values.
62. Trace attributes contain no access tokens.
63. Structured logger rejects denied evidence fields.
64. Provider SDK exception sanitizer handles nested request objects.
65. Queue overflow does not fall back to raw local logging.
66. Disk-full does not trigger raw emergency dump.
67. Observer crash does not write full request for debugging.
68. Multi-process writer enforces same minimization generation.
69. Old binary cannot use permissive fallback schema.
70. Redaction library failure blocks consequential I/O.
71. Audit export proves commitment continuity after secret erasure.
72. Final audit can reconstruct authority/state history without reconstructing erased provider secret material.

## Acceptance boundary

This freeze is design evidence only. No production privacy minimizer, replay-capsule encryption, CE executor or behavioral PASS is claimed until executable RED/GREEN tests are implemented against the real LAB-093 evidence store and provider façade.

## Integration requirements

LAB-093 implementation must compose this contract with:

- canonical/global evidence chain;
- authority lease + one-shot consumption;
- retry/replay capsule;
- semantic extractor and final-request freeze;
- transport observer + `SINK_ENTERED` durability barrier;
- UNKNOWN/manual reconciliation;
- capacity/compaction/archive continuity;
- startup rollback/restore/global-frontier verification.

No subsystem may independently invent a raw logging path or a separate retention authority island.
