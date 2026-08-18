from __future__ import annotations
import argparse, json, os, platform, sqlite3, statistics, tempfile, threading, time, uuid
from pathlib import Path
from experiments.transactional_kernel.kernel import Kernel, Conflict, StaleFence, InvalidCompletion

PAYLOADS={"small":32,"large":65536}

def p95(xs):
    ys=sorted(xs); return ys[max(0, min(len(ys)-1, int(len(ys)*0.95)-1))]

def db_bytes(path):
    total=0
    for suffix in ("", "-wal", "-shm"):
        p=Path(str(path)+suffix)
        if p.exists(): total += p.stat().st_size
    return total

def minimal_once(path, idx, payload):
    c=sqlite3.connect(path, isolation_level=None)
    c.execute('PRAGMA journal_mode=WAL')
    c.execute('CREATE TABLE IF NOT EXISTS result(work_id TEXT PRIMARY KEY,payload TEXT NOT NULL)')
    t=time.perf_counter_ns(); c.execute('BEGIN IMMEDIATE'); c.execute('INSERT INTO result VALUES (?,?)',(f'w{idx}',payload)); c.commit(); dt=time.perf_counter_ns()-t; c.close(); return dt/1e6

def batched_two_tx_once(k, idx, payload):
    wid=f'w{idx}'; owner=f'o{idx}'; effect=f'effect:{wid}'; evid=f'ev:{wid}'; now=time.time()
    t=time.perf_counter_ns()
    # TX1: claim + durable effect intent + outbox. This must commit before the external effect.
    with k.tx() as c:
        c.execute('INSERT OR IGNORE INTO work(work_id) VALUES (?)',(wid,))
        r=c.execute('SELECT * FROM work WHERE work_id=?',(wid,)).fetchone()
        if r['phase']=='DONE':
            if r['effect_key']==effect:
                return (time.perf_counter_ns()-t)/1e6
            raise InvalidCompletion('terminal work cannot accept a new effect intent')
        nf=r['fence']+1; ng=r['generation']+1
        cur=c.execute('UPDATE work SET owner=?,lease_until=?,fence=?,generation=?,phase=?,effect_key=? WHERE work_id=? AND generation=?',
                      (owner,now+30,nf,ng+1,'INTENT',effect,wid,r['generation']))
        if cur.rowcount!=1: raise Conflict('claim+intent CAS failed')
        c.execute('INSERT OR IGNORE INTO outbox(event_id,work_id,kind,dedupe_key,payload) VALUES (?,?,?,?,?)',(str(uuid.uuid4()),wid,'effect-intent',effect,'{}'))
    receipt=f'receipt:{effect}'
    # TX2: confirmation + evidence + fresh evidence check + terminal decision.
    with k.tx() as c:
        r=c.execute('SELECT * FROM work WHERE work_id=?',(wid,)).fetchone()
        if not r or r['owner']!=owner or r['fence']!=nf: raise StaleFence('stale owner/fence')
        c.execute('UPDATE work SET phase=?,effect_receipt=?,generation=generation+1 WHERE work_id=?',('CONFIRMED',receipt,wid))
        c.execute('INSERT INTO evidence VALUES (?,?,?,?,?,?)',(evid,wid,'v1',1,payload,time.time()))
        e=c.execute('SELECT valid FROM evidence WHERE evidence_id=? AND work_id=?',(evid,wid)).fetchone()
        if not e or e['valid']!=1: raise InvalidCompletion('missing/invalid evidence')
        c.execute('UPDATE work SET phase=?,done_evidence_id=?,generation=generation+1 WHERE work_id=? AND fence=?',('DONE',evid,wid,nf))
        if c.total_changes < 3: raise StaleFence('completion lost fence')
    return (time.perf_counter_ns()-t)/1e6

def full_once(k, idx, payload):
    wid=f'w{idx}'; owner=f'o{idx}'; effect=f'effect:{wid}'; evid=f'ev:{wid}'
    t=time.perf_counter_ns(); fence,_=k.claim(wid,owner); k.prepare_intent(wid,owner,fence,effect); k.confirm_effect(wid,owner,fence,f'receipt:{effect}'); k.append_evidence(wid,evid,'v1',payload); k.complete(wid,owner,fence,evid); return (time.perf_counter_ns()-t)/1e6

def run_uncontended(variant, payload_size, repetitions=120):
    with tempfile.TemporaryDirectory() as td:
        path=Path(td)/'bench.db'; payload='x'*payload_size
        if variant=='minimal':
            c=sqlite3.connect(path, isolation_level=None); c.execute('PRAGMA journal_mode=WAL'); c.execute('CREATE TABLE result(work_id TEXT PRIMARY KEY,payload TEXT NOT NULL)'); c.close()
            fn=lambda i: minimal_once(path,i,payload)
        else:
            k=Kernel(path)
            fn=lambda i: (full_once(k,i,payload) if variant=='full' else batched_two_tx_once(k,i,payload))
        for i in range(10): fn(-1000-i)
        samples=[]; before=db_bytes(path)
        for i in range(repetitions): samples.append(fn(i))
        after=db_bytes(path)
        return {'variant':variant,'payload_bytes':payload_size,'mode':'uncontended','repetitions':repetitions,'median_ms':statistics.median(samples),'p95_ms':p95(samples),'mean_ms':statistics.mean(samples),'db_bytes_delta':after-before,'known_tx_per_task':{'minimal':1,'full':6,'batched2':2}[variant],'conflicts':0}

def run_contended(variant, payload_size, workers=4, per_worker=30):
    with tempfile.TemporaryDirectory() as td:
        path=Path(td)/'bench.db'; k=Kernel(path); payload='x'*payload_size
        fn=lambda i: (full_once(k,i,payload) if variant=='full' else batched_two_tx_once(k,i,payload))
        for i in range(10): fn(-1000-i)
        lock=threading.Lock(); samples=[]; conflicts=0; errors=[]
        def worker(w):
            nonlocal conflicts
            for j in range(per_worker):
                idx=w*100000+j; start=time.perf_counter_ns()
                for attempt in range(20):
                    try:
                        fn(idx); break
                    except (sqlite3.OperationalError, Conflict):
                        with lock: conflicts += 1
                        time.sleep(0.001*(attempt+1))
                else:
                    with lock: errors.append('retry budget exhausted')
                    return
                with lock: samples.append((time.perf_counter_ns()-start)/1e6)
        ts=[threading.Thread(target=worker,args=(w,)) for w in range(workers)]
        before=db_bytes(path); t0=time.perf_counter()
        for t in ts:t.start()
        for t in ts:t.join()
        elapsed=time.perf_counter()-t0; after=db_bytes(path)
        if errors: raise RuntimeError(errors[0])
        return {'variant':variant,'payload_bytes':payload_size,'mode':'contended','workers':workers,'repetitions':workers*per_worker,'median_ms':statistics.median(samples),'p95_ms':p95(samples),'mean_ms':statistics.mean(samples),'wall_ms':elapsed*1000,'throughput_tasks_s':len(samples)/elapsed,'db_bytes_delta':after-before,'known_tx_per_task':{'full':6,'batched2':2}[variant],'conflicts':conflicts}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--output',default='results.json'); ap.add_argument('--repetitions',type=int,default=120); args=ap.parse_args()
    rows=[]
    for size in PAYLOADS.values():
        for v in ('minimal','full','batched2'): rows.append(run_uncontended(v,size,args.repetitions))
        for v in ('full','batched2'): rows.append(run_contended(v,size))
    out={'environment':{'python':platform.python_version(),'sqlite':sqlite3.sqlite_version,'platform':platform.platform(),'cpu_count':os.cpu_count()},'rows':rows}
    Path(args.output).write_text(json.dumps(out,indent=2),encoding='utf-8')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
