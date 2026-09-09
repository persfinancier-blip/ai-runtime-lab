# Witness anti-capture, verifier-corpus poisoning, private schema intersection, retention split-view, and PQ/ECH multi-CDN contract

Date: 2026-09-09

Status: design freeze / RED-first contract; **not executable evidence**.

Contract name: `WITNESS_ANTI_CAPTURE_VERIFIER_POISON_SCHEMA_INTERSECTION_RETENTION_SPLIT_PQ_SVCB_V1_FROZEN`

## Why this slice exists

LAB-086 remains the executable priority. In this run direct Git transport again failed before repository execution (`Could not resolve host: github.com`). The retained LAB-086 manifest permits connector reconstruction only when every reconstructed file is byte-verified with `git hash-object`. The GitHub connector can read pinned UTF-8 blobs but has no supported direct materialization primitive into the local executor; manually/model-reserializing the large security-critical closure would weaken the retained gate and is therefore not used.

This document is the pre-recorded distinct fallback from `state/CURRENT.md`. It extends the LAB-093+ trust-boundary work without claiming any LAB-086 behavioral or compile PASS.

## Primary donors

- RFC 9162, Certificate Transparency Version 2 — append-only Merkle history, signed tree heads, consistency evidence, and split-view detection considerations: https://www.rfc-editor.org/rfc/rfc9162
- SLSA v1.2 build-platform assessment and provenance model — provenance trust boundaries, independent build/reproducer assumptions, dependency/control-plane trust, and cache poisoning threats: https://slsa.dev/spec/v1.2/assessing-build-platforms and https://slsa.dev/spec/v1.1/provenance
- W3C Data Integrity BBS Cryptosuites v1.0 — selective disclosure, unlinkable derived proofs, and linkability through disclosed structure/options/key choice: https://www.w3.org/TR/vc-di-bbs/
- NIST SP 800-53 Rev. 5 AU-11 — organization-defined audit retention and long-term retrieval capability: https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final
- RFC 9460 — SVCB/HTTPS endpoint and parameter binding, multi-CDN differences, and downgrade hazards when endpoint capabilities differ: https://www.rfc-editor.org/rfc/rfc9460
- RFC 9849 — ECH key/config rotation, retry configurations, and split-mode client-facing/backend trust boundary: https://www.rfc-editor.org/rfc/rfc9849
- RFC 9846 / TLS 1.3 — resumption PSK/ticket binding, current SNI handling, single-use-ticket considerations and 0-RTT replay constraints: https://www.rfc-editor.org/rfc/rfc9846

Donor use is architectural. No donor text/code is copied into runtime.

## Frozen invariants

### 1. Witness recovery authority anti-capture

`SUCCESSOR_QUORUM_AVAILABLE != SUCCESSOR_QUORUM_LEGITIMATE`

A witness quorum recovery event is a membership/authority transition, not merely a liveness repair. The predecessor generation, recovery proposal, proposed successor membership, denominator, threshold, activation boundary, and evidence root are authenticated before successor votes can authorize consequential history claims.

Rules:

1. Loss and compromise are distinct states. `UNAVAILABLE` does not imply `COMPROMISED`; `COMPROMISED` does not grant the surviving minority unilateral reconfiguration authority.
2. The recovery denominator/threshold is bound before observing which proposed witnesses answer. No post-observation denominator shrinkage.
3. A successor quorum cannot retroactively upgrade predecessor history from `DEGRADED/UNKNOWN` to `VERIFIED` merely by agreeing on it.
4. Witness identity independence is measured over transitive control/build/key/operator domains; many keys behind one control plane are one capture domain for this assurance claim.
5. Recovery has a monotonic generation and predecessor hash/root. Rollback to an earlier witness generation is rejected even if signatures remain cryptographically valid.
6. If the configured recovery authority itself is compromised or cannot be distinguished from capture, the state is `RECOVERY_AUTHORITY_UNTRUSTED`, not automatic threshold reduction.

### 2. Reproducible verifier corpus generation and attestation poisoning

`CORPUS_HASH_MATCHES != CORPUS_TRUSTWORTHY`

A verifier test corpus is a security input. Reproducibility proves repeatability of bytes, not correctness of selection, oracle labels, semantic coverage, or generator integrity.

Bind each corpus generation to:

- corpus schema/version;
- generator source digest;
- generator dependency/material digests;
- semantic oracle/version;
- positive/negative class counts and coverage commitments;
- seed/parameter commitments where deterministic generation is intended;
- builder identity + provenance;
- corpus artifact digest;
- predecessor corpus generation where this is a migration.

Rules:

1. Corpus-generation provenance is verified independently of verifier-build provenance.
2. A malicious generator that consistently emits poisoned vectors cannot become trusted because multiple verifiers reproduce the same corpus.
3. Cache hits are evidence only if cache keys bind every semantic input. SLSA's cache-poisoning threat is a direct donor: an attacker-controlled cache entry must not masquerade as output from different trusted inputs.
4. Dual-verifier assurance requires materially independent parser/verifier/build trust domains or is reported as correlated assurance.
5. Corpus label disagreement is preserved as evidence and fails closed for security-critical semantic migrations.
6. Test-vector deletion or replacement creates a new corpus generation; history is append-only.

### 3. Private schema-gossip intersection attacks and unlinkability budget

`EACH_DISCLOSURE_UNLINKABLE != DISCLOSURE_SEQUENCE_UNLINKABLE`

Selective-disclosure proofs can hide individual schema details while repeated queries still reveal identity through intersection, stable pseudonyms, rare dependency combinations, mandatory revealed indexes, issuer keys, proof options, timing, or cardinality.

Rules:

1. Each gossip policy defines a disclosure budget over a window, not only per-request field minimization.
2. The verifier computes/records a coarse privacy class for each revealed mandatory edge; it does not persist hidden raw identifiers merely to enforce the budget.
3. Stable equality commitments/pseudonyms are scoped to the minimum domain/epoch needed for common-control detection; cross-purpose reuse is forbidden by policy.
4. Mandatory security/common-control edges cannot be hidden when they determine an independence claim. Privacy pressure may yield `INSUFFICIENT_DISCLOSURE`, never invented independence.
5. Repeated adaptive queries that would reduce the anonymity set below policy become `DISCLOSURE_BUDGET_EXHAUSTED`.
6. Key rotation alone is not unlinkability if other stable proof metadata or disclosed structure remains identifying. W3C BBS privacy guidance is a donor for this distinction.

### 4. Retention-hold authority revocation and split-view

`VALID_HOLD_SIGNATURE != CURRENT_HOLD_AUTHORITY`

The runtime enforces authenticated retention/deletion state but does not decide legal authority. Hold creation, extension, release, revocation and authority rollover are versioned lifecycle events.

Rules:

1. Holds bind subject/copy-domain scope, authority generation, policy identifier, issue time, effective boundary, and disposition state.
2. A release signed by a revoked predecessor authority is historical evidence, not current deletion authorization.
3. Two valid conflicting hold/release views for the same generation are `RETENTION_AUTHORITY_SPLIT_VIEW` and fail closed for destructive deletion.
4. Split-view evidence is retained independently of the payload whose deletion is disputed.
5. Authority rollover creates successor lineage; it does not erase predecessor holds or rewrite whether they were effective at a historical time.
6. Long-term audit evidence must remain retrievable after format/tool/provider retirement; NIST AU-11 is the donor for retention + retrieval, not a source of legal policy.
7. If the authenticated hold state cannot be established, destructive deletion is deferred; the runtime reports the technical state and does not infer whether a law requires retain/delete.

### 5. PQ/ECH resumption across DNS HTTPS/SVCB rotation and multi-CDN failover

`SAME_ORIGIN_NAME != SAME_RESUMPTION_AUTHORITY`

RFC 9460 explicitly permits alternative service endpoints with different parameters/operators and warns that multi-CDN capabilities can differ. Therefore DNS routing continuity does not imply continuity of TLS ticket authority, ECH configuration, anti-replay ownership, backend identity, or PQ/hybrid policy.

Bind resumption authorization to the current logical operation and at minimum:

- current origin/inner SNI;
- current HTTPS/SVCB service binding generation or equivalent authenticated routing epoch;
- selected endpoint/operator trust domain;
- current ECH config/public-name generation when ECH is required;
- current backend/server identity generation;
- selected ALPN;
- ticket/PSK predecessor session context;
- current minimum crypto policy epoch, including PQ/hybrid floor;
- current 0-RTT replay/spend authority owner.

Rules:

1. A ticket decrypting at CDN B after failover from CDN A is not proof that B owns resumption authority.
2. An HTTPS/SVCB response selecting a weaker-capability backup must not silently lower the application's current PQ/hybrid floor. Availability fallback and crypto-policy downgrade are separate decisions.
3. ECH `retry_configs` are authenticated retry material, not authority to reuse predecessor tickets across a changed backend/operator generation.
4. Split ECH termination keeps client-facing and backend identities distinct. Sharing an ECH-facing edge does not imply sharing backend TLS tickets.
5. Mixed CDN rollout that yields inconsistent ECH configs/routing generations is a retry/fail-closed condition for consequential operations, not permission to pin whichever old configuration succeeds.
6. Cross-origin/cross-service ticket reuse remains forbidden unless explicit current policy authorizes the target identity and all current-context checks pass; certificate SAN overlap alone is insufficient.
7. Consequential 0-RTT is rejected when anti-replay ownership is ambiguous across failover/partition/multi-CDN routing.
8. Client-side cached HTTPS/SVCB/ECH material is bounded by freshness and current policy. Cache freshness does not override a known stricter policy epoch.

## State machine additions

Suggested states for later implementation/tests:

- `WITNESS_RECOVERY_PENDING`
- `WITNESS_RECOVERY_DENOMINATOR_BOUND`
- `RECOVERY_AUTHORITY_UNTRUSTED`
- `PREDECESSOR_HISTORY_DEGRADED`
- `CORPUS_PROVENANCE_UNVERIFIED`
- `CORPUS_ORACLE_DISAGREEMENT`
- `DISCLOSURE_BUDGET_EXHAUSTED`
- `INSUFFICIENT_DISCLOSURE`
- `RETENTION_AUTHORITY_SPLIT_VIEW`
- `DELETION_DEFERRED_BY_AUTHORITY_AMBIGUITY`
- `RESUMPTION_ROUTING_GENERATION_MISMATCH`
- `RESUMPTION_AUTHORITY_AMBIGUOUS`
- `CURRENT_CRYPTO_FLOOR_UNSATISFIED`
- `ZERO_RTT_REPLAY_AUTHORITY_AMBIGUOUS`

## RED-first matrix (40 cases)

### Witness recovery anti-capture

1. Reject successor quorum chosen only from responders after outage observation.
2. Reject threshold reduction after seeing non-responsive incumbent members.
3. Preserve predecessor `DEGRADED` when successor quorum unanimously endorses it.
4. Reject rollback to older witness generation with otherwise valid signatures.
5. Detect five logical witnesses sharing one signing/control-plane capture domain.
6. Reject recovery proposal whose predecessor root does not match retained history.
7. Fail closed when recovery authority key is revoked before successor activation.
8. Distinguish unavailable witness from positively compromised witness evidence.

### Verifier corpus / poisoning

9. Reject corpus with correct artifact hash but missing generator provenance.
10. Reject corpus built from unpinned generator dependency.
11. Detect deterministic poisoned oracle reproduced by two verifiers.
12. Reject cache hit whose key omits semantic schema generation.
13. Preserve conflicting labels from independent corpus generators.
14. Mark two verifiers correlated when built by same trust-domain pipeline.
15. Reject corpus generation rollback with valid old signature.
16. Require successor generation when a negative test vector is removed.

### Private schema gossip

17. Allow one minimal selective disclosure within budget.
18. Exhaust budget after adaptive intersection sequence crosses anonymity threshold.
19. Reject independence claim when mandatory common-control edge is withheld.
20. Scope pseudonym equality to one configured domain/epoch.
21. Reject cross-purpose reuse of stable equality commitment.
22. Detect linkability caused by rare mandatory reveal/index pattern.
23. Rotate proof key but still account for stable metadata linkage.
24. Preserve privacy-safe budget accounting without storing hidden identifiers.

### Retention authority split/revocation

25. Accept hold from current authority generation.
26. Treat release from revoked predecessor authority as historical only.
27. Fail destructive deletion on two conflicting valid current-generation views.
28. Preserve split-view evidence after payload deletion elsewhere.
29. Keep historical hold effectiveness through authority rollover.
30. Reject rollback to older hold-authority generation.
31. Report authority ambiguity rather than infer legal outcome.
32. Verify retained audit evidence after original storage/provider retirement.

### PQ/ECH + SVCB/multi-CDN

33. Reject CDN-A ticket at CDN-B when only ticket decryption key is shared.
34. Reject fallback endpoint whose current crypto capability is below required PQ/hybrid floor.
35. Reject consequential 0-RTT when failover creates two replay/spend authorities.
36. Re-evaluate backend/server generation after ECH retry/config rotation.
37. Reject cached SVCB route whose routing epoch conflicts with current authenticated policy.
38. Reject ticket reuse across service/origin solely because certificate covers both names.
39. Reject ALPN/backend transition inconsistent with predecessor ticket authorization.
40. Permit full fresh compliant handshake after failover while rejecting unsafe resumption/0-RTT.

## Implementation direction

Do not implement these states before the retained executable gates ahead of LAB-093+ are available. When implementation starts, tests should be introduced first at the same abstraction level as the frozen contracts, with explicit negative controls for denominator rebinding, poisoned corpus provenance, privacy intersection, hold split-view, and cross-CDN resumption downgrade.

## Current-run LAB-086 evidence boundary

Observed this run:

- `git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD` failed with `Could not resolve host: github.com` before repository execution.
- Connector fetch of pinned `strict_fence.py` at `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` succeeds and exposes exact base64 bytes/blob identity, confirming source readability.
- No supported connector-to-local-filesystem materialization primitive was found; manually copying/reserializing the large closure would violate the manifest's byte-exact discipline.
- Therefore no new LAB-086 behavioral, unsafe-seed, or compileall PASS is claimed in this document.
