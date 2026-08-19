# Transport Endpoint Binding Reference Harness

Deterministic fake resolver/redirector/connector prototype for LAB-023. No real network is used.

## Core rule

Authorization of a canonical HTTPS URL is not authorization of whichever endpoint DNS or redirects happen to produce later. The executor preserves LAB-022 request/effect identity, validates endpoint class on every resolution, re-resolves immediately before connect, pins the actual connection to the just-validated IP, and reconciles an `UNKNOWN` outcome by the existing effect identity rather than silently resolving again.

Cross-host redirects require new authorization. Same-host redirects are revalidated and each resolution must contain only allowed public endpoints.

## Run

```bash
python -m unittest discover -s experiments/transport_binding/tests -p 'test_protocol.py' -v
python -m compileall -q experiments
```

The deliberately unsafe baseline is outside normal discovery:

```bash
python -m unittest experiments.transport_binding.tests.unsafe_seed_expected_failure
```

It is expected to fail because a resolve-once/check-then-connect design allows a hostname that was initially public to rebind to loopback before the connection.

## Non-goals

This is not a DNSSEC resolver, HTTP client, proxy, TLS implementation, service mesh, or network sandbox. Production code must additionally ensure TLS certificate/SNI validation applies to the original authorized hostname while the socket connects to the validated pinned endpoint.
