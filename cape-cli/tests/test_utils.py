"""Tests for utility functions."""

import logging
import os
import tempfile
from pathlib import Path
from cape_cli.utils import make_adw_id, setup_logger, get_logger


def test_make_adw_id():
    """Test ADW ID generation."""
    adw_id = make_adw_id()
    assert len(adw_id) == 8
    assert isinstance(adw_id, str)


def test_make_adw_id_unique():
    """Test that ADW IDs are unique."""
    id1 = make_adw_id()
    id2 = make_adw_id()
    assert id1 != id2


def test_setup_logger(tmp_path, monkeypatch):
    """Test logger setup with temp directory."""
    # Use temp directory for agents
    monkeypatch.setenv("CAPE_AGENTS_DIR", str(tmp_path))

    adw_id = "test1234"
    logger = setup_logger(adw_id, "test_trigger")

    assert logger.name == f"cape_{adw_id}"
    assert logger.level == logging.DEBUG

    # Check log directory was created
    expected_dir = tmp_path / adw_id / "test_trigger"
    assert expected_dir.exists()

    # Check log file was created
    log_file = expected_dir / "execution.log"
    assert log_file.exists()

    # Check handlers
    assert len(logger.handlers) == 2

    # Clean up
    logger.handlers.clear()


def test_setup_logger_file_handler(tmp_path, monkeypatch):
    """Test logger file handler writes correctly."""
    monkeypatch.setenv("CAPE_AGENTS_DIR", str(tmp_path))

    adw_id = "test5678"
    logger = setup_logger(adw_id)
    logger.debug("Debug message")
    logger.info("Info message")

    log_file = tmp_path / adw_id / "adw_plan_build" / "execution.log"
    content = log_file.read_text()

    assert "Debug message" in content
    assert "Info message" in content

    # Clean up
    logger.handlers.clear()


def test_get_logger():
    """Test getting existing logger."""
    adw_id = "test9999"
    logger = logging.getLogger(f"cape_{adw_id}")
    retrieved = get_logger(adw_id)
    assert retrieved is logger
