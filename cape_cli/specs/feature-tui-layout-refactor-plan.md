# Feature: TUI Layout and Component Updates

## Description

This feature refactors the Cape TUI to improve layout consistency and component reusability across issue management screens. The primary goals are to eliminate code duplication by creating a reusable IssueForm composite widget, improve the IssueDetailScreen user experience with full-screen scrolling, and conditionally hide comments for pending issues. This refactoring establishes modern component patterns that will accelerate future TUI development while immediately improving maintainability.

The current implementation has ~145 lines of duplicated form logic between CreateIssueScreen and EditDescriptionScreen. Additionally, the IssueDetailScreen uses a constrained RichLog widget for comments, which prevents natural scrolling through the full issue context. By introducing composite widgets and VerticalScroll containers, we'll create a more intuitive and maintainable architecture.

## User Story

As a Cape CLI user
I want a consistent and intuitive interface for creating, editing, and viewing issues
So that I can efficiently manage my workflow without learning different layouts for similar operations

## Problem Statement

The current TUI implementation suffers from three key issues:

1. **Code Duplication**: CreateIssueScreen and EditDescriptionScreen contain nearly identical form implementations (~145 lines duplicated), including validation logic, TextArea configuration, and button handling. Any change to form behavior requires updating both screens, increasing maintenance burden and risk of inconsistencies.

2. **Constrained Scrolling**: IssueDetailScreen uses a fixed-height RichLog widget for comments, creating a scrollable region within the screen. This prevents users from naturally scrolling through the entire issue context (description + comments) as a cohesive unit, especially problematic for issues with long descriptions and many comments.

3. **Information Overload**: Pending issues display an empty comments section before workflow execution begins, creating visual clutter and confusion. Users expect comments to appear only when the workflow starts generating output.

These issues impact maintainability, user experience, and code quality, making future enhancements more costly and error-prone.

## Solution Statement

We will address these problems through a three-phase refactoring approach:

**Phase 1: Reusable Components** - Create an `IssueForm` composite widget that encapsulates all form logic, validation, and layout. This widget will use Textual's message-based communication pattern, allowing parent screens to handle database operations while the form manages user input. This eliminates duplication and establishes a pattern for future reusable components.

**Phase 2: Full-Screen Scrolling** - Restructure IssueDetailScreen to use a `VerticalScroll` container wrapping both issue description and comments. Comments will render as individual `Static` widgets instead of a constrained RichLog, enabling natural top-to-bottom scrolling. The existing auto-refresh mechanism will be preserved to maintain real-time updates for started issues.

**Phase 3: Conditional Visibility** - Implement reactive state management to hide the comments section when issue status is "pending" and reveal it when status changes to "started" or "completed". This reduces visual clutter and provides a clearer mental model of workflow progression.

**Technical Approach**: We'll use Textual's composite widget pattern with custom message classes for parent-child communication, reactive attributes for state management, and VerticalScroll containers with `height: auto` for content-based sizing. All changes are purely frontend refactoring with no database or API modifications required.

## Relevant Files

### Core TUI Implementation
- **`src/cape_cli/tui.py`** (666 lines) - Main TUI application file containing all screen implementations
  - `CreateIssueScreen` (lines 138-205) - Currently has inline form implementation; will be refactored to use IssueForm widget
  - `EditDescriptionScreen` (lines 207-280) - Currently has inline form implementation; will be refactored to use IssueForm widget
  - `IssueDetailScreen` (lines 282-465) - Currently uses RichLog for comments; will be restructured with VerticalScroll and conditional visibility
  - Existing patterns to preserve: `@work(thread=True)` for background operations, reactive attributes, auto-refresh timer mechanism

### Styling
- **`src/cape_cli/cape_tui.tcss`** - Textual CSS stylesheet for TUI layout and theming
  - Current modal styles for CreateIssueScreen and EditDescriptionScreen (will adapt for IssueForm)
  - IssueDetailScreen styles for issue content and comments log (will update for VerticalScroll pattern)
  - Color scheme and spacing conventions to maintain consistency

### Data Models (Read-only reference)
- **`src/cape_cli/models.py`** - Pydantic models for data validation
  - `CapeIssue` - Issue model with status field ("pending", "started", "completed")
  - `CapeComment` - Comment model with created_at timestamp and text
  - Used for type hints and validation; no changes required

### Database Layer (Read-only reference)
- **`src/cape_cli/database.py`** - Supabase database operations
  - `create_issue(description: str)` - Used by CreateIssueScreen
  - `update_issue_description(issue_id: int, description: str)` - Used by EditDescriptionScreen
  - `fetch_issue(issue_id: int)` - Used by IssueDetailScreen
  - `fetch_comments(issue_id: int)` - Used by IssueDetailScreen
  - No changes required; existing functions will continue to work

### Testing
- **`tests/test_tui.py`** - Existing TUI tests
  - Current tests for auto-refresh functionality (lines 1-192)
  - Test patterns to follow: mocking database calls, using Textual pilot for interactions
  - Will add integration tests for refactored screens

#### New Files

- **`tests/test_tui_components.py`** - Unit tests for new composite widgets
  - IssueForm widget validation tests
  - IssueForm message passing tests
  - CommentsSection widget tests
  - Integration tests for refactored screens

## Implementation Plan

### Phase 1: Foundation - Reusable Components

**Objective**: Create the foundational IssueForm composite widget and prepare IssueDetailScreen layout structure. These components establish patterns that will be used throughout the remaining implementation.

**Key Deliverables**:
- IssueForm widget with validation and custom messages
- IssueDetailScreen restructured with VerticalScroll
- Unit tests for core widget functionality

**Why This Phase Matters**: By building reusable components first, we avoid rework later. The IssueForm widget must be stable before refactoring screens that depend on it, and the IssueDetailScreen layout must be restructured before implementing conditional visibility.

### Phase 2: Core Implementation - Screen Refactoring

**Objective**: Replace inline form implementations with the reusable IssueForm widget and implement conditional comments visibility. This phase delivers the primary user-facing value of the feature.

**Key Deliverables**:
- CreateIssueScreen using IssueForm (~40 lines removed, ~15 added)
- EditDescriptionScreen using IssueForm (~40 lines removed, ~15 added)
- Conditional comments visibility based on issue status
- Updated CSS for new component structure

**Why This Phase Matters**: This is where code duplication is eliminated and UX improvements become visible to users. Each screen refactor is independent, allowing incremental testing and validation.

### Phase 3: Integration - Testing and Validation

**Objective**: Ensure all components work together correctly with comprehensive testing and validation. This phase confirms that refactoring hasn't introduced regressions and that new functionality meets acceptance criteria.

**Key Deliverables**:
- Comprehensive unit test suite (≥90% coverage for new code)
- Integration tests for complete workflows
- Manual QA validation checklist
- Documentation updates

**Why This Phase Matters**: TUI applications are challenging to test automatically, so a combination of unit tests, integration tests, and manual QA is essential to catch regressions before deployment.

## Step by Step Tasks

IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create IssueForm Composite Widget

**Objective**: Build the reusable IssueForm widget that will eliminate code duplication between CreateIssueScreen and EditDescriptionScreen.

**Implementation Details**:
- Create `IssueForm` class extending `Widget` in `src/cape_cli/tui.py`
- Implement `compose()` method yielding:
  - Static header with dynamic title based on mode ("Create New Issue" or "Edit Issue #123")
  - TextArea with markdown language support, configured with placeholder text
  - Horizontal button row with "Save" (success variant) and "Cancel" (error variant) buttons
- Define constructor parameters:
  - `description: Optional[str] = None` - For pre-populating content in edit mode
  - `issue_id: Optional[int] = None` - For customizing title in edit mode
  - `mode: Literal["create", "edit"] = "create"` - Controls title display
- Implement validation logic in `validate_and_submit()` method:
  - Check: Description not empty or placeholder text
  - Check: Description ≥ 10 characters
  - Check: Description ≤ 10,000 characters
  - Show error notifications using `self.notify(message, severity="warning")`
- Define custom message classes as inner classes:
  ```python
  class SaveRequested(Message):
      def __init__(self, description: str):
          super().__init__()
          self.description = description

  class CancelRequested(Message):
      pass
  ```
- Implement button handlers using `@on(Button.Pressed)` decorator
- Add keyboard bindings: Ctrl+S triggers save, Escape triggers cancel
- Implement `on_mount()` to set TextArea content and focus
- Add DEFAULT_CSS with self-contained styling for consistent appearance

**Testing Requirements**:
- Unit test: Widget instantiation with no parameters (create mode)
- Unit test: Widget instantiation with pre-populated description (edit mode)
- Unit test: Validation rejects empty description
- Unit test: Validation rejects description < 10 characters
- Unit test: Validation rejects description > 10,000 characters
- Unit test: SaveRequested message posted with valid description
- Unit test: CancelRequested message posted on cancel button
- Unit test: Keyboard shortcuts (Ctrl+S, Escape) trigger appropriate actions

**Acceptance Criteria**:
- ✅ IssueForm widget renders correctly in isolation
- ✅ All validation rules enforced consistently
- ✅ Custom messages posted to parent screens
- ✅ Keyboard shortcuts work as expected
- ✅ TextArea receives focus on mount
- ✅ Unit tests pass with ≥90% coverage

**Estimated Effort**: 1-2 days

---

### Step 2: Refactor IssueDetailScreen Layout Structure

**Objective**: Restructure IssueDetailScreen to use VerticalScroll for full-screen scrolling and prepare for conditional comments visibility.

**Implementation Details**:
- Remove `RichLog(id="comments-log")` widget completely from `compose()` method
- Create `CommentsSection` composite widget class:
  - Extends `Widget` base class
  - Constructor accepts `comments: List[CapeComment]` parameter
  - `compose()` yields Static header "Comments" and Vertical container
  - Renders each comment as individual Static widget with:
    - Timestamp in dim style: `[dim]{timestamp}[/dim]`
    - Comment text in normal style
    - Border separator between comments
  - Implements `update_comments(comments: List[CapeComment])` method to refresh display
- Update IssueDetailScreen `compose()` method:
  - Wrap content in `VerticalScroll(id="detail-scroll")` container
  - Inside VerticalScroll, yield:
    - Static for issue content (id="issue-content")
    - CommentsSection widget (initially empty)
  - Remove separate scrollable RichLog region
- Update `_display_data()` method to call `CommentsSection.update_comments()` instead of RichLog.write()
- Preserve existing auto-refresh mechanism:
  - Keep `set_interval(10, ...)` timer logic
  - Keep `load_data(is_refresh=True)` background worker
  - Update comment comparison logic to work with CommentsSection widget
- Add reactive attribute: `show_comments: reactive[bool] = reactive(True)`
- Add CSS rules for VerticalScroll container and comment items

**Testing Requirements**:
- Unit test: Comments render as individual Static widgets
- Unit test: Full-screen scrolling works for long descriptions + many comments
- Unit test: Auto-refresh timer still fires every 10 seconds for started issues
- Unit test: CommentsSection.update_comments() properly refreshes display
- Integration test: Scroll position maintained during auto-refresh (best effort)
- Visual test: Layout reflows correctly at different terminal sizes

**Acceptance Criteria**:
- ✅ Issue description and comments share single scroll context
- ✅ Auto-refresh functionality preserved for started issues
- ✅ Comments display with proper spacing and separators
- ✅ No live workflow output window present
- ✅ Layout works correctly on 80x24 and 200x60 terminal sizes
- ✅ Tests pass with no regressions

**Estimated Effort**: 1-2 days

---

### Step 3: Refactor CreateIssueScreen to Use IssueForm

**Objective**: Replace inline form implementation in CreateIssueScreen with reusable IssueForm widget, eliminating ~40 lines of duplicated code.

**Implementation Details**:
- Update `compose()` method to yield single `IssueForm(mode="create")` widget
- Remove inline TextArea and Button widgets
- Remove `on_button_pressed()` method (no longer needed)
- Remove `action_save()` method (validation now in IssueForm)
- Implement message handlers:
  ```python
  @on(IssueForm.SaveRequested)
  def handle_save(self, message: IssueForm.SaveRequested) -> None:
      self.create_issue_handler(message.description)

  @on(IssueForm.CancelRequested)
  def handle_cancel(self) -> None:
      self.dismiss(None)
  ```
- Preserve `create_issue_handler()` background worker method unchanged
- Update keyboard bindings to delegate to IssueForm widget
- Remove TextArea query logic (no direct access to TextArea needed)
- Verify modal appearance and behavior unchanged from user perspective

**Testing Requirements**:
- Integration test: Create issue flow completes successfully with valid description
- Integration test: Validation errors displayed for invalid descriptions
- Integration test: Cancel button dismisses modal without saving
- Integration test: Ctrl+S keyboard shortcut saves issue
- Integration test: Escape keyboard shortcut cancels
- Integration test: Database `create_issue()` called with correct description

**Acceptance Criteria**:
- ✅ CreateIssueScreen uses IssueForm widget
- ✅ ~40 lines of code removed (form implementation)
- ✅ ~15 lines of code added (message handlers)
- ✅ All validation logic removed from screen
- ✅ User workflow identical to previous implementation
- ✅ Tests pass with no regressions

**Estimated Effort**: 0.5-1 day

---

### Step 4: Refactor EditDescriptionScreen to Use IssueForm

**Objective**: Replace inline form implementation in EditDescriptionScreen with reusable IssueForm widget, ensuring identical layout to CreateIssueScreen.

**Implementation Details**:
- Update `compose()` method to yield `IssueForm(description=self.current_description, issue_id=self.issue_id, mode="edit")` widget
- Remove inline TextArea and Button widgets
- Remove `on_button_pressed()` method (no longer needed)
- Remove `action_save()` method (validation now in IssueForm)
- Implement message handlers:
  ```python
  @on(IssueForm.SaveRequested)
  def handle_save(self, message: IssueForm.SaveRequested) -> None:
      self.update_description_handler(message.description)

  @on(IssueForm.CancelRequested)
  def handle_cancel(self) -> None:
      self.dismiss(False)
  ```
- Preserve `update_description_handler()` background worker method unchanged
- Verify pre-populated description displays correctly
- Remove TextArea query logic (no direct access to TextArea needed)
- Ensure title displays "Edit Issue #{issue_id}"

**Testing Requirements**:
- Integration test: Edit description flow completes successfully
- Integration test: Pre-populated description displays in TextArea
- Integration test: Validation errors displayed for invalid descriptions
- Integration test: Cancel button dismisses modal without saving
- Integration test: Ctrl+S keyboard shortcut saves changes
- Integration test: Escape keyboard shortcut cancels
- Integration test: Database `update_issue_description()` called with correct parameters

**Acceptance Criteria**:
- ✅ EditDescriptionScreen uses IssueForm widget
- ✅ ~40 lines of code removed (form implementation)
- ✅ ~15 lines of code added (message handlers)
- ✅ Layout identical to CreateIssueScreen
- ✅ Pre-populated description works correctly
- ✅ User workflow identical to previous implementation
- ✅ Tests pass with no regressions

**Estimated Effort**: 0.5-1 day

---

### Step 5: Implement Conditional Comments Visibility

**Objective**: Hide comments section when issue status is "pending" and reveal it when status changes to "started" or "completed".

**Implementation Details**:
- Add reactive attribute to IssueDetailScreen: `show_comments: reactive[bool] = reactive(True)`
- Implement watch method:
  ```python
  def watch_show_comments(self, show: bool) -> None:
      try:
          comments_section = self.query_one(CommentsSection)
          comments_section.display = show
      except NoMatches:
          pass  # Widget not yet mounted
  ```
- Update `_display_data()` method to set `show_comments` based on issue status:
  ```python
  self.show_comments = issue.status != "pending"
  ```
- Ensure comments section only updates if visible (optimization)
- Test smooth transition when status changes from "pending" to "started"
- Verify layout reflows gracefully when comments appear/disappear
- Consider adding helpful message "Comments will appear when workflow starts" for pending issues (optional enhancement)

**Testing Requirements**:
- Unit test: Comments hidden when status is "pending"
- Unit test: Comments visible when status is "started"
- Unit test: Comments visible when status is "completed"
- Unit test: Status transition from "pending" to "started" reveals comments
- Integration test: Auto-refresh maintains correct visibility state
- Visual test: Layout reflow smooth during status transitions

**Acceptance Criteria**:
- ✅ Comments section hidden for pending issues
- ✅ Comments section visible for started/completed issues
- ✅ Status transitions reveal/hide comments smoothly
- ✅ No flash of comments content during initial load
- ✅ Auto-refresh respects visibility state
- ✅ Tests pass with no regressions

**Estimated Effort**: 0.5-1 day

---

### Step 6: Update CSS Styles for New Layout

**Objective**: Update TCSS stylesheet to support new component structure, full-screen scrolling, and refined spacing/borders.

**Implementation Details**:
- Add CSS rules for IssueForm widget:
  ```tcss
  IssueForm {
      height: auto;
      border: solid $primary;
      padding: 2;
  }

  IssueForm Label {
      margin-bottom: 1;
      color: $text-muted;
  }

  IssueForm TextArea {
      height: 15;
      margin-bottom: 2;
  }

  IssueForm #button-row {
      height: auto;
  }

  IssueForm Button {
      margin: 0 1;
  }
  ```
- Add CSS rules for VerticalScroll and CommentsSection:
  ```tcss
  #detail-scroll {
      height: 1fr;
      width: 1fr;
  }

  #detail-scroll > Vertical {
      height: auto;
      padding: 2;
  }

  CommentsSection {
      height: auto;
      margin-top: 2;
  }

  .comment-item {
      padding: 1;
      border-bottom: solid $primary;
      margin-bottom: 1;
  }

  .section-header {
      text-style: bold;
      color: $primary;
      margin-bottom: 1;
  }
  ```
- Update existing modal styles if needed for IssueForm consistency
- Remove obsolete `#comments-log` styles (replaced by CommentsSection)
- Ensure color scheme consistency maintained across themes
- Test responsiveness at terminal sizes: 80x24, 120x40, 200x60

**Testing Requirements**:
- Visual test: IssueForm modal renders correctly
- Visual test: Full-screen scrolling works smoothly
- Visual test: Comments display with proper spacing and separators
- Visual test: Terminal resize maintains layout integrity
- Visual test: All status color themes (pending/started/completed) render correctly
- Visual test: No visual regressions in other screens (IssueListScreen, WorkflowScreen, HelpScreen)

**Acceptance Criteria**:
- ✅ IssueForm widget styled consistently with existing modals
- ✅ VerticalScroll container enables smooth full-screen scrolling
- ✅ CommentsSection displays with proper spacing and separators
- ✅ Layout responsive at different terminal sizes
- ✅ Color scheme consistency maintained
- ✅ No visual regressions in other screens

**Estimated Effort**: 0.5-1 day

---

### Step 7: Create Comprehensive Unit Tests

**Objective**: Develop comprehensive unit test suite for new components and refactored screens to ensure reliability and catch regressions.

**Implementation Details**:
- Create `tests/test_tui_components.py` with test classes:
  - `TestIssueForm` - 15-20 tests covering:
    - Instantiation variants (create mode, edit mode, with/without description)
    - Validation logic (empty, too short, too long, valid)
    - Message posting (SaveRequested, CancelRequested)
    - Keyboard shortcuts (Ctrl+S, Escape)
    - Focus behavior on mount
  - `TestCreateIssueScreen` - 8-10 tests covering:
    - Message handling from IssueForm
    - Database integration (mocked)
    - Error handling for database failures
    - Modal dismiss behavior
  - `TestEditDescriptionScreen` - 8-10 tests covering:
    - Message handling from IssueForm
    - Pre-population of description
    - Database integration (mocked)
    - Error handling for database failures
  - `TestIssueDetailScreen` - 12-15 tests covering:
    - Comments visibility logic based on status
    - Full-screen scrolling behavior
    - Auto-refresh timer activation/deactivation
    - Status transitions (pending → started → completed)
    - CommentsSection update behavior
- Use pytest fixtures for common setup (mock database, sample issues/comments)
- Mock database calls with `@patch` decorator: `@patch('cape_cli.database.create_issue')`
- Test async `@work` decorated methods using Textual test utilities
- Follow existing test patterns from `tests/test_tui.py`
- Target ≥90% coverage for new code, ≥80% overall

**Testing Requirements**:
- All unit tests pass with `pytest tests/test_tui_components.py -v`
- Coverage report shows ≥90% for new code: `pytest tests/test_tui_components.py --cov=cape_cli.tui --cov-report=term-missing`
- Integration tests cover complete user workflows:
  - Create issue → View issue → Edit description
  - View pending issue → Start workflow → View started issue with comments
- Manual QA checklist completed:
  - □ Create new issue with various description lengths
  - □ Edit description of pending issue
  - □ Attempt to edit non-pending issue (should show warning)
  - □ View pending issue (comments hidden)
  - □ Start workflow and verify comments appear
  - □ View started issue with auto-refresh active
  - □ Verify scroll position on long descriptions
  - □ Test all keyboard shortcuts (Ctrl+S, Escape, etc.)
  - □ Resize terminal during use
  - □ Test on macOS and Linux terminals

**Acceptance Criteria**:
- ✅ Test coverage ≥90% for new code
- ✅ Test coverage ≥80% overall
- ✅ All validation scenarios tested
- ✅ Message passing between components tested
- ✅ Reactive attribute behavior tested
- ✅ Mock database calls properly isolated
- ✅ Integration tests cover complete workflows
- ✅ Manual QA checklist 100% complete
- ✅ No P0/P1 bugs identified in testing

**Estimated Effort**: 1-2 days

---

### Step 8: Run Validation Commands

**Objective**: Execute all validation commands to ensure the feature is implemented correctly with zero regressions.

**Validation Commands**:

Execute every command to validate the feature works correctly with zero regressions.

- `cd /Users/bponghneng/git/cape/cape_cli` - Change directory to the root of the codebase
- `uv sync` - Ensure all dependencies are up to date
- `pytest tests/test_tui.py -v` - Run existing TUI tests to ensure no regressions
- `pytest tests/test_tui_components.py -v` - Run new component tests
- `pytest tests/test_tui_components.py --cov=cape_cli.tui --cov-report=term-missing` - Check test coverage
- `pytest --cov=cape_cli --cov-report=term-missing` - Check overall test coverage
- `uv run cape` - Launch TUI and perform manual smoke testing:
  - Create new issue with description
  - View created issue (should be pending, no comments shown)
  - Edit issue description
  - Run workflow (should transition to started, comments appear)
  - Verify auto-refresh updates comments
  - Test keyboard shortcuts (Ctrl+S, Escape, etc.)
  - Resize terminal to verify responsive layout

**Acceptance Criteria**:
- ✅ All test commands execute without errors
- ✅ Test coverage ≥90% for new code, ≥80% overall
- ✅ Manual smoke testing passes all scenarios
- ✅ No visual regressions in existing screens
- ✅ All keyboard shortcuts work as expected
- ✅ TUI responsive at different terminal sizes

**Estimated Effort**: 0.5 day

## Testing Strategy

### Unit Tests

**IssueForm Widget Tests**:
- Instantiation with different parameter combinations (mode, description, issue_id)
- Validation logic for description length (empty, < 10, > 10,000, valid)
- Custom message posting (SaveRequested with description, CancelRequested)
- Button click handling (Save, Cancel)
- Keyboard shortcut functionality (Ctrl+S, Escape)
- TextArea focus on mount
- DEFAULT_CSS applied correctly

**CommentsSection Widget Tests**:
- Rendering comments as individual Static widgets
- Handling empty comments list (display "No comments yet")
- Update behavior when comments change
- Display property toggling

**Screen Refactoring Tests**:
- CreateIssueScreen message handling for IssueForm.SaveRequested and CancelRequested
- EditDescriptionScreen message handling and pre-population
- IssueDetailScreen reactive `show_comments` attribute based on status
- IssueDetailScreen watch method toggling CommentsSection visibility

### Integration Tests

**Complete User Workflows**:
1. **Create Issue Workflow**:
   - User opens CreateIssueScreen
   - User enters valid description
   - User presses Ctrl+S
   - Database `create_issue()` called with description
   - Modal dismisses with issue ID
   - IssueListScreen reloads and shows new issue

2. **Edit Issue Workflow**:
   - User views pending issue in IssueDetailScreen
   - User presses 'e' to edit description
   - EditDescriptionScreen opens with pre-populated description
   - User modifies description and saves
   - Database `update_issue_description()` called
   - IssueDetailScreen reloads with updated description

3. **View Issue Status Transition Workflow**:
   - User views pending issue (comments hidden)
   - User starts workflow
   - Issue status changes to "started"
   - Comments section becomes visible
   - Auto-refresh timer activates
   - Comments update every 10 seconds

4. **Full-Screen Scrolling Workflow**:
   - User views issue with long description (> 50 lines)
   - User views issue with many comments (> 20 comments)
   - User scrolls through entire content smoothly
   - Scroll position maintained during auto-refresh

### Edge Cases

**Validation Edge Cases**:
- Description exactly 10 characters (minimum valid)
- Description exactly 10,000 characters (maximum valid)
- Description with only whitespace characters
- Description equal to placeholder text

**UI Edge Cases**:
- Terminal resize during issue viewing
- Very small terminal (80x24) with long description
- Very large terminal (200x60) layout behavior
- Rapid status transitions (pending → started → completed)
- Auto-refresh during active scrolling
- Multiple rapid saves (debouncing/throttling)

**Data Edge Cases**:
- Issue with zero comments (started status)
- Issue with 100+ comments (performance)
- Comments with very long text (word wrapping)
- Comments with markdown formatting
- Comments with special characters

**Error Handling Edge Cases**:
- Database connection failure during save
- Database timeout during comment fetch
- Invalid issue ID in EditDescriptionScreen
- Race condition: issue deleted while viewing
- Auto-refresh error handling (network failure)

## Acceptance Criteria

1. ✅ **Reusable IssueForm Widget**: A single `IssueForm` composite widget exists that encapsulates all form logic, validation, and layout. It accepts optional `description` and `issue_id` parameters for customization.

2. ✅ **Unified Issue Form Layout**: Both `CreateIssueScreen` and `EditDescriptionScreen` use the `IssueForm` widget, presenting identical layouts and validation behavior to users.

3. ✅ **Code Duplication Eliminated**: ~145 lines of duplicated form code removed. Any future changes to form behavior require editing only the `IssueForm` widget.

4. ✅ **Full-Screen Scrolling**: `IssueDetailScreen` uses a `VerticalScroll` container that allows natural scrolling through both issue description and comments as a cohesive unit.

5. ✅ **No Workflow Output Window**: `IssueDetailScreen` no longer displays a live workflow output window. Comments are the primary mechanism for workflow updates.

6. ✅ **Conditional Comments Visibility**: Comments section is hidden when issue status is "pending" and visible when status is "started" or "completed". Status transitions smoothly update visibility.

7. ✅ **Auto-Refresh Preserved**: The existing auto-refresh mechanism (10-second timer) continues to work for started issues, updating comments in real-time.

8. ✅ **Validation Consistency**: All validation rules (10-10,000 characters, non-empty) are enforced consistently across create and edit workflows.

9. ✅ **Message-Based Communication**: `IssueForm` uses custom `SaveRequested` and `CancelRequested` messages for parent-child communication, avoiding tight coupling.

10. ✅ **Keyboard Shortcuts Preserved**: All existing keyboard shortcuts (Ctrl+S for save, Escape for cancel, 'e' for edit, etc.) continue to work as expected.

11. ✅ **Responsive Layout**: TUI layout works correctly at terminal sizes ranging from 80x24 to 200x60, with graceful reflow during resize.

12. ✅ **Test Coverage**: Unit test coverage ≥90% for new code, ≥80% overall. Integration tests cover complete user workflows.

13. ✅ **No Regressions**: All existing tests pass. Manual QA confirms no regressions in IssueListScreen, WorkflowScreen, HelpScreen, or database operations.

14. ✅ **Visual Consistency**: CSS styling maintains color scheme and spacing conventions. New components look consistent with existing TUI elements.

15. ✅ **Performance**: Scrolling remains smooth with 100+ comments. Auto-refresh does not cause noticeable UI lag.

## Validation Commands

Execute every command to validate the feature works correctly with zero regressions.

- `cd /Users/bponghneng/git/cape/cape_cli` - Change directory to the root of the codebase
- `uv sync` - Ensure all dependencies are up to date
- `pytest tests/test_tui.py -v` - Run existing TUI tests to ensure no regressions
- `pytest tests/test_tui_components.py -v` - Run new component tests
- `pytest tests/test_tui_components.py --cov=cape_cli.tui --cov-report=term-missing` - Check test coverage for new components
- `pytest --cov=cape_cli --cov-report=term-missing` - Check overall test coverage across codebase
- `uv run cape` - Launch TUI for manual smoke testing (see manual QA checklist below)

**Manual QA Checklist**:
- □ Create new issue with description < 10 characters (should show validation error)
- □ Create new issue with description > 10,000 characters (should show validation error)
- □ Create new issue with valid description (should succeed)
- □ View created issue (status: pending, comments section hidden)
- □ Press 'e' to edit description (should open EditDescriptionScreen with pre-populated text)
- □ Edit description and press Ctrl+S (should save and return to detail screen)
- □ Edit description and press Escape (should cancel and return without saving)
- □ Press 'r' to run workflow (should transition to started status)
- □ Verify comments section appears after status changes to started
- □ Verify auto-refresh updates comments every 10 seconds
- □ Scroll through long description and many comments (should be smooth full-screen scrolling)
- □ Resize terminal from 80x24 to 200x60 (layout should reflow gracefully)
- □ Test on macOS terminal (default Terminal.app or iTerm2)
- □ Test on Linux terminal (if available)

## Notes

### Future Enhancements (Not in Scope)

The following enhancements were considered but are **not included** in this implementation to maintain MVP scope:

1. **Comment Editing**: Allow users to edit or delete comments after posting
2. **Comment Pagination**: Load comments in batches (e.g., 50 at a time) for issues with 500+ comments
3. **Comment Reactions**: Add emoji reactions to comments
4. **Rich Text Preview**: Markdown preview pane for issue descriptions while editing
5. **Form Templates**: Pre-populate form with templates for common issue types
6. **Validation Hints**: Real-time character count display (e.g., "125/10,000 characters")
7. **Keyboard Shortcuts Help**: Inline tooltips or help overlay for keyboard shortcuts
8. **Scroll Position Preservation**: Advanced scroll position tracking during auto-refresh (currently best-effort)

These features should be considered for future iterations once the foundational refactoring is stable and validated by users.

### Architectural Decisions

**Why Composite Widgets Over Inline Composition?**
- **Maintainability**: Future form changes require editing only one file
- **Testability**: Widgets can be tested in isolation without screen context
- **Reusability**: IssueForm can be used in future screens (e.g., bulk issue creation)
- **Trade-off**: Slightly more complex but significantly better long-term

**Why VerticalScroll Over RichLog for Comments?**
- **Natural UX**: Users expect full-screen scrolling for reading content
- **Flexibility**: Individual Static widgets allow richer formatting options
- **Consistency**: Matches common TUI patterns (man pages, less, etc.)
- **Trade-off**: Slightly higher memory usage but negligible for typical use cases

**Why Reactive Attributes Over Manual State Tracking?**
- **Framework Integration**: Idiomatic Textual pattern with watch methods
- **Automatic Updates**: UI updates automatically when state changes
- **Reduced Bugs**: Less opportunity for state synchronization errors
- **Trade-off**: Slightly "magical" but integrates seamlessly with Textual

**Why Custom Messages Over Direct Method Calls?**
- **Loose Coupling**: Parent screens don't need to know IssueForm internals
- **Reusability**: IssueForm can be used in different parent contexts
- **Event Handling**: Leverages Textual's event system for consistency
- **Trade-off**: More boilerplate but cleaner separation of concerns

### Performance Considerations

**VerticalScroll with Many Comments**:
- Tested with 100 comments: smooth scrolling, no lag
- 500+ comments may show degradation on slow terminals
- Mitigation: Consider pagination in future iteration if needed

**Auto-Refresh Impact**:
- 10-second interval is conservative (low server load)
- Only updates UI if comments actually changed (optimization)
- Runs in background thread (no UI blocking)

**Memory Usage**:
- Individual Static widgets per comment increases memory vs RichLog
- Estimated impact: ~100 bytes per comment = 10KB for 100 comments
- Acceptable trade-off for improved UX

### Implementation Patterns for Future Development

**Creating New Composite Widgets**:
```python
class MyWidget(Widget):
    """Reusable widget with custom messages."""

    DEFAULT_CSS = """
    MyWidget {
        # Self-contained styling
    }
    """

    class CustomEvent(Message):
        """Posted when something happens."""
        pass

    def compose(self) -> ComposeResult:
        # Yield child widgets
        pass
```

**Handling Messages from Composite Widgets**:
```python
@on(MyWidget.CustomEvent)
def handle_custom_event(self, message: MyWidget.CustomEvent) -> None:
    # Process event
    pass
```

**Conditional Visibility Pattern**:
```python
show_section: reactive[bool] = reactive(True)

def watch_show_section(self, show: bool) -> None:
    widget = self.query_one("#section")
    widget.display = show
```

These patterns should be used consistently across future TUI development to maintain codebase cohesion.

### Related Issues and Context

This refactoring was motivated by user feedback about inconsistent form behavior and difficulty reading long issues. It establishes foundational patterns for upcoming features:

- **Bulk Issue Creation**: IssueForm can be reused in bulk creation screen
- **Comment Editing**: CommentsSection structure supports adding edit buttons
- **Issue Templates**: IssueForm can accept template parameter for pre-population

### Testing Philosophy

This feature follows a **test-driven development (TDD)** approach:

1. **Unit tests first**: Write tests for IssueForm widget before implementation
2. **Incremental testing**: Test each screen refactor immediately after completion
3. **Integration tests last**: Validate complete workflows after all components work
4. **Manual QA essential**: TUI applications require human validation of visual behavior

This approach ensures high confidence in refactoring while maintaining development velocity.

### Code Review Checklist

Before merging, ensure:
- □ All acceptance criteria met
- □ No code duplication between CreateIssueScreen and EditDescriptionScreen
- □ Validation logic consistent with backend (no drift)
- □ Error handling for all database operations
- □ Keyboard shortcuts documented in HelpScreen (if changed)
- □ CSS classes follow naming conventions (.section, .comment-item, etc.)
- □ Tests pass and coverage meets targets (≥90% new code, ≥80% overall)
- □ No performance regressions (test with 100+ comments)
- □ Accessibility considerations (keyboard navigation works)
- □ Documentation updated in CLAUDE.md about composite widget patterns