# LAB-080 — Shared monotonic-anchor intent ledger

## Problem

LAB-079 correctly rejects `external anchor > local migration sequence` when the migration database cannot explain the extra advancement. That is the safe rule for a dedicated anchor, but it prevents multiple already-authorized runtime components from sharing one monotonic provider.

The unsafe alternative is to accept any signed higher number. That reintroduces false confirmation: an unrelated operation can occupy the expected counter position without proving that the component's own intent ever committed.

## Reference protocol

Before an external increment, the shared SQL ledger durably reserves one canonical intent. Its provider request ID commits:

- exact next position and predecessor;
- intent ID;
- component ID;
- allowlisted intent type;
- payload digest;
- provider identity/generation.

The provider result is accepted only by LAB-036 authenticated reconciliation of that exact request. A stable receipt binding is derived from the freshly verified `(provider, generation, position, request_id)` tuple.

Each component keeps its own verified watermark. If the provider is ahead, the component may advance only after the complete intervening ledger slice is contiguous, CONFIRMED, and freshly reauthenticated entry by entry. The slice is re-read under a write lock immediately before the component watermark CAS so rows cannot change between external verification and durable acceptance.

## Initial evidence

- Corrected deterministic suite: 12/12 passed.
- Unsafe monotonic-only seed fails as expected: `external >= local` accepts unrelated advancement.
- Two independent components can share one provider and later verify each other's authorized increments.
- `commit -> timeout -> reconcile` performs one provider increment.
- Gaps, request substitution, intent-type substitution, receipt corruption, unknown intent type, unresolved predecessor and provider-generation rotation fail closed.
- Compileall passed.

## Audit findings before first publication

1. The first request ID committed only a payload digest. A SQL edit could change visible `component_id`/`intent_type` while leaving the provider-bound request unchanged. The request ID now hashes all visible semantic identity fields plus the payload digest.
2. The first component verification advanced its watermark after external verification without re-reading the ledger slice. The corrected version re-reads exact rows under `BEGIN IMMEDIATE` before watermark mutation.

## Boundaries

This reference model deliberately permits only one unresolved PREPARED intent at a time. It does not implement distributed consensus, remote transparency, provider availability, multi-writer replication, or historical provider-key verification after generation rotation. Those remain separate concerns unless evidence makes them the next correctness bottleneck.
