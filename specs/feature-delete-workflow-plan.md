# Feature: Delete Workflow

## Description

This feature adds the ability to delete issues with "pending" status from both the main issue list screen and the issue details screen. The delete operation requires confirmation through a modal dialog to prevent accidental deletions. This feature enhances the issue management workflow by allowing users to remove issues that are no longer needed before they are processed by the workflow engine.

The delete functionality is restricted to pending issues only, ensuring that issues that have been started or completed are preserved for audit and tracking purposes. The confirmation modal provides a safety mechanism and follows UX best practices for destructive operations.

## User Story

As a user managing Cape issues
I want to delete pending issues that are no longer needed
So that I can keep my issue list clean and focused on relevant work items

## Problem Statement

Currently, users cannot remove issues from the system once they have been created. This leads to cluttered issue lists containing obsolete, duplicate, or erroneous issues. Users need a safe and intuitive way to delete pending issues that haven't yet been processed by the workflow engine. The deletion must be restricted to pending issues to preserve the audit trail of started and completed work.

## Solution Statement

Implement a delete workflow feature that:

1. **Adds delete functionality to IssueListScreen**: Users can delete the currently selected issue if its status is "pending" using the Delete key or 'd' keyboard shortcut
2. **Adds delete functionality to IssueDetailScreen**: Users can delete the currently viewed issue if its status is "pending" using the Delete key
3. **Implements confirmation modal**: A ConfirmDeleteModal screen asks users to confirm deletion before proceeding, following Textual's ModalScreen pattern
4. **Adds database delete operation**: A new `delete_issue()` function in the database module that deletes the issue and its associated comments using Supabase's cascade delete functionality
5. **Updates UI after deletion**: On successful deletion, removes the issue from the DataTable (list screen) or returns to the list screen (details screen) and displays a success notification

The solution follows existing patterns in the codebase:
- Uses `ModalScreen[bool]` for the confirmation dialog (similar to EditDescriptionScreen)
- Uses `@work(exclusive=True, thread=True)` for background database operations
- Uses `variant="error"` for destructive action buttons
- Implements proper error handling with user notifications

## Relevant Files

### Core Implementation Files

#### `/Users/bponghneng/git/cape/cape-cli/src/cape_cli/tui.py` (592 lines)
Main TUI application file containing all screens and modals.

**Relevant sections:**
- **IssueListScreen (lines 24-131)**: Main screen displaying issues in a DataTable
  - Add delete keyboard binding
  - Add `action_delete_issue()` method to trigger confirmation modal
  - Add callback handler for delete confirmation result
  - Add background worker to perform deletion and update UI

  ```python
  # Existing binding pattern (lines 27-34)
  BINDINGS = [
      ("n", "new_issue", "New Issue"),
      ("enter", "view_detail", "View Details"),
      ("d", "view_detail", "View Details"),  # Will change to delete
      ("r", "run_workflow", "Run Workflow"),
      ("q", "quit", "Quit"),
      ("?", "help", "Help"),
  ]
  ```

- **IssueDetailScreen (lines 278-390)**: Detail view for a single issue
  - Add delete keyboard binding
  - Add `action_delete_issue()` method similar to edit functionality
  - Add callback handler to navigate back on successful deletion

  ```python
  # Existing binding pattern (lines 283-287)
  BINDINGS = [
      ("e", "edit_description", "Edit Description"),
      ("r", "run_workflow", "Run Workflow"),
      ("escape", "back", "Back"),
  ]
  ```

- **Modal pattern reference - EditDescriptionScreen (lines 213-275)**: Existing modal implementation
  ```python
  class EditDescriptionScreen(ModalScreen[bool]):
      """Example of modal pattern to follow."""

      def __init__(self, issue_id: int, current_description: str):
          super().__init__()
          self.issue_id = issue_id
          self.current_description = current_description
  ```

#### `/Users/bponghneng/git/cape/cape-cli/src/cape_cli/database.py` (320 lines)
Database operations module with Supabase client.

**Relevant sections:**
- **Client management (lines 46-65)**: Singleton Supabase client
  ```python
  _client: Optional[Client] = None

  @lru_cache()
  def get_client() -> Client:
      """Get or create global Supabase client instance."""
      global _client
      if _client is None:
          config = SupabaseConfig()
          config.validate()
          _client = create_client(config.url, config.service_role_key)
      return _client
  ```

- **CRUD operation patterns**: Existing create, read, update operations (lines 68-200+)
  - Follow the pattern of `update_issue_status()` and `update_issue_description()` for error handling
  - Use proper exception handling and response validation

  ```python
  # Example pattern from update_issue_description (lines 178-200)
  def update_issue_description(issue_id: int, description: str) -> CapeIssue:
      """Update issue description."""
      client = get_client()
      update_data = {"description": description_clean}

      response = (
          client.table("cape_issues")
          .update(update_data)
          .eq("id", issue_id)
          .execute()
      )

      if not response.data:
          raise ValueError(f"Issue with id {issue_id} not found")

      return CapeIssue(**response.data[0])
  ```

**New function to add:**
- `delete_issue(issue_id: int) -> bool`: Delete issue and associated comments
  - Use Supabase delete API with `.delete().eq("id", issue_id)`
  - Rely on database cascade delete for comments (already configured)
  - Return True on success, raise ValueError on failure
  - Include proper error handling and logging

#### `/Users/bponghneng/git/cape/cape-cli/src/cape_cli/models.py` (102 lines)
Pydantic models for data validation.

**Relevant sections:**
- **CapeIssue model**: Used for type hints and validation
  ```python
  class CapeIssue(BaseModel):
      id: int
      description: str = Field(..., min_length=1)
      status: Literal["pending", "started", "completed"] = "pending"
      created_at: Optional[datetime] = None
      updated_at: Optional[datetime] = None
  ```

No changes needed to this file - models are used as-is for type checking.

#### `/Users/bponghneng/git/cape/cape-cli/src/cape_cli/cape_tui.tcss` (174 lines)
Textual CSS styling for the TUI.

**Relevant sections:**
- **Modal styling patterns** (lines 60-85): Existing modal CSS to follow
  ```css
  #create-issue-modal {
      width: 80;
      height: 30;
      border: thick $primary;
      background: $surface;
      padding: 1 2;
  }

  #modal-header {
      width: 100%;
      height: 3;
      content-align: center middle;
      text-style: bold;
      background: $primary;
      color: $text;
      margin-bottom: 1;
  }
  ```

**New styling to add:**
- `#confirm-delete-modal`: Container styling for confirmation modal
- `#delete-warning`: Warning text styling (red/error color)
- Button styling is already defined in Textual framework (`variant="error"`)

### Testing Files

#### `/Users/bponghneng/git/cape/cape-cli/tests/test_database.py` (358 lines)
Database operation tests.

**Relevant sections:**
- **Test patterns for CRUD operations**: Follow existing test structure
- **Fixtures for test data**: Use existing fixtures for creating test issues

**New tests to add:**
- `test_delete_issue_success()`: Test successful deletion
- `test_delete_issue_not_found()`: Test deleting non-existent issue
- `test_delete_issue_cascades_comments()`: Verify comments are deleted with issue

### New Files

#### `/Users/bponghneng/git/cape/cape-cli/tests/test_tui_delete.py`
Integration tests for delete functionality in the TUI.

**Test coverage:**
- Test delete action on pending issue (should show confirmation)
- Test delete action on non-pending issue (should show warning)
- Test delete confirmation accepted (should delete and update UI)
- Test delete confirmation cancelled (should not delete)
- Test delete with no selection (should show warning)
- Test delete from issue detail screen

## Implementation Plan

### Phase 1: Foundation
**Goal**: Implement core database delete functionality and confirmation modal

1. **Add database delete operation**
   - Create `delete_issue(issue_id: int) -> bool` function in database.py
   - Implement Supabase delete API call with proper error handling
   - Add logging for delete operations
   - Write unit tests for delete operation

2. **Create confirmation modal component**
   - Create `ConfirmDeleteModal(ModalScreen[bool])` class in tui.py
   - Implement modal UI with issue information, warning text, and action buttons
   - Use `variant="error"` for delete button, `variant="primary"` for cancel button
   - Add CSS styling for the modal in cape_tui.tcss
   - Ensure proper focus handling (focus on cancel by default)

### Phase 2: Core Implementation
**Goal**: Integrate delete functionality into both screens

3. **Add delete to IssueListScreen**
   - Update keyboard bindings (change 'd' from view_detail to delete_issue)
   - Add 'delete' key binding as alternative
   - Implement `action_delete_issue()` to check status and show confirmation
   - Implement callback handler for confirmation result
   - Implement background worker to perform deletion
   - Update DataTable after successful deletion

4. **Add delete to IssueDetailScreen**
   - Add keyboard binding for delete key
   - Implement `action_delete_issue()` similar to edit functionality
   - Check if issue status is pending before allowing delete
   - Show confirmation modal and handle callback
   - Navigate back to list screen on successful deletion

### Phase 3: Integration
**Goal**: Test end-to-end functionality and ensure proper error handling

5. **Testing and validation**
   - Write unit tests for database delete operation
   - Write integration tests for delete workflow in TUI
   - Test edge cases (non-pending issues, missing issues, network errors)
   - Verify UI updates correctly after deletion
   - Test cascade delete for comments
   - Run full validation suite

6. **Polish and documentation**
   - Update help screen with delete keyboard shortcuts
   - Ensure consistent error messages
   - Verify accessibility (keyboard navigation, focus handling)
   - Update any relevant documentation

## Step by Step Tasks

IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Implement Database Delete Operation

Add the delete functionality to the database module with proper error handling and logging.

- Read `/Users/bponghneng/git/cape/cape-cli/src/cape_cli/database.py` to understand existing patterns
- Add `delete_issue(issue_id: int) -> bool` function after the update operations
- Use Supabase client's `.delete().eq("id", issue_id)` pattern
- Include try-except error handling following existing patterns
- Add logger.info() call for successful deletions
- Verify the function signature and return type
- Import any necessary types or exceptions

### Step 2: Write Unit Tests for Delete Operation

Create comprehensive unit tests for the delete database operation.

- Read `/Users/bponghneng/git/cape/cape-cli/tests/test_database.py` to understand test patterns
- Add `test_delete_issue_success()` test case
- Add `test_delete_issue_not_found()` test case
- Add `test_delete_issue_with_comments()` test to verify cascade delete
- Use existing fixtures for creating test data
- Run tests with `cd /Users/bponghneng/git/cape/cape-cli && pytest tests/test_database.py::test_delete_issue* -v`
- Ensure all delete tests pass

### Step 3: Create ConfirmDeleteModal Component

Implement the confirmation modal following Textual's ModalScreen pattern.

- Read the EditDescriptionScreen class in tui.py (lines 213-275) to understand modal patterns
- Add `ConfirmDeleteModal(ModalScreen[bool])` class after EditDescriptionScreen
- Accept `issue_id` and `issue_description` in `__init__`
- Implement `compose()` method with:
  - Static widget for modal header ("Delete Issue #{issue_id}")
  - Static widget showing truncated issue description
  - Static widget with warning text ("This action cannot be undone")
  - Horizontal container with Cancel (primary) and Delete (error) buttons
- Implement `on_mount()` to focus cancel button by default
- Implement `on_button_pressed()` to dismiss with True/False based on button ID
- Add keyboard binding for Escape key to cancel

### Step 4: Add CSS Styling for Delete Modal

Create consistent styling for the confirmation modal.

- Read `/Users/bponghneng/git/cape/cape-cli/src/cape_cli/cape_tui.tcss` to understand existing modal styles
- Add `#confirm-delete-modal` container styling similar to `#create-issue-modal`
- Use `border: thick $error;` to indicate destructive action
- Add `#delete-warning` styling with error color
- Ensure modal centers properly with `align: center middle`
- Keep styling minimal and consistent with existing patterns

### Step 5: Add Delete Functionality to IssueListScreen

Integrate delete into the main issue list with status checking.

- Read IssueListScreen class in tui.py (lines 24-131)
- Update BINDINGS to change 'd' from "view_detail" to "delete_issue"
- Add 'delete' key binding as alternative: `("delete", "delete_issue", "Delete Issue")`
- Implement `action_delete_issue()` method:
  - Get cursor row from DataTable
  - Check if row is selected (show warning if not)
  - Extract issue data from row (ID, description, status)
  - Check if status is "pending" (show warning if not)
  - Use `functools.partial` to create callback with issue_id and row_key
  - Call `self.app.push_screen(ConfirmDeleteModal(...), callback)`
- Implement callback handler `handle_delete_confirmation(issue_id, row_key, confirmed)`
  - Return early if not confirmed
  - Call background worker to perform deletion
- Implement background worker using `@work(exclusive=True, thread=True)`
  - Import delete_issue from database module
  - Call delete_issue(issue_id) in try-except block
  - On success: call `self.app.call_from_thread()` to remove row and notify
  - On error: call `self.app.call_from_thread()` to show error notification
- Add helper method `_remove_row_and_notify(row_key, message)` for UI updates

### Step 6: Add Delete Functionality to IssueDetailScreen

Integrate delete into the issue detail view.

- Read IssueDetailScreen class in tui.py (lines 278-390)
- Add keyboard binding: `("delete", "delete_issue", "Delete Issue")`
- Implement `action_delete_issue()` method:
  - Check if `self.issue` is loaded
  - Check if `self.issue.status == "pending"` (show warning if not)
  - Show ConfirmDeleteModal with issue details
  - Pass callback handler
- Implement callback handler `handle_delete_confirmation(confirmed)`
  - Return early if not confirmed
  - Call background worker to perform deletion
- Implement background worker:
  - Call delete_issue(self.issue_id)
  - On success: navigate back to IssueListScreen with notification
  - On error: show error notification
- Use `self.app.pop_screen()` to return to list screen after successful deletion

### Step 7: Update Help Screen with Delete Shortcuts

Document the new delete functionality in the help screen.

- Read HelpScreen class in tui.py (lines 486-541)
- Add delete keyboard shortcut information to help text
- Include explanation that delete only works for pending issues
- Update the keyboard shortcuts section with Delete key binding

### Step 8: Create Integration Tests for Delete Workflow

Write comprehensive integration tests for the delete functionality.

- Create `/Users/bponghneng/git/cape/cape-cli/tests/test_tui_delete.py`
- Import necessary test utilities and fixtures
- Write test for delete action on pending issue (should show modal)
- Write test for delete action on started/completed issue (should show warning)
- Write test for delete confirmation accepted (should delete and update UI)
- Write test for delete confirmation cancelled (should not delete)
- Write test for delete with no selection (should show warning)
- Write test for delete from detail screen
- Use async test patterns if needed for modal interaction
- Run tests with `cd /Users/bponghneng/git/cape/cape-cli && pytest tests/test_tui_delete.py -v`

### Step 9: Run Complete Test Suite and Validation

Execute all validation commands to ensure zero regressions.

- Run all tests: `cd /Users/bponghneng/git/cape/cape-cli && pytest tests/ -v`
- Verify test coverage: `pytest tests/ --cov=cape_cli --cov-report=term-missing`
- Check that delete_issue function has >90% coverage
- Check that delete modal and actions are tested
- Manually test the TUI with `uv run cape`:
  - Create a pending issue
  - Delete it using delete key from list screen
  - Verify confirmation modal appears
  - Test cancelling deletion
  - Test confirming deletion
  - Verify issue is removed from list
  - Test deleting from detail screen
  - Test that non-pending issues cannot be deleted
- Verify database cascade: Create issue with comments, delete issue, verify comments are gone

## Testing Strategy

### Unit Tests

**Database Operations (test_database.py)**
- `test_delete_issue_success()`: Verify delete_issue() returns True and removes issue from database
- `test_delete_issue_not_found()`: Verify delete_issue() raises ValueError for non-existent issue ID
- `test_delete_issue_with_comments()`: Create issue with comments, delete issue, verify comments are also deleted (cascade)

**Expected Coverage**: >95% for delete_issue() function

### Integration Tests

**TUI Delete Workflow (test_tui_delete.py)**
- `test_delete_action_pending_issue()`: Trigger delete on pending issue, verify confirmation modal appears
- `test_delete_action_non_pending_issue()`: Trigger delete on started/completed issue, verify warning notification
- `test_delete_confirmation_accepted()`: Accept confirmation, verify issue deleted and UI updated
- `test_delete_confirmation_cancelled()`: Cancel confirmation, verify issue not deleted
- `test_delete_no_selection()`: Trigger delete with no selected row, verify warning notification
- `test_delete_from_detail_screen()`: Delete from issue detail screen, verify navigation back to list
- `test_delete_network_error()`: Simulate network error, verify error notification shown

**Expected Coverage**: >80% for delete-related code paths in tui.py

### Edge Cases

**Status Validation**
- Delete button disabled/warning shown for "started" status issues
- Delete button disabled/warning shown for "completed" status issues
- Delete button enabled only for "pending" status issues

**UI State Management**
- DataTable updates correctly after deletion (row removed)
- Cursor position handled correctly after row removal
- Issue detail screen navigates back to list after deletion
- Notifications displayed for success and error cases

**Error Handling**
- Network errors during deletion show appropriate error message
- Database errors (e.g., foreign key violations) handled gracefully
- Missing issue ID handled correctly
- Concurrent deletion attempts handled safely

**Keyboard Navigation**
- Delete key triggers delete action
- Escape key cancels confirmation modal
- Tab/arrow keys navigate between Cancel and Delete buttons
- Focus defaults to Cancel button (safe option)

## Acceptance Criteria

1. **Delete from List Screen**
   - User can press Delete key or 'd' key on a pending issue to trigger delete
   - Confirmation modal appears with issue details and warning
   - User can cancel with Escape key or Cancel button
   - User can confirm with Delete button
   - Issue is removed from DataTable on successful deletion
   - Success notification is displayed
   - Non-pending issues show warning when delete is attempted

2. **Delete from Detail Screen**
   - User can press Delete key while viewing a pending issue
   - Confirmation modal appears with same behavior as list screen
   - User is returned to list screen after successful deletion
   - Non-pending issues show warning when delete is attempted

3. **Confirmation Modal**
   - Modal displays issue ID and truncated description
   - Modal shows "This action cannot be undone" warning
   - Cancel button is styled with primary variant (blue)
   - Delete button is styled with error variant (red)
   - Focus defaults to Cancel button
   - Escape key cancels the operation

4. **Database Operations**
   - delete_issue() function successfully deletes issue from database
   - Comments associated with issue are deleted automatically (cascade)
   - Function raises ValueError if issue not found
   - Function logs successful deletions

5. **Error Handling**
   - Network errors display error notification
   - Database errors are caught and displayed to user
   - UI remains responsive during delete operation
   - No crashes or unhandled exceptions

6. **Testing**
   - All unit tests pass with >90% coverage for delete functionality
   - All integration tests pass
   - Edge cases are tested and handled correctly
   - Manual testing confirms expected behavior

## Validation Commands

Execute every command to validate the feature works correctly with zero regressions.

- `cd /Users/bponghneng/git/cape/cape-cli` - Change directory to the CLI project root
- `uv sync` - Ensure all dependencies are installed and synced
- `pytest tests/test_database.py::test_delete_issue_success -v` - Test successful deletion
- `pytest tests/test_database.py::test_delete_issue_not_found -v` - Test error handling
- `pytest tests/test_database.py::test_delete_issue_with_comments -v` - Test cascade delete
- `pytest tests/test_tui_delete.py -v` - Run all TUI delete integration tests
- `pytest tests/ -v` - Run complete test suite
- `pytest tests/ --cov=cape_cli --cov-report=term-missing` - Verify test coverage
- `uv run cape` - Launch TUI for manual testing
  - Create a new pending issue (press 'n')
  - Select the issue and press Delete key
  - Verify confirmation modal appears with correct details
  - Test cancelling (press Escape or click Cancel)
  - Test confirming (click Delete button)
  - Verify issue is removed from list and success notification shown
  - Create another issue and view details (press Enter)
  - Press Delete key from detail screen
  - Verify same confirmation flow works
  - Verify return to list screen after deletion
  - Create an issue and run workflow to change status to "started"
  - Try to delete the started issue
  - Verify warning notification that only pending issues can be deleted

## Notes

### Database Cascade Configuration

The Supabase schema for `cape_comments` should have a foreign key constraint with ON DELETE CASCADE configured:

```sql
ALTER TABLE cape_comments
  DROP CONSTRAINT IF EXISTS cape_comments_issue_id_fkey,
  ADD CONSTRAINT cape_comments_issue_id_fkey
  FOREIGN KEY (issue_id)
  REFERENCES cape_issues(id)
  ON DELETE CASCADE;
```

If this constraint is not configured, the delete_issue() function may fail with a foreign key violation error when trying to delete issues that have comments. Verify the constraint exists or add logic to manually delete comments before deleting the issue.

### Future Considerations

**Soft Delete Pattern**: Consider implementing soft delete (marking as deleted rather than removing) for production environments where audit trails and data recovery are important. This would involve:
- Adding `deleted_at` timestamp column to `cape_issues` table
- Modifying delete_issue() to UPDATE instead of DELETE
- Filtering deleted issues in fetch_all_issues() queries
- Adding "restore" functionality for undeleting issues

**Bulk Delete**: Future enhancement could allow selecting multiple issues and deleting them at once:
- Multi-select in DataTable using Shift+arrow keys
- Confirmation modal showing count of issues to delete
- Batch delete operation in database module

**Undo Functionality**: Consider adding undo capability:
- Keep deleted issue in memory for short period
- Show "Undo" action in notification
- Restore issue if undo is triggered within timeout

**Archive Instead of Delete**: Alternative to deletion could be archiving:
- Move issue to "archived" status instead of deleting
- Keep archived issues in database but filter from main list
- Add "show archived" toggle for viewing archived issues

### Implementation Notes

- The 'd' key is currently bound to "view_detail" in IssueListScreen. Changing this to delete will require users to use Enter key to view details instead, which is also bound and more intuitive.

- The confirmation modal uses `functools.partial` to bind the issue_id and row_key to the callback function. This is necessary because the callback only receives the boolean result from the modal.

- Background workers use `@work(exclusive=True, thread=True)` to prevent blocking the UI during database operations. All UI updates from worker threads must use `self.app.call_from_thread()`.

- The error variant for buttons (`variant="error"`) provides red styling consistent with destructive actions. This is preferred over custom CSS for button colors.

- Database operations should follow the existing pattern of raising ValueError with descriptive messages for error conditions, which are caught and displayed to users via notifications.
