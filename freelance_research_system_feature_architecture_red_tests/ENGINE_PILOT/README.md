# Research System → Generic Documentation Engine pilot

This is a deliberately narrow migration spike, not a replacement of accepted v1.11.
It moves the **daily monitoring / daily diff** dependency semantics onto
`generic-documentation-engine 0.1.0.dev20` while leaving the existing research-system
contracts untouched.

## Why this slice

The old runtime stores observations in JSONL and computes a daily diff with a bespoke
script. Dependency propagation is a separate hand-maintained `DEPENDENCY_GRAPH.json`.
The pilot tests whether the engine can own the generic part instead:

- research facts remain research-domain data;
- a project-owned builder owns the daily-diff formula;
- every actual input is captured through tracked `resource://` reads;
- the engine persists baselines, receipts, state and history;
- adding/changing an upstream run automatically produces `build_required`;
- Markdown is a generated view owned by the derived descriptor.

## Pilot storage model

```text
project/
  docengine.toml
  docengine_project/
    builders.py
    schemas/
  docs/
    _structured/
      research/
        run_index.json        # collection membership + active run
        diff_request.json     # pair selected for comparison
        daily_diff.json       # derived descriptor / output ownership
      runs/
        r1.json               # one canonical DailyRun incl. observations
        r2.json
        ...
    _dependency/              # engine-owned receipts/baselines/state/events
    research/
      daily_diff.md           # materialized view
```

`research.run_index#/run_ids` is intentionally a first-class dependency. It gives the
project an explicit collection identity without requiring a new engine-level
`collection://` primitive. A new historical run changes membership and therefore
invalidates a gap-sensitive daily diff.

## What changed from the old daily-monitoring runtime

Old:

```text
RUNS/*.json + LEDGER/OBSERVATIONS.jsonl
      ↓ bespoke build_daily_diff.py
LEDGER/DAILY_DIFFS.jsonl

DEPENDENCY_GRAPH.json is separate/manual.
```

Pilot:

```text
resource://research/run_index
resource://runs/<id>
resource://research/diff_request
      ↓ tracked builder reads
resource://research/daily_diff
      ↓ receipt + baseline + state
research/daily_diff.md
```

The research-specific comparability rule is unchanged: method id/version, scope,
source routes and complete coverage must match. Gap-safe new/reopened semantics are
also preserved.

## Run it on Windows PowerShell

From the extracted research-system package:

```powershell
py -m venv .engine-venv
& .\.engine-venv\Scripts\python.exe -m pip install .\VENDOR\generic_documentation_engine-0.1.0.dev20-py3-none-any.whl

$py = ".\.engine-venv\Scripts\python.exe"
$tool = ".\ENGINE_PILOT\research_engine.py"
$project = "$env:TEMP\research-engine-pilot"
Remove-Item $project -Recurse -Force -ErrorAction SilentlyContinue

& $py $tool init $project
& $py $tool start $project --run-id r1 --method-id m --method-version 1 --scope-fingerprint s --source-route a --now 2026-10-01T00:00:00+00:00
& $py $tool observe $project --entity-id e1 --canonical-key k --class explicit_negative --state closed --source-id s1 --payload-json '{}' --now 2026-10-01T00:01:00+00:00
& $py $tool finish $project --coverage complete --now 2026-10-01T01:00:00+00:00

& $py -m unittest ENGINE_PILOT.test_pilot -v
```

The integration test proves both the gap-day reopen behavior and dependency
invalidation when collection membership changes.

## Migration boundary discovered by the spike

The engine can already replace the generic dependency/baseline/derived-view machinery
without engine changes. The research system should **not** be moved wholesale in one
step. The next safe slices are:

1. DailyRun / Observation / DailyDiff (this pilot).
2. Measurements and deterministic result products.
3. Method/source registries as managed resources.
4. Semantic claims/interpretations through engine semantic-review rules.
5. Replace `DEPENDENCY_GRAPH.json`, project manifest duplication and bespoke recovery
   only after their consumers have moved.

Operational workflow state (`active task`, routing, acquisition actions) should remain
research-runtime state unless there is a concrete documentation dependency reason to
promote it into an engine resource.
