#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST = ROOT / ".kb_state.json"

PRIMARY_LAYERS = [
    "raw_papers",
    "extraction",
    "notes",
    "concepts",
    "variables",
    "relationships",
    "systems",
    "questions",
    "meta_questions",
    "theory",
    "experiments",
    "dashboards",
    "home",
]

DERIVED_LAYERS = ["indexes", "outputs"]
ALL_LAYERS = PRIMARY_LAYERS + DERIVED_LAYERS

DISPLAY_NAMES = {
    "raw_papers": "raw/papers",
    "extraction": "raw/extracted",
    "notes": "notes",
    "concepts": "concepts",
    "variables": "variables",
    "relationships": "relationships",
    "systems": "systems",
    "questions": "questions",
    "meta_questions": "meta_questions",
    "theory": "theory",
    "experiments": "experiments",
    "dashboards": "dashboards",
    "home": "HOME",
    "indexes": "indexes",
    "outputs": "outputs",
}

DOWNSTREAM_START = {
    "raw_papers": "extraction",
    "extraction": "notes",
    "notes": "concepts",
    "concepts": "variables",
    "variables": "relationships",
    "relationships": "systems",
    "systems": "questions",
    "questions": "meta_questions",
    "meta_questions": "theory",
    "theory": "experiments",
    "experiments": "dashboards",
    "dashboards": "home",
    "home": None,
}


@dataclass
class FileSnapshot:
    path: str
    layer: str
    sha256: str
    size: int
    mtime_ns: int


@dataclass
class FileChange:
    path: str
    layer: str
    status: str


@dataclass
class ChangeReport:
    manifest_path: str
    manifest_exists: bool
    changed_layers: list[str]
    dirty_layers: list[str]
    changes: list[FileChange]
    changes_by_layer: dict[str, list[FileChange]]
    summary_lines: list[str]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iter_layer_files(layer: str) -> list[Path]:
    if layer == "raw_papers":
        root = ROOT / "raw" / "papers"
        pattern = "*.pdf"
    elif layer == "extraction":
        root = ROOT / "raw" / "extracted"
        pattern = "*.txt"
    elif layer == "notes":
        root = ROOT / "notes"
        pattern = "*.md"
    elif layer == "concepts":
        root = ROOT / "concepts"
        pattern = "*.md"
    elif layer == "variables":
        root = ROOT / "variables"
        pattern = "*.md"
    elif layer == "relationships":
        root = ROOT / "relationships"
        pattern = "*.md"
    elif layer == "systems":
        root = ROOT / "systems"
        pattern = "*.md"
    elif layer == "questions":
        root = ROOT / "questions"
        pattern = "*.md"
    elif layer == "meta_questions":
        root = ROOT / "meta_questions"
        pattern = "*.md"
    elif layer == "theory":
        root = ROOT / "theory"
        pattern = "*.md"
    elif layer == "experiments":
        root = ROOT / "experiments"
        pattern = "*.md"
    elif layer == "dashboards":
        root = ROOT / "dashboards"
        pattern = "*.md"
    elif layer == "indexes":
        root = ROOT / "indexes"
        pattern = "*.md"
    elif layer == "outputs":
        root = ROOT / "outputs"
        pattern = "*.md"
    elif layer == "home":
        home_path = ROOT / "HOME.md"
        return [home_path] if home_path.exists() else []
    else:
        raise ValueError(f"Unknown layer: {layer}")

    if not root.exists():
        return []

    paths = [path for path in root.rglob(pattern) if path.is_file()]
    if layer in {"concepts", "variables", "relationships", "systems"}:
        paths = [path for path in paths if path.name != "README.md"]
    elif layer == "indexes":
        paths = [path for path in paths if path.name != "README.md"]
    elif layer == "theory":
        paths = [path for path in paths if path.suffix == ".md" and path.name != "README.md"]
    elif layer == "experiments":
        paths = [path for path in paths if path.suffix == ".md" and path.name != "README.md"]
    return sorted(paths)


def detect_layer_for_path(relpath: str) -> str:
    if relpath == "HOME.md":
        return "home"
    if relpath.startswith("raw/papers/"):
        return "raw_papers"
    if relpath.startswith("raw/extracted/"):
        return "extraction"
    if relpath.startswith("notes/"):
        return "notes"
    if relpath.startswith("concepts/"):
        return "concepts"
    if relpath.startswith("variables/"):
        return "variables"
    if relpath.startswith("relationships/"):
        return "relationships"
    if relpath.startswith("systems/"):
        return "systems"
    if relpath.startswith("questions/"):
        return "questions"
    if relpath.startswith("meta_questions/"):
        return "meta_questions"
    if relpath.startswith("theory/"):
        return "theory"
    if relpath.startswith("experiments/"):
        return "experiments"
    if relpath.startswith("dashboards/"):
        return "dashboards"
    if relpath.startswith("indexes/"):
        return "indexes"
    if relpath.startswith("outputs/"):
        return "outputs"
    return "unknown"


def build_snapshot() -> dict[str, FileSnapshot]:
    snapshot: dict[str, FileSnapshot] = {}
    for layer in ALL_LAYERS:
        for path in iter_layer_files(layer):
            relpath = path.relative_to(ROOT).as_posix()
            stat = path.stat()
            snapshot[relpath] = FileSnapshot(
                path=relpath,
                layer=layer,
                sha256=sha256_file(path),
                size=stat.st_size,
                mtime_ns=stat.st_mtime_ns,
            )
    return snapshot


def load_manifest(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    raw = json.loads(path.read_text(encoding="utf-8"))
    files = raw.get("files", {})
    if not isinstance(files, dict):
        raise ValueError(f"Invalid manifest structure in {path}")
    return raw


def snapshot_from_manifest(data: dict[str, Any] | None) -> dict[str, FileSnapshot]:
    if not data:
        return {}
    snapshot: dict[str, FileSnapshot] = {}
    for relpath, payload in data.get("files", {}).items():
        snapshot[relpath] = FileSnapshot(
            path=relpath,
            layer=str(payload.get("layer") or detect_layer_for_path(relpath)),
            sha256=str(payload.get("sha256") or ""),
            size=int(payload.get("size") or 0),
            mtime_ns=int(payload.get("mtime_ns") or 0),
        )
    return snapshot


def diff_snapshots(
    previous: dict[str, FileSnapshot],
    current: dict[str, FileSnapshot],
) -> list[FileChange]:
    changes: list[FileChange] = []
    for relpath in sorted(set(previous) | set(current)):
        old = previous.get(relpath)
        new = current.get(relpath)
        if old is None and new is not None:
            changes.append(FileChange(path=relpath, layer=new.layer, status="added"))
            continue
        if old is not None and new is None:
            changes.append(FileChange(path=relpath, layer=old.layer, status="deleted"))
            continue
        if old is None or new is None:
            continue
        if old.sha256 != new.sha256:
            changes.append(FileChange(path=relpath, layer=new.layer, status="modified"))
    return changes


def group_changes_by_layer(changes: list[FileChange]) -> dict[str, list[FileChange]]:
    grouped = {layer: [] for layer in ALL_LAYERS}
    for change in changes:
        grouped.setdefault(change.layer, []).append(change)
    return {layer: items for layer, items in grouped.items() if items}


def downstream_layers_from(layer: str) -> list[str]:
    start = DOWNSTREAM_START.get(layer)
    if start is None:
        return []
    start_index = PRIMARY_LAYERS.index(start)
    return PRIMARY_LAYERS[start_index:]


def summarize_changes(
    manifest_path: Path,
    manifest_exists: bool,
    changed_layers: list[str],
    dirty_layers: list[str],
    changes_by_layer: dict[str, list[FileChange]],
) -> list[str]:
    lines: list[str] = []
    if manifest_exists:
        lines.append(f"Manifest: {manifest_path.relative_to(ROOT)}")
    else:
        lines.append(f"Manifest missing: {manifest_path.relative_to(ROOT)}")
        lines.append("Assuming a bootstrap run and marking the pipeline dirty from extraction onward.")

    if not changes_by_layer:
        lines.append("No tracked file changes detected.")
    else:
        lines.append("Tracked changes since the last successful run:")
        for layer in ALL_LAYERS:
            layer_changes = changes_by_layer.get(layer)
            if not layer_changes:
                continue
            display = DISPLAY_NAMES.get(layer, layer)
            lines.append(f"- {display}:")
            for change in layer_changes:
                lines.append(f"  - {change.status}: {change.path}")

    changed_display = ", ".join(DISPLAY_NAMES[layer] for layer in changed_layers) if changed_layers else "none"
    dirty_display = ", ".join(DISPLAY_NAMES[layer] for layer in dirty_layers) if dirty_layers else "none"
    lines.append(f"Changed layers: {changed_display}")
    lines.append(f"Dirty layers to update: {dirty_display}")
    return lines


def detect_changes(manifest_path: Path = DEFAULT_MANIFEST) -> ChangeReport:
    manifest_data = load_manifest(manifest_path)
    previous_snapshot = snapshot_from_manifest(manifest_data)
    current_snapshot = build_snapshot()
    changes = diff_snapshots(previous_snapshot, current_snapshot)
    changes_by_layer = group_changes_by_layer(changes)

    if manifest_data is None:
        changed_layers = [layer for layer in PRIMARY_LAYERS if iter_layer_files(layer)]
        dirty_layers = PRIMARY_LAYERS[1:] if changed_layers else []
    else:
        changed_layers = [layer for layer in PRIMARY_LAYERS if changes_by_layer.get(layer)]
        dirty_layers_set: set[str] = set()
        for layer in changed_layers:
            dirty_layers_set.update(downstream_layers_from(layer))
        dirty_layers = [layer for layer in PRIMARY_LAYERS if layer in dirty_layers_set]

    summary_lines = summarize_changes(
        manifest_path=manifest_path,
        manifest_exists=manifest_data is not None,
        changed_layers=changed_layers,
        dirty_layers=dirty_layers,
        changes_by_layer=changes_by_layer,
    )
    return ChangeReport(
        manifest_path=str(manifest_path),
        manifest_exists=manifest_data is not None,
        changed_layers=changed_layers,
        dirty_layers=dirty_layers,
        changes=changes,
        changes_by_layer=changes_by_layer,
        summary_lines=summary_lines,
    )


def save_manifest(path: Path, snapshot: dict[str, FileSnapshot]) -> None:
    payload = {
        "version": 1,
        "repo_root": str(ROOT),
        "files": {
            relpath: asdict(entry)
            for relpath, entry in sorted(snapshot.items())
        },
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def report_to_json(report: ChangeReport) -> str:
    payload = {
        "manifest_path": report.manifest_path,
        "manifest_exists": report.manifest_exists,
        "changed_layers": report.changed_layers,
        "dirty_layers": report.dirty_layers,
        "changes": [asdict(change) for change in report.changes],
        "changes_by_layer": {
            layer: [asdict(change) for change in changes]
            for layer, changes in report.changes_by_layer.items()
        },
        "summary_lines": report.summary_lines,
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Detect KB layer changes and compute downstream dirty layers."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help="Path to the manifest file. Defaults to .kb_state.json in the repo root.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the report as JSON instead of a human-readable summary.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = detect_changes(args.manifest)
    if args.json:
        print(report_to_json(report))
        return 0

    for line in report.summary_lines:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
