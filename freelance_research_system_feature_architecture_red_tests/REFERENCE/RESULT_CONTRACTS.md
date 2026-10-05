# Result contracts required by the UI

The current research runtime already has many primitive inputs (DailyRuns, Observations, EntityRegistry, DailyDiffs, Measurements, Claims, Economics). The UI needs four explicit derived result products plus one quality product.

## 1. CurrentStateSnapshot
Purpose: answer “what is true now?” for all research or one scope.
Rules:
- use latest valid observation/measurement per canonical entity/metric;
- exclude stale/invalidated results by default;
- never convert query absence into closure;
- carry freshness, coverage, method/version, confidence and limitations;
- support `scope=all` and a concrete direction/service unit/channel/source.

Minimum fields:
- snapshot_id, generated_at, research_date, scope
- freshness_policy_version
- included_result_ids / excluded_result_ids + exclusion_reason
- current entities / measurements / claims / economics
- coverage summary

## 2. ChangeSet
Purpose: answer “what changed on day X compared with day Y?”.
Rules:
- compare only compatible runs/scopes/methods;
- preserve `new`, `changed`, `confirmed_closed`, `reopened`, `not_seen`, `interesting` separately;
- expose comparison status and coverage.

Minimum fields:
- change_set_id, from_date, to_date, scope
- comparison_status
- new, changed, confirmed_closed, reopened, not_seen, interesting
- source run IDs, coverage, caveats

## 3. TrendSeries
Purpose: answer “what is the tendency across time?”.
Rules:
- aggregate comparable measurements into day/week/month/custom windows;
- never bridge incompatible method versions silently;
- expose missing windows and coverage;
- separate raw series from derived trend statistics.

Minimum fields:
- series_id, metric_id, scope, grain, from/to
- points[{period,value,n,coverage,method_compatibility}]
- trend direction, slope, volatility, change_vs_previous_window
- caveats

## 4. InterpretationRecord
Purpose: answer “what do these results mean?”.
Rules:
- interpretation is not a measurement;
- every statement must link to evidence/result IDs;
- period and scope are mandatory;
- confidence and limitations are mandatory;
- causal claims require stronger support than descriptive trend claims.

Minimum fields:
- interpretation_id, created_at, scope, period
- title, statement
- result_refs/evidence_refs
- confidence
- limitations
- interpretation_kind (descriptive / comparative / causal-hypothesis / decision-support)

## 5. ResearchHealthSnapshot
Purpose: answer “how trustworthy/current is the shown state?”.
Minimum fields:
- freshness by direction/source/method
- stale result count and reasons
- comparable-run ratio
- coverage by scope
- failed/partial runs
- unresolved conflicts / quality flags
- last system audit / release version

# Missing first-class runtime layer
The current system has most primitive data for these outputs, but it does **not yet have all five as canonical derived products**. The next backend step should be a Result Projection / Query layer that builds these products from the append-only ledgers and registries.
