#!/usr/bin/env python3
from pathlib import Path
import json, sys, re
ROOT=Path(__file__).resolve().parents[1]
reg=json.loads((ROOT/'CORE/USE_CASE_REGISTRY.json').read_text()); lim=json.loads((ROOT/'CORE/ARCHITECTURE_BUDGET.json').read_text())['limits']; ucs=reg['use_cases']
deps=[len(u['reads'])+len(u['writes'])+len(u['capabilities']) for u in ucs]
metrics={
 'max_top_level_use_cases':len(ucs),'max_use_case_kinds':len(set(u['kind'] for u in ucs)),'max_use_case_groups':len(set(u['group'] for u in ucs)),'max_query_use_cases':sum(u['interaction_type']=='query' for u in ucs),
 'max_orchestration_use_cases':sum(u['kind']=='orchestration' for u in ucs),'max_canonical_routing_registries':len(list((ROOT/'CORE').glob('USE_CASE_REGISTRY*.json'))),
 'max_routing_metadata_sections_in_workflows':0,'max_unguarded_multi_target_routes':0,
 'max_dependencies_per_use_case':max(deps),'max_average_dependencies_per_use_case':sum(deps)/len(deps),
 'max_entrypoint_route_examples':len(re.findall(r'UC[0-9]{2}',(ROOT/'START_HERE_AGENT.md').read_text(encoding='utf-8'))),
 'min_complete_contract_fields':min(len(u) for u in ucs)}
pat=re.compile(r'(?im)^##\s*(Intent|Route here|Do not route|Normal next|Acceptance|Allowed outcome)')
metrics['max_routing_metadata_sections_in_workflows']=sum(len(pat.findall((ROOT/u['workflow']).read_text(encoding='utf-8'))) for u in ucs)
for u in ucs:
    outs=u['outcomes']; trs=[t['outcome'] for t in u['transitions']]
    if len(outs)>1 and (set(outs)!=set(trs) or len(trs)!=len(set(trs))): metrics['max_unguarded_multi_target_routes']+=1
errors=[]
for k,v in metrics.items():
    if k.startswith('min_'):
        if v<lim[k]: errors.append(f'{k}: current={v} minimum={lim[k]}')
    elif v>lim[k]: errors.append(f'{k}: current={v} limit={lim[k]}')
if errors:
    print('ARCHITECTURE VALIDATION: FAIL'); [print('-',e) for e in errors]; sys.exit(1)
print('ARCHITECTURE VALIDATION: OK'); print(json.dumps(metrics,indent=2))
