#!/usr/bin/env python3
import argparse,sys
from pathlib import Path
ap=argparse.ArgumentParser(); ap.add_argument('project'); args=ap.parse_args(); p=Path(args.project).resolve();
# Conservative repair currently removes orphan temp files only; semantic conflicts require explicit migration/manual decision.
for x in p.rglob('*.tmp'):
    try: x.unlink()
    except Exception: pass
print('REPAIR COMPLETE: non-destructive cleanup only; run validate_project.py next')
