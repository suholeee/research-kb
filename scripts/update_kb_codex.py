#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

from detect_changes import (
    DEFAULT_MANIFEST,
    DISPLAY_NAMES,
    PRIMARY_LAYERS,
    build_snapshot,
    detect_changes,
    diff_snapshots,
    group_changes_by_layer,
    save_manifest,
)
from run_codex_step import run_codex_step


ROOT = Path(__file__).resolve().parent.parent

LLM_LAYERS = {
    "notes",
    "concepts",
    "variables",
    "relationships",
    "systems",
    "questions",
    "meta_questions",
    "theory",
    "experiments",
    "home",
}

STEP_ALLOWED_WRITE_LAYERS = {
    "extraction": {"extraction"},
    "notes": {"notes"},
    "concepts": {"concepts"},
    "variables": {"variables"},
    "relationships": {"relationships"},
    "systems": {"systems"},
    "questions": {"questions"},
    "meta_questions": {"meta_questions"},
    "theory": {"theory"},
    "experiments": {"experiments"},
    "dashboards": {"dashboards"},
    "home": {"home"},
    "validate_notes": set(),
    "build_indexes": {"indexes"},
    "extract_concepts_report": {"outputs"},
}


@dataclass
class ExecutedStep:
    name: str
    success: bool
    changed_files: list[dict[str, str]]
    detail: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Update the markdown KB incrementally from detected upstream changes."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help="Path to the KB state manifest. Defaults to .kb_state.json in the repo root.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Only report what would run.")
    parser.add_argument("--codex-bin", default="codex", help="Codex CLI binary to invoke.")
    parser.add_argument("--model", help="Optional Codex model override.")
    parser.add_argument("--profile", help="Optional Codex profile override.")
    parser.add_argument(
        "--start-at",
        choices=PRIMARY_LAYERS[1:],
        help="Resume at this dirty layer, skipping earlier dirty layers already handled.",
    )
    return parser.parse_args()


def display(layer: str) -> str:
    return DISPLAY_NAMES.get(layer, layer)


def format_change_list(changes: list[dict[str, str]]) -> str:
    if not changes:
        return "none"
    return ", ".join(f"{item['status']} {item['path']}" for item in changes)


def format_layer_list(layers: list[str]) -> str:
    if not layers:
        return "none"
    return ", ".join(display(layer) for layer in layers)


def changed_raw_pdf_paths(changes_by_layer: dict[str, list[dict[str, str]]]) -> list[str]:
    return [
        entry["path"]
        for entry in changes_by_layer.get("raw_papers", [])
        if entry.get("status") in {"added", "modified"}
    ]


def build_extraction_command(
    manifest: Path,
    changes_by_layer: dict[str, list[dict[str, str]]],
) -> list[str]:
    command = [
        sys.executable,
        str(ROOT / "scripts" / "extract_papers.py"),
        "--manifest",
        str(manifest),
    ]
    for pdf_path in changed_raw_pdf_paths(changes_by_layer):
        command.extend(["--pdf", pdf_path])
    return command


def latest_step_changes(step_log: list[ExecutedStep], step_name: str) -> list[dict[str, str]]:
    if not step_log or step_log[-1].name != step_name:
        return []
    return step_log[-1].changed_files


def merged_changes_by_layer(existing: dict[str, list[dict[str, str]]], new_items: list[Any]) -> dict[str, list[dict[str, str]]]:
    merged = {layer: [dict(item) for item in items] for layer, items in existing.items()}
    for item in new_items:
        payload = asdict(item) if hasattr(item, "__dataclass_fields__") else dict(item)
        layer = str(payload["layer"])
        merged.setdefault(layer, [])
        merged[layer] = [entry for entry in merged[layer] if entry["path"] != payload["path"]]
        merged[layer].append(
            {
                "path": str(payload["path"]),
                "layer": layer,
                "status": str(payload["status"]),
            }
        )
        merged[layer].sort(key=lambda entry: entry["path"])
    return merged


def build_layer_context(
    report: Any,
    dirty_layers: list[str],
    changes_by_layer: dict[str, list[dict[str, str]]],
) -> dict[str, Any]:
    return {
        "changed_layers": report.changed_layers,
        "dirty_layers": dirty_layers,
        "changes_by_layer": changes_by_layer,
        "summary_lines": report.summary_lines,
    }


def ensure_allowed_writes(step_name: str, diff_items: list[Any]) -> tuple[bool, str]:
    allowed = STEP_ALLOWED_WRITE_LAYERS[step_name]
    unexpected = [
        f"{item.status} {item.path} ({item.layer})"
        for item in diff_items
        if item.layer not in allowed
    ]
    if unexpected:
        return False, "; ".join(unexpected)
    return True, ""


def run_local_command(
    step_name: str,
    command: list[str],
    *,
    dry_run: bool,
    working_snapshot: dict[str, Any],
    step_log: list[ExecutedStep],
    changes_by_layer: dict[str, list[dict[str, str]]],
) -> tuple[bool, dict[str, Any], dict[str, list[dict[str, str]]]]:
    if dry_run:
        step_log.append(
            ExecutedStep(
                name=step_name,
                success=True,
                changed_files=[],
                detail="would run: " + " ".join(command),
            )
        )
        return True, working_snapshot, changes_by_layer

    completed = subprocess.run(
        command,
        text=True,
        capture_output=True,
        cwd=ROOT,
    )
    detail_parts = []
    if completed.stdout.strip():
        detail_parts.append(completed.stdout.strip())
    if completed.stderr.strip():
        detail_parts.append(completed.stderr.strip())
    detail = "\n".join(detail_parts).strip()
    if completed.returncode != 0:
        step_log.append(
            ExecutedStep(
                name=step_name,
                success=False,
                changed_files=[],
                detail=detail or f"command exited with status {completed.returncode}",
            )
        )
        return False, working_snapshot, changes_by_layer

    new_snapshot = build_snapshot()
    diff_items = diff_snapshots(working_snapshot, new_snapshot)
    allowed, unexpected = ensure_allowed_writes(step_name, diff_items)
    if not allowed:
        step_log.append(
            ExecutedStep(
                name=step_name,
                success=False,
                changed_files=[asdict(item) for item in diff_items],
                detail=f"unexpected file writes: {unexpected}",
            )
        )
        return False, working_snapshot, changes_by_layer

    updated_changes = merged_changes_by_layer(changes_by_layer, diff_items)
    step_log.append(
        ExecutedStep(
            name=step_name,
            success=True,
            changed_files=[asdict(item) for item in diff_items],
            detail=detail or "ok",
        )
    )
    return True, new_snapshot, updated_changes


def run_codex_layer(
    layer: str,
    *,
    report: Any,
    dirty_layers: list[str],
    working_snapshot: dict[str, Any],
    step_log: list[ExecutedStep],
    changes_by_layer: dict[str, list[dict[str, str]]],
    codex_bin: str,
    model: str | None,
    profile: str | None,
    dry_run: bool,
) -> tuple[bool, dict[str, Any], dict[str, list[dict[str, str]]]]:
    context = build_layer_context(report, dirty_layers, changes_by_layer)
    result = run_codex_step(
        layer=layer,
        context=context,
        codex_bin=codex_bin,
        model=model,
        profile=profile,
        dry_run=dry_run,
    )
    if not result.success:
        detail = result.stderr.strip() or result.stdout.strip() or f"`codex exec` returned {result.returncode}"
        step_log.append(
            ExecutedStep(
                name=layer,
                success=False,
                changed_files=[],
                detail=detail,
            )
        )
        return False, working_snapshot, changes_by_layer

    if dry_run:
        step_log.append(
            ExecutedStep(
                name=layer,
                success=True,
                changed_files=[],
                detail="would run: " + " ".join(result.command),
            )
        )
        return True, working_snapshot, changes_by_layer

    new_snapshot = build_snapshot()
    diff_items = diff_snapshots(working_snapshot, new_snapshot)
    allowed, unexpected = ensure_allowed_writes(layer, diff_items)
    if not allowed:
        step_log.append(
            ExecutedStep(
                name=layer,
                success=False,
                changed_files=[asdict(item) for item in diff_items],
                detail=f"unexpected file writes: {unexpected}",
            )
        )
        return False, working_snapshot, changes_by_layer

    updated_changes = merged_changes_by_layer(changes_by_layer, diff_items)
    detail_parts = []
    if result.agent_message:
        detail_parts.append(result.agent_message)
    if result.stderr.strip():
        detail_parts.append(result.stderr.strip())
    detail = "\n".join(detail_parts).strip() or "ok"
    step_log.append(
        ExecutedStep(
            name=layer,
            success=True,
            changed_files=[asdict(item) for item in diff_items],
            detail=detail,
        )
    )
    return True, new_snapshot, updated_changes


def maybe_run_note_hooks(
    *,
    note_inputs_changed: bool,
    dirty_layers: list[str],
    working_snapshot: dict[str, Any],
    step_log: list[ExecutedStep],
    changes_by_layer: dict[str, list[dict[str, str]]],
    dry_run: bool,
) -> tuple[bool, dict[str, Any], dict[str, list[dict[str, str]]]]:
    if not note_inputs_changed:
        return True, working_snapshot, changes_by_layer

    ok, working_snapshot, changes_by_layer = run_local_command(
        "validate_notes",
        [sys.executable, str(ROOT / "scripts" / "validate_notes.py")],
        dry_run=dry_run,
        working_snapshot=working_snapshot,
        step_log=step_log,
        changes_by_layer=changes_by_layer,
    )
    if not ok:
        return False, working_snapshot, changes_by_layer

    ok, working_snapshot, changes_by_layer = run_local_command(
        "build_indexes",
        [sys.executable, str(ROOT / "scripts" / "build_indexes.py")],
        dry_run=dry_run,
        working_snapshot=working_snapshot,
        step_log=step_log,
        changes_by_layer=changes_by_layer,
    )
    return ok, working_snapshot, changes_by_layer


def maybe_run_concept_report(
    *,
    concept_inputs_changed: bool,
    working_snapshot: dict[str, Any],
    step_log: list[ExecutedStep],
    changes_by_layer: dict[str, list[dict[str, str]]],
    dry_run: bool,
) -> tuple[bool, dict[str, Any], dict[str, list[dict[str, str]]]]:
    if not concept_inputs_changed:
        return True, working_snapshot, changes_by_layer

    return run_local_command(
        "extract_concepts_report",
        [sys.executable, str(ROOT / "scripts" / "extract_concepts.py")],
        dry_run=dry_run,
        working_snapshot=working_snapshot,
        step_log=step_log,
        changes_by_layer=changes_by_layer,
    )


def print_report(report: Any) -> None:
    for line in report.summary_lines:
        print(line)


def print_execution_plan(dirty_layers: list[str]) -> None:
    if not dirty_layers:
        print("Execution plan: nothing to do.")
        return
    print("Execution plan:")
    for layer in dirty_layers:
        mode = "codex exec" if layer in LLM_LAYERS else "deterministic script"
        print(f"- {display(layer)} via {mode}")


def print_step_log(step_log: list[ExecutedStep]) -> None:
    print("Step summary:")
    for step in step_log:
        status = "ok" if step.success else "failed"
        print(f"- {step.name}: {status}")
        if step.changed_files:
            print(f"  changed: {format_change_list(step.changed_files)}")
        if step.detail:
            first_line = step.detail.splitlines()[0]
            print(f"  detail: {first_line}")


def filter_dirty_layers(dirty_layers: list[str], start_at: str | None) -> list[str]:
    if not start_at:
        return list(dirty_layers)
    start_index = PRIMARY_LAYERS.index(start_at)
    return [layer for layer in dirty_layers if PRIMARY_LAYERS.index(layer) >= start_index]


def main() -> int:
    args = parse_args()
    report = detect_changes(args.manifest)
    active_dirty_layers = filter_dirty_layers(report.dirty_layers, args.start_at)
    print_report(report)
    if args.start_at:
        skipped_layers = [layer for layer in report.dirty_layers if layer not in active_dirty_layers]
        print(f"Resume start layer: {display(args.start_at)}")
        if skipped_layers:
            print(f"Skipped earlier dirty layers: {format_layer_list(skipped_layers)}")
    print("")
    print_execution_plan(active_dirty_layers)

    if not active_dirty_layers:
        if args.start_at and report.dirty_layers:
            print("")
            print("No dirty layers at or after the resume start. Manifest was not updated.")
            return 0
        if args.dry_run:
            print("")
            if report.changes:
                print("Dry run only. No pipeline steps are required, but the manifest would be refreshed to capture the current state.")
            else:
                print("Dry run only. No files were modified and the manifest was not updated.")
            return 0

        if report.changes:
            save_manifest(args.manifest, build_snapshot())
            print("")
            print(f"Updated manifest: {args.manifest.relative_to(ROOT)}")
        return 0

    if args.dry_run:
        print("")
        print("Dry run only. No files were modified and the manifest was not updated.")
        return 0

    working_snapshot = build_snapshot()
    changes_by_layer = {
        layer: [asdict(item) for item in items]
        for layer, items in report.changes_by_layer.items()
    }
    step_log: list[ExecutedStep] = []

    note_inputs_changed = "notes" in report.changed_layers and "notes" not in report.dirty_layers
    if note_inputs_changed:
        ok, working_snapshot, changes_by_layer = maybe_run_note_hooks(
            note_inputs_changed=True,
            dirty_layers=report.dirty_layers,
            working_snapshot=working_snapshot,
            step_log=step_log,
            changes_by_layer=changes_by_layer,
            dry_run=False,
        )
        if not ok:
            print("")
            print_step_log(step_log)
            print("")
            print("Manifest not updated because the run did not complete successfully.")
            return 1

    concept_inputs_changed = "concepts" in report.changed_layers and "concepts" not in report.dirty_layers
    if concept_inputs_changed:
        ok, working_snapshot, changes_by_layer = maybe_run_concept_report(
            concept_inputs_changed=True,
            working_snapshot=working_snapshot,
            step_log=step_log,
            changes_by_layer=changes_by_layer,
            dry_run=False,
        )
        if not ok:
            print("")
            print_step_log(step_log)
            print("")
            print("Manifest not updated because the run did not complete successfully.")
            return 1

    for index, layer in enumerate(active_dirty_layers):
        remaining_dirty_layers = active_dirty_layers[index + 1 :]
        if layer == "extraction":
            ok, working_snapshot, changes_by_layer = run_local_command(
                "extraction",
                build_extraction_command(args.manifest, changes_by_layer),
                dry_run=False,
                working_snapshot=working_snapshot,
                step_log=step_log,
                changes_by_layer=changes_by_layer,
            )
        elif layer == "dashboards":
            ok, working_snapshot, changes_by_layer = run_local_command(
                "dashboards",
                [sys.executable, str(ROOT / "scripts" / "build_dashboards.py")],
                dry_run=False,
                working_snapshot=working_snapshot,
                step_log=step_log,
                changes_by_layer=changes_by_layer,
            )
        else:
            ok, working_snapshot, changes_by_layer = run_codex_layer(
                layer,
                report=report,
                dirty_layers=remaining_dirty_layers,
                working_snapshot=working_snapshot,
                step_log=step_log,
                changes_by_layer=changes_by_layer,
                codex_bin=args.codex_bin,
                model=args.model,
                profile=args.profile,
                dry_run=False,
            )
        if not ok:
            print("")
            print_step_log(step_log)
            print("")
            print("Manifest not updated because the run did not complete successfully.")
            return 1

        layer_changes = latest_step_changes(step_log, layer)
        if layer == "notes":
            ok, working_snapshot, changes_by_layer = maybe_run_note_hooks(
                note_inputs_changed=bool(layer_changes),
                dirty_layers=remaining_dirty_layers,
                working_snapshot=working_snapshot,
                step_log=step_log,
                changes_by_layer=changes_by_layer,
                dry_run=False,
            )
            if not ok:
                print("")
                print_step_log(step_log)
                print("")
                print("Manifest not updated because the run did not complete successfully.")
                return 1

        if layer == "concepts":
            ok, working_snapshot, changes_by_layer = maybe_run_concept_report(
                concept_inputs_changed=bool(layer_changes),
                working_snapshot=working_snapshot,
                step_log=step_log,
                changes_by_layer=changes_by_layer,
                dry_run=False,
            )
            if not ok:
                print("")
                print_step_log(step_log)
                print("")
                print("Manifest not updated because the run did not complete successfully.")
                return 1

    final_snapshot = build_snapshot()
    save_manifest(args.manifest, final_snapshot)

    print("")
    print_step_log(step_log)
    print("")
    print(f"Updated manifest: {args.manifest.relative_to(ROOT)}")
    print("KB update completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
