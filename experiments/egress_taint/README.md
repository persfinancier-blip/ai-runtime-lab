# LAB-021 Egress Taint Prototype

Standard-library Python reference model for sensitive-data label propagation and egress sink gating.

Core rules:
- normal transforms inherit maximum input sensitivity;
- fallback/tool/peer routing cannot lower sensitivity;
- declassification requires trusted-control authority bound to source identity, target, rule, and generation;
- protected egress requires trusted-control authorization bound to exact payload identity, destination, purpose, sensitivity ceiling, and generation;
- redirects, purpose changes, payload changes, and stale grants invalidate approval;
- evidence records store keyed opaque digests/provenance, not sensitive plaintext.

Run corrected tests:
`python -m unittest discover -s experiments/egress_taint/tests -p 'test_policy.py' -v`

Run unsafe seed (expected failure):
`python -m unittest experiments.egress_taint.tests.unsafe_seed_expected_failure`

Non-goals: enterprise DLP, general information-flow typing, secret management, or cryptographic authorization infrastructure.
