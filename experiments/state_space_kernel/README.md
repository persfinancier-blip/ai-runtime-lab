# LAB-017 state-space kernel

Storage-independent standard-library Python model for bounded correctness exploration.

Run: `python -m unittest experiments.state_space_kernel.test_model -v`.

Configured exhaustive bound: depth 8 over ten actions. Correct model explored 314 queued states with no invariant violation. Seeded supplement: seed 17017, 1000 schedules x 20 steps.

Automatically rediscovered counterexamples:
- `split_unsafe`: `intent -> effect_ok -> append_evidence -> invalidate -> complete` => `done_without_current_evidence`.
- `reopen_unsafe`: `intent -> effect_ok -> append_evidence -> complete -> duplicate` => `terminal_reopened`.
- `stale_unsafe`: `claim -> intent -> effect_ok -> stale_mutate` => `duplicate_effect`.

During implementation audit the model itself exposed an over-permissive transition: it initially allowed a second effect action from `CONFIRMED`, which could erase confirmation. The corrected transition only permits effect execution from `INTENT` or `UNKNOWN`.

This is bounded verification, not a universal proof. It intentionally abstracts storage, timing, network, and unbounded identities.
