# LAB-059 — Transition-evidence integrity and restart history conformance

## Question
After restart, can the authority store prove the complete local bootstrap→head history instead of trusting current head state or persisted evidence narrative?

## Donors
TUF root-update semantics require incremental root evolution: each successor is checked against the predecessor threshold and the successor threshold. The transferable mechanism is re-deriving authority history from exact signed transition material rather than trusting only the latest root.

SQLite provides atomic local transaction recovery, but an internally consistent database is not an external authenticity or anti-rollback guarantee. Whole-file rollback remains delegated to LAB-034–037 external monotonic anchors.

## Protocol
Each winning transition durably stores exact predecessor/successor authority IDs, proposal and transition IDs, canonical signed payload, and every signer ID/signature required by its quorum. On restart, verification begins at the durable bootstrap pair, walks sequence 1..N, reloads historical authorities by content ID, reconstructs payloads, re-verifies threshold signatures, recomputes transition digests, advances the derived authority pair, and finally requires the SQL head to equal the derived terminal pair and sequence.

UNKNOWN reconciliation performs full history verification before returning evidence.

## Failure matrix
Restart, predecessor tamper, successor tamper, signature tamper, missing/gapped transition, head/history mismatch, UNKNOWN-after-commit with later proof corruption, durable proof presence, and an unsafe evidence-trusting baseline.

## Boundary
This establishes local durable-history conformance. It does not detect rollback of the complete database to a previously valid snapshot and does not replace the external monotonic-anchor work from LAB-034–037.
