from __future__ import annotations

import sqlite3

from experiments.anchor_attestation.protocol import AttestedCatchup, UnknownOutcome
from experiments.provider_generation_history.activation import (
    ActivationTicket,
    FencedActivationProvider,
)
from experiments.provider_generation_history.integration import (
    HistoricalSharedAnchorLedger,
    IntegratedProviderHistory,
)
from experiments.provider_generation_history.protocol import (
    GenerationDescriptor,
    HistoricalReceipt,
    HistoricalVerificationError,
    InvalidTransition,
    PendingRotationBlocked,
)
from experiments.shared_anchor_intent_ledger.protocol import IntentSubstitution, LedgerEntry, UnexplainedAdvance
from experiments.shared_anchor_intent_ledger.supported import SupportedSharedAnchorLedger


class CoordinatorOnlyProviderHistory(IntegratedProviderHistory):
    """Provider history whose authority-changing API is only the shared-ledger coordinator."""

    def rotate(self, *args, **kwargs):
        raise PendingRotationBlocked(
            "integrated provider rotation must use SupportedHistoricalSharedAnchorLedger.rotate_provider()"
        )


class SupportedHistoricalSharedAnchorLedger(HistoricalSharedAnchorLedger):
    """Audited LAB-081 surface with LAB-090 provider-activation fencing.

    The first exact signed provider observation for a confirmed request is immutable
    historical evidence. Later verification never replaces it with a new challenge;
    current anchor freshness is established separately by LAB-080 authenticated reads.

    Provider-generation mutation is coordinator-only so a caller cannot bypass the
    shared LAB-080 PREPARED check by invoking the standalone history API directly.

    LAB-090 additionally requires the candidate provider to atomically reserve its
    exact position before the SQL generation-head transaction. The resulting
    activation ticket is durably bound in the same SQLite commit as the generation
    rotation. Provider commit keeps the external fence installed until the
    coordinator durably acknowledges COMMITTED and releases that exact ticket.
    While activation is unresolved, a database trigger blocks new shared-anchor
    intents on every writer.
    """

    def __init__(self, path, attested: AttestedCatchup, bootstrap: GenerationDescriptor):
        if type(attested) is not AttestedCatchup:
            raise TypeError("exact LAB-036 AttestedCatchup required")
        self.provider_history = CoordinatorOnlyProviderHistory(path, bootstrap)
        SupportedSharedAnchorLedger.__init__(self, path, attested)
        self._init_activation_schema()
        self._require_runtime_matches_durable_head()
        self._recover_pending_activation()
        self._verify_activation_records()

    def _init_activation_schema(self):
        q = self._con()
        try:
            q.executescript(
                """
                CREATE TABLE IF NOT EXISTS provider_generation_activations(
                  activation_id TEXT PRIMARY KEY,
                  new_generation_id TEXT NOT NULL UNIQUE,
                  provider_id TEXT NOT NULL,
                  generation INTEGER NOT NULL,
                  expected_position INTEGER NOT NULL,
                  fence INTEGER NOT NULL,
                  status TEXT NOT NULL CHECK(status IN ('SQL_COMMITTED','COMMITTED'))
                );
                CREATE TRIGGER IF NOT EXISTS block_intent_during_provider_activation
                BEFORE INSERT ON shared_anchor_intents
                WHEN EXISTS(
                  SELECT 1 FROM provider_generation_activations WHERE status='SQL_COMMITTED'
                )
                BEGIN
                  SELECT RAISE(ABORT, 'provider activation unresolved');
                END;
                """
            )
            q.commit()
        finally:
            q.close()

    @staticmethod
    def _activation_id(new: GenerationDescriptor, expected_position: int) -> str:
        return f"provider-activation:{new.generation_id}:{int(expected_position)}"

    @staticmethod
    def _ticket_from_row(row) -> ActivationTicket:
        return ActivationTicket(row[2], row[3], row[4], row[0], row[5])

    def _activation_row(self, *, activation_id=None, generation_id=None):
        if (activation_id is None) == (generation_id is None):
            raise ValueError("select exactly one activation identity")
        q = self._con()
        try:
            if activation_id is not None:
                return q.execute(
                    "SELECT activation_id,new_generation_id,provider_id,generation,expected_position,fence,status "
                    "FROM provider_generation_activations WHERE activation_id=?",
                    (activation_id,),
                ).fetchone()
            return q.execute(
                "SELECT activation_id,new_generation_id,provider_id,generation,expected_position,fence,status "
                "FROM provider_generation_activations WHERE new_generation_id=?",
                (generation_id,),
            ).fetchone()
        finally:
            q.close()

    def _mark_activation_committed(self, ticket: ActivationTicket):
        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            changed = q.execute(
                "UPDATE provider_generation_activations SET status='COMMITTED' "
                "WHERE activation_id=? AND provider_id=? AND generation=? "
                "AND expected_position=? AND fence=? AND status IN ('SQL_COMMITTED','COMMITTED')",
                (
                    ticket.activation_id,
                    ticket.provider_id,
                    ticket.generation,
                    ticket.expected_position,
                    ticket.fence,
                ),
            ).rowcount
            if changed != 1:
                raise HistoricalVerificationError("durable activation ticket mismatch")
            q.commit()
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def _release_committed_activation(self, provider: FencedActivationProvider, ticket: ActivationTicket):
        status = provider.activation_status(ticket)
        if status == "RELEASED":
            return
        if status != "COMMITTED_FENCED":
            raise HistoricalVerificationError("durably committed activation is not provider-committed")
        released = provider.release_activation(ticket)
        if released != "RELEASED":
            raise HistoricalVerificationError("provider activation fence did not release")

    def _commit_or_reconcile_activation(self, provider: FencedActivationProvider, ticket: ActivationTicket):
        try:
            status = provider.commit_activation(ticket)
        except UnknownOutcome:
            status = provider.activation_status(ticket)
        if status != "COMMITTED_FENCED":
            raise HistoricalVerificationError(
                "provider activation must remain fenced until durable acknowledgement"
            )
        # Ordering is security/correctness critical: provider commit does not release
        # the external fence. Persist exact-ticket acknowledgement first, then release.
        self._mark_activation_committed(ticket)
        self._release_committed_activation(provider, ticket)

    def _recover_pending_activation(self):
        durable = self.provider_history.current()
        row = self._activation_row(generation_id=durable.generation_id)
        if row is None:
            return
        ticket = self._ticket_from_row(row)
        provider = self.attested.provider
        if not isinstance(provider, FencedActivationProvider):
            raise HistoricalVerificationError("runtime provider cannot reconcile durable activation ticket")
        status = provider.activation_status(ticket)
        if row[6] == "SQL_COMMITTED":
            if status == "PREPARED":
                self._commit_or_reconcile_activation(provider, ticket)
            elif status == "COMMITTED_FENCED":
                self._mark_activation_committed(ticket)
                self._release_committed_activation(provider, ticket)
            elif status == "RELEASED":
                raise HistoricalVerificationError(
                    "provider activation released before durable acknowledgement"
                )
            elif status == "ABSENT":
                raise HistoricalVerificationError("provider lost durable activation reservation")
            else:
                raise HistoricalVerificationError("unknown provider activation status")
        elif row[6] == "COMMITTED":
            if status == "COMMITTED_FENCED":
                self._release_committed_activation(provider, ticket)
            elif status != "RELEASED":
                raise HistoricalVerificationError("durable committed activation/provider status mismatch")
        else:
            raise HistoricalVerificationError("invalid durable activation status")

    def _verify_activation_records(self):
        durable = self.provider_history.current()
        q = self._con()
        try:
            rows = q.execute(
                "SELECT a.activation_id,a.new_generation_id,a.provider_id,a.generation,"
                "a.expected_position,a.fence,a.status,g.verification_key_hex "
                "FROM provider_generation_activations AS a "
                "LEFT JOIN provider_generations AS g ON g.generation_id=a.new_generation_id "
                "ORDER BY a.generation"
            ).fetchall()
        finally:
            q.close()
        for row in rows:
            if row[7] is None:
                raise HistoricalVerificationError("activation references missing provider generation")
            ticket = self._ticket_from_row(row)
            desc = GenerationDescriptor(row[2], row[3], row[7])
            if desc.generation_id != row[1]:
                raise HistoricalVerificationError("activation generation identity mismatch")
            if row[0] != self._activation_id(desc, row[4]):
                raise HistoricalVerificationError("activation identity mismatch")
            if ticket.fence < 1:
                raise HistoricalVerificationError("invalid activation fence")
            if row[6] not in {"SQL_COMMITTED", "COMMITTED"}:
                raise HistoricalVerificationError("invalid activation status")
            if row[6] == "SQL_COMMITTED" and row[1] != durable.generation_id:
                raise HistoricalVerificationError(
                    "historical provider activation remains unresolved"
                )
        return True

    def reserve(self, intent):
        try:
            return super().reserve(intent)
        except sqlite3.IntegrityError as exc:
            if "provider activation unresolved" in str(exc):
                raise PendingRotationBlocked("provider activation commit is unresolved") from exc
            raise

    def rotate_provider(self, new: GenerationDescriptor, proof, new_attested: AttestedCatchup):
        if type(new_attested) is not AttestedCatchup:
            raise TypeError("exact LAB-036 AttestedCatchup required")
        runtime_new = self._descriptor_from_attested(new_attested)
        if runtime_new.generation_id != new.generation_id:
            raise InvalidTransition("new runtime verifier does not match generation descriptor")
        provider = new_attested.provider
        if not isinstance(provider, FencedActivationProvider):
            raise TypeError("LAB-090 rotation requires FencedActivationProvider")

        existing = self._activation_row(generation_id=new.generation_id)
        if existing is not None:
            durable = self.provider_history.current()
            if new.generation_id != durable.generation_id:
                raise InvalidTransition("activation retry is not durable current generation")
            ticket = self._ticket_from_row(existing)
            if existing[6] == "SQL_COMMITTED":
                self._commit_or_reconcile_activation(provider, ticket)
            elif existing[6] == "COMMITTED":
                self._release_committed_activation(provider, ticket)
            else:
                raise HistoricalVerificationError("invalid durable activation status")
            self.attested = new_attested
            self._require_runtime_matches_durable_head()
            return new

        q = self._con()
        try:
            q.execute("BEGIN")
            expected_position = q.execute(
                "SELECT reserved_position FROM shared_anchor_meta WHERE singleton=1"
            ).fetchone()[0]
            q.commit()
        finally:
            q.close()

        activation_id = self._activation_id(new, expected_position)
        ticket = provider.prepare_activation(
            expected_position=expected_position,
            activation_id=activation_id,
        )
        sql_committed = False
        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            unresolved_activation = q.execute(
                "SELECT 1 FROM provider_generation_activations WHERE status='SQL_COMMITTED' LIMIT 1"
            ).fetchone()
            if unresolved_activation is not None:
                raise PendingRotationBlocked("previous provider activation commit is unresolved")
            pending = q.execute(
                "SELECT COUNT(*) FROM shared_anchor_intents WHERE status='PREPARED'"
            ).fetchone()[0]
            if pending:
                raise PendingRotationBlocked("unresolved PREPARED anchor intent")
            reserved = q.execute(
                "SELECT reserved_position FROM shared_anchor_meta WHERE singleton=1"
            ).fetchone()[0]
            if reserved != ticket.expected_position:
                raise InvalidTransition("shared anchor tail changed after provider activation prepare")
            q.execute(
                "INSERT INTO provider_generation_activations VALUES(?,?,?,?,?,?,'SQL_COMMITTED')",
                (
                    ticket.activation_id,
                    new.generation_id,
                    ticket.provider_id,
                    ticket.generation,
                    ticket.expected_position,
                    ticket.fence,
                ),
            )
            self.provider_history._rotate_locked(q, new, proof)
            q.commit()
            sql_committed = True
        except:
            if q.in_transaction:
                q.rollback()
            row = self._activation_row(activation_id=ticket.activation_id)
            if row is not None and row[6] in {"SQL_COMMITTED", "COMMITTED"}:
                sql_committed = True
            if not sql_committed:
                provider.abort_activation(ticket)
                raise
        finally:
            q.close()

        self._commit_or_reconcile_activation(provider, ticket)
        self.attested = new_attested
        self._require_runtime_matches_durable_head()
        return new

    def _stored_receipt(self, entry: LedgerEntry):
        q = self._con()
        try:
            q.execute("BEGIN")
            row = q.execute(
                "SELECT 1 FROM historical_provider_receipts WHERE request_id=?",
                (entry.request_id,),
            ).fetchone()
            if row is None:
                q.commit()
                return None
            receipt = self.provider_history._load_receipt_locked(q, entry.request_id)
            q.commit()
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()
        if (
            receipt.provider_id != entry.provider_id
            or receipt.generation != entry.provider_generation
            or receipt.position != entry.position
            or receipt.request_id != entry.request_id
        ):
            raise IntentSubstitution("historical receipt does not bind exact ledger entry")
        return receipt

    def _reauthenticate(self, entry: LedgerEntry):
        stored = self._stored_receipt(entry)
        if stored is not None:
            return stored.stable_binding

        durable = self.provider_history.current()
        if (entry.provider_id, entry.provider_generation) != (
            durable.provider_id,
            durable.generation,
        ):
            raise HistoricalVerificationError("historical ledger entry has no signed receipt evidence")

        self._runtime_matches_entry(entry)
        challenge = self.attested.challenge()
        obs = self.attested.provider.reconcile_increment(
            challenge=challenge, request_id=entry.request_id
        )
        if obs is None:
            raise UnexplainedAdvance("provider has no result for ledger request")
        verified = self.attested.verifier.verify(
            obs, expected_challenge=challenge, allowed_kinds={"RECONCILE"}
        )
        if verified.position != entry.position or verified.request_id != entry.request_id:
            raise UnexplainedAdvance("provider result does not bind ledger position/request")
        receipt = HistoricalReceipt(
            verified.provider_id,
            verified.generation,
            verified.position,
            verified.request_id,
            verified.kind,
            verified.challenge,
            verified.mac,
        )
        binding = self.provider_history.store_receipt(receipt)
        if binding != self._stable_receipt(verified):
            raise IntentSubstitution("historical receipt identity mismatch")
        return binding