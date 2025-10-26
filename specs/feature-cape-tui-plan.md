# Feature: Cape Textual TUI Interface

## Description

Create a Terminal User Interface (TUI) application using the Textual framework to provide an interactive interface for managing Cape issues and executing automated workflows. The application will replace command-line scripts with an intuitive, navigable interface that displays issue lists from Supabase, allows creation of new issues, and provides real-time monitoring of the adw_plan_build workflow execution.

The TUI will serve as a centralized dashboard for developers to browse issues, create new work items, and trigger automated planning and implementation workflows without needing to remember command syntax or manage multiple terminal sessions.

## User Story

As a **developer using the Cape workflow system**
I want to **interact with issues and workflows through a visual terminal interface**
So that **I can manage work items and monitor automated processes without memorizing CLI commands or switching between multiple terminal windows**

## Problem Statement

The current Cape workflow system requires developers to:
1. Manually execute Python scripts with command-line arguments to create issues
2. Remember specific script names and paths to run workflows
3. Monitor workflow progress by tailing log files or checking database comments
4. Query Supabase directly or use SQL to browse existing issues
5. Switch between multiple terminal windows to track workflow state

This creates friction in the development workflow, increases cognitive load, and makes it difficult to get a quick overview of pending work or workflow status.

## Solution Statement

Build a Textual-based TUI application (`cape_tui.py`) that provides:

1. **Issue List View**: A DataTable displaying all Cape issues with ID, description (truncated), status, and creation date - navigable with keyboard shortcuts
2. **Create Issue Form**: A modal dialog with multi-line text input for issue descriptions, with validation and instant feedback
3. **Issue Detail Screen**: Full issue information including complete description, status, timestamps, and chronological comment history
4. **Workflow Monitor**: Real-time progress tracking for the 4-stage adw_plan_build pipeline (Fetch → Classify → Plan → Implement) with live log output and stage indicators

The application will integrate directly with existing workflow modules (supabase_client.py, adw_plan_build.py, data_types.py, utils.py) rather than duplicating logic, ensuring consistency and maintainability.

## Relevant Files

### Existing Workflow Modules

#### `/Users/bponghneng/git/cape/cape/workflows/supabase_client.py`
**Purpose**: Database operations for Cape issues and comments

**Relevant Functions**:
- `get_client() -> Client` - Singleton Supabase client
- `fetch_issue(issue_id: int) -> CapeIssue` - Retrieve single issue
- `create_issue(description: str) -> CapeIssue` - Create new issue with validation
- `create_comment(issue_id: int, text: str) -> CapeComment` - Add comment to issue

**Needs Extension**:
```python
def fetch_all_issues() -> List[CapeIssue]:
    """Fetch all issues ordered by creation date (newest first)."""
    client = get_client()
    response = (
        client.table("cape_issues")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )
    return [CapeIssue.from_supabase(row) for row in response.data]

def fetch_comments(issue_id: int) -> List[CapeComment]:
    """Fetch all comments for an issue in chronological order."""
    client = get_client()
    response = (
        client.table("cape_comments")
        .select("*")
        .eq("issue_id", issue_id)
        .order("created_at", desc=False)
        .execute()
    )
    return [CapeComment(**row) for row in response.data]
```

#### `/Users/bponghneng/git/cape/cape/workflows/adw_plan_build.py`
**Purpose**: Main workflow orchestrator for the 4-stage pipeline

**Relevant Functions**:
- `classify_issue(issue, adw_id, logger)` - Stage 1: Determine issue type
- `build_plan(issue, command, adw_id, logger)` - Stage 2: Generate implementation plan
- `get_plan_file(output, adw_id, logger)` - Stage 3: Extract plan file path
- `implement_plan(plan_file, adw_id, logger)` - Stage 4: Execute implementation

**Integration Pattern**:
```python
# Import individual functions rather than running entire script
from adw_plan_build import classify_issue, build_plan, get_plan_file, implement_plan

# Execute workflow stages from TUI WorkflowScreen
def run_workflow(issue_id: int, adw_id: str, logger: Logger):
    issue = fetch_issue(issue_id)
    command, error = classify_issue(issue, adw_id, logger)
    plan_response = build_plan(issue, command, adw_id, logger)
    plan_file, error = get_plan_file(plan_response.output, adw_id, logger)
    impl_response = implement_plan(plan_file, adw_id, logger)
```

#### `/Users/bponghneng/git/cape/cape/workflows/data_types.py`
**Purpose**: Pydantic models for type safety and validation

**Relevant Models**:
```python
class CapeIssue(BaseModel):
    id: int
    description: str = Field(..., min_length=1)
    status: Literal["pending", "started", "completed"] = "pending"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class CapeComment(BaseModel):
    id: Optional[int] = None
    issue_id: int
    comment: str = Field(..., min_length=1)
    created_at: Optional[datetime] = None
```

**Usage**: Direct imports for type annotations and validation in TUI screens

#### `/Users/bponghneng/git/cape/cape/workflows/utils.py`
**Purpose**: Logging and utility functions

**Relevant Functions**:
- `make_adw_id() -> str` - Generate 8-character UUID for workflow tracking
- `setup_logger(adw_id, trigger_type) -> Logger` - Dual-sink logger (console + file)

**Integration**:
```python
# Initialize logger on TUI startup
adw_id = make_adw_id()
logger = setup_logger(adw_id, "cape_tui")

# Log TUI events and errors to agents/{adw_id}/cape_tui/execution.log
```

### Database Schema

#### `/Users/bponghneng/git/cape/cape/migrations/001_create_cape_issues_tables.sql`
**Relevant Tables**:

**cape_issues**:
- `id` (SERIAL PRIMARY KEY)
- `description` (TEXT NOT NULL)
- `status` (TEXT DEFAULT 'pending', CHECK IN 'pending', 'started', 'completed')
- `created_at` (TIMESTAMPTZ DEFAULT now())
- `updated_at` (TIMESTAMPTZ DEFAULT now())
- Index: `idx_cape_issues_status` on status column

**cape_comments**:
- `id` (SERIAL PRIMARY KEY)
- `issue_id` (INT NOT NULL REFERENCES cape_issues(id) ON DELETE CASCADE)
- `comment` (TEXT NOT NULL)
- `created_at` (TIMESTAMPTZ DEFAULT now())
- Index: `idx_cape_comments_issue_id` on issue_id column

### Testing Patterns

#### `/Users/bponghneng/git/cape/cape/workflows/test_supabase_create_issue.py`
**Pattern**: Unit testing with mocked Supabase client

**Example**:
```python
@pytest.fixture
def mock_supabase_client():
    with patch('supabase_client.get_client') as mock_get_client:
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        yield mock_client

def test_create_issue_success(mock_supabase_client):
    mock_response = Mock()
    mock_response.data = [{"id": 123, "description": "Test", "status": "pending"}]
    mock_supabase_client.table.return_value.insert.return_value.execute.return_value = mock_response

    result = create_issue("Test issue")
    assert isinstance(result, CapeIssue)
```

**Usage**: Apply same mocking pattern to test new TUI functions

### New Files

#### `/Users/bponghneng/git/cape/cape/workflows/cape_tui.py`
**Purpose**: Main TUI application with all screen implementations

**Structure**:
```python
#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "textual>=0.50.0",
#     "python-dotenv>=1.0.0",
#     "pydantic>=2.0",
#     "supabase>=2.0"
# ]
# ///
"""Cape Issue Management TUI - Textual-based interface for Cape workflows."""

from textual.app import App, ComposeResult
from textual.screen import Screen, ModalScreen
from textual.widgets import Header, Footer, DataTable, TextArea, Button, Static, RichLog
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.worker import work

# Import existing workflow modules
from supabase_client import fetch_issue, create_issue, create_comment, get_client
from data_types import CapeIssue, CapeComment
from utils import make_adw_id, setup_logger
import adw_plan_build

class IssueListScreen(Screen):
    """Main screen displaying issue list in DataTable"""

class CreateIssueScreen(ModalScreen[int]):
    """Modal form for creating new issues"""

class IssueDetailScreen(Screen):
    """Screen showing issue details and comments"""

class WorkflowScreen(Screen):
    """Screen for running and monitoring workflows"""

class CapeApp(App):
    CSS_PATH = "cape_tui.tcss"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("n", "new_issue", "New Issue"),
        ("r", "refresh", "Refresh"),
    ]
```

#### `/Users/bponghneng/git/cape/cape/workflows/cape_tui.tcss`
**Purpose**: Textual CSS styling for consistent visual design

**Structure**:
```css
Screen {
    background: $surface;
}

DataTable > .datatable--header {
    background: $primary;
}

.status-pending { color: $warning; }
.status-started { color: $accent; }
.status-completed { color: $success; }

ModalScreen {
    align: center middle;
}

.log {
    height: 1fr;
    overflow-y: scroll;
    border: solid $primary;
    padding: 1;
}
```

#### `/Users/bponghneng/git/cape/cape/workflows/test_cape_tui.py`
**Purpose**: Comprehensive test suite for TUI application

**Structure**:
```python
#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pytest>=7.0",
#     "python-dotenv>=1.0.0",
#     "pydantic>=2.0",
#     "supabase>=2.0",
#     "textual>=0.50.0"
# ]
# ///
"""Test suite for Cape TUI application."""

import pytest
from unittest.mock import Mock, patch

# Unit tests for new supabase_client functions
def test_fetch_all_issues_success():
    """Test successful fetch of all issues"""

def test_fetch_comments_success():
    """Test successful fetch of issue comments"""

# Integration tests for screen navigation
def test_app_launches_with_issue_list():
    """Test app startup and initial screen"""

def test_create_issue_flow():
    """Test end-to-end issue creation workflow"""
```

## Implementation Plan

### Phase 1: Foundation
Set up the basic Textual application structure with issue list display and create functionality. This phase delivers a working MVP that allows browsing and creating issues without workflow execution.

**Deliverables**:
- Working `cape_tui.py` with uv script dependencies
- IssueListScreen with DataTable showing all issues
- CreateIssueScreen modal for new issue creation
- Basic navigation and keyboard shortcuts
- Extended supabase_client.py with `fetch_all_issues()` function

### Phase 2: Core Implementation
Add issue detail view with comments and implement the workflow execution screen with real-time progress monitoring. This phase completes the full feature set.

**Deliverables**:
- IssueDetailScreen showing full issue and comments
- WorkflowScreen with 4-stage pipeline monitoring
- Integration with adw_plan_build functions
- Background threading for non-blocking execution
- Extended supabase_client.py with `fetch_comments()` function

### Phase 3: Integration
Polish the application with styling, comprehensive error handling, testing, and documentation. This phase ensures production readiness.

**Deliverables**:
- TCSS stylesheet for consistent visual design
- Enhanced error handling and validation
- Comprehensive test suite (test_cape_tui.py)
- Documentation and usage guide
- Help screen with keyboard shortcuts

## Step by Step Tasks

### Task 1: Application Structure and Dependencies Setup

**Create the main TUI application file with proper dependencies and basic structure**

- Create `/Users/bponghneng/git/cape/cape/workflows/cape_tui.py` with uv script header
- Add script metadata: `requires-python = ">=3.12"` and dependencies: `textual>=0.50.0`, `python-dotenv>=1.0.0`, `pydantic>=2.0`, `supabase>=2.0`
- Import required Textual modules: `App`, `Screen`, `ModalScreen`, `DataTable`, `TextArea`, `Button`, `Static`, `RichLog`
- Import existing workflow modules: `supabase_client`, `data_types`, `utils`, `adw_plan_build`
- Define basic `CapeApp(App)` class with placeholder `compose()` method
- Initialize logger in `on_mount()` using `setup_logger(make_adw_id(), "cape_tui")`
- Load environment variables with `load_dotenv()`
- Verify script runs: `uv run cape_tui.py` should launch without errors

**Acceptance**: Script executes and shows empty Textual application window; log file created in `agents/{adw_id}/cape_tui/execution.log`

### Task 2: Extend Supabase Client - Fetch All Issues

**Add function to retrieve all issues for display in issue list**

- Open `/Users/bponghneng/git/cape/cape/workflows/supabase_client.py`
- Add `fetch_all_issues() -> List[CapeIssue]` function
- Query `cape_issues` table with `.select("*").order("created_at", desc=True).execute()`
- Return list of `CapeIssue` objects created with `CapeIssue.from_supabase(row)`
- Handle `APIError` by logging and raising `ValueError` with context
- Return empty list if no issues exist (not None or error)
- Follow existing code style from `fetch_issue()` and `create_issue()`

**Testing**:
- Create unit test `test_fetch_all_issues_success()` with mocked client returning 5 issues
- Create unit test `test_fetch_all_issues_empty()` with mocked empty result
- Create unit test `test_fetch_all_issues_error()` verifying `APIError` handling

**Acceptance**: Function successfully retrieves all issues ordered by creation date; all unit tests pass

### Task 3: Implement Issue List Screen

**Create the main application screen with DataTable displaying all issues**

- Define `IssueListScreen(Screen)` class in `cape_tui.py`
- Implement `compose()` method yielding: `Header(show_clock=True)`, `DataTable(id="issue_table")`, action buttons, `Footer()`
- Add DataTable columns in `on_mount()`: ID (width=6), Description (width=60), Status (width=12), Created (width=18)
- Implement `@work(exclusive=True, thread=True)` decorated `load_issues()` method
- Call `fetch_all_issues()` in background thread
- Update DataTable using `call_from_thread()` to populate rows safely
- Truncate descriptions to 60 characters with "..." suffix
- Format timestamps with `.strftime("%Y-%m-%d %H:%M")`
- Add reactive attribute `loading: reactive[bool] = reactive(False)` for state tracking
- Show loading indicator while fetching
- Display "No issues found" message if table is empty
- Add footer with keybindings: `n`=New Issue, `Enter`=View Details, `r`=Run Workflow, `q`=Quit

**Testing**:
- Visual test: Launch app with populated database, verify table displays correctly
- Visual test: Launch app with empty database, verify empty state message
- Visual test: Test keyboard navigation with arrow keys through rows

**Acceptance**: Issue list displays all issues in DataTable; keyboard navigation works; loading states properly handled

### Task 4: Implement Create Issue Screen

**Create modal dialog for new issue creation with validation**

- Define `CreateIssueScreen(ModalScreen[int])` class in `cape_tui.py`
- Implement `compose()` method yielding: `Container` with `Static` header, `TextArea(id="description")`, `Horizontal` with Save/Cancel buttons
- Add placeholder text to TextArea: "Enter issue description..."
- Implement validation in `on_button_pressed()` handler: check description is not empty after `.strip()`
- Show warning notification if validation fails: `self.notify("Description cannot be empty", severity="warning")`
- Implement `@work(exclusive=True, thread=True)` decorated `create_issue_handler()` method
- Call `create_issue(description)` in background thread
- Show loading spinner during creation
- On success: show notification with created issue ID and dismiss modal with `self.dismiss(issue_id)`
- On error: catch `ValueError` and show error notification
- Handle Cancel button and Esc key to dismiss without action: `self.dismiss(None)`

**Testing**:
- Visual test: Open modal, enter multi-line text, press Ctrl+S, verify success message
- Visual test: Try to save empty description, verify validation error shown
- Visual test: Press Cancel or Esc, verify modal closes without creating issue

**Acceptance**: Modal centers on screen; text input works; validation prevents empty issues; successful creation returns to list

### Task 5: Wire Application Navigation and State Management

**Connect screens with keyboard bindings and refresh logic**

- Update `CapeApp` class to push `IssueListScreen` in `on_mount()` method
- Add `BINDINGS` class variable with: `("q", "quit", "Quit")`, `("n", "new_issue", "New Issue")`, `("r", "refresh", "Refresh")`
- Implement `action_new_issue()` method to push `CreateIssueScreen` with callback: `self.push_screen(CreateIssueScreen(), self.on_issue_created)`
- Implement `on_issue_created(issue_id: int | None)` callback to refresh issue list if `issue_id` is not None
- Implement refresh logic to reload DataTable by calling `load_issues()` again
- Ensure smooth navigation without visual flashing or errors
- Test rapid key presses don't cause race conditions

**Testing**:
- Integration test: Launch → press `n` → create issue → verify appears in refreshed list
- Test: Press `q` exits application immediately without errors
- Test: Multiple rapid `n` key presses don't cause duplicate modals

**Acceptance**: Complete workflow from launch to issue creation works smoothly; keyboard shortcuts function as documented; list refreshes after creation

### Task 6: Extend Supabase Client - Fetch Comments

**Add function to retrieve all comments for a specific issue**

- Open `/Users/bponghneng/git/cape/cape/workflows/supabase_client.py`
- Add `fetch_comments(issue_id: int) -> List[CapeComment]` function
- Query `cape_comments` table with `.select("*").eq("issue_id", issue_id).order("created_at", desc=False).execute()`
- Return list of `CapeComment` objects created with `CapeComment(**row)`
- Handle `APIError` by logging and raising `ValueError` with context
- Return empty list if no comments exist for the issue
- Follow existing code patterns

**Testing**:
- Create unit test `test_fetch_comments_success()` with mocked client returning 3 comments
- Create unit test `test_fetch_comments_empty()` with no comments for issue
- Create unit test `test_fetch_comments_error()` verifying error handling

**Acceptance**: Function retrieves comments in chronological order; all unit tests pass

### Task 7: Implement Issue Detail Screen

**Create screen displaying full issue information and comment history**

- Define `IssueDetailScreen(Screen)` class with `__init__(self, issue_id: int)` constructor
- Implement `compose()` method yielding: `Header()`, `Vertical` container with issue details, `RichLog` or `ListView` for comments, `Footer()`
- Add reactive attributes for issue and comments data
- Implement `@work` decorated methods to fetch issue and comments in parallel
- Display full issue description (no truncation) in scrollable `Static` widget
- Show status badge with colored formatting using Rich markup
- Display creation and update timestamps formatted as "YYYY-MM-DD HH:MM"
- Render comments in chronological order with timestamps and comment text
- Show "No comments yet" message if comments list is empty
- Add loading state while fetching data
- Add footer keybindings: `Esc`=Back to List, `r`=Run Workflow
- Implement `on_key()` handler for Esc to pop screen

**Testing**:
- Visual test: Navigate to issue with 5 comments, verify all display correctly
- Visual test: Navigate to issue with no comments, verify empty state message
- Visual test: Press Esc, verify returns to list at same row selection

**Acceptance**: Full issue details display correctly; comments show in chronological order; navigation works smoothly

### Task 8: Implement Workflow Execution Screen

**Create screen to execute and monitor the 4-stage adw_plan_build workflow**

- Define `WorkflowScreen(Screen)` class with `__init__(self, issue_id: int)` constructor
- Generate unique `adw_id` using `make_adw_id()` and create logger with `setup_logger(adw_id, "tui_workflow")`
- Implement `compose()` method yielding: `Header()`, title `Static`, progress `Static`, `RichLog` for live output, `Footer()`
- Add reactive attribute `progress: reactive[str] = reactive("Initializing...")`
- Implement `watch_progress()` method to auto-update progress Static widget
- Implement `@work(exclusive=True, thread=True)` decorated `run_workflow()` method
- Execute workflow stages sequentially in background thread:
  1. `fetch_issue(issue_id)` - update progress "Fetching issue..."
  2. `classify_issue(issue, adw_id, logger)` - update progress "Classifying issue..."
  3. `build_plan(issue, command, adw_id, logger)` - update progress "Building plan..."
  4. `get_plan_file(output, adw_id, logger)` - update progress "Finding plan file..."
  5. `implement_plan(plan_file, adw_id, logger)` - update progress "Implementing solution..."
- Use `call_from_thread()` to update progress from background thread
- Capture logger output and display in RichLog widget (create custom logging handler)
- Handle errors gracefully: catch exceptions, log, show error message in UI, don't crash
- Show success message "✅ Workflow completed successfully!" on completion
- Show error message "❌ Failed: {error}" on failure
- Add footer keybinding: `Esc`=Back (enabled only after workflow completes)

**Testing**:
- Integration test: Mock all workflow functions, verify stages execute in order
- Test: Invalid issue ID shows error message in UI
- Test: Workflow failure displays error without crashing app
- Visual test: Watch progress indicators update in real-time during execution

**Acceptance**: Workflow executes all 4 stages; progress updates in real-time; log output visible; errors handled gracefully; UI remains responsive

### Task 9: Integrate Workflow Execution from Issue List

**Add workflow trigger capability from issue list with proper state handling**

- Add key binding to `IssueListScreen`: `("r", "run_workflow", "Run Workflow")`
- Implement `action_run_workflow()` method in `IssueListScreen`
- Get selected row from DataTable using `self.query_one(DataTable).cursor_row`
- Validate a row is selected; if not, show warning notification: "No issue selected"
- Extract issue ID from selected row metadata
- Push `WorkflowScreen` with issue ID: `self.app.push_screen(WorkflowScreen(issue_id), self.on_workflow_complete)`
- Implement `on_workflow_complete()` callback to refresh issue list (status may have updated)
- Verify workflow screen receives correct issue data
- Add similar workflow trigger to `IssueDetailScreen` for consistency

**Testing**:
- Integration test: Select issue row → press `r` → verify workflow screen opens with correct issue
- Test: Press `r` with no selection shows error notification
- Test: Return from workflow screen refreshes issue list
- Visual test: Issue status changes visible in refreshed list after workflow

**Acceptance**: Workflow triggers from both list and detail screens; selection validation works; list refreshes after workflow completion

### Task 10: Create TCSS Stylesheet for Visual Design

**Implement consistent styling across all screens using Textual CSS**

- Create `/Users/bponghneng/git/cape/cape/workflows/cape_tui.tcss` file
- Define base screen styling: background color, padding
- Style DataTable: header background ($primary), row hover effects, zebra striping
- Define status badge classes: `.status-pending` (yellow), `.status-started` (blue), `.status-completed` (green)
- Style modal screens: centered alignment, border, shadow/opacity for overlay effect
- Style footer: consistent layout, readable key binding format
- Style RichLog widget: border, padding, scrollbar styling
- Define dark theme colors optimized for terminal readability
- Add `CSS_PATH = "cape_tui.tcss"` to `CapeApp` class variable
- Apply status classes to issue status displays in list and detail screens

**Testing**:
- Visual inspection: Launch app, verify all screens follow consistent color scheme
- Test: Status badges display correct colors for each status value
- Test: Modal dialogs center properly and show visual overlay
- Test: Styling works in multiple terminal emulators (Terminal.app, iTerm2)

**Acceptance**: All screens have consistent visual design; status colors correctly applied; dark theme readable in terminal

### Task 11: Enhance Error Handling and Input Validation

**Add comprehensive error handling, validation, and user feedback throughout the application**

- Wrap all Supabase operations in try/except blocks with user-friendly error messages
- Add error handling for network failures with retry suggestion
- Implement empty state messages for empty issue list: "No issues found. Press 'n' to create one."
- Add form validation to CreateIssueScreen: minimum length (10 chars), maximum length (10000 chars)
- Show inline validation errors in modal with specific messages
- Implement app-level exception handler: override `CapeApp.on_exception()` method
- Log all errors to file for debugging while showing simple messages to users
- Use `notify()` method for toast notifications: success (green), info (blue), warning (yellow), error (red)
- Add validation on startup: check required environment variables, show clear error if missing
- Handle gracefully when Supabase is unreachable: don't crash, show connection error

**Testing**:
- Test: Launch with missing `.env` file, verify helpful error message
- Test: Disconnect network, trigger data fetch, verify connection error shown
- Test: Create issue with description < 10 chars, verify validation error
- Test: Create issue with description > 10000 chars, verify validation error
- Test: Check log file contains all errors with full stack traces

**Acceptance**: All errors display user-friendly messages; validation prevents invalid input; app never crashes; all errors logged to file

### Task 12: Create Comprehensive Test Suite

**Build robust test suite covering unit tests, integration tests, and UI tests**

- Create `/Users/bponghneng/git/cape/cape/workflows/test_cape_tui.py` with uv script header
- Add dependencies: `pytest>=7.0`, `textual>=0.50.0`, plus existing dependencies

**Unit Tests**:
- `test_fetch_all_issues_success()` - Mock client returns multiple issues
- `test_fetch_all_issues_empty()` - Mock client returns empty list
- `test_fetch_all_issues_error()` - Mock APIError handling
- `test_fetch_comments_success()` - Mock client returns multiple comments
- `test_fetch_comments_empty()` - Mock client returns empty list
- `test_fetch_comments_error()` - Mock APIError handling

**Integration Tests** (using Textual's `App.run_test()`):
- `test_app_launches_with_issue_list()` - App startup and initial screen
- `test_create_issue_flow()` - End-to-end issue creation workflow
- `test_navigation_to_detail_screen()` - Navigate from list to detail
- `test_workflow_execution_mock()` - Workflow execution with mocked stages

**Mock Strategy**:
- Use `unittest.mock.patch` for Supabase client operations
- Mock `adw_plan_build` functions for workflow tests
- Create pytest fixtures for common test data: sample issues, comments

**Coverage Goals**:
- Run: `pytest cape/workflows/test_cape_tui.py -v --cov=cape_tui --cov-report=term-missing`
- Target: > 80% coverage for new code
- All tests pass independently and together
- Tests complete in < 5 seconds (use headless mode)

**Acceptance**: All tests pass; coverage > 80%; tests run quickly; no database dependencies in tests

### Task 13: Create Documentation and Help Screen

**Document the application with README, inline help, and comprehensive docstrings**

- Add section to `/Users/bponghneng/git/cape/README.md` titled "## Cape TUI - Terminal User Interface"
- Document installation: prerequisites, environment setup, dependencies
- Document launching: `cd cape/workflows && uv run cape_tui.py`
- List all keyboard shortcuts organized by screen
- Explain workflow stages and what each does
- Add troubleshooting section: common errors and solutions
- Create inline help screen: `HelpScreen(ModalScreen)` accessible with `?` key
- Display all keybindings, screen descriptions, workflow stage explanations in help screen
- Add docstrings to all classes using Google-style format
- Add docstrings to all public methods with parameter descriptions and return types
- Include usage examples in docstrings where helpful

**Documentation Structure**:
```markdown
## Cape TUI - Terminal User Interface

### Quick Start
```bash
cd cape/workflows
uv run cape_tui.py
```

### Keyboard Shortcuts
- **Issue List**: `n`=New Issue, `Enter`=View Details, `r`=Run Workflow, `q`=Quit
- **Create Issue**: `Ctrl+S`=Save, `Esc`=Cancel
- **Issue Detail**: `r`=Run Workflow, `Esc`=Back
- **Workflow Monitor**: `Esc`=Back (after completion)
- **Global**: `?`=Help

### Workflow Stages
1. **Fetch**: Retrieve issue from database
2. **Classify**: Determine issue type (feature/bug/chore)
3. **Plan**: Generate implementation plan
4. **Implement**: Execute implementation

### Troubleshooting
...
```

**Testing**:
- Test: Press `?` from any screen shows help modal
- Visual: Help screen displays all keybindings correctly
- Review: README renders properly on GitHub
- Verify: All documented shortcuts actually work

**Acceptance**: Complete documentation in README; inline help accessible and accurate; all classes and methods have docstrings

### Task 14: Final Integration Testing and Validation

**Execute comprehensive validation to ensure production readiness**

Run all validation commands in sequence to verify zero regressions:

- Verify TUI launches successfully: `cd cape/workflows && uv run cape_tui.py` (manual test, press `q` to quit)
- Run all unit tests: `pytest cape/workflows/test_cape_tui.py -v`
- Run all workflow tests: `pytest cape/workflows/test_*.py -v`
- Verify test coverage: `pytest cape/workflows/ --cov=cape_tui --cov-report=term-missing`
- Test with empty database: Delete all issues, launch TUI, verify empty state
- Test with populated database: Seed test data, launch TUI, verify all issues display
- Test complete workflow: Create issue → run workflow → verify completion
- Test error scenarios: Invalid credentials, network failure, validation errors
- Test keyboard navigation: All shortcuts work as documented
- Test visual consistency: All screens follow style guide, colors correct
- Verify log files created: Check `agents/{adw_id}/cape_tui/execution.log` exists and contains entries
- Check documentation accuracy: Follow README instructions step-by-step

**Integration Test Scenarios**:
1. **Happy Path**: Launch → view list → create issue → view detail → run workflow → return to list
2. **Empty State**: Launch with no issues → create first issue → verify appears in list
3. **Error Handling**: Disconnect network → try to fetch issues → see connection error → reconnect → retry successfully
4. **Workflow Monitoring**: Run workflow → watch all 4 stages complete → verify success message → check log file

**Acceptance Criteria**:
- All automated tests pass with 0 failures
- All manual test scenarios complete successfully
- No errors or warnings in log files during normal operation
- Application feels responsive and stable
- Documentation is accurate and complete

## Testing Strategy

### Unit Tests

**Supabase Client Functions**:
- Test `fetch_all_issues()` with various database states (empty, populated, error)
- Test `fetch_comments()` with various comment counts (0, 1, many)
- Mock Supabase client chain: `.table().select().order().execute()`
- Verify error handling converts `APIError` to `ValueError` with context
- Verify empty results return empty lists (not None or exceptions)

**Screen Initialization**:
- Test screen classes instantiate without errors
- Test reactive attributes initialize with correct default values
- Test compose methods yield expected widget hierarchy

### Integration Tests

**Navigation Flows**:
- Test app launches and displays issue list as initial screen
- Test pressing `n` opens create issue modal
- Test creating issue closes modal and refreshes list
- Test selecting issue and pressing Enter navigates to detail screen
- Test pressing `r` on selected issue opens workflow screen
- Test workflow completion returns to list

**Data Flows**:
- Test issue created via UI appears in database
- Test issue list reflects current database state after refresh
- Test comments display matches database query results
- Test workflow updates issue status in database

**Error Scenarios**:
- Test missing environment variables show clear error on startup
- Test database connection failure shows error message (doesn't crash)
- Test invalid issue ID in workflow shows error (doesn't crash)
- Test empty description validation prevents issue creation

### Edge Cases

**Empty States**:
- Empty database (no issues) - shows "No issues found" message
- Issue with no comments - shows "No comments yet" message
- Workflow screen with invalid issue ID - shows error message

**Long Content**:
- Issue description > 1000 characters - scrollable, no truncation in detail view
- Issue list with 100+ issues - table performance remains acceptable, scrolling works
- Comment with very long text - wraps properly, scrollable

**Concurrent Operations**:
- Multiple rapid key presses don't cause duplicate modals or race conditions
- Background workflow doesn't block UI interactions
- Refresh during background data load doesn't cause errors

**Keyboard Navigation**:
- Arrow keys navigate DataTable rows correctly
- Tab/Shift+Tab move focus between widgets
- Enter selects highlighted row
- Esc closes modals and returns to previous screen
- All documented shortcuts work without conflicts

**Error Recovery**:
- Network failure during fetch - shows error, allows retry
- Workflow stage failure - displays error message, doesn't crash app
- Invalid user input - shows validation error, allows correction
- Database constraint violation - shows user-friendly error message

## Acceptance Criteria

- [ ] TUI application launches successfully with `uv run cape_tui.py`
- [ ] Issue list displays all Cape issues from Supabase in DataTable format
- [ ] Keyboard navigation works: arrow keys, Enter, Esc, n, r, q
- [ ] New issues can be created via modal form with validation
- [ ] Issue detail screen shows complete issue information and comments
- [ ] Workflow execution runs in background without blocking UI
- [ ] Workflow progress updates in real-time through all 4 stages
- [ ] All errors handled gracefully with user-friendly messages
- [ ] No unhandled exceptions cause application crashes
- [ ] Application logging works: dual-sink (console + file)
- [ ] All automated tests pass with > 80% code coverage
- [ ] Documentation complete: README section, inline help, docstrings
- [ ] Visual styling consistent across all screens with TCSS
- [ ] Application feels responsive: operations complete in < 1 second (excluding workflows)
- [ ] Workflow execution completes successfully for test issues

## Validation Commands

Execute every command to validate the feature works correctly with zero regressions.

- `cd /Users/bponghneng/git/cape/cape/workflows` - Change to workflows directory
- `uv run cape_tui.py` - Launch TUI application (manual testing, press 'q' to quit)
- `pytest test_cape_tui.py -v` - Run all TUI unit and integration tests
- `pytest test_*.py -v` - Run all workflow tests to ensure no regressions
- `pytest --cov=cape_tui --cov-report=term-missing` - Verify test coverage > 80%
- `python -m py_compile cape_tui.py` - Verify Python syntax is valid
- `cd ../..` - Return to repository root

**Manual Validation Checklist**:
1. Launch app with populated database, verify issue list displays
2. Press `n`, create new issue, verify it appears in refreshed list
3. Select issue, press Enter, verify detail screen shows full information
4. From detail screen, press `r`, verify workflow executes all 4 stages
5. Verify workflow log output displays in real-time
6. After workflow completes, press Esc, verify returns to list
7. Press `?`, verify help screen displays keyboard shortcuts
8. Press `q`, verify application exits cleanly
9. Check log file exists: `agents/{adw_id}/cape_tui/execution.log`
10. Review log file for any errors or warnings during execution

## Notes

### Technical Architecture Decisions

**Single-File Application**: The TUI is implemented as a single Python file (`cape_tui.py`) with approximately 500-800 lines of code. This simplifies distribution and aligns with the existing uv script pattern in the codebase. If the application grows beyond 1000 lines, consider refactoring into a module structure (`cape_tui/app.py`, `cape_tui/screens.py`, `cape_tui/widgets.py`).

**Background Threading**: Uses Textual's `@work(exclusive=True, thread=True)` decorator for all long-running operations (database fetches, workflow execution). This prevents UI freezing while maintaining simplicity (no explicit thread management required). The `exclusive=True` parameter ensures only one background operation runs at a time, preventing race conditions.

**State Management**: Leverages Textual's reactive attribute system (`reactive[T]`) for automatic UI updates when state changes. This eliminates the need for manual UI refresh calls and follows the framework's declarative programming model.

**Logger Integration**: The TUI integrates with the existing workflow logging system (`utils.setup_logger()`) for consistency. Workflow execution logs are written to `agents/{adw_id}/tui_workflow/execution.log` and optionally displayed in the UI's RichLog widget via a custom logging handler.

### Future Enhancements (Out of Scope)

**Phase 4 Potential Features**:
1. **Issue Editing**: Modify existing issue descriptions and status via TUI
2. **Comment Creation**: Add comments to issues directly from detail screen
3. **Search and Filter**: Text search across issue descriptions, status filter dropdown
4. **Pagination**: Load issues in batches of 50 for performance with large datasets
5. **Custom Workflows**: Configure alternative workflow pipelines via config file
6. **Export Functionality**: Export issues and workflow logs to Markdown or JSON
7. **Real-time Updates**: WebSocket integration for live issue list updates
8. **Keyboard Customization**: User-defined keyboard shortcuts via config file
9. **Multi-column Sorting**: Sort DataTable by multiple columns (e.g., status then date)
10. **Workflow Templates**: Pre-defined workflow configurations for common scenarios

**Design for Extensibility**:
- Screen classes are independent and can be easily extended with new functionality
- Data models (CapeIssue, CapeComment) support additional fields without breaking changes
- Workflow integration uses function imports (not subprocess calls), allowing custom pipelines
- TCSS styling separates presentation from logic, enabling visual customization

### Environment Setup Notes

**Required Environment Variables** (in `.env` file):
```bash
SUPABASE_URL=https://[project-id].supabase.co
SUPABASE_SERVICE_ROLE_KEY=[service-role-jwt-token]
```

**Optional Environment Variables**:
- `ANTHROPIC_API_KEY` - Required for workflow execution (Claude Code)
- `CLAUDE_CODE_PATH` - Path to Claude CLI (default: `claude`)

**Development Tools**:
- **Textual DevTools**: Run `textual run --dev cape_tui.py` for live debugging console
- **Console Logging**: Use `textual console` in separate terminal for real-time log streaming
- **CSS Hot Reload**: Textual automatically reloads `.tcss` files on change

### Performance Considerations

**Expected Scale**:
- Issues: 10-100 initially, up to 1000 long-term
- Comments per issue: 5-20 average, up to 100 maximum
- Workflow execution: 2-10 minutes per run

**Performance Optimizations Applied**:
- DataTable widget uses virtualization (renders only visible rows)
- Comments loaded lazily (only when detail screen opens)
- Issue list cached in memory (refreshed on explicit user action)
- Background threading prevents UI blocking during data fetches

**Future Optimization Opportunities**:
- Implement pagination if issue count exceeds 500
- Add local caching with TTL to reduce database queries
- Stream workflow logs incrementally rather than loading all at once
- Use Supabase real-time subscriptions for automatic list updates

### Testing Philosophy

**Three-Tier Testing Approach**:

1. **Unit Tests** (Fast, Isolated) - Test individual functions with mocked dependencies
   - Run on every code change
   - Target: < 1 second execution time
   - Coverage: All supabase_client functions, screen initialization

2. **Integration Tests** (Medium Speed) - Test navigation flows and data interactions
   - Run before commits
   - Target: < 5 seconds execution time
   - Coverage: Screen navigation, workflow execution, error handling

3. **Manual Visual Tests** (Slow, Comprehensive) - Test user experience and styling
   - Run before releases
   - Target: 10-15 minutes per full test cycle
   - Coverage: UI aesthetics, terminal compatibility, edge cases

**Test Data Management**:
- Use pytest fixtures for consistent test data (sample issues, comments)
- Mock Supabase client for all automated tests (no database dependencies)
- Create seed script for manual testing: `uv run seed_test_data.py`

### Deployment and Distribution

**Single-Command Launch**:
```bash
cd cape/workflows && uv run cape_tui.py
```

**No Installation Required**: The uv script header automatically manages dependencies. Users need only:
1. Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. Clone repository
3. Create `.env` file with Supabase credentials
4. Run the command above

**Version Management**:
- Version number in app header: "Cape TUI v1.0.0"
- Changelog maintained in README
- Consider semantic versioning for future releases

**Future Distribution Options**:
- Standalone executable via PyInstaller (eliminates Python dependency)
- Homebrew formula for macOS users
- Docker container for isolated execution environment