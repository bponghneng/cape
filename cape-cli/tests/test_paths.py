"""Unit tests for paths module."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from cape_cli.paths import CapePaths


class TestCapePaths:
    """Test CapePaths class."""

    def test_get_base_dir_default(self):
        """Test default base directory."""
        with patch.dict(os.environ, {}, clear=True):
            base_dir = CapePaths.get_base_dir()
            assert base_dir == Path.home() / ".cape"

    def test_get_base_dir_with_env_var(self):
        """Test base directory with CAPE_DATA_DIR environment variable."""
        with patch.dict(os.environ, {"CAPE_DATA_DIR": "/tmp/custom_cape"}):
            base_dir = CapePaths.get_base_dir()
            assert base_dir == Path("/tmp/custom_cape")

    def test_get_runtime_dir_default(self):
        """Test default runtime directory."""
        with patch.dict(os.environ, {}, clear=True):
            runtime_dir = CapePaths.get_runtime_dir()
            assert runtime_dir == Path.home() / ".cape" / "pids"

    def test_get_runtime_dir_with_env_var(self):
        """Test runtime directory with CAPE_RUNTIME_DIR environment variable."""
        with patch.dict(os.environ, {"CAPE_RUNTIME_DIR": "/tmp/custom_runtime"}):
            runtime_dir = CapePaths.get_runtime_dir()
            assert runtime_dir == Path("/tmp/custom_runtime")

    def test_get_state_dir(self):
        """Test state directory."""
        with patch.dict(os.environ, {}, clear=True):
            state_dir = CapePaths.get_state_dir()
            assert state_dir == Path.home() / ".cape" / "state"

    def test_get_state_dir_with_env_var(self):
        """Test state directory with CAPE_DATA_DIR environment variable."""
        with patch.dict(os.environ, {"CAPE_DATA_DIR": "/tmp/custom_cape"}):
            state_dir = CapePaths.get_state_dir()
            assert state_dir == Path("/tmp/custom_cape") / "state"

    def test_get_logs_dir(self):
        """Test logs directory."""
        with patch.dict(os.environ, {}, clear=True):
            logs_dir = CapePaths.get_logs_dir()
            assert logs_dir == Path.home() / ".cape" / "logs"

    def test_get_logs_dir_with_env_var(self):
        """Test logs directory with CAPE_DATA_DIR environment variable."""
        with patch.dict(os.environ, {"CAPE_DATA_DIR": "/tmp/custom_cape"}):
            logs_dir = CapePaths.get_logs_dir()
            assert logs_dir == Path("/tmp/custom_cape") / "logs"

    def test_ensure_directories(self, tmp_path):
        """Test directory creation with ensure_directories."""
        with patch.dict(os.environ, {"CAPE_DATA_DIR": str(tmp_path)}):
            CapePaths.ensure_directories()

            # Check that all directories were created
            assert (tmp_path / "pids").exists()
            assert (tmp_path / "state").exists()
            assert (tmp_path / "logs").exists()

            # Check that directories are accessible
            assert (tmp_path / "pids").is_dir()
            assert (tmp_path / "state").is_dir()
            assert (tmp_path / "logs").is_dir()

    def test_ensure_directories_idempotent(self, tmp_path):
        """Test that ensure_directories can be called multiple times safely."""
        with patch.dict(os.environ, {"CAPE_DATA_DIR": str(tmp_path)}):
            # Call twice - should not raise exception
            CapePaths.ensure_directories()
            CapePaths.ensure_directories()

            # Directories should still exist
            assert (tmp_path / "pids").exists()
            assert (tmp_path / "state").exists()
            assert (tmp_path / "logs").exists()

    def test_ensure_directories_with_custom_runtime_dir(self, tmp_path):
        """Test directory creation with custom runtime directory."""
        data_dir = tmp_path / "data"
        runtime_dir = tmp_path / "runtime"

        with patch.dict(
            os.environ,
            {"CAPE_DATA_DIR": str(data_dir), "CAPE_RUNTIME_DIR": str(runtime_dir)},
        ):
            CapePaths.ensure_directories()

            # Runtime dir should be in custom location
            assert runtime_dir.exists()
            # State and logs should be under data dir
            assert (data_dir / "state").exists()
            assert (data_dir / "logs").exists()
