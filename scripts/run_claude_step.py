#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = ROOT / "prompts"

LAYER_TEMPLATE_FILES = {
    "notes": "notes.md",
    "concepts": "concepts.md",
    "variables": "variables.md",
    "relationships": "relationships.md",
    "systems": "systems.md",
    "questions": "questions.md",
    "meta_questions": "meta_questions.md",
    "theory": "theory.md",
    "experiments": "experiments.md",
    "home": "home.md",
}

DISPLAY_NAMES = {
    "notes": "notes",
    "concepts": "concepts",
    "variables": "variables",
    "relationships": "relationships",
    "systems": "systems",
    "questions": "questions",
    "meta_questions": "meta_questions",
    "theory": "theory",
    "experiments": "experiments",
    "home": "HOME",
}


@dataclass
class StepResult:
    layer: str
    success: bool
    command: list[str]
    prompt_text: str
    agent_message: str
    stdout: str
    stderr: str
    returncode: int
    dry_run: bool


def load_context(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def bullet_list(items: list[str]) -> str:
    if not items:
        return "- none"
    return "\n".join(f"- {item}" for item in items)


def render_changes_by_layer(changes_by_layer: dict[str, Any]) -> str:
    if not changes_by_layer:
        return "- none"
    lines: list[str] = []
    for layer in sorted(changes_by_layer):
        entries = changes_by_layer[layer]
        lines.append(f"- {DISPLAY_NAMES.get(layer, layer)}:")
        if not entries:
            lines.append("  - none")
            continue
        for entry in entries:
            if isinstance(entry, dict):
                status = entry.get("status", "changed")
                path = entry.get("path", "")
            else:
                status = getattr(entry, "status", "changed")
                path = getattr(entry, "path", "")
            lines.append(f"  - {status}: {path}")
    return "\n".join(lines)


def render_prompt(layer: str, context: dict[str, Any]) -> str:
    if layer not in LAYER_TEMPLATE_FILES:
        raise ValueError(f"No prompt template configured for layer: {layer}")

    template_path = PROMPTS_DIR / LAYER_TEMPLATE_FILES[layer]
    template = template_path.read_text(encoding="utf-8")
    replacements = {
        "ROOT": str(ROOT),
        "LAYER_DISPLAY": DISPLAY_NAMES.get(layer, layer),
        "DIRTY_LAYERS": bullet_list([DISPLAY_NAMES.get(item, item) for item in context.get("dirty_layers", [])]),
        "CHANGED_LAYERS": bullet_list([DISPLAY_NAMES.get(item, item) for item in context.get("changed_layers", [])]),
        "CHANGES_BY_LAYER": render_changes_by_layer(context.get("changes_by_layer", {})),
        "SUMMARY_LINES": bullet_list(context.get("summary_lines", [])),
    }

    prompt = template
    for key, value in replacements.items():
        prompt = prompt.replace(f"{{{{{key}}}}}", value)
    return prompt


def build_command(
    claude_bin: str,
    model: str | None,
    permission_mode: str,
    skip_permissions: bool,
    add_dirs: list[Path] | None = None,
) -> list[str]:
    command = [
        claude_bin,
        "-p",
        "--output-format",
        "json",
    ]
    if skip_permissions:
        command.append("--dangerously-skip-permissions")
    else:
        command.extend(["--permission-mode", permission_mode])
    if model:
        command.extend(["--model", model])
    for directory in add_dirs or []:
        command.extend(["--add-dir", str(directory)])
    return command


def extract_agent_message(stdout: str) -> str:
    stdout = stdout.strip()
    if not stdout:
        return ""
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError:
        return stdout
    if isinstance(payload, dict):
        for key in ("result", "response", "message", "text"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return stdout


def run_claude_step(
    layer: str,
    context: dict[str, Any] | None = None,
    *,
    claude_bin: str = "claude",
    model: str | None = None,
    permission_mode: str = "acceptEdits",
    skip_permissions: bool = True,
    dry_run: bool = False,
) -> StepResult:
    context = context or {}
    prompt_text = render_prompt(layer, context)

    if dry_run:
        return StepResult(
            layer=layer,
            success=True,
            command=build_command(
                claude_bin=claude_bin,
                model=model,
                permission_mode=permission_mode,
                skip_permissions=skip_permissions,
                add_dirs=[ROOT],
            )
            + ["<prompt via stdin>"],
            prompt_text=prompt_text,
            agent_message="",
            stdout="",
            stderr="",
            returncode=0,
            dry_run=True,
        )

    if shutil.which(claude_bin) is None:
        return StepResult(
            layer=layer,
            success=False,
            command=[claude_bin, "-p"],
            prompt_text=prompt_text,
            agent_message="",
            stdout="",
            stderr=f"Could not find `{claude_bin}` on PATH.",
            returncode=127,
            dry_run=False,
        )

    command = build_command(
        claude_bin=claude_bin,
        model=model,
        permission_mode=permission_mode,
        skip_permissions=skip_permissions,
        add_dirs=[ROOT],
    )

    completed = subprocess.run(
        command,
        input=prompt_text,
        text=True,
        capture_output=True,
        cwd=ROOT,
    )
    agent_message = extract_agent_message(completed.stdout)
    return StepResult(
        layer=layer,
        success=completed.returncode == 0,
        command=command + ["<prompt via stdin>"],
        prompt_text=prompt_text,
        agent_message=agent_message,
        stdout=completed.stdout,
        stderr=completed.stderr,
        returncode=completed.returncode,
        dry_run=False,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render and run a layer-specific Claude Code step for the KB pipeline."
    )
    parser.add_argument("--layer", required=True, choices=sorted(LAYER_TEMPLATE_FILES))
    parser.add_argument(
        "--context-file",
        type=Path,
        help="Optional JSON file with dirty-layer and change-summary context.",
    )
    parser.add_argument("--claude-bin", default="claude")
    parser.add_argument("--model")
    parser.add_argument(
        "--permission-mode",
        default="acceptEdits",
        choices=["default", "plan", "acceptEdits", "bypassPermissions"],
    )
    parser.add_argument(
        "--no-skip-permissions",
        dest="skip_permissions",
        action="store_false",
        help="Honor --permission-mode instead of --dangerously-skip-permissions.",
    )
    parser.set_defaults(skip_permissions=True)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    context = load_context(args.context_file)
    result = run_claude_step(
        layer=args.layer,
        context=context,
        claude_bin=args.claude_bin,
        model=args.model,
        permission_mode=args.permission_mode,
        skip_permissions=args.skip_permissions,
        dry_run=args.dry_run,
    )

    print(f"Layer: {DISPLAY_NAMES.get(result.layer, result.layer)}")
    print("Command:")
    print(" ".join(result.command))
    print("")
    print("Prompt:")
    print(result.prompt_text)

    if result.dry_run:
        return 0

    print("")
    print(f"Return code: {result.returncode}")
    if result.agent_message:
        print("")
        print("Agent message:")
        print(result.agent_message)
    if result.stderr:
        print("")
        print("stderr:")
        print(result.stderr.strip())
    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
