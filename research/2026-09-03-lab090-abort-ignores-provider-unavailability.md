# LAB-090 audit — abort path ignores provider unavailability

Date: 2026-09-03

## Scope

Source-level audit of draft PR #175 (`d9a381dd4607a928cd1315adef6431e239995bc1`) while LAB-086 exact publication remains tool-blocked.

## Finding

`FencedActivationProvider` models provider reachability with `self.available`.

- `prepare_activation()` fails with `ProviderUnavailable` when `available` is false.
- `commit_activation()` fails with `ProviderUnavailable` when `available` is false.
- `release_activation()` fails with `ProviderUnavailable` when `available` is false.
- inherited `read()`, `increment()`, and `reconcile_increment()` also fail when the provider is unavailable.
- **`abort_activation()` is the exception:** it does not check `self.available` and directly mutates provider-owned `ActivationState.pending`.

The LAB-090 coordinator calls `provider.abort_activation(ticket)` when SQL rotation fails before a durable activation row is committed. Therefore the current model can clear a provider-side reservation while the same provider is declared unreachable.

## Why this matters

The LAB-090 authority model treats activation state as externally provider-owned durability and explicitly states that SQLite cannot serialize that external service. If the external provider is unavailable after `prepare_activation()` but before/while the SQL transaction fails, the coordinator cannot safely know that the external reservation was removed unless an abort request actually reached the provider or later reconciliation proves its terminal state.

The current in-process implementation instead lets the coordinator mutate provider-owned state through an unavailable provider. This masks the real unresolved-reservation failure mode and can make SQL-failure cleanup tests stronger than the modeled external-service semantics justify.

This is distinct from LAB-100/#185. LAB-100 concerns whether the coordinator is talking to the trusted provider implementation/authority at all. This finding applies even to the exact audited `FencedActivationProvider`: its own lifecycle treats abort differently from every other provider mutation.

## Regression-first contract

Add a focused schedule:

1. exact `FencedActivationProvider` is available;
2. `prepare_activation()` succeeds and installs the authentic pending reservation;
3. provider becomes unavailable before the SQL rotation commits;
4. inject a SQL-side failure that takes the coordinator cleanup path;
5. pre-fix: `abort_activation()` clears the reservation despite provider unavailability;
6. post-fix: cleanup must not claim a successful abort while unreachable. The reservation remains unresolved until a later provider-visible abort/status reconciliation proves the terminal state.

Also cover restart after this window. A failed local SQL transaction with an externally unresolved reservation has no committed activation row, so a correct design needs an explicit way to preserve/recover abort intent or otherwise prove reservation absence before normal writes resume.

## Design constraint

Do not fix this only by adding `if not available: raise ProviderUnavailable` and leaving the coordinator unchanged. That would expose the deeper durability question: after prepare succeeds but SQL never commits, where is the recoverable evidence that an external reservation may still exist? The solution must keep fail-closed semantics without inventing a coordinator-side assertion that the provider was unfenced.

## Validation status

Source-proved only in this run. Direct Git/source execution is unavailable because `github.com` DNS resolution fails in the local runtime. No exact behavioral PASS is claimed.
