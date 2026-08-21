# LAB-069 — path-compatible memfd credential transport

Reference experiment for replacing named secret-file fallback with an anonymous sealed Linux `memfd` inherited explicitly by a child and referenced as `/proc/self/fd/N`.

The intended route is `MFD_CLOEXEC` by default, explicit descriptor inheritance for the chosen child, and `F_SEAL_WRITE|F_SEAL_GROW|F_SEAL_SHRINK|F_SEAL_SEAL` after publication. Durable evidence contains only credential identity/generation/scope and a keyed fingerprint.

If memfd or procfd-path compatibility is not observed, the caller must route explicitly to the hardened LAB-068 named-file fallback rather than weakening descriptor or sealing controls.

This removes a persistent directory entry when compatible. It does not claim forensic erasure, that anonymous pages cannot reach swap, or universal `/proc/self/fd` compatibility across tools/namespaces.
