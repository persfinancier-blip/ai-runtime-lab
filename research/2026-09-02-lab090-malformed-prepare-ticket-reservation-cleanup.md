# LAB-090 audit — malformed prepare result can strand provider reservation

Date: 2026-09-02

## Scope

Audit of draft PR #175 (`lab-090-provider-activation-fencing`, observed head `d9a381dd4607a928cd1315adef6431e239995bc1`) while LAB-086 remains blocked on byte-preserving machine composition.

## Finding

`SupportedHistoricalSharedAnchorLedger.rotate_provider()` calls `provider.prepare_activation(...)` before entering the SQL rotation transaction. It then validates the returned `ActivationTicket` and separately requires `provider.activation_status(ticket) == "PREPARED"`.

The cleanup path (`provider.abort_activation(ticket)`) is only entered by the later SQL transaction `except` block. If `prepare_activation()` has already installed provider-side reservation state but returns a malformed/misbound ticket, or if the immediate status check fails, `rotate_provider()` raises before reaching the SQL block and no cleanup attempt is made.

The concrete in-repo `FencedActivationProvider.prepare_activation()` currently constructs a well-formed ticket itself, but the supported surface accepts `isinstance(provider, FencedActivationProvider)`, not an exact provider type. A subclass/fault-injection/external implementation can therefore cross this boundary while preserving the declared provider interface. The coordinator must not rely on an implicit "prepare can never return an unusable result after installing state" assumption unless that guarantee is made explicit and enforced at the provider boundary.

## Why this matters

A provider-side activation reservation fences ordinary external increments. Stranding it after a failed rotation can leave the candidate provider externally fenced even though no SQL generation rotation committed. This is a fail-safe availability/correctness defect and weakens the intended rollback guarantee for unsuccessful activation attempts.

The difficult case is a misbound ticket: blindly aborting an arbitrary returned ticket is not automatically safe because it might refer to an older/unrelated reservation. Therefore the fix should not simply wrap every validation failure in `abort_activation(returned_ticket)` without proving ticket provenance.

## Regression-first contract

Add a provider test double/subclass whose `prepare_activation()` atomically installs a new reservation for the requested activation but returns an unusable result (for example a structurally malformed result or an intentionally misbound ticket) while exposing enough provider-side state for the test to inspect the newly created reservation.

Pre-fix expected result:

1. `rotate_provider()` fails before SQLite generation rotation;
2. provider-side reservation remains pending/fenced;
3. durable provider-generation head remains unchanged.

Post-fix required result:

- failed prepare/validation must leave no newly-created activation reservation owned by that attempt;
- cleanup must not abort an unrelated prior reservation;
- SQLite provider-generation history/head remains unchanged;
- provider ordinary increments are not left fenced by the failed attempt.

A robust design is to make `prepare_activation()` itself provide an atomic success contract: either return an exact validated ticket for the requested `(provider_id, generation, expected_position, activation_id)` with the reservation installed, or leave provider activation state unchanged. If external providers cannot provide that contract, introduce a separate attempt/provenance token that allows exact cleanup of only the reservation created by the failed call.

## Validation status

Source audit only in this run. No repository behavioral RED/GREEN is claimed because exact branch execution is not available in the current runtime. The finding is based on direct inspection of PR #175 source: `rotate_provider()` validation/status failures occur before its SQL cleanup block, while `FencedActivationProvider.prepare_activation()` installs `activation_state.pending` before returning.

## Relationship to existing LAB-090 findings

This is distinct from the previously recorded constructor ordering defects:

- runtime-head verification must precede activation-schema mutation;
- complete activation-history verification must precede recovery side effects.

Those concern restart/constructor fail-closed ordering. This finding concerns rollback semantics of a fresh provider activation attempt before any SQL rotation begins.
