# LAB-086 — asymmetric historical break-glass proof migration

The first slice establishes an authenticated cutoff between legacy HMAC recovery history and new Ed25519 threshold proofs. Legacy rows remain legacy; they are committed by a threshold-signed boundary rather than copied into the asymmetric proof table. New proofs bind exact sequence, predecessor root, successor root, recovery authority content ID/version/generation. Durable history stores only public Ed25519 keys and signed proof bytes; private signing capability is runtime-only.

Authority rotation uses old+new thresholds and preserves old public keys strictly for verification. Invalid/duplicate/malformed signature noise cannot inflate quorum or consume a later valid signer.

Next integration step is to map the cutoff and proof rows onto the actual LAB-084/LAB-085 SQL schema and one-transaction serialization boundary rather than treating this reference store as a second authority.
