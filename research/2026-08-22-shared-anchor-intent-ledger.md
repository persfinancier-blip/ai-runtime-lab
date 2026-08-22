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

The supported restart boundary additionally verifies that `reserved_position` equals the exact durable ledger tail, positions/predecessors are contiguous, there is at most one PREPARED entry and it is the tail, component watermarks are structurally valid and end on confirmed history, and every retained entry still belongs to the current provider generation.

## Final observed evidence

- Exact published LAB-080 `protocol.py` blob: `68834409363c93eee4e9a9a7b9ec076098af0acf`.
- Exact published primary tests blob: `d2d127fb67147dda2c5f6786731c0a3310a067e6`.
- Exact published restart tests blob: `aa9b0f3784f97b14b59b128a2e7686e94848d377`.
- Exact published supported boundary blob: `22a05c04831f65c1d7fe9077df3bb780c4008e09`.
- Exact published supported tests blob: `763ee7f6958ed6fda1adde402452fedde5046ea1`.
- Exact merged LAB-036 dependency blob used for execution: `15d8b7cf8ff093490ccb75679030d3a0fe41e401`.
- Corrected exact-source suite: 18/18 passed.
- Unsafe monotonic-only seed failed as expected because `external >= local` accepted unrelated advancement.
- `python -m compileall` over the LAB-080/LAB-036 execution surface passed.
- Two independent components share one provider and later verify each other's authorized increments.
- `commit -> timeout -> reconcile` performs one provider increment.
- Gaps, request substitution, intent-type substitution, receipt corruption, unknown intent type, unresolved predecessor, metadata/tail divergence and provider-generation rotation fail closed.
- A deterministic race regression mutates a previously verified ledger row before watermark commit; the commit-boundary re-read detects the change and the watermark remains unchanged.

## Audit findings fixed before integration

1. The first request ID committed only a payload digest. A SQL edit could change visible `component_id`/`intent_type` while leaving the provider-bound request unchanged. The request ID now hashes all visible semantic identity fields plus the payload digest.
2. The first component verification advanced its watermark after external verification without re-reading the ledger slice. The corrected version re-reads exact rows under `BEGIN IMMEDIATE` before watermark mutation.
3. `shared_anchor_meta.reserved_position` was not independently checked on restart. A corrupted value could prepare a future gap. The supported boundary now requires an exact match to a contiguous ledger tail.
4. Provider-generation behavior is explicit rather than accidental: LAB-036 has no historical provider receipt verifier, so retained ledger entries from an old generation make restart fail closed instead of silently trusting unverifiable history.

## Boundaries

This reference model deliberately permits only one unresolved PREPARED intent at a time. It does not implement distributed consensus, remote transparency, provider availability, multi-writer replication, or historical provider-key verification after generation rotation. Provider-generation rotation therefore remains an availability boundary, not a reason to weaken verification.
