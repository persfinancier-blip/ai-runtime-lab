import unittest

from experiments.anchor_threshold_root.protocol import RootState, key_id
from experiments.sink_registry_threshold_publication.protocol import (
    UnsafeSingleSignerPublication,
    publication_entry,
    sign_publication,
)


class Unsafe(unittest.TestCase):
    def test_one_signer_should_not_publish_threshold_two_but_does(self):
        keys = [b"k0", b"k1"]
        root = RootState(
            "sink-registry", 1, 1, 2, {key_id(k): k.hex() for k in keys}
        )
        entry = publication_entry(
            root,
            sink_id="sink-A",
            generation=1,
            adapter_digest="a" * 64,
            endpoint_origin="https://evil.example",
            operation_profile="charge-v1",
        )
        sig = sign_publication(entry, keys[0])
        self.assertFalse(UnsafeSingleSignerPublication.accepts(root, entry, sig))


if __name__ == "__main__":
    unittest.main()
