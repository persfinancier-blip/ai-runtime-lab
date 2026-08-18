# Current Lab State

Last updated: 2026-08-18

## Active objective

Move from composition correctness to transactional correctness. LAB-014 proved that the main correctness primitives compose under an explicit authority order, but also exposed two composition-only defects that individual component tests did not catch. The next highest-value gap is atomic persistence and multi-worker concurrency at the storage boundary.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-014.
- Completed: #26 / LAB-014 cross-layer correctness-kernel composition and invariant stress test.
- LAB-014 PR #27 squash-merged as `f5cb4ccf1e71eb70ace69a14d464e35df68bb7c0`.
- Next: #28 / LAB-015 transactional correctness kernel — READY.
- Active branch/PR for LAB-015: none yet.

## Last completed step

LAB-014 built `experiments/correctness_kernel/` as a thin deterministic composition layer over existing LAB-005/006/007/008/011/012 interfaces, with topology constrained to an optimization input rather than an authority source.

The deliberately unsafe composition trusted advisory narrative memory (`done successfully`) as completion authority; the expected-safety test failed as intended. The corrected matrix initially passed, then remote audit found two composition defects before merge:

1. ledger/verifier semantic-binding gap — a valid ledger ID could be paired with a caller-fabricated verifier-side requirement mapping;
2. restart memory-state gap — the kernel constructed a fresh `MemoryStore` instead of loading persisted quarantine/retraction state.

Both were fixed. Requirement coverage is now committed into authoritative observation digest material and verifier-side semantics are checked against the ledger record; restart uses `MemoryStore.load(...)`.

The final local interface-compatible suite passed 12/12 tests and `python -m compileall -q experiments/correctness_kernel` passed. A direct exact repository clone was attempted but the local container could not resolve `github.com`, so exact-source validation used GitHub connector patch/file inspection. PR #27 was remote-audited, mergeable at the audited HEAD, and squash-merged.

## Evidence produced

- `experiments/correctness_kernel/kernel.py`
- `experiments/correctness_kernel/tests/test_kernel.py`
- `experiments/correctness_kernel/tests/unsafe_seed_expected_failure.py`
- `experiments/correctness_kernel/README.md`
- `research/2026-08-18-cross-layer-correctness-kernel.md`
- Issue #26 closed DONE.
- PR #27 merged: `f5cb4ccf1e71eb70ace69a14d464e35df68bb7c0`.
- New follow-up Issue #28 / LAB-015 created.

## Findings carried forward

- authority order is part of correctness: durable state/memory reconstruction -> reconciliation -> escalation/authority policy -> trusted advisory-memory filter -> capability selection -> topology optimization -> fenced/idempotent execution -> append evidence -> invalidation/supersession resolution -> ledger-bound verifier semantics -> terminal completion;
- authority flows downward; preferences (route score, topology, similarity) cannot flow upward and weaken safety constraints;
- verifier-side semantic views must be bound to authoritative ledger records, not merely share an ID;
- durable safety metadata such as quarantine/retraction must be reconstructed on restart before decisions;
- completion is derived and revocable, not a sticky boolean;
- file-backed semantics still do not prove atomic multi-worker behavior.

## Known blockers / constraints

- No current blocking issue is known.
- Direct container network/DNS to GitHub remained unavailable in the LAB-014 run; use connector-first exact-source audit and treat local network as a per-run capability.
- Open-model serving efficiency remains deferred until representative target hardware/runtime is available; decorative benchmarking remains disallowed.
- SQLite may be used in LAB-015 only as an executable approximation of SQL transaction semantics; do not claim it is equivalent to PostgreSQL or a distributed lease service.

## Exact next action

Select Issue #28 / LAB-015. Research primary-source transaction/concurrency mechanisms, then build `experiments/transactional_kernel/` with explicit SQL schema and transaction boundaries. Seed an unsafe split-transaction/lost-update or invalid-DONE race, observe it fail, then implement atomic claim/fence/generation/evidence/completion semantics. Cover at least the 10 required concurrency/failure scenarios, run deterministic tests and compile/static checks, perform a separate remote patch audit, integrate safely, and update this state.

## Backlog

- #28 / LAB-015 — transactional correctness kernel: atomic persistence, leases and concurrent completion — READY and next.
- Correctness-kernel latency/cost overhead benchmark — candidate after LAB-015 establishes a transactional prototype.
- Open-model serving efficiency — DEFERRED pending representative hardware/runtime.
