"""
Workflow monitoring and status queries.

This module provides functionality to query workflow status, list active workflows,
tail logs, and wait for workflow completion.
"""

import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from cape_cli.models import WorkflowState
from cape_cli.pid_manager import PIDFileManager
from cape_cli.state_manager import StateManager
from cape_cli.paths import CapePaths


class WorkflowMonitor:
    """Monitor and query workflow status."""

    # Cache for workflow states with TTL
    _cache: dict[str, tuple[WorkflowState, datetime]] = {}
    _cache_ttl = timedelta(seconds=5)

    @classmethod
    def get_workflow_status(
        cls, workflow_id: str, use_cache: bool = True
    ) -> Optional[WorkflowState]:
        """
        Get workflow status from state file.

        Args:
            workflow_id: Workflow ID to query
            use_cache: Whether to use cached state (default: True)

        Returns:
            WorkflowState object if available, None otherwise
        """
        # Check cache first
        if use_cache and workflow_id in cls._cache:
            cached_state, cache_time = cls._cache[workflow_id]
            if datetime.now() - cache_time < cls._cache_ttl:
                return cached_state

        # Read from file
        state = StateManager.read_state(workflow_id)

        # Update cache
        if state:
            cls._cache[workflow_id] = (state, datetime.now())

        return state

    @classmethod
    def list_active_workflows(cls) -> List[WorkflowState]:
        """
        List all active workflows.

        Returns:
            List of WorkflowState objects for running workflows
        """
        workflows = []

        # Get all active workflows with PIDs
        active = PIDFileManager.list_active_workflows()

        for workflow_id, pid in active:
            state = cls.get_workflow_status(workflow_id, use_cache=False)
            if state:
                workflows.append(state)

        return workflows

    @classmethod
    def get_workflow_logs(
        cls, workflow_id: str, lines: int = 50
    ) -> Optional[List[str]]:
        """
        Get recent log lines for a workflow.

        Args:
            workflow_id: Workflow ID
            lines: Number of lines to retrieve from end of log file

        Returns:
            List of log lines, or None if log file doesn't exist
        """
        # Find log file in agents directory
        agents_dir = os.environ.get("CAPE_AGENTS_DIR", os.path.join(os.getcwd(), "agents"))
        log_file = Path(agents_dir) / workflow_id / "adw_plan_build" / "execution.log"

        if not log_file.exists():
            return None

        try:
            with open(log_file, 'r') as f:
                # Read all lines and return last N
                all_lines = f.readlines()
                return all_lines[-lines:] if len(all_lines) > lines else all_lines
        except (IOError, OSError):
            return None

    @classmethod
    def wait_for_completion(
        cls,
        workflow_id: str,
        timeout: Optional[int] = None,
        poll_interval: int = 1
    ) -> Optional[WorkflowState]:
        """
        Wait for workflow to complete.

        Polls state file until status is terminal (completed/failed/stopped).

        Args:
            workflow_id: Workflow ID to wait for
            timeout: Maximum seconds to wait (None for no timeout)
            poll_interval: Seconds between polls

        Returns:
            Final WorkflowState if workflow completed, None if timeout occurred
        """
        start_time = time.time()

        while True:
            # Get current state (bypass cache)
            state = cls.get_workflow_status(workflow_id, use_cache=False)

            # Check if workflow is in terminal state
            if state and state.status in ["completed", "failed", "stopped"]:
                return state

            # Check timeout
            if timeout is not None:
                elapsed = time.time() - start_time
                if elapsed >= timeout:
                    return None

            # Wait before next poll
            time.sleep(poll_interval)

    @classmethod
    def clear_cache(cls) -> None:
        """Clear the workflow state cache."""
        cls._cache.clear()

    @classmethod
    def is_workflow_running(cls, workflow_id: str) -> bool:
        """
        Check if a workflow is currently running.

        Args:
            workflow_id: Workflow ID to check

        Returns:
            True if workflow is running, False otherwise
        """
        # Check PID file
        pid = PIDFileManager.read_pid(workflow_id)
        if not pid or not PIDFileManager.is_process_running(pid):
            return False

        # Check state
        state = cls.get_workflow_status(workflow_id, use_cache=False)
        if not state:
            return False

        return state.status in ["initializing", "running"]

    @classmethod
    def get_workflow_progress(cls, workflow_id: str) -> Optional[dict]:
        """
        Get workflow progress information.

        Args:
            workflow_id: Workflow ID

        Returns:
            Dict with progress info (status, current_step, elapsed_time), or None
        """
        state = cls.get_workflow_status(workflow_id, use_cache=False)
        if not state:
            return None

        # Calculate elapsed time
        elapsed = datetime.now() - state.started_at

        return {
            "workflow_id": workflow_id,
            "status": state.status,
            "current_step": state.current_step,
            "elapsed_seconds": int(elapsed.total_seconds()),
            "elapsed_str": str(elapsed).split('.')[0],  # HH:MM:SS format
            "error_message": state.error_message,
        }
