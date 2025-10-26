"""
CAPE directory structure management.

This module provides centralized path management for runtime directories
following the XDG Base Directory specification.
"""

import os
from pathlib import Path


class CapePaths:
    """Manage CAPE directory structure following XDG Base Directory specification."""

    @staticmethod
    def get_base_dir() -> Path:
        """Get base CAPE directory."""
        base = os.getenv("CAPE_DATA_DIR")
        if base:
            return Path(base)
        return Path.home() / ".cape"

    @staticmethod
    def get_runtime_dir() -> Path:
        """Get runtime directory for PID files."""
        base = os.getenv("CAPE_RUNTIME_DIR")
        if base:
            return Path(base)
        return CapePaths.get_base_dir() / "pids"

    @staticmethod
    def get_state_dir() -> Path:
        """Get state directory for workflow state files."""
        return CapePaths.get_base_dir() / "state"

    @staticmethod
    def get_logs_dir() -> Path:
        """Get logs directory for workflow logs."""
        return CapePaths.get_base_dir() / "logs"

    @staticmethod
    def ensure_directories() -> None:
        """
        Ensure all required directories exist with proper permissions.

        Creates directories atomically with 0755 permissions.
        """
        directories = [
            CapePaths.get_runtime_dir(),
            CapePaths.get_state_dir(),
            CapePaths.get_logs_dir(),
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True, mode=0o755)
