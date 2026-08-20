from __future__ import annotations

import hashlib
import struct
from dataclasses import dataclass
from typing import Iterable

INCLUSION_PROOF_V2 = 0x0106
X509_ENTRY_V2 = 0x0100
PRECERT_ENTRY_V2 = 0x0101
MAX_VECTOR = (1 << 16) - 1
MIN_LOG_ID = 2
MAX_LOG_ID = 127
MIN_NODE_HASH = 32
MAX_NODE_HASH = 255

class InclusionError(ValueError): pass
class Truncated(InclusionError): pass
class TrailingData(InclusionError): pass
class WrongType(InclusionError): pass
class Malformed(InclusionError): pass
class BindingError(InclusionError): pass
class RootMismatch(InclusionError): pass

@dataclass(frozen=True)
class InclusionProofV2:
    log_id: bytes
    tree_size: int
    leaf_index: int
    inclusion_path: tuple[bytes, ...]

class _Reader:
    def __init__(self, data: bytes):
        if not isinstance(data, bytes):
            raise Malformed("wire input must be bytes")
        self.data=data; self.pos=0
    def take(self,n:int)->bytes:
        if type(n) is not int or n < 0 or self.pos+n>len(self.data):
            raise Truncated("truncated field")
        out=self.data[self.pos:self.pos+n]; self.pos+=n; return out
    def u8(self): return self.take(1)[0]
    def u16(self): return struct.unpack("!H",self.take(2))[0]
    def u64(self): return struct.unpack("!Q",self.take(8))[0]

def _validate_log_id(value: bytes) -> None:
    if not isinstance(value, bytes) or not (MIN_LOG_ID <= len(value) <= MAX_LOG_ID):
        raise Malformed("LogID length out of range")
    i=0
    while i < len(value):
        if value[i] == 0x80:
            raise Malformed("non-minimal DER OID subidentifier")
        while value[i] & 0x80:
            i += 1
            if i >= len(value):
                raise Malformed("unterminated DER OID subidentifier")
        i += 1

def _u64(value:int)->bytes:
    if type(value) is not int or not (0 <= value < 1<<64):
        raise Malformed("uint64 out of range")
    return struct.pack("!Q",value)

def _opaque8(value:bytes,lo:int,hi:int,label:str)->bytes:
    if not isinstance(value,bytes) or not (lo <= len(value) <= hi):
        raise Malformed(f"{label} length out of range")
    return bytes([len(value)])+value

def encode_inclusion_proof(item: InclusionProofV2) -> bytes:
    _validate_log_id(item.log_id)
    path=bytearray()
    for node in item.inclusion_path:
        path += _opaque8(node, MIN_NODE_HASH, MAX_NODE_HASH, "NodeHash")
    if len(path) > MAX_VECTOR:
        raise Malformed("inclusion_path exceeds 2^16-1 bytes")
    return (struct.pack("!H",INCLUSION_PROOF_V2)
            + _opaque8(item.log_id,MIN_LOG_ID,MAX_LOG_ID,"LogID")
            + _u64(item.tree_size)+_u64(item.leaf_index)
            + struct.pack("!H",len(path))+bytes(path))

def decode_inclusion_proof(data: bytes, *, hash_size:int) -> InclusionProofV2:
    if type(hash_size) is not int or not (MIN_NODE_HASH <= hash_size <= MAX_NODE_HASH):
        raise Malformed("invalid HASH_SIZE")
    r=_Reader(data)
    if r.u16()!=INCLUSION_PROOF_V2:
        raise WrongType("not inclusion_proof_v2")
    n=r.u8()
    if not (MIN_LOG_ID<=n<=MAX_LOG_ID):
        raise Malformed("LogID length out of range")
    log_id=r.take(n); _validate_log_id(log_id)
    tree_size,leaf_index=r.u64(),r.u64()
    vec_len=r.u16(); end=r.pos+vec_len
    if end>len(data): raise Truncated("truncated inclusion_path")
    nodes=[]
    while r.pos<end:
        node_len=r.u8()
        if node_len != hash_size:
            raise Malformed("NodeHash length does not match HASH_SIZE")
        if r.pos+node_len>end:
            raise Truncated("NodeHash crosses vector boundary")
        nodes.append(r.take(node_len))
    if r.pos!=end: raise Malformed("non-canonical vector boundary")
    if r.pos!=len(data): raise TrailingData("trailing bytes after TransItem")
    if tree_size == 0:
        raise Malformed("inclusion proof tree_size must be positive")
    if leaf_index >= tree_size:
        raise Malformed("leaf_index must be less than tree_size")
    return InclusionProofV2(log_id,tree_size,leaf_index,tuple(nodes))

def leaf_hash_exact(leaf_transitem: bytes, *, hash_size:int=32) -> bytes:
    if type(hash_size) is not int or hash_size != 32:
        raise Malformed("reference profile supports SHA-256/HASH_SIZE=32")
    if not isinstance(leaf_transitem,bytes) or len(leaf_transitem)<3:
        raise Malformed("leaf TransItem is truncated")
    typ=struct.unpack("!H",leaf_transitem[:2])[0]
    if typ not in {X509_ENTRY_V2,PRECERT_ENTRY_V2}:
        raise WrongType("leaf must be x509_entry_v2 or precert_entry_v2")
    return hashlib.sha256(b"\x00"+leaf_transitem).digest()

def _node_hash(left:bytes,right:bytes)->bytes:
    if len(left)!=32 or len(right)!=32:
        raise Malformed("node hash size mismatch")
    return hashlib.sha256(b"\x01"+left+right).digest()

def verify_inclusion_hash(leaf_hash:bytes, *, leaf_index:int, tree_size:int, root_hash:bytes,
                          inclusion_path:Iterable[bytes]) -> bool:
    if not isinstance(leaf_hash,bytes) or len(leaf_hash)!=32: raise Malformed("bad leaf hash")
    if not isinstance(root_hash,bytes) or len(root_hash)!=32: raise Malformed("bad root hash")
    if type(tree_size) is not int or tree_size<=0: raise Malformed("tree_size must be positive int")
    if type(leaf_index) is not int or not (0<=leaf_index<tree_size): raise Malformed("bad leaf_index")
    path=tuple(inclusion_path)
    for p in path:
        if not isinstance(p,bytes) or len(p)!=32: raise Malformed("bad inclusion node")
    fn=leaf_index; sn=tree_size-1; r=leaf_hash
    for p in path:
        if sn==0: raise Malformed("proof contains extra node")
        if (fn & 1) or fn==sn:
            r=_node_hash(p,r)
            if not (fn & 1):
                while fn!=0 and not (fn & 1):
                    fn >>= 1; sn >>= 1
        else:
            r=_node_hash(r,p)
        fn >>= 1; sn >>= 1
    if sn!=0: raise Malformed("proof ended before root")
    if r!=root_hash: raise RootMismatch("inclusion root mismatch")
    return True

def verify_authenticated_inclusion(
    leaf_transitem:bytes,
    sth_wire:bytes,
    inclusion_wire:bytes,
    profile,
) -> bool:
    from experiments.ctv2_sth_chain.protocol import authenticate_sth
    auth=authenticate_sth(sth_wire,profile)
    item=decode_inclusion_proof(inclusion_wire,hash_size=profile.hash_size)
    if item.log_id != profile.log_id:
        raise BindingError("proof LogID does not match authenticated log profile")
    if item.tree_size != auth.sth.tree_head.tree_size:
        raise BindingError("proof tree_size does not match authenticated STH")
    leaf_hash=leaf_hash_exact(leaf_transitem,hash_size=profile.hash_size)
    return verify_inclusion_hash(
        leaf_hash,
        leaf_index=item.leaf_index,
        tree_size=item.tree_size,
        root_hash=auth.sth.tree_head.root_hash,
        inclusion_path=item.inclusion_path,
    )

def unsafe_verify_supplied_leaf_hash(
    supplied_leaf_hash:bytes,
    sth_wire:bytes,
    inclusion_wire:bytes,
    profile,
) -> bool:
    """Deliberately unsafe: caller supplies the leaf hash; exact leaf bytes are not bound."""
    from experiments.ctv2_sth_chain.protocol import authenticate_sth
    auth=authenticate_sth(sth_wire,profile)
    item=decode_inclusion_proof(inclusion_wire,hash_size=profile.hash_size)
    if item.log_id != profile.log_id or item.tree_size != auth.sth.tree_head.tree_size:
        raise BindingError("proof/STH binding failed")
    return verify_inclusion_hash(
        supplied_leaf_hash,
        leaf_index=item.leaf_index,
        tree_size=item.tree_size,
        root_hash=auth.sth.tree_head.root_hash,
        inclusion_path=item.inclusion_path,
    )
