# LAB-100 — activation-provider subclass can replace the fencing protocol

Date: 2026-09-02

## Finding

Draft PR #175 (`d9a381dd4607a928cd1315adef6431e239995bc1`) treats the LAB-090 activation provider as a security-critical protocol implementation, but the supported coordinator checks it with `isinstance(provider, FencedActivationProvider)` rather than requiring the exact audited implementation or an explicitly authenticated capability contract.

This matters because ordinary Python subclassing can override `prepare_activation`, `activation_status`, `commit_activation`, `release_activation`, and `abort_activation` while still satisfying `isinstance(..., FencedActivationProvider)`. The coordinator then trusts those overridden methods for every external linearization/fence transition.

The same supported surface is deliberately stricter about `AttestedCatchup`: constructor and rotation require `type(attested) is AttestedCatchup`. The activation provider therefore has a materially weaker implementation-identity boundary than the wrapper whose `provider` slot it consumes.

## Concrete bypass shape

A subclass of `FencedActivationProvider` can:

1. return a syntactically correct `ActivationTicket` from `prepare_activation()` without installing provider-side `pending` state;
2. report `PREPARED` from `activation_status()`;
3. report `COMMITTED_FENCED` from `commit_activation()` without establishing any external increment fence;
4. report `RELEASED` from `release_activation()`.

`SupportedHistoricalSharedAnchorLedger.rotate_provider()` accepts the subclass, persists the ticket and provider-generation transition, marks the activation COMMITTED, and proceeds under the assumption that the external provider was fenced. The coordinator's checks validate returned values/ticket fields but not the implementation or independently observable provider-side reservation state.

This is not the same issue as LAB-093/#178. LAB-093 concerns capability leakage/rebinding after construction. LAB-100 concerns what implementation is accepted *at construction/rotation as the trusted LAB-090 fencing primitive*.

## Evidence

Source observations on PR #175 head:

- `SupportedHistoricalSharedAnchorLedger.__init__()` requires exact `AttestedCatchup` using `type(attested) is AttestedCatchup`.
- `rotate_provider()` accepts any provider satisfying `isinstance(provider, FencedActivationProvider)`.
- `_recover_pending_activation()` uses the same `isinstance` rule.
- `FencedActivationProvider` is a normal subclassable Python class; all activation lifecycle methods are overridable instance methods.
- `AttestedCatchup` itself stores `provider` without an exact-type constraint, so the exact wrapper check does not constrain the nested provider implementation.

No exact-branch behavioral PASS is claimed in this run; direct git transport remained unavailable (`Could not resolve host: github.com`). This finding is a source-level trust-boundary proof.

## Regression-first contract

Before changing production code, construct an exact `AttestedCatchup` whose `.provider` is a subclass of `FencedActivationProvider` overriding the activation lifecycle to return valid-looking statuses/tickets without installing `ActivationState.pending`.

Pre-fix: demonstrate that LAB-090 rotation accepts the provider and durably advances provider-generation history despite absence of a real provider-side fence.

Post-fix: fail closed before SQL/provider-generation mutation unless the activation capability is the exact audited implementation or satisfies an explicit non-overridable/authenticated provider capability contract whose fence state can be independently verified.

Also cover restart/recovery so a subclass cannot fake `COMMITTED_FENCED`/`RELEASED` during reconciliation.

## Design constraint

Do not solve this by merely changing one `isinstance` to `type(...) is ...` without deciding the supported extension model. If custom real providers are intended, define an explicit trusted adapter/capability boundary and authenticate/verify its semantics outside caller-overridable return values. If only the audited in-process provider model is supported, exact-type enforcement is the minimal coherent contract.

## Priority

READY follow-up. LAB-086 remains priority #1. LAB-090 production changes should not be staged for this finding until its exact pre-fix RED can execute or an equivalently strong auditable execution path exists.
