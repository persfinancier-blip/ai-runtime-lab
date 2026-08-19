import unittest
from experiments.ephemeral_credentials.protocol import unsafe_argv, unsafe_env

SECRET = "s3cr3t-low-entropy"

class UnsafeBaselines(unittest.TestCase):
    def test_raw_secret_should_not_be_in_argv_but_is(self):
        self.assertNotIn(SECRET, " ".join(unsafe_argv("tool", SECRET)))

    def test_raw_secret_should_not_be_in_environment_but_is(self):
        self.assertNotIn(SECRET, repr(unsafe_env(SECRET)))

if __name__ == "__main__": unittest.main()
