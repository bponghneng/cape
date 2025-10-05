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
import platform
import subprocess
import ctypes
import json
import tempfile
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


@dataclass
class SymlinkOperation:
    """Represents a single symlink operation to be performed."""
    source_path: Path
    target_path: Path
    description: str


class OperationResult(NamedTuple):
    """Result of a symlink operation."""
    success: bool
    message: str


def is_windows() -> bool:
    """Check if running on Windows platform."""
    return platform.system() == "Windows"


def is_admin() -> bool:
    """Check if running with administrator privileges on Windows."""
    if not is_windows():
        return False
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def needs_elevation() -> bool:
    """Check if elevation is needed for symlink creation."""
    return is_windows() and not is_admin()


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
    """Find files matching pattern in source directory."""
    if not source_path.exists():
        return []

    if recursive:
        # For recursive, use rglob to get only files (not directories)
        # This ensures we create directory structure as regular dirs and symlink only files
        items = []
        for item in source_path.rglob(pattern):
            # Skip items in hidden directories (starting with .)
            # Only include files, not directories
            if item.is_file() and not any(part.startswith('.') for part in item.relative_to(source_path).parts[:-1]):
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
    description: str,
    collect_for_batch: bool = False
) -> SymlinkOperation | OperationResult:
    """
    Create a single symlink or collect it for batch execution.

    If collect_for_batch is True, returns SymlinkOperation for later batch execution.
    Otherwise, executes immediately and returns OperationResult.
    """
    source_path = repo_root / source_rel
    target_path = target_dir / target_rel

    # Verify source exists
    if not source_path.exists():
        return OperationResult(False, f"Source missing: {source_path}")

    # If collecting for batch, return the operation
    if collect_for_batch:
        return SymlinkOperation(
            source_path=source_path,
            target_path=target_path,
            description=description
        )

    # Execute immediately
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


def execute_symlink_batch_elevated(operations: list[SymlinkOperation], force: bool) -> list[OperationResult]:
    """
    Execute a batch of symlink operations with elevated privileges on Windows.

    Creates a temporary Python script that performs all operations, elevates it,
    and parses the results.
    """
    if not operations:
        return []

    # Generate Python script content
    script_lines = [
        "#!/usr/bin/env python3",
        "import sys",
        "import json",
        "from pathlib import Path",
        "",
        "results = []",
        ""
    ]

    for op in operations:
        # Escape paths for Python string literals
        source_str = str(op.source_path).replace('\\', '\\\\').replace('"', '\\"')
        target_str = str(op.target_path).replace('\\', '\\\\').replace('"', '\\"')
        desc_str = op.description.replace('\\', '\\\\').replace('"', '\\"')

        script_lines.extend([
            f'# {op.description}',
            'try:',
            f'    source_path = Path(r"{source_str}")',
            f'    target_path = Path(r"{target_str}")',
            f'    description = "{desc_str}"',
            '',
            '    # Create parent directory',
            '    target_path.parent.mkdir(parents=True, exist_ok=True)',
            '',
            '    # Handle existing target',
            '    if target_path.exists() or target_path.is_symlink():',
            '        if target_path.is_symlink():',
            '            target_path.unlink()',
            '        elif target_path.is_dir():',
            '            results.append({"success": False, "message": f"Target directory exists, skipping: {target_path}"})',
            '            raise Exception("Directory exists")',
            '        else:',
            '            results.append({"success": False, "message": f"Target file exists, skipping: {target_path}"})',
            '            raise Exception("File exists")',
            '',
            '    # Create symlink',
            '    target_path.symlink_to(source_path, target_is_directory=source_path.is_dir())',
            '    results.append({"success": True, "message": description})',
            'except Exception as e:',
            '    if not any(r.get("message", "").startswith(description) for r in results):',
            '        results.append({"success": False, "message": f"{description} failed: {e}"})',
            ''
        ])

    script_lines.extend([
        '# Output results as JSON',
        'print(json.dumps(results))',
        'sys.exit(0)'
    ])

    script_content = '\n'.join(script_lines)

    # Create temporary script file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        temp_script = f.name
        f.write(script_content)

    try:
        # Prompt for elevation if not in force mode
        if not force:
            console.print(f"\n[yellow]About to request elevation to create {len(operations)} symlinks.[/yellow]")
            choice = input("Proceed with elevation? (y/N): ").strip().lower()
            if choice not in ['y', 'yes']:
                console.print("[yellow]Operation cancelled.[/yellow]")
                return [OperationResult(False, "Operation cancelled by user") for _ in operations]

        console.print(f"[yellow]Requesting elevation to create {len(operations)} symlinks...[/yellow]")

        # Use PowerShell to elevate and capture output
        ps_command = f'Start-Process -FilePath "{sys.executable}" -ArgumentList "{temp_script}" -Verb RunAs -Wait -WindowStyle Hidden'

        # Create output capture script
        output_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8')
        output_path = output_file.name
        output_file.close()

        # Modify the script to redirect output
        with open(temp_script, 'r', encoding='utf-8') as f:
            original_content = f.read()

        modified_content = original_content.replace(
            'print(json.dumps(results))',
            f'with open(r"{output_path}", "w", encoding="utf-8") as f: f.write(json.dumps(results))'
        )

        with open(temp_script, 'w', encoding='utf-8') as f:
            f.write(modified_content)

        # Execute elevated script
        result = subprocess.run(
            ['powershell', '-Command', ps_command],
            capture_output=True,
            text=True,
            timeout=60
        )

        # Read results from output file
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                results_data = json.loads(f.read())

            return [OperationResult(r['success'], r['message']) for r in results_data]
        except (FileNotFoundError, json.JSONDecodeError) as e:
            console.print(f"[red]Failed to read results from elevated script: {e}[/red]")
            return [OperationResult(False, f"{op.description} - elevation failed") for op in operations]
        finally:
            # Clean up output file
            try:
                os.unlink(output_path)
            except Exception:
                pass

    except subprocess.TimeoutExpired:
        console.print("[red]Elevation request timed out[/red]")
        return [OperationResult(False, f"{op.description} - timeout") for op in operations]
    except Exception as e:
        console.print(f"[red]Batch execution failed: {e}[/red]")
        return [OperationResult(False, f"{op.description} - execution failed") for op in operations]
    finally:
        # Clean up temporary script
        try:
            os.unlink(temp_script)
        except Exception:
            pass


def execute_symlink_direct(operation: SymlinkOperation) -> OperationResult:
    """
    Execute a symlink operation directly (for non-Windows or already elevated).
    """
    target_path = operation.target_path
    source_path = operation.source_path

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
        return OperationResult(True, operation.description)
    except OSError as e:
        return OperationResult(False, f"{operation.description} failed: {e}")


def process_mapping(
    repo_root: Path,
    target_dir: Path,
    mapping: SymlinkMapping,
    collect_for_batch: bool = False
) -> tuple[list[SymlinkOperation], list[OperationResult]]:
    """
    Process a symlink mapping configuration.

    Returns (operations, results) tuple where:
    - operations: List of SymlinkOperation objects to be batched (if collect_for_batch=True)
    - results: List of OperationResult objects from immediate execution (if collect_for_batch=False)
    """
    source_path = repo_root / mapping.source_dir

    if not source_path.exists():
        console.print(f"[yellow]Warning: {mapping.label} directory not found: {source_path}[/yellow]")
        return ([], [])

    if not collect_for_batch:
        console.print(f"Processing {mapping.label}...")

    # Find files matching pattern
    files = find_files(source_path, mapping.pattern, mapping.recursive)

    operations = []
    results = []

    for file_path in files:
        # Calculate relative path from source_path to maintain directory structure
        relative_path = file_path.relative_to(source_path)
        source_rel = str(Path(mapping.source_dir) / relative_path)
        target_rel = str(Path(mapping.target_base) / relative_path)
        description = f"{mapping.label}: {relative_path}"

        result = create_symlink(repo_root, target_dir, source_rel, target_rel, description, collect_for_batch)

        if isinstance(result, SymlinkOperation):
            operations.append(result)
        else:
            # It's an OperationResult
            results.append(result)
            if not collect_for_batch:
                if result.success:
                    console.print(f"[green]✓ {result.message}[/green]")
                else:
                    console.print(f"[yellow]Warning: {result.message}[/yellow]")

    return (operations, results)


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

    # Determine if we need batch elevation
    should_batch = needs_elevation()

    # Process all symlink mappings
    all_operations = []
    all_results = []
    hooks_created = False

    if should_batch:
        console.print("[cyan]Collecting symlink operations...[/cyan]")
        console.print()

    for mapping in SYMLINK_CONFIG:
        operations, results = process_mapping(repo_root, target_path, mapping, collect_for_batch=should_batch)
        all_operations.extend(operations)
        all_results.extend(results)

    # Execute batch operations if needed
    if should_batch and all_operations:
        console.print()
        console.print(f"[cyan]Found {len(all_operations)} symlinks to create.[/cyan]")
        batch_results = execute_symlink_batch_elevated(all_operations, force)
        all_results.extend(batch_results)

        # Display batch results
        console.print()
        for result in batch_results:
            if result.success:
                console.print(f"[green]✓ {result.message}[/green]")
            else:
                console.print(f"[yellow]Warning: {result.message}[/yellow]")

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
