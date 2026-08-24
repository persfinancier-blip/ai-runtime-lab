from __future__ import annotations


class CutoffActivationError(RuntimeError):
    pass


def require_public_authority_active_at_cutoff(
    public_authority_id,
    cutoff_root_version,
    ordered_public_authority_ids,
    transitions,
):
    """Require the boundary signer to be active at the cutoff root version.

    ``ordered_public_authority_ids`` is the verified public-custody history in
    version order. ``transitions`` contains ``(old_id, new_id, root_version)``
    for every adjacent authority edge, where ``root_version`` is the version of
    the normal/root authority that co-authorized that public-custody rotation.

    A transition at root version N deactivates the old public authority at N and
    activates the new authority at N. Therefore windows are lower-inclusive and
    upper-exclusive, matching the LAB-085 recovery lifecycle semantics. Multiple
    rotations at the same root version are permitted; only the last successor is
    active for a consequential boundary taken at that version.
    """

    if type(cutoff_root_version) is not int or cutoff_root_version < 1:
        raise CutoffActivationError("invalid cutoff root version")
    if not isinstance(public_authority_id, str) or not public_authority_id:
        raise CutoffActivationError("invalid public authority identity")
    if not isinstance(ordered_public_authority_ids, (tuple, list)):
        raise CutoffActivationError("invalid public authority history")
    ids = tuple(ordered_public_authority_ids)
    if not ids or any(not isinstance(value, str) or not value for value in ids):
        raise CutoffActivationError("invalid public authority history")
    if len(set(ids)) != len(ids):
        raise CutoffActivationError("duplicate public authority identity")
    if public_authority_id not in ids:
        raise CutoffActivationError("boundary references unknown public authority")

    if not isinstance(transitions, (tuple, list)):
        raise CutoffActivationError("invalid public transition history")
    edges = tuple(transitions)
    if len(edges) != len(ids) - 1:
        raise CutoffActivationError("public transition history cardinality mismatch")

    lower = None
    upper = None
    for index, edge in enumerate(edges):
        if not isinstance(edge, (tuple, list)) or len(edge) != 3:
            raise CutoffActivationError("invalid public transition")
        old_id, new_id, root_version = edge
        if (old_id, new_id) != (ids[index], ids[index + 1]):
            raise CutoffActivationError("public transition continuity mismatch")
        if type(root_version) is not int or root_version < 1:
            raise CutoffActivationError("invalid public transition root version")
        if index and root_version < edges[index - 1][2]:
            raise CutoffActivationError("public activation root version rollback")
        if public_authority_id == old_id:
            upper = root_version
        if public_authority_id == new_id:
            lower = root_version

    if lower is not None and cutoff_root_version < lower:
        raise CutoffActivationError("public authority used before activation")
    if upper is not None and cutoff_root_version >= upper:
        raise CutoffActivationError("stale public authority used after rotation")
    return True
