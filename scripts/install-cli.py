#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "typer",
#     "rich",
# ]
# ///

"""
install-cli.py

Copies the cape-cli and hooks directories from the cape repository to a target directory.

This script copies the entire cape-cli and hooks directories to a target directory.

Creates parent directories automatically. Use --force to overwrite existing files.
"""

import os
import sys
import shutil
from pathlib import Path
from typing import NamedTuple
from dataclasses import dataclass

import typer
from rich.console import Console

console = Console()

# Constants
ENV_SAMPLE_FILE = ".env.hooks.example"
REQUIRED_DIRS = ["cape-cli", "hooks", "scripts"]


@dataclass
class CopyMapping:
    """Configuration for copy mappings."""

    source_dir: str
    target_base: str
    pattern: str
    label: str
    recursive: bool = False


# Configurable copy mappings
COPY_CONFIG = [
    CopyMapping("cape-cli", "cape-cli", "*", "CLI", recursive=True),
    CopyMapping("hooks/claude-code", ".claude/hooks", "*", "Hooks", recursive=True),
]


@dataclass
class CopyOperation:
    """Represents a single copy operation to be performed."""

    source_path: Path
    target_path: Path
    description: str


class OperationResult(NamedTuple):
    """Result of a copy operation."""

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
        console.print(
            f"[red]Error: Parent directory of target does not exist: {parent}[/red]"
        )
        sys.exit(1)

    if not os.access(parent, os.W_OK):
        console.print(
            f"[red]Error: No write permission to create target directory: {parent}[/red]"
        )
        sys.exit(1)


def find_files(source_path: Path, pattern: str, recursive: bool) -> list[Path]:
    """Find files matching pattern in source directory."""
    if not source_path.exists():
        return []

    if recursive:
        # For recursive, use rglob to get only files (not directories)
        # This ensures we create directory structure as regular dirs and copy only files
        items = []
        for item in source_path.rglob(pattern):
            # Skip items in hidden directories (starting with .)
            # Only include files, not directories
            if item.is_file() and not any(
                part.startswith(".")
                for part in item.relative_to(source_path).parts[:-1]
            ):
                items.append(item)
        return items
    else:
        # For non-recursive, use glob to get only files (matches *.md pattern usage)
        return [f for f in source_path.glob(pattern) if f.is_file()]


def copy_file(
    repo_root: Path,
    target_dir: Path,
    source_rel: str,
    target_rel: str,
    description: str,
    force: bool = False,
) -> OperationResult:
    """
    Copy a single file, optionally overwriting existing files.
    """
    source_path = repo_root / source_rel
    target_path = target_dir / target_rel

    # Verify source exists
    if not source_path.exists():
        return OperationResult(False, f"Source missing: {source_path}")

    # Create parent directory
    target_path.parent.mkdir(parents=True, exist_ok=True)

    # Check if target exists and not forcing overwrite
    if target_path.exists() and not force:
        return OperationResult(False, f"Target exists, skipping: {target_path}")

    # Copy file
    try:
        shutil.copy2(source_path, target_path)
        return OperationResult(True, description)
    except OSError as e:
        return OperationResult(False, f"{description} failed: {e}")


def process_mapping(
    repo_root: Path, target_dir: Path, mapping: CopyMapping, force: bool = False
) -> list[OperationResult]:
    """
    Process a copy mapping configuration.
    """
    source_path = repo_root / mapping.source_dir
    target_base_dir = target_dir / mapping.target_base
    target_base_dir.mkdir(parents=True, exist_ok=True)

    if not source_path.exists():
        console.print(
            f"[yellow]Warning: {mapping.label} directory not found: {source_path}[/yellow]"
        )
        return []

    console.print(f"Processing {mapping.label}...")

    # Find files matching pattern
    files = find_files(source_path, mapping.pattern, mapping.recursive)

    results = []

    for file_path in files:
        # Calculate relative path from source_path to maintain directory structure
        relative_path = file_path.relative_to(source_path)
        source_rel = str(Path(mapping.source_dir) / relative_path)
        target_rel = str(Path(mapping.target_base) / relative_path)
        description = f"{mapping.label}: {relative_path}"

        result = copy_file(
            repo_root, target_dir, source_rel, target_rel, description, force
        )
        results.append(result)

        if result.success:
            console.print(f"[green]✓ {result.message}[/green]")
        else:
            console.print(f"[yellow]Warning: {result.message}[/yellow]")

    return results


def handle_env_sample(repo_root: Path, target_dir: Path, with_envs: bool) -> None:
    """Handle copying of environment sample file."""
    sample_file = repo_root / ENV_SAMPLE_FILE
    target_file = target_dir / ENV_SAMPLE_FILE

    if not sample_file.exists():
        console.print(
            f"[yellow]Warning: Environment sample not found: {sample_file}[/yellow]"
        )
        return

    if with_envs:
        console.print("Copying environment variables example...")
        copy_sample = True
    else:
        copy_sample = typer.confirm("Copy environment variables example?", default=True)

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


def main(
    target_dir: str = typer.Argument(help="Target directory to copy files to"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files"),
    with_envs: bool = typer.Option(
        False, "--with-envs", help="Automatically copy environment variables example"
    ),
) -> None:
    """
    Copy files from the cape repository to TARGET_DIR.

    This script copies the entire cape-cli and hooks directories from the cape repository to your target directory.

    Examples:

        uv run scripts/install-cli.py ~/my-project

        uv run scripts/install-cli.py /path/to/target --force

        uv run scripts/install-cli.py /path/to/target --with-envs
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

    # Process all copy mappings
    all_results = []
    hooks_created = False

    for mapping in COPY_CONFIG:
        results = process_mapping(repo_root, target_path, mapping, force)
        all_results.extend(results)

    # Check if hooks were created
    for result in all_results:
        if result.success and "Hooks:" in result.message:
            hooks_created = True
            break

    # Summary
    total_all = len(all_results)
    success_all = sum(1 for r in all_results if r.success)

    console.print()
    console.print("=" * 30)
    console.print("File copying complete!")

    if success_all == total_all and total_all > 0:
        console.print(f"[green]Success: {success_all}/{total_all} operations[/green]")
    elif total_all > 0:
        console.print(
            f"[yellow]Partial success: {success_all}/{total_all} operations[/yellow]"
        )
    else:
        console.print("[green]No operations needed.[/green]")

    # Handle environment sample if hooks were created
    if hooks_created:
        console.print()
        console.print(
            "[cyan]📋 Note: Claude Code hooks require API keys in environment variables.[/cyan]"
        )
        handle_env_sample(repo_root, target_path, with_envs)


if __name__ == "__main__":
    typer.run(main)
