# Chore Plan: Refactor to Abstract Agent Interface

## Description

Generalize the agent interface beyond Claude Code to support multiple coding agents and decouple progress comments from provider implementations while preserving streaming JSON output for notifications. This refactor introduces a provider-agnostic abstraction layer that:

1. **Decouples from Claude Code**: Moves Claude-specific logic (CLI invocation, JSONL parsing, subprocess handling) into a dedicated `ClaudeAgent` provider implementation
2. **Enables Multi-Provider Support**: Introduces a `CodingAgent` interface and registry system that allows registration of multiple agent providers (e.g., multiple Claude-like CLIs with different configurations)
3. **Separates Concerns**: Extracts notification logic from agent execution by using injectable stream handlers, keeping provider implementations focused on execution mechanics
4. **Preserves Behavior**: Maintains all existing functionality for Claude-based workflows including streaming output, progress comments, session tracking, and error handling
5. **Hard-Deprecates Legacy Models**: Migrates Claude-specific models from `cape/core/models.py` to `cape/core/agents/claude_models.py` with clear deprecation path

The refactor follows the principle of **introducing abstractions without breaking existing behavior**. All current tests must pass, and the workflow orchestration layer (`workflow.py`) requires minimal changes - primarily updating imports and using the registry to obtain agent instances.

**Key Design Decisions:**
- Stream handlers are the **only** extension point for progress notifications, injected at execution time
- Provider-agnostic models (`AgentExecuteRequest`/`AgentExecuteResponse`) become the primary interfaces
- Claude-specific models remain available but move to a dedicated module for clarity
- `cape/core/agent.py` transforms from Claude-specific implementation to a thin facade over the registry
- Directory structures, logging patterns, and error handling conventions are preserved

## Relevant Files

### Existing Files to Modify

- **`cape/app/src/cape/core/agent.py`** (372 lines) - Current Claude-specific implementation. Will be transformed into a provider-agnostic facade that delegates to the registry. Claude-specific functions (`check_claude_installed`, `parse_jsonl_output`, `convert_jsonl_to_json`, `iter_assistant_items`, `get_claude_env`, `save_prompt`) will be moved to `cape/core/agents/claude.py`. The `_emit_comment` function will be removed (notifications handled via stream handlers). Public API functions (`execute_template`) will be reimplemented to use the registry.

- **`cape/app/src/cape/core/models.py`** (104 lines) - Contains Claude-specific agent models. Lines 19-61 (agent models) will be removed and migrated to `cape/core/agents/claude_models.py`. Database models (`CapeIssue`, `CapeComment`) on lines 64-104 remain unchanged. Add deprecation aliases if needed for backward compatibility during migration.

- **`cape/app/src/cape/core/workflow.py`** (338 lines) - Orchestration layer that uses agent functions. Line 7 import will change from `from cape.core.agent import execute_template` to importing from the facade or registry. Lines 52-64, 126-138, 159-171, 206-218 (agent request creation and execution) may need updates to use provider-agnostic models or remain with Claude models temporarily. No logic changes required - only import/model adjustments.

- **`cape/app/src/cape/core/notifications.py`** (18 lines) - Current implementation remains unchanged. The `insert_progress_comment` function (lines 8-18) continues to provide best-effort comment insertion, but will only be called via stream handlers rather than directly from agent code.

- **`cape/app/tests/test_agent.py`** (181 lines) - Unit tests for agent module. Will need updates for:
  - Import statements to reference new module locations
  - Test functions to work with provider-agnostic models and registry
  - New tests for `ClaudeAgent` behavior and registry selection
  - Preservation of existing test scenarios (streaming, error handling, JSONL parsing)

- **`cape/app/tests/test_workflow.py`** (231 lines) - Workflow orchestration tests. Minimal changes needed - primarily updating mock targets if function locations change. All existing test scenarios (classification, planning, implementation, error handling) must continue passing.

- **`cape/app/tests/test_models.py`** - Will need updates to import Claude-specific models from new location (`cape.core.agents.claude_models`). Tests for database models remain unchanged.

### New Files to Create

#### Core Agent Abstraction

- **`cape/app/src/cape/core/agents/base.py`** - Defines the provider-agnostic interface:
  - `AgentExecuteRequest` model: `prompt`, `issue_id`, `adw_id`, `agent_name`, `model` (Optional[str]), `output_path` (Optional[str]), `provider_options` (Dict[str, Any])
  - `AgentExecuteResponse` model: `output`, `success`, `session_id` (Optional[str]), `raw_output_path` (Optional[str]), `error_detail` (Optional[str])
  - `CodingAgent` abstract base class with `execute_prompt(request: AgentExecuteRequest, *, stream_handler: Optional[Callable[[str], None]] = None) -> AgentExecuteResponse` method
  - Documentation strings explaining the interface contract and stream handler protocol

- **`cape/app/src/cape/core/agents/__init__.py`** - Package initialization that exports public interfaces:
  - Re-exports from `base.py`: `CodingAgent`, `AgentExecuteRequest`, `AgentExecuteResponse`
  - Re-exports from `registry.py`: `get_agent`, `register_agent`
  - Provides clean public API for consumers

#### Claude-Specific Implementation

- **`cape/app/src/cape/core/agents/claude_models.py`** - Migrated Claude-specific models with renamed classes:
  - `ClaudeAgentPromptRequest` (was `AgentPromptRequest` in `models.py:19-28`): Preserves all fields including `model: Literal["sonnet", "opus"]`, `dangerously_skip_permissions`, `output_file`
  - `ClaudeAgentPromptResponse` (was `AgentPromptResponse` in `models.py:31-36`): Fields `output`, `success`, `session_id`
  - `ClaudeAgentTemplateRequest` (was `AgentTemplateRequest` in `models.py:39-47`): Fields for slash command execution
  - `ClaudeAgentResultMessage` (was `ClaudeCodeResultMessage` in `models.py:50-61`): JSONL result parsing structure
  - All field definitions remain compatible with original implementations

- **`cape/app/src/cape/core/agents/claude.py`** - Claude Code provider implementation containing migrated functions:
  - **Environment/CLI Utilities**: `CLAUDE_PATH`, `check_claude_installed()`, `get_claude_env()` (from `agent.py:24`, `43-51`, `139-183`)
  - **JSONL Helpers**: `parse_jsonl_output()`, `convert_jsonl_to_json()` (from `agent.py:54-100`)
  - **Content Parsing**: `iter_assistant_items()` (from `agent.py:103-136`) - critical for streaming
  - **Prompt Logging**: `save_prompt()` (from `agent.py:186-207`)
  - **ClaudeAgent Class**: Implements `CodingAgent` interface with:
    - `execute_prompt()`: Maps `AgentExecuteRequest` → `ClaudeAgentPromptRequest`, runs subprocess with threading (from `agent.py:210-344`), invokes `stream_handler(line)` for each stdout line, parses JSONL to populate `AgentExecuteResponse`
    - Preserves all error handling, session ID extraction, and timeout logic from original implementation
  - **Template Helper**: `execute_claude_template()` function that takes `ClaudeAgentTemplateRequest` and delegates to `execute_prompt()`

#### Registry and Factory

- **`cape/app/src/cape/core/agents/registry.py`** - Provider selection and registration:
  - `_AGENTS: Dict[str, CodingAgent]` - Internal registry mapping provider names to instances
  - `register_agent(name: str, agent: CodingAgent)` - Registration function for adding new providers
  - `get_agent(provider: Optional[str] = None) -> CodingAgent` - Factory function that:
    - Uses explicit `provider` parameter if passed
    - Otherwise reads `CAPE_AGENT_PROVIDER` environment variable
    - Defaults to `"claude"` if not specified
    - Raises `ValueError` if provider not found
  - Default registration: `register_agent("claude", ClaudeAgent())` during module initialization
  - Supports registering multiple Claude-like CLIs with different configurations via `provider_options`

#### Notification Helpers

- **`cape/app/src/cape/core/notifications/agent_stream_handlers.py`** - Stream handler factory for progress comments:
  - `make_progress_comment_handler(issue_id: int, adw_id: str, logger: logging.Logger) -> Callable[[str], None]` - Creates a stream handler that:
    - Parses JSONL lines using `iter_assistant_items`-style logic (imported/reused from `claude.py`)
    - Extracts text and TodoWrite items from assistant messages
    - Calls `insert_progress_comment(issue_id, text, logger)` for each item
    - Handles JSON parsing errors gracefully (logs and continues)
  - `make_simple_logger_handler(logger: logging.Logger) -> Callable[[str], None]` - Creates a stream handler that just logs raw lines (useful for debugging)

- **`cape/app/src/cape/core/notifications/__init__.py`** - Package initialization:
  - Re-exports `insert_progress_comment` from parent `notifications.py`
  - Exports stream handler factories from `agent_stream_handlers.py`
  - Maintains backward compatibility for existing imports

#### Testing

- **`cape/app/tests/test_agents_base.py`** - Tests for core abstraction:
  - Test `AgentExecuteRequest` and `AgentExecuteResponse` model validation
  - Test `CodingAgent` abstract base class cannot be instantiated
  - Test provider_options passthrough behavior

- **`cape/app/tests/test_agents_claude.py`** - Tests for Claude provider:
  - Migrate relevant tests from `test_agent.py` (JSONL parsing, CLI checks, subprocess execution)
  - Test `ClaudeAgent.execute_prompt()` with mocked subprocess
  - Test stream handler invocation during execution
  - Test error handling and session ID extraction
  - Test model mapping from `AgentExecuteRequest` to `ClaudeAgentPromptRequest`

- **`cape/app/tests/test_agents_registry.py`** - Tests for registry:
  - Test default provider selection (`"claude"`)
  - Test explicit provider parameter
  - Test `CAPE_AGENT_PROVIDER` environment variable
  - Test provider not found error
  - Test registering custom providers

- **`cape/app/tests/test_notifications_stream_handlers.py`** - Tests for notification helpers:
  - Test `make_progress_comment_handler()` parses JSONL and calls `insert_progress_comment`
  - Test error handling for malformed JSON
  - Test handler ignores non-assistant messages
  - Mock `insert_progress_comment` to verify call counts and arguments

### Files Used as Reference

- **`cape/app/src/cape/core/agent.py`** (lines 1-372) - Source implementation for all Claude-specific logic to be extracted, subprocess patterns, streaming handlers, error handling, directory conventions
- **`cape/app/src/cape/core/models.py`** (lines 19-61) - Source models to be migrated to `claude_models.py`
- **`cape/app/src/cape/core/workflow.py`** (lines 1-338) - Integration patterns showing how `execute_template` is used in orchestration
- **`cape/app/tests/test_agent.py`** (lines 1-181) - Test patterns for mocking subprocess, streaming, error scenarios

## Step-by-Step Tasks

### 1. Create Base Agent Abstraction Models and Interface

Create the provider-agnostic foundation in `cape/app/src/cape/core/agents/base.py`:

- Define `AgentExecuteRequest` Pydantic model with fields:
  - `prompt: str` - The full prompt/command to execute
  - `issue_id: int` - Cape issue ID for workflow tracking
  - `adw_id: str` - Workflow identifier for logging/artifacts
  - `agent_name: str` - Agent name for directory structure
  - `model: Optional[str] = None` - Provider-neutral model name
  - `output_path: Optional[str] = None` - Optional raw output destination
  - `provider_options: Dict[str, Any] = Field(default_factory=dict)` - Provider-specific configuration
- Define `AgentExecuteResponse` Pydantic model with fields:
  - `output: str` - Main textual result from execution
  - `success: bool` - Execution success flag
  - `session_id: Optional[str] = None` - Session identifier if available
  - `raw_output_path: Optional[str] = None` - Path to raw output file
  - `error_detail: Optional[str] = None` - Error message if failed
- Define `CodingAgent` abstract base class:
  - Import `ABC` and `abstractmethod` from `abc` module
  - Method signature: `@abstractmethod def execute_prompt(self, request: AgentExecuteRequest, *, stream_handler: Optional[Callable[[str], None]] = None) -> AgentExecuteResponse`
  - Docstring explaining:
    - `request`: Execution parameters
    - `stream_handler`: Optional callback receiving raw streaming output (e.g., JSONL lines) as they arrive
    - Returns: Structured response with output and metadata
    - Stream handler protocol: receives chunks (typically line-by-line), should handle parsing errors, never raises
- Add module docstring explaining the provider-agnostic agent interface

**Validation:**
- Import successfully without errors
- Models pass Pydantic validation
- `CodingAgent` cannot be instantiated directly (raises `TypeError`)

### 2. Create Claude-Specific Models Module

Migrate and rename models in `cape/app/src/cape/core/agents/claude_models.py`:

- Copy and rename `AgentPromptRequest` → `ClaudeAgentPromptRequest` from `models.py:19-28`:
  - Preserve fields: `prompt`, `adw_id`, `issue_id`, `agent_name`, `model: Literal["sonnet", "opus"]`, `dangerously_skip_permissions`, `output_file`
  - Keep all field validators and defaults
- Copy and rename `AgentPromptResponse` → `ClaudeAgentPromptResponse` from `models.py:31-36`:
  - Preserve fields: `output`, `success`, `session_id: Optional[str]`
- Copy and rename `AgentTemplateRequest` → `ClaudeAgentTemplateRequest` from `models.py:39-47`:
  - Preserve fields: `agent_name`, `slash_command: SlashCommand`, `args`, `adw_id`, `issue_id`, `model`
  - Import `SlashCommand` from `cape.core.models` (stays in original location)
- Copy and rename `ClaudeCodeResultMessage` → `ClaudeAgentResultMessage` from `models.py:50-61`:
  - Preserve all fields: `type`, `subtype`, `is_error`, `duration_ms`, `duration_api_ms`, `num_turns`, `result`, `session_id`, `total_cost_usd`
- Add module docstring: "Claude Code-specific data models for agent execution. These models preserve Claude CLI contracts including model names, flags, and JSONL result structures."

**Validation:**
- All models import successfully
- Model field definitions match original types exactly
- Pydantic validation works for all models

### 3. Implement ClaudeAgent Provider

Create `cape/app/src/cape/core/agents/claude.py` by extracting and adapting logic from `agent.py`:

**Step 3.1: Migrate Utility Functions**
- Copy `CLAUDE_PATH` constant (from `agent.py:24`)
- Copy `check_claude_installed()` function (from `agent.py:43-51`) - no changes needed
- Copy `get_claude_env()` function (from `agent.py:139-183`) - no changes needed
- Copy `parse_jsonl_output()` function (from `agent.py:54-77`) - no changes needed
- Copy `convert_jsonl_to_json()` function (from `agent.py:80-100`) - no changes needed
- Copy `iter_assistant_items()` function (from `agent.py:103-136`) - **critical for streaming**, no changes needed
- Copy `save_prompt()` function (from `agent.py:186-207`) - no changes needed
- Add module-level `_DEFAULT_LOGGER = logging.getLogger(__name__)`

**Step 3.2: Implement ClaudeAgent Class**
- Define `class ClaudeAgent(CodingAgent)` inheriting from `base.CodingAgent`
- Implement `execute_prompt(self, request: AgentExecuteRequest, *, stream_handler: Optional[Callable[[str], None]] = None) -> AgentExecuteResponse`:
  - **Map models**: Convert `AgentExecuteRequest` to `ClaudeAgentPromptRequest`:
    - Use `provider_options.get("model", "opus")` for model field
    - Use `provider_options.get("dangerously_skip_permissions", True)` for permissions flag
    - Determine `output_file`: Use `request.output_path` if set, otherwise construct from `adw_id/agent_name/raw_output.jsonl` pattern
  - **Check Claude CLI**: Call `check_claude_installed()`, return error response if CLI missing
  - **Save prompt**: Call `save_prompt(request.prompt, request.adw_id, request.agent_name)`
  - **Create output directory**: `os.makedirs(os.path.dirname(output_file), exist_ok=True)`
  - **Build command**: Construct `[CLAUDE_PATH, "-p", prompt, "--model", model, "--output-format", "stream-json", "--verbose", "--dangerously-skip-permissions"]`
  - **Execute subprocess** (adapted from `agent.py:236-274`):
    - Use `subprocess.Popen()` with stdout/stderr pipes
    - Create two daemon threads for streaming:
      - `_stream_stdout`: Reads lines, writes to output file, flushes, calls `stream_handler(line)` if provided
      - `_capture_stderr`: Collects stderr lines
    - Wait for process completion with `process.wait()`
    - Join threads
  - **Parse results** (adapted from `agent.py:276-344`):
    - Call `parse_jsonl_output(output_file)` to get messages and result message
    - Call `convert_jsonl_to_json(output_file)` to create JSON version
    - Extract `session_id`, `is_error`, `result` text from result message with fallback logic
    - Map to `AgentExecuteResponse`:
      - `output`: result text or error detail
      - `success`: based on returncode and is_error flag
      - `session_id`: from result message
      - `raw_output_path`: the output_file path
      - `error_detail`: stderr or parsed error message if failed
  - **Error handling**: Wrap in try-except, catch all exceptions, return failed `AgentExecuteResponse` with error details
- Add docstring explaining Claude Code CLI integration, JSONL format, stream handler protocol

**Step 3.3: Add Template Helper**
- Implement `execute_claude_template(request: ClaudeAgentTemplateRequest) -> ClaudeAgentPromptResponse`:
  - Construct prompt: `f"{request.slash_command} {' '.join(request.args)}"`
  - Create output directory: `.cape/logs/agents/{adw_id}/{agent_name}/`
  - Build output file path: `{output_dir}/raw_output.jsonl`
  - Create `AgentExecuteRequest` with prompt, issue_id, adw_id, agent_name, provider_options for model
  - Create `ClaudeAgent` instance and call `execute_prompt()`
  - Map `AgentExecuteResponse` back to `ClaudeAgentPromptResponse`
  - Return response
- Add docstring explaining template execution pattern

**Validation:**
- All functions and classes import without circular dependencies
- `ClaudeAgent` implements `CodingAgent` interface correctly
- Existing subprocess patterns preserved (threading, error handling)
- JSONL parsing logic identical to original

### 4. Create Agent Registry

Implement provider selection in `cape/app/src/cape/core/agents/registry.py`:

- Import `CodingAgent` from `base`, `ClaudeAgent` from `claude`
- Define `_AGENTS: Dict[str, CodingAgent] = {}` module-level registry
- Implement `register_agent(name: str, agent: CodingAgent) -> None`:
  - Validate `name` is non-empty string
  - Validate `agent` is instance of `CodingAgent`
  - Store in `_AGENTS[name]`
- Implement `get_agent(provider: Optional[str] = None) -> CodingAgent`:
  - If `provider` is None, read `CAPE_AGENT_PROVIDER` environment variable
  - If still None, default to `"claude"`
  - Look up provider in `_AGENTS` dictionary
  - If not found, raise `ValueError(f"Agent provider '{provider}' not registered. Available: {list(_AGENTS.keys())}")`
  - Return agent instance
- Add initialization code at module level:
  - `register_agent("claude", ClaudeAgent())`
  - Log default registration at debug level
- Add docstring explaining registry pattern, environment variable usage, and how to register custom providers

**Validation:**
- `get_agent()` returns `ClaudeAgent` instance by default
- `get_agent("claude")` returns registered instance
- `CAPE_AGENT_PROVIDER` environment variable overrides default
- `ValueError` raised for unknown providers with helpful message
- Multiple registrations work correctly

### 5. Create Notification Stream Handlers

Implement stream handler factories in `cape/app/src/cape/core/notifications/agent_stream_handlers.py`:

- Import `logging`, `json`, `Callable`, `insert_progress_comment` from `cape.core.notifications`, `iter_assistant_items` from `cape.core.agents.claude`
- Implement `make_progress_comment_handler(issue_id: int, adw_id: str, logger: logging.Logger) -> Callable[[str], None]`:
  - Define inner closure function `handler(line: str) -> None`:
    - Strip line and skip if empty
    - Call `iter_assistant_items(line)` to parse JSONL
    - For each item returned:
      - Serialize to JSON: `json.dumps(item, indent=2)`
      - Call `insert_progress_comment(issue_id, text, logger)`
    - Catch `json.JSONDecodeError` and log error but continue
    - Catch all other exceptions, log error, continue (never raise)
  - Return handler function
  - Add docstring explaining: "Creates stream handler that parses assistant messages and inserts progress comments. Best-effort, never raises exceptions."
- Implement `make_simple_logger_handler(logger: logging.Logger) -> Callable[[str], None]`:
  - Define inner closure function `handler(line: str) -> None`:
    - Log line at debug level: `logger.debug("Agent output: %s", line.strip())`
  - Return handler function
  - Add docstring: "Creates stream handler that logs raw output lines for debugging."
- Add module docstring explaining stream handler protocol and usage patterns

**Validation:**
- Handlers can be created and called successfully
- `make_progress_comment_handler` parses JSONL and calls `insert_progress_comment`
- Handlers handle errors gracefully without raising
- Simple logger handler logs output correctly

### 6. Update Package Initializations

Create `__init__.py` files to define public APIs:

**Step 6.1: `cape/app/src/cape/core/agents/__init__.py`**
- Import and re-export from `base`: `CodingAgent`, `AgentExecuteRequest`, `AgentExecuteResponse`
- Import and re-export from `registry`: `get_agent`, `register_agent`
- Import `ClaudeAgent` from `claude` (for direct instantiation if needed)
- Add `__all__` list with exported names
- Add module docstring: "Provider-agnostic coding agent interfaces and registry. Use get_agent() to obtain configured provider."

**Step 6.2: `cape/app/src/cape/core/notifications/__init__.py`**
- Import and re-export `insert_progress_comment` from parent `notifications.py`
- Import and re-export from `agent_stream_handlers`: `make_progress_comment_handler`, `make_simple_logger_handler`
- Add `__all__` list with exported names
- Add module docstring: "Notification helpers for Cape workflows including progress comments and stream handlers."

**Validation:**
- All imports resolve correctly
- No circular import errors
- Public API exports work from package level

### 7. Refactor cape/core/agent.py to Provider-Agnostic Facade

Transform existing `agent.py` into a thin wrapper over the registry:

**Step 7.1: Remove Migrated Code**
- Delete functions moved to `claude.py`: `check_claude_installed`, `parse_jsonl_output`, `convert_jsonl_to_json`, `iter_assistant_items`, `get_claude_env`, `save_prompt` (lines 43-207)
- Delete `CLAUDE_PATH` constant (line 24)
- Delete `_emit_comment` function (lines 35-40) - notifications now via stream handlers
- Keep `_get_issue_logger` helper (lines 29-32) - may be useful for backward compatibility

**Step 7.2: Update Imports**
- Remove: `from cape.core.models import AgentPromptRequest, AgentPromptResponse, AgentTemplateRequest`
- Remove: `from cape.core.notifications import insert_progress_comment`
- Add: `from cape.core.agents import get_agent, AgentExecuteRequest, AgentExecuteResponse`
- Add: `from cape.core.agents.claude_models import ClaudeAgentPromptRequest, ClaudeAgentPromptResponse, ClaudeAgentTemplateRequest`
- Add: `from cape.core.notifications import make_progress_comment_handler`

**Step 7.3: Implement Backward-Compatible Functions**
- Reimplement `prompt_claude_code(request: ClaudeAgentPromptRequest) -> ClaudeAgentPromptResponse`:
  - Map `ClaudeAgentPromptRequest` to `AgentExecuteRequest`:
    - Set `prompt`, `issue_id`, `adw_id`, `agent_name` directly
    - Set `model` to `request.model`
    - Set `output_path` to `request.output_file`
    - Set `provider_options` with `{"dangerously_skip_permissions": request.dangerously_skip_permissions}`
  - Create progress comment handler: `handler = make_progress_comment_handler(request.issue_id, request.adw_id, _get_issue_logger(request.adw_id))`
  - Get agent: `agent = get_agent("claude")`
  - Execute: `response = agent.execute_prompt(agent_request, stream_handler=handler)`
  - Map `AgentExecuteResponse` to `ClaudeAgentPromptResponse`
  - Add final progress comment if successful: `insert_progress_comment(request.issue_id, f"Output saved to: {response.raw_output_path}", logger)`
  - Return response
  - Add docstring: "Legacy function for backward compatibility. Prefer using get_agent() and AgentExecuteRequest directly."
- Reimplement `execute_template(request: ClaudeAgentTemplateRequest) -> ClaudeAgentPromptResponse`:
  - Import `execute_claude_template` from `cape.core.agents.claude`
  - Delegate directly: `return execute_claude_template(request)`
  - Add docstring: "Legacy function for backward compatibility. Delegates to Claude provider template helper."

**Step 7.4: Add New Provider-Agnostic Helpers**
- Implement `execute_agent_prompt(request: AgentExecuteRequest, provider: Optional[str] = None, *, stream_handler: Optional[Callable[[str], None]] = None) -> AgentExecuteResponse`:
  - Get agent: `agent = get_agent(provider)`
  - Execute: `return agent.execute_prompt(request, stream_handler=stream_handler)`
  - Add docstring: "Execute agent prompt with specified or default provider. Use stream_handler for notifications."
- Optionally implement `execute_agent_template(agent_name: str, slash_command: str, args: List[str], adw_id: str, issue_id: int, provider: Optional[str] = None, model: Optional[str] = None) -> AgentExecuteResponse`:
  - Construct prompt from slash command and args
  - Build `AgentExecuteRequest`
  - Call `execute_agent_prompt`
  - Return response
  - Add docstring: "Template execution helper using provider-agnostic models."

**Validation:**
- `prompt_claude_code` maintains exact same signature and behavior
- `execute_template` maintains exact same signature and behavior
- New functions provide clean provider-agnostic API
- No Claude-specific implementation details remain in module

### 8. Update cape/core/models.py

Remove migrated models and add deprecation guidance:

**Step 8.1: Remove Claude-Specific Models**
- Delete `AgentPromptRequest` class definition (lines 19-28)
- Delete `AgentPromptResponse` class definition (lines 31-36)
- Delete `AgentTemplateRequest` class definition (lines 39-47)
- Delete `ClaudeCodeResultMessage` class definition (lines 50-61)
- Keep `SlashCommand` type definition (lines 9-16) - used by database and workflows
- Keep `CapeIssue` model (lines 64-89) - database model
- Keep `CapeComment` model (lines 92-104) - database model

**Step 8.2: Add Deprecation Aliases (Optional)**
- If immediate migration is difficult, add temporary aliases:
  ```python
  # Deprecated - use cape.core.agents.claude_models instead
  from cape.core.agents.claude_models import (
      ClaudeAgentPromptRequest as AgentPromptRequest,
      ClaudeAgentPromptResponse as AgentPromptResponse,
      ClaudeAgentTemplateRequest as AgentTemplateRequest,
      ClaudeAgentResultMessage as ClaudeCodeResultMessage,
  )
  ```
- Add comment: "TODO: Remove aliases after migrating all imports"

**Step 8.3: Update Module Docstring**
- Change to: "Data types for Cape CLI workflow components. Agent-specific models moved to cape.core.agents package."

**Validation:**
- File still imports successfully
- Database models remain functional
- Deprecation aliases work if added
- No circular imports

### 9. Update cape/core/workflow.py Imports

Minimal changes to workflow orchestration:

**Step 9.1: Update Import Statements**
- Change line 7 from: `from cape.core.agent import execute_template`
- To: `from cape.core.agent import execute_template`  # No change needed if facade preserved
- Or: `from cape.core.agents.claude import execute_claude_template as execute_template`  # If using provider directly
- Update imports from models if needed:
  - If using aliases: No changes needed
  - If migrating fully: `from cape.core.agents.claude_models import ClaudeAgentTemplateRequest as AgentTemplateRequest, ClaudeAgentPromptResponse as AgentPromptResponse`

**Step 9.2: Verify Function Calls**
- Lines 52-64, 126-138, 159-171, 206-218: Verify `execute_template()` calls work with updated imports
- No logic changes required - only import path adjustments

**Validation:**
- All workflow functions execute successfully
- Request/response models work correctly
- No behavior changes in orchestration

### 10. Update Tests for New Module Structure

Migrate and create tests for refactored code:

**Step 10.1: Create test_agents_base.py**
- Test `AgentExecuteRequest` model validation:
  - Valid request with all required fields
  - Optional fields default correctly
  - provider_options defaults to empty dict
- Test `AgentExecuteResponse` model validation:
  - Valid response with all fields
  - Optional fields can be None
- Test `CodingAgent` abstract class:
  - Cannot instantiate directly (raises TypeError)
  - Must implement execute_prompt method

**Step 10.2: Create test_agents_claude.py**
- Migrate tests from `test_agent.py`:
  - `test_check_claude_installed_success` → test utility function
  - `test_parse_jsonl_output` → test JSONL parsing
  - `test_convert_jsonl_to_json` → test conversion
  - `test_get_claude_env` → test environment filtering
  - `test_save_prompt` → test prompt logging
- Add new `ClaudeAgent` tests:
  - `test_claude_agent_execute_prompt_success`: Mock subprocess, verify `AgentExecuteResponse` populated correctly, verify stream_handler called
  - `test_claude_agent_execute_prompt_failure`: Test error handling, verify `error_detail` populated
  - `test_claude_agent_execute_prompt_no_stream_handler`: Verify execution works without handler
  - `test_claude_agent_model_mapping`: Verify `AgentExecuteRequest` → `ClaudeAgentPromptRequest` mapping
- Use same mocking patterns as original tests (patch subprocess.Popen, StringIO for streams)

**Step 10.3: Create test_agents_registry.py**
- `test_get_agent_default`: Verify returns ClaudeAgent by default
- `test_get_agent_explicit_provider`: Verify explicit "claude" parameter works
- `test_get_agent_environment_variable`: Mock `CAPE_AGENT_PROVIDER` env var, verify selection
- `test_get_agent_not_found`: Verify ValueError with helpful message for unknown provider
- `test_register_agent`: Create mock agent, register, verify retrieval works
- `test_register_agent_duplicate`: Verify can overwrite existing registration

**Step 10.4: Create test_notifications_stream_handlers.py**
- `test_make_progress_comment_handler_success`: Mock `insert_progress_comment`, feed JSONL lines, verify calls
- `test_make_progress_comment_handler_malformed_json`: Feed invalid JSON, verify logs error but doesn't raise
- `test_make_progress_comment_handler_non_assistant_message`: Feed non-assistant JSONL, verify no comment inserted
- `test_make_simple_logger_handler`: Mock logger, feed lines, verify debug logs

**Step 10.5: Update test_agent.py**
- Update imports to reference new locations:
  - `from cape.core.agents.claude import check_claude_installed, parse_jsonl_output, ...`
  - `from cape.core.agents.claude_models import ClaudeAgentPromptRequest, ...`
- Update function references in tests to match new module structure
- Verify all existing tests still pass with updated imports
- **Critical**: Preserve `test_prompt_claude_code_success` test - validates end-to-end flow

**Step 10.6: Update test_workflow.py**
- Update mock targets if function locations changed (e.g., `@patch("cape.core.workflow.execute_template")`)
- Verify all existing tests pass without modification to test logic
- No behavior changes expected

**Step 10.7: Update test_models.py**
- Update imports for Claude models: `from cape.core.agents.claude_models import ...`
- Verify model validation tests still pass
- Database model tests unchanged

**Validation:**
- All new test files pass successfully
- All existing tests pass with updated imports
- Test coverage maintained or improved
- No behavior regressions

### 11. Run Full Test Suite and Validation

Execute comprehensive validation to ensure refactor preserves behavior:

- Run full test suite: `cd cape/app && uv run pytest -v`
- Verify all tests pass (expect ~30-40 tests total after additions)
- Check for import errors or circular dependencies
- Verify specific test categories:
  - Agent execution tests (streaming, error handling, JSONL parsing)
  - Workflow orchestration tests (classification, planning, implementation)
  - Database operation tests (unchanged)
  - Model validation tests (updated imports)
- Run type checking if configured: `mypy cape/app/src/cape`
- Verify no regression in existing functionality
- Check logs for any deprecation warnings or errors

**Acceptance Criteria:**
- Zero test failures
- No import errors
- All original functionality preserved
- New abstraction layers working correctly
- Stream handlers properly integrated
- Registry selection working

### 12. Update Documentation

Update documentation to reflect new architecture:

**Step 12.1: Update cape/templates/AGENTS.md**
- Add section "Agent Provider System":
  - Explain `CodingAgent` interface and abstraction
  - Document `get_agent()` and `register_agent()` functions
  - Show example of using different providers
  - Explain `CAPE_AGENT_PROVIDER` environment variable
- Add section "Claude Code Provider":
  - Document Claude-specific models location (`cape.core.agents.claude_models`)
  - Explain JSONL format and streaming behavior
  - Document configuration options via `provider_options`
- Add section "Stream Handlers for Notifications":
  - Explain stream handler protocol
  - Show example of `make_progress_comment_handler`
  - Document how to create custom handlers
  - Note separation of concerns (execution vs. notifications)

**Step 12.2: Create cape/ai_docs/agent-architecture.md**
- Document overall architecture:
  - Three-layer design (abstraction → provider → orchestration)
  - Request/response flow diagrams
  - Model mapping between layers
- Explain design decisions:
  - Why stream handlers instead of embedded notifications
  - How to add new providers
  - When to use provider-agnostic vs. Claude-specific models
- Provide examples:
  - Basic agent execution
  - Custom provider implementation
  - Stream handler customization
  - Registry usage patterns

**Step 12.3: Add Migration Guide**
- Create `cape/specs/agent-refactor-migration-guide.md`:
  - List all import changes needed
  - Show before/after code examples
  - Document backward-compatible facade functions
  - Provide timeline for deprecation aliases removal
  - List breaking changes (if any)

**Validation:**
- Documentation is clear and accurate
- Examples work as written
- Migration guide covers all changes
- Architecture diagrams (if added) are correct

## Validation Commands

Execute every command to validate the chore is complete with zero regressions.

```bash
# Change to cape app directory
cd cape/app

# Run full test suite with verbose output
uv run pytest -v

# Run specific test files for new modules
uv run pytest tests/test_agents_base.py -v
uv run pytest tests/test_agents_claude.py -v
uv run pytest tests/test_agents_registry.py -v
uv run pytest tests/test_notifications_stream_handlers.py -v

# Run existing tests to verify no regressions
uv run pytest tests/test_agent.py -v
uv run pytest tests/test_workflow.py -v
uv run pytest tests/test_models.py -v

# Check test coverage for new modules
uv run pytest tests/test_agents_base.py --cov=cape.core.agents.base --cov-report=term-missing
uv run pytest tests/test_agents_claude.py --cov=cape.core.agents.claude --cov-report=term-missing
uv run pytest tests/test_agents_registry.py --cov=cape.core.agents.registry --cov-report=term-missing

# Verify imports work correctly
uv run python -c "from cape.core.agents import CodingAgent, get_agent, AgentExecuteRequest, AgentExecuteResponse; print('Base imports: OK')"
uv run python -c "from cape.core.agents.claude import ClaudeAgent, check_claude_installed; print('Claude imports: OK')"
uv run python -c "from cape.core.agents.claude_models import ClaudeAgentPromptRequest; print('Claude models imports: OK')"
uv run python -c "from cape.core.notifications import make_progress_comment_handler; print('Notification handlers imports: OK')"

# Verify registry functionality
uv run python -c "from cape.core.agents import get_agent; agent = get_agent(); print(f'Default agent type: {type(agent).__name__}')"
uv run python -c "from cape.core.agents import get_agent; agent = get_agent('claude'); print(f'Claude agent type: {type(agent).__name__}')"

# Check for circular import errors
uv run python -c "import cape.core.agents; import cape.core.agent; import cape.core.workflow; print('No circular imports detected')"

# Run type checking if mypy is configured
uv run mypy cape/app/src/cape/core/agents/ || echo "Mypy not configured, skipping type checks"

# Verify backward compatibility - old imports still work if aliases added
uv run python -c "from cape.core.agent import execute_template; print('Backward compatible import: OK')" || echo "Note: Update imports if aliases removed"

# Run integration-style test of full workflow
uv run pytest tests/test_workflow.py::test_execute_workflow_success -v

# Check all Python files for syntax errors
uv run python -m py_compile src/cape/core/agents/base.py
uv run python -m py_compile src/cape/core/agents/claude.py
uv run python -m py_compile src/cape/core/agents/claude_models.py
uv run python -m py_compile src/cape/core/agents/registry.py
uv run python -m py_compile src/cape/core/notifications/agent_stream_handlers.py
```

## Notes

### Implementation Priorities

1. **Preserve Streaming Behavior**: The `iter_assistant_items()` function (agent.py:103-136) is critical for real-time progress comments. ClaudeAgent must call stream_handler for each line to maintain this behavior.

2. **Session ID Extraction**: Lines 287-291, 297-305, 320-338 in original agent.py have complex fallback logic for extracting session_id from JSONL results. This logic must be preserved in ClaudeAgent.execute_prompt().

3. **Directory Conventions**: The `.cape/logs/agents/{adw_id}/{agent_name}/` structure is used throughout the system. Preserve this pattern in ClaudeAgent and any facade functions.

4. **Error Handling**: The system uses best-effort patterns for status updates and progress comments (never halt workflow on notification failures). Maintain this principle with stream handlers.

5. **Thread Safety**: Original implementation uses daemon threads for stdout/stderr streaming. Preserve this pattern in ClaudeAgent to avoid blocking issues.

### Future Extensibility

- **Multiple Claude CLIs**: The registry can register multiple Claude instances with different paths: `register_agent("claude_alt", ClaudeAgent())` with different `provider_options["cli_path"]`
- **Alternative Providers**: New providers (Aider, Cursor API, etc.) can implement CodingAgent interface with their own streaming formats
- **Custom Stream Handlers**: Users can create specialized handlers for different notification backends (Slack, email, webhooks) by implementing the handler protocol
- **Provider-Specific Options**: The `provider_options` dict allows passing arbitrary configuration (timeouts, retry policies, custom flags) without changing the interface

### Migration Strategy

**Phase 1** (This Implementation):
- Create abstraction layer and ClaudeAgent
- Preserve backward-compatible facade in agent.py
- Update imports gradually using aliases in models.py
- All existing code continues working unchanged

**Phase 2** (Future):
- Migrate workflow.py to use provider-agnostic models directly
- Remove deprecation aliases from models.py
- Update all call sites to import from new locations
- Remove facade functions in favor of registry

**Phase 3** (Future):
- Add additional providers (if needed)
- Enhance stream handler capabilities
- Optimize provider selection logic

### Testing Considerations

- **Mock Patterns**: Preserve existing mocking approach (patch subprocess.Popen, use StringIO for streams) for ClaudeAgent tests
- **Integration Tests**: Consider adding integration tests that actually call Claude CLI (marked as slow/optional) to validate end-to-end
- **Stream Handler Testing**: Mock `insert_progress_comment` in handler tests to verify parsing logic without database dependencies
- **Registry Testing**: Use in-memory registry (don't persist registrations between tests) to avoid test pollution

### Performance Notes

- **Streaming Overhead**: Adding stream_handler callback introduces minimal overhead (function call per line). JSONL parsing already happens in original implementation.
- **Threading Model**: Daemon threads for stdout/stderr are efficient for I/O-bound operations. No changes to threading model needed.
- **Registry Lookup**: Dictionary lookup for provider is O(1). Registrations happen at module import time (negligible cost).

### Documentation Standards

- All new classes/functions include docstrings with:
  - One-line summary
  - Args section describing parameters
  - Returns section describing return value
  - Raises section for expected exceptions
  - Examples section for complex usage patterns
- Use Google-style docstring format for consistency with existing code
- Include type hints for all function signatures
- Add module-level docstrings explaining purpose and usage

### Rollback Plan

If issues arise during implementation:
1. The refactor is designed to be incremental - each step can be validated independently
2. Backward-compatible facade in agent.py allows rolling back by reverting imports
3. Git history preserves original implementations if full rollback needed
4. Deprecation aliases provide safety net during migration phase
5. All existing tests must pass before considering implementation complete
