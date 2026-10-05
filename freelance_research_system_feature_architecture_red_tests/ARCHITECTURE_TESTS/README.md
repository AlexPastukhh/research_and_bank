# Red architecture suite

This directory is the architecture plan. It intentionally describes **future behavior by failing tests**; there is no implementation under `src/research_system/` yet.

Run:

```bash
python -m unittest discover -s ARCHITECTURE_TESTS -p 'test_*.py' -v
```

Conventions used in test docstrings:

- `BASELINE` — behavior inherited from accepted v1.11 contracts/methods/use cases.
- `PROPOSAL` — architecture decision introduced for the feature/DDD migration and still changeable while the suite is red.

Implementation rule: do not weaken an assertion merely to make a test green. If evidence shows a proposed assertion is wrong, change the red contract explicitly before implementing the corresponding behavior.
