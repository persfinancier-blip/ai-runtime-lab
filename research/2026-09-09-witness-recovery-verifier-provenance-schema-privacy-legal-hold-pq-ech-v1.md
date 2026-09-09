# Witness recovery, verifier provenance, schema-gossip privacy, legal-hold deletion, and PQ/ECH authority — v1

Date: 2026-09-09
Status: FROZEN RESEARCH CONTRACT; executable RED/GREEN proof pending
Contract: `WITNESS_RECOVERY_VERIFIER_PROVENANCE_SCHEMA_PRIVACY_LEGAL_HOLD_PQ_ECH_V1_FROZEN`

## Why this exists

LAB-086 remains the first executable priority. In this run direct Git transport was re-probed and failed before repository code execution with `Could not resolve host: github.com`. The GitHub connector remains available, but the complete byte-exact LAB-080→086 closure has not yet been materialized into the local executor in this run, so no new behavioral/compile PASS is claimed.

This note completes the distinct fallback recorded in `state/CURRENT.md`. It does not substitute for any executable gate.

## Primary sources / donors

- RFC 9162, Certificate Transparency Version 2.0: https://www.rfc-editor.org/rfc/rfc9162.html
- The Update Framework specification: https://theupdateframework.github.io/specification/latest/
- SLSA Provenance v1.1 model (v1.2 is current; v1.1 page retained for exact field semantics referenced here): https://slsa.dev/spec/v1.1/provenance
- W3C Data Integrity BBS Cryptosuites v1.0 Candidate Recommendation Draft, 2026-04-07: https://www.w3.org/TR/vc-di-bbs/
- NIST SP 800-88 Rev. 2, Guidelines for Media Sanitization, September 2025: https://csrc.nist.gov/pubs/sp/800/88/r2/final
- RFC 9849, TLS Encrypted Client Hello: https://www.rfc-editor.org/rfc/rfc9849.html
- RFC 8446 / RFC 9846 TLS 1.3 resumption semantics: https://www.rfc-editor.org/rfc/rfc8446.html and https://www.rfc-editor.org/rfc/rfc9846.html

## 1. External witness quorum recovery

### Boundary

`SUCCESSOR_WITNESSES_AGREE != PREDECESSOR_HISTORY_REPAIRED`

Witness loss and witness compromise are different events. Losing enough witnesses to make a quorum unavailable is an availability failure; evidence that a witness signing root was compromised is an integrity failure. A recovery protocol MUST NOT silently convert either event into permission for a smaller incumbent quorum to rewrite history.

### Frozen contract

1. Every witness set has an authenticated `witness_generation`, member population, threshold, signer/root lineage, and activation boundary.
2. Successor enrollment is forward-only. It cannot mutate the predecessor generation or erase conflicting predecessor statements.
3. If predecessor quorum is unavailable but not known compromised, recovery may create a successor generation only through a separately authenticated recovery authority whose denominator and policy were fixed before the outage.
4. If predecessor witness authority is compromised, all affected historical statements remain retained with explicit degraded assurance; a clean successor cannot retroactively make them trustworthy.
5. Recovery must preserve both sides of any split view. RFC 9162 consistency mechanisms are a donor for append-only ancestry, not a license to discard a conflicting signed tree head.
6. Quorum recovery must be independently witnessed. A recovery controller that is also the sole witness population is one failure domain, regardless of key count.

## 2. Semantic projection test corpus and verifier-build provenance

### Boundary

`TWO_VERIFIERS_PASS != TWO_INDEPENDENT_VERIFIERS`

and

`VERIFIER_BINARY_HASH_MATCHES != VERIFIER_SEMANTICS_ARE_ATTESTED`

A dual-verifier transition only adds assurance if the implementations/builds are meaningfully independent and both are tested against the same authenticated semantic corpus. Two binaries built from the same parser library, same generator, same compromised build platform, or same hidden normalization bug can fail identically.

### Frozen contract

1. Each semantic-projection version has an immutable corpus root covering positive, negative, ambiguity, duplicate-key, Unicode, number-boundary, unknown-critical-field, default/null/empty, and schema-version cases.
2. A verifier-generation record binds: source revision, dependency digests, build type, builder identity, build-platform trust domain, compiler/runtime versions, produced artifact digest, corpus root, and observed corpus result digest.
3. SLSA provenance is a donor: its `builder.id` represents the transitive closure of trusted build-platform entities, and external parameters must be verified downstream. A signed artifact digest alone is therefore insufficient provenance for verifier independence.
4. Promotion from verifier generation N to N+1 requires dual interpretation over a transition window. Any semantic disagreement is fail-closed and retained as evidence.
5. Parser/library deprecation does not allow corpus shrinkage. Unsupported historical vectors remain required historical-verification evidence or explicitly degrade the supported assurance claim.

## 3. Privacy-preserving schema gossip / selective disclosure

### Boundary

`SELECTIVE_DISCLOSURE_VERIFIES != COMPLETE_SCHEMA_VIEW_PROVEN`

W3C BBS is a donor for unlinkable selective disclosure: a holder can prove selected signed statements without revealing all signed statements. That solves disclosure minimization, not completeness of a security-critical schema/gossip view.

### Frozen contract

1. Gossip heads remain globally comparable by stable generation/root identifiers even when schema body fields are selectively disclosed.
2. Mandatory security-critical facts — schema generation, projection version, compatibility floor, critical-field set commitment, predecessor root, activation boundary, and root/witness lineage — cannot be hidden from the verifier that decides compatibility.
3. Private attributes may use commitments/selective proofs, but omission of a required disclosure produces `INSUFFICIENT_DISCLOSURE`, never implicit compatibility.
4. Two holders presenting different selectively disclosed subsets from one valid schema root do not constitute a split view. Two different authenticated roots for the same generation do.
5. Privacy transformations must not erase common-control edges needed for independence decisions; a stable pseudonymous/equality-preserving representation is acceptable where raw provider/account identifiers are not.

## 4. Deletion proofs versus legal hold / retention policy

### Boundary

`DELETION_REQUESTED != DELETION_AUTHORIZED`

and

`RETENTION_HOLD != SILENT_DELETION_FAILURE`

NIST SP 800-88 Rev. 2 defines sanitization as rendering access to target data infeasible for a chosen level of effort and frames sanitization as an organizational program with applicable controls. The lab must separately model whether deletion is currently authorized. A legal/contractual/incident hold is an authority state, not a storage error.

### Frozen contract

1. Each deletion generation evaluates current `deletion_policy_epoch` and `retention_hold_set` before destructive work.
2. An active applicable hold yields an authenticated `DELETION_DEFERRED_BY_HOLD` disposition with scope, authority reference, start generation, review/expiry semantics if available, and the copy domains that remain intentionally retained.
3. A deletion proof MUST distinguish: authorized+completed, authorized+partially completed, deferred by hold, denied by policy, and technically blocked/unreachable.
4. Hold release creates a successor authorization event; it never rewrites the historical deferred disposition.
5. Tombstone/negative-cache propagation may proceed while payload destruction is held only if doing so cannot violate the retention requirement or destroy evidentiary discoverability.
6. The implementation must not infer legal authority. Which hold applies is an owner/organization legal-policy input; the runtime only enforces authenticated policy state.

## 5. PQ/ECH resumption authority during ECH key rotation and split termination

### Boundary

`ECH_RETRY_AUTHENTICATED != OLD_RESUMPTION_AUTHORITY_STILL_VALID`

and

`EDGE_CAN_DECRYPT_ECH != EDGE_OWNS_INNER_SERVICE_TICKET_AUTHORITY`

RFC 9849 explicitly allows authenticated retry configurations after ECH rejection, warns that repeated retry configurations can signal inconsistent multi-server deployment, recommends regular ECH key rotation, and supports split mode in which the client-facing server forwards `ClientHelloInner` to a backend that the client authenticates. TLS 1.3 separately renegotiates extensions on resumption; 0-RTT parameters come from the predecessor session and mismatches can require early-data rejection.

### Frozen contract

1. ECH config generation is separate from TLS ticket-key generation, backend service identity generation, and PQ/hybrid crypto-policy generation.
2. Successful ECH retry only authenticates the replacement ECH configuration under the RFC 9849 retry rules. It does not extend the authorization scope of an old ticket.
3. On inner-backend migration, resumption must re-evaluate inner service identity/SNI authorization, ALPN/application protocol, current certificate/server identity generation, current PQ/hybrid floor, and ticket spend/replay ownership.
4. Shared edge ECH keys or shared ticket-decryption keys do not imply shared application authority across inner services.
5. During mixed ECH-key rollout, a retry loop/inconsistent config observation is not authority to fall back below the current PQ/hybrid policy floor.
6. Split client-facing/inner termination must bind the resumption decision to the authenticated inner service context. If that binding cannot be proven, perform a fresh policy-compliant handshake; consequential 0-RTT remains disabled.
7. Post-compromise ticket-key rotation revokes future authorization under the affected ticket generation even when old tickets remain syntactically decryptable elsewhere.

## RED-first regression matrix (40 cases)

### Witness recovery (8)
1. One witness unavailable; quorum still healthy -> no generation change.
2. Quorum unavailable; no compromise evidence -> no threshold shrink.
3. Recovery authority creates successor with precommitted policy -> predecessor retained.
4. Compromised witness root discovered -> affected history marked degraded.
5. Successor all agree -> compromised predecessor not rewritten.
6. Split predecessor heads -> both retained through recovery.
7. Recovery controller and all successor witnesses same failure domain -> independence claim rejected.
8. Stale recovery generation replay -> rejected.

### Verifier provenance/corpus (8)
9. Two binaries same artifact under different filenames -> not independent.
10. Different binaries same builder/control plane -> common dependency recorded.
11. Same source, independently built and provenance-bound -> eligible distinct build evidence, subject to policy.
12. Corpus root mismatch -> verifier generation rejected.
13. Duplicate-key vector accepted by one verifier only -> fail closed.
14. Unicode/numeric canonicalization disagreement -> fail closed.
15. Deprecated parser cannot execute historical mandatory corpus -> assurance degraded, not silently dropped.
16. New verifier passes reduced corpus only -> promotion rejected.

### Schema gossip privacy (8)
17. Same root, different allowed selective disclosures -> not split view.
18. Same generation, different roots -> split view.
19. Hidden compatibility floor -> insufficient disclosure.
20. Hidden critical-field commitment -> insufficient disclosure.
21. Pseudonymous common-control equality preserved -> independence evaluator can detect shared domain.
22. Privacy transform makes common-control equality unverifiable -> independence claim rejected.
23. Valid selective proof over disclosed subset -> does not imply hidden-schema completeness.
24. Root rollover with old conflicting head -> conflict retained.

### Deletion/hold (8)
25. Deletion authorized, no hold, all domains sanitized -> COMPLETED.
26. Applicable active hold -> DEFERRED_BY_HOLD; payload remains.
27. Hold appears after partial deletion -> PARTIAL + hold, no false completeness.
28. Hold released -> successor authorization event, old deferred record retained.
29. Unreachable backup with no hold -> TECHNICALLY_BLOCKED/PARTIAL.
30. Policy denies deletion -> DENIED_BY_POLICY, distinct from hold.
31. Tombstone propagation would destroy required evidence under hold -> blocked.
32. Deletion engine receives ambiguous/unsigned hold state -> fail closed.

### PQ/ECH resumption (8)
33. ECH key rotates; authenticated retry config; old ticket still meets all current inner policy -> resumption policy reevaluated, not automatically accepted.
34. Retry config points to inconsistent second retry -> reject/misconfiguration path per policy.
35. Backend identity changes while edge ticket key is shared -> old ticket not automatically authorized.
36. Inner SNI moves to a different service under same certificate -> service authority rechecked.
37. ALPN changes -> consequential 0-RTT rejected.
38. Current PQ/hybrid floor rises after ticket issuance -> fresh compliant handshake required.
39. Ticket key compromised/rotated in one region but stale replica can decrypt -> authorization rejected by ticket-generation revocation state.
40. Split termination cannot prove binding to intended inner service -> fresh handshake; no consequential 0-RTT.

## Decision

Freeze `WITNESS_RECOVERY_VERIFIER_PROVENANCE_SCHEMA_PRIVACY_LEGAL_HOLD_PQ_ECH_V1_FROZEN` as design evidence only. No production refactor is authorized from this note without RED-first exact execution on the relevant supported surface.

## Exact next research fallback if LAB-086 is still not executable

Investigate **witness recovery authority anti-capture and quorum denominator migration + reproducible verifier corpus generation/attestation poisoning + private schema-gossip intersection attacks and unlinkability budget + retention-hold authority revocation/split-view + PQ/ECH resumption state under DNS HTTPS/SVCB rotation, multi-CDN failover and cross-origin ticket reuse**.
