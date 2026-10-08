"""Isolated local exchange experiment; not a Universal Bank implementation."""
import argparse
import hashlib
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

BASE = Path(__file__).resolve().parent / "data"

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def scan(root):
    """Read only complete, verified bundles; build a disposable projection."""
    root = root.resolve()
    items, errors = [], []
    for marker in sorted(root.glob("*/READY.json")):
        try:
            bundle = marker.parent.resolve()
            entry = json.loads(marker.read_text(encoding="utf-8"))
            if entry.get("schema") != "local-exchange-trial-v1":
                raise ValueError("unknown experimental schema")
            if entry.get("id") != bundle.name or entry.get("kind") != "technical_trial":
                raise ValueError("invalid trial identity/kind")
            if not isinstance(entry.get("title"), str) or not entry["title"]:
                raise ValueError("missing title")
            path = (bundle / entry["report"]).resolve()
            if not path.is_relative_to(bundle) or not path.is_file():
                raise ValueError("report missing or outside bundle")
            if digest(path) != entry["sha256"]:
                raise ValueError("report checksum mismatch")
            items.append({
                "id": entry["id"], "title": entry["title"],
                "report": str(path), "sha256": entry["sha256"],
                "text": path.read_text(encoding="utf-8"),
            })
        except (OSError, ValueError, KeyError, TypeError) as exc:
            errors.append({"bundle": marker.parent.name, "error": str(exc)})
    return {"items": items, "errors": errors}

def publish_trial(root):
    root.mkdir(parents=True, exist_ok=True)
    bundle = root / ("trial-" + uuid4().hex[:12])
    bundle.mkdir()
    report = bundle / "report.md"
    report.write_text(
        "# Local file exchange trial\n\n"
        "Synthetic technical note, not a research result.\n\n"
        "Chosen trial route: ChatGPT -> Desktop Commander -> local files.\n"
        "Application ingestion remains to be implemented in Universal Bank.\n"
        "GitHub is optional history/sync for this local exchange.\n",
        encoding="utf-8",
    )
    assert not scan(root)["items"], "fresh root must ignore incomplete bundle"
    entry = {
        "schema": "local-exchange-trial-v1", "kind": "technical_trial",
        "id": bundle.name, "title": "Local file exchange trial",
        "report": "report.md", "sha256": digest(report),
    }
    pending = bundle / "READY.pending"
    pending.write_text(json.dumps(entry, indent=2), encoding="utf-8")
    os.replace(pending, bundle / "READY.json")
    return bundle

def demo():
    # A unique directory avoids overwriting existing materials.
    root = BASE / ("run-" + uuid4().hex[:12])
    bundle = publish_trial(root)
    result = scan(root)
    assert len(result["items"]) == 1 and not result["errors"]
    assert scan(root) == result, "repeat scan must return the same projection"
    # Negative checks are confined to a disposable synthetic copy.
    with TemporaryDirectory(prefix="checks-", dir=root) as temp:
        check_root = Path(temp)
        check_bundle = publish_trial(check_root)
        report = check_bundle / "report.md"
        report.write_text("modified", encoding="utf-8")
        assert not scan(check_root)["items"] and scan(check_root)["errors"]
        report.unlink()
        assert not scan(check_root)["items"] and scan(check_root)["errors"]
        marker = check_bundle / "READY.json"
        entry = json.loads(marker.read_text(encoding="utf-8"))
        entry["report"] = "../../outside.md"
        marker.write_text(json.dumps(entry), encoding="utf-8")
        assert not scan(check_root)["items"] and scan(check_root)["errors"]
    projection = root / "catalog.json"
    projection.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({
        "status": "PASS", "bundle": str(bundle), "catalog": str(projection),
        "checks": ["incomplete ignored", "complete report read",
                   "repeat scan stable", "tampering rejected",
                   "missing report rejected", "outside path rejected"],
        "limitation": "No UI, automatic watcher, or production Bank schema.",
    }, indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["demo", "scan"])
    parser.add_argument("--root", type=Path)
    args = parser.parse_args()
    if args.command == "demo":
        demo()
    else:
        if args.root is None:
            parser.error("scan requires --root")
        result = scan(args.root)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        raise SystemExit(bool(result["errors"]))
