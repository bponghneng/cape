"""
Process management utilities.

This module provides utilities for process management including process
alive checks, signal sending, and graceful termination.
"""

import os
import signal
import time
from typing import Optional

try:
    import psutil

    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


def is_process_alive(pid: int) -> bool:
    """
    Check if a process is alive.

    Uses psutil if available, otherwise falls back to os.kill signal check.

    Args:
        pid: Process ID to check

    Returns:
        True if process is alive, False otherwise
    """
    if pid <= 0:
        return False

    if HAS_PSUTIL:
        try:
            process = psutil.Process(pid)
            return process.is_running()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False

    # Fallback to os.kill signal check
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        # Process exists but we don't have permission
        return True
    except OSError:
        return False


def send_signal(pid: int, sig: signal.Signals) -> bool:
    """
    Send a signal to a process with error handling.

    Args:
        pid: Process ID to send signal to
        sig: Signal to send

    Returns:
        True if signal was sent successfully, False otherwise
    """
    if pid <= 0:
        return False

    try:
        os.kill(pid, sig)
        return True
    except (ProcessLookupError, PermissionError, OSError):
        return False


def terminate_process(pid: int, timeout: int = 30) -> bool:
    """
    Gracefully terminate a process with SIGTERM → wait → SIGKILL escalation.

    Args:
        pid: Process ID to terminate
        timeout: Seconds to wait for graceful shutdown before SIGKILL

    Returns:
        True if process was terminated, False otherwise
    """
    if not is_process_alive(pid):
        return True

    # Send SIGTERM for graceful shutdown
    if not send_signal(pid, signal.SIGTERM):
        return False

    # Wait for process to exit
    start_time = time.time()
    while time.time() - start_time < timeout:
        if not is_process_alive(pid):
            return True
        time.sleep(0.1)

    # Process didn't exit gracefully, send SIGKILL
    if is_process_alive(pid):
        send_signal(pid, signal.SIGKILL)
        # Give it a moment to die
        time.sleep(0.5)

    return not is_process_alive(pid)


def get_process_info(pid: int) -> Optional[dict]:
    """
    Get process information (cmdline, status).

    Args:
        pid: Process ID to get info for

    Returns:
        Dict with process info if available, None otherwise
    """
    if not HAS_PSUTIL:
        return None

    try:
        process = psutil.Process(pid)
        return {
            "pid": pid,
            "cmdline": process.cmdline(),
            "status": process.status(),
            "create_time": process.create_time(),
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None
