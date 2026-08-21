import os,tempfile,unittest
from pathlib import Path
from experiments.memfd_credential_transport.protocol import UnsafeNamedPath

SECRET=b'memfd-secret-value'

class UnsafeNamedPathBaseline(unittest.TestCase):
    def test_named_file_should_disappear_with_transport_lifetime_but_does_not(self):
        with tempfile.TemporaryDirectory() as td:
            path=UnsafeNamedPath().create(td,SECRET)
            fd=os.open(path,os.O_RDONLY|os.O_CLOEXEC)
            os.close(fd)
            self.assertFalse(Path(path).exists(), 'ordinary named secret outlived all open transport descriptors')

if __name__=='__main__':unittest.main()
