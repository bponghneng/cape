# Feature: TUI Layout and Component Updates

## Description

Refine the Cape TUI by improving layout consistency and component usage across the issue detail, new issue, and edit issue screens. This feature focuses on creating a more intuitive user experience through better information architecture, reusable components, and conditional rendering based on issue status.

Key improvements include:
- Replacing the live workflow output window with a standard comments widget in the issue detail screen
- Making the description section collapsible for better space management
- Hiding comments when issues are in pending status
- Implementing full-screen scrolling instead of nested scrollable sections
- Creating a unified, reusable form component for issue creation and editing

## User Story

As a Cape TUI user
I want a cleaner, more consistent interface for viewing and managing issues
So that I can focus on relevant information without visual clutter and navigate the interface more efficiently

## Problem Statement

The current TUI has several UX issues that create friction for users:

1. **Visual Clutter**: The IssueDetailScreen displays a live workflow output window that is no longer needed, taking up valuable screen space
2. **Inconsistent Layouts**: CreateIssueScreen and EditDescriptionScreen have duplicate code with identical layouts, making maintenance difficult and increasing the risk of inconsistencies
3. **Information Overload**: The description section is always fully visible, consuming space even when users want to focus on comments or workflows
4. **Irrelevant Information**: Comments are shown for pending issues even though no comments exist until a workflow starts
5. **Confusing Scrolling**: Multiple nested scrollable sections create a confusing navigation experience

These issues reduce user efficiency and create a cluttered, inconsistent experience across different screens.

## Solution Statement

Implement a component-based architecture with conditional rendering and improved scrolling:

1. **Remove Workflow Output Window**: Eliminate the live workflow output RichLog from IssueDetailScreen, replacing it with the standard CommentsWidget that already supports auto-refresh
2. **Create Reusable IssueForm Component**: Extract common form logic into a single IssueForm composite widget that both CreateIssueScreen and EditDescriptionScreen can use, ensuring consistency and reducing code duplication
3. **Add Collapsible Description**: Wrap the description in a Textual Collapsible widget, allowing users to collapse it when focusing on other information
4. **Implement Conditional Comments Visibility**: Hide the entire comments section when issue status is "pending" since no comments exist yet, reducing visual clutter
5. **Enable Full-Screen Scrolling**: Replace individual scrollable sections with a single VerticalScroll container that scrolls the entire screen content, providing a more intuitive navigation experience

This approach leverages Textual's built-in components (Collapsible, VerticalScroll) and follows composition patterns to create maintainable, reusable widgets.

## Relevant Files

### Existing Files to Modify

#### `/Users/bponghneng/git/cape/cape_cli/src/cape_cli/tui.py`
Primary implementation file containing all screens and widgets. Key areas to modify:

**IssueDetailScreen (Lines 321-608)**:
- Currently uses RichLog for comments and workflow output
- Current layout: Header → Vertical(detail-header, issue-content, workflows-header, workflows-content, comments-header, comments-log) → Footer
- Needs refactoring to use Collapsible for description and conditional comments rendering

**CreateIssueScreen (Lines 177-244)**:
- Current layout: Container(modal-header, TextArea, Horizontal(Save, Cancel))
- Duplicate validation logic (lines 217-227)
- Will be refactored to use IssueForm component

**EditDescriptionScreen (Lines 246-319)**:
- Current layout: Container(modal-header, TextArea, Horizontal(Save, Cancel))
- Duplicate validation logic (lines 292-302) identical to CreateIssueScreen
- Will be refactored to use IssueForm component

**Relevant Code Patterns**:
```python
# Current validation pattern (duplicated in both screens)
if not description or description == "Enter issue description...":
    self.notify("Description cannot be empty", severity="warning")
    return

if len(description) < 10:
    self.notify("Description must be at least 10 characters", severity="warning")
    return

if len(description) > 10000:
    self.notify("Description cannot exceed 10,000 characters", severity="warning")
    return
```

```python
# Current comment display pattern (IssueDetailScreen._display_data, lines 462-472)
comments_log = self.query_one(RichLog)
comments_log.clear()

if not comments:
    comments_log.write("No comments yet")
else:
    for comment in comments:
        timestamp = comment.created_at.strftime("%Y-%m-%d %H:%M") if comment.created_at else "Unknown"
        comments_log.write(f"[dim]{timestamp}[/dim]\n{comment.comment}\n")
```

```python
# Current auto-refresh logic (lines 478-489)
if self.refresh_timer is not None:
    if issue.status == "started":
        if not self.auto_refresh_active:
            self.auto_refresh_active = True
            self.refresh_timer.resume()
            logger.info(f"Auto-refresh activated for issue {self.issue_id}")
    else:
        if self.auto_refresh_active:
            self.auto_refresh_active = False
            self.refresh_timer.pause()
            logger.info(f"Auto-refresh deactivated for issue {self.issue_id}")
```

#### `/Users/bponghneng/git/cape/cape_cli/src/cape_cli/cape_tui.tcss`
CSS styling file for the TUI. Will need updates for new components:

**Current Styles to Reference**:
- Modal styling patterns for headers and buttons
- Color scheme for status indicators (pending=yellow, started=blue, completed=green)
- Layout patterns using `height: 1fr` for flexible sizing

**New Styles Needed**:
- IssueForm container styling
- Collapsible widget styling for description section
- VerticalScroll container for full-screen scrolling
- CommentsWidget container styling

#### `/Users/bponghneng/git/cape/cape_cli/tests/test_tui.py`
Test file for TUI components. Will need new tests for:
- IssueForm validation and callbacks
- CommentsWidget rendering and formatting
- Conditional comments visibility based on status
- Collapsible description behavior

### Supporting Files (Read-Only Reference)

#### `/Users/bponghneng/git/cape/cape_cli/src/cape_cli/models.py`
Data models - no changes needed:

```python
# Lines 89-102: CapeComment model
class CapeComment(BaseModel):
    id: Optional[int]
    issue_id: int
    comment: str
    created_at: Optional[datetime]
```

```python
# Lines 53-87: CapeIssue model
class CapeIssue(BaseModel):
    id: Optional[int]
    description: str
    status: str  # "pending", "started", "completed"
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
```

#### `/Users/bponghneng/git/cape/cape_cli/src/cape_cli/database.py`
Database operations - no changes needed, will use existing functions:
- `fetch_issue(issue_id: int) -> CapeIssue`
- `fetch_comments(issue_id: int) -> List[CapeComment]`
- `create_issue(description: str) -> CapeIssue`
- `update_issue_description(issue_id: int, description: str) -> None`

### New Files

#### None
All implementation will be in existing `tui.py` file as new widget classes. The single-file architecture is maintained for simplicity.

## Implementation Plan

### Phase 1: Foundation - Reusable Component Creation

**Objective**: Build the foundation by creating reusable widgets that will be used across multiple screens.

**Tasks**:
1. Create IssueForm composite widget
   - Extract common form logic from CreateIssueScreen and EditDescriptionScreen
   - Implement validation logic in the widget
   - Expose callbacks for save and cancel actions
   - Add keyboard shortcuts (Ctrl+S for save, Escape for cancel)

2. Create CommentsWidget component
   - Simple wrapper around RichLog for consistent comment display
   - Accept list of CapeComment objects
   - Format timestamps and content using existing pattern
   - Handle empty state gracefully

**Deliverables**: Two new widget classes in tui.py with unit tests

**Success Criteria**: Widgets can be instantiated, rendered, and tested in isolation

### Phase 2: Core Implementation - Screen Refactoring

**Objective**: Refactor existing screens to use new components and implement layout changes.

**Tasks**:
1. Refactor CreateIssueScreen to use IssueForm
   - Replace TextArea and Button composition with IssueForm
   - Wire up callbacks to existing handlers
   - Remove duplicate validation code
   - Maintain modal styling

2. Refactor EditDescriptionScreen to use IssueForm
   - Replace TextArea and Button composition with IssueForm
   - Pre-populate form with current description
   - Wire up callbacks
   - Remove duplicate validation code

3. Refactor IssueDetailScreen layout (most complex task)
   - Remove workflow output RichLog section completely
   - Wrap description in Collapsible widget (initially expanded)
   - Replace comments RichLog with CommentsWidget
   - Implement conditional rendering for comments section based on status
   - Wrap all content in VerticalScroll for full-screen scrolling
   - Update _display_data() method to work with new widget structure
   - Ensure auto-refresh mechanism works with CommentsWidget

**Deliverables**: Three refactored screens with all functionality preserved

**Success Criteria**: All keyboard shortcuts work, auto-refresh functions correctly, no visual regressions

### Phase 3: Integration - Testing and Polish

**Objective**: Ensure all components work together correctly and meet quality standards.

**Tasks**:
1. Update CSS styling
   - Add styles for new components (IssueForm, Collapsible, CommentsWidget)
   - Update #detail-container for full-screen scrolling
   - Remove unused styles for workflow sections
   - Test on various terminal sizes

2. Create comprehensive test suite
   - Unit tests for IssueForm (validation, callbacks)
   - Unit tests for CommentsWidget (display, formatting, empty state)
   - Integration tests for conditional comments rendering
   - Tests for Collapsible behavior
   - Regression tests for auto-refresh

3. Documentation and code cleanup
   - Add docstrings to all new classes
   - Update HelpScreen if needed
   - Remove dead code
   - Clean up imports

**Deliverables**: Updated CSS, comprehensive test suite, documentation

**Success Criteria**: All tests pass, code coverage >85%, visual consistency across screens

## Step by Step Tasks

IMPORTANT: Execute every step in order, top to bottom.

### 1. Create IssueForm Composite Widget

- Create new IssueForm class extending Container in tui.py
- Add constructor accepting optional initial_text parameter
- Implement compose() method with TextArea and Button widgets
- Add keyboard bindings (ctrl+s for save, escape for cancel)
- Implement validation logic (10-10,000 characters, non-empty, not placeholder)
- Add on_save_callback and on_cancel_callback properties
- Write unit tests for IssueForm validation logic
- Write unit tests for button event handling
- Manually test widget rendering in isolation

### 2. Create CommentsWidget Component

- Create CommentsWidget class extending RichLog in tui.py
- Implement update_comments(comments: List[CapeComment]) method
- Add timestamp formatting using existing pattern ("%Y-%m-%d %H:%M")
- Handle empty comments list ("No comments yet")
- Add loading state support
- Write unit tests for comment display with data
- Write unit tests for empty state
- Write unit tests for timestamp formatting

### 3. Refactor CreateIssueScreen to Use IssueForm

- Update CreateIssueScreen.compose() to use IssueForm instead of TextArea and Buttons
- Pass initial text "Enter issue description..." to IssueForm
- Wire up IssueForm.on_save_callback to action_save method
- Wire up IssueForm.on_cancel_callback to action_cancel method
- Remove duplicate validation code from action_save
- Update create_issue_handler to work with IssueForm
- Test create issue flow in running TUI
- Test keyboard shortcuts (Ctrl+S, Escape)
- Verify validation messages display correctly
- Run existing tests to check for regressions

### 4. Refactor EditDescriptionScreen to Use IssueForm

- Update EditDescriptionScreen.compose() to use IssueForm
- Pass current_description to IssueForm initial_text parameter
- Wire up IssueForm.on_save_callback to action_save method
- Wire up IssueForm.on_cancel_callback to action_cancel method
- Remove duplicate validation code from action_save
- Update update_description_handler to work with IssueForm
- Test edit description flow on pending issue
- Test keyboard shortcuts (Ctrl+S, Escape)
- Verify validation messages display correctly
- Run existing tests to check for regressions

### 5. Refactor IssueDetailScreen Layout

- Import VerticalScroll and Collapsible from textual.containers and textual.widgets
- Update compose() method to wrap content in VerticalScroll container
- Remove Static widgets for workflows-header and workflows-content (workflow monitoring removed)
- Wrap description Static in Collapsible widget with title="Description", collapsed=False
- Update compose() to conditionally include comments section (will be added dynamically)
- Modify _display_data() to handle conditional comments section visibility
- Implement logic to show comments when status is "started" or "completed"
- Implement logic to hide comments when status is "pending"
- Replace comments RichLog with CommentsWidget
- Update comment display logic to use CommentsWidget.update_comments()
- Update auto-refresh logic to work with new widget structure
- Test with pending issue (comments hidden)
- Test with started issue (comments visible, auto-refresh active)
- Test with completed issue (comments visible, auto-refresh inactive)
- Test Collapsible expand/collapse behavior
- Test full-screen scrolling with long descriptions and many comments
- Verify all keyboard shortcuts still work (e, r, w, s, escape)
- Run auto-refresh tests from test_tui.py

### 6. Update CSS Styling for New Components

- Add CSS rules for IssueForm container in cape_tui.tcss
- Add CSS rules for Collapsible widget styling
- Update #detail-container to use height: 1fr and overflow-y: auto for scrolling
- Remove CSS for #workflows-header and #workflows-content (no longer used)
- Add CSS for CommentsWidget container
- Ensure responsive layout on different terminal sizes
- Test visual consistency across all screens (issue list, detail, create, edit)
- Test on various terminal sizes (80x24, 120x40, 160x50)
- Verify color scheme consistency (status colors, borders, etc.)

### 7. Create Comprehensive Test Suite

- Write unit test for IssueForm initialization
- Write unit test for IssueForm validation (empty, too short, too long)
- Write unit test for IssueForm save callback
- Write unit test for IssueForm cancel callback
- Write unit test for CommentsWidget with comments
- Write unit test for CommentsWidget empty state
- Write unit test for CommentsWidget formatting
- Write integration test for IssueDetailScreen hiding comments when pending
- Write integration test for IssueDetailScreen showing comments when started
- Write integration test for IssueDetailScreen showing comments when completed
- Write integration test for Collapsible description behavior
- Run full test suite: pytest tests/test_tui.py -v
- Check test coverage: pytest tests/test_tui.py --cov=cape_cli.tui --cov-report=term-missing
- Fix any failing tests
- Ensure coverage is >85% on modified code

### 8. Documentation and Code Cleanup

- Add comprehensive docstring to IssueForm class
- Add comprehensive docstring to CommentsWidget class
- Update docstrings for modified methods in IssueDetailScreen
- Update docstrings for modified methods in CreateIssueScreen
- Update docstrings for modified methods in EditDescriptionScreen
- Add inline comments for complex logic in conditional rendering
- Remove any commented-out code from refactoring
- Remove unused imports
- Update HelpScreen if keyboard shortcuts changed (verify no changes needed)
- Review code for consistency with existing patterns

### 9. Run Validation Commands

Execute every command to validate the feature works correctly with zero regressions.

## Testing Strategy

### Unit Tests

**IssueForm Widget**:
- Test initialization with and without initial_text
- Test validation logic for empty description
- Test validation logic for description too short (<10 chars)
- Test validation logic for description too long (>10,000 chars)
- Test validation logic for placeholder text
- Test save button event handling
- Test cancel button event handling
- Test keyboard shortcut handling (Ctrl+S, Escape)

**CommentsWidget**:
- Test initialization
- Test update_comments with list of comments
- Test update_comments with empty list
- Test timestamp formatting
- Test Rich markup formatting (dim timestamps)
- Test clear and repopulate behavior

**IssueDetailScreen**:
- Test conditional rendering of comments section based on status
- Test Collapsible widget initialization
- Test auto-refresh activation/deactivation with new widget structure

### Integration Tests

**CreateIssueScreen with IssueForm**:
- Test end-to-end issue creation flow
- Test validation error display
- Test successful issue creation
- Test cancel flow

**EditDescriptionScreen with IssueForm**:
- Test end-to-end description edit flow
- Test pre-population of description
- Test validation error display
- Test successful description update
- Test cancel flow

**IssueDetailScreen Layout**:
- Test full-screen scrolling with long content
- Test Collapsible expand/collapse
- Test comments visibility for pending issue (hidden)
- Test comments visibility for started issue (visible)
- Test comments visibility for completed issue (visible)
- Test auto-refresh with CommentsWidget

### Edge Cases

**Empty States**:
- IssueForm with empty initial text
- CommentsWidget with no comments
- IssueDetailScreen with no issue data

**Boundary Conditions**:
- Description exactly 10 characters (valid)
- Description exactly 10,000 characters (valid)
- Description 9 characters (invalid)
- Description 10,001 characters (invalid)

**State Transitions**:
- Issue transitioning from pending to started (comments should appear)
- Issue transitioning from started to completed (comments should remain visible)
- Auto-refresh timer activation/deactivation during status changes

**UI Interactions**:
- Rapid toggling of Collapsible widget
- Scrolling while auto-refresh is updating
- Keyboard shortcuts while form is validating

## Acceptance Criteria

1. ✅ **Issue Detail Screen No Longer Shows Workflow Output**: The live workflow output window (RichLog) is completely removed from IssueDetailScreen and replaced by the standard CommentsWidget for auto-refreshing comments
   - Validation: Navigate to issue detail screen, verify no workflow output section exists
   - Validation: Comments section displays and auto-refreshes correctly for started issues

2. ✅ **Issue Detail Description is Collapsible**: The description section in IssueDetailScreen is wrapped in a Collapsible widget that can be expanded/collapsed
   - Validation: Navigate to issue detail screen, click on description header to collapse
   - Validation: Click again to expand, content shows/hides correctly
   - Validation: Collapsible starts in expanded state by default

3. ✅ **Comments Hidden for Pending Issues**: The entire comments section is hidden when issue status is "pending"
   - Validation: View issue detail for pending issue, verify no comments section
   - Validation: View issue detail for started issue, verify comments section visible
   - Validation: View issue detail for completed issue, verify comments section visible

4. ✅ **Full-Screen Scrolling**: The IssueDetailScreen has full-screen scrolling instead of individual scrollable sections
   - Validation: Navigate to issue with long description and many comments
   - Validation: Scroll down smoothly without nested scroll contexts
   - Validation: All content (description, comments) scrolls in single container

5. ✅ **Unified Issue Form**: CreateIssueScreen and EditDescriptionScreen use identical layouts via shared IssueForm widget
   - Validation: Compare create and edit screens, layouts are identical
   - Validation: Both screens have same validation behavior
   - Validation: Both screens respond to same keyboard shortcuts (Ctrl+S, Escape)

6. ✅ **Reusable Form Component**: IssueForm composite widget exists and is used by both NewIssueScreen and EditIssueScreen
   - Validation: Code review confirms IssueForm widget exists
   - Validation: Code review confirms both screens use IssueForm in compose()
   - Validation: No duplicate validation code exists between screens

## Validation Commands

Execute every command to validate the feature works correctly with zero regressions.

- `cd /Users/bponghneng/git/cape/cape_cli` - Change directory to the root of the codebase.
- `uv sync` - Install and sync dependencies.
- `pytest tests/test_tui.py -v` - Run TUI test suite with verbose output.
- `pytest tests/test_tui.py --cov=cape_cli.tui --cov-report=term-missing` - Run tests with coverage report.
- `pytest tests/ -v` - Run all tests to check for regressions in other modules.
- `uv run cape` - Launch the TUI application for manual testing.

**Manual Testing Checklist** (run after `uv run cape`):
1. Press 'n' to create new issue - verify IssueForm layout and validation
2. Enter description, press Ctrl+S to save - verify issue created
3. Press Enter on issue to view details - verify Collapsible description
4. Click description header to collapse/expand - verify behavior
5. View pending issue - verify comments section hidden
6. Press 'r' to run workflow on pending issue - verify workflow starts
7. Wait for issue to transition to started - verify comments section appears
8. Wait for auto-refresh - verify comments update automatically
9. Press 'e' to edit description - verify IssueForm pre-populated
10. Modify description, press Ctrl+S - verify description updates
11. Test scrolling on issue with long description and many comments
12. Press all keyboard shortcuts (escape, r, w, s) - verify all work

## Notes

### Architectural Context

**Single-File Architecture**: The entire TUI is implemented in a single file (`tui.py`, ~1200 lines). This refactoring maintains this architecture while improving code organization through composition.

**Textual Framework Version**: Requires Textual >=0.50.0 for Collapsible widget support. Current version in pyproject.toml should be verified before implementation.

**Auto-Refresh Mechanism**: The existing auto-refresh functionality (10-second interval when status="started") must be preserved and should work seamlessly with the new CommentsWidget. The refresh_timer and auto_refresh_active reactive properties are already implemented correctly.

### Design Decisions

**Why Remove Workflow Output Window**: The live workflow output window was removed because:
- Workflows now run as background processes that persist even when the TUI is closed
- Real-time output is less critical since workflows continue independently
- Comments provide sufficient progress information via auto-refresh
- Removing it simplifies the UI and reduces visual clutter

**Why Use Collapsible for Description**: Descriptions can be very long (up to 10,000 characters), often containing detailed feature specs or bug reports. Making this collapsible allows users to:
- Focus on comments and workflow status when needed
- Reduce scrolling distance to reach comments
- Maintain context by expanding when needed

**Why Hide Comments for Pending Issues**: Comments are only created by workflows, which haven't run yet for pending issues. Showing an empty comments section adds no value and creates visual clutter.

**Why Create IssueForm Widget**: CreateIssueScreen and EditDescriptionScreen had ~100 lines of duplicate code (TextArea, buttons, validation logic). Extracting this into a reusable component:
- Reduces code duplication from ~200 lines to ~100 lines
- Ensures consistent validation behavior
- Makes future changes easier (modify once instead of twice)
- Follows DRY principle and composition over inheritance

### Future Considerations

**Potential Enhancements** (out of scope for this implementation):
- Keyboard shortcut to toggle Collapsible (e.g., 'c' key)
- Syntax highlighting for markdown in description preview
- Inline comment creation from IssueDetailScreen
- Comment pagination for issues with hundreds of comments
- Animated transitions for Collapsible expand/collapse

**Performance Considerations**:
- The VerticalScroll container should handle long content efficiently
- Auto-refresh with many comments may cause UI lag - consider limiting displayed comments
- Collapsible state should be preserved if issue is reloaded

**Testing Gaps** (known limitations):
- Manual testing required for terminal size responsiveness
- Automated testing of Collapsible expand/collapse animations is difficult
- Auto-refresh timing tests may be flaky (time-dependent)

### Dependencies on Other Work

**No blocking dependencies**: This feature is self-contained and doesn't depend on other in-progress work.

**Blocked work**: None - other features can continue in parallel.

**Related features**:
- Workflow monitoring improvements (separate feature)
- Comment threading (future enhancement)
- Real-time collaboration (future enhancement)

### Risk Mitigation

**Risk: Breaking Auto-Refresh**: The auto-refresh mechanism is critical for monitoring workflow progress.
- Mitigation: Thoroughly test with started issues
- Mitigation: Preserve existing refresh_timer and auto_refresh_active logic
- Fallback: Revert to RichLog if CommentsWidget causes issues

**Risk: Conditional Rendering Complexity**: Dynamically showing/hiding comments section may introduce bugs.
- Mitigation: Use Textual's display property for simple show/hide
- Mitigation: Test all status transitions (pending→started, started→completed)
- Fallback: Always show section with "Not available for pending issues" message

**Risk: CSS Regressions**: Widget restructuring may break existing styles.
- Mitigation: Test on various terminal sizes after each change
- Mitigation: Use Textual DevTools for debugging CSS issues
- Fallback: Add inline styles if CSS selectors break

### Code Review Checklist

When reviewing this implementation, verify:
- [ ] IssueForm is used in both CreateIssueScreen and EditDescriptionScreen
- [ ] No duplicate validation logic exists between screens
- [ ] Comments section is hidden for pending issues
- [ ] Comments section is visible for started and completed issues
- [ ] Description is wrapped in Collapsible widget
- [ ] Workflow output RichLog section is completely removed
- [ ] Full-screen scrolling works without nested scroll contexts
- [ ] Auto-refresh functionality is preserved
- [ ] All keyboard shortcuts continue to work
- [ ] Test coverage is >85% on modified code
- [ ] All existing tests pass
- [ ] Visual consistency maintained across screens
