import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from experiments.ctv2_sth_chain.protocol import (
    ED25519,
    LogProfile,
    SignatureError,
    TreeHeadDataV2,
    authenticate_sth,
    sign_sth,
)


class SignatureCorruptionTests(unittest.TestCase):
    def test_corrupted_signature_rejected(self):
        private_key = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
        public_key = private_key.public_key().public_bytes_raw()
        log_id = bytes.fromhex("2b65645000")
        tree = TreeHeadDataV2(1000, 1, b"r" * 32, ())
        wire = bytearray(sign_sth(tree, log_id=log_id, private_key=private_key, hash_size=32))
        wire[-1] ^= 0x01
        profile = LogProfile(log_id, 32, ED25519, public_key)
        with self.assertRaises(SignatureError):
            authenticate_sth(bytes(wire), profile)


if __name__ == "__main__":
    unittest.main()
