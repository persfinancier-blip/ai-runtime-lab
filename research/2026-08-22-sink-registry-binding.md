# LAB-075 — authenticated sink adapter/endpoint registry

LAB-074 bound requests to authenticated sink *capabilities* but still trusted a runtime-provided object after comparing only `sink_id`. LAB-075 adds a versioned authenticated registry in the same SQLite authority.

The registry entry binds `sink_id`, generation, stable adapter/profile digest, canonical endpoint origin, operation profile, exact predecessor entry digest, and registry issuer generation. New reservations persist exact entry digest/generation. Registry head and request binding are serialized in the journal database.

Rotation rules are asymmetric by state: CONFIRMED returns the durable receipt without consulting the new adapter; old INTENT cannot execute after rotation; old UNKNOWN may only reconcile through the direct authenticated successor and can never be re-executed. Free-form lineage labels are intentionally rejected because unrelated successors could copy them.

The first implementation attempt exposed a real race: LAB-074 could create an `INTENT` before the registry head was atomically bound, leaving a durable unbound request if rotation won between those steps. The corrected design writes request identity, capability identity, and exact registry entry in one SQL transaction after rechecking both heads.

Non-goals: service discovery, DNS/TLS/proxy policy (LAB-022–025), Python object identity as production code identity, universal exactly-once, distributed registry consensus.
