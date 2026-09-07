# Semantic inventory authority / effect-capability registration / latent-side-effect detection v1

Status: `SEMANTIC_INVENTORY_AUTHORITY_EFFECT_CAPABILITY_REGISTRATION_LATENT_SIDE_EFFECT_DETECTION_V1_FROZEN`

Date: 2026-09-07

Related: LAB-093 / #178; composes with manifest-schema authority, producer-bound effect manifests, federated finalization, refresh/GC and retained-authority contracts.

## Problem

`OperationSemanticInventoryV1` was introduced as an independent universe against which a closed-world manifest schema proves declaration-slot completeness. That only moves the common-mode failure one level outward if the semantic inventory itself can omit a real consequential effect path.

A runtime can gain effects through plugin loading, FFI/native calls, reflection/dynamic dispatch, generated wrappers, provider SDKs, broker clients, filesystem handles, delayed schedulers, authority/recovery APIs, subprocesses, pre-opened descriptors, or runtime upgrades. If those paths are absent from both the manifest schema and the inventory, a schema-completeness checker may honestly prove completeness over an incomplete universe.

The required property is therefore not "the inventory lists every effect we know about". It is: **every consequential effect capability that can become reachable is either registered and bound into the active semantic inventory generation before use, or mechanically prevented from producing an unregistered effect; independently observable consequential effects are reconciled against that declaration universe.**

## Donor mechanisms and limits

### Linux seccomp

Kernel seccomp filters can mediate system calls; `SECCOMP_RET_USER_NOTIF` can route selected calls to a userspace supervisor, while `SECCOMP_RET_LOG` is explicitly useful for learning which syscalls a program actually needs. This is a useful donor for an *effect choke point* and for discovery, but syscall identity alone is not semantic completeness: one syscall can encode many destinations/operations, userspace libraries can batch work, and kernel docs explicitly warn about architecture-dependent syscall interpretation.

Primary: https://docs.kernel.org/userspace-api/seccomp_filter.html

### Linux Landlock

Landlock models explicit access rights over kernel objects and composes restrictions monotonically. It is a donor for binding acquired capabilities to concrete allowed object/action classes rather than trusting a caller-declared intent. Its own limitations are important: pre-opened file descriptors and non-filesystem objects require separate treatment, so a filesystem-only inventory cannot claim general effect completeness.

Primary: https://docs.kernel.org/userspace-api/landlock.html

### eBPF LSM

BPF LSM programs attach to kernel security hooks and can provide runtime audit/enforcement at effect-relevant kernel boundaries. This is a donor for independently observed effect classes. It is not a semantic oracle by itself: it observes kernel events, not application-level business causality, and privileged/native surfaces outside the selected hooks remain a coverage concern.

Primary: https://www.kernel.org/doc/html/v5.9/bpf/bpf_lsm.html

### OpenTelemetry semantic conventions

OpenTelemetry messaging conventions distinguish create/send/receive/process/settle and require producer creation context propagation for correlation. This is a donor for stable semantic effect identities and producer-to-consumer linkage. It is observability, not authority: missing instrumentation cannot be interpreted as proof that no effect occurred.

Primary: https://opentelemetry.io/docs/specs/semconv/messaging/messaging-spans/

### SLSA provenance

SLSA requires external parameters to be enumerated at stronger levels, while resolved-dependency completeness remains best effort. It explicitly distinguishes trusted platform-generated fields from user-controlled build steps. This supports the boundary that inventory evidence for consequential effects must be generated/verified by a control plane outside the same untrusted producer path, and that "best effort" dependency discovery is not enough for destructive authority.

Primary: https://slsa.dev/spec/v1.2-rc2/build-provenance

## Frozen model

### 1. Capability classes

Each effect-capable primitive receives a stable `EffectCapabilityId` in one or more canonical classes:

- `C_STORAGE_MUTATE`: persistent storage write/delete/schema/topology mutation;
- `C_NETWORK_EMIT`: externally visible network/RPC request capable of changing remote state;
- `C_BROKER_EMIT`: queue/topic/event publication or settlement with downstream consequence;
- `C_DELAYED_WORK`: timer/job/task registration whose later execution can create another material effect;
- `C_AUTHORITY_MUTATE`: trust root, signer set, policy, provider generation, activation/fence, revocation or recovery authority mutation;
- `C_RECOVERY_MUTATE`: backup/restore/rollback/failover state that changes what can later be recovered or accepted;
- `C_GC_DEPENDENCY_MUTATE`: create/remove/repair a dependency or root relevant to destructive retention;
- `C_PROCESS_EXEC`: launch/attach/drive a subprocess or native helper that can itself gain consequential capabilities;
- `C_NATIVE_ESCAPE`: FFI/native/JIT/reflection/dynamic-loading surface able to obtain capabilities not represented by the managed call graph;
- `C_EXTERNAL_HANDLE_IMPORT`: pre-opened FD/socket/provider/client/session/capability supplied from outside the audited construction graph.

Capability IDs are semantic and non-reusable. Implementation changes that preserve the exact semantic contract may retain an ID only with an authenticated compatibility proof; broadened effect authority requires a new ID.

### 2. Inventory generations

`EffectCapabilityInventoryV1` is consequential authority metadata and contains at minimum:

- inventory generation and predecessor digest;
- activation frontier / runtime build identity;
- registered capability IDs and classes;
- acquisition mechanism for each capability (constructor injection, plugin import, FFI binding, dynamic loader, provider adapter, inherited descriptor, subprocess broker, etc.);
- enforcement/observation point(s);
- allowed operation families and target namespaces;
- whether effects may be delayed, delegated or transitively amplified;
- runtime/plugin/provider version roots;
- deprecation/revocation state;
- independent observation coverage statement;
- authenticated authority and threshold approving the generation.

Generations are immutable, monotonic and predecessor-linked. Runtime/plugin/provider upgrade that can alter reachable effects either proves semantic compatibility or activates a new generation before the new code can emit consequential effects.

### 3. Registration-before-use

For consequential classes, registration is a gate, not documentation after the fact.

A runtime may only use a capability when:

1. its exact `EffectCapabilityId` is present in the active inventory generation;
2. the active manifest-schema generation has a declaration mapping for the capability or a reviewed `NOT_APPLICABLE` witness for the specific operation kind;
3. the capability is bound to an enforcement/observation path that cannot be bypassed by the producer under the supported threat model;
4. the producer's effect manifest commits to the capability ID and concrete effect instance where required.

Unknown capability use must fail closed or move the operation into an explicitly non-authoritative quarantine mode. `UNKNOWN -> allow + log` is not permitted for operations whose result can later authorize finalization, destructive GC, trust mutation or recovery.

### 4. Independent derivation

The inventory must not merely restate the manifest schema or source-level annotations generated by the same compiler.

For E2/E3/E4-consequential effects, at least two materially distinct derivation domains are required:

- **declared reachability**: registered construction/plugin/provider/FFI capability graph;
- **runtime effect observation/enforcement**: kernel/broker/storage/provider choke point or equivalent independent boundary.

Where a consequential effect is not independently observable at the platform boundary, the capability must be isolated behind a trusted adapter whose implementation identity and authority are themselves registered and whose output is independently reconcilable.

### 5. Dynamic dispatch, plugins and reflection

Dynamic code is represented by an explicit capability envelope.

- Plugin install/enable is itself a consequential inventory mutation when the plugin can gain any material capability.
- The plugin's declared capability set is authenticated and bounded by the host-granted envelope.
- Host code must not grant ambient authority merely because the plugin exports a known interface.
- Reflection/dynamic dispatch may select only among already registered capabilities; constructing a new effect path dynamically requires a new inventory generation or a pre-authorized bounded family whose target namespace is committed in the inventory.
- Generated wrapper code is not an independent checker of the source definition that generated it.

### 6. FFI/native escape hatches

Any managed-to-native boundary capable of arbitrary syscalls, handle import, dynamic loading, raw provider SDK invocation or memory-mediated control of a privileged helper is `C_NATIVE_ESCAPE` unless a narrower audited adapter proves otherwise.

A raw FFI pointer/function name is never sufficient semantic identity. The inventory binds native library digest/version, exported adapter identity, allowed effect classes, target scope and enforcement boundary. Runtime replacement of the native library invalidates the inventory generation unless covered by a compatibility handoff.

### 7. External/provider capabilities

Caller-owned provider/client/session objects are registered as `C_EXTERNAL_HANDLE_IMPORT` plus their derived effect classes. The inventory distinguishes ownership from trust: possession by the caller does not make the object a trusted proof source.

Consequential provider operations require an independently verifiable provider-side state transition, receipt, fence, sequence/epoch or equivalent evidence where the remote effect cannot be observed directly. A subclass or wrapper that can fabricate valid-looking status values without the underlying side effect is not semantically equivalent merely because it implements the same interface.

### 8. Delayed effects

Scheduling a future consequential action is itself a material effect. `C_DELAYED_WORK` manifests must commit to:

- scheduler/domain identity;
- task identity and generation;
- eventual capability class(es) the task may exercise;
- cancellation/retry semantics;
- causality from scheduling effect to later effect;
- lifetime / expiry / recovery semantics.

The later execution must reconcile to the original delayed-work commitment. A task engine or plugin may not hide a later network/storage/authority mutation behind a harmless-looking `schedule()` call.

### 9. Independent reconciliation

Observed effects are reconciled against registered capability and manifest universes.

A consequential observed effect with no valid registered capability instance yields `UNDECLARED_RUNTIME_EFFECT_OBSERVED`. Absence of an observation is **not** proof of absence unless the relevant choke point has a complete enforcement guarantee for that effect class.

Reconciliation coverage therefore has explicit states:

- `ENFORCED_COMPLETE`: every supported effect of the class must cross the bound choke point;
- `OBSERVED_BEST_EFFORT`: useful anomaly evidence only, never completeness proof;
- `NOT_COVERED`: no independent observation; consequential use requires another trusted boundary or is disallowed.

### 10. Inventory omission fraud proof

`InventoryOmittedCapabilityProofV1` may establish `INVENTORY_OMITTED_CAPABILITY_PROVEN` when it binds:

1. authenticated/runtime-verifiable evidence of a consequential effect or an effect-capable acquisition path;
2. the active inventory generation and activation frontier;
3. canonical classification showing the effect belongs to a material capability class;
4. exact non-membership of the required capability ID/family in that inventory generation;
5. provenance tying the effect/acquisition to a producer/runtime/plugin/provider version governed by that inventory generation.

A valid proof:

- stales dependent `SchemaCompletenessProofV1`, effect-manifest completeness, federated-finalization and destructive-GC authority for the affected closure;
- re-roots affected E2/E3/E4 evidence;
- requires additive inventory N+1 plus schema/manifest historical repair;
- never rewrites the old inventory or old effect manifest bytes;
- expands historical repair only to the bounded activation/runtime/plugin/provider frontier for which omission could have mattered, unless the omission's exact start cannot be proven, in which case the safe closure expands to the last independently established complete inventory frontier.

### 11. Rotation, revocation and downgrade

Inventory authority is threshold-authorized and distinct from producer authority.

- Capability removal/downgrade that can make prior effects disappear from completeness obligations is deletion-authorizing and requires stronger review than additive registration.
- Revoking an inventory signer/checker stales generations whose completeness depended solely on that authority domain unless independent attestation remains sufficient.
- Runtime rollback to an older build cannot reactivate an older inventory generation if newer authenticated evidence proved that generation incomplete.
- Capability aliases are authenticated, acyclic and cannot narrow semantic class by aliasing (`C_NATIVE_ESCAPE -> harmless helper`) without a new reviewed adapter proof.

### 12. Relationship to `OperationSemanticInventoryV1`

`OperationSemanticInventoryV1` becomes a projection, not the root of truth. For each operation kind it maps the active effect-capability inventory into required semantic slots.

Completeness chain:

`runtime capability universe -> EffectCapabilityInventoryV1 -> OperationSemanticInventoryV1 -> manifest declaration slots -> producer EffectManifestV1 -> independent observed/reconciled effects`.

A proof at a later layer cannot repair an omission at an earlier layer. Each layer commits to the exact generation/root of the preceding layer.

## Safety invariants

1. No consequential runtime capability may become reachable after the active inventory frontier without authenticated registration or a pre-authorized bounded family.
2. A producer cannot be the sole source of both capability discovery and proof that no undeclared capabilities exist.
3. Observability is not authority unless coverage is mechanically complete for the relevant effect class.
4. Plugin/interface conformance does not imply semantic side-effect conformance.
5. FFI/native/dynamic-loading paths are explicit capabilities, never invisible implementation details.
6. Scheduling a consequential future action is itself consequential.
7. External handles are classified by what they can do, not by who supplied them.
8. Inventory/schema downgrades cannot retroactively erase prior obligations.
9. Late omission discovery stales dependent destructive/finalization proofs and triggers additive bounded repair.
10. Unknown or unclassified consequential paths fail closed for authoritative operations.

## RED-first matrix — 80 cases

### A. Registration and authority (1-10)
1. registered storage capability accepted;
2. unregistered storage writer rejected before write;
3. unregistered network mutator rejected before send;
4. additive capability generation succeeds with threshold authorization;
5. unauthorized inventory generation rejected;
6. rollback to older inventory rejected;
7. predecessor mismatch rejected;
8. reused semantic capability ID with broadened authority rejected;
9. capability removal without downgrade proof rejected;
10. revoked inventory authority invalidates dependent completion.

### B. Plugins and dynamic dispatch (11-20)
11. plugin with declared bounded storage capability accepted;
12. plugin gains undeclared broker client -> fail/omission proof;
13. plugin update broadens effects without new generation -> reject;
14. dynamic dispatch among registered implementations accepted;
15. reflection constructs unregistered provider client -> reject;
16. alias cycle rejected;
17. alias narrows native escape to harmless class -> reject;
18. generated wrapper drift discovered by independent checker;
19. plugin disabled while delayed effects remain -> obligations retained;
20. concurrent plugin activation/inventory rotation cannot create gap.

### C. FFI/native/process escape (21-30)
21. audited narrow native adapter accepted;
22. raw arbitrary FFI marked `C_NATIVE_ESCAPE`;
23. swapped native library digest invalidates generation;
24. subprocess with no consequential capability accepted only in bounded sandbox;
25. subprocess inherits writable FD -> external-handle capability required;
26. subprocess opens network socket outside declared envelope -> reject/observe;
27. pre-opened FD write is not missed by path-only inventory;
28. ptrace/debug escape invalidates seccomp-only completeness assumption;
29. architecture/syscall-number ambiguity cannot prove semantic class;
30. JIT-generated native call path requires registered envelope.

### D. Provider/external handles (31-40)
31. exact trusted provider adapter accepted;
32. caller-owned mutable provider registered but not trusted as sole evidence;
33. provider subclass fabricates success without remote state -> independent verifier catches;
34. provider SDK update broadens mutating methods -> new generation required;
35. imported socket/session classified despite construction outside runtime;
36. external handle rebind after construction invalidates capability binding;
37. stale provider epoch rejected;
38. provider side effect with missing local manifest creates omission/fraud evidence;
39. remote effect not independently observable requires trusted receipt/fence boundary;
40. best-effort telemetry alone cannot authorize destructive finalization.

### E. Delayed and delegated effects (41-50)
41. registered delayed job with exact eventual capabilities accepted;
42. schedule call omits eventual storage write -> reject;
43. retry duplicates effect but same causal task ID reconciles correctly;
44. delayed task survives plugin upgrade and retains original obligation;
45. cancellation proof closes future obligation;
46. unknown cancellation outcome keeps obligation open;
47. delegated child task must inherit/bind capability envelope;
48. task dynamically loads undeclared plugin -> reject;
49. scheduler migration preserves task/effect identity;
50. GC cannot remove evidence while delayed consequential task remains live.

### F. Observation and reconciliation (51-60)
51. complete storage choke point observes every supported write;
52. best-effort trace gap cannot be interpreted as no effect;
53. broker send observed without registered capability -> omission proof;
54. network effect observed under wrong capability ID -> fail;
55. batch operation reconciles each material target/semantic effect;
56. producer trace missing but broker/platform observation exists -> fraud evidence;
57. producer and instrumentation share same bug; kernel/provider boundary still detects effect;
58. observer outage marks coverage UNKNOWN, blocks completion;
59. observer recovery with durable cursor closes gap exactly once;
60. conflicting observers cause disagreement/quarantine, not latest-wins.

### G. Schema/inventory composition and historical repair (61-70)
61. operation inventory projects all active material capabilities;
62. schema has slots for all projected material capabilities;
63. inventory omission makes existing schema-completeness proof stale;
64. inventory N+1 additive repair restores bounded closure;
65. old inventory bytes remain immutable;
66. historical operation under prior complete inventory remains valid when unaffected;
67. omission start frontier known -> bounded repair only;
68. omission start unknown -> expand to last independently complete frontier;
69. inventory downgrade cannot erase historical declaration obligations;
70. runtime rollback cannot reactivate generation already proven incomplete.

### H. Concurrency, crash and recovery (71-80)
71. capability registration committed before plugin enable;
72. crash after registration/before enable leaves no undeclared effect path;
73. crash after enable/before inventory activation is impossible/fail-closed;
74. concurrent inventory readers pin exact generation;
75. effect initiated under generation N completes with N-bound manifest after N+1 activation;
76. revocation during in-flight effect marks result for revalidation;
77. restart reconstructs active inventory frontier before enabling producers;
78. missing inventory state on previously initialized runtime fails closed, not fresh-bootstrap;
79. disaster recovery cannot restore plugin/provider without corresponding inventory generation;
80. final GC/federated completion requires no unresolved inventory omission, observation gap or repair obligation.

## Decisions

- `OperationSemanticInventoryV1` is no longer treated as an independent root-of-truth artifact. It is a deterministic/reviewed projection of an authenticated `EffectCapabilityInventoryV1` plus operation semantics.
- Consequential capability completeness requires registration-before-use and an effect boundary that is either enforcing-complete or paired with a trusted independently verifiable adapter.
- Observability-only signals remain anomaly/fraud evidence unless coverage is mechanically complete.
- Plugins, FFI/native paths, delayed work, subprocesses and externally imported handles are first-class semantic capabilities.
- Late observed undeclared capability yields `INVENTORY_OMITTED_CAPABILITY_PROVEN`, stales dependent schema/finalization/GC proofs and triggers additive bounded historical repair.

## Next distinct evidence question

Freeze **capability-envelope transitive delegation / pre-opened-handle provenance / ambient-authority elimination semantics**: define how a registered capability may be safely delegated across process/plugin/task boundaries without becoming broader ambient authority; how pre-opened descriptors/sessions inherit provenance and epoch; how capability attenuation is proven; how revocation propagates to descendants; and how an independently observed effect can be attributed to the exact delegated ancestor rather than merely to the final process. Cover descriptor passing, fork/exec inheritance, broker credentials, provider sessions, task queues, capability attenuation, revocation races and orphaned descendants.
