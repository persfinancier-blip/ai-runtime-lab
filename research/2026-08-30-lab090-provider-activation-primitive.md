# LAB-090 — provider-owned activation fencing primitive

Date: 2026-08-30
Issue: #169
Draft PR: #175
Branch: `lab-090-provider-activation-fencing`

## Objective

Implement the smallest provider-owned primitive needed to close the reproduced handoff race before wiring it into `HistoricalSharedAnchorLedger.rotate_provider()`.

The existing coordinator path authenticates the candidate provider before the SQLite write transaction. SQLite cannot prevent another actor from advancing that external provider after the read. The linearization point therefore has to be owned by the provider.

## Implemented slice

`experiments/provider_generation_history/activation.py` adds:

- `ActivationTicket(provider_id, generation, expected_position, activation_id, fence)`;
- provider-owned `ActivationState` with a monotonically increasing fence, one pending reservation and idempotent committed-ticket records;
- `FencedActivationProvider.prepare_activation()` which atomically checks the exact expected position before installing a reservation;
- `activation_status()`, idempotent `commit_activation()` and `abort_activation()`;
- ordinary provider increment is rejected while an activation reservation is PREPARED;
- provider-owned activation state can be shared by a reconstructed provider object, modelling provider-side durability across coordinator restart.

The primitive intentionally lives beside provider-generation history instead of adding another coordinator/SQLite lock. A production external provider must implement equivalent state atomically with its own position/CAS metadata.

## Focused execution actually performed

Direct repository `git` transport was probed in this run and failed before clone with `Could not resolve host: github.com`. Therefore no claim is made that the exact branch unittest suite executed.

A local focused mechanism execution was run against the exact new primitive logic with dependency behavior matching the LAB-036 `SignedAnchorProvider` methods used by the primitive. Results: 6/6 PASS.

Cases executed:

1. prepare at position N installs fence and blocks an unrelated increment;
2. candidate already at N+1 rejects prepare(N) as stale;
3. repeated prepare with the same activation id is idempotent and does not allocate a second fence;
4. commit followed by simulated lost acknowledgement raises UNKNOWN but provider status reconciles as COMMITTED and repeated commit is idempotent;
5. reconstructed coordinator/provider wrapper over the same provider-owned activation state sees PREPARED and can commit it;
6. abort releases the fence without changing provider position and a subsequent ordinary increment succeeds.

## Source audit

PR #175 was re-fetched as a two-file patch after publication. The change is additive and does not mutate LAB-036 or the existing LAB-081 rotation path yet. This is deliberate: wiring must persist/bind the activation ticket on the coordinator side before the SQL generation-head commit so restart and UNKNOWN can reconcile the exact ticket rather than relying on process memory.

A remaining integration concern is that all provider mutations relevant to an actual external implementation must honor the same fence. The experiment currently fences `increment`, which is the reproduced shared-anchor advance path. Provider identity/configuration mutation is not yet claimed to be covered by LAB-090.

## Decision

Keep PR #175 draft. Do not replace the atomic provider precondition with a second authenticated read or SQLite locking. Next, bind the activation ticket/fence into the durable rotation protocol and then change `HistoricalSharedAnchorLedger.rotate_provider()` to `prepare -> persist ticket/SQL rotate -> commit/reconcile`, with abort on pre-SQL failure and restart recovery from the durable ticket.
