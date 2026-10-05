#!/usr/bin/env python3
import time,hashlib,json
N=100_000; start=time.perf_counter(); seen={}
for i in range(N):
    eid=f'e{i%25000}'; payload={'budget':i%1000,'state':'active'}; fp=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest(); seen[eid]=fp
elapsed=time.perf_counter()-start
limit=10.0
print(json.dumps({'observations':N,'unique_entities':len(seen),'elapsed_seconds':round(elapsed,4),'limit_seconds':limit}))
raise SystemExit(0 if elapsed<=limit else 1)
