from __future__ import annotations
import sqlite3
from pathlib import Path
from .protocol import VersionedState, FutureVersionError, OldWorkerError, MigrationError

DDL='''CREATE TABLE IF NOT EXISTS work(work_id TEXT PRIMARY KEY,storage_version INTEGER NOT NULL,protocol_version INTEGER NOT NULL,migration_epoch INTEGER NOT NULL,worker_epoch INTEGER NOT NULL,phase TEXT NOT NULL,fence INTEGER NOT NULL,generation INTEGER NOT NULL,effect_key TEXT,effect_receipt TEXT,evidence_id TEXT,artifact_version TEXT,migration_marker TEXT);'''

class SQLiteVersionedKernel:
    def __init__(self,path:str|Path): self.path=str(path); c=sqlite3.connect(self.path); c.execute(DDL); c.commit(); c.close()
    def put(self,s):
        c=sqlite3.connect(self.path); c.execute('DELETE FROM work WHERE work_id=?',(s.work_id,)); c.execute('INSERT INTO work VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)',(s.work_id,s.storage_version,s.protocol_version,s.migration_epoch,s.worker_epoch,s.phase,s.fence,s.generation,s.effect_key,s.effect_receipt,s.evidence_id,s.artifact_version,s.migration_marker)); c.commit(); c.close()
    def get(self,work_id):
        c=sqlite3.connect(self.path); r=c.execute('SELECT * FROM work WHERE work_id=?',(work_id,)).fetchone(); c.close(); return VersionedState(*r)
    def migrate_v1_to_v2(self,work_id,*,crash=False):
        c=sqlite3.connect(self.path,isolation_level=None)
        try:
            c.execute('BEGIN IMMEDIATE'); s=VersionedState(*c.execute('SELECT * FROM work WHERE work_id=?',(work_id,)).fetchone())
            if s.storage_version>2 or s.protocol_version>2: raise FutureVersionError('future state')
            if s.storage_version==2: c.commit(); return s
            if s.storage_version!=1: raise MigrationError('unsupported source')
            if crash: c.execute("UPDATE work SET migration_marker='v1->v2' WHERE work_id=?",(work_id,)); raise MigrationError('injected crash')
            epoch=max(s.migration_epoch,s.worker_epoch)+1
            c.execute('UPDATE work SET storage_version=2,protocol_version=2,migration_epoch=?,worker_epoch=?,fence=fence+1,generation=generation+1,migration_marker=NULL WHERE work_id=? AND storage_version=1',(epoch,epoch,work_id)); c.commit(); return self.get(work_id)
        except Exception: c.rollback(); raise
        finally: c.close()
    def mutate_phase(self,work_id,worker_epoch,fence,phase):
        c=sqlite3.connect(self.path,isolation_level=None)
        try:
            c.execute('BEGIN IMMEDIATE'); r=c.execute('SELECT migration_epoch,worker_epoch,fence FROM work WHERE work_id=?',(work_id,)).fetchone()
            if worker_epoch<r[0] or worker_epoch<r[1] or fence!=r[2]: raise OldWorkerError('stale authority')
            c.execute('UPDATE work SET phase=?,generation=generation+1 WHERE work_id=?',(phase,work_id)); c.commit()
        except Exception: c.rollback(); raise
        finally: c.close()
