from __future__ import annotations
from pathlib import Path
from .future import call_feature

START = "research_system.features.project.start"
START_RUN = "research_system.features.monitoring.start_run"
OBSERVE = "research_system.features.monitoring.record_observation"
FINISH_RUN = "research_system.features.monitoring.finish_run"


def start_project(root: Path, *, project_id: str = "p1"):
    return call_feature(START, root, {"project_id": project_id, "research_day_timezone": "UTC"}, now="2026-10-01T00:00:00+00:00")


def completed_run(root: Path, run_id: str, date: str, *, method_id="m", method_version="1", scope="scope", routes=("route",), observations=(), coverage="complete"):
    call_feature(START_RUN, root, {
        "run_id": run_id,
        "method_id": method_id,
        "method_version": method_version,
        "scope_fingerprint": scope,
        "source_route_ids": list(routes),
    }, now=f"{date}T00:00:00+00:00")
    for idx, obs in enumerate(observations, 1):
        payload = {
            "entity_id": obs.get("entity_id", f"e{idx}"),
            "canonical_key": obs.get("canonical_key", obs.get("entity_id", f"e{idx}")),
            "observation_class": obs.get("observation_class", "seen"),
            "asserted_state": obs.get("asserted_state", "active"),
            "source_id": obs.get("source_id", "s1"),
            "semantic_payload": obs.get("semantic_payload", {}),
        }
        call_feature(OBSERVE, root, payload, now=f"{date}T00:{idx:02d}:00+00:00")
    return call_feature(FINISH_RUN, root, {"coverage_status": coverage, "coverage_notes": ""}, now=f"{date}T01:00:00+00:00")
