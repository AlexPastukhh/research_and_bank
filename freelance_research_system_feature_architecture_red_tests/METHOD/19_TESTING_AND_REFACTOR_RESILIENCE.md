# Testing and refactor resilience

Test public semantic contracts, not JSON formatting, worksheet IDs, helper function names or incidental ordering. Tests are offline when possible, use frozen clocks for temporal logic, include idempotency/metamorphic/mutation/adversarial cases, and every fixed release-gate defect gets a regression test.
