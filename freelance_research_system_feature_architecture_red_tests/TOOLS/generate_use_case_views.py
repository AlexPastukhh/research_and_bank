#!/usr/bin/env python3
from pathlib import Path
import argparse, json, sys
ROOT=Path(__file__).resolve().parents[1]
REG=ROOT/'CORE/USE_CASE_REGISTRY.json'
OUT=ROOT/'REFERENCE/USE_CASE_REGISTRY.md'

def render():
    r=json.loads(REG.read_text(encoding='utf-8'))
    lines=['# Use Case Registry — generated view','',f"> GENERATED from `CORE/USE_CASE_REGISTRY.json` registry **{r['registry_version']}**, contract **{r.get('contract_version')}**. Do not edit semantics here.",'',
           '| UC | Group | Interaction | Execution owner | Action class | Inputs | Outputs | Reads | Writes | Golden Paths |','|---|---|---|---|---|---:|---:|---:|---:|---|']
    for u in r['use_cases']:
        lines.append(f"| {u['id']} {u['name']} | {u['group']} | {u['interaction_type']} | `{u['execution_owner']}` | `{u['action_class']}` | {len(u['inputs'])} | {len(u['outputs'])} | {len(u['reads'])} | {len(u['writes'])} | {', '.join(u['golden_paths']) or '—'} |")
    lines += ['', '## Group definitions','']
    for k,v in r['use_case_groups'].items(): lines.append(f'- **{k}** — {v}')
    lines += ['', '## Interaction types','']
    for k,v in r['interaction_types'].items(): lines.append(f'- **{k}** — {v}')
    lines += ['', '## Execution owners','']
    for k,v in r['execution_owners'].items(): lines.append(f'- **{k}** — {v}')
    lines += ['', 'Canonical routing, typed I/O, reads/writes, acceptance, failure modes, side effects, freshness/comparability, transitions, UI/API hooks and Golden Path links remain only in the JSON registry.','']
    return '\n'.join(lines)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--check',action='store_true'); a=ap.parse_args(); expected=render()
    if a.check:
        if not OUT.exists() or OUT.read_text(encoding='utf-8')!=expected:
            print('USE CASE VIEW PARITY: FAIL'); return 1
        print('USE CASE VIEW PARITY: OK'); return 0
    OUT.write_text(expected,encoding='utf-8'); print('USE CASE VIEW GENERATED'); return 0
if __name__=='__main__': raise SystemExit(main())
