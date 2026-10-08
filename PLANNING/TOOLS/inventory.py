"""Validate vNext inventory metadata and preserved backlog/proposal references."""
import argparse,json,re,hashlib
from pathlib import Path
KINDS={'user_outcome','product_capability','data_contract','architecture_constraint','research_method','governance','implementation_choice'}
ROOT=Path(__file__).resolve().parents[2]
MASTER='DRAFT_NOTES/11_MASTER_REQUIREMENTS_AND_EXTENSION_AXES.md'
BACKLOG='DRAFT_NOTES/08_IDEA_BACKLOG_AND_OPEN_DECISIONS.md'
REPORT='PLANNING/vnext_requirements_normalization_review.md'
BEGIN='<!-- BEGIN_REQUIREMENT_CROSSWALK -->'
END='<!-- END_REQUIREMENT_CROSSWALK -->'
def check(ok,message):
 if not ok:raise ValueError(message)
def sha(text):return hashlib.sha256(text.encode('utf-8')).hexdigest()
def section_refs(value):
 result=[]
 for a,b in re.findall(r'(\d+(?:\.\d+)*)(?:[–-](\d+(?:\.\d+)*))?',value):
  if b and '.' in a and a.rsplit('.',1)[0]==b.rsplit('.',1)[0]:
   result.extend(a.rsplit('.',1)[0]+'.'+str(i) for i in range(int(a.rsplit('.',1)[1]),int(b.rsplit('.',1)[1])+1))
  else:result.append(a);result.extend([b] if b else [])
 return list(dict.fromkeys(result))
def table_rows(text,start,end,pattern):
 section=text.split(start,1)[1].split(end,1)[0]
 return [(i+1,[c.strip() for c in line.strip('|').split(' | ')]) for i,line in enumerate(text.splitlines()) if re.match(pattern,line) and line in section.splitlines()]
def parse_report(text):
 rows=table_rows(text,'## 5. ','## 6. ',r'^\| (?:INT|MVP|TGT|COND|OPP|EXP|OPEN|ANTI)-\d{3} \|')
 reviews={}
 for line,c in rows:
  check(len(c)==5,'Requirement review table shape')
  trace=c[4];section=re.search(r'§([^;]+)',trace).group(1).strip()
  reviews[c[0]]={'line':line,'statement_snapshot':c[1],'action':c[2],'rationale':c[3],
   'kind':trace.split(';',1)[0].strip(),'axes':['AX-V'+n for n in re.findall(r'\bV(\d{2})\b',trace)],
   'section':section,'sections':section_refs(section),
   'reference_patterns':[x.strip() for x in trace.split('ref:',1)[1].strip().split(',') if x.strip()!='—']}
 children=table_rows(text,'## 6. ','## 7. ',r'^\| (?:TGT|OPEN)-\d{3}\.[A-Za-z_]+ \|')
 proposals=table_rows(text,'## 7. ','## 8. ',r'^\| NEW-\d{3} \|')
 backlog=table_rows(text,'## 8. ','## 9. ',r'^\| B\d{3} /')
 return reviews,children,proposals,backlog
def source_bullets(text):
 section='';items=[]
 for n,line in enumerate(text.splitlines(),1):
  if line.startswith('#'):section=line.lstrip('#').strip()
  if line.startswith('- '):items.append({'line':n,'section':section,'excerpt':line[2:],'excerpt_sha256':sha(line[2:])})
 return items
def crosswalk(registry):
 lines=[BEGIN,'## Registry crosswalk — current stable IDs','',
 'Generated metadata crosswalk; status is intent classification, not implementation completion. Pending proposals/backlog are linked from the registry.','',
 '| ID | Status | Kind | Axes | Human sections |','| --- | --- | --- | --- | --- |']
 for x in registry['requirements']:
  lines.append('| '+x['id']+' | '+x['status']+' | '+x['kind']+' | '+', '.join(x['axes'])+' | '+x['human_ref']['section']+' |')
 return '\n'.join(lines+['',END])
def validate(registry,triage,proposals,master,backlog,report):
 req=registry['requirements'];ids=[x['id'] for x in req];live=set(ids)
 check(len(ids)==len(live),'Duplicate requirement IDs')
 axes={x['id'] for x in registry['extension_axes']}
 headings=set(re.findall(r'^#{1,6} (\d+(?:\.\d+)*)',master,re.M))
 for x in req:
  check(x.get('status') in registry['classification_semantics'],'Unknown intent classification: '+x['id'])
  check(x.get('kind') in KINDS,'Unknown kind: '+x['id'])
  check(bool(x.get('axes')) and len(x['axes'])==len(set(x['axes'])) and set(x['axes'])<=axes,'Invalid axes: '+x['id'])
  check(x.get('origin',{}).get('basis')=='unknown' and x.get('origin_confidence')=='document_lineage_verified_original_user_attribution_unknown','Invented historical attribution: '+x['id'])
  check(x['origin'].get('entry_id')==x['id'] and bool(x['origin'].get('baseline_inventory_sha256')),'Missing origin: '+x['id'])
  ref=x.get('human_ref',{});check(ref.get('path')==MASTER and ref.get('requirement_id')==x['id'],'Invalid human ref: '+x['id'])
  sections=ref.get('sections') or section_refs(ref.get('section',''))
  check(bool(sections) and set(sections)<=headings,'Missing human sections: '+x['id'])
  check(bool(x.get('rationale')) and bool(x.get('change_history')),'Missing rationale/history: '+x['id'])
  check(x.get('normalization_review',{}).get('statement_rewrite_adopted') is False,'Unadopted rewrite promoted: '+x['id'])
 pids=[x['proposal_id'] for x in proposals['entries']];pset=set(pids)
 check(len(pids)==len(pset) and not pset&live,'Proposal ID collision')
 for p in proposals['entries']:
  check(p['state'] in {'pending_not_adopted','consolidated_into_existing_requirements','superseded_by_current_storage_decision'},'Proposal state')
  check(set(p.get('live_requirement_refs',[]))<=live,'Proposal live ref dangling')
  if p['proposal_id']=='NEW-004' or p['proposal_id']=='OPEN-011.backend':check(p['state']=='superseded_by_current_storage_decision','Stale GitHub backend decision active')
 items=triage['items'];bids=[x['backlog_id'] for x in items];bullets=source_bullets(backlog)
 check(len(bids)==len(set(bids))==len(bullets),'Backlog missing/duplicate coverage')
 for x,source in zip(items,bullets):
  check(x['source']==dict(path=BACKLOG,**source),'Backlog origin drift: '+x['backlog_id'])
  check(set(x['requirement_refs'])<=live,'Backlog dangling live ref: '+x['backlog_id'])
  check(set(x['proposal_refs'])<=pset,'Backlog dangling proposal ref: '+x['backlog_id'])
  check(x['disposition'] in {'linked_existing_scope','pending_clarification','pending_proposal','confirmed_existing_decision'},'Backlog disposition')
  check(bool(x['requirement_refs'] or x['proposal_refs']),'Backlog without destination')
  if x['source']['excerpt'].startswith('positive examples + negative examples'):
   check('OPP-017' in x['requirement_refs'] and x['disposition']=='confirmed_existing_decision','Negative example decision lost')
 reviews,children,new,rows=parse_report(report)
 check(set(reviews)==live,'Review requirement coverage mismatch')
 check({c[0] for _,c in children+new}==pset,'Proposal catalog coverage mismatch')
 deps=table_rows(report,'### Кандидатные dependencies','### Golden Scenario',r'^\| (?:INT|MVP|TGT|COND|OPP|EXP|OPEN|ANTI)-\d{3} \|')
 check([x['row_cells'] for x in proposals['dependency_review_rows']]==[c for _,c in deps],'Dependency proposal coverage drift')
 check(all(x['state']=='pending_not_adopted' for x in proposals['dependency_review_rows']),'Proposed prerequisite promoted silently')
 check({c[0].split(' / ')[0] for _,c in rows}==set(bids),'Review backlog coverage mismatch')
 snap=triage['review_source_snapshot'];check(sha(report[:snap['character_count']])==snap['text_sha256'],'Historical review snapshot drift')
 snap=triage['source_snapshot'];check(sha(backlog[:snap['character_count']])==snap['text_sha256'],'Historical backlog snapshot drift')
 block=re.search(re.escape(BEGIN)+r'.*?'+re.escape(END),master,re.S)
 check(bool(block) and block.group(0)==crosswalk(registry),'Generated human crosswalk drift')
 return {'requirements':len(req),'backlog_items':len(items),'proposals':len(pids),'axes':len(axes)}
def load(root):
 read=lambda p:(root/p).read_text(encoding='utf-8-sig')
 return (json.loads(read('DRAFT_NOTES/REQUIREMENTS_MAP.json')),json.loads(read('DRAFT_NOTES/BACKLOG_TRIAGE.json')),
  json.loads(read('DRAFT_NOTES/NORMALIZATION_PROPOSALS.json')),read(MASTER),read(BACKLOG),read(REPORT))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=ROOT);args=ap.parse_args()
 print(json.dumps({'status':'PASS',**validate(*load(args.root))}))
