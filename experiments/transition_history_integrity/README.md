# LAB-059 transition-history integrity

`verify_history()` reconstructs bootstrap → head and re-verifies exact historical threshold proof material after restart. `reconcile_verified()` refuses to return a committed UNKNOWN result until the entire history verifies.

This is local durable-history conformance, **not** whole-database rollback resistance; that remains the LAB-034–037 external-anchor boundary.
