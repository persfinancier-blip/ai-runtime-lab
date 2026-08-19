# Child Sandbox Authority Prototype

Deterministic policy model for LAB-028. It does not claim kernel isolation.

A permit is bound to task ID, sandbox generation, credential generation, and a fingerprint of filesystem/exec/FD/socket/network capabilities. HOME/config is not ambiently allowed; local sockets and network are distinct.

Run corrected tests:
`python -m unittest discover -s experiments/child_sandbox/tests -p 'test_protocol.py' -v`

The unsafe seed is intentionally outside that pattern and must fail.
