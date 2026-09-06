# Equivalence-certificate trust-root rotation, cross-generation verifier handoff, and recursive-proof verifier agility — v1

Status: **FROZEN design contract / RED-first**

Date: 2026-09-06

Related: LAB-093 / #178; composes with the frozen semantic-equivalence substitution, substitution-chain composability, dependency-repair, GC/evidence-reachability, trust-frontier, monitor and adjudication contracts.

## Problem

Long-lived compressed evidence chains cannot assume that the signer key, signature algorithm, hash function, verifier binary, proof system, verification key, policy schema, or trust root used when an equivalence certificate was created will remain acceptable forever.

Two opposite failure modes must both be prevented:

1. **obsolete-crypto immortality** — a certificate remains deletion-authoritative forever merely because it was valid under a key/algorithm/verifier that was trusted years ago;
2. **history amnesia on upgrade** — rotating keys/algorithms/verifiers invalidates every historical substitution at once, forcing genesis replay or silently discarding historical assurance.

The system therefore needs authenticated handoff semantics that preserve the *meaning and obligations* of an already accepted certificate while allowing the cryptographic/verifier mechanism that carries that meaning to change.

## Primary-source donor mechanisms

### TUF root continuity

The Update Framework root update procedure requires clients to walk intermediate root versions and requires each new root to be signed by both the threshold trusted by the predecessor and the threshold declared by the new root. Root versions are monotonic and rollback is rejected. This is the closest direct donor for trust-root handoff without simply trusting the new root because it says so.

Source: https://theupdateframework.github.io/specification/v1.0.26/ — sections 5.3 and 6.1.

### Sigstore historical verification under rotation/revocation

Sigstore uses TUF to distribute rotating verification material. Its threat model explicitly calls out rotation, revocation with compromise time, freshness, offline root keys, and threshold root authority. Its policy-controller also supports a pinned initial TUF root plus automatic updates, while air-gapped serialized repositories require explicit manual rotation.

Sources:
- https://docs.sigstore.dev/about/threat-model/
- https://docs.sigstore.dev/policy-controller/overview/
- https://docs.sigstore.dev/cosign/system_config/custom_components/

### NIST crypto agility

NIST CSWP 39 defines crypto agility as the ability to replace/adapt cryptographic mechanisms while preserving security and ongoing operations, and emphasizes migration/interoperability as an explicit operational concern rather than assuming algorithms are permanent.

Source: https://www.nist.gov/publications/considerations-achieving-crypto-agility-strategies-and-practices-0 (CSWP 39 upd1, 2026-06-29).

### SLSA verifier/policy identity

SLSA VSA v1 binds a verification result to a verifier identity/version, policy URI/digest, subject digest, verification time and optionally all input attestations used. A historical PASS is therefore not context-free: verifier and policy generations are part of its meaning.

Source: https://slsa.dev/spec/v1.2/verification_summary

## Frozen terminology

- **Certificate statement (CS):** canonical semantic statement being asserted by an equivalence/substitution certificate: root obligation set, dependency classes, contexts, observation schema, subject/substitute digests, supported verifier/recovery sets, trust/policy frontier and revocation dependencies.
- **Carrier generation (CG):** exact cryptographic/proof mechanism carrying CS: signer/root generation, signature/hash algorithms, proof system, verification key, verifier implementation/version and policy generation.
- **Handoff certificate (HC):** authenticated statement that successor carrier generation `CG(n+1)` accepts responsibility for the exact CS/obligation namespace inherited from `CG(n)` under explicitly frozen conditions.
- **Subsumption certificate (SC):** stronger statement proving that a new observation/verifier/proof semantics preserves or strengthens every obligation in an old semantics for a specified support set.
- **Retirement frontier (RF):** policy-authenticated boundary after which a carrier generation may no longer authorize new consequential decisions.
- **Historical verification frontier (HVF):** boundary defining whether and how old evidence remains acceptable for historical facts after carrier retirement.
- **Compromise effective time/frontier (CEF):** authenticated point from which a compromised key/verifier/proof system is no longer trusted; must not be inferred solely from the disclosure time.
- **Bridge window:** bounded interval/generation range in which old and new mechanisms coexist to create independently checkable handoff evidence.

## Core rule: rotate the carrier, not the statement

A handoff MUST NOT redefine the historical certificate statement. The exact inherited CS digest and root obligation set remain immutable.

`HC(old -> new)` must bind at minimum:

- old and new carrier-generation identifiers;
- exact inherited CS / obligation-namespace digest;
- old and new signer/root identities and thresholds;
- old and new signature/hash/proof/verifier identifiers and versions;
- policy/trust-frontier generation;
- activation and retirement frontiers;
- compromise status known at handoff time;
- support-set declarations for online verification, offline late verification and recovery;
- explicit downgrade/compatibility result;
- nonce/sequence/version preventing replay or rollback;
- any required predecessor HC/SC digests.

A new carrier signing only `"I replace old"` is insufficient.

## Trust-root rotation

### Normal uncompromised rotation

For consequential historical authority, adopt TUF-like cross-sign semantics:

1. old trusted root/threshold authenticates the successor handoff;
2. successor root/threshold independently authenticates the same handoff statement;
3. handoff generations are monotonic and cannot skip required intermediate generations unless a separately authorized checkpoint/subsumption mechanism proves the skipped path;
4. clients persist the highest accepted handoff generation and reject rollback;
5. expiration/retirement is evaluated against a fixed verification-start observation, not a clock value that can change mid-check.

The old root does not become trusted forever: after RF it cannot authorize *new* substitutions/handoffs, but historical statements created before retirement can remain historically verifiable if HVF policy permits and no compromise invalidates their interval.

### Compromised old root

If the old root is compromised before it validly co-signs a successor, ordinary cross-sign rotation cannot establish trustworthy continuity. A successor cannot bootstrap itself by claiming that the old root was compromised.

Recovery requires an independently pre-authorized recovery path such as:

- offline threshold recovery root;
- separately scoped emergency root already committed by the prior valid trust state;
- transparency-backed owner recovery with an authenticated pre-existing policy;
- explicit human/owner authority where repository policy defines this as a genuine escalation.

No self-authenticated emergency root.

### Compromise effective frontier

Historical signatures are not automatically invalidated merely because a key was later compromised. Policy must bind an authenticated CEF. Evidence before CEF may remain valid for historical assertions if it also satisfies freshness/timestamp/transparency requirements; evidence at/after CEF becomes `REVALIDATION_REQUIRED` or invalid according to policy.

Disclosure time alone is not proof of compromise start time.

## Algorithm retirement and mixed-algorithm chains

Carrier identity includes the algorithm suite. Policy classifies suites at least as:

- `ACTIVE_FOR_NEW_AND_HISTORICAL`;
- `HISTORICAL_VERIFY_ONLY`;
- `REVALIDATION_REQUIRED`;
- `REJECTED`.

A suite moved to `HISTORICAL_VERIFY_ONLY` cannot authorize a new destructive substitution, new GC decision, new handoff, or new downgrade. It may only contribute to verification of evidence demonstrably created within an authorized historical interval.

If a suite becomes `REJECTED`, a certificate chain relying solely on that suite loses authority unless a previously created stronger handoff/subsumption certificate re-carried the exact statement before rejection.

Mixed-algorithm chains are evaluated per edge and per statement. One strong terminal signature does not launder a weak/forged ancestor. Every ancestor needed to establish CS must either remain historically acceptable or have been independently re-attested/re-proved while trustworthy.

## Verifier-generation handoff

A verifier PASS is scoped to its verifier identity/version, observation schema and policy digest. Replacing verifier V1 with V2 requires one of:

1. **direct replay:** V2 verifies the retained original evidence and produces a new certificate for the exact CS;
2. **subsumption proof:** independently justified SC proves that V2 observes at least every material obligation V1 observed for the relevant classes/context;
3. **dual-verifier bridge:** during a bounded bridge window, V1 and V2 independently verify the same retained originals and produce a canonical equivalence-of-observations manifest.

Merely asserting that V2 is newer, or that V1 and V2 both return `PASS`, is insufficient.

If V2 introduces a new material observation that cannot be reconstructed from the retained substitute, the old substitution becomes `REVALIDATION_REQUIRED`. If the original was already destroyed, the affected guarantee must degrade/quarantine; missing information must not be invented.

## Recursive-proof / proof-system agility

No recursive proof system is selected by this contract. The following semantics apply to any future recursive/compressed proof carrier.

A proof-system upgrade `P1 -> P2` may preserve historical authority only if the new proof binds:

- exact old public statement/CS digest;
- exact old verification-key/proof-system generation;
- exact parent proof/certificate digest or a lossless authenticated commitment to it;
- root obligation set;
- policy/trust frontier;
- verification result of the parent under the historically authorized P1 verifier;
- new P2 statement proving the inherited obligations, not merely `P1 returned PASS` unless policy explicitly treats P1 verification as a sufficient observation and that verifier remains acceptable.

Recursive compression cannot erase the identity of an algorithm/verifier/root whose revocation would change the result. Revocation dependencies remain logical ancestors even if bytes are compressed.

A proof generated after P1's retirement cannot use P1 as a new authority merely by embedding a P1 verifier circuit. Historical-verification allowance is not new-signing/new-proof authority.

## Offline late-verifier semantics

A late verifier starting from an old locally pinned trust root may catch up only through authenticated handoff generations. It must not fetch only the newest root/verifier bundle and accept it self-authentically.

For offline/air-gapped systems, a serialized handoff bundle must contain or reference content-addressed copies of every required intermediate trust/verifier/proof generation, retirement/compromise metadata and policy frontier. Missing intermediate evidence means `INCOMPLETE_CHAIN`, not optimistic trust.

An implementation MAY authorize a checkpoint bootstrap that skips intermediate bytes only if the checkpoint itself is anchored by a previously trusted root or separately authorized threshold and commits to the complete skipped handoff history in a way that permits later fraud/consistency verification.

## Downgrade resistance

Forbidden without an explicit stronger adjudication contract:

- new root reducing threshold while claiming unchanged assurance;
- switching from public-key/threshold evidence to shared-secret or unauthenticated digest evidence;
- dropping root-obligation fields because the successor verifier does not understand them;
- changing canonicalization/hash namespace without collision/domain-separation migration proof;
- substituting a verifier with a narrower observation set;
- accepting a proof system whose verifier accepts a strict superset of invalid statements;
- treating `unknown algorithm` as `ignore field` on a consequential certificate;
- using `latest wins` for conflicting handoff/retirement metadata.

Unknown critical carrier/obligation semantics fail closed.

## Authority matrix

| Situation | Historical verify | New substitution/GC authority | Required action |
|---|---:|---:|---|
| Old root active | yes | yes, subject to policy | ordinary verification |
| Old root retired, historically acceptable | yes | no | use successor for new decisions |
| Old root compromised after authenticated CEF, evidence before CEF | policy-dependent yes | no | retain timestamp/frontier evidence |
| Evidence at/after CEF | no / revalidate | no | direct replay under uncompromised successor |
| Algorithm historical-verify-only | yes | no | bridge/re-attest before rejection deadline |
| Algorithm rejected with no prior bridge | no | no | degrade/quarantine; original evidence needed |
| V2 direct-replays original | yes under V2 | yes if all obligations preserved | new certificate may supersede carrier only |
| V2 sees fewer obligations than V1 | maybe historical V1 | no | retain V1/original; reject downgrade |
| Recursive proof hides revoked ancestor identity | no | no | proof format invalid for consequential use |
| Late verifier missing handoff generation | no | no | `INCOMPLETE_CHAIN` |

## Canonical verification procedure

For a consequential certificate at time/frontier `F`:

1. Parse CS and CG with critical-field rejection.
2. Resolve the verifier's locally trusted anchor and highest persisted handoff generation.
3. Verify monotonic handoff chain/checkpoint from that anchor to the carrier generation needed for CS.
4. Verify every old->new HC under both predecessor and successor authority unless an explicitly authorized recovery/checkpoint rule applies.
5. Evaluate carrier algorithms/verifiers against policy at both creation frontier and current verification frontier.
6. Apply authenticated CEF/retirement metadata.
7. Reconstruct logical proof ancestors after compression.
8. Ensure no required ancestor is `REJECTED`, revoked-with-effective-impact, unknown, or unsupported.
9. Verify ROS/observation/support-set monotonicity through verifier/proof migrations.
10. Verify the terminal carrier cryptography/proof.
11. Bind result to exact policy/trust frontier and verification time/frontier.
12. Return one of `VALID`, `HISTORICAL_ONLY`, `REVALIDATION_REQUIRED`, `INCOMPLETE_CHAIN`, `REVOKED`, `DOWNGRADE`, `INVALID`.

Only `VALID` may authorize new destructive substitution/GC. `HISTORICAL_ONLY` may support historical audit but cannot authorize a new deletion.

## RED-first matrix — 80 cases

### A. Root handoff and rollback (1–10)
1. valid old+new threshold handoff;
2. new-only signed handoff rejected;
3. old-only signed handoff rejected;
4. wrong inherited CS digest rejected;
5. skipped mandatory root generation rejected;
6. persisted generation rollback rejected;
7. duplicate generation with different bytes rejected;
8. expired/frozen handoff rejected;
9. wrong threshold in successor rejected;
10. self-declared emergency root rejected.

### B. Compromise/revocation frontiers (11–20)
11. pre-CEF historical evidence policy-valid;
12. post-CEF evidence rejected;
13. disclosure time substituted for CEF rejected;
14. forged CEF rejected;
15. rollback to pre-revocation metadata rejected;
16. compromised old root cannot authorize successor after CEF;
17. pre-authorized recovery root succeeds;
18. uncommitted recovery root rejected;
19. revoked intermediate ancestor still visible through compressed proof;
20. revocation reactivates GC-retained original closure.

### C. Algorithm agility (21–30)
21. active->active dual-algorithm bridge valid;
22. historical-only algorithm verifies old evidence;
23. historical-only algorithm cannot create new HC;
24. historical-only algorithm cannot authorize GC;
25. rejected algorithm with prior trustworthy re-attestation survives through successor statement;
26. rejected algorithm with no bridge invalidates dependent chain;
27. strong terminal signature does not launder rejected ancestor;
28. unknown critical algorithm fails closed;
29. hash-domain migration without domain separation rejected;
30. collision/ambiguous canonicalization migration rejected.

### D. Verifier handoff (31–40)
31. V2 direct replay of original succeeds;
32. V1/V2 same PASS but V2 narrower observation set rejected;
33. explicit observation subsumption succeeds;
34. forged subsumption manifest rejected;
35. common-mode V1/V2 implementation bug not counted as independent bridge;
36. V2 new material observation triggers revalidation;
37. original retained -> V2 revalidation succeeds;
38. original deleted -> missing new observation degrades guarantee;
39. policy digest change without authorized handoff rejected;
40. verifier version omitted from consequential certificate rejected.

### E. Recursive/proof-system agility (41–50)
41. P2 binds exact P1 statement and parent digest;
42. P2 proves only generic `P1 PASS` and loses ROS -> rejected;
43. wrong P1 verification key generation rejected;
44. parent-proof substitution rejected;
45. recursive proof cycle/self-support rejected;
46. revoked ancestor identity preserved after compression;
47. P1 historical-only verifier embedded after retirement cannot create new authority;
48. P2 weaker acceptance language rejected;
49. proof-system upgrade with complete public-input subsumption succeeds;
50. proof verifier version drift without revalidation rejected.

### F. Offline/late verifier (51–60)
51. late verifier walks all intermediate roots successfully;
52. newest-root-only self-bootstrap rejected;
53. missing intermediate HC -> `INCOMPLETE_CHAIN`;
54. air-gap bundle with complete content-addressed history succeeds;
55. stale air-gap bundle after known local newer root rejected rollback;
56. valid anchored checkpoint skips history under explicit policy;
57. unanchored checkpoint rejected;
58. checkpoint commits wrong skipped history rejected;
59. offline verifier lacks retired algorithm implementation -> historical result unavailable, not guessed;
60. offline verifier later installs supported historical verifier and rechecks deterministically.

### G. Downgrade and support-set portability (61–70)
61. threshold reduction without stronger authorization rejected;
62. E3->E2 laundering rejected;
63. recovery support-set shrink rejected for inherited E3;
64. unknown ROS field rejected rather than ignored;
65. carrier generation drops revocation dependency rejected;
66. successor narrows namespace/context rejected;
67. explicit stronger policy-approved narrowing with retained original handled as new statement, not silent inheritance;
68. latest-wins conflicting HC rejected;
69. mixed-policy chain requires exact authorized transitions;
70. cross-tenant/root substitution rejected despite same object digest.

### H. GC/recovery/concurrency (71–80)
71. GC cannot delete old carrier evidence before valid successor handoff is durable;
72. crash after successor write before old-root cosign leaves no active handoff;
73. crash after dual-sign before persistence recovers idempotently;
74. concurrent conflicting successor rotations produce fork/quarantine;
75. revocation arriving during GC invalidates mark and re-roots closure;
76. retirement frontier advancing during destructive decision forces recheck;
77. archived old verifier material retrieval failure blocks deletion-authoritative verification;
78. disaster recovery from retained handoff bundle reproduces highest trusted generation;
79. proof compression followed by algorithm retirement still identifies exact affected ancestors;
80. independent verifier reproduces final `VALID/HISTORICAL_ONLY/REVALIDATION_REQUIRED` classification from canonical evidence.

## Implementation consequences for LAB-093 family

No production refactor is authorized by this research alone. When executable source becomes available, tests should be introduced before implementation.

Any future equivalence certificate schema should make carrier generation and semantic statement separate content-addressed objects so rotations do not require rewriting historical CS. Handoff, retirement, compromise and subsumption records should be append-only authenticated evidence with explicit lineage; cached terminal verdicts are not authority sources.

GC must retain whatever old carrier/verifier material is necessary to independently validate the handoff until a successor certificate has safely re-carried all applicable obligations and challenge/revocation horizons permit deletion.

## Decision

Freeze **`EQUIVALENCE_CERTIFICATE_TRUST_ROOT_ROTATION_CROSS_GENERATION_VERIFIER_HANDOFF_RECURSIVE_PROOF_AGILITY_V1_FROZEN`**.

The invariant is: **cryptographic/verifier carriers may rotate; historical semantic obligations do not. A successor receives authority only through authenticated continuity or independent replay/subsumption, and retired/compromised mechanisms never regain authority merely because they are embedded inside a newer signature or recursive proof.**

## Next distinct evidence task if exact execution remains unavailable

**Historical re-attestation scheduling / cryptographic sunset horizon / evidence refresh completeness semantics**: define how the system discovers every still-live certificate that depends on a soon-to-be-rejected carrier, proves the refresh campaign is complete before the sunset deadline, prioritizes irreplaceable E2/E3/E4 evidence, handles unreachable/offline archives, and prevents an algorithm retirement from silently stranding evidence after its original bytes were garbage-collected.