# Archive restore verifier reproducibility / hermetic verifier supply-chain / executable-obsolescence v1

Date: 2026-09-07
Status: **ARCHIVE_RESTORE_VERIFIER_REPRODUCIBILITY_HERMETIC_SUPPLY_CHAIN_EXECUTABLE_OBSOLESCENCE_V1_FROZEN**
Parent: LAB-093 / #178

## Question

When an archive is complete, independently replicated, WORM-protected and physically restorable, what additional proof is required before destructive GC may depend on the claim that the archived evidence will still be independently verifiable years later, after package registries, mutable image tags, language runtimes, CPU/ABI assumptions, signing/build infrastructure or historical crypto/tooling disappear or become untrusted?

## Executive result

`BYTES_RETRIEVABLE` and `EVIDENCE_VERIFIABLE` are distinct closure properties.

A successful archive restore does **not** prove long-term verification if the verifier still depends on live package registries, mutable container tags, current OS packages, current trust stores, current language runtimes, current provider APIs, or undocumented host CPU/ABI behavior.

For destructive archive dependency, require a current `VERIFIER_DURABILITY_CLOSED` proof in addition to archive completeness and archive durability. The proof must establish that the historical verifier semantic generation can be executed or independently reconstructed from archived, content-addressed inputs without trusting mutable external services.

## Core invariants

### V1 — verifier semantics are archived evidence

The verifier implementation, exact semantic schema, parser rules, canonicalization rules, crypto algorithm parameters, historical trust-policy generation, expected inputs/outputs and negative-test corpus are themselves first-class archive objects.

A source URL, package name, Git branch, container tag or documentation link is not an archival identity.

### V2 — content identity before execution

Every executable/runtime/dependency object must be selected by immutable digest and size before execution. OCI content descriptors are a useful donor: a descriptor binds media type, digest and byte size, and consumers are expected to verify retrieved bytes against the digest before use.

A mutable `latest`, semver range, branch ref, package-registry resolution result or runtime download URL cannot satisfy hermetic replay.

### V3 — source-only is insufficient unless rebuild closure is proven

Archiving verifier source alone is insufficient when rebuilding requires unavailable compilers, package indexes, generated code, external downloads, mutable build scripts or host-specific behavior.

A source path may satisfy the closure only if all build inputs and instructions are archived and an independent rebuild reproduces the expected artifact bit-for-bit or produces an independently justified semantic-equivalent artifact.

The Reproducible Builds definition is the positive donor: given the same source, build environment and build instructions, independent parties can recreate bit-for-bit identical specified artifacts. `SOURCE_DATE_EPOCH` is one mechanism for eliminating time-dependent build output, not a complete reproducibility proof.

### V4 — binary-only is insufficient unless execution substrate is durable

Archiving one executable binary is insufficient when its ISA, ABI, dynamic loader, libc, kernel interface, accelerator instruction set or runtime is not independently preserved.

A durable verifier bundle therefore needs either:

1. a sufficiently self-contained native executable plus exact execution-contract metadata and independently preserved compatible substrate; or
2. a preserved VM/runtime image selected by digest; or
3. a preserved emulator/interpreter path capable of executing the historical substrate.

QEMU is a useful donor for the third path because its TCG system/user emulation supports current and legacy CPU architectures. Emulation is a survivability mechanism, not an authenticity proof; the emulator itself must be archived and verified like every other executable dependency.

### V5 — container image is packaging, not immortality

A container image pinned by OCI digest is useful because its component graph is content-addressed, but it does not by itself close execution durability. Host kernel, CPU architecture, runtime-spec implementation and external mounts/devices remain outside the image.

Therefore `oci_digest_pinned=true` may support `HERMETIC_INPUTS_CLOSED`, but cannot alone imply `EXECUTION_SUBSTRATE_CLOSED`.

### V6 — historical verification must not silently migrate

A future verifier semantic generation must not reinterpret old receipts merely because it is newer.

Every verification result binds:
- archive generation/root;
- receipt/evidence semantic generation;
- verifier semantic generation;
- parser/canonicalizer generation;
- historical trust-policy generation;
- runtime/substrate generation;
- cryptographic algorithm suite.

Migration from verifier generation N to N+1 requires an explicit cross-generation equivalence or successor-proof campaign over the retained historical corpus. Until then, N remains authoritative for N-era evidence.

### V7 — crypto agility is additive, never retrospective wishful thinking

When a hash/signature algorithm approaches obsolescence, the system must create a stronger authenticated renewal binding **before** the old primitive can no longer support the required claim.

Keeping old bytes after the primitive is no longer defensible is not crypto agility. Archive renewal must preserve the old evidence and bind it into the successor proof; it must not rewrite historical receipts.

### V8 — executable provenance is not executable availability

Source/build provenance explains where an executable came from. It does not prove that the executable can still be run.

Conversely, a runnable binary does not prove it implements the intended verifier semantics.

`VerifierDurabilityProofV1` therefore requires both provenance/reproducibility evidence and observed replay evidence.

## Required objects

### `HermeticVerifierBundleV1`

Minimum fields:
- `bundle_id`;
- `archive_generation` and `archive_root`;
- `verifier_semantic_generation`;
- exact source-tree digest(s);
- exact verifier executable digest(s);
- exact dependency/artifact digests;
- build recipe/instruction digest;
- build-environment manifest digest;
- runtime/VM/container filesystem digest(s);
- target ISA/ABI/OS/kernel-interface assumptions;
- emulator/interpreter digest(s), if required;
- canonicalizer/parser/schema digests;
- crypto implementation and parameter identifiers;
- historical trust-policy digest;
- positive/negative conformance-corpus root;
- expected verdict root;
- licenses/provenance required for lawful future reconstruction;
- external-input declaration, which must be empty for hermetic replay except explicitly archived read-only inputs.

### `VerifierBuildReproductionProofV1`

Records at least two independently instantiated builds where practical:
- exact input root;
- builder implementation/environment identities;
- produced artifact digests;
- equality verdict;
- documented nondeterminism exclusions, if any;
- failure reason when equality is not achieved.

For high assurance, a single builder recreating its own output is weaker than independent builders/environments agreeing on the artifact.

### `VerifierReplayDrillV1`

A periodic isolated drill must:
1. start without live registry/package/provider/trust-store access;
2. restore the hermetic verifier bundle from a non-primary archival replica;
3. verify every bundle object by immutable digest/size;
4. instantiate the declared runtime or emulator path;
5. run the positive and adversarial conformance corpus;
6. verify a representative historical archive sample end-to-end;
7. compare verdicts against the frozen expected-verdict root;
8. record host assumptions that were actually required;
9. fail if undeclared network/package/runtime resolution occurs.

A checksum-only check is not a replay drill.

### `VerifierDurabilityProofV1`

States:
- `OPEN`;
- `HERMETIC_INPUTS_CLOSED`;
- `EXECUTION_SUBSTRATE_CLOSED`;
- `REPRODUCIBILITY_CLOSED`;
- `REPLAY_VERIFIED`;
- `VERIFIER_DURABILITY_CLOSED`;
- `UNKNOWN_OBSOLESCENCE_RISK`;
- `FAILED`.

`VERIFIER_DURABILITY_CLOSED` requires all preceding positive closures plus a fresh replay under the current `RestoreFreshnessPolicyV1`-equivalent policy.

## Dependency and registry rules

The authoritative bundle must not require package-manager re-resolution at replay time.

Archive exact package/artifact bytes, metadata needed to validate them, and dependency graph edges. Package lockfiles help but are insufficient when referenced packages can disappear or be replaced and the bytes are not independently retained.

For OCI artifacts, retain the entire reachable content DAG, not only the manifest digest. Before execution verify each descriptor's digest and size.

For language ecosystems, archive the interpreter/compiler/runtime when its semantics materially affect verification. `requirements.txt`, `Cargo.lock`, `go.sum`, `package-lock.json` or equivalent remain provenance inputs, not substitutes for retained dependency bytes when long-term availability is required.

## Build reproducibility rules

A reproducibility claim must bind source, environment and instructions, matching the Reproducible Builds model.

Normalize or eliminate build-time nondeterminism. Time normalization such as `SOURCE_DATE_EPOCH` is allowed but must be declared in the build environment manifest.

If exact bit reproduction is impossible, the result cannot silently be called reproducible. A separately defined semantic-equivalence proof may be created, but it is weaker and must show that both implementations agree across the complete frozen conformance corpus plus targeted parser/crypto edge cases.

## Runtime and emulator survivability

The bundle records every material host contract:
- ISA and required extensions;
- endianness/word size;
- system-call/kernel ABI assumptions;
- dynamic loader and shared-library identities;
- locale/timezone/Unicode data assumptions;
- filesystem semantics;
- entropy/randomness assumptions;
- floating-point behavior if material;
- hardware-backed crypto requirements.

Where native replay may disappear, preserve an emulator/VM fallback and test it periodically before the old substrate becomes unavailable.

An emulator path is considered healthy only after observed replay of the same verifier corpus; theoretical architecture support is insufficient.

## Trust and supply-chain independence

The verifier must not obtain historical trust from today's mutable OS trust store or provider account.

The hermetic bundle references the already frozen `HistoricalTrustBundleV1`. It may contain verification software for signatures/timestamps/transparency evidence, but the historical trust facts remain archive data, not live network queries.

The archival verifier's own authenticity should be established using at least one path independent from the system that produced the evidence being verified. A self-signed build log produced by the same mutable builder is provenance telemetry, not independent verification.

## Migration and obsolescence protocol

When runtime/toolchain/crypto obsolescence is detected:

1. freeze the current authoritative verifier generation N;
2. restore N from independent custody and replay its corpus;
3. construct N+1 from archived or newly reviewed inputs;
4. execute N and N+1 over the frozen historical/adversarial corpus;
5. investigate every verdict or canonical-byte divergence;
6. create an authenticated `VerifierGenerationMigrationProofV1` binding both generations and the comparison root;
7. replicate and restore-test N+1 before declaring it durable;
8. retain N; never rewrite historical evidence to look native to N+1.

If N can no longer execute before equivalence is established, affected historical evidence becomes `UNKNOWN_OBSOLESCENCE_RISK`; destructive GC may not newly depend on it.

## Negative boundaries

The following do **not** prove verifier durability by themselves:
- Git commit/tag;
- source archive;
- SBOM;
- provenance statement;
- package lockfile;
- OCI tag;
- OCI digest without the complete reachable content DAG and execution substrate;
- Dockerfile/container image;
- VM image without preserved runtime/emulator and verified boot/execution path;
- one successful build;
- one successful replay on the original host;
- current package-registry availability;
- current cloud account/provider API availability;
- current OS trust store;
- theoretical QEMU/emulator support;
- timestamp/signature over an executable without semantic-generation binding.

## Destructive-GC gate

Historical primary evidence may be destructively removed only while all of these are current:

`FINAL_ARCHIVE_CLOSED`
AND `ARCHIVE_DURABILITY_CLOSED`
AND `VERIFIER_DURABILITY_CLOSED`.

If any proof becomes stale because of topology, key, runtime, verifier, dependency, crypto-policy, emulator or host-contract change, destructive GC pauses until the corresponding replay/migration campaign closes again.

## Failure / fraud proofs

Define at minimum:
- `UndeclaredExternalDependencyProofV1` — replay attempted live network/registry/provider resolution not declared by the bundle;
- `VerifierArtifactMismatchProofV1` — restored executable/dependency bytes differ from archived digest;
- `BuildNonReproductionProofV1` — independent rebuild from declared inputs produces a different authoritative artifact;
- `SemanticGenerationDriftProofV1` — newer verifier produces a different verdict/canonicalization without an authenticated migration proof;
- `ReplayExpectedVerdictMismatchProofV1` — isolated replay disagrees with frozen corpus expectation;
- `ExecutionSubstrateMissingProofV1` — no archived/tested native, VM or emulator path can execute the authoritative generation;
- `MutableReferenceDependencyProofV1` — an authoritative bundle resolves a mutable tag/range/branch/current trust store at execution time;
- `CryptoObsolescenceGapProofV1` — required primitive became unacceptable before a stronger renewal/migration binding was established.

Any proved item invalidates `VERIFIER_DURABILITY_CLOSED` for the affected scope.

## RED-first matrix (80 cases)

### Bundle identity / mutable references — 1..10
1. exact source/executable/dependency digests accepted;
2. changed executable rejected;
3. changed dependency rejected;
4. mutable OCI tag rejected as authority;
5. semver range rejected;
6. Git branch ref rejected;
7. package-registry latest resolution rejected;
8. complete OCI reachable DAG accepted after digest checks;
9. missing reachable layer rejected;
10. same label with different digest rejected.

### Hermetic execution — 11..20
11. offline replay succeeds;
12. undeclared DNS attempt fails;
13. undeclared package download fails;
14. live provider lookup fails;
15. live OS trust-store lookup fails;
16. archived read-only evidence input succeeds;
17. undeclared writable host mount fails;
18. environment-variable semantic dependency detected;
19. locale/timezone dependency detected;
20. hidden current-time dependency detected.

### Reproducible build — 21..30
21. independent builders produce identical artifact;
22. timestamp nondeterminism produces RED;
23. normalized time closes reproduction;
24. unarchived generated source fails;
25. missing compiler fails;
26. mutable compiler package fails;
27. changed build flag changes digest and fails;
28. same source/different dependency fails;
29. source-only bundle without build closure remains OPEN;
30. semantic-equivalence path cannot masquerade as bit reproducibility.

### Runtime / ABI — 31..40
31. native current-ISA replay succeeds;
32. missing dynamic loader fails;
33. mismatched libc fails;
34. missing CPU extension fails;
35. preserved VM runtime succeeds;
36. emulator replay succeeds;
37. theoretical emulator support without drill remains OPEN;
38. endian/word-size mismatch detected;
39. Unicode/locale database drift detected;
40. material kernel/syscall behavior drift detected.

### Semantic generation — 41..50
41. N verifies N evidence;
42. N+1 agrees across frozen corpus and authenticated migration succeeds;
43. N+1 verdict divergence blocks migration;
44. canonical-byte divergence blocks migration;
45. historical evidence not rewritten;
46. N retained after N+1 activation;
47. unknown schema remains UNKNOWN;
48. accidental default-to-current parser rejected;
49. migration proof wrong corpus root rejected;
50. rollback from N+1 authority to unapproved N rejected where generation witness forbids it.

### Crypto agility / trust — 51..60
51. historical trust bundle used offline;
52. current root store substitution rejected;
53. pre-obsolescence renewal succeeds;
54. post-gap renewal cannot retroactively close gap;
55. expired-but-historically-valid credential handled per historical policy;
56. compromised-before-event fails;
57. unknown compromise interval stays UNKNOWN;
58. crypto implementation replacement requires generation migration;
59. algorithm-policy change stales proof;
60. timestamp alone cannot prove verifier semantics.

### Replay drills / custody — 61..70
61. replay from non-primary replica succeeds;
62. primary-only replay is insufficient for high-assurance durability;
63. key-recovery path exercised;
64. emulator path exercised;
65. positive corpus passes;
66. adversarial corpus passes;
67. expected-verdict mismatch fails;
68. topology change invalidates freshness;
69. runtime/toolchain change invalidates freshness;
70. stale replay blocks new destructive GC.

### Crash / corruption / fraud — 71..80
71. partial bundle capture fails;
72. manifest/object digest mismatch fails;
73. truncated VM/runtime artifact fails;
74. builder claims success but artifact differs -> fraud proof;
75. replay harness omits negative tests -> completeness failure;
76. hidden network fallback -> fraud proof;
77. same semantic generation with different expected-verdict roots -> equivocation;
78. obsolete executable with no working substrate -> UNKNOWN_OBSOLESCENCE_RISK;
79. N+1 migration crash before durable proof keeps N authoritative;
80. destructive GC request with any verifier closure stale is rejected.

## Primary donors / current evidence

1. Reproducible Builds, definition: reproducibility requires same source, build environment and build instructions to recreate bit-for-bit identical artifacts. https://reproducible-builds.org/docs/definition/
2. Reproducible Builds, `SOURCE_DATE_EPOCH`: standardized mechanism for removing build-time timestamp nondeterminism. https://reproducible-builds.org/docs/source-date-epoch/
3. OCI Image Spec, content descriptors: content is identified by digest and size and should be verified before consumption. https://specs.opencontainers.org/image-spec/descriptor/
4. OCI Image Spec config: image configuration and layer identities are immutable/content-addressed; changing content changes identity. https://github.com/opencontainers/image-spec/blob/main/config.md
5. QEMU emulation documentation: TCG supports system/user emulation across current and legacy CPU architectures, providing a practical execution-survivability donor. https://www.qemu.org/docs/master/about/emulation.html

## Decision

Freeze `ARCHIVE_RESTORE_VERIFIER_REPRODUCIBILITY_HERMETIC_SUPPLY_CHAIN_EXECUTABLE_OBSOLESCENCE_V1_FROZEN`.

LAB-093 implementation must treat verifier durability as an independent closure dimension. Archive completeness + replica durability + WORM + byte restoration do not authorize destructive dependency unless the exact historical verification semantics remain hermetically executable or independently reproducible and have passed a fresh isolated replay drill.

## Next distinct research question if exact execution is still unavailable

**Verifier conformance-corpus completeness / parser differential testing / semantic-equivalence proof semantics**: define how to justify that the frozen replay corpus is strong enough to detect parser/canonicalization/crypto semantic drift rather than merely confirming happy-path compatibility; include grammar-derived adversarial generation, differential verifier execution, malformed/ambiguous encodings, algorithm edge cases, proof that N→N+1 equivalence is scoped rather than universal, and rules for keeping `UNKNOWN` when corpus coverage cannot justify equivalence.
