# Bootstrap runbook

1. Inventory supplied files/archive(s).
2. Locate ProjectIndex/State/RunState if present.
3. Validate and report conflicts rather than silently resolving them.
4. Classify prior data/methods/sources as reusable, due, stale or broken.
5. Recover method/source routes.
6. Create a minimal DeltaPlan: REPAIR / REFRESH / CONTINUE / REDISCOVER.
7. Set `next_use_case_id` and `next_task_id` in RunState.
