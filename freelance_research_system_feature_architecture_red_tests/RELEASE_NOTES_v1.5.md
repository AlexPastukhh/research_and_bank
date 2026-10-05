# Release notes — v1.5.0

## Main changes

1. **Configurable runtime**: system defaults + project overrides + task overrides.
2. **Daily research ledger**: explicit research date/timezone and Daily Runs.
3. **Persistent entities + append-only observations**.
4. **Daily diffs**: new / changed / confirmed closed / reopened / not seen.
5. **Conservative disappearance semantics** to avoid false closure events.
6. **Interesting items by day** with manual/configurable-rule origin.
7. **Refactor-resistant testing model**: schema, semantic invariants, idempotency, metamorphic tests, mutation tests and integration smoke tests.
8. **Deterministic clocks** for tools/tests.

Runtime data and test policy remain versioned and replaceable; v1.5 adds supported primitives rather than freezing one market-research policy.
