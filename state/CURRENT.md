# Current Lab State

Last updated: 2026-08-22

## Active objective

LAB-075 — remove the remaining trusted `sink_id -> runtime adapter/endpoint` mapping behind LAB-074 by binding each new broker reservation to an authenticated/versioned registry entry and enforcing safe rotation/reconciliation semantics.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-074.
- Active: Issue #141 / LAB-075 — IN_PROGRESS.
- Active branch: `lab/075-sink-registry-binding-v2`.
- PR: none. Normal draft PR creation was attempted in this run and blocked by an external safety-status gate before execution.

## Last completed step

Implemented and published the first executable LAB-075 slice. Registry entries bind `sink_id`, registry generation, stable adapter/profile digest, canonical endpoint origin, operation profile, exact predecessor entry digest and registry issuer generation. Registry entries/heads and request bindings live in the same SQLite journal authority.

The first wrapper implementation failed its concurrency test because LAB-074 could commit an `INTENT` before the registry entry was bound; a concurrent registry rotation could therefore leave a durable request with NULL registry identity. The corrected design inserts request identity + LAB-074 capability identity + exact LAB-075 registry identity in one SQL transaction after rechecking both capability and registry heads.

A separate remote audit then found three more cross-layer conditions: a pre-existing content-address registry row must be reread before head activation; terminal CONFIRMED must be receipt-only and not depend on new registry/capability input; historical UNKNOWN reconciliation must require the current capability to authorize `reconcile_by_key`. These corrections are published in `audit_fixes.py` with regressions.

## Evidence produced

- `experiments/sink_registry_binding/protocol.py`
- `experiments/sink_registry_binding/tests/test_protocol.py`
- `experiments/sink_registry_binding/tests/unsafe_string_only_expected_failure.py`
- `experiments/sink_registry_binding/audit_fixes.py`
- `experiments/sink_registry_binding/tests/test_audit_fixes.py`
- `experiments/sink_registry_binding/README.md`
- `research/2026-08-22-sink-registry-binding.md`
- Local interface-compatible main matrix: 14/14 passed.
- Audit-fix suite plus inherited matrix: 30/30 passed.
- Unsafe string-only baseline: failed as expected because attacker adapter executed one side effect.
- Compileall: passed. Python startup emits an unrelated artifact-tool warmup timeout but unittest/compileall exit statuses are authoritative.
- Published initial protocol blob before audit overlay: `0e2671d4c14681267d25ff7aea9afeafbb976621`.
- PR creation attempt blocked before execution; no PR exists.

## Known blockers / constraints

- No owner/product blocker.
- Direct GitHub clone is unavailable in this runtime due DNS; connector remains the durable read/write path.
- Branch is based on the prior main commit and is one state-only commit behind current main; all LAB-075 paths are new.
- `audit_fixes.py` currently overlays corrections rather than consolidating them into the primary protocol surface. Do not merge this branch until that is resolved.
- Interface-compatible local tests are not a substitute for exact execution against the real merged LAB-074 `CapabilityBoundJournal` and `TransactionalJournal`.
- LAB-075 must reuse LAB-022–025 transport/destination enforcement; stable adapter digest is a reference profile identity, not a claim that Python object identity is production code identity.

## Exact next action

Resume Issue #141 on `lab/075-sink-registry-binding-v2`. First consolidate the `audit_fixes.py` corrections into the supported LAB-075 protocol surface (or make the corrected classes the only documented/exported surface) without weakening the 14-case matrix. Then reconstruct exact merged LAB-074/LAB-073/LAB-072 executable sources through the GitHub connector, run LAB-075 against the real `CapabilityBoundJournal`/`TransactionalJournal`, run LAB-074/LAB-073/LAB-072 regressions and compileall, and perform a fresh remote patch audit. If all gates are clean, retry normal draft PR creation; if that endpoint is still blocked before execution, keep work on the branch and use only the documented safe integration fallback after exact conflict/audit checks.

## Backlog

- #141 / LAB-075 — authenticated sink-adapter and endpoint registry binding — IN_PROGRESS.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
