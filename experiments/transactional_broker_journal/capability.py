from __future__ import annotations

import hashlib
from dataclasses import dataclass

from experiments.sink_capability_contract import protocol as cap
from experiments.transactional_broker_journal.protocol import (
    JournalError,
    Request,
    RequestConflict,
    Result,
    StaleCredential,
    TransactionalJournal,
    UnknownOutcome,
)


class CapabilityBindingError(JournalError):
    pass


class CapabilityExecutionBlocked(JournalError):
    pass


POLICIES = {
    "SAFE_RETRY_RECONCILE",
    "SAFE_RETRY_IDEMPOTENT_ONLY",
    "NO_AUTOMATIC_RETRY",
    "READ_ONLY",
}


@dataclass(frozen=True)
class DurableCapabilityPlan:
    sink_id: str
    capability_generation: int
    claim_digest: str
    probe_generation: int
    issuer_id: str
    policy: str
    key_created_at: int
    effect_key: str


class CapabilityBoundJournal:
    """LAB-073 authority persisted in LAB-072's existing broker_requests rows."""

    _COLUMNS = (
        ("capability_sink_id", "TEXT"),
        ("capability_generation", "INTEGER"),
        ("capability_claim_digest", "TEXT"),
        ("capability_probe_generation", "INTEGER"),
        ("capability_issuer_id", "TEXT"),
        ("capability_policy", "TEXT"),
        ("capability_key_created_at", "INTEGER"),
    )

    def __init__(self, journal: TransactionalJournal, verifier: cap.ProbeAuthority):
        self.journal = journal
        self.verifier = verifier
        self._migrate()

    def _migrate(self) -> None:
        q = self.journal._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            present = {row[1] for row in q.execute("PRAGMA table_info(broker_requests)")}
            for name, sql_type in self._COLUMNS:
                if name not in present:
                    q.execute(f"ALTER TABLE broker_requests ADD COLUMN {name} {sql_type}")
            q.execute(
                """
                CREATE TABLE IF NOT EXISTS sink_capability_heads(
                  sink_id TEXT PRIMARY KEY,
                  capability_generation INTEGER NOT NULL,
                  claim_digest TEXT NOT NULL,
                  probe_generation INTEGER NOT NULL,
                  issuer_id TEXT NOT NULL
                )
                """
            )
            q.commit()
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    @staticmethod
    def _sink_request(request: Request) -> dict[str, str]:
        return {
            "task_id": request.task_id,
            "scope": request.scope,
            "payload": request.payload,
        }

    @staticmethod
    def _is_hex_digest(value: object) -> bool:
        return (
            isinstance(value, str)
            and len(value) == 64
            and all(c in "0123456789abcdef" for c in value)
        )

    def _plan_from_row(self, row) -> DurableCapabilityPlan:
        if row is None or len(row) != 7:
            raise CapabilityBindingError("missing capability binding")
        sink_id, generation, claim_digest, probe_generation, issuer_id, policy, created = row
        if not isinstance(sink_id, str) or not sink_id:
            raise CapabilityBindingError("invalid sink identity")
        if type(generation) is not int or generation < 1:
            raise CapabilityBindingError("invalid capability generation")
        if not self._is_hex_digest(claim_digest):
            raise CapabilityBindingError("invalid capability claim digest")
        if type(probe_generation) is not int or probe_generation < 1:
            raise CapabilityBindingError("invalid probe generation")
        if not isinstance(issuer_id, str) or not issuer_id:
            raise CapabilityBindingError("invalid probe issuer")
        if policy not in POLICIES:
            raise CapabilityBindingError("invalid capability policy")
        if type(created) is not int or created < 0:
            raise CapabilityBindingError("invalid capability key creation time")
        return DurableCapabilityPlan(
            sink_id,
            generation,
            claim_digest,
            probe_generation,
            issuer_id,
            policy,
            created,
            "",
        )

    def _load_binding(self, q, request_id: str) -> DurableCapabilityPlan:
        row = q.execute(
            """
            SELECT capability_sink_id,capability_generation,capability_claim_digest,
                   capability_probe_generation,capability_issuer_id,capability_policy,
                   capability_key_created_at,effect_key
            FROM broker_requests WHERE request_id=?
            """,
            (request_id,),
        ).fetchone()
        if row is None:
            raise CapabilityBindingError("unknown request")
        plan = self._plan_from_row(row[:7])
        effect_key = row[7]
        if not isinstance(effect_key, str) or not effect_key:
            raise CapabilityBindingError("invalid effect identity")
        return DurableCapabilityPlan(
            plan.sink_id,
            plan.capability_generation,
            plan.claim_digest,
            plan.probe_generation,
            plan.issuer_id,
            plan.policy,
            plan.key_created_at,
            effect_key,
        )

    def binding(self, request_id: str) -> DurableCapabilityPlan:
        q = self.journal._con()
        try:
            return self._load_binding(q, request_id)
        finally:
            q.close()

    def observe_capability(self, capability: cap.VerifiedCapability):
        claim = self.verifier.verify(capability)
        att = capability.attestation
        q = self.journal._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            row = q.execute(
                "SELECT capability_generation,claim_digest,probe_generation,issuer_id "
                "FROM sink_capability_heads WHERE sink_id=?",
                (claim.sink_id,),
            ).fetchone()
            identity = (claim.generation, att.claim_digest, att.probe_generation, att.issuer_id)
            if row is None:
                q.execute(
                    "INSERT INTO sink_capability_heads VALUES(?,?,?,?,?)",
                    (claim.sink_id, *identity),
                )
            else:
                if claim.generation < row[0]:
                    raise cap.StaleCapability("sink capability generation rolled back")
                if claim.generation == row[0] and tuple(row) != identity:
                    raise cap.StaleCapability("same-generation sink capability substitution")
                if claim.generation > row[0]:
                    q.execute(
                        "UPDATE sink_capability_heads SET capability_generation=?,claim_digest=?,"
                        "probe_generation=?,issuer_id=? WHERE sink_id=?",
                        (*identity, claim.sink_id),
                    )
            q.commit()
            return claim
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    @staticmethod
    def _assert_head_locked(q, capability: cap.VerifiedCapability) -> None:
        claim = capability.claim
        att = capability.attestation
        row = q.execute(
            "SELECT capability_generation,claim_digest,probe_generation,issuer_id "
            "FROM sink_capability_heads WHERE sink_id=?",
            (claim.sink_id,),
        ).fetchone()
        expected = (claim.generation, att.claim_digest, att.probe_generation, att.issuer_id)
        if row is None or tuple(row) != expected:
            raise cap.StaleCapability("sink capability head changed before reservation commit")

    def reserve(self, request: Request, capability: cap.VerifiedCapability, *, now: int):
        if type(now) is not int or now < 0:
            raise CapabilityBindingError("invalid time")

        q = self.journal._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            row = q.execute(
                "SELECT request_digest,status,effect_key,receipt FROM broker_requests WHERE request_id=?",
                (request.request_id,),
            ).fetchone()
            if row is not None:
                if row[0] != request.digest:
                    raise RequestConflict("request_id reused with different content")
                plan = self._load_binding(q, request.request_id)
                q.commit()
                return row[1], plan, row[3]
            q.commit()
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

        claim = self.observe_capability(capability)
        policy = cap.derive_policy(capability, self.verifier, now=now, key_created_at=now)
        if policy in {"READ_ONLY", "NO_AUTOMATIC_RETRY"}:
            raise CapabilityExecutionBlocked("new execution lacks safe retry authority")
        claim_digest = capability.attestation.claim_digest

        q = self.journal._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            row = q.execute(
                "SELECT request_digest,status,effect_key,receipt FROM broker_requests WHERE request_id=?",
                (request.request_id,),
            ).fetchone()
            if row is not None:
                if row[0] != request.digest:
                    raise RequestConflict("request_id reused with different content")
                plan = self._load_binding(q, request.request_id)
                q.commit()
                return row[1], plan, row[3]

            self._assert_head_locked(q, capability)
            current_generation = q.execute(
                "SELECT credential_generation FROM broker_meta WHERE singleton=1"
            ).fetchone()[0]
            if request.credential_generation != current_generation:
                raise StaleCredential("new request uses stale credential generation")
            effect_key = self.journal._effect_key(request)
            q.execute(
                """
                INSERT INTO broker_requests(
                  request_id,request_digest,task_id,scope,credential_generation,effect_key,status,receipt,
                  capability_sink_id,capability_generation,capability_claim_digest,
                  capability_probe_generation,capability_issuer_id,capability_policy,
                  capability_key_created_at
                ) VALUES(?,?,?,?,?,?,'INTENT',NULL,?,?,?,?,?,?,?)
                """,
                (
                    request.request_id,
                    request.digest,
                    request.task_id,
                    request.scope,
                    request.credential_generation,
                    effect_key,
                    claim.sink_id,
                    claim.generation,
                    claim_digest,
                    capability.attestation.probe_generation,
                    capability.attestation.issuer_id,
                    policy,
                    now,
                ),
            )
            q.commit()
            return "INTENT", self.binding(request.request_id), None
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def _revalidate_exact(
        self,
        plan: DurableCapabilityPlan,
        capability: cap.VerifiedCapability,
        *,
        now: int,
    ) -> str:
        claim = self.verifier.verify(capability)
        if claim.sink_id != plan.sink_id:
            raise cap.StaleCapability("sink changed")
        if claim.generation != plan.capability_generation:
            raise cap.StaleCapability("capability generation changed")
        if capability.attestation.claim_digest != plan.claim_digest:
            raise cap.StaleCapability("capability claim changed")
        if capability.attestation.probe_generation != plan.probe_generation:
            raise cap.StaleCapability("probe generation changed")
        if capability.attestation.issuer_id != plan.issuer_id:
            raise cap.StaleCapability("probe issuer changed")
        current = cap.derive_policy(
            capability,
            self.verifier,
            now=now,
            key_created_at=plan.key_created_at,
        )
        order = {
            "READ_ONLY": 0,
            "NO_AUTOMATIC_RETRY": 1,
            "SAFE_RETRY_IDEMPOTENT_ONLY": 2,
            "SAFE_RETRY_RECONCILE": 3,
        }
        return plan.policy if order[current] > order[plan.policy] else current

    def verify_durable(self) -> bool:
        self.journal.verify_durable()
        q = self.journal._con()
        try:
            rows = q.execute("SELECT request_id FROM broker_requests").fetchall()
            heads = q.execute(
                "SELECT sink_id,capability_generation,claim_digest,probe_generation,issuer_id "
                "FROM sink_capability_heads"
            ).fetchall()
            head_map = {}
            for sink_id, generation, claim_digest, probe_generation, issuer_id in heads:
                if not isinstance(sink_id, str) or not sink_id:
                    raise CapabilityBindingError("invalid capability head sink")
                if type(generation) is not int or generation < 1:
                    raise CapabilityBindingError("invalid capability head generation")
                if not self._is_hex_digest(claim_digest):
                    raise CapabilityBindingError("invalid capability head digest")
                if type(probe_generation) is not int or probe_generation < 1:
                    raise CapabilityBindingError("invalid capability head probe generation")
                if not isinstance(issuer_id, str) or not issuer_id:
                    raise CapabilityBindingError("invalid capability head issuer")
                head_map[sink_id] = (generation, claim_digest, probe_generation, issuer_id)
            for (request_id,) in rows:
                plan = self._load_binding(q, request_id)
                head = head_map.get(plan.sink_id)
                if head is None or plan.capability_generation > head[0]:
                    raise CapabilityBindingError("request capability is ahead of durable sink head")
                if plan.capability_generation == head[0] and (
                    plan.claim_digest, plan.probe_generation, plan.issuer_id
                ) != head[1:]:
                    raise CapabilityBindingError("request capability disagrees with same-generation head")
            return True
        finally:
            q.close()


class CapabilityBrokerWorker:
    """External execution is gated by the capability identity durable in broker_requests."""

    def __init__(self, bound: CapabilityBoundJournal, sink, secret: bytes, *, sink_id: str):
        if not isinstance(sink_id, str) or not sink_id:
            raise CapabilityBindingError("invalid configured sink identity")
        self.bound = bound
        self.journal = bound.journal
        self.sink = sink
        self.secret = bytes(secret)
        self.sink_id = sink_id

    def _assert_sink_binding(self, plan: DurableCapabilityPlan) -> None:
        if self.sink_id != plan.sink_id:
            raise CapabilityBindingError("configured sink does not match durable capability")

    def _reconcile(self, plan: DurableCapabilityPlan):
        self._assert_sink_binding(plan)
        if hasattr(self.sink, "lookup"):
            return self.sink.lookup(plan.effect_key)
        if hasattr(self.sink, "reconcile"):
            return self.sink.reconcile(plan.effect_key)
        raise CapabilityExecutionBlocked("sink has no reconciliation interface")

    def process(
        self,
        request: Request,
        capability: cap.VerifiedCapability,
        *,
        now: int,
        timeout_after_commit: bool = False,
    ) -> Result:
        status, plan, receipt = self.bound.reserve(request, capability, now=now)
        if status == "CONFIRMED":
            assert receipt is not None
            return Result(request.request_id, "ALREADY_COMMITTED", receipt, plan.effect_key)

        claim = self.bound.observe_capability(capability)
        if claim.sink_id != plan.sink_id:
            raise cap.StaleCapability("sink changed")

        if status == "UNKNOWN" and claim.generation > plan.capability_generation:
            if not claim.reconcile_by_key:
                raise CapabilityExecutionBlocked(
                    "current rotated capability does not authorize reconciliation"
                )
            observed = self._reconcile(plan)
            if observed is None:
                raise CapabilityExecutionBlocked(
                    "rotated capability permits historical reconciliation only"
                )
            self.journal.confirm(request, observed)
            return Result(request.request_id, "RECONCILED", observed, plan.effect_key)

        policy = self.bound._revalidate_exact(plan, capability, now=now)
        if policy in {"READ_ONLY", "NO_AUTOMATIC_RETRY"}:
            raise CapabilityExecutionBlocked("current capability no longer permits automatic execution")

        if status == "UNKNOWN":
            if policy == "SAFE_RETRY_IDEMPOTENT_ONLY":
                raise CapabilityExecutionBlocked(
                    "UNKNOWN on idempotent-only sink requires external/manual reconciliation"
                )
            observed = self._reconcile(plan)
            if observed is not None:
                self.journal.confirm(request, observed)
                return Result(request.request_id, "RECONCILED", observed, plan.effect_key)

        self._assert_sink_binding(plan)
        try:
            receipt = self.sink.apply(
                plan.effect_key,
                request.payload,
                self.secret,
                timeout_after_commit=timeout_after_commit,
            )
        except UnknownOutcome:
            self.journal.mark_unknown(request)
            raise
        self.journal.confirm(request, receipt)
        return Result(request.request_id, "COMMITTED", receipt, plan.effect_key)


class UnsafeSplitAuthority:
    """Deliberately unsafe: journal intent is reused without capability identity."""

    def process(self, journal: TransactionalJournal, request: Request, sink, secret: bytes):
        status, effect_key, receipt = journal.reserve(request)
        if status == "CONFIRMED":
            return receipt
        return sink.apply(effect_key, request.payload, secret)
