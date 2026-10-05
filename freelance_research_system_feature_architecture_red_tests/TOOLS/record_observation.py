#!/usr/bin/env python3
import argparse,json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from common import load_json,save_json
SECRET_KEYS={'password','passwd','secret','token','api_key','apikey','authorization','cookie'}
def redact(v):
    if isinstance(v,dict): return {k:('[REDACTED]' if k.lower() in SECRET_KEYS else redact(x)) for k,x in v.items()}
    if isinstance(v,list): return [redact(x) for x in v]
    return v
ap=argparse.ArgumentParser(); ap.add_argument('project'); ap.add_argument('--entity-id',required=True); ap.add_argument('--canonical-key',required=True); ap.add_argument('--class',dest='klass',choices=['seen','explicit_negative','query_absence','error'],required=True); ap.add_argument('--state',default='unknown'); ap.add_argument('--source-id',required=True); ap.add_argument('--payload-json',default='{}'); ap.add_argument('--now'); args=ap.parse_args(); p=Path(args.project).resolve(); rs=load_json(p/'RUN_STATE.json'); rid=rs.get('active_daily_run_id')
if not rid: raise SystemExit('no active daily run')
run=load_json(p/'RUNS'/f'{rid}.json'); now=args.now or datetime.now(timezone.utc).isoformat(); payload=redact(json.loads(args.payload_json)); sem=json.dumps(payload,sort_keys=True,separators=(',',':'),ensure_ascii=False); fp=hashlib.sha256(sem.encode()).hexdigest(); idem=hashlib.sha256(f"{rid}|{args.entity_id}|{args.source_id}|{args.klass}|{fp}".encode()).hexdigest()
ledger=p/'LEDGER/OBSERVATIONS.jsonl'; existing=set()
for line in ledger.read_text(encoding='utf-8').splitlines():
    if line.strip(): existing.add(json.loads(line)['idempotency_key'])
if idem in existing: print('REPLAY'); raise SystemExit(0)
obs={'observation_id':'obs-'+idem[:16],'idempotency_key':idem,'run_id':rid,'entity_id':args.entity_id,'canonical_key':args.canonical_key,'observed_at':now,'research_date':run['research_date'],'observation_class':args.klass,'asserted_state':args.state,'source_id':args.source_id,'method_id':run['method_id'],'method_version':run['method_version'],'scope_fingerprint':run['scope_fingerprint'],'source_route_ids':run['source_route_ids'],'semantic_fingerprint':fp,'semantic_payload':payload}
with ledger.open('a',encoding='utf-8') as f: f.write(json.dumps(obs,ensure_ascii=False)+'\n')
print(obs['observation_id'])
