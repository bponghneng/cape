"""
Workflow state file management.

This module provides workflow state management with atomic JSON writes
and Pydantic validation.
"""

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional

from pydantic import ValidationError

from cape_cli.models import WorkflowState
from cape_cli.paths import CapePaths


class StateManager:
    """Manage workflow state files."""

    @staticmethod
    def _get_state_file_path(workflow_id: str) -> Path:
        """Get the path to a state file for a given workflow ID."""
        return CapePaths.get_state_dir() / f"{workflow_id}.json"

    @staticmethod
    def write_state(state: WorkflowState) -> None:
        """
        Write state file atomically using temp file + rename.

        Args:
            state: WorkflowState object to write

        Raises:
            OSError: If file write fails
            ValidationError: If state validation fails
        """
        # Ensure directory exists
        CapePaths.ensure_directories()

        state_file = StateManager._get_state_file_path(state.workflow_id)

        # Serialize to JSON with datetime handling
        state_dict = state.model_dump()
        # Convert datetime objects to ISO 8601 strings
        for key, value in state_dict.items():
            if isinstance(value, datetime):
                state_dict[key] = value.isoformat()

        # Write to temp file first, then atomically rename
        fd, temp_path = tempfile.mkstemp(
            dir=state_file.parent, prefix=".tmp_", suffix=".json"
        )
        try:
            with os.fdopen(fd, "w") as f:
                json.dump(state_dict, f, indent=2)
            # Atomic rename
            os.replace(temp_path, state_file)
        except Exception:
            # Clean up temp file on error
            try:
                os.unlink(temp_path)
            except OSError:
                pass
            raise

    @staticmethod
    def read_state(workflow_id: str) -> Optional[WorkflowState]:
        """
        Read state from file with JSON parsing and Pydantic validation.

        Args:
            workflow_id: Unique workflow identifier

        Returns:
            WorkflowState object if file exists and is valid, None otherwise
        """
        state_file = StateManager._get_state_file_path(workflow_id)

        try:
            content = state_file.read_text()
            state_dict = json.loads(content)

            # Parse datetime strings back to datetime objects
            for key in ["started_at", "updated_at"]:
                if key in state_dict and isinstance(state_dict[key], str):
                    state_dict[key] = datetime.fromisoformat(state_dict[key])

            return WorkflowState(**state_dict)
        except (FileNotFoundError, json.JSONDecodeError, ValidationError, OSError):
            return None

    @staticmethod
    def update_state(workflow_id: str, **updates) -> Optional[WorkflowState]:
        """
        Update state file with partial updates.

        Args:
            workflow_id: Unique workflow identifier
            **updates: Fields to update

        Returns:
            Updated WorkflowState object if successful, None otherwise
        """
        # Read existing state
        state = StateManager.read_state(workflow_id)
        if state is None:
            return None

        # Update fields
        state_dict = state.model_dump()
        state_dict.update(updates)
        # Always update the updated_at timestamp
        state_dict["updated_at"] = datetime.now()

        # Validate and write
        try:
            updated_state = WorkflowState(**state_dict)
            StateManager.write_state(updated_state)
            return updated_state
        except ValidationError:
            return None

    @staticmethod
    def delete_state(workflow_id: str) -> None:
        """
        Delete state file safely.

        Args:
            workflow_id: Unique workflow identifier
        """
        state_file = StateManager._get_state_file_path(workflow_id)

        try:
            state_file.unlink()
        except FileNotFoundError:
            # Already deleted, not an error
            pass
