# LAB-094 bootstrap trust-root lifetime contract

Date: 2026-09-01
Issue: #179

## Objective

Define the smallest lower-layer contract that prevents post-construction rebinding of the provider-history bootstrap trust root while preserving read-only introspection and existing LAB-081/LAB-090/LAB-092 composition.

## Source evidence

At LAB-090 base `d9a381dd4607a928cd1315adef6431e239995bc1`:

- `DurableProviderHistory.__init__()` validates the caller's `GenerationDescriptor`, then stores it directly as public mutable `self.bootstrap`.
- `_init()` uses `self.bootstrap` to seed a previously empty history.
- `DurableProviderHistory.verify_durable()` later compares the first durable descriptor to `self.bootstrap.generation_id`.
- `IntegratedProviderHistory._verify_durable_locked()` performs the same comparison inside the shared ledger transaction boundary.

Therefore `bootstrap` is not merely descriptive state after construction. It remains active verification authority.

## Threat / correctness model

Python attribute assignment by itself is not a security boundary. The defect arises from combining:

1. an object that has already authenticated/accepted bootstrap A;
2. a public assignable slot used as the root of later durable-history verification; and
3. supported verification methods that trust the slot after construction.

A caller that can substitute durable history and then rebind `history.bootstrap` to the substituted first descriptor can change the root against which later `verify_durable()` decisions are made. The supported object no longer proves continuity from the bootstrap it originally accepted.

This is a lifetime-invariant problem, not an activation-schema provenance problem.

## Required invariant

For one constructed supported provider-history object:

> The generation identity accepted as bootstrap during construction is immutable for the lifetime of that object and is the only bootstrap identity consumed by every later durable-history verification path.

A different bootstrap requires constructing a new object through the full initialization/verification path. There is no supported in-place bootstrap rebind operation.

## Smallest implementation shape

Preferred source design:

- copy/retain the validated bootstrap descriptor into a private lifetime slot such as `self._bootstrap` during `DurableProviderHistory.__init__()`;
- expose `bootstrap` only as a read-only property returning that frozen `GenerationDescriptor` if public introspection compatibility is required;
- make `_init()`, `verify_durable()`, and inherited/integrated `_verify_durable_locked()` consume the same private retained source of truth;
- do not add a setter or rebinding protocol;
- do not combine this change with DB path identity (#180/LAB-095) or caller-owned provider capability encapsulation (#178/LAB-093).

Because `GenerationDescriptor` is already `@dataclass(frozen=True)`, retaining that object is sufficient for field immutability; the remaining problem is rebinding the containing history attribute.

## Regression shape

Regression should reproduce the authority change before the fix, not merely test Python property syntax:

1. create DB/history rooted at bootstrap A and construct the supported history object;
2. prepare/substitute a durable history whose first descriptor is bootstrap B and which would fail continuity against A;
3. demonstrate the pre-fix object can have its public bootstrap slot rebound to B and then accepts the substituted history through `verify_durable()` / integrated locked verification;
4. after the fix, assignment to public `bootstrap` must not change the retained authority (raising `AttributeError` is acceptable), and the same substituted history must still fail against original A;
5. verify normal initialization, transition, receipt verification, LAB-081 shared-ledger construction, LAB-090 activation fencing, and LAB-092 provenance construction remain compatible.

## Compatibility audit

No source observed requires a legitimate post-construction bootstrap mutation. Constructors pass bootstrap once. Verification reads it; rotation advances durable generation history but does not change the original trust root. Therefore making the attribute read-only matches existing semantic intent rather than removing a supported lifecycle operation.

## Implementation decision for this run

Do not stage the code change yet. Exact repository execution is unavailable in this run because direct git transport fails DNS before checkout. The change is small, but acceptance explicitly requires a regression demonstrating the pre-fix authority failure and downstream LAB-081/LAB-090/LAB-092 gates. Writing only the property refactor without executable regression evidence would weaken the repository's regression-first discipline.

## Exact next implementation action

When exact execution is available:

1. branch from the reconciled lower-layer base that LAB-081/LAB-090/LAB-092 actually inherit;
2. add the failing bootstrap-rebinding/substituted-history regression first;
3. implement private retained `_bootstrap` + read-only `bootstrap` property and switch every trust decision to the private source;
4. run provider-history focused tests, LAB-081 integration tests, LAB-090 focused/downstream tests, LAB-092 focused/downstream tests, and compileall;
5. audit for any remaining writes/reads of a mutable bootstrap authority slot before opening/integrating a PR.
