# LAB-100 — rejected activation ticket can leave provider reservation stranded

Date: 2026-09-03

## Scope

Source audit of draft PR #175 (`LAB-090: provider-owned activation fencing primitive`) while LAB-086 exact publication remains blocked by per-run direct Git DNS failure.

This note strengthens existing LAB-100/#185 rather than creating another issue.

## Source finding

`SupportedHistoricalSharedAnchorLedger.rotate_provider()` performs these steps after candidate-provider validation:

1. call `provider.prepare_activation(...)`;
2. validate the returned `ActivationTicket` fields;
3. check `provider.activation_status(ticket) == "PREPARED"`;
4. only then set up the SQL-phase cleanup scope (`sql_committed = False`, `_con()`, `try/except`, and eventual `provider.abort_activation(ticket)`).

Therefore any rejection between steps 1 and 3 occurs after the provider may already have installed a real reservation but before the coordinator owns a cleanup path.

## Existing regression proves the setup but misses the leak

`tests/test_activation_ticket_binding.py` defines `WrongTicketProvider.prepare_activation()` by first calling `super().prepare_activation(...)`, which installs `ActivationState.pending`, and then returning a modified `ActivationTicket` whose `provider_id` is `"wrong-provider"`.

The production rotation code rejects that returned ticket with `HistoricalVerificationError` before entering its SQL-phase cleanup scope.

The regression currently asserts only:

- durable generation remains g1; and
- no g2 activation row exists.

It does **not** assert that the provider-side reservation created by `super().prepare_activation()` was removed. Under the current control flow the authentic underlying pending ticket remains in `p2.activation_state.pending`.

This is a fail-closed availability/state-ownership defect: the durable coordinator correctly refuses the malformed ticket, but the candidate provider can remain fenced even though no durable activation record exists from which restart/recovery could reconcile it.

## Relationship to existing work

This is not a new independent issue:

- LAB-100/#185 already establishes that subclassable/caller-controlled activation-provider semantics are not a sufficiently bound authority boundary.
- LAB-090/#169 already owns provider reservation lifecycle and cleanup/reconciliation behavior.

The important addition is that the existing malformed-ticket regression itself supplies a concrete pre-fix schedule for a stranded provider reservation and should be strengthened rather than duplicated.

## Regression-first extension

Extend the malformed-ticket test so that after `rotate_provider()` rejects the ticket it also proves the candidate provider has no live reservation/fence.

A safe post-fix design must avoid attempting to abort an untrusted/malformed returned ticket blindly. Coherent options include:

1. enforce the trusted/exact provider boundary before calling `prepare_activation()` (the minimal LAB-100 direction if subclasses are unsupported); or
2. if extensible providers are supported, define a trusted capability/adapter protocol whose prepare operation either returns a verified ownership handle that can always be safely cancelled by the caller, or performs validation atomically inside the trusted boundary.

Do not merely call `abort_activation()` on the malformed ticket: the provider's authentic installed reservation may correspond to different authority-relevant fields, and a caller-controlled subclass can override abort semantics too.

## Validation status

This is source/control-flow evidence from the exact PR patch and existing regression source. Direct Git clone was re-probed in this run and failed before repository access with `Could not resolve host: github.com`; no exact repository behavioral PASS/RED execution is claimed.
