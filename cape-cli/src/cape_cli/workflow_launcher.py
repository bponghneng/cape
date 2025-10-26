"""
Workflow launcher for detached background processes.

This module launches workflows as independent background processes that are
detached from the TUI lifecycle.
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from cape_cli.models import WorkflowState
from cape_cli.paths import CapePaths
from cape_cli.pid_manager import PIDFileManager
from cape_cli.process_utils import terminate_process
from cape_cli.state_manager import StateManager


class WorkflowLauncher:
    """Launch and manage workflow processes."""

    @staticmethod
    def launch_workflow(issue_id: int, adw_id: str) -> str:
        """
        Launch a workflow as a detached background process.

        Args:
            issue_id: Issue ID to work on
            adw_id: Workflow ID (ADW identifier)

        Returns:
            Workflow ID

        Raises:
            RuntimeError: If workflow launch fails
        """
        # Ensure directories exist
        CapePaths.ensure_directories()

        # Build command to run workflow daemon
        cmd = [
            sys.executable,  # Use current Python interpreter
            "-m",
            "cape_cli.workflow_daemon",
            str(issue_id),
            adw_id
        ]

        try:
            # Launch process with full detachment
            process = subprocess.Popen(
                cmd,
                start_new_session=True,  # Detach from current session
                stdout=subprocess.DEVNULL,  # Redirect stdout to null
                stderr=subprocess.DEVNULL,  # Redirect stderr to null
                close_fds=True,  # Close file descriptors
            )

            # Write PID file
            PIDFileManager.write_pid(adw_id, process.pid)

            # Create initial state file
            initial_state = WorkflowState(
                workflow_id=adw_id,
                issue_id=issue_id,
                status="initializing",
                pid=process.pid,
                started_at=datetime.now(),
                updated_at=datetime.now(),
            )
            StateManager.write_state(initial_state)

            # Try to update issue status in Supabase (best-effort)
            try:
                from cape_cli.database import update_issue_status
                update_issue_status(issue_id, "started")
            except Exception:
                # Ignore Supabase errors - they're not critical for workflow launch
                pass

            return adw_id

        except Exception as e:
            raise RuntimeError(f"Failed to launch workflow: {e}") from e

    @staticmethod
    def stop_workflow(workflow_id: str, timeout: int = 30) -> bool:
        """
        Stop a running workflow gracefully.

        Args:
            workflow_id: Workflow ID to stop
            timeout: Seconds to wait for graceful shutdown before SIGKILL

        Returns:
            True if workflow was stopped, False otherwise
        """
        # Read PID from file
        pid = PIDFileManager.read_pid(workflow_id)
        if pid is None:
            return False

        # Update state to stopping
        StateManager.update_state(workflow_id, status="stopped")

        # Terminate process (SIGTERM → wait → SIGKILL)
        success = terminate_process(pid, timeout=timeout)

        # Clean up PID file
        PIDFileManager.delete_pid(workflow_id)

        # Try to update issue status in Supabase (best-effort)
        try:
            state = StateManager.read_state(workflow_id)
            if state:
                from cape_cli.database import update_issue_status
                update_issue_status(state.issue_id, "pending")
        except Exception:
            # Ignore Supabase errors
            pass

        return success

    @staticmethod
    def get_workflow_pid(workflow_id: str) -> Optional[int]:
        """
        Get the PID for a running workflow.

        Args:
            workflow_id: Workflow ID

        Returns:
            Process ID if workflow is running, None otherwise
        """
        pid = PIDFileManager.read_pid(workflow_id)
        if pid and PIDFileManager.is_process_running(pid):
            return pid
        return None
