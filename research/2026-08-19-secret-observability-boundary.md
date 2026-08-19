# Secret-material observability, redaction, and evidence-boundary conformance

Date: 2026-08-19  
Issue: #50 / LAB-026  
Branch: `lab/026-secret-observability`

## Question
How can credential-bearing runtime state remain debuggable and auditable without allowing raw credential bytes to enter logs, traces, exceptions, evidence records, or replay snapshots?

## Primary-source donors

### OpenTelemetry sensitive-data guidance
OpenTelemetry explicitly treats authentication credentials and session tokens as sensitive telemetry and recommends data minimization plus removal/redaction/transform processors. Transferable mechanism: observability is not a trusted sink by default; collection needs an explicit minimizing/redacting policy boundary.

Sources:
- https://opentelemetry.io/docs/security/handling-sensitive-data/
- https://opentelemetry.io/docs/specs/otel/logs/supplementary-guidelines/
- https://opentelemetry.io/docs/specs/semconv/url/

### OpenTelemetry logs/exceptions model
Exception data may be recorded in structured log attributes, which means exception strings are a first-class leakage path, not an edge case. Transferable mechanism: sanitize exception content before durable emission, not only HTTP header maps.

Source:
- https://opentelemetry.io/docs/specs/otel/logs/data-model/

### RFC 6750 bearer-token security
RFC 6750 identifies token disclosure as a primary threat and explicitly warns that tokens can leak through browser history, web-server logs, and other unsecured locations. Transferable mechanism: bearer-token bytes must never be treated as ordinary diagnostic material.

Source:
- https://www.rfc-editor.org/rfc/rfc6750

## Protocol
A single `SecretBoundary` owns durable observability emission. It:
1. recursively sanitizes structured payloads;
2. canonicalizes case/underscore variants of known secret-bearing field names;
3. sanitizes exceptions before recording;
4. scans free text for registered secret values and bearer/basic credential patterns;
5. exposes stable public credential identity (`credential_id`, scope, kind, generation) instead of credential bytes;
6. uses keyed HMAC when correlation to secret material is required, avoiding raw low-entropy SHA-256 oracle behavior;
7. sanitizes again at serialization as a second sink boundary.

## Unsafe baseline
`UnsafeRecorder` JSON-serializes request/exception state directly. The seeded test proves the raw Authorization value survives durable serialization.

## Audit defect found and fixed
The first corrected implementation normalized incoming field names by replacing `_` with `-`, but the sensitive-key set still contained mixed underscore and dash forms. `API_KEY` therefore became `api-key` and escaped field-name redaction. The matrix caught the defect; the sensitive-key vocabulary was canonicalized and the entire suite was rerun.

## Observed local validation
- corrected deterministic suite: 13/13 passed;
- `python -m compileall -q .`: passed;
- unsafe serializer retains secret bytes by construction and is tested as the falsified baseline.

Covered cases include Authorization across log/trace/evidence/replay channels; Cookie and Proxy-Authorization separation; exceptions; nested structures; case variants; keyed identity versus raw hash; credential rotation; UNKNOWN/retry evidence; serialization-time re-sanitization; unregistered bearer-pattern detection; and preservation of non-secret route/method/status fields.

## Boundary with earlier LABs
- LAB-007 evidence identity remains append-only provenance; secret observability records may reference evidence but may not put raw credentials into it.
- LAB-021/LAB-022 payload/egress permits remain authoritative for disclosure; redaction does not create permission to disclose data.
- LAB-025 credential scope determines which credential may be used on a route; LAB-026 determines what representation of that credential may enter observability.

## Non-goals and limits
- This is not a secret manager, SIEM, tracing backend, or regex-complete DLP system.
- Pattern redaction cannot discover arbitrary unknown secrets; known secret-bearing structures should be labeled upstream and registered values are scrubbed as a defense in depth.
- The HMAC audit key must itself remain secret and out of observability; production deployments should keep it in an appropriate secret/KMS boundary.

## Decision
Treat logs, traces, exceptions, evidence and replay snapshots as durable egress sinks. All such outputs must cross one fail-closed sanitization boundary. Preserve only non-secret credential identity/scope/generation and keyed correlation material; never persist raw credential bytes or raw low-entropy secret hashes.
