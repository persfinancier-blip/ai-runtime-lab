from __future__ import annotations

import hashlib, hmac, json, os, sqlite3, tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

SCHEMA=1
PROTOCOL="lab061-pruning-v1"

class PruneError(RuntimeError): pass
class IntegrityError(PruneError): pass
class AuthenticationError(PruneError): pass
class StaleCheckpoint(PruneError): pass
class ArchiveError(PruneError): pass
class HeadMismatch(PruneError): pass
class UnknownOutcome(PruneError): pass

def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()
def sha(x:bytes): return hashlib.sha256(x).hexdigest()
def mac(key:bytes,obj): return hmac.new(key,canon(obj),hashlib.sha256).hexdigest()
def strict_int(x,name,minimum=0):
    if type(x) is not int or x<minimum: raise AuthenticationError(f"invalid {name}")
def strict_hex(x,name,n=64):
    if type(x) is not str or len(x)!=n: raise AuthenticationError(f"invalid {name}")
    try: bytes.fromhex(x)
    except ValueError as e: raise AuthenticationError(f"invalid {name}") from e

def row_obj(row):
    names=("sequence","proposal_id","transition_digest","kind","predecessor_root_id",
           "predecessor_recovery_id","successor_root_id","successor_recovery_id","proof_json")
    return dict(zip(names,row))

def seed_commitment(bootstrap_root_id,bootstrap_recovery_id):
    return sha(canon({"kind":"lab061-prefix-seed","bootstrap_root_id":bootstrap_root_id,
                      "bootstrap_recovery_id":bootstrap_recovery_id,"protocol":PROTOCOL}))
def advance_commitment(previous,row):
    return sha(bytes.fromhex(previous)+canon(row_obj(row)))

@dataclass(frozen=True)
class CompactCheckpoint:
    schema_version:int
    protocol_version:str
    history_id:str
    sequence:int
    root_id:str
    recovery_id:str
    prefix_commitment:str
    base_sequence:int
    base_archive_id:str|None
    external_anchor_id:str
    signer_id:str
    signature:str
    @property
    def unsigned(self):
        d=asdict(self); d.pop("signature"); return d
    @property
    def checkpoint_id(self): return sha(canon(asdict(self)))
    @classmethod
    def parse(cls,raw):
        x=json.loads(raw) if isinstance(raw,str) else dict(raw)
        if set(x)!=set(cls.__dataclass_fields__): raise AuthenticationError("checkpoint fields")
        strict_int(x["schema_version"],"schema_version",1)
        strict_int(x["sequence"],"sequence")
        strict_int(x["base_sequence"],"base_sequence")
        for k in ("protocol_version","external_anchor_id"):
            if type(x[k]) is not str or not x[k]: raise AuthenticationError(k)
        for k in ("history_id","root_id","recovery_id","prefix_commitment","signature"):
            strict_hex(x[k],k)
        strict_hex(x["signer_id"],"signer_id",16)
        if x["base_archive_id"] is not None: strict_hex(x["base_archive_id"],"base_archive_id")
        if x["base_sequence"]>x["sequence"]: raise AuthenticationError("base beyond checkpoint")
        return cls(**x)

@dataclass(frozen=True)
class ArchiveManifest:
    schema_version:int
    protocol_version:str
    history_id:str
    archive_id:str
    previous_archive_id:str|None
    start_sequence:int
    end_sequence:int
    start_commitment:str
    end_commitment:str
    end_root_id:str
    end_recovery_id:str
    checkpoint_id:str
    artifact_sha256:str
    row_count:int
    @classmethod
    def parse(cls,raw):
        x=json.loads(raw) if isinstance(raw,str) else dict(raw)
        if set(x)!=set(cls.__dataclass_fields__): raise ArchiveError("manifest fields")
        for k in ("schema_version","start_sequence","end_sequence","row_count"):
            if type(x[k]) is not int: raise ArchiveError(k)
        if x["start_sequence"]<1 or x["end_sequence"]<x["start_sequence"]-1 or x["row_count"]<0:
            raise ArchiveError("manifest range")
        for k in ("history_id","archive_id","start_commitment","end_commitment","end_root_id",
                  "end_recovery_id","checkpoint_id","artifact_sha256"):
            try: strict_hex(x[k],k)
            except AuthenticationError as e: raise ArchiveError(str(e)) from e
        if x["previous_archive_id"] is not None:
            try: strict_hex(x["previous_archive_id"],"previous_archive_id")
            except AuthenticationError as e: raise ArchiveError(str(e)) from e
        return cls(**x)
