from __future__ import annotations

import json

from experiments.sink_registry_binding import audit_fixes as audited
from experiments.sink_registry_binding import protocol as base
from experiments.sink_registry_authority_lifecycle.protocol import (
    AuthoritySubstitution,
    DurableRegistryAuthority,
    EntryAuthError,
)


class _LifecycleAuthorityAdapter:
    """Compatibility adapter for inherited LAB-075 read paths.

    An already accepted entry is verified against its exact historical authority.
    A never-before-accepted candidate is checked against the current publication
    authority. Registry generation/predecessor rules still decide whether the
    candidate may become a registry head.
    """

    def __init__(self, lifecycle: DurableRegistryAuthority):
        self.lifecycle = lifecycle

    def verify(self, entry):
        try:
            historical = self.lifecycle.verify_historical_entry(entry.entry_digest)
        except Exception as exc:
            # Only a genuinely unknown accepted-entry binding may fall through to
            # current publication verification. Corruption/authentication errors
            # must not be converted into a chance to re-authorize the bytes.
            if exc.__class__.__name__ != "HistoricalAuthorityMissing":
                raise
            return self.lifecycle.verify_for_publication(entry)
        if historical != entry:
            raise AuthoritySubstitution("historical entry bytes differ")
        return historical


class LifecycleRegistryBoundJournal(audited.CorrectedRegistryBoundJournal):
    """LAB-075 registry journal with LAB-076 authority lifecycle binding.

    The lifecycle DB and transactional broker journal must be the same SQLite
    database so authority rotation and new registry publication serialize on one
    write boundary.
    """

    def __init__(self, bound, lifecycle: DurableRegistryAuthority):
        if str(bound.journal.path) != lifecycle.path:
            raise base.RegistryBindingError(
                "registry authority lifecycle must share the broker journal database"
            )
        self.lifecycle = lifecycle
        super().__init__(bound, _LifecycleAuthorityAdapter(lifecycle))

    @staticmethod
    def _entry_from_authority_row(row):
        raw, authority_id, authority_version = row
        data = json.loads(raw)
        entry = base.RegistryEntry(
            data["sink_id"],
            data["generation"],
            data["adapter_digest"],
            data["endpoint_origin"],
            data["operation_profile"],
            data.get("predecessor_entry_digest"),
            data["issuer_id"],
            data["issuer_generation"],
            data["signature"],
        )
        return entry, authority_id, authority_version

    def _historical_locked(self, q, entry_digest):
        row = q.execute(
            "SELECT entry_json,authority_id,authority_version "
            "FROM registry_authorized_entries WHERE entry_digest=?",
            (entry_digest,),
        ).fetchone()
        if row is None:
            return None
        entry, authority_id, authority_version = self._entry_from_authority_row(row)
        if entry.entry_digest != entry_digest:
            raise AuthoritySubstitution("historical entry digest mismatch")
        root = self.lifecycle._load_root(q, authority_id)
        if root.version != authority_version:
            raise AuthoritySubstitution("historical authority version mismatch")
        self.lifecycle._verify_against(entry, root)
        return entry

    def _current_locked(self, q):
        row = q.execute(
            "SELECT authority_id,version,epoch FROM registry_authority_head WHERE singleton=1"
        ).fetchone()
        if row is None:
            raise AuthoritySubstitution("missing registry authority head")
        root = self.lifecycle._load_root(q, row[0])
        if (root.version, root.authority_epoch) != (row[1], row[2]):
            raise AuthoritySubstitution("registry authority head mismatch")
        return row[0], root

    def observe(self, entry):
        entry_digest = entry.entry_digest
        q = self.journal._con()
        try:
            q.execute("BEGIN IMMEDIATE")

            accepted = self._historical_locked(q, entry_digest)
            if accepted is not None:
                if accepted != entry:
                    raise base.RegistrySubstitution(
                        "accepted historical entry differs from candidate"
                    )
            else:
                authority_id, current = self._current_locked(q)
                if entry.issuer_generation != current.version:
                    raise EntryAuthError(
                        "new registry publication requires current authority generation"
                    )
                self.lifecycle._verify_against(entry, current)
                raw = json.dumps(
                    {**entry.unsigned, "signature": entry.signature},
                    sort_keys=True,
                    separators=(",", ":"),
                )
                q.execute(
                    "INSERT INTO registry_authorized_entries VALUES(?,?,?,?)",
                    (entry_digest, raw, authority_id, current.version),
                )

            row = q.execute(
                "SELECT entry_digest,sink_id,generation,adapter_digest,endpoint_origin,"
                "operation_profile,predecessor_entry_digest,issuer_id,issuer_generation,signature "
                "FROM sink_registry_entries WHERE entry_digest=?",
                (entry_digest,),
            ).fetchone()
            if row is not None:
                stored = self._row_entry(row)
                historical = self._historical_locked(q, entry_digest)
                if historical != stored or stored != entry:
                    raise base.RegistrySubstitution(
                        "stored registry row differs from authenticated historical entry"
                    )

            head = q.execute(
                "SELECT entry_digest,generation FROM sink_registry_heads WHERE sink_id=?",
                (entry.sink_id,),
            ).fetchone()
            if head is None:
                if entry.generation != 1 or entry.predecessor_entry_digest is not None:
                    raise base.RegistryRollback("invalid registry bootstrap")
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
            historical = self._historical_locked(q, entry_digest)
            if historical != stored or stored != entry:
                raise base.RegistrySubstitution(
                    "registry row / historical-authority binding mismatch before head activation"
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
                        "registry head changed before authority-bound activation"
                    )
            q.commit()
            return entry
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def verify_durable(self):
        self.lifecycle.verify_durable()
        return super().verify_durable()


class LifecycleRegistryBrokerWorker(audited.CorrectedRegistryBrokerWorker):
    """Exact-type-gated worker for the lifecycle-aware audited journal."""

    def __init__(self, registry, runtime, secret):
        if type(registry) is not LifecycleRegistryBoundJournal:
            raise base.RegistryBindingError(
                "lifecycle broker worker requires lifecycle registry journal"
            )
        # Bypass CorrectedRegistryBrokerWorker.__init__ exact-type gate while
        # retaining its audited process() implementation.
        base.RegistryBrokerWorker.__init__(self, registry, runtime, secret)
