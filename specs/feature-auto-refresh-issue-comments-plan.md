# Feature: Auto-Refresh Issue Comments

## Description

Implement a mechanism to automatically refresh the list of comments on the IssueDetailScreen every 10 seconds when the issue status is "started". This feature provides near real-time updates to users monitoring active workflow progress without requiring manual page refreshes. The implementation leverages Textual's built-in timer and worker APIs for non-blocking, resource-efficient periodic updates with proper lifecycle management.

## User Story

As a user monitoring an active workflow
I want to see new comments appear automatically on the issue detail screen
So that I can track workflow progress in near real-time without manually refreshing

## Problem Statement

Currently, the IssueDetailScreen loads issue data and comments only once when the screen is mounted. Users monitoring active workflows (status="started") that generate progress comments must manually navigate away and back to see new comments. This creates a poor user experience for tracking workflow execution, as progress comments are created programmatically during workflow steps but are not visible until the user manually refreshes.

The workflow system (`workflow.py`) inserts progress comments at 4 key points during execution:
1. "Workflow started - Issue fetched and validated"
2. "Issue classified as {issue_command}"
3. "Implementation plan created successfully"
4. "Solution implemented successfully"

Without automatic refresh, users cannot see these progress updates as they occur.

## Solution Statement

Implement a conditional periodic refresh mechanism that:
1. Activates a 10-second interval timer only when viewing issues with "started" status
2. Refreshes comments asynchronously using the existing `@work` decorator pattern
3. Properly manages timer lifecycle (start on mount, stop on unmount)
4. Provides subtle UI feedback during refresh operations
5. Reuses existing database functions (`fetch_issue`, `fetch_comments`) without modifications

This approach builds on the existing codebase patterns, requiring minimal changes while delivering significant UX improvements for workflow monitoring.

## Relevant Files

### Core Implementation Files

**`/Users/bponghneng/git/cape/cape_cli/src/cape_cli/tui.py`** (Lines 278-391 - IssueDetailScreen)
- **Why relevant**: Contains the IssueDetailScreen class that needs the auto-refresh functionality
- **Current implementation**:
  - One-time data load in `on_mount()` method
  - Uses `@work(exclusive=True, thread=True)` decorator for async loading
  - Has `loading` reactive attribute (declared but not actively used)
  - No timer or periodic refresh mechanisms
- **Changes needed**:
  - Add timer to trigger periodic refresh
  - Modify `load_data()` to be called periodically
  - Add conditional logic to activate timer only for "started" status
  - Implement `on_unmount()` to clean up timer resources
  - Activate the `loading` reactive for UI feedback

**Key code snippets:**

Current `on_mount()`:
```python
def on_mount(self) -> None:
    """Initialize the screen when mounted."""
    self.load_data()
```

Current `load_data()`:
```python
@work(exclusive=True, thread=True)
def load_data(self) -> None:
    """Load issue and comments in background thread."""
    try:
        issue = fetch_issue(self.issue_id)
        comments = fetch_comments(self.issue_id)
        self.app.call_from_thread(self._display_data, issue, comments)
    except Exception as e:
        self.app.call_from_thread(self.notify, f"Error loading issue: {e}", severity="error")
```

**`/Users/bponghneng/git/cape/cape_cli/src/cape_cli/database.py`** (Lines 157-188 - fetch_comments)
- **Why relevant**: Provides the database function for fetching comments
- **Current implementation**: Already handles chronological ordering (oldest first) and error handling
- **Changes needed**: None - reuse as-is

```python
def fetch_comments(issue_id: int) -> List[CapeComment]:
    """Fetch all comments for an issue in chronological order.

    Args:
        issue_id: The ID of the issue to fetch comments for.

    Returns:
        List of CapeComment objects. Returns empty list if no comments exist.

    Raises:
        ValueError: If database operation fails.
    """
    client = get_client()

    try:
        response = (
            client.table("cape_comments")
            .select("*")
            .eq("issue_id", issue_id)
            .order("created_at", desc=False)  # Chronological order (oldest first)
            .execute()
        )

        if not response.data:
            return []

        return [CapeComment(**row) for row in response.data]

    except APIError as e:
        logger.error(f"Database error fetching comments for issue {issue_id}: {e}")
        raise ValueError(f"Failed to fetch comments for issue {issue_id}: {e}") from e
```

**`/Users/bponghneng/git/cape/cape_cli/src/cape_cli/database.py`** (Lines 74-94 - fetch_issue)
- **Why relevant**: Provides the database function for fetching issue details (including status)
- **Current implementation**: Returns CapeIssue object with status field
- **Changes needed**: None - reuse as-is

```python
def fetch_issue(issue_id: int) -> CapeIssue:
    """Fetch issue from Supabase by ID."""
    client = get_client()
    try:
        response = (
            client.table("cape_issues")
            .select("*")
            .eq("id", issue_id)
            .maybe_single()
            .execute()
        )
        if response.data is None:
            raise ValueError(f"Issue with id {issue_id} not found")
        return CapeIssue.from_supabase(response.data)
    except APIError as e:
        logger.error(f"Database error fetching issue {issue_id}: {e}")
        raise ValueError(f"Failed to fetch issue {issue_id}: {e}") from e
```

**`/Users/bponghneng/git/cape/cape_cli/src/cape_cli/models.py`** (Lines 35-88 - CapeIssue)
- **Why relevant**: Defines the CapeIssue model with status field used for conditional activation
- **Current implementation**: Has `status: str` field with values: "pending", "started", "completed"
- **Changes needed**: None - reference only

```python
class CapeIssue(BaseModel):
    """Cape issue model matching Supabase schema."""

    id: Optional[int] = None
    description: str = Field(..., min_length=1)
    status: str = Field(default="pending")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
```

**`/Users/bponghneng/git/cape/cape_cli/src/cape_cli/models.py`** (Lines 89-102 - CapeComment)
- **Why relevant**: Defines the CapeComment model used in the comments list
- **Current implementation**: Complete model with validation
- **Changes needed**: None - reference only

### Testing Files

**`/Users/bponghneng/git/cape/cape_cli/test_cape_tui.py`**
- **Why relevant**: Contains existing tests for the TUI application
- **Changes needed**: Add new test cases for auto-refresh functionality

### New Files

None - all changes are modifications to existing files.

## Implementation Plan

### Phase 1: Foundation
Add the infrastructure for periodic refresh without activating it. This includes:
- Adding timer property to IssueDetailScreen
- Implementing lifecycle management (on_unmount)
- Setting up conditional timer activation based on issue status
- Adding reactive property for tracking refresh state

### Phase 2: Core Implementation
Implement the actual refresh logic:
- Modify load_data() to support periodic calls
- Add visual feedback for refresh operations
- Implement smart refresh (only update if comments changed)
- Add error handling for refresh failures

### Phase 3: Integration
Integrate with existing functionality and add polish:
- Ensure timer stops when navigating away
- Test interaction with workflow completion callback
- Add tests for auto-refresh behavior
- Validate resource cleanup

## Step by Step Tasks

### Step 1: Add Timer Infrastructure to IssueDetailScreen

- Read `/Users/bponghneng/git/cape/cape_cli/src/cape_cli/tui.py` to understand current IssueDetailScreen implementation
- Add timer property to store the refresh timer reference
- Add reactive property `auto_refresh_active: reactive[bool] = reactive(False)` to track refresh state
- Import necessary Textual timer types (`from textual.timer import Timer`)

### Step 2: Implement Conditional Timer Activation

- Modify the `on_mount()` method to:
  - Call initial `load_data()` as before
  - Create a paused timer using `self.set_interval(10, self.load_data, pause=True, name="comment_refresh")`
  - Store timer reference for later control
- Modify `_display_data()` method to:
  - Check if `issue.status == "started"`
  - If true, set `auto_refresh_active = True` and resume timer
  - If false, set `auto_refresh_active = False` and pause timer

### Step 3: Implement Timer Lifecycle Management

- Add `on_unmount()` method to IssueDetailScreen:
  - Stop the refresh timer to prevent background API calls
  - Log cleanup for debugging purposes
- Test that timer stops when navigating away from the screen

### Step 4: Add Visual Feedback for Refresh Operations

- Modify `load_data()` to accept optional parameter `is_refresh: bool = False`
- When `is_refresh=True`, show subtle loading indicator:
  - Use the existing `loading` reactive attribute on RichLog widget
  - Set `self.query_one(RichLog).loading = True` before refresh
  - Set `self.query_one(RichLog).loading = False` after refresh completes
- Update timer callback to pass `is_refresh=True`: `self.set_interval(10, lambda: self.load_data(is_refresh=True), ...)`

### Step 5: Write Unit Tests for Auto-Refresh

- Create test file or add to existing `/Users/bponghneng/git/cape/cape_cli/test_cape_tui.py`
- Add test cases:
  - `test_auto_refresh_activates_for_started_status`: Verify timer starts only for "started" issues
  - `test_auto_refresh_inactive_for_pending_status`: Verify timer remains paused for "pending" issues
  - `test_auto_refresh_inactive_for_completed_status`: Verify timer remains paused for "completed" issues
  - `test_timer_cleanup_on_unmount`: Verify timer stops when screen unmounts
  - `test_refresh_updates_comments`: Verify comments are refreshed every 10 seconds
- Use Textual's async test utilities and mocking for database calls

### Step 6: Add Error Handling for Refresh Failures

- Modify `load_data()` error handling to differentiate between initial load and refresh:
  - Initial load failure: Show error notification (existing behavior)
  - Refresh failure: Log error but don't stop timer, show subtle warning
- Add retry logic or pause timer after consecutive failures (optional enhancement)

### Step 7: Optimize Refresh Logic

- Implement smart refresh to reduce unnecessary UI updates:
  - Compare new comments list with `self.comments` reactive property
  - Only call `_display_data()` if comments have changed (length or content)
- Add logging to track refresh operations for debugging

### Step 8: Manual Testing

- Start the TUI application: `uv run cape`
- Create a test issue with "started" status
- Navigate to issue detail screen
- Verify timer activates (check logs or add debug notification)
- Run a workflow to generate comments
- Observe comments appearing every 10 seconds
- Navigate away and verify timer stops (no more API calls in logs)

### Step 9: Run Validation Commands

- Execute all validation commands to ensure zero regressions
- Fix any formatting, linting, type checking, or test failures
- Verify all tests pass with the new functionality

## Testing Strategy

### Unit Tests

**Timer Activation Tests:**
- Test timer is created paused on mount
- Test timer resumes when issue status is "started"
- Test timer remains paused when issue status is "pending" or "completed"
- Test timer state changes when issue status changes

**Lifecycle Tests:**
- Test timer stops on unmount
- Test timer cleanup prevents background API calls after unmount
- Test multiple mount/unmount cycles don't leak timers

**Refresh Logic Tests:**
- Test `load_data()` is called every 10 seconds when timer is active
- Test comments are fetched from database on each refresh
- Test UI updates with new comments
- Test error handling during refresh operations

**Visual Feedback Tests:**
- Test loading indicator appears during refresh (optional)
- Test loading indicator is cleared after refresh completes

### Integration Tests

**Workflow Integration:**
- Test auto-refresh works correctly during workflow execution
- Test comments appear as workflow progresses
- Test timer deactivates when workflow completes (status changes to "completed")

**Navigation Integration:**
- Test timer stops when navigating back to issue list
- Test timer stops when switching to different issue
- Test timer restarts correctly when returning to same issue

### Edge Cases

1. **Rapid status changes**: Issue status changes from "started" to "completed" during a refresh operation
2. **Database failures**: Database becomes unavailable during auto-refresh (should log error but not crash)
3. **Empty comments**: Issue has no comments, refresh should handle gracefully
4. **Network latency**: Refresh takes longer than 10 seconds (exclusive=True should prevent overlap)
5. **Concurrent updates**: Multiple comments added between refresh intervals
6. **Timer precision**: Verify 10-second interval is reasonably accurate
7. **Memory leaks**: Long-running auto-refresh doesn't accumulate memory
8. **Screen switching**: Rapidly switching between issues doesn't leak timers

## Acceptance Criteria

- [ ] When the IssueDetailScreen is loaded with an issue status of "started", a periodic refresh mechanism is activated
- [ ] The comments list is refreshed every 10 seconds (±1 second tolerance)
- [ ] The data fetching process is asynchronous and does not block the UI or cause freezing
- [ ] The refresh timer is properly started when the screen is mounted
- [ ] The refresh timer is properly stopped when the screen is unmounted to prevent background API calls
- [ ] When the issue status is NOT "started" (pending or completed), the auto-refresh mechanism is NOT activated
- [ ] A subtle loading indicator or visual cue is displayed during comment refresh (optional but recommended)
- [ ] The feature does not introduce regressions in existing functionality
- [ ] All existing tests continue to pass
- [ ] New tests for auto-refresh functionality pass with >80% code coverage

## Validation Commands

Execute every command to validate the feature works correctly with zero regressions.

- `cd /Users/bponghneng/git/cape/cape_cli` - Change directory to the root of the codebase
- `uv sync` - Ensure all dependencies are installed and synced
- `pytest test_cape_tui.py -v` - Run all tests with verbose output
- `pytest test_cape_tui.py --cov=cape_cli.tui --cov-report=term-missing` - Run tests with coverage report
- `uv run cape` - Start the TUI application for manual testing
- Manual validation steps:
  1. Create a new issue or find an existing issue
  2. Manually set the issue status to "started" using database tools or workflow
  3. Navigate to the issue detail screen
  4. Observe that the screen loads normally
  5. Wait 10 seconds and observe if any visual feedback occurs (optional loading indicator)
  6. In a separate terminal, add a new comment to the issue using database tools or run a workflow
  7. Wait up to 10 seconds and verify the new comment appears without manual refresh
  8. Navigate back to the issue list
  9. Check application logs to verify timer stopped (no more API calls)
  10. Navigate to an issue with "pending" or "completed" status
  11. Verify auto-refresh does NOT activate (no periodic API calls in logs)

## Notes

### Implementation Considerations

**Simplicity-First Approach:**
- Reuse existing `@work` decorator pattern - no new async patterns needed
- Reuse existing database functions - no modifications required
- Minimal changes to IssueDetailScreen - add timer + lifecycle method
- No new dependencies or external libraries

**Textual Framework Patterns:**
- Use `self.set_interval()` for periodic callbacks (Textual's native timer API)
- Timers automatically clean up when parent widget unmounts (but explicit cleanup is recommended)
- `@work(exclusive=True, thread=True)` prevents overlapping refresh operations
- `call_from_thread()` required for UI updates from worker threads

**Performance & Resource Management:**
- 10-second interval is reasonable for database load (6 requests/minute max)
- `exclusive=True` prevents request pileup if database is slow
- Timer only active for "started" issues (subset of all issues)
- Automatic cleanup prevents memory leaks

### Future Enhancements (Out of Scope)

1. **Configurable refresh interval**: Allow users to set custom intervals
2. **Manual pause/resume**: Add keybinding to toggle auto-refresh
3. **Visual refresh indicator**: Show countdown or pulse animation
4. **Smart throttling**: Increase interval if no new comments for extended period
5. **WebSocket support**: Replace polling with real-time push notifications
6. **Optimistic UI updates**: Show new comments immediately when created locally
7. **Last refresh timestamp**: Display "Last updated: 2 seconds ago" status

### Context for Engineers

**Workflow Progress Comments Pattern:**
The workflow system (`/Users/bponghneng/git/cape/cape_cli/src/cape_cli/workflow.py`) creates comments at these points:
1. After fetching and validating the issue
2. After classifying the issue type
3. After creating the implementation plan
4. After implementing the solution

Auto-refresh enables users to see these progress updates in near real-time without manual intervention.

**Existing Codebase Patterns to Follow:**
- Worker pattern: `@work(exclusive=True, thread=True)` + `call_from_thread()`
- Error handling: Log with `logger.error()`, notify user with `self.notify()`
- Reactive state: Use `reactive` attributes for automatic UI updates
- Database access: Use existing `fetch_*` functions from `database.py`

**Testing Strategy Notes:**
- Mock Supabase client for unit tests to avoid real database calls
- Use Textual's async test utilities (`AsyncTestCase` or `pytest-asyncio`)
- Test timer behavior with Textual's time-based test utilities
- Integration tests can use in-memory database or test fixtures
