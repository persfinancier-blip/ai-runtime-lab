# Append-only evidence ledger — donor synthesis

Date: 2026-08-18 · Issue #12 / LAB-007

## Donors and transferable mechanisms

### in-toto Attestation Framework
The v1 Statement binds metadata to immutable subjects by digest and identifies predicate semantics with `predicateType`. Test Result and Simple Verification Result predicates reinforce artifact-bound observations and explicit verifier identity/policy context. Transfer: evidence must identify exact subject/artifact, evidence type/schema, producer/verifier, and result; verifier output is a separate derived assertion rather than mutation of source evidence.

Primary sources:
- https://github.com/in-toto/attestation/blob/main/spec/v1/statement.md
- https://github.com/in-toto/attestation/blob/main/spec/predicates/test-result.md
- https://github.com/in-toto/attestation/blob/main/spec/predicates/svr.md

### Apache Kafka log
Kafka's log is serially appended, records have stable offsets, and startup recovery validates newest log entries for corruption. Transfer: use append-only ordered records and recover by validating history; invalidation/supersession should be later events rather than edits. We do not copy Kafka's distributed broker/replication machinery.

Primary source: https://kafka.apache.org/42/implementation/log/

### Git content-addressed objects
Git is fundamentally a content-addressable store: content maps to an identity key and immutable objects are retrieved by that identity. Transfer: canonical evidence bodies get deterministic content IDs; sequence/location is separate from semantic identity.

Primary source: https://git-scm.com/book/en/v2/Git-Internals-Git-Objects.html

## Protocol decision
Use both identities: a SHA-256 content ID for semantic evidence identity/idempotency and a monotonic sequence plus previous-record link for ledger position/history. Artifact digest is part of an observation, so evidence for an old artifact fails freshness checks after mutation.

Observation records are immutable. Invalidation and supersession are new records. A verifier resolves evidence IDs, rejects dangling/stale/invalidated/superseded observations, and requires an independently trusted observer before accepting a PASS observation.

## Trust boundary
A content hash proves integrity/identity relative to bytes, not truth. A worker can hash a lie. The reference prototype therefore separates producer assertion from trusted observation. The boolean is deliberately only a model of the boundary; production needs authenticated producer identity/attestation or a trusted execution/verifier service. A hash chain detects local mutation only when its head/checkpoint is itself trusted externally.

## Experiment
`experiments/evidence_ledger/` implements canonical JSON records, SHA-256 content IDs, JSONL append/reload, sequence/hash chaining, duplicate suppression, invalidation/supersession, and verifier resolution.

Observed local validation on 2026-08-18: 9 deterministic tests passed covering restart/reload, duplicate/idempotency, mutation/tamper, stale artifact, dangling reference, invalidation, supersession, untrusted worker assertion, and valid current evidence.

## LAB-005 / LAB-006 integration
LAB-005 terminal state should reference a verifier verdict/evidence IDs, not embed mutable worker prose. `DONE` should require a current accepted verifier decision for the intended artifact/work identity. LAB-006's in-memory evidence model can be replaced by resolver calls into this ledger while preserving the rule that completion is a verifier decision.

## Limits / non-goals
This is not a replicated log, database, transparency service, timestamp authority, PKI, or Byzantine-secure ledger. It does not make a dishonest producer trustworthy and does not prevent full-history rewrite without an externally trusted head/signature. Those concerns are deliberately outside LAB-007.
