# Spec: Add OpenCode Coding Agent for Implement Plan

## Goal

Add an OpenCode-based coding agent under `cape/app/src/cape/core/agents` and wire the `adw_plan_build` workflow so that only `implement_plan` uses OpenCode, while classification/plan steps remain on Claude Code. The implementation step is controlled via `CAPE_IMPLEMENT_PROVIDER` and calls the OpenCode CLI with `.opencode/command/implement.md`.

## Requirements

- New `OpenCode` provider in `cape/app/src/cape/core/agents/opencode/`.
- Only `/implement` is supported initially.
- Classification, plan building, and plan file discovery stay on Claude templates.
- `CAPE_IMPLEMENT_PROVIDER` selects the provider for the implementation step; other steps are unchanged.
- Implement CLI signature:
  - `opencode --model zai-coding-plan/glm-4.6 --command implement --format json "<message text>"`
- `--command` must be `implement` (no slash).
- Message text is the plan content only (no `/implement` prefix); `.opencode/command/implement.md` uses it as `$ARGUMENTS`.
- JSONL logging/structure should match the Claude provider.

## Key Files

- `cape/app/src/cape/core/workflow.py`
  - `implement_plan` currently calls `execute_template` with the Claude implementor agent.
- `cape/app/src/cape/core/agent.py`
  - Facade for `execute_template` / provider-based execution.
- `cape/app/src/cape/core/agents/base.py`
  - `AgentPromptRequest`, `AgentPromptResponse`, `AgentProvider` interface.
- `cape/app/src/cape/core/agents/registry.py`
  - Provider registration and resolution.
- `cape/app/src/cape/core/agents/claude_code/*`
  - Reference for CLI, JSONL, env, and error handling.
- `.opencode/command/implement.md`
  - Implement prompt template; expects plan as `$ARGUMENTS`.

## Design

### 1. OpenCode Provider

- Create package:
  - `cape/app/src/cape/core/agents/opencode/__init__.py`
  - `cape/app/src/cape/core/agents/opencode/provider.py`
- In `provider.py`:
  - Implement `OpenCodeAgentProvider(AgentProvider)` with `execute_prompt(self, request: AgentPromptRequest) -> AgentPromptResponse`.
  - Add `check_opencode_installed()` that runs `opencode --help` or `--version` and returns `None` or an error string.

### 2. CLI + JSONL

- Reuse/mirror Claude JSONL helpers:
  - Same log dir under `CAPE_AGENTS_DIR`.
  - Stream stdout to `*.jsonl` while the process runs.
  - Parse JSONL into messages and build `AgentPromptResponse(success, output, debug_info)`.

- Implement mapping for `/implement` only:
  - Expect `request.slash_command == "/implement"` and `request.args[0]` as the plan file path.
  - Read plan file contents; use that text as the CLI message.
  - Build command:
    - `opencode --model zai-coding-plan/glm-4.6 --command implement --format json "<plan contents>"`.

- Env setup (similar to Claude):
  - Include `PATH`, `HOME`, `USER`, `SHELL`, `TERM`, `CAPE_AGENTS_DIR`.
  - Forward `GITHUB_PAT` / `GH_TOKEN` if present.
  - Support `OPENCODE_API_KEY`, optional `OPENCODE_PATH` for binary override.

- Execution:
  - Run via `subprocess.Popen`.
  - On non-zero exit, return `AgentPromptResponse` with `success=False` and error details from stderr/JSONL.
  - On success, parse JSONL and choose the final assistant message as `output` (fallback to last message/raw log when needed).

### 3. Registry and `CAPE_IMPLEMENT_PROVIDER`

- In `registry.py`:
  - Register `OpenCodeAgentProvider` under name `"opencode"`.
  - Keep `"claude-code"` as the default provider.
- Add `get_implement_provider()`:
  - Read `CAPE_IMPLEMENT_PROVIDER`.
  - If set and a provider exists with that name, return it; otherwise return the default provider from `get_agent_provider()`.
- Export `get_implement_provider` from `cape/core/agents/__init__.py`.

### 4. `execute_implement_plan` Helper

- In `cape/app/src/cape/core/agent.py` add:

  - `execute_implement_plan(plan_file: str, issue_id: int, adw_id: str) -> AgentPromptResponse`:
    - Build `AgentPromptRequest` with `slash_command="/implement"`, `args=[plan_file]`, `adw_id`, `issue_id`, and a logging-only `model`.
    - Resolve provider via `get_implement_provider()` and call `execute_prompt`.
    - Return `AgentPromptResponse`.

### 5. Workflow Wiring

- In `workflow.py`:
  - Import `execute_implement_plan`.
  - Change `implement_plan` to call `execute_implement_plan(plan_file, issue_id, adw_id)` instead of building an `AgentTemplateRequest` + `execute_template`.
  - Keep `classify_issue`, `build_plan`, and `get_plan_file` unchanged (still Claude templates).

### 6. Tests + Docs

- New tests in `cape/app/tests/core/agents/opencode/test_provider.py`:
  - Installation check.
  - Command construction for `/implement` (uses plan contents; correct model/flags).
  - JSONL parsing and error handling.

- Workflow tests in `cape/app/tests/core/test_workflow.py`:
  - Confirm classification/plan steps still use `execute_template`.
  - With `CAPE_IMPLEMENT_PROVIDER="opencode"`, ensure `implement_plan` uses the OpenCode provider via `execute_implement_plan`.

- Docs (`AGENTS.md`):
  - Describe `opencode` provider, required env vars, `CAPE_IMPLEMENT_PROVIDER` semantics, and that only `implement` is wired for now with model `zai-coding-plan/glm-4.6`.

## Future

- Later, generalize OpenCode to more commands by mapping additional slash commands to `--command` values and adjusting message text/model selection.
