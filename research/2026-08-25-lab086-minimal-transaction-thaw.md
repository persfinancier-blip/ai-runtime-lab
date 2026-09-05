# LAB-086 — transaction-scoped thaw must preserve historical immutability

## Finding

The current `remove_public_mutation_fence_locked()` is broader than the consequential writers require.

For inherited authenticated history it drops `*_all_inherited_trigger_names()`, which includes both creation-deny triggers and UPDATE/DELETE immutability guards for already committed history. It also drops the complete public-recovery and singleton-head mutation trigger sets.

A focused SQLite semantic counterexample reproduced the consequence for inherited history:

1. an existing authenticated root transition is protected before thaw;
2. current-source-equivalent thaw drops INSERT + UPDATE + DELETE triggers;
3. UPDATE of the old transition succeeds;
4. a creation-only thaw keeps the UPDATE blocked and preserves the old row.

This is not an external concurrent-writer bypass: the final writer holds `BEGIN IMMEDIATE`. It is a least-privilege/correctness blocker because transaction-scoped authority is wider than the supported operation requires.

## Exact capabilities used by supported writers

Source audit of the lower primitives established the required operations:

- normal root rotation: `INSERT provider_rotation_authorities`, `INSERT provider_rotation_authority_transitions`, `UPDATE provider_rotation_authority_head`;
- provider rotation: `INSERT asymmetric_provider_generations`, `INSERT provider_rotation_threshold_proofs`, `INSERT asymmetric_provider_transitions`, `UPDATE asymmetric_provider_head`;
- public-recovery rotation: `INSERT provider_recovery_public_authorities`, `INSERT provider_recovery_public_transitions`, `UPDATE provider_recovery_public_head`;
- asymmetric break-glass: `INSERT provider_rotation_authorities`, `UPDATE provider_rotation_authority_head`, `INSERT provider_asymmetric_break_glass_proofs`.

None of these supported operations requires:

- UPDATE/DELETE of an existing authenticated transition/proof/authority row;
- INSERT/REPLACE of an already initialized singleton head;
- DELETE of a singleton head.

## Required fix

Split transaction-scoped mutation capability from durable-history immutability.

During thaw remove only the exact creation/head-update triggers needed above:

- public recovery: authority INSERT, transition INSERT, head UPDATE;
- inherited root/provider evidence: `INHERITED_MUTATION_TRIGGERS.values()` only;
- root head: UPDATE only;
- current root/provider state: root-authority INSERT, provider-generation INSERT, provider-head UPDATE only;
- LAB-086 post-cutoff evidence: creation triggers only;
- obsolete legacy trigger names as needed for upgrade cleanup.

Keep installed throughout thaw:

- all UPDATE/DELETE immutability guards for committed history;
- public/root/provider head INSERT/REPLACE and DELETE guards;
- threshold-enablement, migration-metadata, legacy-projection and provider-receipt history guards.

## Regression

`tests/test_transaction_scoped_thaw_minimality.py` is committed red on the current candidate. It now requires:

1. inherited authenticated transition history stays immutable after thaw;
2. existing public-recovery authority/transition history stays immutable after thaw;
3. public/root/provider singleton heads still reject `INSERT OR REPLACE` and DELETE during thaw.

The next implementation step is a minimal change to the exact current `strict_fence.py`, followed by this regression plus the complete strict-fence suite before resuming the full real-ledger merge gate.
