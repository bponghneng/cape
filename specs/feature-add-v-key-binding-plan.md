# Feature: Add 'v' Key Binding for Issue Details View

## Description

Add a 'v' key binding to the IssueListScreen in the Cape TUI as an alternative to the 'enter' key for viewing issue details. This enhancement provides users with a more intuitive keyboard shortcut that is commonly used in similar terminal-based applications (like vim and less) for viewing content. The feature maintains backward compatibility with the existing 'enter' key while providing users with an additional, arguably more ergonomic option for accessing issue details.

## User Story

As a Cape TUI user
I want to press 'v' to view issue details
So that I can use a familiar keyboard shortcut without moving my hand to the 'enter' key

## Problem Statement

Currently, users can only press 'enter' to view issue details from the issue list screen. While functional, this requires users to move their hand from the home row to press 'enter'. Many terminal applications use 'v' for "view" operations, making it a more intuitive and ergonomic choice. Adding 'v' as an alternative provides:
- Improved ergonomics (no need to leave home row)
- Consistency with other terminal applications
- Better discoverability (mnemonic: 'v' for "view")

## Solution Statement

Add 'v' as an additional key binding in the IssueListScreen.BINDINGS list that triggers the same `action_view_detail` method as 'enter'. Update the help screen documentation to reflect both key options. This is a minimal, non-breaking change that enhances user experience without modifying any core logic or data flow.

## Relevant Files

### cape-cli/src/cape_cli/tui.py

The main TUI implementation file containing all screen definitions and key bindings.

**IssueListScreen class (lines 30-231)**
- **BINDINGS** (lines 33-42): List of key bindings for the issue list screen
  - Currently has 'enter' bound to 'action_view_detail'
  - Need to add 'v' key binding here
  ```python
  BINDINGS = [
      ("n", "new_issue", "New Issue"),
      ("enter", "view_detail", "View Details"),
      ("d", "delete_issue", "Delete Issue"),
      ("delete", "delete_issue", "Delete Issue"),
      ("r", "run_workflow", "Run Workflow"),
      ("w", "view_workflows", "View Workflows"),
      ("q", "quit", "Quit"),
      ("?", "help", "Help"),
  ]
  ```
- **action_view_detail method** (lines 134-143): Handles navigation to issue detail screen
  - No changes needed - already implements the desired behavior
  - Both 'enter' and 'v' will call this method

**HelpScreen class (lines 1294-1379)**
- **compose method** (lines 1301-1375): Contains help text with keyboard shortcuts
  - **Issue List section** (lines 1307-1314): Documents keyboard shortcuts for issue list
  - Currently shows: `- **Enter**: View issue details`
  - Need to update to: `- **Enter/v**: View issue details`
  ```python
  ### Issue List
  - **n**: Create new issue
  - **Enter**: View issue details  # Update this line
  - **d/Delete**: Delete issue (pending issues only)
  - **r**: Run workflow on selected issue
  - **w**: View all active workflows
  - **q**: Quit application
  - **?**: Show this help screen
  ```

### cape-cli/tests/test_tui.py

Test file for TUI functionality using Textual testing patterns.

**Relevant context:**
- Uses pytest for testing with `pytest-asyncio` plugin
- Follows Textual testing best practices with fixtures and mocks
- Tests use unit test pattern (mocking, not `run_test()`) since we're testing key bindings directly

**Existing patterns to follow:**
- Use fixtures for mock data (lines 10-62)
- Mock screen components and timers
- Test specific behavior, not just existence

## Implementation Plan

### Phase 1: Foundation
No foundational work needed - this is a simple enhancement to existing functionality.

### Phase 2: Core Implementation
1. Add 'v' key binding to IssueListScreen.BINDINGS
2. Update help documentation to show both 'enter' and 'v' keys

### Phase 3: Integration
Add test coverage to verify:
1. 'v' key triggers the same behavior as 'enter'
2. Help screen displays updated key binding information
3. No regression in existing 'enter' key functionality

## Step by Step Tasks

### 1. Update IssueListScreen BINDINGS

Add the 'v' key binding to the BINDINGS list in IssueListScreen class.

**File:** `cape-cli/src/cape_cli/tui.py`
**Location:** Lines 33-42 (IssueListScreen.BINDINGS)

**Change:**
- Add new binding: `("v", "view_detail", "View Details")`
- Place it after the 'enter' binding for logical grouping

**Result:**
```python
BINDINGS = [
    ("n", "new_issue", "New Issue"),
    ("enter", "view_detail", "View Details"),
    ("v", "view_detail", "View Details"),
    ("d", "delete_issue", "Delete Issue"),
    ("delete", "delete_issue", "Delete Issue"),
    ("r", "run_workflow", "Run Workflow"),
    ("w", "view_workflows", "View Workflows"),
    ("q", "quit", "Quit"),
    ("?", "help", "Help"),
]
```

### 2. Update Help Screen Documentation

Update the help text in HelpScreen to reflect the new key binding.

**File:** `cape-cli/src/cape_cli/tui.py`
**Location:** Line 1309 (in HelpScreen.compose method)

**Change:**
- Update `- **Enter**: View issue details` to `- **Enter/v**: View issue details`

**Result:**
```python
### Issue List
- **n**: Create new issue
- **Enter/v**: View issue details
- **d/Delete**: Delete issue (pending issues only)
- **r**: Run workflow on selected issue
- **w**: View all active workflows
- **q**: Quit application
- **?**: Show this help screen
```

### 3. Create Unit Tests for 'v' Key Binding

Add test coverage to verify the 'v' key binding works correctly.

**File:** `cape-cli/tests/test_tui.py`

**Add new test:**
```python
def test_v_key_triggers_view_detail():
    """Test that 'v' key binding triggers action_view_detail method."""
    from cape_cli.tui import IssueListScreen

    # Create screen instance
    screen = IssueListScreen()

    # Mock the action_view_detail method
    screen.action_view_detail = Mock()

    # Verify 'v' key is in bindings
    binding_keys = [binding[0] for binding in screen.BINDINGS]
    assert "v" in binding_keys

    # Verify 'v' maps to 'view_detail' action
    v_binding = next(b for b in screen.BINDINGS if b[0] == "v")
    assert v_binding[1] == "view_detail"
    assert v_binding[2] == "View Details"


def test_enter_key_still_works():
    """Test that existing 'enter' key binding still works after adding 'v'."""
    from cape_cli.tui import IssueListScreen

    # Create screen instance
    screen = IssueListScreen()

    # Verify 'enter' key is still in bindings
    binding_keys = [binding[0] for binding in screen.BINDINGS]
    assert "enter" in binding_keys

    # Verify 'enter' still maps to 'view_detail' action
    enter_binding = next(b for b in screen.BINDINGS if b[0] == "enter")
    assert enter_binding[1] == "view_detail"
    assert enter_binding[2] == "View Details"


def test_both_keys_map_to_same_action():
    """Test that both 'enter' and 'v' map to the same action."""
    from cape_cli.tui import IssueListScreen

    screen = IssueListScreen()

    # Get bindings for both keys
    enter_binding = next(b for b in screen.BINDINGS if b[0] == "enter")
    v_binding = next(b for b in screen.BINDINGS if b[0] == "v")

    # Verify they map to the same action
    assert enter_binding[1] == v_binding[1]
    assert enter_binding[1] == "view_detail"
```

### 4. Run Validation Commands

Execute the validation commands to ensure the feature works correctly with zero regressions.

## Testing Strategy

### Unit Tests

**Test 1: Verify 'v' key binding exists**
- Check that 'v' is in the BINDINGS list
- Verify it maps to 'view_detail' action
- Verify the description is "View Details"

**Test 2: Verify 'enter' key still works**
- Check that 'enter' binding is unchanged
- Verify backward compatibility

**Test 3: Verify both keys map to same action**
- Confirm 'enter' and 'v' both trigger 'action_view_detail'
- Ensure consistency between the two bindings

### Integration Tests

No integration tests needed for this simple feature. The unit tests verify the key bindings are correctly configured, and manual testing can confirm the behavior.

### Edge Cases

1. **Both keys pressed in sequence**: Should both trigger view detail action normally
2. **Help screen display**: Should show both keys in documentation
3. **No issue selected**: Both keys should show the same warning message
4. **Invalid row**: Both keys should handle errors identically

## Acceptance Criteria

1. ✅ Pressing 'v' on the issue list screen navigates to issue details
2. ✅ Pressing 'enter' on the issue list screen continues to work as before
3. ✅ Help screen shows "Enter/v" for viewing issue details
4. ✅ No regression in existing functionality (all other key bindings work)
5. ✅ Tests pass for both 'v' and 'enter' key bindings
6. ✅ Code follows existing patterns and conventions

## Validation Commands

Execute every command to validate the feature works correctly with zero regressions.

- `cd /Users/bponghneng/git/cape/cape-cli` - Change directory to the root of the codebase
- `uv sync` - Ensure dependencies are installed
- `uv run pytest tests/test_tui.py -v -k "test_v_key or test_enter_key or test_both_keys"` - Run new tests for key bindings
- `uv run pytest tests/ -v` - Run full test suite to ensure no regressions
- `uv run pytest tests/ --cov=cape_cli --cov-report=term-missing` - Check test coverage
- `uv run cape` - Manually test the TUI to verify:
  - Press 'v' on an issue in the list -> should navigate to detail view
  - Press 'enter' on an issue in the list -> should navigate to detail view
  - Press '?' to view help -> should show "Enter/v" for view details
  - Test with no issue selected -> both keys should show warning
- `cd /Users/bponghneng/git/cape` - Return to workspace root

## Notes

### Implementation Simplicity
This is an excellent example of a minimal, high-value enhancement:
- Only 2 lines of code changed (1 line added, 1 line updated)
- No new methods or classes needed
- No changes to core logic or data flow
- Leverages existing `action_view_detail` method
- Zero risk of breaking existing functionality

### Testing Philosophy
Following the codebase testing guidelines:
- Focus on behavioral tests (key bindings work correctly)
- Use simple unit tests with mocks (no `run_test()` needed for this)
- Test both success path and backward compatibility
- Keep tests focused and specific

### User Experience
The 'v' key is more ergonomic because:
- Users can keep hands on home row
- Mnemonic: 'v' for "view" is more intuitive than 'enter'
- Consistent with vim, less, and other terminal tools
- Optional: users can continue using 'enter' if preferred

### Future Considerations
This pattern could be extended to other screens if desired:
- IssueDetailScreen could add 'v' for viewing workflows
- WorkflowsScreen could add 'v' for viewing details
However, per the simplicity-first mindset, we should only add these if users specifically request them.
