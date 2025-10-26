# Feature: Repackage Workflow Scripts into a TUI-First CLI Application

## Description

Transform the existing Cape workflow Python scripts from a collection of standalone executables into a unified, professionally structured CLI package named `cape-cli`. The package will provide a TUI-first user experience while maintaining full CLI automation capabilities through subcommands. This refactoring will improve maintainability, distribution, and user experience while preserving all existing functionality and database compatibility.

The application will default to launching an interactive Textual-based TUI when invoked without arguments (`cape`), and expose workflow operations as explicit subcommands for automation (`cape create`, `cape run`, etc.).

## User Story

As a **developer using Cape workflows**
I want to **install and use a single, cohesive CLI tool with both interactive and automation interfaces**
So that **I can efficiently manage issues through a TUI for exploration and use CLI commands for scripting and CI/CD integration**

## Problem Statement

The current Cape workflow implementation consists of multiple standalone Python scripts (`create_issue_from_string.py`, `create_issue_from_file.py`, `adw_plan_build.py`, `cape_tui.py`) that:

1. **Lack cohesive distribution**: Each script must be run via `uv run`, requiring users to know exact script names and paths
2. **Have inconsistent interfaces**: Different argument parsing patterns across scripts create cognitive overhead
3. **Duplicate functionality**: Common code (database, agents, models) is shared via module imports but not packaged
4. **Complicate installation**: No installable package means users can't simply `pip install cape-cli` and use `cape` command
5. **Split user experience**: TUI and CLI scripts are separate tools rather than unified interface

These limitations make Cape workflows difficult to distribute, install on new systems, and integrate into automated pipelines.

## Solution Statement

Create a professionally structured Python package `cape-cli` using modern packaging standards (uv, src/ layout, pyproject.toml) that:

1. **Provides a unified entry point**: Single `cape` command accessible after installation
2. **Defaults to TUI experience**: Running `cape` without arguments launches the interactive Textual interface
3. **Exposes CLI subcommands**: `cape create`, `cape create-from-file`, `cape run` for automation
4. **Follows Python best practices**: Proper package structure, entry points, resource management
5. **Maintains backward compatibility**: No changes to Supabase schema, agent templates, or environment variables

The implementation will use Typer's `invoke_without_command=True` pattern to enable TUI-first behavior while cleanly supporting explicit subcommands for scripting.

## Relevant Files

Use these files to implement the feature.

### Existing Source Files (cape/workflows/)

#### `/Users/bponghneng/git/cape/workflows/data_types.py` - Data Models
**Purpose**: Pydantic models for type-safe data handling
- **CapeIssue**: Domain model with id, description, status, timestamps
- **CapeComment**: Comment model for issue tracking
- **AgentPromptRequest/Response**: Claude Code agent execution types
- **SlashCommand**: Type literal for workflow commands
- **Migration**: Copy to `src/cape-cli/models.py` with no logic changes

#### `/Users/bponghneng/git/cape/workflows/utils.py` - Utility Functions
**Purpose**: ADW ID generation and structured logging
- **make_adw_id()**: Generates 8-character UUID for execution tracking
- **setup_logger()**: Creates dual-output logger (file + console)
- **Migration**: Copy to `src/cape-cli/utils.py`, update path logic for installed package context

#### `/Users/bponghneng/git/cape/workflows/supabase_client.py` - Database Client
**Purpose**: Supabase integration for issue and comment operations
- **get_client()**: Singleton Supabase client with LRU cache
- **create_issue()/fetch_issue()**: Issue CRUD operations
- **create_comment()/fetch_comments()**: Comment operations
- **Migration**: Copy to `src/cape-cli/database.py`, update imports to use cape-cli package

#### `/Users/bponghneng/git/cape/workflows/agent.py` - Agent Execution
**Purpose**: Claude Code CLI integration for workflow automation
- **execute_template()**: Run Claude Code with slash commands
- **prompt_claude_code()**: Low-level CLI execution and JSONL parsing
- **get_claude_env()**: Environment variable filtering for security
- **Migration**: Copy to `src/cape-cli/agent.py`, update output path resolution

#### `/Users/bponghneng/git/cape/workflows/adw_plan_build.py` - Workflow Driver
**Purpose**: End-to-end issue processing pipeline
- **classify_issue()**: Determine issue type (feature/bug/chore)
- **build_plan()**: Generate implementation plan via agent
- **get_plan_file()**: Extract plan file path from agent output
- **implement_plan()**: Execute implementation via agent
- **insert_progress_comment()**: Best-effort progress tracking
- **Migration**: Extract workflow functions to `src/cape-cli/workflow.py` module for reuse by both CLI and TUI

#### `/Users/bponghneng/git/cape/workflows/cape_tui.py` - TUI Application
**Purpose**: Textual-based terminal user interface
- **IssueListScreen**: Main issue table with DataTable
- **CreateIssueScreen**: Modal for creating new issues
- **IssueDetailScreen**: Issue details and comment history
- **WorkflowScreen**: Real-time workflow execution monitor
- **HelpScreen**: Keyboard shortcuts and usage info
- **Migration**: Copy to `src/cape-cli/tui.py`, update imports, integrate with shared workflow module

#### `/Users/bponghneng/git/cape/workflows/cape_tui.tcss` - TUI Stylesheet
**Purpose**: Textual CSS for TUI styling
- **Migration**: Copy to `src/cape-cli/cape_tui.tcss`, configure resource loading from installed package

#### `/Users/bponghneng/git/cape/workflows/create_issue_from_string.py` - CLI Script
**Purpose**: Create issues from command-line string
- **Migration**: Refactor logic into `cape create` subcommand in `src/cape-cli/cli.py`

#### `/Users/bponghneng/git/cape/workflows/create_issue_from_file.py` - CLI Script
**Purpose**: Create issues from file contents
- **Migration**: Refactor logic into `cape create-from-file` subcommand in `src/cape-cli/cli.py`

### Test Files

#### `/Users/bponghneng/git/cape/workflows/test_supabase_create_issue.py`
**Purpose**: Unit tests for create_issue() function with mocked Supabase
- **Migration**: Split into `tests/test_models.py` and `tests/test_database.py`

#### `/Users/bponghneng/git/cape/workflows/test_cli_scripts.py`
**Purpose**: Integration tests for CLI scripts via subprocess
- **Migration**: Migrate to `tests/test_cli.py` using Typer's CliRunner

#### `/Users/bponghneng/git/cape/workflows/test_adw_comments.py`
**Purpose**: Tests for progress comment insertion
- **Migration**: Migrate to `tests/test_workflow.py`

#### `/Users/bponghneng/git/cape/workflows/test_cape_tui.py`
**Purpose**: TUI component and interaction tests
- **Migration**: Migrate to `tests/test_tui.py` with updated imports

### New Files

#### `pyproject.toml` - Package Configuration
**Purpose**: Define package metadata, dependencies, and build configuration
```toml
[project]
name = "cape-cli"
version = "0.1.0"
description = "TUI-first CLI for Cape workflow management"
requires-python = ">=3.12"
dependencies = [
    "typer>=0.12.0",
    "textual>=0.50.0",
    "supabase>=2.0",
    "pydantic>=2.0",
    "python-dotenv>=1.0.0",
]

[project.scripts]
cape = "cape_cli.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

#### `src/cape-cli/__init__.py` - Package Initialization
**Purpose**: Define public API and version
```python
"""Cape CLI - TUI-first workflow management."""

__version__ = "0.1.0"
```

#### `src/cape-cli/cli.py` - CLI Entry Point
**Purpose**: Typer application with TUI-first behavior
```python
import typer
from typing import Optional
from pathlib import Path

app = typer.Typer(
    invoke_without_command=True,
    no_args_is_help=False,
    help="Cape CLI - TUI-first workflow management"
)

@app.callback()
def main(ctx: typer.Context):
    """Main entry point. Launches TUI if no subcommand provided."""
    if ctx.invoked_subcommand is None:
        from cape_cli.tui import CapeApp
        tui_app = CapeApp()
        tui_app.run()

@app.command()
def create(description: str):
    """Create a new issue from description string."""
    # Implementation from create_issue_from_string.py

@app.command()
def create_from_file(file_path: Path):
    """Create a new issue from description file."""
    # Implementation from create_issue_from_file.py

@app.command()
def run(
    issue_id: int,
    adw_id: Optional[str] = typer.Option(None, help="ADW workflow ID")
):
    """Execute the adw_plan_build workflow for an issue."""
    # Implementation using workflow.execute_workflow()
```

#### `src/cape-cli/workflow.py` - Workflow Orchestration
**Purpose**: Shared workflow logic for CLI and TUI
```python
"""Workflow orchestration for adw_plan_build process."""

def classify_issue(issue, adw_id, logger):
    """Classify issue and return command or error."""

def build_plan(issue, command, adw_id, logger):
    """Build implementation plan."""

def get_plan_file(plan_output, adw_id, logger):
    """Extract plan file path from output."""

def implement_plan(plan_file, adw_id, logger):
    """Execute implementation."""

def insert_progress_comment(issue_id, comment_text, logger):
    """Best-effort progress comment insertion."""

def execute_workflow(issue_id, adw_id, logger) -> bool:
    """Execute complete workflow. Returns True on success."""
```

## Implementation Plan

### Phase 1: Foundation

**Objective**: Establish core package structure and migrate foundational modules

**Duration**: 4-6 days

**Deliverable**: Installable package with core functionality (models, database, agent, utils)

### Phase 2: Core Implementation

**Objective**: Implement CLI commands and workflow orchestration

**Duration**: 5-7 days

**Deliverable**: Working CLI commands (create, create-from-file, run) for automation

### Phase 3: Integration

**Objective**: Integrate TUI, complete testing, and prepare for distribution

**Duration**: 5-7 days

**Deliverable**: Production-ready package with TUI, comprehensive tests, and documentation

## Step by Step Tasks

IMPORTANT: Execute every step in order, top to bottom.

### Task 1.1: Initialize Project Structure and Configuration

**Objective**: Create the cape-cli directory with proper Python package layout using src/ structure

**Steps**:
1. Create project directory: `mkdir -p /Users/bponghneng/git/cape/cape-cli`
2. Initialize uv project: `cd cape-cli && uv init --lib`
3. Create src layout:
   ```bash
   mkdir -p src/cape-cli
   mkdir -p tests
   touch src/cape-cli/__init__.py
   touch tests/__init__.py
   ```
4. Configure `pyproject.toml` with project metadata, dependencies, and entry point
5. Create `.gitignore` with Python, uv, and IDE patterns
6. Verify installation: `uv sync`

**Acceptance Criteria**:
- Project installs successfully with `uv sync`
- Entry point configured: `cape = "cape_cli.cli:main"`
- All required dependencies listed in `pyproject.toml`

### Task 1.2: Migrate Core Data Models Module

**Objective**: Copy and refactor data_types.py into src/cape-cli/models.py

**Steps**:
1. Copy `/Users/bponghneng/git/cape/workflows/data_types.py` to `src/cape-cli/models.py`
2. Update all imports to use absolute package imports
3. Verify all Pydantic models are present: CapeIssue, CapeComment, Agent types, SlashCommand
4. Add module-level docstring
5. Create unit tests in `tests/test_models.py` for field validators

**Acceptance Criteria**:
- `from cape_cli.models import CapeIssue` works correctly
- All Pydantic validation tests pass
- No relative imports from workflows directory

### Task 1.3: Migrate Utility Functions Module

**Objective**: Copy and refactor utils.py with updated path handling

**Steps**:
1. Copy `/Users/bponghneng/git/cape/workflows/utils.py` to `src/cape-cli/utils.py`
2. Update log directory path calculation:
   - Use current working directory as base for `agents/` directory
   - Remove hardcoded absolute paths
3. Add environment variable support for custom agents directory location
4. Create unit tests in `tests/test_utils.py`

**Acceptance Criteria**:
- `make_adw_id()` generates 8-character UUIDs
- `setup_logger()` creates log files in `./agents/{adw_id}/{trigger_type}/`
- Tests verify file and console handlers work independently

### Task 1.4: Migrate Supabase Client Module

**Objective**: Copy and refactor supabase_client.py with package imports

**Steps**:
1. Copy `/Users/bponghneng/git/cape/workflows/supabase_client.py` to `src/cape-cli/database.py`
2. Update imports: `from cape_cli.models import CapeIssue, CapeComment`
3. Preserve all functions: get_client, fetch_issue, fetch_all_issues, create_issue, create_comment, fetch_comments
4. Preserve SupabaseConfig validation logic
5. Create unit tests in `tests/test_database.py` with mocked Supabase client

**Acceptance Criteria**:
- All database operations work with mocked client
- Environment validation raises clear errors for missing variables
- LRU cache on get_client() functions correctly

### Task 1.5: Migrate Claude Code Agent Module

**Objective**: Copy and refactor agent.py with updated paths

**Steps**:
1. Copy `/Users/bponghneng/git/cape/workflows/agent.py` to `src/cape-cli/agent.py`
2. Update imports: `from cape_cli.models import AgentPromptRequest, AgentPromptResponse, AgentTemplateRequest`
3. Update output directory paths to use current working directory
4. Preserve subprocess execution logic and JSONL parsing
5. Create unit tests in `tests/test_agent.py` with mocked subprocess

**Acceptance Criteria**:
- `execute_template()` works with mocked Claude Code CLI
- JSONL parsing handles sample output files correctly
- Environment variable filtering preserves required vars

### Task 1.6: Create Workflow Orchestration Module

**Objective**: Extract workflow logic from adw_plan_build.py into reusable module

**Steps**:
1. Create `src/cape-cli/workflow.py`
2. Extract functions from `/Users/bponghneng/git/cape/workflows/adw_plan_build.py`:
   - classify_issue()
   - build_plan()
   - get_plan_file()
   - implement_plan()
   - insert_progress_comment()
3. Create new function: `execute_workflow(issue_id, adw_id, logger) -> bool`
4. Update imports to use cape-cli package
5. Create unit tests in `tests/test_workflow.py` with mocked agent calls

**Acceptance Criteria**:
- All workflow functions work independently
- `execute_workflow()` orchestrates all stages correctly
- Returns boolean instead of calling sys.exit()
- Progress comments inserted at 4 key points

### Task 2.1: Create CLI Entry Point with TUI-First Behavior

**Objective**: Implement cli.py with Typer configuration for TUI-first behavior

**Steps**:
1. Create `src/cape-cli/cli.py`
2. Configure Typer app: `typer.Typer(invoke_without_command=True, no_args_is_help=False)`
3. Implement main callback:
   ```python
   @app.callback()
   def main(ctx: typer.Context):
       if ctx.invoked_subcommand is None:
           from cape_cli.tui import CapeApp
           tui_app = CapeApp()
           tui_app.run()
   ```
4. Add stub subcommands: create, create-from-file, run
5. Add --version flag
6. Create basic CLI tests in `tests/test_cli.py` using CliRunner

**Acceptance Criteria**:
- `cape --help` displays command list
- `cape --version` shows version number
- Subcommand routing works (even with stubs)
- TUI callback prepared (will implement TUI in Task 3.1)

### Task 2.2: Implement `create` Subcommand

**Objective**: Create issues from command-line string arguments

**Steps**:
1. Implement `create` command in `cli.py`:
   ```python
   @app.command()
   def create(description: str):
       """Create a new issue from description string."""
   ```
2. Extract logic from `/Users/bponghneng/git/cape/workflows/create_issue_from_string.py`
3. Use `database.create_issue()` function
4. Use `setup_logger()` for execution logging
5. Print issue ID to stdout on success
6. Handle errors with user-friendly messages
7. Add CLI tests using CliRunner

**Acceptance Criteria**:
- `cape create "Fix login bug"` creates issue and prints ID
- Empty description raises clear error
- Missing env vars produce helpful error message
- Tests verify stdout contains only issue ID

### Task 2.3: Implement `create-from-file` Subcommand

**Objective**: Create issues from file contents

**Steps**:
1. Implement `create_from_file` command in `cli.py`:
   ```python
   @app.command()
   def create_from_file(file_path: Path):
       """Create a new issue from description file."""
   ```
2. Extract logic from `/Users/bponghneng/git/cape/workflows/create_issue_from_file.py`
3. Read file with UTF-8 encoding
4. Validate file exists, is regular file, content not empty
5. Use `database.create_issue()` function
6. Add CLI tests with temp files

**Acceptance Criteria**:
- `cape create-from-file issue.txt` creates issue and prints ID
- Missing file raises FileNotFoundError with clear message
- Directory path raises ValueError
- Empty file raises validation error
- Multi-line content preserved correctly

### Task 2.4: Implement `run` Subcommand

**Objective**: Execute adw_plan_build workflow from CLI

**Steps**:
1. Implement `run` command in `cli.py`:
   ```python
   @app.command()
   def run(
       issue_id: int,
       adw_id: Optional[str] = typer.Option(None, help="ADW workflow ID")
   ):
       """Execute the adw_plan_build workflow for an issue."""
   ```
2. Use `workflow.execute_workflow()` function
3. Auto-generate ADW ID if not provided
4. Set up logger with adw_id
5. Display progress messages during execution
6. Exit with code 1 on failure, 0 on success
7. Add integration tests with mocked agent calls

**Acceptance Criteria**:
- `cape run 123` executes full workflow
- Optional `--adw-id` parameter works
- Progress displayed during execution
- Errors halt workflow with clear messages
- All 5 workflow stages execute in sequence

### Task 3.1: Migrate TUI Application Module

**Objective**: Copy and integrate cape_tui.py into package

**Steps**:
1. Copy `/Users/bponghneng/git/cape/workflows/cape_tui.py` to `src/cape-cli/tui.py`
2. Update all imports to use cape-cli package:
   - `from cape_cli.database import fetch_issue, create_issue, fetch_all_issues, create_comment`
   - `from cape_cli.models import CapeIssue, CapeComment`
   - `from cape_cli.utils import make_adw_id, setup_logger`
3. Update WorkflowScreen to use `workflow.execute_workflow()` instead of inline logic
4. Verify all screens work: IssueListScreen, CreateIssueScreen, IssueDetailScreen, WorkflowScreen, HelpScreen
5. Test keyboard bindings: n, r, enter, q, ?, escape

**Acceptance Criteria**:
- `cape` command launches TUI successfully
- All screens render correctly
- Issue creation from TUI works
- Workflow execution from TUI works
- All keyboard shortcuts functional

### Task 3.2: Migrate TUI Stylesheet and Configure Resource Loading

**Objective**: Package cape_tui.tcss and configure loading from installed package

**Steps**:
1. Copy `/Users/bponghneng/git/cape/workflows/cape_tui.tcss` to `src/cape-cli/cape_tui.tcss`
2. Update `CapeApp` class in `tui.py` to load CSS from package resources:
   ```python
   from importlib.resources import files

   class CapeApp(App):
       CSS_PATH = None  # Will set dynamically

       def __init__(self):
           super().__init__()
           css_path = files("cape_cli").joinpath("cape_tui.tcss")
           self.CSS = css_path.read_text()
   ```
3. Test CSS loads correctly from installed package (not just source directory)
4. Verify all styling renders: colors, layouts, modal styles

**Acceptance Criteria**:
- TUI renders with correct styling after package installation
- CSS file packaged correctly in distribution
- Color themes apply (primary, accent, warning, success)
- Modal screens styled properly

### Task 3.3: Migrate Unit Tests

**Objective**: Migrate all test files with updated imports

**Steps**:
1. Create test files in `tests/` directory:
   - `tests/test_models.py` - From test_supabase_create_issue.py (model tests)
   - `tests/test_database.py` - From test_supabase_create_issue.py (database tests)
   - `tests/test_workflow.py` - From test_adw_comments.py
   - `tests/test_cli.py` - From test_cli_scripts.py
   - `tests/test_tui.py` - From test_cape_tui.py
2. Update all imports to use `cape-cli` package
3. Add pytest configuration to `pyproject.toml`:
   ```toml
   [tool.pytest.ini_options]
   testpaths = ["tests"]
   asyncio_mode = "auto"
   ```
4. Create `tests/conftest.py` with shared fixtures
5. Run full test suite: `pytest tests/`

**Acceptance Criteria**:
- All tests pass after migration
- Test coverage >= 80% for core modules
- No import errors
- Mocked dependencies work correctly

### Task 3.4: Create End-to-End Integration Tests

**Objective**: Validate complete application flows

**Steps**:
1. Create `tests/test_integration.py`
2. Implement integration tests:
   - Package installation test
   - CLI entry point test (`cape --help`)
   - Create command flow (string and file)
   - Run command flow with mocked agents
   - TUI launch test (initialization only)
3. Use pytest fixtures for test data setup/teardown
4. Tag integration tests: `@pytest.mark.integration`

**Acceptance Criteria**:
- All integration tests pass independently
- Tests clean up created resources
- Can run integration tests separately: `pytest -m integration`
- Tests work in fresh virtual environment

### Task 3.5: Create Documentation and Migration Guide

**Objective**: Write comprehensive user and developer documentation

**Steps**:
1. Create `README.md` with:
   - Project description
   - Installation instructions: `uv pip install cape-cli`
   - Quick start guide
   - Command reference
   - TUI usage with keyboard shortcuts
   - Environment variables
   - Troubleshooting
2. Create `MIGRATION.md` with:
   - Side-by-side command comparisons (old scripts vs new CLI)
   - Deprecation timeline
   - Breaking changes (if any)
3. Add docstrings to all public functions (Google style)
4. Update CLI help text for clarity

**Acceptance Criteria**:
- README covers all installation and usage scenarios
- MIGRATION guide clear for existing users
- All public APIs documented
- `cape --help` provides comprehensive guidance

### Task 3.6: Package Build and Distribution Setup

**Objective**: Configure package building and verify distribution

**Steps**:
1. Complete `pyproject.toml` build configuration:
   ```toml
   [build-system]
   requires = ["hatchling"]
   build-backend = "hatchling.build"

   [project]
   name = "cape-cli"
   version = "0.1.0"
   authors = [{name = "Your Name", email = "email@example.com"}]
   classifiers = [
       "Programming Language :: Python :: 3.12",
   ]
   ```
2. Build package: `uv build`
3. Test installation from wheel in fresh virtualenv:
   ```bash
   uv venv test-env
   source test-env/bin/activate
   uv pip install dist/cape_cli-0.1.0-py3-none-any.whl
   cape --version
   ```
4. Verify entry point works
5. Verify CSS and resources packaged

**Acceptance Criteria**:
- Package builds successfully with `uv build`
- Wheel and source distribution created in `dist/`
- Package installs from wheel
- `cape` command works after installation
- All resources (CSS) load correctly

### Task 3.7: Run Validation Commands

**Objective**: Validate the feature works correctly with zero regressions

**Steps**:
1. Install package in development mode: `uv pip install -e .`
2. Run all tests: `pytest tests/ -v --cov=cape-cli`
3. Verify CLI commands:
   - `cape --help` - Shows all commands
   - `cape --version` - Shows version
   - `cape create "Test issue"` - Creates issue
   - `cape create-from-file /tmp/test.txt` - Creates from file
   - `cape run <issue-id>` - Runs workflow (with mocked agents)
4. Verify TUI:
   - `cape` - Launches TUI
   - Navigate all screens
   - Create issue via TUI
   - Run workflow via TUI
5. Build package: `uv build`
6. Install from wheel and re-test all commands

**Acceptance Criteria**:
- All tests pass with coverage >= 80%
- All CLI commands work correctly
- TUI launches and all features functional
- Package builds and installs successfully
- No errors or warnings

## Testing Strategy

### Unit Tests

**Models** (`tests/test_models.py`):
- Pydantic model validation (field validators, defaults)
- `from_supabase()` class method conversion
- Type checking for all models

**Database** (`tests/test_database.py`):
- Mock all Supabase client calls
- Test CRUD operations: create_issue, fetch_issue, fetch_all_issues
- Test comment operations: create_comment, fetch_comments
- Test error handling for database failures
- Test SupabaseConfig validation

**Agent** (`tests/test_agent.py`):
- Mock subprocess execution
- Test JSONL parsing with sample outputs
- Test environment variable filtering
- Test error handling for CLI not found

**Workflow** (`tests/test_workflow.py`):
- Mock all agent.execute_template calls
- Test each workflow stage independently
- Test execute_workflow orchestration
- Test progress comment insertion (best-effort)

**Utils** (`tests/test_utils.py`):
- Test make_adw_id() UUID generation
- Test setup_logger() creates files and handlers
- Test logger retrieval

### Integration Tests

**CLI Commands** (`tests/test_cli.py`):
- Use Typer's CliRunner for testing
- Test create command with valid/invalid input
- Test create-from-file with temp files
- Test run command with mocked workflow

**TUI Application** (`tests/test_tui.py`):
- Use Textual's pilot for async testing
- Test screen navigation
- Test issue creation modal
- Test workflow execution screen
- Test keyboard bindings

**End-to-End** (`tests/test_integration.py`):
- Test package installation
- Test CLI entry point
- Test complete workflows
- Test TUI launch

### Edge Cases

- Empty or whitespace-only issue descriptions
- Missing or invalid file paths
- Missing environment variables (SUPABASE_URL, etc.)
- Database connection failures
- Agent execution failures at each workflow stage
- Non-existent issue IDs
- Unicode content in issues and files
- Very long issue descriptions (> 10,000 chars)
- Concurrent workflow executions
- CSS resource loading from installed vs. source package

## Acceptance Criteria

1. **Package Installation**:
   - Package builds successfully with `uv build`
   - Installs via `uv pip install cape-cli` (or from wheel)
   - Entry point `cape` accessible from command line

2. **CLI Functionality**:
   - `cape --help` displays all commands with descriptions
   - `cape --version` shows package version
   - `cape create <description>` creates issue and outputs ID
   - `cape create-from-file <path>` creates issue from file
   - `cape run <issue-id>` executes full workflow

3. **TUI Functionality**:
   - `cape` without arguments launches TUI
   - All screens render correctly (issue list, create, detail, workflow, help)
   - All keyboard shortcuts work (n, r, enter, q, ?, escape)
   - Workflow execution displays real-time progress
   - CSS styling applies correctly

4. **Testing**:
   - All unit tests pass
   - All integration tests pass
   - Test coverage >= 80% for core modules
   - No failing tests in CI

5. **Documentation**:
   - README with installation, usage, and examples
   - MIGRATION guide for transitioning from old scripts
   - All public functions have docstrings
   - CLI help text comprehensive

6. **Quality**:
   - No linting errors
   - Type hints where applicable
   - Consistent code style
   - No hardcoded paths or credentials

## Validation Commands

Execute every command to validate the feature works correctly with zero regressions.

```bash
# Install package in development mode
cd /Users/bponghneng/git/cape/cape-cli
uv pip install -e .

# Run test suite
pytest tests/ -v --cov=cape-cli --cov-report=term-missing

# Verify CLI entry point
cape --help
cape --version

# Test create command
cape create "Test issue from CLI"

# Test create-from-file command
echo "Test issue from file" > /tmp/test_issue.txt
cape create-from-file /tmp/test_issue.txt

# Test run command (requires valid issue ID and env vars)
# cape run <issue-id>

# Test TUI launch
cape

# Build package
uv build

# Test installation from wheel
uv venv /tmp/test-cape-env
source /tmp/test-cape-env/bin/activate
uv pip install dist/cape_cli-0.1.0-py3-none-any.whl
cape --version
cape --help
deactivate
```

## Notes

### Architecture Decisions

**TUI-First Approach**: Using `typer.Typer(invoke_without_command=True)` with a callback provides the cleanest pattern for defaulting to TUI while supporting explicit CLI commands. Alternative approaches (checking sys.argv manually) were considered but are less idiomatic.

**Workflow Module Extraction**: Creating a shared `workflow.py` module allows both CLI `run` command and TUI WorkflowScreen to use the same execution logic, reducing duplication and ensuring consistency.

**CSS Resource Loading**: Using `importlib.resources.files()` (Python 3.12+) for loading the CSS file from the installed package ensures it works in both development and production environments.

### Migration Considerations

**Backward Compatibility**: The package maintains full compatibility with existing:
- Supabase schema (cape_issues, cape_comments tables)
- Agent templates (slash commands unchanged)
- Environment variables (same names and usage)
- Log directory structure (agents/{adw_id}/...)

**Deprecation Path**: Old scripts can coexist during transition:
1. v0.1.0: Initial release, old scripts still functional
2. v0.2.0: Deprecation warnings added to old scripts
3. v1.0.0: Old scripts removed (if appropriate)

### Future Enhancements

**Potential Extensions**:
- Plugin system for custom workflow stages
- Configuration file support (cape.toml)
- Multi-project support
- Export/import issue data
- GitHub integration for creating GitHub issues
- Workflow templates and customization

### Development Environment

**Prerequisites**:
- Python >=3.12
- uv package manager
- Supabase account with configured environment variables
- Claude Code CLI (for workflow execution)
- Git for version control

**Environment Variables**:
```bash
# Required
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Optional
CLAUDE_CODE_PATH=claude
GITHUB_PAT=ghp_your_token
```

### Risk Mitigation

**CSS Loading Risk**: If importlib.resources causes issues, fallback to embedding CSS as Python string constant in tui.py.

**Path Resolution Risk**: Agent output paths use current working directory; document expected directory structure and make configurable via environment variable if needed.

**Testing Database Risk**: Integration tests should use mocked Supabase client or separate test instance to avoid polluting production data.
