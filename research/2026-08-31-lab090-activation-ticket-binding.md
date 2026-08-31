# LAB-090 activation-ticket binding audit

Date: 2026-08-31

## Finding

`SupportedHistoricalSharedAnchorLedger.rotate_provider()` derives the expected activation identity from the candidate `GenerationDescriptor` and shared-anchor tail, then calls `provider.prepare_activation(...)`. The returned `ActivationTicket` is persisted into `provider_generation_activations` before the coordinator has checked that its `provider_id`, `generation`, `expected_position`, and `activation_id` are exactly the values requested for the candidate generation.

The current in-process `FencedActivationProvider` returns a correctly bound ticket, but the supported surface accepts subclasses and the protocol boundary should fail closed on a malformed provider response rather than durably rotating first and discovering inconsistency during provider commit or restart verification.

A malformed ticket can therefore produce a durable generation-head rotation plus an activation row whose provider identity does not bind the new generation. This is a correctness/availability state-poisoning defect, not an authority expansion.

## Regression

Published on draft PR #175:

- commit `91b54bc3440c2e13dcc60a3138b7793afc58d85e`
- `experiments/provider_generation_history/tests/test_activation_ticket_binding.py`
- expected Git blob `05b11e7549a051ee5c09d77b3571aa8123e95e3d`

The regression uses a `FencedActivationProvider` subclass that performs the real provider-side prepare but returns a ticket with the wrong `provider_id`. Required behavior: `HistoricalVerificationError`, durable provider generation remains G1, and no G2 activation row is persisted.

The test source was independently hashed locally to the expected Git blob above and `py_compile` passed. Behavioral RED/GREEN execution is not claimed because direct repository transport remains unavailable in this run.

## Minimal fix

Immediately after `prepare_activation()` returns and before opening/mutating the authoritative generation-head transaction, require:

- `ticket.provider_id == new.provider_id`;
- `ticket.generation == new.generation`;
- `ticket.expected_position == expected_position`;
- `ticket.activation_id == activation_id`;
- `ticket.fence >= 1`;
- provider-reported status for the exact ticket is `PREPARED` (or an explicitly documented idempotent committed state only if retry semantics require it).

On mismatch, fail before any coordinator SQL mutation. Do not attempt to infer or repair hidden provider-side reservation state from a malformed response.

## LAB-086 probe

LAB-086 remained first priority. `fetch_pr_file_patch` for PR #165 returned the complete 949-line `strict_fence.py` addition and the retained hidden-rowid patch still has blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`. However, no supported operation in this run can server-side apply the retained unified patch to that exact payload and feed the result directly into a normal Contents write. Manual/model reserialization of the security-critical whole file remains prohibited, so no LAB-086 mutation was attempted.
