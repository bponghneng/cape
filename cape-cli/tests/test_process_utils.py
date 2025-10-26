"""Unit tests for process utilities."""

import os
import signal
import subprocess
import time
from unittest.mock import Mock, patch

import pytest

from cape_cli.process_utils import (
    get_process_info,
    is_process_alive,
    send_signal,
    terminate_process,
)


class TestProcessUtils:
    """Test process utility functions."""

    def test_is_process_alive_current_process(self):
        """Test checking if current process is alive."""
        assert is_process_alive(os.getpid()) is True

    def test_is_process_alive_invalid_pid(self):
        """Test checking invalid PIDs."""
        assert is_process_alive(0) is False
        assert is_process_alive(-1) is False

    def test_is_process_alive_nonexistent(self):
        """Test checking nonexistent process."""
        assert is_process_alive(999999999) is False

    def test_send_signal_to_invalid_pid(self):
        """Test sending signal to invalid PID."""
        assert send_signal(0, signal.SIGTERM) is False
        assert send_signal(-1, signal.SIGTERM) is False

    def test_send_signal_to_nonexistent_process(self):
        """Test sending signal to nonexistent process."""
        assert send_signal(999999999, signal.SIGTERM) is False

    def test_send_signal_success(self):
        """Test sending signal to real process."""
        # Start a subprocess that will ignore signals
        proc = subprocess.Popen(
            ["python", "-c", "import time; time.sleep(10)"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            # Should successfully send signal
            assert send_signal(proc.pid, signal.SIGTERM) is True
        finally:
            # Clean up
            try:
                proc.kill()
                proc.wait(timeout=1)
            except:
                pass

    def test_terminate_process_nonexistent(self):
        """Test terminating nonexistent process."""
        # Should return True (already not alive)
        assert terminate_process(999999999) is True

    def test_terminate_process_graceful(self):
        """Test graceful process termination."""
        # Start a subprocess
        proc = subprocess.Popen(
            ["sleep", "10"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        try:
            pid = proc.pid
            # Verify process is alive
            assert is_process_alive(pid) is True

            # Terminate it
            result = terminate_process(pid, timeout=5)

            # Wait for process to be reaped
            try:
                proc.wait(timeout=1)
            except subprocess.TimeoutExpired:
                pass

            # Process should no longer be alive
            assert is_process_alive(pid) is False
        finally:
            # Ensure cleanup
            try:
                proc.kill()
                proc.wait(timeout=1)
            except:
                pass

    def test_terminate_process_with_sigkill(self):
        """Test process termination escalates to SIGKILL."""
        # Create a script that ignores SIGTERM
        script = """
import signal
import time

def ignore_sigterm(signum, frame):
    pass

signal.signal(signal.SIGTERM, ignore_sigterm)

# Sleep forever
while True:
    time.sleep(1)
"""
        proc = subprocess.Popen(
            ["python", "-c", script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        try:
            pid = proc.pid
            # Verify process is alive
            assert is_process_alive(pid) is True

            # Terminate with very short timeout so it escalates to SIGKILL
            result = terminate_process(pid, timeout=1)

            # Wait for process to be reaped
            try:
                proc.wait(timeout=1)
            except subprocess.TimeoutExpired:
                pass

            # Process should be killed
            assert is_process_alive(pid) is False
        finally:
            # Ensure cleanup
            try:
                proc.kill()
                proc.wait(timeout=1)
            except:
                pass

    @patch("cape_cli.process_utils.HAS_PSUTIL", True)
    @patch("cape_cli.process_utils.psutil")
    def test_is_process_alive_with_psutil(self, mock_psutil):
        """Test is_process_alive uses psutil when available."""
        # Mock process as running
        mock_process = Mock()
        mock_process.is_running.return_value = True
        mock_psutil.Process.return_value = mock_process

        assert is_process_alive(12345) is True
        mock_psutil.Process.assert_called_once_with(12345)

    @patch("cape_cli.process_utils.HAS_PSUTIL", True)
    @patch("cape_cli.process_utils.psutil")
    def test_is_process_alive_psutil_no_such_process(self, mock_psutil):
        """Test is_process_alive handles NoSuchProcess from psutil."""
        # Create a real exception instance
        import psutil

        mock_psutil.NoSuchProcess = psutil.NoSuchProcess
        mock_psutil.AccessDenied = psutil.AccessDenied
        mock_psutil.Process.side_effect = psutil.NoSuchProcess(12345)

        assert is_process_alive(12345) is False

    @patch("cape_cli.process_utils.HAS_PSUTIL", True)
    @patch("cape_cli.process_utils.psutil")
    def test_get_process_info_success(self, mock_psutil):
        """Test get_process_info with psutil."""
        # Mock process info
        mock_process = Mock()
        mock_process.cmdline.return_value = ["python", "test.py"]
        mock_process.status.return_value = "running"
        mock_process.create_time.return_value = 1234567890.0
        mock_psutil.Process.return_value = mock_process

        info = get_process_info(12345)

        assert info is not None
        assert info["pid"] == 12345
        assert info["cmdline"] == ["python", "test.py"]
        assert info["status"] == "running"
        assert info["create_time"] == 1234567890.0

    @patch("cape_cli.process_utils.HAS_PSUTIL", True)
    @patch("cape_cli.process_utils.psutil")
    def test_get_process_info_no_such_process(self, mock_psutil):
        """Test get_process_info handles NoSuchProcess."""
        # Create a real exception instance
        import psutil

        mock_psutil.NoSuchProcess = psutil.NoSuchProcess
        mock_psutil.AccessDenied = psutil.AccessDenied
        mock_psutil.Process.side_effect = psutil.NoSuchProcess(12345)

        info = get_process_info(12345)
        assert info is None

    @patch("cape_cli.process_utils.HAS_PSUTIL", False)
    def test_get_process_info_without_psutil(self):
        """Test get_process_info returns None without psutil."""
        info = get_process_info(12345)
        assert info is None

    def test_terminate_process_invalid_pid(self):
        """Test terminate_process with invalid PID."""
        assert terminate_process(0) is True  # Already not alive
        assert terminate_process(-1) is True  # Already not alive
