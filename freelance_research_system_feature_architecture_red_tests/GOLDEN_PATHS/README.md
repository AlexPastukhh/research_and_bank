# Golden Paths

Golden Paths are executable end-to-end reference workflows for the system. They are intentionally hermetic: release-gate paths do not depend on live websites or network availability.

Canonical definitions live in `CORE/GOLDEN_PATH_REGISTRY.json`. The Markdown files in this directory explain each path; the executable implementation is `TOOLS/run_golden_paths.py`.

A Golden Path checks the whole public chain: **request → routing → use-case transitions → public tools/data → persisted state/output → acceptance**. It does not replace unit or adversarial regression tests.

Current release-gate paths: GP01 new project, GP02 baseline continuation, GP03 paid-work pipeline, GP04 daily monitoring, GP05 source management, GP06 method-change migration.
