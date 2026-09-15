# LAB-095 DB-binding provider-position audit

Date: 2026-09-15

## Runtime observation

LAB-086 was probed first with a direct `git clone --no-checkout` of the repository. The command failed before repository code execution with `Could not resolve host: github.com` (exit 128). No LAB-086 executable PASS is claimed.

## Scope

Source-audited PR #187 `experiments/provider_generation_history/tests/test_database_path_binding.py` against the composed LAB-090/LAB-092/LAB-101 position semantics recorded in `state/CURRENT.md`.

## Position accounting

The regression is internally consistent; no source change is required.

1. Fresh DB A enters only through `migrate_activation_schema_v1(...)`. Authenticated LAB-092 migration completion consumes provider position **1**.
2. `ledger.execute(Intent("a-1", ...))` is therefore the first ordinary DB-A intent and consumes position **2**.
3. The generation-2 fenced candidate is correctly constructed with `value=2`, exactly matching the durable tail before rotation.
4. Provider rotation changes generation authority but does not itself consume a shared-anchor provider position in this fixture.
5. The subsequent DB-A-only `ledger.execute(Intent("a-2", ...))` therefore confirms at position **3**, matching the assertion.
6. DB B is copied after DB A reaches generation 2/tail 2 in the corruption/rebinding test, so its captured `b_tail_before` is 2 and must remain unchanged after failed rebinding plus DB-A mutation.
7. In the independent strategy-rebinding test, DB B is separately initialized only through `migrate_activation_schema_v1(...)`; its authenticated migration consumes position **1**. No ordinary intent is executed on B, so the final assertion that B remains at tail **1** is correct.
8. In that same test DB A has only migration position 1 before `Intent("a-1", ...)`, so the ordinary intent correctly confirms at position **2**.

## Audit result

PASS by source inspection for provider-position accounting. The regression preserves the intended LAB-095/LAB-096 authority checks and is aligned with composed LAB-090 fencing and LAB-101 bootstrap semantics.

This is **not** an executable GREEN. Exact repository pytest/compileall and retained downstream gates remain pending until byte-exact materialization is available.
