# LAB-067 namespace retirement

This first slice models the authority boundary for retiring a superseded namespace generation. A retirement permit is authenticated and binds the predecessor record, successor record, both generations, the successor-verified archive-chain commitment, and policy generation. Destructive cleanup is allowed only after the successor is current, the successor archive chain audits, and the old namespace can be strongly reacquired.

This is not secure erasure, backup retention, remote GC, or cross-host object identity. Real `SignedPrunableHistory` / LAB-063 integration remains a completion gate.
