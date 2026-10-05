#!/usr/bin/env python3
from pathlib import Path
import json,sys,subprocess
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'TOOLS'))
from route_use_case import route
reg=json.loads((ROOT/'CORE/USE_CASE_REGISTRY.json').read_text())
budget=json.loads((ROOT/'CORE/ARCHITECTURE_BUDGET.json').read_text())['limits']
mapj=json.loads((ROOT/'REFERENCE/SYSTEM_MAP.json').read_text())
contracts=json.loads((ROOT/'CORE/RESULT_PRODUCT_CONTRACTS.json').read_text())
base=json.loads((ROOT/'REFERENCE/PHASE2_ROUTING_BASELINE_v1.10.json').read_text())['fixtures']
checks={}; evidence={}
q=[u for u in reg['use_cases'] if u['interaction_type']=='query']
expected_ids={'UC21','UC22','UC23','UC24','UC25'}
expected_products={'CurrentStateSnapshot','ChangeSet','TrendSeries','InterpretationRecord','ResearchHealthSnapshot'}
checks['A2.1']={u['id'] for u in q}==expected_ids and {u['outputs'][0]['type'] for u in q}==expected_products and all(u['group']=='results' for u in q)
evidence['A2.1']='five results-group query UCs with one typed result product each'
# English/Russian command-query + state-sensitive examples
pairs=[
 ('show current state for Programming',{},'UC21'),('покажи актуальное состояние по Programming',{},'UC21'),
 ('show me the changes already recorded',{},'UC22'),('покажи что изменилось с вчера',{},'UC22'),
 ('what changed since yesterday',{'existing_change_result_available':True},'UC22'),('what changed since yesterday',{'refresh_requested':True},'UC09'),
 ('measure payout for Programming',{},'UC08'),('show trend for Programming payout',{},'UC23'),
 ('verify whether this claim is supported',{},'UC11'),('explain the results already collected',{},'UC24'),
 ('audit the reusable system architecture',{},'UC19'),('show how fresh the research data is',{},'UC25')]
checks['A2.2']=all(route(reg,t,s)[0]==e for t,s,e in pairs)
evidence['A2.2']=f'{len(pairs)} targeted English/Russian/state-sensitive command-query contrasts route as expected'
checks['A2.3']=all(not u['writes'] and any('read-only' in x.lower() for x in u['side_effects']) for u in q) and all(u['interaction_type']!='query' for u in reg['use_cases'] if u['id'] in {'UC08','UC09','UC11','UC18','UC19'})
evidence['A2.3']='query UCs write nothing and declare read-only; representative research/repair/audit UCs remain commands'
banned={'Direction Detail','Current State Screen','Daily Changes Screen','Trends Screen','Interpretations Screen','Coverage & Quality Screen'}
checks['A2.4']=not any(u['name'] in banned or u['action_class'].startswith('ui.') for u in reg['use_cases'])
evidence['A2.4']='UI screen names/action classes do not appear as top-level UCs'
checks['A2.5']=not any(u['name'].lower().startswith(('build ','render ','project ')) for u in q) and all(any('projection capability' in c.lower() for c in u['capabilities']) for u in q)
evidence['A2.5']='projection is declared as a capability dependency, not a builder UC'
legacy_fail=[]
for f in base:
 got=route(reg,f['request'],f.get('state',{}))[0]
 if got!=f['expected_use_case_id']: legacy_fail.append((f['id'],got,f['expected_use_case_id']))
checks['A2.6']=not legacy_fail
evidence['A2.6']=f'{len(base)} v1.10 routing fixtures preserved; regressions={legacy_fail}'
checks['A2.7']=len(reg['use_cases'])==25 and len(set(u['group'] for u in reg['use_cases']))==6 and len(q)==5 and budget.get('max_top_level_use_cases')==25 and budget.get('max_use_case_groups')==6 and budget.get('max_query_use_cases')==5 and len(list((ROOT/'CORE').glob('USE_CASE_REGISTRY*.json')))==1
evidence['A2.7']='25 UCs / 6 groups / 5 queries explicitly budgeted; one canonical routing registry'
node_ids={n['id'] for n in mapj['nodes']}; edge_pairs={(e['from'],e['to'],e['type']) for e in mapj['edges']}
checks['A2.8']=expected_ids.issubset(node_ids) and not any('PLANNED:UC2' in x for x in node_ids) and all('RESULT:'+p in node_ids for p in expected_products) and all(any(e[0]==uid and e[2]=='returns' for e in edge_pairs) for uid in expected_ids)
evidence['A2.8']='System Map contains implemented UC21–UC25 and result return edges; no PLANNED:UC21–UC25 nodes'
failed=[k for k,v in checks.items() if not v]
print(json.dumps({'phase':2,'system_version':'1.11.0','accepted':not failed,'checks':checks,'evidence':evidence,'failed':failed},ensure_ascii=False,indent=2))
raise SystemExit(1 if failed else 0)
