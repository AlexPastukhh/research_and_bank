#!/usr/bin/env python3
import argparse, json, re
from pathlib import Path
from common import load_json

def score_use_case(u,text,state):
    t=text.lower()
    terms=u.get("match_rules",{}).get("terms",[])
    score=sum(2 if term.lower() in t else 0 for term in terms)
    hints=u.get("match_rules",{}).get("state_hints",{})
    for k,v in hints.items():
        if state.get(k)==v: score+=3
    return score

def route(registry,text,state=None):
    state=state or {}
    low=text.lower().strip()
    # explicit state-sensitive generic continuation
    if low in {"continue","продолжай","continue research"}:
        if state.get("next_task_available"): return "UC03","state says next task is available"
        if state.get("baseline_supplied"): return "UC02","baseline supplied but no active next task"
    # State-sensitive boundary discriminators are canonical registry data.
    state_matches=[]
    for rule in registry.get("routing_contract",{}).get("state_discriminators",[]):
        required=rule.get("state_equals",{})
        if all(state.get(k)==v for k,v in required.items()) and any(pat.lower() in low for pat in rule.get("patterns",[])):
            state_matches.append(rule)
    if len(state_matches)==1:
        rule=state_matches[0]
        return rule["use_case_id"], rule.get("reason",f"matched canonical state discriminator for {rule['use_case_id']}")
    if len(state_matches)>1:
        return registry["routing_contract"]["on_ambiguity"], f"ambiguous state discriminators: {[r['use_case_id'] for r in state_matches]}"
    # Boundary-precedence text discriminators are canonical registry data, not hard-coded routing tables.
    for rule in registry.get("routing_contract",{}).get("priority_discriminators",[]):
        if any(pat.lower() in low for pat in rule.get("patterns",[])):
            return rule["use_case_id"], f"matched canonical priority discriminator for {rule['use_case_id']}"
    scores=[(score_use_case(u,text,state),u["id"]) for u in registry["use_cases"]]
    top=max(s for s,_ in scores)
    if top<=0: return registry["routing_contract"]["on_no_match"],"no canonical match; governance fallback"
    winners=[i for s,i in scores if s==top]
    if len(winners)!=1: return registry["routing_contract"]["on_ambiguity"],f"ambiguous: {winners}"
    return winners[0],f"highest canonical routing score={top}"

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('request'); ap.add_argument('--state-json'); ap.add_argument('--registry',default=str(Path(__file__).resolve().parents[1]/'CORE/USE_CASE_REGISTRY.json')); args=ap.parse_args()
    reg=load_json(args.registry); state=json.loads(args.state_json) if args.state_json else {}
    uc,reason=route(reg,args.request,state); print(json.dumps({"use_case_id":uc,"route_reason":reason,"registry_version":reg["registry_version"]},ensure_ascii=False))
if __name__=='__main__': main()
