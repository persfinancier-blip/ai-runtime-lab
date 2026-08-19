# CT v2 consistency-proof wire experiment

Strict standard-library reference for RFC 9162 `TransItem<consistency_proof_v2>`.

It encodes/decodes the TLS 1.3 presentation-language structure, rejects malformed or ambiguous input, binds `LogID` and both tree sizes to witnessed checkpoints, then delegates compact Merkle verification to LAB-041.

The experiment intentionally does not implement CT HTTP APIs, STH signatures, witness quorum, or log discovery.
