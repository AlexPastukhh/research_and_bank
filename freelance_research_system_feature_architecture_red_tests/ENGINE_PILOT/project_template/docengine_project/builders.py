"""Engine-native research builders.

The first migration slice replaces the hand-maintained dependency graph for daily
monitoring with tracked runtime reads. Collection membership is explicit in the
project-owned ``research.run_index`` resource.
"""


def _run_ref(run_id):
    return f"resource://runs/{run_id}"


def build_daily_diff(ctx):
    request = ctx.get("resource://research/diff_request").to_builtin()
    current_id = request["current_run_id"]
    previous_id = request["previous_run_id"]

    # Track collection membership explicitly. This prevents a newly-added prior
    # run from being invisible to gap-safe new/reopened classification.
    run_ids = list(ctx.read("resource://research/run_index#/run_ids", comparator="exact"))
    current = ctx.get(_run_ref(current_id)).to_builtin()
    previous = ctx.get(_run_ref(previous_id)).to_builtin()

    compatible = (
        current["method_id"] == previous["method_id"]
        and current["method_version"] == previous["method_version"]
        and current["scope_fingerprint"] == previous["scope_fingerprint"]
        and sorted(current["source_route_ids"]) == sorted(previous["source_route_ids"])
        and current["coverage_status"] == "complete"
        and previous["coverage_status"] == "complete"
    )
    status = "comparable" if compatible else "not_comparable"

    new = []
    changed = []
    closed = []
    reopened = []
    not_seen = []
    seen_again = []

    if compatible:
        current_obs = {
            item["entity_id"]: item
            for item in current.get("observations", [])
            if item["observation_class"] in {"seen", "explicit_negative"}
        }
        previous_obs = {
            item["entity_id"]: item
            for item in previous.get("observations", [])
            if item["observation_class"] in {"seen", "explicit_negative"}
        }

        # Load only earlier runs listed by the canonical membership resource.
        # Every loaded run is therefore direct dependency evidence.
        history = {}
        for run_id in run_ids:
            if run_id in {current_id}:
                continue
            run = ctx.get(_run_ref(run_id)).to_builtin()
            if run.get("started_at", "") >= current.get("started_at", ""):
                continue
            for obs in run.get("observations", []):
                if obs["observation_class"] in {"seen", "explicit_negative"}:
                    history.setdefault(obs["entity_id"], []).append(obs)

        for entity_id, obs in current_obs.items():
            prior = history.get(entity_id, [])
            if not prior:
                new.append(entity_id)
                continue
            last = sorted(prior, key=lambda item: item["observed_at"])[-1]
            if last["observation_class"] == "explicit_negative" and obs["observation_class"] == "seen":
                reopened.append(entity_id)
            elif obs["observation_class"] == "explicit_negative":
                closed.append(entity_id)
            elif last.get("semantic_fingerprint") != obs.get("semantic_fingerprint"):
                changed.append(entity_id)
            else:
                seen_again.append(entity_id)
        not_seen = sorted(set(previous_obs) - set(current_obs))

    return {
        "title": "Daily Research Diff",
        "current_run_id": current_id,
        "previous_run_id": previous_id,
        "comparison_status": status,
        "new_entity_ids": sorted(new),
        "changed_entity_ids": sorted(changed),
        "confirmed_closed_ids": sorted(closed),
        "reopened_ids": sorted(reopened),
        "not_seen_ids": sorted(not_seen),
        "seen_again_ids": sorted(seen_again),
    }


def register(registry):
    registry.register(
        "resource://research/daily_diff",
        build_daily_diff,
        builder_id="research.build_daily_diff",
        dependency_type="aggregate",
        comparator="exact",
    )
