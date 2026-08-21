from __future__ import annotations
import hashlib,hmac,json,os,sqlite3,stat,uuid
from dataclasses import dataclass
from pathlib import Path
from experiments.filesystem_namespace_binding.protocol import DirectoryIdentity,NamespaceHandle
from experiments.namespace_reacquisition.protocol import HandleEvidence,name_handle
from experiments.supervisor_restart.protocol import DurableLaunchRecord,ReconcileState,reconcile

class CleanupError(RuntimeError): pass
class StaleCleanupGeneration(CleanupError): pass
class LiveOwner(CleanupError): pass
class NamespaceIdentityMismatch(CleanupError): pass
class ObjectIdentityMismatch(CleanupError): pass
class SecretIdentityMismatch(CleanupError): pass
class StrongIdentityUnavailable(CleanupError): pass
class UnknownCleanupOutcome(CleanupError): pass
class SimulatedCreationCrash(CleanupError): pass

@dataclass(frozen=True)
class FileIdentity:
    st_dev:int; st_ino:int; handle_type:int; mount_id:int; handle_hex:str

@dataclass(frozen=True)
class Lease:
    lease_id:str; task_id:str; credential_id:str; credential_generation:int; scope:str
    fingerprint:str; directory_path:str; directory:DirectoryIdentity; name:str
    file:FileIdentity|None; status:str; process_record:str|None

def fp(key,secret): return hmac.new(key,secret,hashlib.sha256).hexdigest()

def open_ns(path):
    absolute=os.path.abspath(os.fspath(path))
    try:return NamespaceHandle.authorize_beneath('/',absolute.lstrip('/'))
    except Exception as e: raise NamespaceIdentityMismatch(str(e)) from e

def _handle_for(ns,name):
    evidence=name_handle(f'/proc/self/fd/{ns.fd}/{name}')
    if evidence is None: raise StrongIdentityUnavailable('name_to_handle_at unavailable for credential fallback')
    return evidence

def _file_identity(st,evidence):
    return FileIdentity(int(st.st_dev),int(st.st_ino),int(evidence.handle_type),int(evidence.mount_id),evidence.handle_hex)

class CredentialLeaseStore:
    def __init__(self,db_path,*,audit_key):
        self.db_path=str(db_path); self.audit_key=bytes(audit_key)
        q=self._con(); q.executescript('''
        CREATE TABLE IF NOT EXISTS control(singleton INTEGER PRIMARY KEY,cleanup_generation INTEGER,current_credential_generation INTEGER);
        INSERT OR IGNORE INTO control VALUES(1,1,1);
        CREATE TABLE IF NOT EXISTS leases(
          lease_id TEXT PRIMARY KEY,task_id TEXT,credential_id TEXT,credential_generation INTEGER,scope TEXT,
          fingerprint TEXT,directory_path TEXT,directory_dev INTEGER,directory_ino INTEGER,name TEXT,
          file_dev INTEGER,file_ino INTEGER,handle_type INTEGER,mount_id INTEGER,handle_hex TEXT,status TEXT,process_record TEXT);
        CREATE TABLE IF NOT EXISTS evidence(
          lease_id TEXT PRIMARY KEY,cleanup_generation INTEGER,credential_id TEXT,credential_generation INTEGER,
          fingerprint TEXT,directory_dev INTEGER,directory_ino INTEGER,file_dev INTEGER,file_ino INTEGER,
          handle_type INTEGER,mount_id INTEGER,handle_hex TEXT,outcome TEXT);
        '''); q.close()
    def _con(self):
        q=sqlite3.connect(self.db_path,timeout=5); q.execute('PRAGMA busy_timeout=5000'); return q
    def cleanup_generation(self):
        q=self._con()
        try:return int(q.execute('SELECT cleanup_generation FROM control').fetchone()[0])
        finally:q.close()
    def current_credential_generation(self):
        q=self._con()
        try:return int(q.execute('SELECT current_credential_generation FROM control').fetchone()[0])
        finally:q.close()
    def advance_cleanup_generation(self):
        q=self._con()
        try:
            q.execute('BEGIN IMMEDIATE'); q.execute('UPDATE control SET cleanup_generation=cleanup_generation+1')
            v=int(q.execute('SELECT cleanup_generation FROM control').fetchone()[0]); q.commit(); return v
        finally:q.close()
    def rotate_credential_generation(self):
        q=self._con()
        try:
            q.execute('BEGIN IMMEDIATE'); q.execute('UPDATE control SET current_credential_generation=current_credential_generation+1')
            v=int(q.execute('SELECT current_credential_generation FROM control').fetchone()[0]); q.commit(); return v
        finally:q.close()
    def _lease(self,row):
        file=None
        if row[10] is not None:
            file=FileIdentity(int(row[10]),int(row[11]),int(row[12]),int(row[13]),row[14])
        return Lease(row[0],row[1],row[2],int(row[3]),row[4],row[5],row[6],
                     DirectoryIdentity(int(row[7]),int(row[8])),row[9],file,row[15],row[16])
    def load(self,lease_id):
        q=self._con()
        try:
            r=q.execute('SELECT * FROM leases WHERE lease_id=?',(lease_id,)).fetchone()
            if not r: raise CleanupError('unknown lease')
            return self._lease(r)
        finally:q.close()
    def _set_status(self,lease_id,old,new,*,file=None):
        q=self._con()
        try:
            q.execute('BEGIN IMMEDIATE')
            if file is None:
                changed=q.execute('UPDATE leases SET status=? WHERE lease_id=? AND status=?',(new,lease_id,old)).rowcount
            else:
                changed=q.execute('UPDATE leases SET file_dev=?,file_ino=?,handle_type=?,mount_id=?,handle_hex=?,status=? WHERE lease_id=? AND status=?',
                    (file.st_dev,file.st_ino,file.handle_type,file.mount_id,file.handle_hex,new,lease_id,old)).rowcount
            if changed!=1: raise CleanupError(f'expected {old} lease state')
            q.commit()
        except:
            if q.in_transaction:q.rollback()
            raise
        finally:q.close()
    def create_named_fallback(self,*,task_id,credential_id,scope,secret,directory,credential_generation=None,simulate_crash_after_secret_write=False,simulate_crash_after_partial_write=False):
        generation=self.current_credential_generation() if credential_generation is None else credential_generation
        absolute=os.path.abspath(os.fspath(directory)); lease_id=str(uuid.uuid4()); name=f'cred-{lease_id}.tmp'; fingerprint=fp(self.audit_key,secret)
        with open_ns(absolute) as ns:
            did=ns.directory
        q=self._con()
        try:
            q.execute('INSERT INTO leases VALUES(?,?,?,?,?,?,?,?,?,?,NULL,NULL,NULL,NULL,NULL,?,NULL)',
                (lease_id,task_id,credential_id,generation,scope,fingerprint,absolute,did.st_dev,did.st_ino,name,'PREPARED'))
            q.commit()
        finally:q.close()
        fd=None
        try:
            with open_ns(absolute) as ns:
                if ns.directory!=did: raise NamespaceIdentityMismatch('directory changed after PREPARED')
                flags=os.O_RDWR|os.O_CREAT|os.O_EXCL|os.O_CLOEXEC|getattr(os,'O_NOFOLLOW',0)
                fd=os.open(name,flags,0o600,dir_fd=ns.fd)
                os.fchmod(fd,0o600)
                st=os.fstat(fd)
                if stat.S_IMODE(st.st_mode)!=0o600 or not stat.S_ISREG(st.st_mode): raise CleanupError('bad fallback mode/type')
                os.fsync(fd); os.fsync(ns.fd)
                evidence=_handle_for(ns,name)
                fileid=_file_identity(st,evidence)
                self._set_status(lease_id,'PREPARED','ALLOCATED',file=fileid)
                if simulate_crash_after_partial_write:
                    prefix=secret[:max(1,len(secret)//2)]; os.write(fd,prefix); os.fsync(fd); raise SimulatedCreationCrash(lease_id)
                offset=0
                while offset<len(secret): offset+=os.write(fd,secret[offset:])
                os.fsync(fd)
                if simulate_crash_after_secret_write: raise SimulatedCreationCrash(lease_id)
                self._set_status(lease_id,'ALLOCATED','READY')
            return self.load(lease_id)
        except SimulatedCreationCrash:
            raise
        except Exception:
            try:
                if fd is not None:
                    with open_ns(absolute) as ns:
                        if ns.directory==did:
                            try: os.unlink(name,dir_fd=ns.fd); os.fsync(ns.fd)
                            except FileNotFoundError: pass
                q=self._con(); q.execute("UPDATE leases SET status='ABORTED' WHERE lease_id=? AND status IN ('PREPARED','ALLOCATED')",(lease_id,)); q.commit(); q.close()
            finally: raise
        finally:
            if fd is not None: os.close(fd)
    def handoff(self,lease_id,record):
        lease=self.load(lease_id)
        if record.task_id!=lease.task_id: raise CleanupError('wrong task')
        q=self._con()
        try:
            q.execute('BEGIN IMMEDIATE')
            if q.execute("UPDATE leases SET status='HANDED_OFF',process_record=? WHERE lease_id=? AND status='READY'",(record.to_json(),lease_id)).rowcount!=1: raise CleanupError('not handoff eligible')
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
        if ns.directory!=lease.directory: ns.close(); raise NamespaceIdentityMismatch('directory replaced')
        try:st=os.stat(lease.name,dir_fd=ns.fd,follow_symlinks=False)
        except FileNotFoundError: ns.close(); return None
        if lease.file is None:
            ns.close(); raise ObjectIdentityMismatch('file exists without durable strong identity')
        if not stat.S_ISREG(st.st_mode): ns.close(); raise ObjectIdentityMismatch('not regular file')
        current=_handle_for(ns,lease.name)
        expected=(lease.file.handle_type,lease.file.mount_id,lease.file.handle_hex)
        if (current.handle_type,current.mount_id,current.handle_hex)!=expected: ns.close(); raise ObjectIdentityMismatch('opaque file handle changed')
        if (int(st.st_dev),int(st.st_ino))!=(lease.file.st_dev,lease.file.st_ino): ns.close(); raise ObjectIdentityMismatch('file observation drift')
        fd=os.open(lease.name,os.O_RDONLY|os.O_CLOEXEC|os.O_NONBLOCK|getattr(os,'O_NOFOLLOW',0),dir_fd=ns.fd)
        try:
            data=b''
            while True:
                chunk=os.read(fd,65536)
                if not chunk:break
                data+=chunk
        finally:os.close(fd)
        if lease.status!='ALLOCATED' and not hmac.compare_digest(fp(self.audit_key,data),lease.fingerprint): ns.close(); raise SecretIdentityMismatch('content mismatch')
        return ns
    def cleanup(self,lease_id,*,expected_cleanup_generation,simulate_unknown_after_unlink=False):
        q=self._con(); ns=None
        try:
            q.execute('BEGIN IMMEDIATE'); gen=int(q.execute('SELECT cleanup_generation FROM control').fetchone()[0])
            if gen!=expected_cleanup_generation: raise StaleCleanupGeneration('cleanup generation changed')
            row=q.execute('SELECT * FROM leases WHERE lease_id=?',(lease_id,)).fetchone()
            if not row:raise CleanupError('unknown lease')
            lease=self._lease(row)
            if lease.status=='CLEANED':q.commit();return self.evidence(lease_id)
            if lease.status=='ABORTED':q.commit();return {'lease_id':lease_id,'status':'ABORTED'}
            if self._is_live(lease):raise LiveOwner('live process still owns file')
            ns=self._verify_exact(lease)
            outcome='MISSING_RECONCILED' if ns is None else 'UNLINKED'
            if ns is not None:os.unlink(lease.name,dir_fd=ns.fd);os.fsync(ns.fd)
            if simulate_unknown_after_unlink:raise UnknownCleanupOutcome(lease_id)
            q.execute("UPDATE leases SET status='CLEANED' WHERE lease_id=?",(lease_id,))
            f=lease.file
            q.execute('INSERT OR REPLACE INTO evidence VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)',
                (lease.lease_id,gen,lease.credential_id,lease.credential_generation,lease.fingerprint,lease.directory.st_dev,lease.directory.st_ino,
                 None if f is None else f.st_dev,None if f is None else f.st_ino,None if f is None else f.handle_type,None if f is None else f.mount_id,None if f is None else f.handle_hex,outcome))
            q.commit(); return self.evidence(lease_id)
        except:
            if q.in_transaction:q.rollback()
            raise
        finally:
            if ns is not None:ns.close()
            q.close()
    def reconcile_cleanup(self,lease_id,*,expected_cleanup_generation):
        if self.load(lease_id).status=='CLEANED':return self.evidence(lease_id)
        return self.cleanup(lease_id,expected_cleanup_generation=expected_cleanup_generation)
    def evidence(self,lease_id):
        q=self._con()
        try:
            r=q.execute('SELECT * FROM evidence WHERE lease_id=?',(lease_id,)).fetchone()
            if not r:return {'lease_id':lease_id,'status':self.load(lease_id).status}
            return {'lease_id':r[0],'cleanup_generation':int(r[1]),'credential_id':r[2],'credential_generation':int(r[3]),'fingerprint':r[4],
                    'directory':{'st_dev':int(r[5]),'st_ino':int(r[6])},
                    'file':None if r[7] is None else {'st_dev':int(r[7]),'st_ino':int(r[8]),'handle_type':int(r[9]),'mount_id':int(r[10]),'handle_hex':r[11]},
                    'outcome':r[12],'status':'CLEANED'}
        finally:q.close()

class UnsafeGlobCleanup:
    def cleanup(self,directory):
        deleted=[]
        for p in Path(directory).glob('cred-*.tmp'):p.unlink(missing_ok=True);deleted.append(p.name)
        return tuple(deleted)
