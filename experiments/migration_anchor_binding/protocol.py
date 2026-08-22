from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass


class MigrationAnchorError(RuntimeError):
    pass


class MigrationAnchorPending(MigrationAnchorError):
    pass


class MigrationRollbackDetected(MigrationAnchorError):
    pass


class MigrationAnchorSubstitution(MigrationAnchorError):
    pass


class MigrationAnchorUnavailable(MigrationAnchorError):
    pass


def _canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def _sha(obj) -> str:
    return hashlib.sha256(_canon(obj)).hexdigest()


@dataclass(frozen=True)
class MigrationIdentity:
    checkpoint_id: str
    cutoff_sequence: int
    terminal_authority_id: str
    terminal_authority_version: int
    terminal_authority_epoch: int

    @classmethod
    def from_checkpoint(cls, cp):
        return cls(
            cp.checkpoint_id,
            cp.cutoff_sequence,
            cp.terminal_authority_id,
            cp.terminal_authority_version,
            cp.terminal_authority_epoch,
        )

    @property
    def payload_digest(self) -> str:
        return _sha(asdict(self))


@dataclass(frozen=True)
class BindingState:
    checkpoint_id: str
    payload_digest: str
    sequence: int
    status: str
    anchor_receipt_ref: str | None
    provider_id: str
    provider_generation: int


class RegistryAnchorState:
    """Anchor state stored in the same SQLite DB as LAB-078.

    Restoring the whole DB rewinds this sequence together with the migration
    checkpoint, while the external monotonic anchor remains ahead. That is the
    rollback signal LAB-079 composes with LAB-034--037.
    """

    def __init__(self, connect):
        self._connect = connect
        self._init()

    def _init(self):
        q = self._connect()
        try:
            q.executescript(
                """
                CREATE TABLE IF NOT EXISTS migration_anchor_meta(
                  singleton INTEGER PRIMARY KEY CHECK(singleton=1),
                  global_sequence INTEGER NOT NULL
                );
                INSERT OR IGNORE INTO migration_anchor_meta VALUES(1,0);
                CREATE TABLE IF NOT EXISTS migration_anchor_binding(
                  singleton INTEGER PRIMARY KEY CHECK(singleton=1),
                  checkpoint_id TEXT NOT NULL,
                  payload_digest TEXT NOT NULL,
                  sequence INTEGER NOT NULL,
                  status TEXT NOT NULL CHECK(status IN ('PENDING','CONFIRMED')),
                  anchor_receipt_ref TEXT,
                  provider_id TEXT NOT NULL,
                  provider_generation INTEGER NOT NULL
                );
                """
            )
            q.commit()
        finally:
            q.close()

    def sequence(self) -> int:
        q = self._connect()
        try:
            return q.execute(
                "SELECT global_sequence FROM migration_anchor_meta WHERE singleton=1"
            ).fetchone()[0]
        finally:
            q.close()

    def load(self) -> BindingState | None:
        q = self._connect()
        try:
            row = q.execute(
                "SELECT checkpoint_id,payload_digest,sequence,status,anchor_receipt_ref,"
                "provider_id,provider_generation FROM migration_anchor_binding WHERE singleton=1"
            ).fetchone()
            return None if row is None else BindingState(*row)
        finally:
            q.close()

    def prepare(self, identity: MigrationIdentity, *, provider_id: str, provider_generation: int):
        q = self._connect()
        try:
            q.execute("BEGIN IMMEDIATE")
            existing = q.execute(
                "SELECT checkpoint_id,payload_digest,sequence,status,anchor_receipt_ref,"
                "provider_id,provider_generation FROM migration_anchor_binding WHERE singleton=1"
            ).fetchone()
            if existing is not None:
                state = BindingState(*existing)
                expected = (identity.checkpoint_id, identity.payload_digest, provider_id, provider_generation)
                actual = (state.checkpoint_id, state.payload_digest, state.provider_id, state.provider_generation)
                if actual != expected:
                    raise MigrationAnchorSubstitution("existing binding names different migration/provider")
                q.commit()
                return state
            seq = q.execute(
                "SELECT global_sequence FROM migration_anchor_meta WHERE singleton=1"
            ).fetchone()[0] + 1
            q.execute(
                "UPDATE migration_anchor_meta SET global_sequence=? WHERE singleton=1",
                (seq,),
            )
            q.execute(
                "INSERT INTO migration_anchor_binding VALUES(1,?,?,?,'PENDING',NULL,?,?)",
                (identity.checkpoint_id, identity.payload_digest, seq, provider_id, provider_generation),
            )
            q.commit()
            return BindingState(
                identity.checkpoint_id, identity.payload_digest, seq, "PENDING", None,
                provider_id, provider_generation,
            )
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def confirm(self, expected: BindingState, receipt_ref: str):
        q = self._connect()
        try:
            q.execute("BEGIN IMMEDIATE")
            row = q.execute(
                "SELECT checkpoint_id,payload_digest,sequence,status,anchor_receipt_ref,"
                "provider_id,provider_generation FROM migration_anchor_binding WHERE singleton=1"
            ).fetchone()
            if row is None:
                raise MigrationAnchorSubstitution("binding disappeared before confirmation")
            current = BindingState(*row)
            if (
                current.checkpoint_id,
                current.payload_digest,
                current.sequence,
                current.provider_id,
                current.provider_generation,
            ) != (
                expected.checkpoint_id,
                expected.payload_digest,
                expected.sequence,
                expected.provider_id,
                expected.provider_generation,
            ):
                raise MigrationAnchorSubstitution("binding changed during anchor catch-up")
            q.execute(
                "UPDATE migration_anchor_binding SET status='CONFIRMED',anchor_receipt_ref=? "
                "WHERE singleton=1",
                (receipt_ref,),
            )
            q.commit()
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()


class MigrationAnchorCoordinator:
    """Compose an authenticated LAB-078 checkpoint with LAB-036 attested catch-up."""

    def __init__(self, migration, attested_catchup):
        self.migration = migration
        self.attested = attested_catchup
        self.state = RegistryAnchorState(migration._con)

    def _expected_provider(self):
        expected = self.attested.verifier.expected
        return expected.provider_id, expected.generation

    def _load_identity(self) -> MigrationIdentity:
        self.migration.verify_mixed_history()
        q = self.migration._con()
        try:
            q.execute("BEGIN")
            cp, _ = self.migration._load_checkpoint_locked(q)
            q.commit()
            return MigrationIdentity.from_checkpoint(cp)
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def prepare(self) -> BindingState:
        identity = self._load_identity()
        provider_id, generation = self._expected_provider()
        return self.state.prepare(identity, provider_id=provider_id, provider_generation=generation)

    def catch_up(self, *, timeout_after_commit=False) -> BindingState:
        binding = self.prepare()
        request_id = f"migration-anchor:{binding.sequence}:{binding.checkpoint_id}"
        try:
            receipt = self.attested.catch_up_one(
                db_sequence=binding.sequence,
                request_id=request_id,
                timeout_after_commit=timeout_after_commit,
            )
        except Exception as exc:
            raise MigrationAnchorPending(str(exc)) from exc
        self.state.confirm(binding, receipt)
        return self.state.load()

    def verify_restart(self) -> bool:
        local_seq = self.state.sequence()
        try:
            identity = self._load_identity()
        except Exception as migration_error:
            try:
                obs = self.attested.authenticated_read(request_id="migration-restart:no-checkpoint")
            except Exception as anchor_error:
                raise MigrationAnchorUnavailable(str(anchor_error)) from anchor_error
            if obs.position > local_seq:
                raise MigrationRollbackDetected(
                    f"external anchor ahead of restored DB: anchor={obs.position} db={local_seq}"
                ) from migration_error
            raise MigrationAnchorPending("migration checkpoint not consequentially established") from migration_error

        binding = self.state.load()
        if binding is None:
            raise MigrationAnchorPending("migration committed locally but no anchor binding exists")
        provider_id, generation = self._expected_provider()
        if (binding.provider_id, binding.provider_generation) != (provider_id, generation):
            raise MigrationAnchorSubstitution("binding provider/generation mismatch")
        if (binding.checkpoint_id, binding.payload_digest) != (identity.checkpoint_id, identity.payload_digest):
            raise MigrationAnchorSubstitution("same-position migration identity substitution")
        if binding.sequence != local_seq:
            raise MigrationAnchorSubstitution("binding/meta sequence mismatch")
        if binding.status != "CONFIRMED" or not binding.anchor_receipt_ref:
            raise MigrationAnchorPending("external anchor confirmation is pending")
        try:
            obs = self.attested.authenticated_read(
                request_id=f"migration-restart:{binding.sequence}:{binding.checkpoint_id}"
            )
        except Exception as exc:
            raise MigrationAnchorUnavailable(str(exc)) from exc
        if obs.position < binding.sequence:
            raise MigrationRollbackDetected("external anchor rolled back below confirmed migration")
        if obs.position > binding.sequence:
            raise MigrationRollbackDetected("external anchor position cannot be explained by this DB snapshot")
        return True


class UnsafeLocalOnlyMigration:
    def consequential(self, migration) -> bool:
        try:
            migration.verify_mixed_history()
            return True
        except Exception:
            return False
