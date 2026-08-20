# LAB-052 — Multi-replica root+bundle convergence and split-view detection

Date: 2026-08-20  
Issue: #99  
Branch: `lab/052-bundle-replica-convergence`

## Question

How can replicas distribute the authenticated root+bundle state from LAB-050/051, safely catch up a stale replica, and detect divergent authenticated views without pretending that gossip/detection is a consensus protocol?

## Primary donors and transferable mechanisms

### RFC 9162 — authenticated append-only views still need cross-client comparison

RFC 9162 makes two distinct points that are directly relevant here:

1. Merkle/continuity proofs can prove that one authenticated state extends another.
2. A malicious service can still show different, internally consistent views to different clients; detecting that class of misbehavior requires sharing/comparing independently obtained views (gossip), and the RFC does not define consensus/prevention.

Transfer to LAB-052: a replica may advance only through an authenticated continuity path; incomparable authenticated histories are evidence of split view, but isolated replicas can retain forks until their views meet.

Primary source: https://www.rfc-editor.org/rfc/rfc9162.html

### TUF — monotonic trusted metadata and rollback/mix-and-match rejection

TUF requires clients not to replace trusted metadata with lower versions and binds metadata through authenticated version/hash relationships to prevent rollback and mix-and-match. Root updates also require strict predecessor continuity.

Transfer to LAB-052: a shorter authenticated replica history remains historically attributable but cannot replace the current service head; catch-up is one-directional over exact predecessor continuity, never “pick the higher-looking version”.

Primary source: https://theupdateframework.github.io/specification/draft/

### Existing lab donors

- LAB-040 established the internal distinction between local checkpoint validity and split-view detection after independent views meet.
- LAB-050/051 established exact authenticated root+bundle identities, root lifecycle continuity, bundle signer binding, and historical attribution.

LAB-052 composes those results rather than inventing a separate authority model.

## Reference protocol

`experiments/ctv2_bundle_replica_convergence/` models an authenticated linear event history:

- `RootEvent` commits provider, version/epoch, exact predecessor root, root material, root authority identity and the bundle signer authorized by that root.
- `BundleEvent` commits bundle version/generation, exact predecessor bundle, exact active root identity, payload digest and bundle signer.
- `AuthenticatedHistory.validate()` verifies signatures and continuity before a head can be served or exchanged.
- `Replica.receive()/exchange()` permit only strict-prefix catch-up. A shorter incoming history is rejected for current service; incomparable histories raise `SplitViewDetected`.
- `ReplicaStore` persists the observed `head_id + history_digest + history_length`; restart recomputes all three from authenticated event bytes before accepting the watermark.
- `ViewPolicy` counts distinct authenticated replica identities; duplicate identity cannot inflate evidence quorum.

The model intentionally does **not** elect a leader, run quorum commit, prevent two isolated writers, or guarantee liveness. It is a detection/convergence harness, not consensus.

## Unsafe baseline

The deliberately unsafe `UnsafeIsolatedReplica` validates each presented history locally but never compares it with previously accepted views. Two incompatible same-predecessor bundle forks are therefore both accepted.

Observed failure:

```text
AssertionError: 2 != 1 : isolated replica accepted two incompatible authenticated heads
```

This demonstrates the core gap: local cryptographic validity does not imply one global view.

## Corrected deterministic validation

Observed local command:

```bash
PYTHONPATH=. python -m unittest discover \
  -s experiments/ctv2_bundle_replica_convergence/tests \
  -p 'test_*.py' -v
```

Result after audit fix: **14/14 tests passed**.

Covered scenarios:

1. identical authenticated heads converge trivially;
2. stale replica catches up over an authenticated strict prefix;
3. rollback/stale history cannot replace current service head;
4. same-predecessor root forks are detected;
5. same-root divergent bundle successors are detected;
6. restart preserves/revalidates watermark and head;
7. split view exists locally before exchange and becomes detectable only when views meet;
8. duplicate replica identity does not inflate quorum;
9. conflicting views under one replica identity are rejected;
10. bundle cannot advance onto a new root until the authenticated root event is in the history;
11. valid root transition followed by bundle transition succeeds;
12. evidence quorum requires distinct authenticated replica identities;
13. two isolated authenticated root forks can exist simultaneously, proving no consensus/prevention claim;
14. an authenticated root signature from a registry key that was not authorized by the predecessor root is rejected.

`python -m compileall -q experiments/ctv2_bundle_replica_convergence` also passed.

## Audit finding and correction

The first corrected implementation verified a successor root signature against the global known-key registry but failed to require that the signer was authorized by the predecessor root. A different known root key could therefore extend the lineage despite not being the current authority.

The audit added an explicit predecessor-authority binding and regression test. This matters because “signature valid” and “signer currently authorized for this lineage” are separate properties, a distinction already established in LAB-037/038/051.

## Guarantees

The reference protocol demonstrates:

- local authentication and root+bundle continuity;
- monotonic service-head behavior per replica;
- deterministic authenticated catch-up over strict prefixes;
- rollback rejection for current service while retaining historical attribution;
- deterministic split-view evidence once divergent histories are compared;
- restart-persistent local watermark/head validation;
- distinct replica identity accounting.

## Non-guarantees

It does **not** demonstrate:

- Byzantine consensus;
- prevention of forks while replicas are isolated;
- leader election or quorum commit;
- reliable gossip/network delivery;
- availability/liveness under partition;
- a production key-management or HSM implementation.

A split view can remain undetected indefinitely if conflicting views never cross an independent comparison path. That limitation is part of the result, not hidden by the model.

## Integration implication

For the lab runtime, a replica must never select a “newer-looking” root+bundle head by version alone. It may move current service state only when the candidate is an authenticated strict extension of its durable watermark. An incomparable authenticated view becomes security evidence and blocks automatic convergence until a higher-level mechanism resolves authority; it is not silently merged.

The next likely correctness gap is **gossip/exchange evidence durability and partition/freeze semantics**: LAB-052 assumes replicas eventually exchange complete authenticated histories. Before any consensus work, the lab should first determine how to distinguish ordinary delivery delay/partition from a maliciously frozen view without turning timeouts into false split-view claims.
