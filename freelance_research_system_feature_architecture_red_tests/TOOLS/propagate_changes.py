#!/usr/bin/env python3
import argparse,json
from pathlib import Path
ap=argparse.ArgumentParser(); ap.add_argument('project'); ap.add_argument('node'); args=ap.parse_args(); p=Path(args.project); g=json.loads((p/'DEPENDENCY_GRAPH.json').read_text()); seen=set(); q=[args.node];
while q:
 n=q.pop(0)
 for e in g.get('edges',[]):
  if e.get('from_node_id')==n and e.get('to_node_id') not in seen: seen.add(e['to_node_id']); q.append(e['to_node_id'])
print(json.dumps({'changed_node':args.node,'affected':sorted(seen)}))
