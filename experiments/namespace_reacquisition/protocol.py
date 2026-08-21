from __future__ import annotations
import ctypes, errno, hashlib, hmac, json, os, stat
from dataclasses import asdict, dataclass
from pathlib import Path

AT_FDCWD = -100
MAX_HANDLE_SZ = 128

class ReacquisitionError(RuntimeError): pass
class AuthenticationError(ReacquisitionError): pass
class PathReplaced(ReacquisitionError): pass
class PathMissing(ReacquisitionError): pass
class UnsupportedStrongReacquisition(ReacquisitionError): pass
class HandleStale(ReacquisitionError): pass
class StaleGeneration(ReacquisitionError): pass
class MigrationError(ReacquisitionError): pass

@dataclass(frozen=True)
class HandleEvidence:
    handle_type: int
    mount_id: int
    handle_hex: str

@dataclass(frozen=True)
class ContinuityRecord:
    schema_version: int
    archive_path: str
    namespace_generation: int
    boot_id: str
    st_dev: int
    st_ino: int
    handle: HandleEvidence | None
    mac: str

    def unsigned(self):
        d=asdict(self); d.pop("mac")
        return d

    @property
    def record_id(self):
        return hashlib.sha256(canon(self.unsigned())).hexdigest()

@dataclass(frozen=True)
class MigrationPermit:
    old_record_id: str
    new_path: str
    new_generation: int
    mac: str
    def unsigned(self):
        return {"old_record_id":self.old_record_id,"new_path":self.new_path,"new_generation":self.new_generation}

def canon(obj): return json.dumps(obj,sort_keys=True,separators=(",",":")).encode()
def mac(key,obj): return hmac.new(key,canon(obj),hashlib.sha256).hexdigest()
def boot_id():
    return Path("/proc/sys/kernel/random/boot_id").read_text().strip()

def _lexical_abs(path):
    p=os.path.abspath(os.fspath(path))
    if not p.startswith("/") or p=="/": raise ReacquisitionError("archive path must be non-root absolute path")
    return p

def _open_no_symlink_dir(path):
    path=_lexical_abs(path)
    parts=Path(path).parts[1:]
    flags=os.O_RDONLY|os.O_DIRECTORY|os.O_CLOEXEC|getattr(os,"O_NOFOLLOW",0)
    fd=os.open("/",flags)
    try:
        for part in parts:
            try:
                nxt=os.open(part,flags,dir_fd=fd)
            except FileNotFoundError as exc:
                raise PathMissing(path) from exc
            except OSError as exc:
                if exc.errno in {errno.ELOOP,errno.ENOTDIR}: raise PathReplaced(path) from exc
                raise
            os.close(fd); fd=nxt
        return fd
    except:
        os.close(fd); raise

class _FileHandle(ctypes.Structure):
    _fields_=[("handle_bytes",ctypes.c_uint),("handle_type",ctypes.c_int),("f_handle",ctypes.c_ubyte*MAX_HANDLE_SZ)]

def name_handle(path):
    libc=ctypes.CDLL(None,use_errno=True)
    fn=getattr(libc,"name_to_handle_at",None)
    if fn is None: return None
    fh=_FileHandle(); fh.handle_bytes=MAX_HANDLE_SZ
    mount_id=ctypes.c_int()
    rc=fn(AT_FDCWD,os.fsencode(path),ctypes.byref(fh),ctypes.byref(mount_id),0)
    if rc<0:
        e=ctypes.get_errno()
        if e in {errno.ENOSYS,errno.EOPNOTSUPP,errno.ENOTSUP,errno.EPERM,errno.EACCES}: return None
        if e==errno.ENOENT: raise PathMissing(path)
        if e==errno.ESTALE: raise HandleStale(path)
        raise OSError(e,os.strerror(e))
    raw=bytes(fh.f_handle[:fh.handle_bytes])
    return HandleEvidence(fh.handle_type,mount_id.value,raw.hex())

def capture(path,key,generation=1):
    if type(generation) is not int or generation<1: raise ValueError("generation")
    p=_lexical_abs(path)
    fd=_open_no_symlink_dir(p)
    try: st=os.fstat(fd)
    finally: os.close(fd)
    h=name_handle(p)
    unsigned={
        "schema_version":1,"archive_path":p,"namespace_generation":generation,"boot_id":boot_id(),
        "st_dev":st.st_dev,"st_ino":st.st_ino,
        "handle":None if h is None else asdict(h),
    }
    return ContinuityRecord(
        schema_version=1, archive_path=p, namespace_generation=generation, boot_id=unsigned["boot_id"],
        st_dev=st.st_dev, st_ino=st.st_ino, handle=h, mac=mac(key,unsigned)
    )

def verify_record(record,key):
    if type(record.schema_version) is not int or record.schema_version!=1: raise AuthenticationError("schema")
    if type(record.namespace_generation) is not int or record.namespace_generation<1: raise AuthenticationError("generation")
    if not hmac.compare_digest(record.mac,mac(key,record.unsigned())): raise AuthenticationError("record MAC")
    return record

def issue_migration(record,new_path,new_generation,key):
    verify_record(record,key)
    if new_generation!=record.namespace_generation+1: raise MigrationError("migration generation")
    u={"old_record_id":record.record_id,"new_path":_lexical_abs(new_path),"new_generation":new_generation}
    return MigrationPermit(**u,mac=mac(key,u))

def migrate(record,permit,key):
    verify_record(record,key)
    if not hmac.compare_digest(permit.mac,mac(key,permit.unsigned())): raise MigrationError("permit MAC")
    if permit.old_record_id!=record.record_id: raise MigrationError("wrong predecessor")
    if permit.new_generation!=record.namespace_generation+1: raise MigrationError("stale generation")
    return capture(permit.new_path,key,permit.new_generation)

def reacquire(record,key,*,require_strong=True):
    verify_record(record,key)
    p=record.archive_path
    try:
        fd=_open_no_symlink_dir(p)
    except PathMissing:
        if record.handle is not None and require_strong:
            return {"status":"UNSUPPORTED_STRONG_REACQUISITION","reason":"path missing; opaque reopen capability not demonstrated"}
        return {"status":"PATH_MISSING"}
    except PathReplaced:
        return {"status":"PATH_REPLACED"}
    try: st=os.fstat(fd)
    finally: os.close(fd)

    if record.boot_id != boot_id():
        return {"status":"UNSUPPORTED_STRONG_REACQUISITION","reason":"boot changed; current runtime cannot reopen saved handle"}
    try:
        current_handle=name_handle(p)
    except HandleStale:
        return {"status":"HANDLE_STALE"}
    if record.handle is not None:
        if current_handle is None:
            return {"status":"UNSUPPORTED_STRONG_REACQUISITION","reason":"saved strong handle exists but current handle capture unavailable"}
        if (current_handle.handle_type,current_handle.handle_hex,current_handle.mount_id)!=(record.handle.handle_type,record.handle.handle_hex,record.handle.mount_id):
            return {"status":"PATH_REPLACED"}
        if (record.st_dev,record.st_ino)!=(st.st_dev,st.st_ino):
            return {"status":"PATH_REPLACED"}
        return {"status":"REACQUIRED","strength":"SAME_BOOT_OPAQUE_HANDLE_MATCH","namespace_generation":record.namespace_generation}

    same_boot = record.boot_id == boot_id()
    inode_match=(record.st_dev,record.st_ino)==(st.st_dev,st.st_ino)
    if require_strong:
        return {"status":"UNSUPPORTED_STRONG_REACQUISITION","same_boot":same_boot,"inode_match":inode_match}
    if same_boot and inode_match:
        return {"status":"REACQUIRED","strength":"SAME_BOOT_INODE_OBSERVATION","namespace_generation":record.namespace_generation}
    return {"status":"PATH_REPLACED"}

def detached_classification(record,key):
    verify_record(record,key)
    result=reacquire(record,key,require_strong=True)
    if result["status"]=="UNSUPPORTED_STRONG_REACQUISITION" and record.handle is not None:
        return {"status":"UNSUPPORTED_STRONG_REACQUISITION","detached_possible":True}
    return result

class UnsafePathBytesTrust:
    def trust(self,path,expected_files):
        p=Path(path)
        return p.exists() and all((p/name).read_bytes()==data for name,data in expected_files.items())
