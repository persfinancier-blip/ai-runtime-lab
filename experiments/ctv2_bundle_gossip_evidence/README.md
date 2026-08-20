# LAB-053 Gossip Evidence Reference Prototype

Durable authenticated exchange observations on LAB-052-style replica/head histories.

- `CURRENT`: fresh authenticated view.
- `UNKNOWN_PARTITIONED`: no sufficiently fresh exchange; silence is not proof of malice.
- `FREEZE_SUSPECTED`: an older authenticated prefix is served after a different observer already saw a newer same-lineage view.
- `SPLIT_VIEW`: authenticated incomparable histories.

Duplicate replay does not refresh freshness. Observer evidence survives restart and is authenticated. Trusted-clock rollback fails closed. Historical incidents remain attributable after freshness expiry.

Not a production gossip transport, Byzantine consensus protocol, or fork-prevention mechanism.
