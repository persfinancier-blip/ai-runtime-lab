# TLS Origin + Proxy Path Binding Prototype

Deterministic standard-library harness for LAB-024. It models the identities a real HTTPS/proxy adapter must prove before committing an external effect.

A safe transport binds LAB-022 request identity, LAB-023 validated endpoint, TLS SNI/certificate DNS-ID, direct-vs-proxy route, proxy identity/policy generation, CONNECT authority, proxy-side target resolution and UNKNOWN reconciliation to one stable effect identity.

Run corrected tests:

```bash
python -m unittest discover -s experiments/tls_proxy_binding/tests -p 'test_protocol.py' -v
python -m compileall -q experiments/tls_proxy_binding
```

Unsafe seeds are excluded from passing discovery and are expected to fail:

```bash
python -m unittest experiments.tls_proxy_binding.tests.unsafe_seed_expected_failure -v
```

Non-goals: no real TLS/CA validation, sockets, production proxy, kernel egress policy or claim that the fake harness proves any specific HTTP client configuration.