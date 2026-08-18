from __future__ import annotations
import sqlite3, time, uuid
from contextlib import contextmanager
from pathlib import Path

SCHEMA = '''
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS work(
  work_id TEXT PRIMARY KEY,
  phase TEXT NOT NULL DEFAULT 'NEW',
  generation INTEGER NOT NULL DEFAULT 0,
  fence INTEGER NOT NULL DEFAULT 0,
  owner TEXT,
  lease_until REAL,
  effect_key TEXT UNIQUE,
  effect_receipt TEXT,
  done_evidence_id TEXT,
  CHECK (phase IN ('NEW','INTENT','UNKNOWN','CONFIRMED','DONE'))
);
CREATE TABLE IF NOT EXISTS evidence(
  evidence_id TEXT PRIMARY KEY,
  work_id TEXT NOT NULL,
  artifact_version TEXT NOT NULL,
  valid INTEGER NOT NULL DEFAULT 1,
  payload TEXT NOT NULL,
  created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS outbox(
  event_id TEXT PRIMARY KEY,
  work_id TEXT NOT NULL,
  kind TEXT NOT NULL,
  dedupe_key TEXT NOT NULL UNIQUE,
  payload TEXT NOT NULL,
  published INTEGER NOT NULL DEFAULT 0
);
'''

class Conflict(RuntimeError): pass
class StaleFence(RuntimeError): pass
class InvalidCompletion(RuntimeError): pass

class Kernel:
    def __init__(self, path: str|Path):
        self.path=str(path)
        c=self._conn(); c.executescript(SCHEMA); c.close()
    def _conn(self, timeout=0.2):
        c=sqlite3.connect(self.path, timeout=timeout, isolation_level=None, check_same_thread=False)
        c.row_factory=sqlite3.Row
        c.execute('PRAGMA foreign_keys=ON')
        c.execute('PRAGMA busy_timeout=200')
        return c
    @contextmanager
    def tx(self, immediate=True, timeout=0.2):
        c=self._conn(timeout)
        try:
            c.execute('BEGIN IMMEDIATE' if immediate else 'BEGIN')
            yield c
            c.commit()
        except Exception:
            c.rollback(); raise
        finally: c.close()
    def ensure_work(self, work_id):
        with self.tx() as c:
            c.execute('INSERT OR IGNORE INTO work(work_id) VALUES (?)',(work_id,))
    def claim(self, work_id, owner, ttl=30):
        self.ensure_work(work_id)
        now=time.time()
        with self.tx() as c:
            row=c.execute('SELECT * FROM work WHERE work_id=?',(work_id,)).fetchone()
            if row['owner'] and row['lease_until'] and row['lease_until']>now and row['owner']!=owner:
                raise Conflict('lease held')
            new_fence=row['fence']+1
            new_gen=row['generation']+1
            c.execute('UPDATE work SET owner=?, lease_until=?, fence=?, generation=? WHERE work_id=? AND generation=?',
                      (owner,now+ttl,new_fence,new_gen,work_id,row['generation']))
            if c.total_changes!=1: raise Conflict('claim CAS failed')
            return new_fence,new_gen
    def state(self, work_id):
        c=self._conn(); r=c.execute('SELECT * FROM work WHERE work_id=?',(work_id,)).fetchone(); c.close(); return dict(r) if r else None
    def prepare_intent(self, work_id, owner, fence, effect_key):
        with self.tx() as c:
            r=c.execute('SELECT * FROM work WHERE work_id=?',(work_id,)).fetchone()
            self._owner(r,owner,fence)
            c.execute("UPDATE work SET phase='INTENT', effect_key=?, generation=generation+1 WHERE work_id=?",(effect_key,work_id))
            c.execute("INSERT OR IGNORE INTO outbox(event_id,work_id,kind,dedupe_key,payload) VALUES (?,?,?,?,?)",
                      (str(uuid.uuid4()),work_id,'effect-intent',effect_key,'{}'))
    def confirm_effect(self, work_id, owner, fence, receipt):
        with self.tx() as c:
            r=c.execute('SELECT * FROM work WHERE work_id=?',(work_id,)).fetchone(); self._owner(r,owner,fence)
            c.execute("UPDATE work SET phase='CONFIRMED', effect_receipt=?, generation=generation+1 WHERE work_id=?",(receipt,work_id))
    def mark_unknown(self, work_id, owner, fence):
        with self.tx() as c:
            r=c.execute('SELECT * FROM work WHERE work_id=?',(work_id,)).fetchone(); self._owner(r,owner,fence)
            c.execute("UPDATE work SET phase='UNKNOWN', generation=generation+1 WHERE work_id=?",(work_id,))
    def append_evidence(self, work_id, evidence_id, version, payload='ok'):
        with self.tx() as c:
            c.execute('INSERT OR IGNORE INTO evidence VALUES (?,?,?,?,?,?)',(evidence_id,work_id,version,1,payload,time.time()))
    def invalidate(self, evidence_id):
        with self.tx() as c: c.execute('UPDATE evidence SET valid=0 WHERE evidence_id=?',(evidence_id,))
    def complete(self, work_id, owner, fence, evidence_id):
        with self.tx() as c:
            r=c.execute('SELECT * FROM work WHERE work_id=?',(work_id,)).fetchone(); self._owner(r,owner,fence)
            e=c.execute('SELECT * FROM evidence WHERE evidence_id=? AND work_id=?',(evidence_id,work_id)).fetchone()
            if not e or not e['valid']: raise InvalidCompletion('missing/invalid evidence')
            if r['phase']!='CONFIRMED': raise InvalidCompletion('effect not confirmed')
            c.execute("UPDATE work SET phase='DONE', done_evidence_id=?, generation=generation+1 WHERE work_id=? AND fence=?",
                      (evidence_id,work_id,fence))
            if c.total_changes!=1: raise StaleFence('completion lost fence')
    def _owner(self,r,owner,fence):
        if not r or r['owner']!=owner or r['fence']!=fence: raise StaleFence('stale owner/fence')

def unsafe_split_complete(path, work_id, evidence_id):
    c=sqlite3.connect(path, isolation_level=None)
    ok=c.execute('SELECT valid FROM evidence WHERE evidence_id=?',(evidence_id,)).fetchone()
    c.close()
    if not ok or ok[0]!=1: raise InvalidCompletion('invalid evidence')
    return True
