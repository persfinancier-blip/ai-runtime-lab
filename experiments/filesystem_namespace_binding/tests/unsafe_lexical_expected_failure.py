import os
import tempfile
import unittest
from pathlib import Path
from experiments.filesystem_namespace_binding.protocol import UnsafeLexicalPublisher

class UnsafeBaseline(unittest.TestCase):
    def test_same_lexical_path_should_stay_in_authorized_directory_but_does_not(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); safe=root/"safe"; attacker=root/"attacker"
            safe.mkdir(); attacker.mkdir(); alias=root/"alias"; os.symlink(safe,alias)
            publisher=UnsafeLexicalPublisher(); planned=publisher.plan(alias/"artifact.json")
            alias.unlink(); os.symlink(attacker,alias)
            publisher.publish(planned,b"secret")
            self.assertTrue((safe/"artifact.json").exists(), "lexical path was retargeted to attacker directory")

if __name__=="__main__":
    unittest.main()
