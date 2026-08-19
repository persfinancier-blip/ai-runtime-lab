# Witnessed Transparency Checkpoints and Split-View Detection

Date: 2026-08-19  
Issue: #76 / LAB-040  
Branch: `lab/040-transparency-witness`

## Question

How can the lab make authority-history equivocation observable across independently served views without pretending that a witness layer is a consensus protocol?

## Primary-source donors

### RFC 9162 — Certificate Transparency v2

Primary source: https://www.rfc-editor.org/rfc/rfc9162.html

Transferable mechanisms:

- each signed tree head/checkpoint commits to a specific tree size and Merkle root;
- append-only evolution is checked with a consistency proof between older and newer tree states;
- auditors should check append-only behavior and the consistency of the log view presented to different query sources;
- when views differ, comparing signed tree heads gives cryptographic evidence of log misbehavior, but sharing/comparing views is an ecosystem requirement outside one isolated client.

Implication: a locally valid signed checkpoint is not sufficient. The verifier needs continuity from a previously trusted/witnessed checkpoint and some path for independently obtained views to meet.

### transparency-dev Witness

Primary source: https://github.com/transparency-dev/witness

Transferable mechanisms:

- a witness keeps one durable checkpoint per log;
- it obtains a new checkpoint plus consistency proof from the prior state;
- it updates only after append-only verification;
- it countersigns the accepted checkpoint;
- multiple signatures can coexist on the same checkpoint, enabling policies based on independently identified witnesses.

Implication: durable witness watermarks turn replay/fork checks into cross-run invariants. Witness identity must be unique in quorum counting.

### Trillian transparent logging

Primary sources:

- https://github.com/google/trillian/blob/master/docs/TransparentLogging.md
- https://github.com/google/trillian

Transferable mechanisms:

- append-only Merkle logs expose inclusion and consistency proofs;
- signed tree heads/log roots summarize a concrete tree state;
- transparency depends on a broader monitor/auditor ecosystem rather than the storage engine alone.

Implication: the correctness kernel should keep the log commitment, the consistency verifier, and the observer/witness ecosystem as distinct responsibilities.

## Reference protocol

The prototype under `experiments/anchor_transparency_witness/` uses:

- versioned checkpoint `{schema_version, log_id, size, root_hash, sequence, signature}`;
- RFC-style Merkle tree hashing with domain-separated leaf/node prefixes and largest-power-of-two tree decomposition;
- a deterministic, self-contained reference consistency proof containing prior and appended leaf material. This is intentionally larger than RFC 9162's compact Merkle consistency proof, but it proves the same bounded append-only property without hiding proof machinery;
- a durable witness store containing the last accepted checkpoint plus trusted local `accepted_at` observation time;
- witness countersignatures bound to exact checkpoint identity;
- a threshold policy over distinct witness identities;
- a separate observer that detects conflicting roots for the same `(log_id, size)` once independently obtained views are compared.

HMAC is reference-only deterministic cryptography, as in earlier lab experiments. Production signing keys must remain outside verifier state.

## Failure matrix

Observed corrected suite: **14/14 deterministic tests passed**.

Covered cases:

1. linear history with valid extension -> accepted;
2. same-size/different-root -> split view detected;
3. larger checkpoint without consistency proof -> rejected;
4. explicit proof with wrong appended material -> rejected;
5. stale duplicate checkpoint -> surfaced as stale;
6. older checkpoint after witness advancement -> replay rejected;
7. fork after common predecessor -> conflict detected once one witness sees both;
8. separate witnesses TOFU different forks -> observer detects conflict when views meet;
9. witness restart preserves watermark;
10. witness restart can verify next extension using self-contained proof;
11. threshold policy accepts distinct witness quorum;
12. duplicate witness identity is not double-counted;
13. local freshness window surfaces a frozen view as `STALE`;
14. structural boolean schema version is rejected instead of passing Python numeric equality.

Unsafe baseline: a client that verifies only the log's self-presented checkpoint signature accepts **both** signed forks. The expected-failure test observes `2 != 1`.

`python -m compileall -q experiments` also passed.

## Audit findings and corrections

### 1. Simplified pairwise Merkle tree was too implementation-specific

The first draft paired adjacent nodes and promoted an odd node directly. That was adequate for a toy commitment but not close enough to RFC transparency semantics. It was replaced with RFC-style recursive tree decomposition using the largest power of two smaller than the tree size.

### 2. A single witness did not model independently isolated views

The first suite only demonstrated a witness observing both forks. A separate `CheckpointObserver` was added so two witnesses can independently TOFU different forks and the conflict becomes observable when their checkpoints are later compared.

### 3. Restart verification originally depended on caller-held prior leaves

The first reference proof required an external `previous_leaves` argument. The proof was made self-contained so a restarted witness needs only its durable checkpoint plus the supplied consistency evidence. This remains a deliberately non-succinct reference proof.

### 4. Duplicate witness signatures should not be a denial-of-service primitive

The first threshold policy raised on a repeated witness identity. It now ignores repeated identities for counting: duplicates cannot increase quorum, but redundant input does not invalidate an otherwise sufficient distinct quorum.

### 5. Structural validation must not trust Python numeric equality

The audit added strict integer/nonnegative checks for schema/size/sequence and root-hash structure. This closes the `True == 1` edge case seen elsewhere in the lab.

### 6. Freeze is not the same as cryptographic replay

A cryptographically older checkpoint can be rejected against a durable watermark. A log that simply stops advancing cannot be proven malicious from a Merkle root alone. The harness therefore exposes freshness relative to a trusted local observation clock and explicit maximum-age policy. `STALE` is a policy observation, not signed proof of operator equivocation.

## Guarantee boundaries

### Proven in the bounded reference model

- local append-only continuity from a durable witnessed checkpoint;
- replay rejection against a durable witness watermark;
- detection of same-size conflicting roots after evidence meets;
- distinct-witness quorum counting over exact checkpoint identity;
- restart persistence of witness state;
- explicit freshness status relative to trusted local observation time.

### Not proven / intentionally out of scope

- preventing an operator from maintaining isolated forks before witness/gossip evidence crosses trust domains;
- Byzantine consensus or a globally unique history across disconnected parties;
- availability of honest independent witnesses;
- network-level gossip/distribution reliability;
- RFC 9162 compact proof interoperability (the reference proof is intentionally explicit, not wire-compatible);
- monotonic rollback protection of the witness store itself, which remains governed by LAB-034/035-style external-anchor assumptions.

The correct statement is therefore: **witnesses make split views detectable after independent evidence is compared; they do not by themselves prevent a malicious operator from presenting isolated views.**

## Integration implication

Authority activation from LAB-039 should publish a stable checkpoint identity into a transparency log. Consumers that require global observability should accept a checkpoint only under a configured distinct-witness policy and retain a durable witness watermark. The local transactional single-successor guarantee and the transparency split-view detection guarantee remain separate layers.

## Stop-condition assessment

RFC 9162 plus two production-oriented transparency sources were compared; bounded fork, stale, replay, restart and multi-witness scenarios are covered; unsafe self-presented-checkpoint behavior is reproduced; and the model explicitly separates detection from prevention/consensus. LAB-040 can stop after repository audit/integration.
