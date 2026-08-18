# Verification Harness

A minimal deterministic completion verifier for LAB-006.

The harness separates three things:

- `Task`: requirements plus the exact artifact digest being judged.
- `Evidence`: an observed result bound to an artifact digest and the requirements it supports.
- `Claim`: the completion assertion and the evidence IDs it relies on.

The verifier never treats agent narrative as proof. Acceptance requires complete requirement coverage, resolvable evidence references, evidence bound to the current artifact, and at least one observed passing test.

Run:

```bash
python -m unittest discover -s experiments/verification_harness/tests -p 'test_*.py' -v
```

The seeded trajectories cover valid completion, an unexecuted test, an observed failing test, stale evidence, partial completion, a fabricated evidence reference, and mutation of a previously verified artifact.

## Boundary

This is a verification-contract experiment, not a claim that all software correctness is decidable. A passing test only proves what that test actually checks. The harness establishes freshness, observation, linkage, coverage and deterministic policy; semantic adequacy of requirements/tests remains a separate concern.
