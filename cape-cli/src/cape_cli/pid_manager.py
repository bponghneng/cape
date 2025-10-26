"""
PID file management for workflow processes.

This module provides robust PID file management with stale PID detection
and cleanup capabilities.
"""

import os
import tempfile
from pathlib import Path
from typing import List, Optional

from cape_cli.paths import CapePaths


class PIDFileManager:
    """Manage PID files for workflow processes."""

    @staticmethod
    def _get_pid_file_path(workflow_id: str) -> Path:
        """Get the path to a PID file for a given workflow ID."""
        return CapePaths.get_runtime_dir() / f"{workflow_id}.pid"

    @staticmethod
    def write_pid(workflow_id: str, pid: int) -> None:
        """
        Write a PID file atomically using temp file + rename.

        Args:
            workflow_id: Unique workflow identifier
            pid: Process ID to write

        Raises:
            OSError: If file write fails
        """
        # Ensure directory exists
        CapePaths.ensure_directories()

        pid_file = PIDFileManager._get_pid_file_path(workflow_id)

        # Write to temp file first, then atomically rename
        fd, temp_path = tempfile.mkstemp(
            dir=pid_file.parent, prefix=".tmp_", suffix=".pid"
        )
        try:
            with os.fdopen(fd, "w") as f:
                f.write(str(pid))
            # Atomic rename
            os.replace(temp_path, pid_file)
        except Exception:
            # Clean up temp file on error
            try:
                os.unlink(temp_path)
            except OSError:
                pass
            raise

    @staticmethod
    def read_pid(workflow_id: str) -> Optional[int]:
        """
        Read PID from file.

        Args:
            workflow_id: Unique workflow identifier

        Returns:
            Process ID if file exists and is valid, None otherwise
        """
        pid_file = PIDFileManager._get_pid_file_path(workflow_id)

        try:
            content = pid_file.read_text().strip()
            return int(content)
        except (FileNotFoundError, ValueError, OSError):
            return None

    @staticmethod
    def delete_pid(workflow_id: str) -> None:
        """
        Delete PID file safely.

        Args:
            workflow_id: Unique workflow identifier
        """
        pid_file = PIDFileManager._get_pid_file_path(workflow_id)

        try:
            pid_file.unlink()
        except FileNotFoundError:
            # Already deleted, not an error
            pass

    @staticmethod
    def is_process_running(pid: int) -> bool:
        """
        Check if a process is running using os.kill signal check.

        Args:
            pid: Process ID to check

        Returns:
            True if process is running, False otherwise
        """
        if pid <= 0:
            return False

        try:
            # Signal 0 doesn't kill the process, just checks if it exists
            os.kill(pid, 0)
            return True
        except ProcessLookupError:
            # Process doesn't exist
            return False
        except PermissionError:
            # Process exists but we don't have permission to signal it
            # We'll consider this as "running" since it exists
            return True
        except OSError:
            # Other errors - assume not running
            return False

    @staticmethod
    def cleanup_stale_pids() -> List[str]:
        """
        Remove PID files for processes that are no longer running.

        Returns:
            List of workflow IDs that were cleaned up
        """
        CapePaths.ensure_directories()
        pid_dir = CapePaths.get_runtime_dir()

        cleaned_workflows = []

        for pid_file in pid_dir.glob("*.pid"):
            workflow_id = pid_file.stem

            pid = PIDFileManager.read_pid(workflow_id)
            if pid is None or not PIDFileManager.is_process_running(pid):
                # Stale PID file
                PIDFileManager.delete_pid(workflow_id)
                cleaned_workflows.append(workflow_id)

        return cleaned_workflows

    @staticmethod
    def list_active_workflows() -> List[tuple[str, int]]:
        """
        List all active workflows.

        Returns:
            List of (workflow_id, pid) tuples for running workflows
        """
        CapePaths.ensure_directories()
        pid_dir = CapePaths.get_runtime_dir()

        active_workflows = []

        for pid_file in pid_dir.glob("*.pid"):
            workflow_id = pid_file.stem

            pid = PIDFileManager.read_pid(workflow_id)
            if pid is not None and PIDFileManager.is_process_running(pid):
                active_workflows.append((workflow_id, pid))

        return active_workflows

    @staticmethod
    def discover_workflows() -> List[tuple[str, int, Optional[object]]]:
        """
        Discover all workflows with PID files and load their states.

        Scans PID directory for all .pid files, checks if processes are running,
        and loads corresponding state files.

        Returns:
            List of (workflow_id, pid, state) tuples where state is WorkflowState
            object or None if state file doesn't exist or is corrupted
        """
        from cape_cli.state_manager import StateManager

        CapePaths.ensure_directories()
        pid_dir = CapePaths.get_runtime_dir()

        workflows = []

        for pid_file in pid_dir.glob("*.pid"):
            workflow_id = pid_file.stem

            pid = PIDFileManager.read_pid(workflow_id)
            if pid is not None and PIDFileManager.is_process_running(pid):
                # Load state file
                state = StateManager.read_state(workflow_id)
                workflows.append((workflow_id, pid, state))

        return workflows

    @staticmethod
    def recover_orphaned_workflows() -> List[str]:
        """
        Find state files without corresponding PID files and mark as failed.

        This handles the case where a workflow process crashed without
        cleaning up its state file.

        Returns:
            List of workflow IDs that were recovered
        """
        from cape_cli.state_manager import StateManager

        CapePaths.ensure_directories()
        state_dir = CapePaths.get_state_dir()
        pid_dir = CapePaths.get_runtime_dir()

        recovered_workflows = []

        for state_file in state_dir.glob("*.json"):
            workflow_id = state_file.stem

            # Check if PID file exists
            pid_file = pid_dir / f"{workflow_id}.pid"
            if not pid_file.exists():
                # No PID file - this is an orphaned workflow
                state = StateManager.read_state(workflow_id)
                if state and state.status in ["initializing", "running"]:
                    # Mark as failed
                    StateManager.update_state(
                        workflow_id,
                        status="failed",
                        error_message="Process terminated unexpectedly (orphaned state)"
                    )
                    recovered_workflows.append(workflow_id)

        return recovered_workflows

    @staticmethod
    def cleanup_completed_workflows(max_age_hours: int = 24) -> List[str]:
        """
        Remove PID and state files for completed/failed workflows older than threshold.

        Args:
            max_age_hours: Maximum age in hours for completed workflows

        Returns:
            List of workflow IDs that were cleaned up
        """
        from datetime import datetime, timedelta
        from cape_cli.state_manager import StateManager

        CapePaths.ensure_directories()
        state_dir = CapePaths.get_state_dir()

        cleaned_workflows = []
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)

        for state_file in state_dir.glob("*.json"):
            workflow_id = state_file.stem

            # Read state
            state = StateManager.read_state(workflow_id)
            if not state:
                continue

            # Check if workflow is completed/failed and old enough
            if state.status in ["completed", "failed", "stopped"]:
                if state.updated_at < cutoff_time:
                    # Clean up PID file (if it exists)
                    PIDFileManager.delete_pid(workflow_id)
                    # Clean up state file
                    StateManager.delete_state(workflow_id)
                    cleaned_workflows.append(workflow_id)

        return cleaned_workflows
