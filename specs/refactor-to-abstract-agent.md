## Refactor to Abstract Agent Interface

Goal: generalize the agent interface beyond Claude Code, support multiple coding agents, and decouple progress comments from provider implementations while keeping streaming JSON output available for notifications.

---

## 1. Current Behavior and Constraints

- Agents are currently implemented in `cape/core/agent.py` and tightly coupled to the Claude CLI (`CLAUDE_CODE_PATH`, JSONL format, `TodoWrite` tools, specific models like `"sonnet"`/`"opus"`).
- Agent request/response models live in `cape/core/models.py` and are Claude-specific (`AgentPromptRequest`, `AgentPromptResponse`, `AgentTemplateRequest`, `ClaudeCodeResultMessage`).
- `agent.py` also emits progress comments directly via `insert_progress_comment`, mixing provider logic with notifications.

Constraints for the refactor:

- Preserve existing behavior for Claude-based workflows while introducing a provider-agnostic abstraction.
- Support multiple Claude-like CLIs via configuration/registry.
- Hard-deprecate Claude-specific models/functions from generic modules over time.

---

## 2. Provider-Agnostic Models and Interface

Create `cape/core/agents/base.py` with:

- `AgentExecuteRequest` (provider-agnostic):
	- `prompt: str` – full prompt/command.
	- `issue_id: int`, `adw_id: str`, `agent_name: str` – workflow metadata.
	- `model: Optional[str]` – provider-neutral model name.
	- `output_path: Optional[str]` – optional raw output destination.
	- `provider_options: Dict[str, Any]` – provider-specific configuration (flags, timeouts, env tweaks, etc.).

- `AgentExecuteResponse`:
	- `output: str` – main textual result.
	- `success: bool`.
	- `session_id: Optional[str]`.
	- `raw_output_path: Optional[str]`.
	- `error_detail: Optional[str]`.

- `CodingAgent` interface:
	- `execute_prompt(request: AgentExecuteRequest, *, stream_handler: Optional[Callable[[str], None]] = None) -> AgentExecuteResponse`.
	- `stream_handler` receives streaming chunks (e.g., JSONL lines) and is the only extension point for notifications.

Template execution remains a higher-level helper that builds prompts (e.g., from slash commands + args) and calls `execute_prompt`.

---

## 3. Move/Rename Claude-Specific Models

Create `cape/core/agents/claude_models.py` and move the current Claude-specific models from `cape/core/models.py`, renaming:

- `AgentPromptRequest` → `ClaudeAgentPromptRequest`.
- `AgentPromptResponse` → `ClaudeAgentPromptResponse`.
- `AgentTemplateRequest` → `ClaudeAgentTemplateRequest`.
- `ClaudeCodeResultMessage` → `ClaudeAgentResultMessage`.

Keep field definitions compatible (e.g., `model: Literal["sonnet", "opus"]`, `dangerously_skip_permissions`, `output_file`).

In `cape/core/models.py`:

- Remove the original class definitions.
- If necessary, add short-lived aliases that re-export from `claude_models` with clear deprecation notes.

Update all call sites to import from `cape.core.agents.claude_models` instead of `cape.core.models` when Claude-specific types are required.

---

## 4. Implement `ClaudeAgent` and Extract Claude Logic

Create `cape/core/agents/claude.py` containing Claude-specific behavior currently in `agent.py`:

- Env/CLI utilities: `CLAUDE_PATH`, `check_claude_installed`, `get_claude_env` (if still useful).
- JSONL helpers: `parse_jsonl_output`, `convert_jsonl_to_json`.
- Content parsing: `iter_assistant_items`.
- Prompt logging: `save_prompt`.
- Subprocess execution (command construction, stdout/stderr handling, timeouts).

Implement `ClaudeAgent(CodingAgent)`:

- Maps `AgentExecuteRequest` to `ClaudeAgentPromptRequest` (including `output_file` path).
- Runs the Claude CLI and writes JSONL output.
- Invokes `stream_handler(line)` for each stdout line if a handler is provided.
- Parses JSONL to fill `AgentExecuteResponse` (`output`, `success`, `session_id`, `raw_output_path`, `error_detail`).

Add a helper for templates that takes `ClaudeAgentTemplateRequest`, builds the slash-command prompt, and delegates to `ClaudeAgent.execute_prompt`.

---

## 5. Agent Registry/Factory

Create `cape/core/agents/registry.py` (or use `__init__.py`) to select implementations:

- Internal mapping: `Dict[str, CodingAgent]` or factories.
- `get_agent(provider: Optional[str] = None) -> CodingAgent`:
	- Uses explicit `provider` if passed.
	- Otherwise reads `CAPE_AGENT_PROVIDER` (or similar) with default `"claude"`.

Register at least:

- `"claude"` → default `ClaudeAgent` instance.

Support multiple Claude-like CLIs by registering additional providers (e.g., `"claude_alt"`) with differently configured `ClaudeAgent`s (different paths/flags via `provider_options`).

Call sites currently using `prompt_claude_code` / `execute_template` should:

- Obtain a `CodingAgent` via `get_agent`.
- Build `AgentExecuteRequest` and call `execute_prompt`, optionally passing a `stream_handler` (see Section 7).

---

## 6. Rescope `cape/core/agent.py`

Turn `cape/core/agent.py` into a small, provider-agnostic façade:

- Provide helpers like:
	- `execute_agent_prompt(request: AgentExecuteRequest, provider: Optional[str] = None, *, stream_handler: Optional[Callable[[str], None]] = None) -> AgentExecuteResponse`.
	- Optional `execute_agent_template(...)` that constructs prompts and delegates to `execute_agent_prompt`.

Internally:

- Use the registry to get a `CodingAgent`.
- Delegate to `execute_prompt`.

Remove Claude-specific details from this module (CLI flags, JSONL parsing, `save_prompt`, etc.) and keep only generic logic and logging.

---

## 7. Progress Comments via Stream Handlers

Progress comments should be a higher-level concern, not baked into agents.

- Remove `_emit_comment` and direct `insert_progress_comment` calls from provider code.
- Rely on `stream_handler` in `execute_prompt` to expose raw streaming output.
- For Claude, `ClaudeAgent` should:
	- Call `stream_handler(line)` for each JSONL line if provided.
	- Avoid direct notification calls.

Add a helper module like `cape/core/notifications/agent_stream_handlers.py` with:

- `make_progress_comment_handler(issue_id: int, adw_id: str, logger: logging.Logger) -> Callable[[str], None]` that:
	- Parses JSONL lines (reusing `iter_assistant_items`-style logic).
	- Extracts text/TodoWrite and calls `insert_progress_comment`.

Orchestration code (workflows/CLI) should create this handler when needed and pass it into `execute_prompt`, keeping notifications outside the agent implementation.

---

## 8. Hard Deprecation, Tests, and Docs

- Remove Claude-specific models from `cape/core/models.py` and migrate all imports to `cape.core.agents.claude_models` or the new generic models.
- Prefer `AgentExecuteRequest` / `AgentExecuteResponse` at higher levels; reserve Claude models for CLI wiring.
- Update tests to cover:
	- `ClaudeAgent` behavior and error handling.
	- Registry selection (`get_agent`).
	- Streaming behavior and progress-comment handlers.
- Adjust/remove tests that use old names.

Update `AGENTS.md` and relevant `ai_docs` to:

- Describe the `CodingAgent` abstraction and registry.
- Show how to add new providers or multiple Claude-like CLIs.
- Document the new pattern for notifications using injected stream handlers.
