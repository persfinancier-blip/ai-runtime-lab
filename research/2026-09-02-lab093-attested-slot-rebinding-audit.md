# LAB-093 — attested authority-slot rebinding audit

Date: 2026-09-02

## Question

Does LAB-093 cover only recovery of the caller-owned raw provider capability through `ledger.attested`, or is the public `attested` attribute itself also a construction-bound authority slot whose rebinding changes supported ledger behavior?

## Source facts

`SharedAnchorLedger.__init__()` stores the exact caller-supplied `AttestedCatchup` as public mutable `self.attested`.

Subsequent supported operations repeatedly dispatch authority-sensitive behavior through that slot:

- `_provider()` derives provider identity from `self.attested.verifier.expected`;
- `_reauthenticate()` uses `self.attested.challenge()`, `self.attested.provider.reconcile_increment(...)`, and `self.attested.verifier.verify(...)`;
- `execute()` advances the external anchor with `self.attested.catch_up_one(...)`;
- `verify_component()` uses `self.attested.authenticated_read(...)` and then `_provider()` / `_reauthenticate()`.

`HistoricalSharedAnchorLedger` continues to use the same mutable slot. It additionally compares a descriptor derived from `self.attested` to the durable provider-history head, then uses that handle for reconcile/verification. `rotate_provider()` explicitly assigns `self.attested = new_attested` after durable rotation.

`AttestedCatchup` itself stores public mutable `provider` and `verifier` fields. Its verification identity is `(provider_id, generation)` plus the verification key selected from the verifier keyring; there is no separate durable identity for a particular provider object instance or anchor-store instance.

## Concrete delegated-ledger violation

A component delegated only a supported ledger can replace `ledger.attested` after construction with another exact `AttestedCatchup` instance. This is a stronger authority change than merely reading the original caller-owned handle from the ledger:

1. Construct the ledger against external anchor A and durable DB A.
2. Prepare another exact `AttestedCatchup` B whose verifier advertises the same current `(provider_id, generation)` and authenticates with the same verification key, but whose provider object/store has independent position/request-result state.
3. Assign `ledger.attested = B`.
4. Supported methods now perform authenticated reads, catch-up increments, reconcile calls, and provider identity derivation against B without reconstructing the ledger or re-verifying a construction-time binding to external anchor A.

For the historical ledger, `_require_runtime_matches_durable_head()` checks only the generation descriptor obtained from the rebound verifier. If B presents the same generation identity/key, that check does not distinguish external-anchor instance A from B.

This permits a delegated ledger holder to redirect future supported external effects to a different authenticated anchor instance that shares the same logical provider generation. Whether such duplicate authenticated instances are permitted operationally is a deployment question, but the object currently has no lifetime binding that could enforce the answer.

## Relationship to the existing LAB-093 finding

This does **not** justify a new issue. It strengthens LAB-093:

- existing LAB-093 finding: a ledger-only delegate can recover the raw caller-owned mutable capability through public `ledger.attested` / `.provider`;
- this audit: the same public attribute is also a mutable strategy/authority slot, so the delegate can substitute a different exact capability and redirect supported ledger operations.

Both should be fixed by one construction-bound internal authority graph rather than independent wrappers.

## Contract implication

The LAB-093 implementation should treat the active attested capability as private construction/runtime state, not merely hide `.provider` from a public view.

Recommended shape:

- store the active runtime handle in private `_attested`;
- all ledger-internal authenticated read/catch-up/reconcile/verification paths use `_attested`;
- expose only immutable least-capability identity/status information if public inspection is required;
- provider rotation changes `_attested` only through the validated `rotate_provider(...)` transition path, after durable rotation succeeds;
- ordinary external assignment must not be able to redirect the authority slot.

This composes with LAB-094/095/096: bootstrap, DB identity, provider-history strategy, and attested external-anchor capability should form one construction-bound authority graph with explicit validated transition points only.

## Regression-first requirement

In addition to the existing raw-capability escape regression, add a rebound-anchor regression:

- build ledger + anchor A;
- build exact `AttestedCatchup` B with matching provider generation/key but independent anchor state;
- demonstrate pre-fix that assigning `ledger.attested = B` redirects a supported authenticated operation/effect to B;
- post-fix, public assignment must not affect the internal active handle;
- separately prove validated `rotate_provider(...)` still updates the internal active handle when the generation transition succeeds.

Exact behavioral RED/GREEN is still pending an executable source runtime. This note records source-level proof only and does not claim test execution.

## LAB-086 runtime observation in this run

LAB-086 remained first priority. PR #165 currently has head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, but `experiments/asymmetric_break_glass_history/strict_fence.py` at that head still has blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`, i.e. the recorded predecessor, not required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.

The retained patch file remains blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`. Direct local Git clone was probed again and failed before repository execution with `Could not resolve host: github.com`. No LAB-086 source mutation or behavioral execution is claimed.
