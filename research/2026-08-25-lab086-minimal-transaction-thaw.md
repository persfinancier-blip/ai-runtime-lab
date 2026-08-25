# LAB-086 — transaction-scoped thaw must preserve historical immutability

## Finding

The current `remove_public_mutation_fence_locked()` is broader than the consequential writers require.

For inherited authenticated history it drops `*_all_inherited_trigger_names()`, which includes both:

- creation-deny triggers needed to permit a new authenticated transition/proof; and
- UPDATE/DELETE immutability guards for already committed history.

It also drops the complete `PUBLIC_MUTATION_TRIGGER_NAMES` set, including UPDATE/DELETE guards for existing public-recovery authorities/transitions, even though public rotation only requires INSERT of the new authority/transition and UPDATE of the current head.

A focused SQLite semantic counterexample reproduced the consequence for inherited history:

1. existing authenticated root transition is protected before thaw;
2. current-source-equivalent thaw drops INSERT + UPDATE + DELETE triggers;
3. UPDATE of the old transition succeeds;
4. a minimal thaw that drops only the INSERT-deny keeps the same UPDATE blocked.

This is not an external concurrent-writer bypass: the final writer holds `BEGIN IMMEDIATE`. It is a least-privilege/correctness blocker because transaction-scoped authority is wider than the operation needs and makes old evidence mutable inside the most privileged path.

## Required fix

Split mutation-capability triggers from history-immutability triggers.

At minimum:

```diff
 def remove_public_mutation_fence_locked(q):
     for name in (
-        *PUBLIC_MUTATION_TRIGGER_NAMES,
-        *_all_inherited_trigger_names(),
+        *PUBLIC_RECOVERY_CREATION_AND_HEAD_MUTATION_TRIGGER_NAMES,
+        *INHERITED_MUTATION_TRIGGERS.values(),
         *ROOT_HEAD_MUTATION_TRIGGER_NAMES,
         *CURRENT_AUTHORITY_WRITER_TRIGGER_NAMES,
         *_all_post_cutoff_evidence_creation_trigger_names(),
         *OBSOLETE_PUBLIC_MUTATION_TRIGGER_NAMES,
     ):
         q.execute(f"DROP TRIGGER IF EXISTS {name}")
```

The exact public subset should include only the operations required by the final public-recovery writer:

- INSERT new public authority;
- INSERT new public transition;
- INSERT/UPDATE public head as required by the supported primitive.

It must not remove UPDATE/DELETE guards on existing public authorities/transitions, and it should not remove public-head DELETE unless a supported operation proves it is required.

## Regression

`tests/test_transaction_scoped_thaw_minimality.py` is committed red on the current candidate. It requires both inherited transition history and existing public-recovery history to remain immutable after transaction-scoped thaw.

The next run should apply the minimal source patch to the exact current `strict_fence.py` blob, execute this regression plus the existing strict-fence suite, then resume the full real-ledger merge gate.
