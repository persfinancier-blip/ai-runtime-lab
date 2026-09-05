# Authority dependency manifest / policy compiler + completeness verifier V1

Status: `AUTHORITY_DEPENDENCY_MANIFEST_POLICY_COMPILER_COMPLETENESS_VERIFIER_V1_FROZEN`

Date: 2026-09-05

Scope: design contract only; no production behavioral PASS is claimed.

## Objective

Define how every consequential `SEND`, `MUTATE`, `RESUME`, `TOKEN_MINT`, `ACTIVATE`, `ROTATE`, `RELEASE`, and externally consequential adapter surface is declared, compiled into an authenticated authority-dependency manifest, bound to an exact build/runtime/configuration, and checked both statically and at runtime so that omissions, plugins, reflection, dynamic dispatch, adapter drift, or stale manifests fail closed instead of silently shrinking quarantine blast radius or bypassing the effective-authority gate.

This contract extends `CHALLENGE_BLAST_RADIUS_QUARANTINE_EFFECT_CLASS_READMISSION_V1_FROZEN` and composes with the LAB-093 least-capability façade/session/request/effect registry, provider-capability evidence, UNKNOWN-oracle, manual-reconciliation, challenge, quarantine/re-admission, and LAB-097..100 global provenance line.

## Core security decision

**A dependency graph is authoritative only when the runtime can prove both that every admitted consequential surface is represented by the manifest and that every consequential invocation is dominated by the current effective-authority gate. A missing or unverifiable edge removes authority; it never grants it.**

The manifest is not merely documentation and not a hand-maintained allowlist. It is a build-bound, canonical, authenticated compilation result whose completeness is checked against independent static and runtime evidence.

## Non-negotiable invariants

1. **Default-deny consequential surfaces.** A provider/plugin/adapter operation cannot obtain SEND/MUTATE/RESUME/TOKEN_MINT authority unless its exact surface identity is present in the current verified manifest.
2. **Exact build binding.** A manifest is valid only for the exact code/build subject, compiler policy generation, adapter/config inputs, and plugin set it names.
3. **No self-asserted completeness.** A manifest cannot prove its own completeness merely by setting `complete=true`; completeness is an output of independent verifier checks.
4. **Two-sided discovery.** Static discovery and runtime registration are compared. Either side finding a consequential surface absent from the other is fail-closed evidence.
5. **Gate domination.** Every consequential provider I/O path must consume a current `EffectiveAuthorityLeaseV1` minted by the authoritative broker/ledger gate immediately before the effect-capable call.
6. **Dynamic behavior is explicit authority.** Reflection, `importlib`, entry-point plugins, subclass dispatch, monkeypatch/rebinding, generated adapters, FFI/native bridges, subprocess helpers, and runtime-loaded config cannot silently create new effect-capable surfaces.
7. **Unknown expands quarantine.** If the verifier cannot determine whether a new or changed surface depends on challenged authority, it joins the affected quarantine closure.
8. **Manifest rollback cannot restore authority.** Older valid manifests remain historical evidence but cannot become current by deleting or restoring newer state.
9. **Runtime registration is not authority by itself.** A plugin may register what it wants to do; registration does not grant admission unless it matches the authenticated manifest and all current policy gates.
10. **Historical operation identities remain pinned.** Manifest evolution never changes the capability/provider/request identities already bound to an in-flight or historical operation.
11. **Read-only and consequential capabilities are distinct.** A missing SEND dependency may still leave independently verified read-only reconciliation available.
12. **No emergency bypass.** Break-glass/re-root/quarantine administration cannot disable manifest completeness checks for consequential effects. Recovery may replace authority through its own authenticated lifecycle, not bypass this one.

## Donor mechanisms and rationale

### SLSA provenance — build and dependency binding

SLSA provenance is a donor for binding an artifact to the process and resolved dependencies that produced it. SLSA v1.2 describes provenance as verifiable information about where, when, and how software artifacts were produced and its build provenance model binds outputs to build definition/run details and resolved dependencies.

Adopted mechanism: the authority manifest names an exact build subject digest, compiler identity/version, source/config/plugin inputs, and resolved adapter dependencies. A manifest generated for another build is not admissible.

Primary source: https://slsa.dev/spec/v1.2/provenance

### Open Policy Agent signed bundles — authenticated policy activation

OPA signed bundles are a donor for authenticated policy payload activation: a bundle may carry signed hashes of the files it contains, and activation occurs only after signature/file-set/hash verification. OPA discovery also separates bootstrap verification keys from data learned through discovery.

Adopted mechanism: compiler output is canonicalized and authenticated; startup verifies exact payload membership/digests before activating it. Verification trust is bootstrapped outside the mutable manifest itself.

Primary sources:
- https://www.openpolicyagent.org/docs/management-bundles
- https://www.openpolicyagent.org/docs/management-discovery

### Existing LAB global provenance contracts

LAB-097..100 already freeze one parent-linked global provenance chain, expected-head CAS, rollback-resistant startup, durable SQL storage, external evidence continuity, recovery executor, and finite startup state machine.

Adopted mechanism: manifest generations are entries in that same chain. No independent locally valid policy island is introduced.

## Canonical objects

All objects use the shared canonical V1 JSON/digest rules already frozen by the LAB-097..100 line.

### `AuthoritySurfaceDeclarationV1`

One declaration per effect-capable operation.

Required fields:

- `surface_id`
- `surface_kind`: `SEND | MUTATE | RESUME | TOKEN_MINT | ACTIVATE | ROTATE | RELEASE | ABORT | DELETE | EXTERNAL_WRITE | OTHER_CONSEQUENTIAL`
- `component_id`
- `module_path`
- `qualified_symbol`
- `source_blob_digest`
- `build_subject_digest`
- `adapter_id` and adapter implementation digest
- provider/service/API/operation/account/region/scope selectors where applicable
- effect class
- trust epoch / effect namespace constraints where applicable
- required dependency object IDs / dependency kinds
- required authoritative gate ID
- required lease capability set
- runtime-registration key
- dynamic-load mode (`STATIC`, `REGISTERED_PLUGIN`, `GENERATED`, `FFI_BRIDGE`, `SUBPROCESS_BRIDGE`)
- exact configuration fields capable of altering endpoint/operation/scope/side-effect semantics
- declaration digest

A declaration is immutable within one manifest generation.

### `AuthorityDependencyManifestV1`

Required fields:

- `manifest_version`
- monotonically increasing `manifest_generation`
- parent manifest digest
- global provenance parent
- exact build subject digest(s)
- source revision when available
- compiler implementation digest/version
- compiler policy digest/version
- source inventory digest
- config/schema digest
- plugin/adapter inventory digest
- complete ordered set of `AuthoritySurfaceDeclarationV1` digests
- complete ordered set of typed dependency-edge digests
- allowed dynamic loaders/plugin namespaces
- required runtime-registration set
- explicitly non-consequential/read-only surface set
- verification policy ID
- signer/attestation references

There is deliberately no trusted `is_complete` boolean.

### `RuntimeAuthorityRegistrationV1`

Produced by an actually loaded component before it may handle effect-capable work.

Fields include:

- process/runtime instance ID
- exact build subject digest
- manifest digest expected by the process
- component/adapter/plugin implementation digest
- runtime-registration key
- declared surface IDs
- provider/API/operation selectors resolved after configuration
- effective endpoint/account/region/scope
- configuration digest
- dynamic loader/plugin provenance
- registration timestamp/nonce
- local attestation/authentication reference where configured

Registration is descriptive until matched by the startup verifier.

### `EffectiveAuthorityLeaseV1`

Short-lived/operation-scoped capability minted only by the authoritative gate.

Required bindings:

- manifest generation/digest
- effective-authority/quarantine generation
- trust epoch/effect namespace
- exact surface ID
- exact request/effect identity
- provider/service/API/operation/account/region/scope
- allowed capability verb(s)
- current provider-capability generation
- current challenge/re-admission state
- expiry/use bound
- nonce / one-shot or monotonic use counter as required
- broker/ledger authentication

A provider adapter MUST reject consequential methods without a valid lease or when any exact binding differs.

### `CompletenessVerificationReportV1`

Machine-produced report; never hand-authored authority.

Required sections:

- manifest authenticity/build-binding result
- static discovery result
- runtime-registration result
- static-vs-manifest set difference
- runtime-vs-manifest set difference
- manifest-vs-runtime missing-registration set
- gate-domination result
- config/adapter/plugin drift result
- unresolved dynamic-dispatch findings
- quarantine impact result
- final verdict: `VERIFIED | FAIL_CLOSED | READ_ONLY_ONLY`
- verifier implementation/policy digest
- global provenance append reference

## Policy compiler pipeline

### Phase 1 — source inventory

The compiler inventories source modules and known effect adapters from the exact build inputs.

It identifies candidate consequential sinks including:

- network/client calls capable of create/update/delete/send/commit/release/resume;
- provider SDK methods classified as mutating;
- adapter methods named/declared as consequential by provider capability schemas;
- token/request-ID minting that grants new external effect attempts;
- subprocess/CLI invocation that can mutate external state;
- FFI/native bridge entry points capable of external effects;
- durable local mutation that changes activation/send authority.

Static discovery is deliberately conservative. Ambiguous sinks are consequential until explicitly classified with evidence.

### Phase 2 — explicit declarations and dependency compilation

Each candidate sink must map to exactly one declared surface and to all authority dependencies needed to admit it.

Dependency kinds include at minimum:

- `AUTHENTICATION`
- `EFFECT_CLASS`
- `IDEMPOTENCY`
- `OUTCOME_ORACLE`
- `PROVIDER_FENCE`
- `ACTIVATION`
- `GLOBAL_PROVENANCE`
- `TRUST_EPOCH`
- `EFFECT_NAMESPACE`
- `CHALLENGE_STATUS`
- `QUARANTINE_GENERATION`
- `READMISSION_GENERATION`
- `PROVIDER_CAPABILITY`
- `MANUAL_RECONCILIATION`
- `OWNER_AUTHORIZATION` where required

An edge that cannot be resolved is not omitted; it becomes an unresolved dependency that blocks admission for the affected surface.

### Phase 3 — configuration and plugin expansion

The compiler expands all known configuration that can affect authority semantics:

- endpoint/provider/account/region/scope selection;
- API version and operation mapping;
- adapter implementation selection;
- plugin entry points;
- feature flags that expose a mutation path;
- retry/resume strategy;
- provider token construction;
- dynamic loader allowlists.

Wildcard configuration is allowed only where the verifier can prove a safe closed set. Otherwise it compiles to fail-closed or read-only-only.

### Phase 4 — canonical output and authentication

The compiler emits a deterministic manifest, records compiler/build/input digests, and submits it to the shared authenticated provenance/authorization path.

The manifest becomes eligible for startup only after:

- canonical digest verification;
- authorized signature/attestation verification;
- global parent/head validation;
- expected-head CAS append;
- independent verifier success.

Compiler output alone is not activation authority.

## Static completeness verifier

Python and plugin-rich runtimes cannot rely on a perfect static call graph. Therefore static analysis is one independent sensor, not a sole proof.

The static verifier MUST:

1. enumerate known effect sinks and compare them with manifest declarations;
2. flag direct provider SDK/network calls outside approved adapter modules;
3. flag consequential adapter methods callable without the lease-bearing interface;
4. inspect dynamic loader sites (`importlib`, entry points, reflection factories, subprocess/FFI bridges) and require an explicit manifest policy;
5. flag public/rebindable strategy/provider slots that can swap an audited implementation after construction;
6. detect configuration paths that can change endpoint/operation/effect semantics without changing the manifest-bound configuration digest;
7. emit unresolved findings rather than silently dropping analysis it cannot model.

Any unresolved consequential finding results in `FAIL_CLOSED` for the affected scope, or `READ_ONLY_ONLY` if the verifier can prove the unresolved path cannot mutate.

## Runtime completeness verifier

Static coverage is insufficient for dynamic dispatch and loaded plugins. Before a runtime can accept consequential work:

1. every loaded provider/adapter/plugin registers its exact effect-capable surfaces;
2. registration is bound to exact build/plugin/config digests;
3. the verifier requires runtime registrations to be a subset of the authenticated manifest;
4. every manifest surface configured as active must have exactly the expected registration unless the manifest explicitly marks it disabled;
5. duplicate/conflicting registrations fail closed;
6. unregistered dynamic plugins may load only into a no-consequential-authority sandbox/read-only mode;
7. drift in account/region/API/endpoint/adapter/config identity invalidates admission;
8. the runtime publishes one verified `EffectiveAuthoritySnapshotV1` only after all checks succeed.

### Set-equality rule

For the active configuration:

`manifest_required_surfaces == runtime_registered_consequential_surfaces == verifier_resolved_consequential_surfaces`

subject only to explicitly declared disabled/read-only surfaces.

A mismatch never causes the runtime to infer a missing surface automatically.

## Gate-domination contract

Manifest completeness is useful only if declarations cannot be bypassed.

### Required architecture

- All supported consequential provider adapters accept an `EffectiveAuthorityLeaseV1` on their effect-capable methods.
- Lease verification occurs in the adapter/broker boundary immediately before external I/O, not merely in a distant caller.
- Direct provider client handles capable of mutation are private to the adapter boundary and are not exposed through the supported façade.
- A stale worker request carrying an older manifest/quarantine generation fails at the authoritative gate even if the worker has not received revocation propagation.
- Token minting and resume are treated as consequential when they can create/recreate effect authority.

### Static domination proof obligation

For each surface the verifier must demonstrate either:

1. all supported call paths terminate at an adapter method that requires/validates the lease; or
2. the surface is independently proven read-only/non-consequential.

A raw SDK/network/FFI/subprocess escape path invalidates domination for the affected class.

### Runtime domination proof obligation

Before every consequential I/O the adapter verifies:

- lease authenticity;
- current manifest generation;
- current effective-authority/quarantine generation;
- exact surface ID;
- exact operation/request/effect identity;
- exact provider/account/region/scope/API binding;
- current provider-capability generation;
- lease expiry/use state.

The adapter must not accept a generic `authorized=true` bit or a bearer token lacking those bindings.

## Dynamic dispatch / plugin / reflection policy

### Plugins

A plugin that can mutate external state is admitted only when its implementation digest, declared surfaces, configuration schema, provider semantics, and registration keys are present in the current manifest.

Unknown plugin version => no consequential authority.

### Reflection / monkeypatch / rebinding

Supported objects holding authority-critical adapters/strategies are construction-bound. Rebinding the strategy/provider implementation after verification invalidates the runtime snapshot and removes consequential authority until a new manifest/runtime verification succeeds.

### Generated code

Generated adapters are valid only when the generated output digest is part of the exact build subject or resolved dependency set and the compiler inventories the generated consequential surfaces.

### FFI/native bridges

FFI/native calls that can create external effects are explicit surfaces. If the verifier cannot inspect the implementation sufficiently, admission depends on a narrowly declared adapter wrapper whose lease enforcement can be verified at the language boundary; otherwise the scope remains blocked.

### Subprocess/CLI bridges

Any subprocess that can mutate a provider is a consequential surface. Command path, implementation/version digest where available, exact argument template and environment/config inputs that choose effect semantics are manifest-bound.

## Manifest evolution

A code/config/plugin change that can affect consequential authority requires a new manifest generation.

### Safe additive evolution

A new read-only surface may be added without expanding SEND authority if it is independently verified read-only.

A new consequential surface remains blocked until its fresh manifest generation is authenticated, statically verified, runtime-registered, and admitted through current challenge/quarantine/provider-capability gates.

### Removal

Removing a surface from a newer manifest subtracts authority. Historical operation records remain bound to the old surface ID/manifest generation for audit/reconciliation.

### Dependency change

Changing dependencies for an existing surface creates a new declaration digest and manifest generation. Existing in-flight operations do not migrate automatically to the new dependency graph.

## Composition with quarantine / re-admission

The quarantine engine may use the manifest dependency graph only if the manifest is currently verified.

If manifest completeness becomes suspect:

- affected consequential classes are quarantined;
- unknown edges widen, never narrow, blast radius;
- read-only reconciliation may continue only where its own manifest/dependencies remain independently verified;
- re-admission requires a fresh verified manifest generation before provider/effect authority can return.

A stale/incomplete manifest can never be used to argue that a challenged capability has a small blast radius.

## Startup state machine

Recommended finite startup states:

`LOAD_BOOTSTRAP_TRUST`
→ `VERIFY_GLOBAL_PROVENANCE`
→ `VERIFY_BUILD_SUBJECT`
→ `VERIFY_MANIFEST_AUTHENTICITY`
→ `RUN_STATIC_COMPLETENESS_CHECK`
→ `LOAD_COMPONENTS_READ_ONLY`
→ `COLLECT_RUNTIME_REGISTRATIONS`
→ `VERIFY_SET_EQUALITY`
→ `VERIFY_GATE_DOMINATION`
→ `VERIFY_CHALLENGE_QUARANTINE_PROVIDER_STATE`
→ `PUBLISH_EFFECTIVE_AUTHORITY_SNAPSHOT`
→ `ADMIT_CONSEQUENTIAL_WORK`

Any failure before the final state yields `FAIL_CLOSED` or a deliberately proven `READ_ONLY_ONLY` mode.

Startup MUST NOT auto-repair a missing declaration, auto-import a new plugin, or regenerate/activate a manifest from the running mutable environment.

## Crash / rollback / concurrency

### Crash during manifest generation

Staged compiler output has no authority. Restart uses only the last authenticated/verified manifest generation.

### Crash after provenance append but before activation

The new manifest exists durably but SEND remains blocked until startup/runtime completeness verification finishes against the exact build/config/plugin set.

### Rollback to old manifest

If global provenance says a newer manifest generation exists, an older locally valid manifest is stale and cannot restore authority.

### Plugin appears after startup

The plugin may not gain consequential authority dynamically. It is rejected or constrained to read-only/no-effect mode until a new authenticated manifest generation and startup/re-admission cycle covers it.

### Config changes after startup

Any authority-relevant config digest mismatch invalidates the current snapshot before the next consequential I/O. The authoritative gate/adapter recheck blocks stale leases.

### Challenge races a send

The adapter-side lease check compares the current quarantine/effective-authority generation immediately before provider I/O; an older lease fails.

## Verifier independence and authority separation

Automation MAY:

- run compiler/static/runtime inventory;
- generate candidate manifests;
- compute dependency graphs;
- detect mismatches/drift;
- subtract authority/quarantine on failed completeness;
- run safe read-only verification;
- assemble re-admission evidence.

Automation MUST NOT:

- mark unresolved dynamic behavior as safe merely to achieve startup;
- activate a manifest whose build/config/plugin identity differs from the running subject;
- lower owner/security quorum to re-admit a consequential class;
- mint a bypass lease outside the authoritative gate;
- treat a manually edited manifest as proof of completeness;
- reactivate historical/stale manifests after rollback.

## RED-first regression matrix (72 minimum)

### Canonical identity / build binding (10)
1. exact build + exact manifest verifies;
2. one source blob changes with same manifest -> fail closed;
3. adapter implementation digest changes -> fail closed;
4. compiler policy digest changes without new manifest -> fail closed;
5. config digest changes endpoint -> fail closed;
6. API version changes operation semantics -> fail closed;
7. plugin digest changes -> fail closed;
8. stale manifest generation with valid signature -> rejected by global head;
9. malformed/duplicate canonical fields -> rejected;
10. manifest signed by unauthorized key -> rejected.

### Static discovery completeness (12)
11. declared mutating SDK sink -> verified;
12. undeclared direct SDK mutation call -> fail closed;
13. undeclared raw HTTP POST/DELETE provider path -> fail closed;
14. subprocess mutation path absent from manifest -> fail closed;
15. FFI mutation bridge absent -> fail closed;
16. ambiguous SDK method -> consequential until classified;
17. proven GET/describe path remains read-only;
18. token mint capable of new attempt classified consequential;
19. resume endpoint capable of effect classified consequential;
20. dynamic import site with no loader policy -> affected scope blocked;
21. provider strategy public rebinding path invalidates domination;
22. unresolved static analysis finding cannot be suppressed by `complete=true`.

### Runtime registration / set equality (12)
23. exact expected registrations -> verified;
24. runtime registers extra consequential surface -> blocked;
25. manifest requires active surface but registration missing -> blocked;
26. duplicate conflicting registration -> blocked;
27. registration uses different account -> blocked;
28. registration uses different region -> blocked;
29. registration uses different API/operation -> blocked;
30. registration uses different adapter digest -> blocked;
31. unknown plugin loads -> read-only/no-effect only;
32. dynamic plugin appears after startup -> cannot gain SEND;
33. generated adapter digest differs -> blocked;
34. runtime registration cannot self-grant by claiming read-only while static sink is mutating.

### Gate domination / lease enforcement (14)
35. correct current lease at exact adapter surface -> allowed;
36. no lease -> consequential adapter rejects;
37. stale manifest-generation lease -> rejects;
38. stale quarantine-generation lease -> rejects;
39. lease for different surface -> rejects;
40. lease for different request/effect identity -> rejects;
41. lease for different account/region/scope -> rejects;
42. lease for different provider-capability generation -> rejects;
43. expired lease -> rejects;
44. one-shot lease replay -> rejects;
45. raw client escape path discovered -> affected class blocked;
46. worker with stale local config cannot override broker/adapter recheck;
47. generic bearer `authorized=true` credential insufficient;
48. token-mint helper cannot execute without its own exact authority surface/lease.

### Quarantine / manifest composition (10)
49. challenged dependency maps through verified manifest to minimal safe class;
50. incomplete manifest prevents narrow blast-radius claim and widens quarantine;
51. unrelated independently verified class remains admitted;
52. read-only oracle remains available when outside challenged closure;
53. challenged oracle removes read-only automation but does not create resend;
54. stale manifest cannot exclude newly discovered dependency;
55. fresh manifest adds missing dependency and requires re-admission;
56. historical UNKNOWN remains pinned to old manifest generation;
57. historical consumed provider token never resets on manifest upgrade;
58. trust-epoch discontinuity still requires namespace/owner gates.

### Evolution / plugins / drift (8)
59. new consequential plugin declared but not yet admitted -> SEND blocked;
60. new read-only plugin with proof may be read-only admitted;
61. authority-relevant config hot reload invalidates snapshot;
62. harmless telemetry-only config change does not invent SEND delta;
63. reflection factory resolves unexpected mutating implementation -> blocked;
64. monkeypatch/rebinding after startup invalidates snapshot;
65. removed surface cannot be called using older lease;
66. in-flight operation remains auditable under historical surface ID.

### Crash / rollback / startup (6)
67. crash before authenticated manifest append -> no new authority;
68. crash after append before runtime verification -> no SEND on restart;
69. delete latest manifest row -> global provenance prevents old authority resurrection;
70. restore stale DB snapshot -> fail closed against global head;
71. runtime registration race before snapshot publication -> no effect authority;
72. restart derives same effective authority from durable inputs without auto-repair.

## Acceptance gate for future implementation

Do not claim implementation complete until all of the following are executed on exact repository source:

1. RED tests demonstrate undeclared static sink, unexpected runtime registration, stale manifest, stale lease, raw client escape, plugin drift, and quarantine-completeness failure;
2. compiler emits deterministic canonical manifests for exact test builds;
3. verifier binds manifest to exact build/config/plugin inputs;
4. static and runtime set-difference checks execute;
5. consequential adapter paths require current leases immediately before effect-capable I/O;
6. rollback/crash/startup tests execute against durable provenance storage;
7. LAB-093 façade/provider capability/UNKNOWN/quarantine tests compose without bypass;
8. LAB-097..100 global provenance/startup/recovery gates pass;
9. security audit finds no supported consequential surface outside the manifest+lease boundary.

## Decision

Freeze this V1 contract for the next LAB-093 implementation slice:

> An authority dependency graph is usable for quarantine and effect admission only when an authenticated compiler binds it to the exact build/config/plugin subject, independent static and runtime discovery agree on the consequential surface set, and every effect-capable invocation is enforced by an adapter-side current-generation authority lease. Unknown or undeclared behavior subtracts authority; it never creates an implicit dependency omission or bypass.

No production code or behavioral PASS is claimed by this research artifact.
