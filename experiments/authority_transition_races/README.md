# LAB-058 authority-transition races

Corrected suite:

`python -m unittest experiments.authority_transition_races.tests.test_protocol -v`

Unsafe seed (expected failure):

`python -m unittest experiments.authority_transition_races.tests.unsafe_race_expected_failure.U.test_expected_failure -v`

The reference store uses SQLite `BEGIN IMMEDIATE` plus an exact predecessor `(root_id, recovery_id, sequence)` CAS. It models local serialization only, not distributed consensus.
