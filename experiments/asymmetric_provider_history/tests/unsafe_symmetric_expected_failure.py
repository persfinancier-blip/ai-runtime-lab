import unittest
from experiments.asymmetric_provider_history.protocol import UnsafeSymmetricHistory


class UnsafeBaseline(unittest.TestCase):
    def test_durable_historical_key_should_not_be_able_to_sign_but_can(self):
        history = UnsafeSymmetricHistory(b"durable-historical-hmac")
        payload = {"provider_id": "anchor-A", "generation": 1, "request_id": "new-effect"}
        forged = history.sign(payload)
        self.assertFalse(
            history.verify(payload, forged),
            "durable symmetric history re-authorized signing",
        )


if __name__ == "__main__":
    unittest.main()
