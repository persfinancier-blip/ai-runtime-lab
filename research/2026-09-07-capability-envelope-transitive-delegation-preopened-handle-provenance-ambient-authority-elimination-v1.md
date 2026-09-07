# Capability-envelope transitive delegation / pre-opened-handle provenance / ambient-authority elimination v1

Date: 2026-09-07
Status: `CAPABILITY_ENVELOPE_TRANSITIVE_DELEGATION_PREOPENED_HANDLE_PROVENANCE_AMBIENT_AUTHORITY_ELIMINATION_V1_FROZEN`
Parent: LAB-093 / #178

## Question

Given the frozen `EffectCapabilityInventoryV1` registration-before-use model, how may a consequential capability cross process, plugin, task, broker, provider-session, or file-descriptor boundaries without silently broadening authority or severing provenance?

The prior contract proves that a consequential capability must be registered and bound to a real enforcement/observation choke point. That is insufficient once an already-authorized handle is delegated. A child can inherit, duplicate, receive, queue, or recover a capability whose existence is legitimate while its descendant lineage, epoch, attenuation, or revocation state is no longer attributable to the original authority decision.

## Primary-source donor mechanisms

Observed 2026-09-07.

1. Linux `SCM_RIGHTS`: a UNIX-domain-socket transfer passes a reference to an open file description; semantically it behaves like duplicating a descriptor into another process. The receiving descriptor number is not the identity of the authority. This is the key negative boundary for provenance: FD integers cannot serve as capability identities.
   - https://man7.org/linux/man-pages/man7/unix.7.html
2. Linux `open(2)`: an `O_PATH` descriptor can itself be passed via `SCM_RIGHTS` and then used as authority for `*at()` operations. Possession of a pre-opened object can therefore carry useful authority independently of ambient namespace permission.
   - https://man7.org/linux/man-pages/man2/open.2.html
3. Linux Landlock: inherited restrictions compose across descendants, but some restrictions do not retroactively cover pre-existing descriptors (the kernel documentation explicitly calls out pre-opened TTY descriptors for IOCTL restrictions). Sandbox state alone therefore cannot prove the authority of inherited handles.
   - https://www.kernel.org/doc/html/latest/userspace-api/landlock.html
4. FreeBSD Capsicum: capability mode removes ambient global namespace access and relies on explicitly delegated descriptor rights; `cap_rights_limit()` can reduce but never expand rights. This is a strong donor for monotonic attenuation.
   - https://man.freebsd.org/cgi/man.cgi?query=capsicum&sektion=4
   - https://man.freebsd.org/cgi/man.cgi?query=cap_rights_limit&sektion=2
5. Fuchsia Zircon handles: rights are attached to handles, and duplicate/replace operations can reduce rights; transfer and duplicate are themselves explicit rights. Fuchsia also documents that for duplicable handles, possession alone does not reveal all other extant handles without trusted history back to creation/transfer. This directly motivates lineage tracking and revocation limits.
   - https://fuchsia.dev/fuchsia-src/concepts/kernel/rights
   - https://fuchsia.dev/fuchsia-src/contribute/governance/rfcs/0240_async_ops_are_on_objects
6. Linux socket filter locking: a privileged process can prepare a filtered socket, lock the filter, then pass the descriptor to a less-privileged process. This demonstrates a useful pattern: delegation may transfer already-constrained object authority rather than ambient privilege.
   - https://man7.org/linux/man-pages/man7/socket.7.html

## Frozen threat model

A consequential authority may enter a component through any of these paths:

- inherited FD/handle across `fork` or `exec`;
- explicit descriptor/handle transfer (`SCM_RIGHTS`, IPC channel transfer, broker handoff);
- pre-opened directory/socket/device/session supplied at startup;
- plugin host object or FFI pointer containing an authority-bearing resource;
- broker/provider credentials or a live authenticated provider session;
- queued task containing a token/session/handle captured earlier;
- duplicated handle or derived child capability;
- restart/recovery reconstruction of a previously delegated capability.

The system MUST distinguish **possession** from **authorized consequential use**. A process may physically possess an OS handle while policy denies its use for a current operation/epoch.

## `CapabilityEnvelopeV1`

Every consequential capability admitted to the supported runtime has an authenticated envelope with at least:

- `capability_id`: stable non-reusable semantic identity from `EffectCapabilityInventoryV1`;
- `instance_id`: identity of this concrete authority-bearing object/session/handle generation;
- `ancestor_envelope_digest`: exact parent delegation, or authenticated root issuance;
- `delegation_id`: unique handoff identity;
- `issuer_identity` and `issuer_epoch`;
- `recipient_identity` and `recipient_epoch`;
- `capability_class`;
- `object_binding`: content/object/session identity independent of local FD number or pointer value;
- `rights_scope`: explicit allowed operations;
- `resource_scope`: namespace/provider/account/queue/path/object constraints;
- `temporal_scope`: not-before / expiry / lease or activation epoch as applicable;
- `delegation_rights`: whether re-delegation/duplication is permitted;
- `max_descendant_depth` or equivalent bounded re-delegation policy when required;
- `revocation_domain` and `revocation_generation`;
- `causal_parent`: operation/task/effect manifest that justified the delegation;
- `schema_generation`, `inventory_generation`, and policy/trust frontiers;
- `handoff_mechanism`: inherit/fork, exec, SCM_RIGHTS, plugin, task queue, provider session, broker token, recovery, other registered adapter;
- `enforcement_binding`: kernel/broker/runtime choke point that prevents authority beyond the envelope where such enforcement exists;
- authenticated issuer statement over the complete envelope.

Local resource names (`fd=7`, pointer address, socket number, task object address) are observations, not authority identities.

## Core invariants

### D1 — Explicit handoff

No consequential cross-boundary possession is treated as authorized delegation without a corresponding envelope or a registered root-issuance rule. Undeclared inherited/pre-opened handles are `POSSESSED_UNATTRIBUTED`, not valid authority.

### D2 — Monotonic attenuation

For descendant `C -> C'`:

`rights(C') ⊆ rights(C)`

`resource_scope(C') ⊆ resource_scope(C)`

`temporal_scope(C') ⊆ temporal_scope(C)`

`delegation_rights(C') <= delegation_rights(C)`

and descendant policy/trust frontiers may become stricter but may not silently roll back.

A descendant can never regain a right removed by an ancestor. This follows the Capsicum/Fuchsia donor model but is generalized across non-FD capabilities.

### D3 — Authority identity is object/session lineage, not handle number

`dup`, `fork`, `SCM_RIGHTS`, plugin wrapping, or deserialization may create a new local reference while preserving or deriving authority from the same underlying object/session. The lineage must therefore bind an independently meaningful object/session identity plus delegation ancestry.

### D4 — Fork/exec is a delegation event

Inherited authority after `fork`/`exec` is not considered ambient continuation. Supported launch code must produce a child manifest enumerating consequential inherited handles/sessions and the child envelope derivations. Unexpected inherited handles fail closed or are closed before lower-trust code runs.

`FD_CLOEXEC`/close-on-exec is hygiene, not proof of completeness: the contract still requires an explicit expected inheritance set.

### D5 — `SCM_RIGHTS`/handle transfer is atomic with delegation evidence

A receiving process may use a transferred consequential handle only after matching it to an authenticated handoff envelope. The envelope binds sender/recipient epochs and object identity; the receiver rejects unmatched extra handles, stale envelopes, duplicate replay, or object-binding mismatch.

### D6 — Pre-opened handles need provenance

A sandbox established after descriptors already exist cannot by itself prove their permitted semantics. Every consequential pre-opened descriptor/session must have a root envelope minted by the trusted launcher/broker before restricted execution begins. Unknown pre-opened handles are closed/quarantined or cause fail-closed startup according to capability class.

### D7 — Ambient credentials are not delegated capability

Environment variables, default credential chains, implicit home-directory config, agent sockets, inherited cloud metadata access, default provider sessions, or process-wide keyrings MUST NOT silently satisfy a consequential capability requirement.

Supported consequential code receives an explicit envelope-bound adapter/session. Discovery of usable ambient authority outside the inventory/envelope graph is an omitted-capability finding.

### D8 — Queued work freezes authority context

A task that may later execute a consequential effect must commit at enqueue time to the capability envelope digests or to a narrower derivation rule. Execution revalidates current recipient epoch, revocation generation, expiry, policy/trust frontiers, and object/session binding.

A queued task does not preserve authority merely because it was created while authority was valid.

### D9 — Provider/broker sessions are capabilities, not identities

A session token or client object is insufficient evidence of authority. Consequential use requires a bound envelope naming provider/broker identity, account/resource scope, session generation, supported effects, expiry/revocation domain, and causal parent. Reauthenticated replacement sessions require a new descendant/root envelope rather than aliasing the old session identity.

### D10 — Re-delegation is separately authorized

Possessing `WRITE` or `MUTATE` authority does not imply the right to delegate it. Duplication/transfer/re-delegation rights are explicit. This follows the Fuchsia distinction between ordinary operation rights and `DUPLICATE`/`TRANSFER` rights.

### D11 — Revocation propagates over the logical descendant DAG

Revoking an ancestor at generation `r` invalidates every descendant whose authority depends on that ancestor unless an authenticated independent root issuance predating the effect is proven.

The runtime maintains or can reconstruct a revocation-reachable descendant set. A descendant cannot escape revocation by being duplicated, transferred to another process, wrapped by a plugin, or serialized into a queue.

### D12 — Physical revocation and logical revocation are distinct

Some OS capabilities cannot be forcibly clawed back after transfer. Therefore:

- `PHYSICALLY_REVOKED`: the object/session itself is mechanically unusable;
- `LOGICALLY_REVOKED`: supported runtime/broker paths reject use, but a stale raw handle may still physically exist;
- `REVOCATION_UNENFORCEABLE`: the recipient retains an unmediated authority-bearing object that the system cannot revoke.

`REVOCATION_UNENFORCEABLE` is incompatible with claims that require descendant revocation. Such a delegation must instead be bounded by process isolation/lease expiry/object-level revocation or declared outside the supported security claim.

### D13 — Independent effect attribution

Where consequential effects are independently observable, reconciliation records the exact `instance_id/delegation_id/causal_parent`. If an effect is observed from a capability that lacks a valid current lineage, it can produce `UNATTRIBUTED_DELEGATED_EFFECT_PROVEN` or `REVOKED_DESCENDANT_EFFECT_PROVEN` and stale dependent finalization/GC authority.

### D14 — Restart does not launder descendants into roots

Recovery must reconstruct the prior envelope lineage or explicitly perform a fresh root issuance under current policy. A persisted token/session/FD-surrogate cannot become a new root merely because its parent process no longer exists.

## Attenuation proof

`DelegationAttenuationProofV1` commits to:

- parent and child envelope digests;
- canonical rights/resource/temporal/delegation scopes;
- deterministic subset checks;
- object/session binding relation;
- issuer/recipient epochs;
- policy/trust/inventory/schema generations;
- enforcement adapter identity;
- proof/verifier version.

For E2/E3/E4 consequential paths, the checker must be independent from the code that constructs the child scope. A producer cannot broaden scope and have its own mapper declare the broadening to be attenuation.

## Descendant revocation protocol

1. Authority owner advances `revocation_generation` for the revocation domain.
2. Revocation statement identifies root/ancestor envelope and effective frontier.
3. Broker/runtime marks all known descendants stale immediately.
4. Queue workers, plugins, process brokers and provider adapters revalidate generation before every consequential effect, not only at initial handoff.
5. Independently observed late effects reconcile against the revocation frontier.
6. Discovery of a previously unknown descendant extends the stale closure; it does not reopen the revoked authority.
7. Finalization/GC proofs that assumed the old live descendant set become stale when a material late descendant is proven.

## Handoff-specific rules

### fork

Child receives only the enumerated inherited capability set. Parent and child epochs are recorded. A post-fork child may not treat arbitrary inherited descriptors as roots.

### exec

Launcher builds an allowlist of inherited consequential descriptors and passes envelope metadata through a protected broker/control channel. All other consequential descriptors use close-on-exec or explicit close. Environment credentials are scrubbed unless specifically registered as non-consequential configuration.

### `SCM_RIGHTS`

Envelope and descriptor transfer are correlated by a nonce/message identity and object-binding check. Truncated ancillary data, extra descriptors, replay, sender-epoch mismatch, recipient-epoch mismatch, or missing envelope fail closed.

### plugin / FFI

Plugins receive least-capability façade objects whose methods map to envelope-authorized effects. Raw native handles/pointers are not passed unless the plugin boundary is itself within the same trust domain and the broader claim is explicitly abandoned. A plugin that can call arbitrary FFI/process spawn/network APIs remains an ambient-authority escape and must be sandboxed/brokered for least-authority claims.

### task queue

Task payload references envelope digests/derivation identities, not reusable bearer credentials where avoidable. Worker resolves the capability through a broker under the current epoch and revocation frontier. Retried/replayed tasks cannot mint fresh authority.

### provider/broker session

The session is bound to provider/account/resource identity and effect class. Session renewal/credential rotation creates a new session generation and authenticated lineage edge. A client object with default credential discovery is not accepted as proof of that binding.

## Omission/fraud proofs

### `UndeclaredDelegationProofV1`

Proves that a consequential descendant effect/handle/session was reachable or used without an authenticated handoff from any admitted ancestor/root.

### `AttenuationViolationProofV1`

Proves a child scope/right/temporal/delegation property exceeded its parent.

### `RevokedDescendantUseProofV1`

Proves a consequential effect occurred after the ancestor revocation frontier while still depending on the revoked lineage.

Valid proof outcome:

- mark dependent capability-inventory/schema/effect-manifest/federated-finalization/GC evidence stale;
- re-root affected E2/E3/E4 closure;
- quarantine the offending recipient lineage;
- require additive repair/new generation; never rewrite historical envelopes.

## Ambient-authority elimination boundary

A meaningful least-authority claim requires both:

1. **namespace/ambient restriction** — lower-trust code cannot independently reacquire equivalent authority from filesystem/network/process/provider namespaces; and
2. **explicit capability lineage** — all allowed consequential handles/sessions/tasks are envelope-bound and attenuated.

Either alone is insufficient. Capsicum is the strongest donor for this combination: remove global namespace access, then operate through explicit descriptor capabilities whose rights only decrease. Landlock demonstrates why pre-existing descriptors must still be audited separately.

For the Python LAB-093 surface, same-process object encapsulation cannot establish this property against hostile introspection. Production least-authority claims therefore compose with the LAB-087 process/broker boundary or an equivalent isolation boundary.

## 80-case RED-first matrix

Freeze all cases RED before implementation; GREEN requires both decision correctness and unchanged durable/external state on rejected paths.

### A. Inheritance / pre-opened handles (10)
1. expected inherited read-only FD;
2. undeclared inherited writable FD;
3. inherited directory FD enabling `openat`;
4. pre-opened socket inside later sandbox;
5. pre-opened TTY/device IOCTL surface;
6. close-on-exec expected closure;
7. accidental non-CLOEXEC secret/session FD;
8. fork child with stale parent epoch;
9. restart with persisted handle surrogate but no parent lineage;
10. duplicate local FD number referring to a different object.

### B. SCM_RIGHTS / explicit transfer (10)
11. valid attenuated transfer;
12. envelope without descriptor;
13. descriptor without envelope;
14. extra descriptor injection;
15. transfer replay;
16. stale sender epoch;
17. stale recipient epoch;
18. object-binding mismatch;
19. transfer after ancestor revocation;
20. delegated write right without transfer/re-delegation right.

### C. Attenuation (10)
21. rights subset;
22. rights broadening;
23. resource-scope narrowing;
24. resource-scope broadening;
25. shorter expiry;
26. longer expiry;
27. lower max delegation depth;
28. re-delegation added where parent forbids it;
29. stricter policy frontier;
30. rollback to older policy/trust frontier.

### D. Plugins / FFI / processes (10)
31. least-capability plugin façade;
32. plugin receives raw provider object;
33. plugin receives native writable FD;
34. plugin spawns child carrying undeclared handles;
35. FFI pointer wraps registered object identity;
36. FFI pointer aliases a different object;
37. subprocess inherits ambient cloud credentials;
38. subprocess receives only broker endpoint;
39. plugin-to-plugin valid attenuated delegation;
40. plugin-to-plugin scope laundering.

### E. Queued/delayed work (10)
41. enqueue+execute under unchanged generation;
42. revoked before dequeue;
43. expired before dequeue;
44. worker epoch changed before dequeue;
45. replay of completed task;
46. retry after provider session rotation;
47. task captures bearer token outside envelope;
48. task references broker-resolved envelope only;
49. delayed child effect absent from parent causal manifest;
50. cancellation races effect execution.

### F. Provider/broker sessions (10)
51. exact account/resource binding;
52. default credential chain silently chooses another account;
53. session renewed to new generation;
54. old session used after renewal revocation;
55. broker token scope narrowing;
56. broker token scope broadening;
57. provider client object shared across unrelated tenants;
58. session object duplicated to unauthorized plugin;
59. remote provider effect independently attributed to delegation id;
60. remote effect observed but lineage missing.

### G. Revocation / descendant graph (10)
61. revoke leaf only;
62. revoke ancestor with one child;
63. revoke ancestor with deep chain;
64. descendant duplicated before revocation and used after;
65. descendant transferred to offline worker before revocation;
66. late-discovered descendant after finalization;
67. independent fresh root survives unrelated ancestor revocation;
68. fake independent-root claim;
69. logically revoked but physically usable raw FD;
70. object-level hard revocation makes raw descendant unusable.

### H. Crash/recovery/finalization (10)
71. crash after envelope persisted before handle handoff;
72. crash after handle handoff before acknowledgement;
73. receiver crash with transferred FD;
74. broker restart preserves revocation generation;
75. recovery accidentally promotes descendant into root;
76. stale finalization after undeclared descendant discovered;
77. stale GC proof after revoked-descendant effect;
78. duplicated envelope id with different object binding;
79. issuer equivocation over same delegation id;
80. complete replay reconstructs identical descendant authority graph.

## Production composition decision

`EffectCapabilityInventoryV1` defines what consequential capabilities exist. `CapabilityEnvelopeV1` defines who currently holds a particular concrete instance, by what lineage, with what attenuated authority. `EffectManifestV1` defines why a consequential operation used it. Federated finalization/GC may trust the effect only when these three layers compose at the same authenticated frontiers.

No layer may infer another by absence: registered capability does not prove valid delegation; possession does not prove authorization; a valid envelope does not prove an effect was declared; an effect manifest does not prove the runtime lacked undeclared ambient authority.

## Verdict

`CAPABILITY_ENVELOPE_TRANSITIVE_DELEGATION_PREOPENED_HANDLE_PROVENANCE_AMBIENT_AUTHORITY_ELIMINATION_V1_FROZEN`

The next unresolved trust gap is **descendant-discovery completeness / revocation-set closure / offline-delegate resurrection semantics**: how to prove that every still-live descendant is known before declaring revocation complete when recipients may be offline, queues may be partitioned, handles may have been duplicated outside a central registry, and some OS capabilities are not physically clawbackable.