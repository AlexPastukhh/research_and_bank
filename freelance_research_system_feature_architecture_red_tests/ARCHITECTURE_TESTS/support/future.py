from __future__ import annotations
import hashlib
import importlib
import json
import os
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in os.sys.path:
    os.sys.path.insert(0, str(SRC))

class ArchitectureNotImplemented(AssertionError):
    pass

def require_symbol(module_name: str, symbol: str) -> Any:
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError as exc:
        raise ArchitectureNotImplemented(
            f"ARCHITECTURE RED: expected module {module_name!r} does not exist yet"
        ) from exc
    if not hasattr(module, symbol):
        raise ArchitectureNotImplemented(
            f"ARCHITECTURE RED: expected public symbol {module_name}.{symbol} does not exist yet"
        )
    return getattr(module, symbol)

def call_feature(module_name: str, project_root: Path, request: dict[str, Any], *, now: str | None = None, **kwargs: Any) -> dict[str, Any]:
    execute: Callable[..., Any] = require_symbol(module_name, "execute")
    result = execute(project_root, request, now=now, **kwargs)
    if not isinstance(result, dict):
        raise AssertionError(f"{module_name}.execute must return dict, got {type(result).__name__}")
    return result

def assert_error_code(testcase, expected: str, fn: Callable[[], Any]) -> None:
    try:
        fn()
    except Exception as exc:  # application/domain errors must expose stable machine code
        actual = getattr(exc, "code", None)
        testcase.assertEqual(actual, expected, f"wrong error from {type(exc).__name__}: {exc}")
        return
    testcase.fail(f"expected error code {expected!r}, but operation succeeded")

def tree_digest(root: Path) -> str:
    h = hashlib.sha256()
    if not root.exists():
        return h.hexdigest()
    for p in sorted(x for x in root.rglob('*') if x.is_file()):
        rel = p.relative_to(root).as_posix()
        if any(part in {'.git', '__pycache__', '.pytest_cache'} for part in p.relative_to(root).parts):
            continue
        h.update(rel.encode())
        h.update(b'\0')
        h.update(p.read_bytes())
        h.update(b'\0')
    return h.hexdigest()

def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
