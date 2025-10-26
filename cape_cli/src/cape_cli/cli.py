"""Cape CLI - TUI-first workflow management CLI."""

import sys
import typer
from datetime import datetime
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

from cape_cli import __version__
from cape_cli.database import create_issue, fetch_issue
from cape_cli.utils import make_adw_id, setup_logger
from cape_cli.workflow import execute_workflow
from cape_cli.workflow_launcher import WorkflowLauncher
from cape_cli.workflow_monitor import WorkflowMonitor
from cape_cli.pid_manager import PIDFileManager

# Load environment variables
load_dotenv()

app = typer.Typer(
    invoke_without_command=True,
    no_args_is_help=False,
    help="Cape CLI - TUI-first workflow management"
)


def version_callback(value: bool):
    """Print version and exit."""
    if value:
        typer.echo(f"Cape CLI version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit"
    )
):
    """Main entry point. Launches TUI if no subcommand provided."""
    if ctx.invoked_subcommand is None:
        # Import TUI here to avoid import errors if textual isn't installed
        try:
            from cape_cli.tui import CapeApp
            tui_app = CapeApp()
            tui_app.run()
        except ImportError as e:
            typer.echo(f"Error: TUI dependencies not available: {e}", err=True)
            typer.echo("Please install with: uv pip install cape-cli", err=True)
            raise typer.Exit(1)
        except Exception as e:
            typer.echo(f"Error launching TUI: {e}", err=True)
            raise typer.Exit(1)


@app.command()
def create(description: str):
    """Create a new issue from description string.

    Args:
        description: The issue description text

    Example:
        cape create "Fix login authentication bug"
    """
    try:
        # Create issue in database
        issue = create_issue(description)
        typer.echo(f"{issue.id}")  # Output only the ID for scripting
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def create_from_file(file_path: Path):
    """Create a new issue from description file.

    Args:
        file_path: Path to file containing issue description

    Example:
        cape create-from-file issue-description.txt
    """
    try:
        # Validate file exists
        if not file_path.exists():
            typer.echo(f"Error: File not found: {file_path}", err=True)
            raise typer.Exit(1)

        # Validate it's a file, not a directory
        if not file_path.is_file():
            typer.echo(f"Error: Path is not a file: {file_path}", err=True)
            raise typer.Exit(1)

        # Read file content
        description = file_path.read_text(encoding="utf-8").strip()

        if not description:
            typer.echo("Error: File is empty", err=True)
            raise typer.Exit(1)

        # Create issue in database
        issue = create_issue(description)
        typer.echo(f"{issue.id}")  # Output only the ID for scripting

    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
    except UnicodeDecodeError:
        typer.echo(f"Error: File is not valid UTF-8: {file_path}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def run(
    issue_id: int,
    adw_id: Optional[str] = typer.Option(None, help="Workflow ID (auto-generated if not provided)")
):
    """Execute the adw_plan_build workflow for an issue.

    Args:
        issue_id: The Cape issue ID to process
        adw_id: Optional workflow ID for tracking (auto-generated if not provided)

    Example:
        cape run 123
        cape run 123 --adw-id abc12345
    """
    # Generate ADW ID if not provided
    if not adw_id:
        adw_id = make_adw_id()

    # Set up logger
    logger = setup_logger(adw_id, "adw_plan_build")

    # Execute workflow
    success = execute_workflow(issue_id, adw_id, logger)

    if not success:
        raise typer.Exit(1)


# Workflow management commands
workflow_app = typer.Typer(help="Manage background workflows")
app.add_typer(workflow_app, name="workflow")


@workflow_app.command("start")
def workflow_start(issue_id: int):
    """Launch a workflow in the background.

    Args:
        issue_id: Issue ID to process

    Example:
        cape workflow start 123
    """
    try:
        # Fetch issue to validate it exists
        issue = fetch_issue(issue_id)
        typer.echo(f"Launching workflow for issue {issue_id}: {issue.description[:60]}...")

        # Generate workflow ID
        adw_id = make_adw_id()

        # Launch workflow
        WorkflowLauncher.launch_workflow(issue_id, adw_id)

        typer.echo(f"✓ Workflow started: {adw_id}")
        typer.echo(f"  Monitor with: cape workflow status {adw_id}")
        typer.echo(f"  View logs with: cape workflow logs {adw_id}")

    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        raise typer.Exit(1)


@workflow_app.command("list")
def workflow_list():
    """List all active workflows.

    Example:
        cape workflow list
    """
    try:
        workflows = WorkflowMonitor.list_active_workflows()

        if not workflows:
            typer.echo("No active workflows")
            return

        typer.echo(f"\n{len(workflows)} active workflow(s):\n")

        # Print header
        typer.echo(f"{'ID':<10} {'ISSUE':<8} {'STATUS':<12} {'STEP':<12} {'ELAPSED':<12}")
        typer.echo("-" * 64)

        # Print workflows
        for state in workflows:
            elapsed = str(datetime.now() - state.started_at).split('.')[0]
            step = state.current_step or "-"
            typer.echo(
                f"{state.workflow_id:<10} {state.issue_id:<8} "
                f"{state.status:<12} {step:<12} {elapsed:<12}"
            )

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@workflow_app.command("status")
def workflow_status(workflow_id: str):
    """Show detailed workflow status.

    Args:
        workflow_id: Workflow ID

    Example:
        cape workflow status abc12345
    """
    try:
        state = WorkflowMonitor.get_workflow_status(workflow_id, use_cache=False)

        if not state:
            typer.echo(f"Error: Workflow not found: {workflow_id}", err=True)
            raise typer.Exit(1)

        # Print status
        typer.echo(f"\nWorkflow: {state.workflow_id}")
        typer.echo(f"Issue ID: {state.issue_id}")
        typer.echo(f"Status:   {state.status}")
        typer.echo(f"PID:      {state.pid}")

        if state.current_step:
            typer.echo(f"Step:     {state.current_step}")

        elapsed = str(datetime.now() - state.started_at).split('.')[0]
        typer.echo(f"Started:  {state.started_at.strftime('%Y-%m-%d %H:%M:%S')}")
        typer.echo(f"Elapsed:  {elapsed}")

        if state.error_message:
            typer.echo(f"\nError:    {state.error_message}")

        typer.echo()

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@workflow_app.command("stop")
def workflow_stop(workflow_id: str):
    """Stop a running workflow.

    Args:
        workflow_id: Workflow ID

    Example:
        cape workflow stop abc12345
    """
    try:
        # Check if workflow exists
        state = WorkflowMonitor.get_workflow_status(workflow_id)
        if not state:
            typer.echo(f"Error: Workflow not found: {workflow_id}", err=True)
            raise typer.Exit(1)

        # Check if already stopped
        if state.status in ["completed", "failed", "stopped"]:
            typer.echo(f"Workflow {workflow_id} is already {state.status}")
            return

        typer.echo(f"Stopping workflow {workflow_id}...")

        # Stop workflow
        success = WorkflowLauncher.stop_workflow(workflow_id, timeout=30)

        if success:
            typer.echo(f"✓ Workflow stopped")
        else:
            typer.echo(f"Warning: Failed to stop workflow cleanly", err=True)

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@workflow_app.command("logs")
def workflow_logs(workflow_id: str, lines: int = typer.Option(50, help="Number of lines to show")):
    """Show workflow logs.

    Args:
        workflow_id: Workflow ID
        lines: Number of lines to show (default: 50)

    Example:
        cape workflow logs abc12345
        cape workflow logs abc12345 --lines 100
    """
    try:
        log_lines = WorkflowMonitor.get_workflow_logs(workflow_id, lines=lines)

        if log_lines is None:
            typer.echo(f"Error: Log file not found for workflow: {workflow_id}", err=True)
            raise typer.Exit(1)

        if not log_lines:
            typer.echo("(empty log file)")
            return

        # Print logs
        for line in log_lines:
            typer.echo(line.rstrip())

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@workflow_app.command("cleanup")
def workflow_cleanup():
    """Clean up stale PIDs and old workflow state files.

    Example:
        cape workflow cleanup
    """
    try:
        typer.echo("Cleaning up stale workflows...")

        # Clean up stale PIDs
        stale = PIDFileManager.cleanup_stale_pids()
        if stale:
            typer.echo(f"✓ Removed {len(stale)} stale PID file(s)")

        # Recover orphaned workflows
        orphaned = PIDFileManager.recover_orphaned_workflows()
        if orphaned:
            typer.echo(f"✓ Recovered {len(orphaned)} orphaned workflow(s)")

        # Clean up old completed workflows (>24 hours)
        old = PIDFileManager.cleanup_completed_workflows(max_age_hours=24)
        if old:
            typer.echo(f"✓ Cleaned up {len(old)} old workflow(s)")

        if not stale and not orphaned and not old:
            typer.echo("No cleanup needed")

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
