import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from experiments.ctv2_sth_chain.protocol import (
    TreeHeadDataV2,
    sign_sth,
    unsafe_trust_parsed_fields,
)


class UnsafeParsedSTHBaseline(unittest.TestCase):
    def test_corrupted_signature_should_not_authenticate_but_parser_trusts_fields(self):
        private_key = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
        log_id = bytes.fromhex("2b65645000")
        tree = TreeHeadDataV2(1000, 1, b"r" * 32, ())
        wire = bytearray(sign_sth(tree, log_id=log_id, private_key=private_key, hash_size=32))
        wire[-1] ^= 0x01
        parsed = unsafe_trust_parsed_fields(bytes(wire), hash_size=32)
        self.assertNotEqual(
            parsed.tree_head,
            tree,
            "unsafe parser accepted the signed fields without authenticating the corrupted signature",
        )


if __name__ == "__main__":
    unittest.main()
