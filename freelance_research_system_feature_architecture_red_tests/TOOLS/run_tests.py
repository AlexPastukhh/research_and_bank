#!/usr/bin/env python3
import argparse, concurrent.futures, subprocess, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

QUICK_RUNTIME=[
 'test_path_confinement',
 'test_not_seen_not_closed_and_gap_safe_new',
 'test_source_route_blocks_comparability',
 'test_task_done_requires_acceptance',
 'test_manifest_integrity_detects_missing_file',
 'test_migration_110_to_111',
]

def run_cmd(label,cmd):
    p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
    return label,p.returncode,p.stdout,p.stderr

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--full',action='store_true'); ap.add_argument('--workers',type=int,default=4); args=ap.parse_args()
    jobs=[('use_cases',[sys.executable,'-m','unittest','-q','TESTS.test_use_cases']),('golden_paths',[sys.executable,'-m','unittest','-q','TESTS.test_golden_paths']),('phase_records',[sys.executable,'-m','unittest','-q','TESTS.test_phase_records'])]
    if args.full:
        from TESTS.test_runtime import RuntimeTests
        names=unittest.defaultTestLoader.getTestCaseNames(RuntimeTests)
    else:
        names=QUICK_RUNTIME
    for name in names:
        jobs.append((name,[sys.executable,'-m','unittest','-q',f'TESTS.test_runtime.RuntimeTests.{name}']))
    results=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1,args.workers)) as ex:
        futs=[ex.submit(run_cmd,*j) for j in jobs]
        for fut in concurrent.futures.as_completed(futs):
            results.append(fut.result())
    failed=[]
    for label,rc,out,err in sorted(results):
        status='PASS' if rc==0 else 'FAIL'
        print(f'{status} {label}')
        if rc:
            failed.append(label); print(out[-3000:]); print(err[-3000:])
    if failed:
        print(f'TEST GATE: FAIL — {len(failed)} failed'); return 1
    print(f'TEST GATE: OK — {len(results)} test groups; mode={"full" if args.full else "quick"}')
    return 0
if __name__=='__main__': raise SystemExit(main())
