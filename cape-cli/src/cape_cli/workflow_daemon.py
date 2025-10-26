"""
Workflow daemon entry point for detached background execution.

This module serves as the standalone entry point for workflow execution as a
detached background process.
"""

import signal
import sys
from datetime import datetime

from cape_cli.pid_manager import PIDFileManager
from cape_cli.state_manager import StateManager
from cape_cli.utils import setup_logger, log_workflow_event
from cape_cli.workflow import execute_workflow


# Global flag for graceful shutdown
shutdown_requested = False


def handle_shutdown_signal(signum, frame):
    """Handle shutdown signals (SIGTERM, SIGINT).

    Sets global shutdown flag and updates state to stopped.
    """
    global shutdown_requested
    shutdown_requested = True


def main(issue_id: int, adw_id: str) -> int:
    """
    Main entry point for workflow daemon.

    Args:
        issue_id: Issue ID to process
        adw_id: Workflow ID

    Returns:
        Exit code: 0 for success, 1 for failure, 130 for SIGTERM
    """
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGTERM, handle_shutdown_signal)
    signal.signal(signal.SIGINT, handle_shutdown_signal)

    # Set up detached logging (no console output)
    logger = setup_logger(
        adw_id,
        trigger_type="adw_plan_build",
        detached_mode=True,
        use_rotating=True
    )

    try:
        # Update state to running
        log_workflow_event(logger, "workflow", "started", f"Issue ID: {issue_id}")
        StateManager.update_state(adw_id, status="running")

        # Check for shutdown before starting
        if shutdown_requested:
            log_workflow_event(logger, "workflow", "stopped", "Shutdown requested before execution")
            StateManager.update_state(adw_id, status="stopped")
            PIDFileManager.delete_pid(adw_id)
            return 130

        # Execute workflow
        success = execute_workflow(issue_id, adw_id, logger)

        # Check for shutdown after execution
        if shutdown_requested:
            log_workflow_event(logger, "workflow", "stopped", "Shutdown requested")
            StateManager.update_state(adw_id, status="stopped")
            PIDFileManager.delete_pid(adw_id)
            return 130

        # Update state based on result
        if success:
            log_workflow_event(logger, "workflow", "completed", "All steps completed successfully")
            StateManager.update_state(adw_id, status="completed")
            # Try to update issue status
            try:
                from cape_cli.database import update_issue_status
                update_issue_status(issue_id, "completed")
            except Exception as e:
                logger.debug(f"Failed to update issue status: {e}")
        else:
            log_workflow_event(logger, "workflow", "failed", "Workflow execution failed")
            StateManager.update_state(
                adw_id,
                status="failed",
                error_message="Workflow execution failed"
            )

        # Clean up PID file
        PIDFileManager.delete_pid(adw_id)

        return 0 if success else 1

    except Exception as e:
        # Handle unexpected errors
        error_msg = f"Unexpected error: {e}"
        log_workflow_event(logger, "workflow", "failed", error_msg)
        logger.exception("Workflow daemon crashed")

        # Update state to failed
        try:
            StateManager.update_state(
                adw_id,
                status="failed",
                error_message=str(e)
            )
        except Exception:
            pass  # Best effort

        # Clean up PID file
        try:
            PIDFileManager.delete_pid(adw_id)
        except Exception:
            pass  # Best effort

        return 1


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python -m cape_cli.workflow_daemon <issue_id> <adw_id>", file=sys.stderr)
        sys.exit(2)

    try:
        issue_id_arg = int(sys.argv[1])
        adw_id_arg = sys.argv[2]
    except (ValueError, IndexError):
        print("Error: Invalid arguments", file=sys.stderr)
        print("Usage: python -m cape_cli.workflow_daemon <issue_id> <adw_id>", file=sys.stderr)
        sys.exit(2)

    exit_code = main(issue_id_arg, adw_id_arg)
    sys.exit(exit_code)
