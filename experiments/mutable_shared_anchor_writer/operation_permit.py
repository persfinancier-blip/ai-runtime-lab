from __future__ import annotations

import contextlib
import sqlite3


class OperationPermitError(RuntimeError):
    pass


class PermitConnection(sqlite3.Connection):
    """SQLite connection carrying one connection-local, one-shot DML permit."""

    pass


def install_operation_permit_udf(q: PermitConnection) -> None:
    if type(q) is not PermitConnection:
        raise TypeError("exact LAB-091 permit connection required")
    q._lab091_permit = None

    def consume(kind, identity, old_value, new_value):
        expected = q._lab091_permit
        actual = (kind, identity, old_value, new_value)
        if expected is None or actual != expected:
            return 0
        # Consume before SQLite executes the row mutation.  A second statement in
        # the same transaction therefore cannot inherit authority.  Rollback does
        # not resurrect the Python-side capability.
        q._lab091_permit = None
        return 1

    q.create_function("lab091_consume_permit", 4, consume)


@contextlib.contextmanager
def one_shot_permit(q: PermitConnection, *, kind, identity, old_value, new_value):
    if type(q) is not PermitConnection:
        raise TypeError("exact LAB-091 permit connection required")
    if not q.in_transaction:
        raise OperationPermitError("operation permit requires an active transaction")
    if q._lab091_permit is not None:
        raise OperationPermitError("nested operation permit")
    permit = (kind, identity, old_value, new_value)
    if not all(isinstance(value, str) for value in permit):
        raise OperationPermitError("permit fields must be canonical strings")
    q._lab091_permit = permit
    try:
        yield q
    finally:
        # Clear unused permits and also clear after statement errors.  Successful
        # statements normally consume the permit from the trigger itself.
        q._lab091_permit = None
