# Chore Plan: Refactor insert_progress_comment

## Task Context

- Scope: small-change
- Goal: Refactor `insert_progress_comment` to return status tuples instead of using logger parameter, improving testability and separation of concerns
- Constraints: Maintain backward compatibility with existing progress comment functionality

## Description

Refactor the `insert_progress_comment` function to follow a cleaner pattern where the function returns success/error status as a tuple instead of taking a logger as a parameter. This improves testability by making the function more pure and allows callers to decide how to handle logging.

Current signature: `def insert_progress_comment(issue_id: int, comment_text: str, logger) -> None`
New signature: `def insert_progress_comment(issue_id: int, comment_text: str) -> tuple[str, str]`

The function will return `("success", message)` on successful comment insertion or `("error", message)` on failure. Callers will capture these return values and log them appropriately using their local loggers.

Out of scope:
- Changes to the progress comment handler functionality
- Modifications to database layer (`create_comment`)
- Changes to `cape-cli` duplicate files (focus on `cape/app` only as specified)

## Relevant Files

- **cape/app/src/cape/core/notifications/__init__.py** (lines 27-43) - Primary implementation location containing `insert_progress_comment` function that needs signature and return value changes

- **cape/app/src/cape/core/notifications.py** (lines 8-18) - Duplicate implementation that should be kept consistent with the primary version

- **cape/app/src/cape/core/workflow.py** (lines 277, 307, 318, 343) - Four call sites that need to capture return values and log based on status

- **cape/app/src/cape/core/agent.py** (lines 66, 211) - Two call sites that need to capture return values and log based on status

- **cape/app/tests/test_workflow.py** (lines 53-72) - Test mocks and assertions that need updating for new signature and return values

## Implementation Plan

### 1. Update insert_progress_comment in notifications/__init__.py

Modify the function signature and implementation:

- Change signature from `def insert_progress_comment(issue_id: int, comment_text: str, logger) -> None:` to `def insert_progress_comment(issue_id: int, comment_text: str) -> tuple[str, str]:`
- Remove `from logging import Logger` import (line 36)
- Remove logger parameter from function signature
- Remove all logger calls from function body (lines 40, 42)
- Add return statement on success: `return ("success", f"Comment inserted: ID={comment.id}, Text='{comment_text}'")`
- Add return statement on exception: `return ("error", f"Failed to insert comment on issue {issue_id}: {exc}")`
- Update docstring to document return value format and remove logger parameter documentation

### 2. Update insert_progress_comment in notifications.py

Apply identical changes to maintain consistency:

- Change signature to match notifications/__init__.py
- Remove `from logging import Logger` import (line 3)
- Update function body to return tuples instead of logging
- Update docstring to match primary implementation

### 3. Update callers in workflow.py

Update all four call sites (lines 277, 307, 318, 343):

- Line 277: `insert_progress_comment(issue_id, "Workflow started - Issue fetched and validated", logger)`
  - Change to: `status, msg = insert_progress_comment(issue_id, "Workflow started - Issue fetched and validated")`
  - Add conditional logging: `logger.debug(msg) if status == "success" else logger.error(msg)`

- Line 307: `insert_progress_comment(issue_id, comment_text, logger)`
  - Change to: `status, msg = insert_progress_comment(issue_id, comment_text)`
  - Add conditional logging: `logger.debug(msg) if status == "success" else logger.error(msg)`

- Line 318: `insert_progress_comment(issue_id, "Implementation plan created successfully", logger)`
  - Change to: `status, msg = insert_progress_comment(issue_id, "Implementation plan created successfully")`
  - Add conditional logging: `logger.debug(msg) if status == "success" else logger.error(msg)`

- Line 343: `insert_progress_comment(issue_id, "Solution implemented successfully", logger)`
  - Change to: `status, msg = insert_progress_comment(issue_id, "Solution implemented successfully")`
  - Add conditional logging: `logger.debug(msg) if status == "success" else logger.error(msg)`

### 4. Update callers in agent.py

Update both call sites (lines 66, 211):

- Line 66: `insert_progress_comment(request.issue_id, f"Output saved to: {response.raw_output_path}", logger)`
  - Change to: `status, msg = insert_progress_comment(request.issue_id, f"Output saved to: {response.raw_output_path}")`
  - Add conditional logging: `logger.debug(msg) if status == "success" else logger.error(msg)`

- Line 211: `insert_progress_comment(issue_id, f"Implementation complete. Output saved to: {response.raw_output_path}", logger)`
  - Change to: `status, msg = insert_progress_comment(issue_id, f"Implementation complete. Output saved to: {response.raw_output_path}")`
  - Add conditional logging: `logger.debug(msg) if status == "success" else logger.error(msg)`

### 5. Update test mocks and assertions in test_workflow.py

Update tests to match new signature and return values:

- Lines 53-62 (`test_insert_progress_comment_success`):
  - Update mock to return tuple: `insert_progress_comment.return_value = ("success", f"Comment inserted: ID={mock_comment.id}, Text='Test comment'")`
  - Remove logger parameter from call: `status, msg = insert_progress_comment(1, "Test comment")`
  - Add assertions: `assert status == "success"` and `assert "Comment inserted" in msg`
  - Remove mock_logger assertions

- Lines 65-72 (`test_insert_progress_comment_failure`):
  - Update mock to return error tuple: `insert_progress_comment.return_value = ("error", "Failed to insert comment on issue 1: Database error")`
  - Remove logger parameter from call: `status, msg = insert_progress_comment(1, "Test comment")`
  - Add assertions: `assert status == "error"` and `assert "Failed to insert comment" in msg`
  - Remove mock_logger assertions

- Lines 182-210 (`test_execute_workflow_success`):
  - Update mock_insert_comment to return success tuples for all calls
  - Verify call count remains 4 for progress comments
  - Update assertions to not check logger calls on insert_progress_comment

## Validation

Execute commands to ensure the chore is complete with zero regressions:

- `cd cape/app` - Change to app directory
- `uv run pytest tests/test_workflow.py -v` - Run workflow tests to verify all tests pass with updated mocks and assertions
- `uv run pytest tests/ -v` - Run full test suite to ensure no regressions in other tests
- `cd ../..` - Return to workspace root

Expected results:
- All tests in test_workflow.py pass
- No regressions in other test files
- Progress comments still inserted correctly during workflow execution
- Error handling maintains same best-effort behavior (failures don't halt workflow)

## Notes / Future Considerations

### Design Rationale

**Return Tuple Pattern:**
- Separates concerns: function handles database operation, caller handles logging
- Improves testability: no need to mock logger in unit tests of the function
- Makes success/failure status explicit and verifiable
- Follows functional programming principles by reducing side effects

**Message Format:**
- Success messages include comment ID and text for traceability
- Error messages include issue ID and exception details for debugging
- Format matches existing debug/error log patterns in the codebase

**Backward Compatibility:**
- Same best-effort behavior preserved (errors don't halt workflow)
- Same log levels used (debug for success, error for failures)
- Progress comments still inserted at same four points in workflow

### Future Enhancements

**Potential Extensions (not in scope for this chore):**
- Consider returning structured objects instead of tuples (e.g., `Result[Comment, Error]`)
- Add retry logic for transient database failures
- Implement batched comment insertion for performance
- Add telemetry/metrics for comment insertion success rates

### Context for Implementation

**Existing Pattern:**
- The `update_status` function in workflow.py (lines 25-41) uses a similar best-effort pattern but still takes logger as parameter
- This refactor establishes a pattern that could be applied to `update_status` in a future chore
- The `create_comment` database function already has good error handling and validation

**Testing Strategy:**
- Tests focus on return value verification rather than logger call verification
- Maintains test coverage while making tests simpler and more focused
- Integration tests still verify end-to-end behavior through workflow execution
