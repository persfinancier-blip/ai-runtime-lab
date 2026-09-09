# Witness finalization, corpus/oracle recovery, schema privacy budget, retention freshness, and PQ/ECH DNS downgrade contract

Date: 2026-09-10
Status: `WITNESS_FINALIZATION_CORPUS_ORACLE_SCHEMA_BUDGET_RETENTION_FRESHNESS_PQ_DNS_V1_FROZEN`
Origin: distinct fallback while LAB-086 exact local source materialization remains unavailable in the current runtime.

## Scope

This note freezes the next regression-first contract for LAB-093/#178 and follow-on capability/evidence work. It does **not** substitute for LAB-086 executable proof and does not change PR #165 draft status.

## Primary sources / donors

- RFC 9162, Certificate Transparency Version 2.0: signed tree heads and consistency proofs; conflicting views are evidence rather than a condition that can be normalized away. https://www.rfc-editor.org/rfc/rfc9162.html
- SLSA FAQ and provenance guidance: reproducible/verified builds require genuinely independent rebuilders; common pipeline/build-platform compromise remains a correlated failure mode. https://slsa.dev/spec/draft/faq and https://slsa.dev/spec/v1.0-rc1/provenance
- NIST SP 800-53 Rev. 5, AU family: audit records need retention, protection, time semantics, and long-term retrievability according to policy; the runtime must not infer legal authority. https://csrc.nist.gov/pubs/sp/800/53/r5/final
- RFC 9460, SVCB/HTTPS: SVCB resolution failure and unauthenticated DNS can create downgrade conditions; clients need a defined fail/fallback policy, and endpoint indirection does not replace service authentication. https://www.rfc-editor.org/rfc/rfc9460.html
- RFC 9848, ECH bootstrapping with SVCB/HTTPS: mixed ECH/non-ECH endpoint sets are downgrade-prone; blocking ECH-capable alternatives can force weaker paths. https://www.rfc-editor.org/rfc/rfc9848.html
- RFC 9849, TLS ECH: retry configuration, ECHConfig source binding, freshness, DNS poisoning considerations, and downgrade resistance. https://www.rfc-editor.org/rfc/rfc9849.html

## Frozen decisions

### 1. Witness recovery: activation and finalization are separate authorities

`RECOVERY_QUORUM_ACTIVATED != RECOVERY_HISTORY_FINALIZED`

A successor witness set may become operational only after predecessor-bound recovery parameters are committed before availability is observed: predecessor generation/root, proposed successor membership, denominator, threshold, activation boundary, and recovery reason.

Finalization is a second event. It must bind the exact predecessor evidence set, all conflicting signed heads/views known at activation, the successor generation, and the adjudicated continuity result. A successor quorum cannot erase or rewrite evidence that predecessor quorum was lost or compromised.

Split-brain rule: if two candidate successor quorums activate from the same predecessor generation without a common authenticated activation lineage, both become `RECOVERY_SPLIT_VIEW`; neither may self-finalize the other away.

### 2. Verifier corpus: semantic coverage and oracle authority are explicit

`CORPUS_REPRODUCES != SECURITY_SEMANTICS_COVERED`

A verifier corpus commitment must bind at least:
- corpus format/schema version;
- generator source and dependency/build provenance;
- oracle implementation/version and trust root;
- semantic coverage manifest (critical fields, invalid forms, boundary values, downgrade cases, canonicalization/parser differentials);
- mutation operators used to challenge coverage;
- expected result for each case.

Mutation score is evidence of exercised semantics, not proof of completeness. A corpus that reproduces bit-for-bit but whose oracle and generator share one compromised trust domain remains degraded.

Oracle compromise rule: successor oracle approval does not retroactively convert historical results to `TRUSTED`. Historical verdicts are marked with the oracle generation that produced them and can be re-evaluated under a successor oracle only as a new attested result.

### 3. Schema gossip privacy: compose disclosure budgets across verifiers

`PER_VERIFIER_PRIVACY_BUDGET_OK != GLOBAL_DISCLOSURE_BUDGET_OK`

Independent/selective-disclosure verifiers can collectively deanonymize a subject through adaptive intersection. Disclosure accounting therefore applies to a logical subject/window across verifier identities and channels, not independently per verifier.

The budget commits to:
- subject/pseudonym scope;
- disclosure class;
- verifier/domain identity or privacy-equivalence class;
- epoch/window;
- cumulative disclosure cost;
- mandatory security/common-control predicates that must remain provable.

When the budget is exhausted, the result is `INSUFFICIENT_DISCLOSURE` or delayed review, never fabricated independence or silent weakening of required security predicates.

### 4. Retention authority: freshness is part of authority

`VALID_HOLD_SIGNATURE != FRESH_HOLD_AUTHORITY`

Hold, release, revocation, and policy-root rollover records bind:
- authority generation/root;
- issued-at / not-before / expiry-or-review boundary;
- target evidence class/scope;
- predecessor event hash;
- policy identifier/version;
- optional offline-root recovery lineage.

Stale but cryptographically valid hold material cannot indefinitely override a newer authenticated release or policy-root rollover. Conversely, loss of online freshness service does not authorize deletion: uncertain authority fails closed into `RETENTION_AUTHORITY_FRESHNESS_UNKNOWN`.

Offline-root recovery creates a successor authority generation and preserves the degraded predecessor period. It cannot backdate a new legal/retention conclusion into an interval where current authority was unknown.

### 5. PQ/ECH/SVCB: DNS transition and heterogeneous client capability cannot lower current crypto floor

`DNS_ROUTE_AUTHENTICATED != TLS_RESUMPTION_AUTHORITY_CONTINUOUS`

`CLIENT_LACKS_PQ_CAPABILITY != AUTHORITY_TO_DOWNGRADE_SERVER_POLICY`

SVCB/HTTPS/ECH records influence routing and ECH bootstrap, but do not by themselves grant TLS ticket authority across endpoints/services or permission to weaken a current PQ/hybrid policy.

Current connection authorization rebinds to:
- logical service identity;
- authenticated DNS/SVCB generation when required by policy;
- ECHConfig source and accepted inner service;
- ALPN;
- backend/server identity generation;
- current PQ/hybrid policy epoch;
- ticket age and replay/spend authority.

DNS cache poisoning or selective blocking that removes security-bearing SvcParams must not silently route a security-required client onto a weaker path. Authenticated transition to a new SVCB/ECH generation is a versioned policy event; old cached data may be historical evidence but cannot override a newer minimum floor.

Heterogeneous rollout rule: legacy clients may receive a fresh connection only under an explicitly defined compatibility policy. They must not cause capable clients or resumption paths to inherit a lower floor. Mixed ECH/non-ECH endpoint sets are treated as downgrade-sensitive configuration and require explicit policy rather than opportunistic fallback.

## 40-case RED-first matrix

### Witness recovery / finalization
1. Precommitted successor quorum activates after predecessor quorum loss -> allowed, degraded predecessor retained.
2. Membership chosen after observing which witnesses are online -> reject.
3. Two successor sets activate from same predecessor without common lineage -> split-view, fail closed.
4. One successor tries to finalize the competing successor out of history -> reject.
5. Finalization omits one known conflicting predecessor head -> reject.
6. Finalization binds wrong predecessor root -> reject.
7. Compromised predecessor quorum signs successor as clean after compromise boundary -> degraded, not repaired.
8. Successor finalizes continuity with complete conflicting-view evidence preserved -> allowed as new adjudicated generation.

### Corpus / oracle / mutation coverage
9. Same corpus reproduced by two builders sharing one compromised pipeline -> independence claim reject/degrade.
10. Corpus hash matches but critical-field mutation class absent -> coverage insufficient.
11. Mutation operator changes canonicalization-sensitive field and verifier still passes -> RED defect.
12. Mutation operator changes unknown critical field and verifier ignores it -> RED defect.
13. Oracle version changes expected verdict without lineage -> reject.
14. Oracle compromise discovered after historical PASS -> mark historical oracle generation degraded.
15. Successor oracle re-evaluates old corpus -> store a new verdict, do not overwrite old one.
16. Generator and oracle both attest independent provenance and required mutation classes kill expected mutants -> coverage evidence accepted, not declared complete proof.

### Schema-gossip privacy composition
17. Each of two verifiers stays under local budget but combined disclosures exceed global subject budget -> reject second disclosure.
18. Pseudonym rotates inside same protected window and would evade accounting -> link to privacy-equivalence scope or reject.
19. Mandatory common-control predicate hidden because budget exhausted -> `INSUFFICIENT_DISCLOSURE`.
20. Verifier requests adaptive complementary fields after prior disclosures -> account cumulative intersection cost.
21. Independent organizations share one analytics back end -> common privacy-equivalence domain.
22. Old disclosure ledger is unavailable -> fail closed for new consequential disclosure.
23. Window rollover occurs without authenticated epoch transition -> reject reset.
24. Minimal disclosure proves required security predicate while cumulative budget remains below threshold -> allow.

### Retention freshness / offline-root recovery
25. Hold signature valid but expired review boundary passed -> freshness unknown/revalidation required.
26. Older hold races newer authenticated release -> newer generation wins.
27. Release signed by revoked predecessor authority -> reject.
28. Online authority unavailable and deletion requested -> fail closed, do not infer release.
29. Offline root activates successor authority with authenticated predecessor lineage -> allow successor generation.
30. Offline successor attempts to backdate release into unknown interval -> reject.
31. Two current valid policy roots issue conflicting hold/release -> split-view, destructive action blocked.
32. Long-term archive remains verifiable after online root retirement via retained root/format interpretation evidence -> allow audit retrieval.

### PQ/ECH/SVCB / DNS transitions
33. Capable client receives authenticated SVCB with PQ/ECH-required route -> enforce current floor.
34. Attacker strips security-bearing SVCB and client policy requires it -> fail/abort, no silent downgrade.
35. Mixed ECH/non-ECH endpoints plus selective blocking of ECH endpoint -> detect downgrade-sensitive condition; do not infer equivalent security.
36. Cached old ECHConfig conflicts with fresher authenticated generation -> current generation wins; old config cannot authorize resumption.
37. ECH retry points to different backend generation but old ticket decrypts -> fresh authorization required.
38. Legacy client lacks PQ capability -> apply explicit compatibility policy only; never relax capable-client/resumption floor.
39. DNS route moves to CDN B sharing ticket decrypt key but not replay/spend authority -> consequential 0-RTT rejected until authority continuity is proven.
40. Authenticated SVCB/ECH transition preserves logical service, ALPN, backend authority, replay ownership and current PQ floor -> resumption may proceed under normal ticket freshness rules.

## Implementation direction

No production refactor should start from this note alone. Implement RED tests first once exact executable source is available. Prefer small generation-bound records and canonical commitments over implicit mutable process state. Preserve predecessor/degraded evidence append-only. Separate operational availability from authority, and separate cryptographic validity from freshness, independence, privacy composition, and current-policy authorization.

## Current run observation

Direct `git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD` failed before repository code execution with `Could not resolve host: github.com`. GitHub connector reads/writes work, but no supported non-model connector-to-local-filesystem materialization primitive is exposed in this run. Therefore no new LAB-086 behavioral, unsafe-seed, compileall, or merge/conflict PASS is claimed.