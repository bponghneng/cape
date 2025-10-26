# Feature: TUI Enhancements and Workflow Refinements

## Description

This feature improves the Cape TUI's usability and makes the backend workflow more robust by fixing navigation issues, adding conditional editing capabilities, and centralizing issue status management. The enhancements focus on three key areas:

1. **TUI Navigation Improvements**: Fix the Enter key navigation bug in the IssueListScreen and add alternative key bindings for better user experience
2. **Conditional Description Editing**: Add the ability to edit issue descriptions with status-based validation to prevent modifications to in-progress or completed issues
3. **Centralized Workflow Status Management**: Move issue status updates into dedicated database functions and integrate them into the workflow lifecycle

These improvements will make the TUI more intuitive and reliable while ensuring data integrity through proper status management.

## User Story

As a Cape CLI user
I want to navigate issues easily with keyboard shortcuts, edit pending issue descriptions, and have issue statuses automatically updated during workflow execution
So that I can manage my issues efficiently and track their progress accurately

## Problem Statement

The current Cape TUI has several usability and workflow issues:
- The Enter key navigation in IssueListScreen may not be working correctly, preventing users from easily viewing issue details
- Users have no way to edit issue descriptions after creation, even for pending issues that haven't been processed yet
- Issue status updates are not centralized, and the workflow doesn't automatically update issue status when execution starts or completes, making it difficult to track which issues are being processed

## Solution Statement

The solution addresses these issues through targeted enhancements:

1. **Navigation Fix**: Verify and fix the Enter key binding in IssueListScreen (lines 28-34 in tui.py), add 'd' as an alternative key binding, and update the HelpScreen documentation to reflect all available shortcuts

2. **Conditional Editing**: Add a new 'e' key binding to IssueDetailScreen that checks the issue's status before allowing description edits. Only pending issues can be edited, with a warning shown for started/completed issues. Create a new `update_issue_description()` function in database.py to persist changes

3. **Status Management**: Create an `update_issue_status()` function in database.py to centralize status updates. Modify the `execute_workflow()` function in workflow.py to call this function at two critical points: setting status to "started" when workflow begins, and "completed" when it succeeds

This approach maintains the existing architecture while adding focused improvements that enhance usability and data integrity.

## Relevant Files

### Core TUI Implementation
**src/cape-cli/tui.py** (505 lines)
- Lines 25-131: `IssueListScreen` class with keyboard bindings and issue list display
  - Line 30: BINDINGS list includes `("enter", "view_detail", "View Details")`
  - Lines 92-101: `action_view_detail()` method that handles Enter key press
  - Need to verify this binding works correctly and add 'd' as alternative
- Lines 202-289: `IssueDetailScreen` class showing issue details
  - Lines 205-208: Current BINDINGS only include "escape" and "r" for workflow
  - Need to add "e" binding for edit functionality with status check
  - Will require TextArea widget for editing interface
- Lines 404-454: `HelpScreen` modal displaying keyboard shortcuts
  - Lines 413-433: Help text markdown with keyboard shortcut documentation
  - Need to update to include 'd' for detail view and 'e' for editing

### Database Operations
**src/cape-cli/database.py** (228 lines)
- Lines 74-95: `fetch_issue()` function - retrieves issue by ID
- Lines 97-124: `fetch_all_issues()` function - retrieves all issues
- Lines 190-228: `create_issue()` function - creates new issue with validation

#### New Files
- Need to add `update_issue_description(issue_id: int, description: str) -> CapeIssue` function
  - Validate description is not empty (min 10 chars, max 10000 chars like create_issue)
  - Update the description field in cape_issues table
  - Return updated CapeIssue object

- Need to add `update_issue_status(issue_id: int, status: str) -> CapeIssue` function
  - Validate status is one of: "pending", "started", "completed"
  - Update the status field in cape_issues table
  - Update the updated_at timestamp
  - Return updated CapeIssue object

### Workflow Orchestration
**src/cape-cli/workflow.py** (274 lines)
- Lines 193-274: `execute_workflow()` function - main workflow orchestration
  - Lines 216-227: Issue fetch and validation section
  - After line 227 (after issue fetch): Add call to `update_issue_status(issue_id, "started", logger)`
  - Lines 261-273: Implementation and completion section
  - After line 267 (after successful implementation): Add call to `update_issue_status(issue_id, "completed", logger)`
  - Need to handle status update failures gracefully (log but don't halt workflow)

### Data Models
**src/cape-cli/models.py** (102 lines)
- Lines 62-87: `CapeIssue` model with status field
  - Line 67: Status is Literal["pending", "started", "completed"]
  - Already has proper validation in place

### Database Schema Reference
**README.md** (266 lines)
- Lines 229-239: `cape_issues` table schema
  - id, description, status, created_at, updated_at fields
  - Status CHECK constraint: status IN ('pending', 'started', 'completed')

## Implementation Plan

### Phase 1: Foundation - Database Status Management
Create the centralized database functions for issue status and description updates. This provides the foundation for both the TUI editing feature and workflow status tracking.

**Tasks:**
- Add `update_issue_status()` function to database.py with proper validation
- Add `update_issue_description()` function to database.py with validation
- Write unit tests for both new database functions
- Ensure both functions update the `updated_at` timestamp

### Phase 2: Core Implementation - Workflow Status Integration
Integrate status updates into the workflow lifecycle to automatically track issue progress.

**Tasks:**
- Modify `execute_workflow()` to call `update_issue_status()` when workflow starts
- Modify `execute_workflow()` to call `update_issue_status()` when workflow completes successfully
- Add error handling for status updates (log failures but don't halt workflow)
- Update workflow tests to verify status changes
- Test workflow status updates end-to-end

### Phase 3: Integration - TUI Enhancements
Add navigation fixes and editing capabilities to the TUI, completing the user-facing improvements.

**Tasks:**
- Verify and fix Enter key binding in IssueListScreen if needed
- Add 'd' key binding to IssueListScreen for viewing details
- Add 'e' key binding to IssueDetailScreen for editing
- Implement conditional editing modal that checks issue status
- Update HelpScreen documentation with new key bindings
- Manual TUI testing of all navigation and editing flows

## Step by Step Tasks

### 1. Create `update_issue_status()` function in database.py
- Add function after `create_issue()` function (around line 228)
- Accept `issue_id: int` and `status: str` parameters
- Validate status is in ["pending", "started", "completed"]
- Use Supabase client to update status and updated_at timestamp
- Return updated CapeIssue object
- Handle APIError exceptions with proper error messages
- Follow existing function patterns (e.g., `create_issue`, `fetch_issue`)

### 2. Create `update_issue_description()` function in database.py
- Add function after `update_issue_status()` function
- Accept `issue_id: int` and `description: str` parameters
- Validate description is not empty after stripping whitespace
- Validate description length (min 10 chars, max 10000 chars)
- Use Supabase client to update description and updated_at timestamp
- Return updated CapeIssue object
- Handle APIError exceptions with proper error messages
- Follow existing validation patterns from `create_issue()`

### 3. Write unit tests for `update_issue_status()`
- Add tests to tests/test_database.py
- Test successful status update to each valid status
- Test invalid status validation (e.g., "invalid_status")
- Test updating non-existent issue
- Test database error handling
- Mock Supabase client following existing test patterns

### 4. Write unit tests for `update_issue_description()`
- Add tests to tests/test_database.py
- Test successful description update
- Test empty description validation
- Test whitespace-only description validation
- Test description too short (< 10 chars)
- Test description too long (> 10000 chars)
- Test updating non-existent issue
- Mock Supabase client following existing test patterns

### 5. Integrate status updates into workflow start
- Modify `execute_workflow()` in workflow.py
- After successful issue fetch (line 227), add status update to "started"
- Use try/except to handle update failures gracefully
- Log success at DEBUG level, failures at ERROR level
- Don't halt workflow execution on status update failure
- Update existing workflow test to verify status update is called

### 6. Integrate status updates into workflow completion
- Modify `execute_workflow()` in workflow.py
- After successful implementation (line 267), add status update to "completed"
- Use try/except to handle update failures gracefully
- Log success at DEBUG level, failures at ERROR level
- Don't halt workflow execution on status update failure
- Update existing workflow test to verify status update is called

### 7. Update workflow tests for status integration
- Modify tests/test_workflow.py
- Add mock for `update_issue_status` to `test_execute_workflow_success`
- Verify status is set to "started" at workflow beginning
- Verify status is set to "completed" at workflow end
- Verify status update failures don't halt workflow
- Test that status updates are logged appropriately

### 8. Verify and enhance IssueListScreen navigation
- Review IssueListScreen BINDINGS in tui.py (line 28-34)
- Verify `action_view_detail()` method works correctly
- Add 'd' key binding to BINDINGS list: `("d", "view_detail", "View Details")`
- Ensure both Enter and 'd' trigger the same action
- Update docstring or comments to note multiple key options

### 9. Add conditional editing to IssueDetailScreen
- Add `("e", "edit_description", "Edit Description")` to BINDINGS (after line 207)
- Create `action_edit_description()` method in IssueDetailScreen class
- Check if current issue status is "pending" before allowing edit
- Show warning notification if status is not "pending"
- If pending, push EditDescriptionScreen modal
- Pass current issue to the modal for editing

### 10. Create EditDescriptionScreen modal
- Create new ModalScreen class after IssueDetailScreen (around line 290)
- Similar structure to CreateIssueScreen (lines 133-200)
- Accept issue_id and current description in __init__
- Use TextArea widget pre-filled with current description
- Add Save/Cancel buttons with Ctrl+S and Escape bindings
- On save, validate description and call `update_issue_description()`
- Return updated issue to parent screen
- Handle validation errors with user-friendly notifications

### 11. Update HelpScreen documentation
- Modify help_text in HelpScreen.compose() (lines 413-446)
- Under "Issue List" section, update Enter description to show "Enter/d"
- Add note that both keys perform the same action
- Add new "Issue Detail" shortcut: `- **e**: Edit description (pending issues only)`
- Ensure formatting is consistent with existing help text

### 12. Run validation commands
- Execute all validation commands to ensure zero regressions
- Format codebase with code formatter (if configured)
- Run linter to check code quality (if configured)
- Run type checker (if using mypy or similar)
- Run full test suite with `pytest tests/ -v`
- Manually test TUI flows:
  - Launch TUI and verify issue list displays
  - Test Enter key and 'd' key both open detail screen
  - Test 'e' key on pending issue allows editing
  - Test 'e' key on started/completed issue shows warning
  - Test editing description saves correctly
  - Run workflow and verify status changes from pending → started → completed
  - Verify help screen shows updated documentation

## Testing Strategy

### Unit Tests

**Database Functions:**
- `update_issue_status()`: Test valid status transitions, invalid status values, non-existent issues, and database errors
- `update_issue_description()`: Test successful updates, empty/whitespace validation, length constraints, non-existent issues, and database errors

**Workflow Integration:**
- Mock `update_issue_status()` in workflow tests
- Verify status updates are called at correct points in workflow
- Test that status update failures don't halt workflow execution
- Verify appropriate logging for status changes

### Integration Tests

**Workflow Status Lifecycle:**
- Create a pending issue
- Execute workflow and verify status progresses: pending → started → completed
- Verify status updates are persisted in database
- Test workflow failure scenarios don't incorrectly mark as completed

**TUI Editing Flow:**
- Create pending issue via TUI
- Open detail screen and edit description
- Verify description updates are persisted
- Verify only pending issues can be edited

### Edge Cases

- Attempting to edit description of started/completed issue (should show warning)
- Status update failures during workflow execution (should log but not halt)
- Empty or invalid description in edit modal (should show validation error)
- Description at exact length boundaries (10 chars, 10000 chars)
- Concurrent status updates (database constraint should handle)
- Network failures during status/description updates (should handle gracefully)
- Rapid key presses in TUI (should handle without errors)

## Acceptance Criteria

- [ ] Enter key and 'd' key both open IssueDetailScreen from IssueListScreen
- [ ] 'e' key in IssueDetailScreen opens edit modal for pending issues
- [ ] 'e' key shows warning for started/completed issues without allowing edit
- [ ] Issue descriptions can be successfully edited and persisted for pending issues
- [ ] Description validation matches create_issue requirements (10-10000 chars, not empty)
- [ ] HelpScreen displays updated keyboard shortcuts including 'd' and 'e' keys
- [ ] `update_issue_status()` function exists and validates status values
- [ ] `update_issue_description()` function exists and validates descriptions
- [ ] Workflow sets issue status to "started" when execution begins
- [ ] Workflow sets issue status to "completed" when execution succeeds
- [ ] Status update failures are logged but don't halt workflow execution
- [ ] All existing tests pass without modification (no regressions)
- [ ] New unit tests for database functions achieve >90% coverage
- [ ] Manual TUI testing confirms all navigation and editing flows work correctly

## Validation Commands

Execute every command to validate the feature works correctly with zero regressions.

- `cd /Users/bponghneng/git/cape/cape-cli` - Change to project root
- `pytest tests/test_database.py -v` - Run database tests including new functions
- `pytest tests/test_workflow.py -v` - Run workflow tests with status integration
- `pytest tests/ -v` - Run full test suite
- `pytest tests/ -v --cov=cape-cli --cov-report=term-missing` - Run tests with coverage report
- Manual TUI testing:
  - `cape` - Launch TUI
  - Navigate with Enter and 'd' keys to verify both work
  - Press 'e' on pending issue and verify edit modal opens
  - Edit description and save, verify it persists
  - Press 'e' on completed issue and verify warning appears
  - Run workflow on pending issue, verify status changes in database
  - Press '?' to verify help screen shows new shortcuts

## Notes

### Navigation Bug Investigation
The Enter key binding appears to be correctly defined in the code (tui.py:30), but the feature spec mentions a bug preventing it from working. During implementation, we should:
- Test the current behavior to confirm the bug exists
- If the bug is confirmed, investigate whether it's a Textual framework issue or implementation issue
- Check if the DataTable widget is properly capturing the Enter key event
- Consider if there are any event propagation issues

### Status Update Best Practices
The workflow status updates should be best-effort operations:
- Log failures at ERROR level for visibility
- Never halt workflow execution due to status update failures
- Consider adding retry logic if database connectivity is unreliable
- Status updates provide valuable tracking but aren't critical to workflow success

### Future Enhancements
These items are out of scope for this feature but worth considering:
- Add ability to edit issue descriptions from IssueListScreen directly
- Add visual indicators in issue list for different statuses (colors, icons)
- Add filtering/sorting in IssueListScreen by status
- Add confirmation dialog before editing to prevent accidental changes
- Add undo/history for description edits
- Add ability to cancel running workflows and reset status
- Add status transition validation (e.g., can't go from completed back to pending)

### Testing Considerations
- Textual TUI components can be challenging to unit test - focus on logic testing
- Manual testing is critical for TUI changes to verify user experience
- Consider using Textual's built-in testing utilities if available
- Test with different terminal sizes and configurations
- Verify keyboard shortcuts don't conflict with terminal emulator shortcuts
