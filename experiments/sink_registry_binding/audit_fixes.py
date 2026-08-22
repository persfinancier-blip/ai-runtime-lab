from __future__ import annotations

from experiments.sink_registry_binding import protocol as base


class CorrectedRegistryBoundJournal(base.RegistryBoundJournal):
    """Audited LAB-075 journal surface.

    Registry row validation and head activation intentionally occur in one
    ``BEGIN IMMEDIATE`` transaction. A content-addressed row must never be
    checked in one snapshot and activated in a later snapshot.
    """

    def _capability_fields(self, capability, *, now):
        # The base prototype retains a dict compatibility path for historical
        # interface tests. The audited/supported surface must never convert an
        # unauthenticated structural claim into execution or reconciliation
        # authority. Terminal CONFIRMED reads return before this gate.
        if not (hasattr(capability, "claim") and hasattr(capability, "attestation")):
            raise base.RegistryBindingError(
                "authenticated sink capability attestation required"
            )
        return super()._capability_fields(capability, now=now)

    def observe(self, entry):
        entry = self.authority.verify(entry)
        entry_digest = entry.entry_digest
        q = self.journal._con()
        try:
            q.execute("BEGIN IMMEDIATE")

            row = q.execute(
                "SELECT entry_digest,sink_id,generation,adapter_digest,endpoint_origin,"
                "operation_profile,predecessor_entry_digest,issuer_id,issuer_generation,signature "
                "FROM sink_registry_entries WHERE entry_digest=?",
                (entry_digest,),
            ).fetchone()
            if row is not None:
                stored = self._row_entry(row)
                self.authority.verify(stored)
                if stored != entry:
                    raise base.RegistrySubstitution(
                        "stored entry differs from authenticated candidate"
                    )

            head = q.execute(
                "SELECT entry_digest,generation FROM sink_registry_heads WHERE sink_id=?",
                (entry.sink_id,),
            ).fetchone()
            if head is None:
                if entry.generation != 1 or entry.predecessor_entry_digest is not None:
                    raise base.RegistryRollback("invalid bootstrap")
            else:
                if entry.generation < head[1]:
                    raise base.RegistryRollback("registry generation rollback")
                if entry.generation == head[1]:
                    if entry_digest != head[0]:
                        raise base.RegistrySubstitution(
                            "same-generation registry substitution"
                        )
                    q.commit()
                    return entry
                if (
                    entry.generation != head[1] + 1
                    or entry.predecessor_entry_digest != head[0]
                ):
                    raise base.RegistryRollback(
                        "successor must name exact current predecessor"
                    )

            if row is None:
                q.execute(
                    "INSERT INTO sink_registry_entries VALUES(?,?,?,?,?,?,?,?,?,?)",
                    (
                        entry_digest,
                        entry.sink_id,
                        entry.generation,
                        entry.adapter_digest,
                        entry.endpoint_origin,
                        entry.operation_profile,
                        entry.predecessor_entry_digest,
                        entry.issuer_id,
                        entry.issuer_generation,
                        entry.signature,
                    ),
                )

            stored = self._load_entry(q, entry_digest)
            self.authority.verify(stored)
            if stored != entry:
                raise base.RegistrySubstitution(
                    "authoritative registry row differs before head activation"
                )

            if head is None:
                q.execute(
                    "INSERT INTO sink_registry_heads VALUES(?,?,?)",
                    (entry.sink_id, entry_digest, entry.generation),
                )
            else:
                changed = q.execute(
                    "UPDATE sink_registry_heads SET entry_digest=?,generation=? "
                    "WHERE sink_id=? AND entry_digest=? AND generation=?",
                    (
                        entry_digest,
                        entry.generation,
                        entry.sink_id,
                        head[0],
                        head[1],
                    ),
                ).rowcount
                if changed != 1:
                    raise base.RegistryRollback(
                        "registry head changed before activation"
                    )
            q.commit()
            return entry
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def reserve(self, request, capability, entry, *, now):
        q = self.journal._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            columns = {r[1] for r in q.execute("PRAGMA table_info(broker_requests)")}
            has_digest = "request_digest" in columns
            prefix = "request_digest," if has_digest else ""
            row = q.execute(
                f"SELECT {prefix}status,receipt,effect_key,registry_entry_digest,"
                "registry_generation,capability_sink_id FROM broker_requests WHERE request_id=?",
                (request.request_id,),
            ).fetchone()
            if row is not None:
                off = 1 if has_digest else 0
                if has_digest and row[0] != request.digest:
                    raise base.RegistryBindingError(
                        "request_id reused with different content"
                    )
                if row[off] == "CONFIRMED":
                    receipt = row[off + 1]
                    if not isinstance(receipt, str) or not receipt:
                        raise base.CorruptRegistry("confirmed record missing receipt")
                    entry_digest = row[off + 3]
                    generation = row[off + 4]
                    sink_id = row[off + 5]
                    if entry_digest is None or type(generation) is not int or not sink_id:
                        raise base.CorruptRegistry(
                            "confirmed record lacks registry identity"
                        )
                    historical_entry = self._load_entry(q, entry_digest)
                    self.authority.verify(historical_entry)
                    if (
                        historical_entry.sink_id != sink_id
                        or historical_entry.generation != generation
                    ):
                        raise base.CorruptRegistry(
                            "confirmed record registry identity mismatch"
                        )
                    capplan = (
                        self.bound._load_binding(q, request.request_id)
                        if hasattr(self.bound, "_load_binding")
                        else type(
                            "CapPlan",
                            (),
                            {"sink_id": sink_id, "effect_key": row[off + 2]},
                        )()
                    )
                    rplan = base.DurableRegistryPlan(
                        sink_id, entry_digest, generation
                    )
                    q.commit()
                    return "CONFIRMED", capplan, rplan, receipt
            q.commit()
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()
        return super().reserve(request, capability, entry, now=now)


class CorrectedRegistryBrokerWorker(base.RegistryBrokerWorker):
    def __init__(self, registry, runtime, secret):
        if type(registry) is not CorrectedRegistryBoundJournal:
            raise base.RegistryBindingError(
                "supported broker worker requires audited registry journal"
            )
        super().__init__(registry, runtime, secret)

    def process(
        self,
        request,
        capability,
        entry,
        *,
        now,
        timeout_after_commit=False,
    ):
        status, capplan, rplan, receipt = self.registry.reserve(
            request, capability, entry, now=now
        )
        if status == "CONFIRMED":
            return "ALREADY_COMMITTED", receipt

        if status == "UNKNOWN":
            claim = capability.claim if hasattr(capability, "claim") else capability
            allowed = getattr(claim, "reconcile_by_key", None)
            if allowed is None and isinstance(claim, dict):
                allowed = claim.get("reconcile_by_key")
            if allowed is not True:
                raise base.HistoricalExecutionBlocked(
                    "current capability does not authorize reconciliation"
                )
            self.registry.verify_runtime(
                rplan, self.runtime, allow_successor_reconcile=True
            )
            sink = self.runtime.sink
            lookup = getattr(sink, "lookup", None) or getattr(sink, "reconcile", None)
            if lookup is None:
                raise base.HistoricalExecutionBlocked("no reconciliation interface")
            observed = lookup(capplan.effect_key)
            if observed is None:
                raise base.HistoricalExecutionBlocked(
                    "historical UNKNOWN may reconcile only; no re-execution"
                )
            self.registry.journal.confirm(request, observed)
            return "RECONCILED", observed

        self.registry.verify_runtime(
            rplan, self.runtime, allow_successor_reconcile=False
        )
        sink = self.runtime.sink
        try:
            receipt = sink.apply(
                capplan.effect_key,
                request.payload,
                self.secret,
                timeout_after_commit=timeout_after_commit,
            )
        except Exception as exc:
            if exc.__class__.__name__ == "UnknownOutcome":
                self.registry.journal.mark_unknown(request)
            raise
        self.registry.journal.confirm(request, receipt)
        return "COMMITTED", receipt
