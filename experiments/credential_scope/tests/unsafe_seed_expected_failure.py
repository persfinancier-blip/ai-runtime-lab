import unittest
from experiments.credential_scope.protocol import UnsafeForwarder


class UnsafeForwardingBaseline(unittest.TestCase):
    def test_cross_origin_redirect_should_strip_credentials_but_does_not(self):
        headers = {"Authorization": "Bearer SECRET", "Cookie": "sid=secret", "Proxy-Authorization": "Basic PROXY"}
        _, forwarded = UnsafeForwarder.redirect(headers, "https://attacker.example/")
        self.assertNotIn("Authorization", forwarded)
        self.assertNotIn("Cookie", forwarded)
        self.assertNotIn("Proxy-Authorization", forwarded)


if __name__ == "__main__":
    unittest.main()
