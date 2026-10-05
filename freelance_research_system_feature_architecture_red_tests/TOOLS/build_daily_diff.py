#!/usr/bin/env python3
import argparse,json,hashlib
from pathlib import Path
from common import load_json
ap=argparse.ArgumentParser(); ap.add_argument('project'); ap.add_argument('--current-run',required=True); ap.add_argument('--previous-run',required=True); args=ap.parse_args(); p=Path(args.project).resolve(); cur=load_json(p/'RUNS'/f'{args.current_run}.json'); prev=load_json(p/'RUNS'/f'{args.previous_run}.json')
compatible=(cur['method_id']==prev['method_id'] and cur['method_version']==prev['method_version'] and cur['scope_fingerprint']==prev['scope_fingerprint'] and sorted(cur['source_route_ids'])==sorted(prev['source_route_ids']) and cur['coverage_status']=='complete' and prev['coverage_status']=='complete')
status='comparable' if compatible else 'not_comparable'
obs=[json.loads(x) for x in (p/'LEDGER/OBSERVATIONS.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
byrun={args.current_run:{},args.previous_run:{}}
for o in obs:
    if o['run_id'] in byrun and o['observation_class'] in {'seen','explicit_negative'}: byrun[o['run_id']][o['entity_id']]=o
# history across all prior observations protects gap-day new/reopened semantics
hist={}
for o in obs:
    if o['observed_at'] < cur['started_at'] and o['observation_class'] in {'seen','explicit_negative'}: hist.setdefault(o['entity_id'],[]).append(o)
new=[];changed=[];closed=[];reopened=[];not_seen=[];seen_again=[]
if compatible:
    for eid,o in byrun[args.current_run].items():
        prior=hist.get(eid,[])
        if not prior: new.append(eid); continue
        last=sorted(prior,key=lambda x:x['observed_at'])[-1]
        if last['observation_class']=='explicit_negative' and o['observation_class']=='seen': reopened.append(eid)
        elif o['observation_class']=='explicit_negative': closed.append(eid)
        elif last.get('semantic_fingerprint')!=o.get('semantic_fingerprint'): changed.append(eid)
        else: seen_again.append(eid)
    not_seen=sorted(set(byrun[args.previous_run])-set(byrun[args.current_run]))
d={'diff_id':'diff-'+hashlib.sha256(f"{args.previous_run}|{args.current_run}".encode()).hexdigest()[:16],'research_date':cur['research_date'],'current_run_id':args.current_run,'previous_run_id':args.previous_run,'comparison_status':status,'new_entity_ids':new,'changed_entity_ids':changed,'confirmed_closed_ids':closed,'reopened_ids':reopened,'not_seen_ids':not_seen,'seen_again_ids':seen_again}
with (p/'LEDGER/DAILY_DIFFS.jsonl').open('a',encoding='utf-8') as f: f.write(json.dumps(d,ensure_ascii=False)+'\n')
print(json.dumps(d,ensure_ascii=False))
