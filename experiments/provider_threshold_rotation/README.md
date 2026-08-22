# LAB-083 — threshold-authorized asymmetric provider rotation

LAB-082 keeps historical provider verification asymmetric, but its current generation transition still relies on the old provider key plus possession of the proposed new provider key. If the old private key is compromised, an attacker can choose the new key too.

LAB-083 adds an independent durable threshold rotation authority. The supported integration requires:

1. LAB-082 old-provider Ed25519 continuity proof;
2. LAB-082 new-provider possession proof;
3. a threshold proof over the exact provider predecessor/successor plus the current rotation-authority identity/version/generation;
4. one `BEGIN IMMEDIATE` transaction for threshold-proof persistence and provider-head advancement while unresolved PREPARED shared-anchor work is excluded.

Historical LAB-082 transitions that predate LAB-083 remain verification-only behind an explicit threshold start boundary; they are not retroactively promoted to threshold-authorized transitions.

This is local compromise containment, not HSM/KMS custody, remote ceremony orchestration, or distributed consensus.
