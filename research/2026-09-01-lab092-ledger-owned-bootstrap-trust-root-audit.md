# LAB-092 ledger-owned bootstrap trust-root audit

Date: 2026-09-01

## Scope

Continuation of the LAB-092 audit after public return values/descriptors and caller-owned `attested`/provider capabilities were separated from the activation-schema provenance question.

This pass examined ledger-owned reference state that remains publicly reachable after construction, especially `provider_history.bootstrap`, for a concrete supported-API privilege amplification rather than treating arbitrary Python attribute reassignment as a bug by itself.

## Runtime/tool observation

LAB-086 was probed first as required by `state/CURRENT.md`. A fresh local clone attempt failed before repository code execution:

```text
fatal: unable to access 'https://github.com/persfinancier-blip/ai-runtime-lab.git/': Could not resolve host: github.com
```

The GitHub connector still exposes ordinary Contents reads/writes but no observed byte-preserving operation that can compose exact predecessor `d4a6a40f...` with retained patch blob `61841b58...` and require target blob `b78e7c98...` without model/manual reserialization of the security-critical source. No LAB-086 branch mutation was attempted.

## Finding

A concrete lower-layer trust-root issue exists in provider history, but it is not specific to LAB-092.

`DurableProviderHistory.__init__()` validates the bootstrap descriptor and stores it in public mutable attribute `self.bootstrap`.

`DurableProviderHistory.verify_durable()` later authenticates the beginning of provider history with:

```python
if descriptors[0].generation_id != self.bootstrap.generation_id:
    raise HistoryRollback("bootstrap generation changed")
```

`IntegratedProviderHistory._verify_durable_locked()` performs the same comparison and is inherited by LAB-081/LAB-090/LAB-092 supported ledger composition.

The reachable ledger-owned object `ledger.provider_history` therefore contains a caller-rebindable slot that is later consumed by a supported verification API as the authenticated trust root. Rebinding the attribute is not merely cosmetic state mutation: if durable history is substituted/rolled back to a different valid chain and the public bootstrap slot is rebound to the substituted chain's first descriptor, the verification comparison uses the new value rather than the construction-time trust root.

That is a concrete authority amplification because a supported verification method consumes the rebound value as security-critical authority. It differs from the rejected class of arbitrary attribute reassignment that has no subsequent privileged interpretation.

## Scope decision

Do **not** patch this in LAB-092.

The mutable bootstrap originates in the base provider-history abstraction and affects every composition that consumes `DurableProviderHistory` / `IntegratedProviderHistory`. A LAB-092-only wrapper would leave the underlying trust-root contract inconsistent and would mix activation-schema provenance with provider-history root ownership.

This is also distinct from LAB-093/#178. LAB-093 concerns caller-owned mutable `AttestedCatchup`/provider capabilities that the caller already possessed before ledger construction. The bootstrap descriptor is retained verification authority owned by the history object after construction and used to validate durable history.

## Durable follow-up

Opened #179 / LAB-094: **Make provider-history bootstrap trust root immutable after construction**.

Acceptance direction:

- define construction-time bootstrap continuity as a lifetime invariant for supported provider-history objects;
- retain the validated bootstrap in non-rebindable/private immutable state;
- make all durable verification paths use that retained trust root;
- preserve read-only introspection only if needed;
- add a regression proving post-construction public-state rebinding cannot make substituted/rollback history pass `verify_durable()`;
- keep `path` and other retained reference fields as separate audits rather than silently broadening the change.

## LAB-092 verdict for this pass

No new LAB-092 production or regression change is justified by this finding. The concrete defect belongs to the lower provider-history trust-root boundary and is tracked in LAB-094.

PR #177 therefore remains draft and unchanged pending exact behavioral execution.
