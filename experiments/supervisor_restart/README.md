# Supervisor restart recovery

LAB-032 reference harness. Persist restart-safe identity (`pid`, `/proc` starttime, task and generations), never a pidfd descriptor number. After supervisor restart, re-read identity, reacquire a fresh pidfd, bind its target PID back to the durable record, re-read starttime across the acquisition window, and only then allow consequential continuation.

States: `SAME_INSTANCE`, `EXITED`, `IDENTITY_MISMATCH`, `UNVERIFIABLE`, `GENERATION_DRIFT`.

A fresh pidfd is live authority for the current process instance; PID + starttime is reconstructible identity evidence, not a substitute for the pidfd.
