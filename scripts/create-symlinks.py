#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "click",
#     "rich",
# ]
# ///

"""
create-symlinks.py

Creates symlinks from the cape repository to a target directory.

This script creates symbolic links from the cape repository to a target directory:
- Agent files (.md): agents/claude-code -> .claude/agents, agents/opencode -> .opencode/agent
- Hook files: hooks/claude-code -> .claude/hooks
- Command files: commands/claude-code -> .claude/commands
- Documentation: ai_docs -> ai_docs

Creates parent directories automatically and replaces existing symlinks.
Preserves existing regular directories and files.

NOTE: On Windows, requires administrator privileges to create symbolic links.
"""

import os
import sys
import shutil
from pathlib import Path
from typing import NamedTuple
from dataclasses import dataclass

import click
from rich.console import Console
from rich.prompt import Confirm

console = Console()

# Constants
ENV_SAMPLE_FILE = ".env.hooks.example"
REQUIRED_DIRS = ["agents", "hooks", "commands", "scripts"]


@dataclass
class SymlinkMapping:
    """Configuration for symlink mappings."""
    source_dir: str
    target_base: str
    pattern: str
    label: str
    recursive: bool = False


# Configurable symlink mappings
SYMLINK_CONFIG = [
    SymlinkMapping("agents/claude-code", ".claude/agents", "*.md", "Agents", recursive=False),
    SymlinkMapping("agents/opencode", ".opencode/agent", "*.md", "Agents", recursive=False),
    SymlinkMapping("hooks/claude-code", ".claude/hooks", "*", "Hooks", recursive=True),
    SymlinkMapping("commands/claude-code", ".claude/commands", "*", "Commands", recursive=True),
    SymlinkMapping("ai_docs", "ai_docs", "*.md", "AI docs", recursive=False),
]


class OperationResult(NamedTuple):
    """Result of a symlink operation."""
    success: bool
    message: str


def get_repo_root() -> Path:
    """Get the repository root directory."""
    script_path = Path(__file__).resolve()
    repo_root = script_path.parent.parent
    return repo_root


def validate_repository(repo_root: Path) -> None:
    """Validate that we're in the cape repository."""
    missing_dirs = [d for d in REQUIRED_DIRS if not (repo_root / d).exists()]
    if missing_dirs:
        console.print(
            f"[red]Error: Must run from cape repository root (missing directories: {', '.join(missing_dirs)})[/red]"
        )
        sys.exit(1)


def expand_and_resolve_path(path_str: str) -> Path:
    """Expand ~ and resolve to absolute path."""
    # First expand user home directory
    path = Path(path_str).expanduser()
    # If already absolute, resolve it; otherwise make it absolute from current directory
    if path.is_absolute():
        return path.resolve()
    else:
        return Path.cwd().joinpath(path).resolve()


def validate_target_directory(target_dir: Path) -> None:
    """Validate target directory parent exists and is writable."""
    if not target_dir.is_absolute():
        console.print(f"[red]Error: Target must be absolute path: {target_dir}[/red]")
        sys.exit(1)

    parent = target_dir.parent
    if not parent.exists():
        console.print(f"[red]Error: Parent directory of target does not exist: {parent}[/red]")
        sys.exit(1)

    if not os.access(parent, os.W_OK):
        console.print(f"[red]Error: No write permission to create target directory: {parent}[/red]")
        sys.exit(1)


def find_files(source_path: Path, pattern: str, recursive: bool) -> list[Path]:
    """Find files and directories matching pattern in source directory."""
    if not source_path.exists():
        return []

    if recursive:
        # For recursive, use rglob to get both files and directories
        # This matches shell behavior for hooks/commands that may contain subdirectories
        items = []
        for item in source_path.rglob(pattern):
            # Skip items in hidden directories (starting with .)
            if not any(part.startswith('.') for part in item.relative_to(source_path).parts[:-1]):
                items.append(item)
        return items
    else:
        # For non-recursive, use glob to get only files (matches *.md pattern usage)
        return [f for f in source_path.glob(pattern) if f.is_file()]


def create_symlink(
    repo_root: Path,
    target_dir: Path,
    source_rel: str,
    target_rel: str,
    description: str
) -> OperationResult:
    """
    Create a single symlink.

    Returns OperationResult with success status and message.
    """
    source_path = repo_root / source_rel
    target_path = target_dir / target_rel

    # Verify source exists
    if not source_path.exists():
        return OperationResult(False, f"Source missing: {source_path}")

    # Create parent directory
    target_path.parent.mkdir(parents=True, exist_ok=True)

    # Handle existing target
    if target_path.exists() or target_path.is_symlink():
        if target_path.is_symlink():
            # It's a symlink, replace it
            target_path.unlink()
        elif target_path.is_dir():
            # It's a directory, skip
            return OperationResult(False, f"Target directory exists, skipping: {target_path}")
        else:
            # It's a file, skip
            return OperationResult(False, f"Target file exists, skipping: {target_path}")

    # Create symlink
    try:
        target_path.symlink_to(source_path, target_is_directory=source_path.is_dir())
        return OperationResult(True, description)
    except OSError as e:
        return OperationResult(False, f"{description} failed: {e}")


def process_mapping(
    repo_root: Path,
    target_dir: Path,
    mapping: SymlinkMapping
) -> tuple[int, int]:
    """
    Process a symlink mapping configuration.

    Returns (total_ops, success_ops) tuple.
    """
    source_path = repo_root / mapping.source_dir

    if not source_path.exists():
        console.print(f"[yellow]Warning: {mapping.label} directory not found: {source_path}[/yellow]")
        return (0, 0)

    console.print(f"Processing {mapping.label}...")

    # Find files matching pattern
    files = find_files(source_path, mapping.pattern, mapping.recursive)

    total_ops = 0
    success_ops = 0

    for file_path in files:
        # Calculate relative path from source_path to maintain directory structure
        relative_path = file_path.relative_to(source_path)
        source_rel = str(Path(mapping.source_dir) / relative_path)
        target_rel = str(Path(mapping.target_base) / relative_path)
        description = f"{mapping.label}: {relative_path}"

        total_ops += 1
        result = create_symlink(repo_root, target_dir, source_rel, target_rel, description)

        if result.success:
            console.print(f"[green]✓ {result.message}[/green]")
            success_ops += 1
        else:
            console.print(f"[yellow]Warning: {result.message}[/yellow]")

    return (total_ops, success_ops)


def handle_env_sample(repo_root: Path, target_dir: Path, force: bool) -> None:
    """Handle copying of environment sample file."""
    sample_file = repo_root / ENV_SAMPLE_FILE
    target_file = target_dir / ENV_SAMPLE_FILE

    if not sample_file.exists():
        console.print(f"[yellow]Warning: Environment sample not found: {sample_file}[/yellow]")
        return

    if force:
        console.print("Copying environment variables example...")
        copy_sample = True
    else:
        copy_sample = Confirm.ask("Copy environment variables example?", default=True)

    if copy_sample:
        try:
            shutil.copy2(sample_file, target_file)
            console.print(f"[green]✓ Copied: {ENV_SAMPLE_FILE}[/green]")
            console.print("[cyan]  Edit this file and set your API keys.[/cyan]")
        except Exception as e:
            console.print(f"[red]✗ Failed to copy environment example: {e}[/red]")
    else:
        console.print("[yellow]Skipped environment example[/yellow]")
        console.print("[cyan]You can copy .env.hooks.example manually later.[/cyan]")


@click.command()
@click.argument('target_dir', type=click.Path())
@click.option('--force', '-f', is_flag=True, help='Skip confirmation prompts')
def main(target_dir: str, force: bool) -> None:
    """
    Create symlinks from the cape repository to TARGET_DIR.

    This script creates symbolic links for agents, hooks, commands, and AI documentation
    from the cape repository to your target directory.

    Examples:

        uv run scripts/create-symlinks.py ~/my-project

        uv run scripts/create-symlinks.py /path/to/target --force
    """
    # Get and validate repository root
    repo_root = get_repo_root()
    validate_repository(repo_root)

    # Expand and validate target directory
    target_path = expand_and_resolve_path(target_dir)
    validate_target_directory(target_path)

    # Display paths
    console.print(f"Repository: {repo_root}")
    console.print(f"Target: {target_path}")
    console.print("=" * 30)
    console.print()

    # Process all symlink mappings
    total_all = 0
    success_all = 0
    hooks_created = False

    for mapping in SYMLINK_CONFIG:
        total, success = process_mapping(repo_root, target_path, mapping)
        total_all += total
        success_all += success

        # Track if hooks were created
        if mapping.source_dir == "hooks/claude-code" and success > 0:
            hooks_created = True

    # Summary
    console.print()
    console.print("=" * 30)
    console.print("Symlink creation complete!")

    if success_all == total_all and total_all > 0:
        console.print(f"[green]Success: {success_all}/{total_all} operations[/green]")
    elif total_all > 0:
        console.print(f"[yellow]Partial success: {success_all}/{total_all} operations[/yellow]")
    else:
        console.print("[green]No operations needed.[/green]")

    # Handle environment sample if hooks were created
    if hooks_created:
        console.print()
        console.print("[cyan]📋 Note: Claude Code hooks require API keys in environment variables.[/cyan]")
        handle_env_sample(repo_root, target_path, force)


if __name__ == "__main__":
    main()
