from __future__ import annotations
import hashlib,hmac,json,os,sqlite3,stat,uuid
from dataclasses import dataclass
from pathlib import Path
from experiments.filesystem_namespace_binding.protocol import DirectoryIdentity,NamespaceHandle
from experiments.supervisor_restart.protocol import DurableLaunchRecord,ReconcileState,reconcile

class CleanupError(RuntimeError): pass
class StaleCleanupGeneration(CleanupError): pass
class LiveOwner(CleanupError): pass
class NamespaceIdentityMismatch(CleanupError): pass
class ObjectIdentityMismatch(CleanupError): pass
class SecretIdentityMismatch(CleanupError): pass
class UnknownCleanupOutcome(CleanupError): pass

@dataclass(frozen=True)
class FileIdentity:
    st_dev:int; st_ino:int; st_ctime_ns:int

@dataclass(frozen=True)
class Lease:
    lease_id:str; task_id:str; credential_id:str; credential_generation:int; scope:str
    fingerprint:str; directory_path:str; directory:DirectoryIdentity; name:str
    file:FileIdentity; status:str; process_record:str|None

def fp(key,secret): return hmac.new(key,secret,hashlib.sha256).hexdigest()
def fid(st): return FileIdentity(int(st.st_dev),int(st.st_ino),int(st.st_ctime_ns))

def open_ns(path):
    absolute=os.path.abspath(os.fspath(path))
    try:return NamespaceHandle.authorize_beneath("/",absolute.lstrip("/"))
    except Exception as e: raise NamespaceIdentityMismatch(str(e)) from e

class CredentialLeaseStore:
    def __init__(self,db_path,*,audit_key):
        self.db_path=str(db_path); self.audit_key=bytes(audit_key)
        q=self._con(); q.executescript("""
        CREATE TABLE IF NOT EXISTS control(singleton INTEGER PRIMARY KEY,cleanup_generation INTEGER,current_credential_generation INTEGER);
        INSERT OR IGNORE INTO control VALUES(1,1,1);
        CREATE TABLE IF NOT EXISTS leases(
          lease_id TEXT PRIMARY KEY,task_id TEXT,credential_id TEXT,credential_generation INTEGER,scope TEXT,
          fingerprint TEXT,directory_path TEXT,directory_dev INTEGER,directory_ino INTEGER,name TEXT,
          file_dev INTEGER,file_ino INTEGER,file_ctime_ns INTEGER,status TEXT,process_record TEXT);
        CREATE TABLE IF NOT EXISTS evidence(
          lease_id TEXT PRIMARY KEY,cleanup_generation INTEGER,credential_id TEXT,credential_generation INTEGER,
          fingerprint TEXT,directory_dev INTEGER,directory_ino INTEGER,file_dev INTEGER,file_ino INTEGER,file_ctime_ns INTEGER,outcome TEXT);
        """); q.close()
    def _con(self):
        q=sqlite3.connect(self.db_path,timeout=5); q.execute("PRAGMA busy_timeout=5000"); return q
    def cleanup_generation(self):
        q=self._con()
        try:return int(q.execute("SELECT cleanup_generation FROM control").fetchone()[0])
        finally:q.close()
    def current_credential_generation(self):
        q=self._con()
        try:return int(q.execute("SELECT current_credential_generation FROM control").fetchone()[0])
        finally:q.close()
    def advance_cleanup_generation(self):
        q=self._con()
        try:
            q.execute("BEGIN IMMEDIATE"); q.execute("UPDATE control SET cleanup_generation=cleanup_generation+1")
            v=int(q.execute("SELECT cleanup_generation FROM control").fetchone()[0]); q.commit(); return v
        finally:q.close()
    def rotate_credential_generation(self):
        q=self._con()
        try:
            q.execute("BEGIN IMMEDIATE"); q.execute("UPDATE control SET current_credential_generation=current_credential_generation+1")
            v=int(q.execute("SELECT current_credential_generation FROM control").fetchone()[0]); q.commit(); return v
        finally:q.close()
    def _lease(self,row):
        return Lease(row[0],row[1],row[2],int(row[3]),row[4],row[5],row[6],
                     DirectoryIdentity(int(row[7]),int(row[8])),row[9],FileIdentity(int(row[10]),int(row[11]),int(row[12])),row[13],row[14])
    def load(self,lease_id):
        q=self._con()
        try:
            r=q.execute("SELECT * FROM leases WHERE lease_id=?",(lease_id,)).fetchone()
            if not r: raise CleanupError("unknown lease")
            return self._lease(r)
        finally:q.close()
    def create_named_fallback(self,*,task_id,credential_id,scope,secret,directory,credential_generation=None):
        generation=self.current_credential_generation() if credential_generation is None else credential_generation
        absolute=os.path.abspath(os.fspath(directory)); lease_id=str(uuid.uuid4()); name=f"cred-{lease_id}.tmp"
        with open_ns(absolute) as ns:
            flags=os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_CLOEXEC|getattr(os,"O_NOFOLLOW",0)
            fd=os.open(name,flags,0o600,dir_fd=ns.fd)
            try:
                os.fchmod(fd,0o600); os.write(fd,secret); os.fsync(fd); st=os.fstat(fd)
            finally: os.close(fd)
            os.fsync(ns.fd)
            if stat.S_IMODE(st.st_mode)!=0o600 or not stat.S_ISREG(st.st_mode): raise CleanupError("bad fallback mode/type")
            did=ns.directory; fileid=fid(st)
        q=self._con()
        try:
            q.execute("INSERT INTO leases VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,NULL)",
                      (lease_id,task_id,credential_id,generation,scope,fp(self.audit_key,secret),absolute,did.st_dev,did.st_ino,name,fileid.st_dev,fileid.st_ino,fileid.st_ctime_ns,"CREATED"))
            q.commit()
        except:
            try:
                with open_ns(absolute) as ns:
                    if ns.directory==did:
                        st=os.stat(name,dir_fd=ns.fd,follow_symlinks=False)
                        if fid(st)==fileid: os.unlink(name,dir_fd=ns.fd); os.fsync(ns.fd)
            finally: raise
        return self.load(lease_id)
    def handoff(self,lease_id,record):
        lease=self.load(lease_id)
        if record.task_id!=lease.task_id: raise CleanupError("wrong task")
        q=self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            if q.execute("UPDATE leases SET status='HANDED_OFF',process_record=? WHERE lease_id=? AND status='CREATED'",(record.to_json(),lease_id)).rowcount!=1:
                raise CleanupError("not handoff eligible")
            q.commit()
        except:
            if q.in_transaction:q.rollback()
            raise
        finally:q.close()
        return self.load(lease_id)
    def _is_live(self,lease):
        if not lease.process_record:return False
        record=DurableLaunchRecord.from_json(lease.process_record)
        state,authority,_=reconcile(record,record.generations,expected_task_id=lease.task_id)
        try:return state is ReconcileState.SAME_INSTANCE and authority is not None
        finally:
            if authority is not None: os.close(authority.pidfd)
    def _verify_exact(self,lease):
        ns=open_ns(lease.directory_path)
        if ns.directory!=lease.directory: ns.close(); raise NamespaceIdentityMismatch("directory replaced")
        try:st=os.stat(lease.name,dir_fd=ns.fd,follow_symlinks=False)
        except FileNotFoundError: ns.close(); return None
        if not stat.S_ISREG(st.st_mode) or fid(st)!=lease.file: ns.close(); raise ObjectIdentityMismatch("file replaced")
        fd=os.open(lease.name,os.O_RDONLY|os.O_CLOEXEC|os.O_NONBLOCK|getattr(os,"O_NOFOLLOW",0),dir_fd=ns.fd)
        try:
            if fid(os.fstat(fd))!=lease.file: raise ObjectIdentityMismatch("opened object drift")
            data=b""
            while True:
                chunk=os.read(fd,65536)
                if not chunk:break
                data+=chunk
        finally:os.close(fd)
        if not hmac.compare_digest(fp(self.audit_key,data),lease.fingerprint): ns.close(); raise SecretIdentityMismatch("content mismatch")
        return ns
    def cleanup(self,lease_id,*,expected_cleanup_generation,simulate_unknown_after_unlink=False):
        q=self._con(); ns=None
        try:
            q.execute("BEGIN IMMEDIATE")
            gen=int(q.execute("SELECT cleanup_generation FROM control").fetchone()[0])
            if gen!=expected_cleanup_generation: raise StaleCleanupGeneration("cleanup generation changed")
            row=q.execute("SELECT * FROM leases WHERE lease_id=?",(lease_id,)).fetchone()
            if not row:raise CleanupError("unknown lease")
            lease=self._lease(row)
            if lease.status=="CLEANED":q.commit();return self.evidence(lease_id)
            if self._is_live(lease):raise LiveOwner("live process still owns file")
            ns=self._verify_exact(lease)
            outcome="MISSING_RECONCILED" if ns is None else "UNLINKED"
            if ns is not None:os.unlink(lease.name,dir_fd=ns.fd);os.fsync(ns.fd)
            if simulate_unknown_after_unlink:raise UnknownCleanupOutcome(lease_id)
            q.execute("UPDATE leases SET status='CLEANED' WHERE lease_id=?",(lease_id,))
            q.execute("INSERT OR REPLACE INTO evidence VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                      (lease.lease_id,gen,lease.credential_id,lease.credential_generation,lease.fingerprint,
                       lease.directory.st_dev,lease.directory.st_ino,lease.file.st_dev,lease.file.st_ino,lease.file.st_ctime_ns,outcome))
            q.commit(); return self.evidence(lease_id)
        except:
            if q.in_transaction:q.rollback()
            raise
        finally:
            if ns is not None:ns.close()
            q.close()
    def reconcile_cleanup(self,lease_id,*,expected_cleanup_generation):
        if self.load(lease_id).status=="CLEANED":return self.evidence(lease_id)
        return self.cleanup(lease_id,expected_cleanup_generation=expected_cleanup_generation)
    def evidence(self,lease_id):
        q=self._con()
        try:
            r=q.execute("SELECT * FROM evidence WHERE lease_id=?",(lease_id,)).fetchone()
            if not r:return {"lease_id":lease_id,"status":self.load(lease_id).status}
            return {"lease_id":r[0],"cleanup_generation":int(r[1]),"credential_id":r[2],"credential_generation":int(r[3]),
                    "fingerprint":r[4],"directory":{"st_dev":int(r[5]),"st_ino":int(r[6])},
                    "file":{"st_dev":int(r[7]),"st_ino":int(r[8]),"st_ctime_ns":int(r[9])},"outcome":r[10],"status":"CLEANED"}
        finally:q.close()

class UnsafeGlobCleanup:
    def cleanup(self,directory):
        deleted=[]
        for p in Path(directory).glob("cred-*.tmp"):p.unlink(missing_ok=True);deleted.append(p.name)
        return tuple(deleted)
