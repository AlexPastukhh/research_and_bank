# Static contract checks

Isolated tooling environment; no product runtime/backend dependency chosen.
From project root on Windows:
```cmd
python -m venv PLANNING\TOOLS\.schema_validation_env
PLANNING\TOOLS\.schema_validation_env\Scripts\python.exe -m pip install -r PLANNING\TOOLS\schema_validation_requirements.txt
PLANNING\TOOLS\.schema_validation_env\Scripts\python.exe PLANNING\TOOLS\check_bank_contracts.py
PLANNING\TOOLS\.schema_validation_env\Scripts\python.exe PLANNING\TOOLS\test_bank_contracts.py
```
Resolved and pinned on Python 3.14 Windows during this task. No other platform compatibility is claimed.
The helper does not import or mutate Bank state. Do not use it as production path-confinement validation or a writer.
Development environment/dependencies are not product deliverables; no baseline/global Python packages changed.
