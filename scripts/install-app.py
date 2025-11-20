#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "typer",
#     "rich",
# ]
# ///

"""
install-app.py

Copies the cape/app package into a `cape/` subdirectory inside a target directory.
If the destination already exists, it can be deleted before copying.
"""

import os
import shutil
import stat
from pathlib import Path

import typer
from rich.console import Console

console = Console()
APP_DIR_NAME = "app"
INSTALL_DIR_NAME = "cape-cli"
EXCLUDED_APP_DIRS = {".cape", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".venv"}


def get_repo_root() -> Path:
    """Return the cape repository root (parent of scripts directory)."""
    script_path = Path(__file__).resolve()
    return script_path.parent.parent


def expand_and_resolve_path(path_str: str) -> Path:
    """Expand ~ and resolve a path relative to CWD if needed."""
    path = Path(path_str).expanduser()
    if path.is_absolute():
        return path.resolve()
    return Path.cwd().joinpath(path).resolve()


def validate_source(repo_root: Path) -> Path:
    """Ensure the source app directory exists."""
    source_path = repo_root / APP_DIR_NAME
    if not source_path.is_dir():
        console.print(
            f"[red]Error: Expected application directory at {source_path}[/red]"
        )
        raise typer.Exit(code=1)
    return source_path


def ensure_parent_writable(target_path: Path) -> None:
    """Make sure the destination parent exists and is writable."""
    parent = target_path.parent
    parent.mkdir(parents=True, exist_ok=True)
    if not os.access(parent, os.W_OK):
        console.print(
            f"[red]Error: No write permission for parent directory {parent}[/red]"
        )
        raise typer.Exit(code=1)


def remove_existing_target(target_path: Path, force: bool) -> None:
    """Delete the existing destination directory after confirmation."""
    if not target_path.exists():
        return

    if not target_path.is_dir():
        console.print(
            f"[red]Error: Target path {target_path} exists and is not a directory[/red]"
        )
        raise typer.Exit(code=1)

    if not force:
        proceed = typer.confirm(
            f"{target_path} already exists. Remove it before copying?",
            default=False,
        )
        if not proceed:
            console.print("[yellow]Copy cancelled by user.[/yellow]")
            raise typer.Exit(code=0)

    console.print(f"[yellow]Removing existing directory: {target_path}[/yellow]")

    def _on_rm_error(func, path, exc_info):
        # Clear read-only flag (Windows) then retry removal
        os.chmod(path, stat.S_IWRITE)
        func(path)

    shutil.rmtree(target_path, onerror=_on_rm_error)


def copy_app(source_path: Path, target_path: Path) -> None:
    """Copy the app directory into the destination."""
    console.print(f"[cyan]Copying {source_path} -> {target_path}[/cyan]")

    def _ignore_unwanted_dirs(src: str, names: list[str]) -> set[str]:
        """Skip transient directories that should not be part of installs."""
        ignored: set[str] = set()
        current = Path(src)
        for name in names:
            if name in EXCLUDED_APP_DIRS and (current / name).is_dir():
                ignored.add(name)
        return ignored

    shutil.copytree(source_path, target_path, ignore=_ignore_unwanted_dirs)
    console.print(f"[green]\u2713 Copied application to {target_path}[/green]")


def main(
    target_dir: str = typer.Argument(
        ..., help="Absolute or relative path for the copied app directory"
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Skip confirmations and overwrite destination"
    ),
) -> None:
    repo_root = get_repo_root()
    source_path = validate_source(repo_root)
    base_target = expand_and_resolve_path(target_dir)
    target_path = base_target / INSTALL_DIR_NAME

    console.print(f"Repository: {repo_root}")
    console.print(f"Source: {source_path}")
    console.print(f"Target directory: {base_target}")
    console.print(f"Destination: {target_path}")
    console.print("=" * 30)

    ensure_parent_writable(target_path)
    remove_existing_target(target_path, force)
    copy_app(source_path, target_path)


if __name__ == "__main__":
    typer.run(main)
