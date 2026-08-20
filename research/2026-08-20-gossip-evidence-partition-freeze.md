# Gossip evidence durability and partition/freeze classification

Date: 2026-08-20  
Issue: #101 / LAB-053  
Branch: `lab/053-gossip-evidence`

## Question

What can a durable gossip/evidence layer actually conclude when authenticated replica views are delayed, missing, stale, selectively frozen, or divergent?

## Donor mechanisms

### RFC 9162 — asynchronous audit and split-view boundary

RFC 9162 makes log checking asynchronous specifically because network connectivity and firewalls can delay audit. It also states that inconsistent views presented to different clients can circumvent ordinary log auditing. Transferable rule: **non-delivery is not itself cryptographic evidence of equivocation**; split-view attribution requires incompatible authenticated views to meet a comparison path.

Primary source: https://www.rfc-editor.org/rfc/rfc9162.html

### TUF — freeze is authenticated staleness, not silence

The TUF specification treats indefinite freeze/rollback as use of older authenticated metadata beyond freshness/version expectations. It also notes that an attacker who can intercept traffic can always cause denial of service. Transferable rule: distinguish availability uncertainty from affirmative stale authenticated state.

Primary source: https://github.com/theupdateframework/specification/blob/master/tuf-spec.md

### transparency-dev witness / C2SP tlog-witness

A witness stores its latest verified checkpoint and only advances when a consistency proof demonstrates append-only evolution. The witness protocol therefore gives a production example of durable last-seen state plus authenticated forward progress, without claiming that request timeout proves a malicious fork.

Primary sources:
- https://github.com/transparency-dev/witness
- https://c2sp.org/tlog-witness@v1.0.0-rc.1

## Protocol model

Each peer emits a signed view containing the LAB-052-compatible identity material needed for comparison: peer identity plus ordered authenticated event IDs. Each observer turns a verified peer view into an observer-signed durable observation containing view identity and trusted receipt time.

The tracker classifies:

- `CURRENT` — a sufficiently fresh authenticated view is present;
- `UNKNOWN_PARTITIONED` — no sufficiently fresh exchange is available; no accusation is inferred from silence;
- `FREEZE_SUSPECTED` — a peer serves an older authenticated prefix after a different observer had already supplied a newer same-lineage view;
- `SPLIT_VIEW` — two authenticated histories for the same peer are incomparable.

A replay of the same signed view at a later transport attempt does **not** refresh its freshness timestamp. Historical freeze/split attribution remains after ordinary freshness expiry.

## Failure injection

Unsafe seed: timeout is mapped directly to `SPLIT_VIEW`.

Observed result: the unsafe test fails because absence of a response is incorrectly converted into affirmative equivocation evidence.

Corrected local validation:

```text
13 tests passed
python -m compileall -q experiments/ctv2_bundle_gossip_evidence
```

Covered cases:

1. timely authenticated exchange;
2. missing exchange -> `UNKNOWN_PARTITIONED`;
3. silence after a previously fresh view expires to unknown;
4. older prefix served after independently observed newer view -> `FREEZE_SUSPECTED`;
5. ordinary old-before-new history is not freeze;
6. incomparable authenticated histories -> `SPLIT_VIEW`;
7. duplicate/replay does not refresh freshness;
8. restart preserves signed observations and derived incident history;
9. trusted-clock rollback fails closed;
10. selective freeze across observers is detected after evidence crosses the aggregator;
11. evidence freshness expiry does not erase historical attribution;
12. tampered durable observation is rejected;
13. forged persisted incident labels are ignored because incidents are re-derived from verified observations.

## Audit finding and correction

The first corrected implementation persisted incident labels and then trusted those labels during classification. That allowed storage corruption to manufacture a `SPLIT_VIEW` accusation even when the underlying signed observations did not support it.

The final implementation treats incident labels as a cache only. Before consequential classification it verifies observer-signed observations and deterministically rebuilds incidents from those observations. A regression test injects a forged persisted `SPLIT_VIEW` record and confirms the peer remains `CURRENT`.

## Epistemic limits

- Silence, timeout, packet loss, and partition do not prove malicious behavior.
- `FREEZE_SUSPECTED` is stronger than staleness but weaker than cryptographic split view: it depends on authenticated newer evidence being known before a later stale presentation.
- `SPLIT_VIEW` requires incompatible authenticated histories.
- This experiment uses a trusted monotonic receipt clock in one durable aggregator. It does **not** prove that clocks across independent observers are synchronized or honest.
- Observer signatures authenticate who made an observation, not the truth of a malicious observer's claimed time.
- Durable JSON storage is reference persistence, not rollback-resistant trusted storage; earlier LABs cover stronger rollback anchors.
- The prototype does not provide reliable delivery, Byzantine consensus, leader election, or fork prevention.

## Integration implication

Use gossip evidence as an epistemic layer over LAB-052 authenticated histories:

`authenticated peer view -> durable observer evidence -> freshness/causal comparison -> classification`

Never let network timeout jump directly to `SPLIT_VIEW`. Never let a persisted narrative incident outrank its signed observations.

## Next gap

The remaining correctness gap is cross-observer ordering/credibility. A distributed system should not infer freeze from unauthenticated wall-clock ordering across observers. The next experiment should replace that assumption with authenticated causal exchange/sequence evidence and require sufficient independent observer evidence before consequential freeze attribution.
