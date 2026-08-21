# LAB-066 — Restart namespace reacquisition

## First slice
A restart loses LAB-065's held directory FD, so a pathname alone cannot recreate authority. The reference record is authenticated and generation-bound. Linux opaque handle evidence is captured when `name_to_handle_at` supports the filesystem; the current pathname is reauthorized without following symlinks and its handle is compared to the durable record. `st_dev/st_ino` and mount IDs are observations only, not universal persistent identities.

The current runtime can capture handles but cannot prove `open_by_handle_at` because `CAP_DAC_READ_SEARCH` is absent. Therefore a missing/renamed directory with saved handle is classified `UNSUPPORTED_STRONG_REACQUISITION`, never silently rebound by path or bytes. Intentional relocation requires an authenticated migration permit and increments namespace generation.

This slice intentionally stops before wiring the record into real SignedPrunableHistory/LAB-063; that integration is the remaining acceptance gate.
