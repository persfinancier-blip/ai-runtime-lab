# LAB-090 supported-ledger activation wiring — 2026-09-15

## Runtime observation

LAB-086 was probed first with `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git`. Git transport failed before repository execution with `Could not resolve host: github.com`, exit 128. No LAB-086 PASS is claimed.

## Objective

Compose the already isolated LAB-090 provider fence transition and durable acknowledgement slices into PR #187's construction-bound `SupportedHistoricalSharedAnchorLedger` without restoring the authority-heavy donor `supported.py` from PR #175.

## Change

PR #187 `experiments/provider_generation_history/supported.py` now composes `ActivationTransitionMixin` and `ActivationCoordinatorMixin` ahead of `HistoricalSharedAnchorLedger`.

`rotate_provider()` now:

1. requires exact `AttestedCatchup` and a runtime descriptor matching the requested new generation;
2. requires `FencedActivationProvider`;
3. for a durable retry, accepts only the durable current generation and reconciles exact `SQL_COMMITTED` / `COMMITTED` activation state;
4. otherwise calls `_preack_activation_transition(provider, new, proof)`;
5. only after that durable SQL transition calls `_commit_or_reconcile_activation(provider, ticket)`;
6. installs `new_attested` only after durable acknowledgement/release succeeds.

The supported rotation path does not call `_rotate_locked` directly, does not use the public `provider_history` inspection view, and does not reintroduce the donor's pre-fence `authenticated_read` path. Private construction-bound `_history()` remains the history authority.

Production commit: `6b8469a52f6c3f924ceb9c281593261108f87569`.
Focused regression commit: `16f06a710990932ed4a76e80fc1c66bced76b000`.

## Validation and audit

Because exact branch materialization remains unavailable, no repository pytest/compile GREEN is claimed. A committed focused regression (`tests/test_supported_activation_wiring.py`) checks MRO composition, fenced pre-ack -> durable acknowledgement -> runtime-install ordering, absence of direct `_rotate_locked` / public `provider_history` use in the supported rotation method, and retry rejection before reconciliation when the requested generation is not the durable current head.

Separate source audit found no need to copy PR #175's schema installation or public-history authority into this slice. Activation schema installation remains the explicit LAB-092 migration/startup concern already composed on PR #187.

## Remaining LAB-090 work

The next slice is restart/historical recovery. It must reconcile current-generation `SQL_COMMITTED` / `COMMITTED` records against provider `PREPARED` / `COMMITTED_FENCED` / `RELEASED`, reject premature release or lost reservation, and fail closed if any historical generation remains unresolved. It must use private `_history()` and must not weaken LAB-092 provenance or LAB-095 canonical database binding.
