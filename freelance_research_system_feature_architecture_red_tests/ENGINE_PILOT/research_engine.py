#!/usr/bin/env python3
"""Engine-native pilot for the research system daily-monitoring slice."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import uuid

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / "project_template"
ID_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
SECRET_KEYS = {"password", "passwd", "secret", "token", "api_key", "apikey", "authorization", "cookie"}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    tmp.replace(path)


def redact(value):
    if isinstance(value, dict):
        return {key: ("[REDACTED]" if key.lower() in SECRET_KEYS else redact(item)) for key, item in value.items()}
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


def require_id(value: str, label: str) -> str:
    if not ID_RE.fullmatch(value):
        raise SystemExit(f"{label} must match {ID_RE.pattern}")
    return value


def structured(project: Path, relative: str) -> Path:
    return project / "docs" / "_structured" / relative


def index_path(project: Path) -> Path:
    return structured(project, "research/run_index.json")


def run_path(project: Path, run_id: str) -> Path:
    require_id(run_id, "run id")
    return structured(project, f"runs/{run_id}.json")


def run_envelope(run_id: str, data: dict) -> dict:
    return {
        "$docengine": {
            "resource_id": f"runs.{run_id}",
            "schema": "research://schemas/daily-run/v1",
            "materialize": [],
        },
        "data": data,
    }


def init_project(project: Path):
    if project.exists() and any(project.iterdir()):
        raise SystemExit(f"target is not empty: {project}")
    project.mkdir(parents=True, exist_ok=True)
    shutil.copytree(TEMPLATE, project, dirs_exist_ok=True)
    engine(project, "init")
    print(f"ENGINE PILOT INITIALIZED {project}")


def start(project: Path, args):
    idx = load(index_path(project))
    if idx["data"].get("active_run_id"):
        raise SystemExit("active daily run already exists")
    now = args.now or datetime.now(timezone.utc).isoformat()
    run_id = require_id(args.run_id or "run-" + uuid.uuid4().hex[:12], "run id")
    data = {
        "run_id": run_id,
        "started_at": now,
        "completed_at": None,
        "research_date": now[:10],
        "method_id": args.method_id,
        "method_version": args.method_version,
        "scope_fingerprint": args.scope_fingerprint,
        "source_route_ids": sorted(set(args.source_route)),
        "coverage_status": "in_progress",
        "coverage_notes": "",
        "observations": [],
    }
    path = run_path(project, run_id)
    if path.exists():
        raise SystemExit(f"run already exists: {run_id}")
    save(path, run_envelope(run_id, data))
    idx["data"]["run_ids"].append(run_id)
    idx["data"]["active_run_id"] = run_id
    save(index_path(project), idx)
    print(run_id)


def observe(project: Path, args):
    idx = load(index_path(project))
    run_id = idx["data"].get("active_run_id")
    if not run_id:
        raise SystemExit("no active daily run")
    path = run_path(project, run_id)
    env = load(path)
    run = env["data"]
    payload = redact(json.loads(args.payload_json))
    semantic = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    semantic_fp = hashlib.sha256(semantic.encode("utf-8")).hexdigest()
    idem = hashlib.sha256(
        f"{run_id}|{args.entity_id}|{args.source_id}|{args.klass}|{semantic_fp}".encode("utf-8")
    ).hexdigest()
    if any(item.get("idempotency_key") == idem for item in run["observations"]):
        print("REPLAY")
        return
    now = args.now or datetime.now(timezone.utc).isoformat()
    run["observations"].append({
        "observation_id": "obs-" + idem[:16],
        "idempotency_key": idem,
        "run_id": run_id,
        "entity_id": args.entity_id,
        "canonical_key": args.canonical_key,
        "observed_at": now,
        "research_date": run["research_date"],
        "observation_class": args.klass,
        "asserted_state": args.state,
        "source_id": args.source_id,
        "method_id": run["method_id"],
        "method_version": run["method_version"],
        "scope_fingerprint": run["scope_fingerprint"],
        "source_route_ids": run["source_route_ids"],
        "semantic_fingerprint": semantic_fp,
        "semantic_payload": payload,
    })
    save(path, env)
    print("obs-" + idem[:16])


def finish(project: Path, args):
    idx = load(index_path(project))
    run_id = idx["data"].get("active_run_id")
    if not run_id:
        raise SystemExit("no active daily run")
    path = run_path(project, run_id)
    env = load(path)
    run = env["data"]
    if run.get("completed_at"):
        raise SystemExit("daily run already finalized")
    run["completed_at"] = args.now or datetime.now(timezone.utc).isoformat()
    run["coverage_status"] = args.coverage
    run["coverage_notes"] = args.notes
    save(path, env)
    idx["data"]["active_run_id"] = None
    save(index_path(project), idx)
    print("FINALIZED")


def engine(project: Path, *engine_args: str, allow_attention: bool = False):
    cmd = [sys.executable, "-m", "docengine.cli", *engine_args, "--project-root", str(project), "--json"]
    proc = subprocess.run(cmd, text=True, capture_output=True)
    if proc.returncode not in ({0, 2} if allow_attention else {0}):
        raise SystemExit(proc.stdout + proc.stderr)
    if proc.stdout.strip():
        print(proc.stdout.strip())
    return proc


def diff(project: Path, args):
    current = require_id(args.current_run, "current run id")
    previous = require_id(args.previous_run, "previous run id")
    for run_id in (current, previous):
        if not run_path(project, run_id).is_file():
            raise SystemExit(f"unknown run: {run_id}")
    request_path = structured(project, "research/diff_request.json")
    request = load(request_path)
    request["data"] = {"current_run_id": current, "previous_run_id": previous}
    save(request_path, request)
    engine(project, "rebuild", "resource://research/daily_diff")
    engine(project, "materialize", "resource://research/daily_diff")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="command", required=True)
    p = sub.add_parser("init"); p.add_argument("project")
    p = sub.add_parser("start"); p.add_argument("project"); p.add_argument("--run-id"); p.add_argument("--method-id", required=True); p.add_argument("--method-version", required=True); p.add_argument("--scope-fingerprint", required=True); p.add_argument("--source-route", action="append", default=[]); p.add_argument("--now")
    p = sub.add_parser("observe"); p.add_argument("project"); p.add_argument("--entity-id", required=True); p.add_argument("--canonical-key", required=True); p.add_argument("--class", dest="klass", choices=["seen", "explicit_negative", "query_absence", "error"], required=True); p.add_argument("--state", default="unknown"); p.add_argument("--source-id", required=True); p.add_argument("--payload-json", default="{}"); p.add_argument("--now")
    p = sub.add_parser("finish"); p.add_argument("project"); p.add_argument("--coverage", choices=["complete", "partial", "failed"], required=True); p.add_argument("--notes", default=""); p.add_argument("--now")
    p = sub.add_parser("diff"); p.add_argument("project"); p.add_argument("--current-run", required=True); p.add_argument("--previous-run", required=True)
    p = sub.add_parser("check"); p.add_argument("project")
    args = ap.parse_args(); project = Path(args.project).resolve()
    if args.command == "init": init_project(project)
    elif args.command == "start": start(project, args)
    elif args.command == "observe": observe(project, args)
    elif args.command == "finish": finish(project, args)
    elif args.command == "diff": diff(project, args)
    elif args.command == "check": engine(project, "check", allow_attention=True)


if __name__ == "__main__":
    main()
