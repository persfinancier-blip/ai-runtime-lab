import unittest
from experiments.transport_binding.protocol import FakeConnector, FakeResolver, Resolution, RequestIdentity, UnsafeResolveOnceExecutor, canonical_https_url

class UnsafeBaseline(unittest.TestCase):
    def test_resolve_once_check_then_connect_should_not_rebind_but_does(self):
        resolver=FakeResolver({'trusted.example':[
            Resolution('trusted.example',['93.184.216.34']),
            Resolution('trusted.example',['127.0.0.1']),
        ]})
        connector=FakeConnector()
        identity=RequestIdentity('permit-1','effect-abc','payload-hash',canonical_https_url('https://trusted.example/upload'),'report',7)
        receipt=UnsafeResolveOnceExecutor(resolver,connector).execute(url='https://trusted.example/upload',identity=identity)
        self.assertEqual(receipt['endpoint'],'93.184.216.34','unsafe resolve-once design connected to rebound endpoint')

if __name__=='__main__': unittest.main()
