"""Tests for Claude Code agent module."""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from cape_cli.agent import (
    check_claude_installed,
    parse_jsonl_output,
    convert_jsonl_to_json,
    get_claude_env,
    save_prompt,
    prompt_claude_code,
    execute_template,
)
from cape_cli.models import AgentPromptRequest, AgentTemplateRequest


def test_check_claude_installed_success():
    """Test checking for Claude Code CLI success."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = Mock(returncode=0)
        result = check_claude_installed()
        assert result is None


def test_check_claude_installed_not_found():
    """Test checking for Claude Code CLI failure."""
    with patch("subprocess.run", side_effect=FileNotFoundError):
        result = check_claude_installed()
        assert result is not None
        assert "not installed" in result


def test_parse_jsonl_output(tmp_path):
    """Test parsing JSONL output file."""
    jsonl_file = tmp_path / "test.jsonl"
    messages = [
        {"type": "message", "data": "test1"},
        {"type": "result", "is_error": False, "result": "success"},
    ]
    with open(jsonl_file, "w") as f:
        for msg in messages:
            f.write(json.dumps(msg) + "\n")

    all_messages, result_message = parse_jsonl_output(str(jsonl_file))
    assert len(all_messages) == 2
    assert result_message["type"] == "result"
    assert result_message["result"] == "success"


def test_convert_jsonl_to_json(tmp_path):
    """Test converting JSONL to JSON array."""
    jsonl_file = tmp_path / "test.jsonl"
    messages = [
        {"type": "message", "data": "test1"},
        {"type": "result", "result": "success"},
    ]
    with open(jsonl_file, "w") as f:
        for msg in messages:
            f.write(json.dumps(msg) + "\n")

    json_file = convert_jsonl_to_json(str(jsonl_file))
    assert Path(json_file).exists()
    with open(json_file) as f:
        data = json.load(f)
        assert len(data) == 2


def test_get_claude_env(monkeypatch):
    """Test getting Claude Code environment variables."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test_key")
    monkeypatch.setenv("HOME", "/home/test")
    monkeypatch.setenv("PATH", "/usr/bin")

    env = get_claude_env()
    assert "ANTHROPIC_API_KEY" in env
    assert "HOME" in env
    assert "PATH" in env


def test_get_claude_env_with_github_pat(monkeypatch):
    """Test environment includes GitHub tokens when GITHUB_PAT is set."""
    monkeypatch.setenv("GITHUB_PAT", "test_pat")
    monkeypatch.setenv("HOME", "/home/test")

    env = get_claude_env()
    assert env.get("GITHUB_PAT") == "test_pat"
    assert env.get("GH_TOKEN") == "test_pat"


def test_save_prompt(tmp_path, monkeypatch):
    """Test saving prompt to file."""
    monkeypatch.setenv("CAPE_AGENTS_DIR", str(tmp_path))

    save_prompt("/implement plan.md", "test123", "ops")

    expected_file = tmp_path / "test123" / "ops" / "prompts" / "implement.txt"
    assert expected_file.exists()
    assert expected_file.read_text() == "/implement plan.md"


@patch("cape_cli.agent.check_claude_installed")
@patch("subprocess.run")
def test_prompt_claude_code_success(mock_run, mock_check, tmp_path, monkeypatch):
    """Test successful Claude Code execution."""
    monkeypatch.setenv("CAPE_AGENTS_DIR", str(tmp_path))
    mock_check.return_value = None

    output_file = tmp_path / "output.jsonl"
    request = AgentPromptRequest(
        prompt="/implement plan.md",
        adw_id="test123",
        output_file=str(output_file),
    )

    # Mock successful execution
    mock_run.return_value = Mock(returncode=0, stderr="")

    # Create mock JSONL output
    result_msg = {
        "type": "result",
        "is_error": False,
        "result": "Implementation complete",
        "session_id": "session123",
    }
    with open(output_file, "w") as f:
        f.write(json.dumps(result_msg) + "\n")

    response = prompt_claude_code(request)
    assert response.success is True
    assert response.session_id == "session123"


@patch("cape_cli.agent.check_claude_installed")
def test_prompt_claude_code_cli_not_installed(mock_check):
    """Test handling of Claude Code CLI not installed."""
    mock_check.return_value = "Error: Claude Code CLI is not installed"

    request = AgentPromptRequest(
        prompt="/implement plan.md",
        adw_id="test123",
        output_file="/tmp/output.jsonl",
    )

    response = prompt_claude_code(request)
    assert response.success is False
    assert "not installed" in response.output


@patch("cape_cli.agent.prompt_claude_code")
def test_execute_template(mock_prompt, tmp_path, monkeypatch):
    """Test executing template with slash command."""
    monkeypatch.setenv("CAPE_AGENTS_DIR", str(tmp_path))
    mock_prompt.return_value = Mock(output="Success", success=True, session_id="test")

    request = AgentTemplateRequest(
        agent_name="ops",
        slash_command="/implement",
        args=["plan.md"],
        adw_id="test123",
    )

    response = execute_template(request)
    assert response.success is True
    mock_prompt.assert_called_once()
