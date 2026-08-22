from __future__ import annotations

from .protocol import InvalidAuthority, RotationAuthority, key_id


def _lower_hex(value: str) -> bool:
    return (
        isinstance(value, str)
        and len(value) > 0
        and len(value) % 2 == 0
        and all(c in "0123456789abcdef" for c in value)
    )


def require_canonical_authority(authority: RotationAuthority):
    if type(authority) is not RotationAuthority:
        raise TypeError("exact LAB-083 RotationAuthority required")
    authority.validate()
    if type(authority.keys) is not dict or type(authority.revoked) is not tuple:
        raise InvalidAuthority("noncanonical authority container type")
    for signer_id, key_hex in authority.keys.items():
        if not isinstance(signer_id, str) or not signer_id:
            raise InvalidAuthority("invalid signer identity")
        if not _lower_hex(key_hex):
            raise InvalidAuthority("authority key must be canonical lowercase hex")
        if signer_id != key_id(bytes.fromhex(key_hex)):
            raise InvalidAuthority("signer/key mismatch")
    for signer_id in authority.revoked:
        if not isinstance(signer_id, str) or signer_id not in authority.keys:
            raise InvalidAuthority("revoked signer is not a known authority key")
    return authority
