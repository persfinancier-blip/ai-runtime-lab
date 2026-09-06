# Semantic-equivalence substitution / minimal-retention witness / dependency-class portability v1

Status: `SEMANTIC_EQUIVALENCE_SUBSTITUTION_MINIMAL_RETENTION_WITNESS_DEPENDENCY_CLASS_PORTABILITY_V1_FROZEN`

Date: 2026-09-06

Scope: LAB-093 follow-up to dependency materiality / proof-carrying GC. This is a design and RED-first contract only. It does **not** claim production implementation, successful LAB-086 execution, or behavioral PASS.

## 1. Problem

The previous contracts intentionally make destructive evidence GC conservative. An `E1_REPRODUCIBILITY_INPUT`, `E2_VERIFICATION_DEPENDENCY`, or `E3_RECOVERY_DEPENDENCY` object remains live while a supported guarantee still depends on it. That is safe, but it can make retention expensive when historical objects are large and only a smaller semantic projection is actually required by every supported verifier/recovery path.

The obvious optimization — retain a smaller canonical substitute and delete the original — creates a new authority problem. A substitute can be content-addressed and internally well formed while still dropping exactly the field that a future verifier, challenge, recovery path, or upgraded semantic rule needs. A producer can also choose the projection that makes its own old decision look valid.

Therefore storage reduction MUST NOT be inferred from size, canonicalization, a producer signature, matching current output, or a one-version verifier PASS. Substitution is a new authenticated claim:

> For a specific dependency class, guarantee namespace, verifier/recovery version set, and policy frontier, substitute object `S` preserves every material semantic observation of original object `O` required by the supported guarantee.

That claim must be independently verifiable and revocable.

## 2. Donor mechanisms and applicability

### Reproducible Builds — bit identity is the strongest cheap equivalence

Reproducible Builds defines reproducibility as independent recreation of bit-for-bit identical artifacts from the same source, environment and instructions; cryptographic digests make equality compact to verify.

LAB inference: if `hash(O) == hash(S)` under the same canonical object encoding, this is ordinary content identity and no semantic-substitution authority is needed. The difficult case starts only when bytes differ.

Primary sources:
- https://reproducible-builds.org/docs/definition/
- https://reproducible-builds.org/docs/checksums/

### Nix content addressing — identity includes object graph/reference context

Nix content-addressed store objects derive identity from the file-system object graph plus references and other intrinsic store-object properties; GC keeps roots and transitive references live.

LAB inference: hash equality of an isolated payload is insufficient when the supported semantics include references/context. A substitute binding must include the semantic context required by the dependency class, not just a byte digest of a detached payload.

Primary sources:
- https://releases.nixos.org/nix/nix-2.30.1/manual/store/store-object/content-address.html
- https://releases.nixos.org/nix/nix-2.26.3/manual/command-ref/nix-store/gc.html

### SLSA provenance — subject digest alone does not prove equivalent inputs/semantics

SLSA provenance binds subjects to cryptographic digests and records build definition / resolved dependencies. Verification checks that the attested subject digest matches the artifact under verification, while provenance quality depends on the trusted builder and completeness of captured inputs.

LAB inference: a signed attestation that names `S` cannot prove `S` is a safe replacement for `O` unless the equivalence procedure itself is part of an authenticated, independently verified policy and its material inputs are complete enough for the claim.

Primary sources:
- https://slsa.dev/spec/v1.2/build-provenance
- https://slsa.dev/spec/v1.2/verifying-artifacts

### in-toto — materials/products and inspections separate provenance from policy verification

in-toto records materials/products for authorized steps and verifies them against a signed layout plus inspections.

LAB inference: semantic substitution should be represented as an explicit transformation/verification step with bound inputs, outputs, functionary/verifier identity and policy, not as an implicit alias in the GC layer.

Primary source:
- https://in-toto.io/docs/getting-started/

## 3. Core rule: identity, projection and equivalence are different

Every candidate replacement MUST fall into exactly one category.

### `IDENTICAL_BYTES`

`O` and `S` have the same canonical byte representation and content digest. This is identity, not semantic substitution.

GC effect: references may be retargeted to the same content address if object-context requirements also match.

### `LOSSLESS_REENCODING`

Bytes differ, but a frozen reversible transform can recover the exact canonical bytes of `O` from `S` with no external secret or discarded state.

GC effect: `S` may replace `O` only if the decoder/version and all required decoding dependencies are themselves retained/authenticated at at least the same dependency class needed to reconstruct `O`.

Examples: a deterministic archive/compression representation whose exact decompressed bytes and metadata are committed.

### `SEMANTIC_EQUIVALENT`

Bytes differ and exact `O` cannot be reconstructed, but a frozen equivalence relation proves that all material observations required for a declared guarantee set are equal.

GC effect: allowed only under an authenticated substitution decision scoped to dependency class, namespace, verifier/recovery version set and policy frontier.

### `LOSSY_PROJECTION`

`S` intentionally omits information and no current-policy proof establishes preservation of all material observations.

GC effect: cannot substitute for `E1/E2/E3`. It may coexist as `E0_AUDIT_PROVENANCE` or a cache/index, but the original remains live if the stronger edge remains live.

## 4. Equivalence is relative to a guarantee, never universal

There is no global boolean `equivalent(O,S)` suitable for destructive GC.

Define a canonical equivalence claim:

`EQ = (O_digest, S_digest, class, namespace, observation_schema_gen, verifier_set_gen, recovery_set_gen, context_digest, policy_gen)`

The claim is true only when every material observation function admitted by that tuple produces the same authoritative result on `O` and `S`, or when a lossless reconstruction proof restores `O` exactly.

Consequences:

1. Equivalence for `E1` does not imply equivalence for `E2` or `E3`.
2. Equivalence for verifier v5 does not automatically extend to verifier v6.
3. Equivalence in namespace A cannot be reused in namespace B merely because payload hashes are the same.
4. A context-free substitute cannot satisfy a context-dependent observation.
5. Future policy may invalidate an old substitution and re-root the original if it still exists or require guarantee degradation if it does not.

## 5. Dependency-class portability

### 5.1 `E1_REPRODUCIBILITY_INPUT`

A substitute is portable for `E1` only if all supported reproduction procedures either:

- reconstruct the exact original material bytes/context from `S`; or
- independently reproduce the same declared result while treating `S` as the canonical allowed representation under the frozen reproduction schema.

If build/debug/reproduction procedures consume fields removed by `S`, the substitute is not `E1`-portable even if current final output hashes happen to match once.

### 5.2 `E2_VERIFICATION_DEPENDENCY`

A substitute is portable for `E2` only if every supported verifier version in the declared support set can verify the consequential claim from `S` with the same fail-closed semantics as from `O`.

A producer-local extractor that emits only the fields its own verifier currently reads is insufficient. The observation schema must be separately authenticated and independently implemented or cross-checked for consequential use.

### 5.3 `E3_RECOVERY_DEPENDENCY`

A substitute is portable for `E3` only if every supported recovery procedure/failure class in scope can reach the same authenticated safe state using `S` instead of `O`.

Recovery has the strongest anti-projection rule: a field unused during normal verification may still be necessary only during corruption, rollback, fork, revocation or disaster recovery. Any such field makes a smaller verifier-only substitute invalid for `E3`.

### 5.4 `E4_AUTHORITY_CONTINUITY`

Default rule: semantic substitution is **not** allowed merely to save space for `E4` authority-continuity evidence. Prefer byte identity or lossless re-encoding. A semantic substitute for `E4` requires a separately frozen authority-continuity subsumption contract at least as strong as the original trust path and is outside this v1 ordinary substitution path.

## 6. Canonical substitution record

Every destructive substitution decision MUST bind at minimum:

- substitution record version;
- original object digest and original object type/schema generation;
- substitute digest and substitute type/schema generation;
- substitution category (`IDENTICAL_BYTES`, `LOSSLESS_REENCODING`, `SEMANTIC_EQUIVALENT`);
- dependency class being preserved;
- exact guarantee namespace / verdict/checkpoint/recovery closure;
- observation-schema generation;
- supported verifier-version set generation;
- supported recovery-version/failure-set generation when `E3` is involved;
- object/context binding digest (references, namespace identity, logical DB/history identity, trust frontier as applicable);
- equivalence procedure/toolchain generation;
- independent verifier/adjudicator generations and diversity domains;
- proof/witness bundle digests;
- original-retention fallback location/availability state during the challenge horizon;
- policy/trust/repair frontiers under which the decision was accepted;
- explicit blast radius;
- decision (`ACCEPT`, `REJECT`, `QUARANTINE`, `REVALIDATION_REQUIRED`);
- signatures/threshold authorization required by current policy.

The record is immutable and additive. Revalidation creates a successor record; no old record is rewritten.

## 7. Minimal-retention witness

A **minimal-retention witness (MRW)** is the smallest authenticated proof bundle that lets an independent verifier determine why `S` is sufficient for the retained class/guarantee and why deleting `O` is currently allowed.

An MRW MUST contain or content-address:

1. the exact substitution record;
2. commitment to `O` and `S`;
3. observation/equivalence schema generation;
4. proof that every required observation was compared or exactly reconstructable;
5. verifier/recovery support-set manifest;
6. independent verifier verdicts and diversity-domain data;
7. context-binding evidence;
8. challenge/revocation status;
9. GC root/frontier snapshot and proof that no stronger live edge still requires exact `O`;
10. archive/fallback evidence during the substitution challenge horizon;
11. deletion authorization bound to the exact GC epoch.

A small `S` without the MRW is merely a cache/projection. It has zero destructive-GC authority.

## 8. Independent equivalence proof

For `SEMANTIC_EQUIVALENT`, default policy for consequential `E2/E3` MUST require at least two independent evidence paths:

- **transform-side evidence**: deterministic derivation of `S` from `O` under a frozen transform/schema; and
- **verifier-side evidence**: independent comparison that exercises all material observation functions admitted by the guarantee.

The same buggy extractor must not define the projection and then certify that its own output retained everything important.

Independence is evaluated using the existing semantic/toolchain/dependency diversity contracts. Two nominally separate verifiers collapse into one diversity domain if they share the same material parser, canonicalizer, semantic oracle or generated decision code.

For finite structured records, proof may be an authenticated field/relationship coverage manifest plus independent replay. For executable behavior, equivalence testing alone is generally incomplete; destructive substitution is therefore allowed only for a frozen, explicitly enumerable observation interface or a stronger formal proof accepted by policy.

`tests passed on current samples` is not an equivalence proof.

## 9. Verifier-version drift

Every accepted semantic substitution is scoped to a **support-set generation**.

When a new verifier/recovery generation is admitted:

1. compute whether it introduces a new material observation or interprets an existing field differently;
2. if no new observation exists, publish authenticated subsumption from old support set to new;
3. if a new observation exists, every affected substitution becomes `REVALIDATION_REQUIRED` before the new verifier can be consequentially authoritative;
4. if the original `O` is still retained/archived, re-run equivalence against `O`;
5. if `O` was already deleted and `S` cannot answer the new observation, the system MUST degrade/retire the affected guarantee or use an independently retained proof sufficient for the new observation. It MUST NOT invent the missing data.

This is why substitution deletion needs a conservative horizon and why `E3` should normally retain originals much longer than `E1`.

## 10. Context-invalid reuse

Content identity of `S` does not imply semantic portability across contexts.

A substitution MUST fail closed when any material context differs, including as applicable:

- trust-root / authority-frontier generation;
- provider or logical-history identity;
- schema/taxonomy generation;
- namespace / subject key;
- external anchor position;
- recovery epoch/failure class;
- object references/dependency graph;
- canonicalization rules;
- interpretation/toolchain generation.

A substitute hash reused under a different context needs a separate authenticated substitution decision unless the policy explicitly proves context independence.

## 11. Substitution revocation and fallback

Substitution is revocable without rewriting the original evidence graph.

Triggers for revalidation/revocation include:

- equivalence verifier/parser/canonicalizer compromise;
- newly discovered material field omitted by the projection;
- support-set expansion;
- recovery failure using `S`;
- context-binding defect;
- forged/incomplete MRW;
- discovered common-mode verifier dependence;
- policy/taxonomy repair that upgrades the dependency class;
- conflicting authenticated equivalence verdicts.

On trigger:

1. mark affected substitution closure `REVALIDATION_REQUIRED`;
2. make all pre-trigger destructive GC marks stale;
3. re-root retained originals/archive copies while available;
4. prefer the exact original for verification/recovery until revalidation succeeds;
5. if original is already deleted, quarantine affected consequential verdicts/guarantees rather than silently trusting `S`;
6. preserve the old substitution record as historical evidence.

## 12. Challenge horizon and deletion rule

A newly accepted semantic substitute SHOULD NOT cause immediate physical deletion of `O`.

Minimum safe sequence:

1. admit `S` and MRW;
2. keep `O` reachable through a substitution-challenge root;
3. independently retrieve/replay `S`, MRW and `O` from the configured durability domains;
4. wait through the policy challenge/revocation observation horizon;
5. freeze trust/schema/materiality/substitution frontiers;
6. recompute dependency graph and complete mark;
7. prove no `E4`, stronger `E3`, unresolved challenge, fork, revocation or unsupported verifier path still needs exact `O`;
8. issue GC-epoch-specific deletion authorization;
9. re-check frontiers immediately before physical deletion.

No retention budget or operator pressure may skip these steps for consequential evidence.

## 13. Anti-laundering rules

1. Smaller size is never evidence of equivalence.
2. Matching a current verdict is not enough; all material observations must be preserved.
3. Producer self-attestation alone cannot authorize destructive substitution.
4. Canonicalization may remove only fields proven non-material for the exact class/support set.
5. Unknown fields default to materiality `UNKNOWN`, not disposable.
6. Hash-identical detached payloads cannot be reused when context binding differs.
7. A semantic substitute cannot downgrade `E3` to `E2` merely because normal verification succeeds.
8. A substitute must not erase evidence needed to audit the equivalence transform itself.
9. Cyclic substitution records do not self-authorize liveness or deletion.
10. Substitution chains (`O -> S1 -> S2`) require transitive proof composition; `S2` cannot rely on a property that `S1` already discarded.
11. A revoked substitute does not retroactively erase historical evidence that it was used.
12. GC must consider the strongest live class across all original and repaired dependency edges before deleting `O`.

## 14. 80-case RED-first matrix

No production substitution/GC implementation should be integrated until these cases exist as executable RED-first tests at the appropriate abstraction level.

### A. Identity / lossless boundary (1-10)

1. exact canonical bytes, same digest -> identity accepted;
2. one-byte difference -> not identity;
3. same payload but different required metadata/context -> identity reuse rejected;
4. deterministic compression round-trip reconstructs exact bytes -> lossless accepted;
5. compression drops filename/mode that is material -> rejected for affected class;
6. decoder version missing -> lossless substitute not deletion-authoritative;
7. decoder dependency revoked -> substitution revalidation required;
8. encrypted archive without retained authorized decryption path -> rejected;
9. archive claims original digest but decompression differs -> rejected;
10. malformed substitute with matching self-declared digest -> rejected.

### B. E1 reproducibility portability (11-20)

11. substitute reproduces exact declared artifact across independent run -> candidate accepted;
12. single lucky matching run but nondeterministic omitted seed -> rejected;
13. omitted build flag changes debug/reproduction behavior -> rejected;
14. omitted dependency version affects reproduction -> rejected;
15. canonical source archive preserves all declared build inputs -> accepted under exact schema;
16. generated cache can reproduce output only while remote service exists -> rejected unless service dependency is retained/authenticated;
17. substitute requires unrecorded environment variable -> rejected;
18. old reproducer succeeds but newly supported reproducer needs omitted field -> revalidation required;
19. reproduction policy retired explicitly -> E1 retention may expire, but no implicit downgrade;
20. E1 substitute reused for unrelated namespace -> rejected absent portability proof.

### C. E2 verification portability (21-30)

21. all supported verifier observations equal -> candidate accepted;
22. current verifier ignores a field used by another supported verifier -> rejected;
23. projection built and verified by same buggy parser only -> insufficient independence;
24. two verifiers share same material canonicalizer bug -> diversity collapse;
25. verifier v6 adds material observation -> old substitution revalidation required;
26. support-set manifest omits an active verifier -> rejected;
27. substitute changes failure classification while preserving PASS result -> rejected when failure semantics are material;
28. substitute preserves signature fields but drops signed context binding -> rejected;
29. substitute supports verification only after network lookup not covered by retained dependencies -> rejected;
30. independent verifier reproduces MRW and exact observation closure -> accepted.

### D. E3 recovery portability (31-40)

31. normal verification works but fork recovery needs omitted branch evidence -> rejected;
32. rollback recovery needs original timestamp/frontier field omitted by substitute -> rejected;
33. revocation recovery needs historical signer lineage omitted by substitute -> rejected;
34. substitute works for crash recovery but not compromise recovery in declared set -> rejected;
35. recovery-set manifest excludes a currently supported failure class -> rejected;
36. recovery v2 introduces new required observation -> revalidation required;
37. substitute reaches same data state but cannot prove same authority state -> rejected;
38. substitute relies on unavailable external secret -> rejected;
39. exact original archived through independent domain during challenge -> fallback recognized;
40. original deleted after E3 substitute accepted, then recovery failure discovered -> affected guarantee quarantined, not silently accepted.

### E. Context binding / reuse (41-50)

41. same substitute digest, different trust frontier -> separate decision required;
42. same payload, different provider/history identity -> reuse rejected;
43. same payload, different schema generation with same observations -> requires authenticated subsumption;
44. same namespace and context -> reuse allowed only within explicit policy scope;
45. detached hash lacks dependency references required by semantics -> rejected;
46. subject-key collision maps two originals to same substitute -> fail closed;
47. canonicalizer generation changes ordering semantics -> revalidation required;
48. old context digest forged/self-asserted by producer -> rejected;
49. context-independence formally/authentically proven for a field set -> bounded reuse accepted;
50. substitute copied across tenant/security domain without authority portability proof -> rejected.

### F. Revocation / conflict / drift (51-60)

51. equivalence signer revoked before deletion -> mark stale;
52. semantic parser vulnerability discovered after acceptance -> re-root originals/revalidate;
53. conflicting authenticated PASS/FAIL equivalence verdicts -> disagreement/quarantine;
54. latest-wins attempts to erase older conflict -> rejected;
55. common-mode dependency discovered among threshold verifiers -> quorum recomputed;
56. taxonomy repair upgrades edge from E2 to E3 -> substitution re-evaluated under E3;
57. new material field discovered while original still archived -> replay against original;
58. new material field discovered after original deleted -> guarantee degradation/quarantine if S insufficient;
59. substitute revocation does not delete historical usage record;
60. resolved disagreement produces new additive decision, not mutation of old record.

### G. GC / challenge / archive races (61-70)

61. substitute accepted but challenge horizon open -> original remains rooted;
62. archive write succeeds but independent re-read fails -> hot original not deleted;
63. trust frontier advances after mark before delete -> mark stale;
64. support-set changes after mark before delete -> mark stale;
65. revocation lands concurrently with deletion -> pre-delete frontier check blocks delete;
66. retention budget exceeded -> alert/degrade policy, no silent deletion;
67. substitute chain drops observation at S1->S2 -> original/S1 cannot be pruned on false transitivity;
68. dangling MRW reference -> substitution not deletion-authoritative;
69. GC sees only substitute edge but stronger repaired original edge exists -> original retained;
70. crash after delete authorization but before physical delete -> restart rechecks authorization/frontiers.

### H. Malicious / incomplete substitution (71-80)

71. producer chooses projection that hides its own invalid field -> independent verifier rejects;
72. substitute contains only fields needed to reproduce current PASS -> rejected if failure/recovery observations omitted;
73. unknown extension field silently stripped -> default UNKNOWN/material until adjudicated;
74. giant object replaced by self-hash only -> rejected for E1/E2/E3;
75. “equivalent” PDF/text summary replaces signed binary evidence -> rejected absent exact supported observation contract;
76. same logical records but duplicate/order information was material -> rejected;
77. normalized timestamps remove ordering evidence -> rejected when frontier semantics depend on them;
78. substitute claims smaller blast radius than dependency graph proves -> rejected;
79. MRW signed by unauthorized/out-of-scope adjudicator -> rejected;
80. independent replay from frozen artifacts reconstructs the same substitution decision and GC eligibility -> PASS criterion for production readiness.

## 15. Composition with existing frozen contracts

This v1 composes with, and does not weaken:

- dependency-schema evolution and authenticated repair edges;
- materiality adjudication / semantic edge taxonomy;
- proof-carrying GC reachability and complete-mark proofs;
- trust-root/verifier diversity and revocation;
- snapshot/bootstrap provenance;
- omission/non-inclusion/mapper-completeness evidence.

Specific composition rules:

- substitution decisions themselves become evidence objects in the dependency graph;
- MRW/verifier/toolchain/context artifacts are `E2` or stronger when needed to validate a consequential destructive substitution;
- the original `O` remains rooted through the challenge horizon and whenever stronger edges, disputes, revocations or unsupported version transitions exist;
- an accepted substitute never proves that all future verifiers/recovery procedures will remain equivalent;
- `UNKNOWN` portability fails closed for destructive GC.

## 16. Frozen implementation contract

A future implementation MUST be regression-first and MUST NOT start by adding a generic `semantic_hash()` or “canonical compact evidence” helper.

Required implementation order:

1. introduce typed substitution records and support-set/context bindings;
2. implement identity/lossless cases first;
3. add MRW validation with no destructive effect;
4. add independent semantic-equivalence adjudication for one narrowly enumerable `E2` evidence type;
5. execute RED matrix for false equivalence/version drift/context reuse;
6. integrate with GC as a new deletion precondition, not as replacement for reachability;
7. add substitution revocation/revalidation and original fallback;
8. only then consider `E3`; keep `E4` out unless separately proven.

No production destructive substitution should be claimed until exact executable tests prove the relevant RED cases and a separate audit finds no unsupported observation path.

## 17. Decision

Freeze `SEMANTIC_EQUIVALENCE_SUBSTITUTION_MINIMAL_RETENTION_WITNESS_DEPENDENCY_CLASS_PORTABILITY_V1_FROZEN`.

The central invariant is:

> A smaller object may replace exact retained evidence only when an authenticated, independently reproducible proof establishes equivalence for the exact dependency class, guarantee namespace, context and supported verifier/recovery generation set; any unknown, drift, revocation or stronger live dependency re-roots the original or degrades the guarantee rather than laundering lossy storage optimization into authority.

This is donor-derived design evidence only. No production code or behavioral PASS is claimed.