"""Tests for TUI auto-refresh functionality and new widget components."""

import pytest
from unittest.mock import Mock, patch, PropertyMock, MagicMock
from datetime import datetime
from cape_cli.models import CapeIssue, CapeComment
from cape_cli.tui import IssueDetailScreen, IssueForm, CommentsWidget


@pytest.fixture
def mock_issue_started():
    """Create a mock issue with 'started' status."""
    return CapeIssue(
        id=1,
        description="Test issue with started status",
        status="started",
        created_at=datetime(2024, 1, 1, 12, 0, 0),
        updated_at=datetime(2024, 1, 1, 12, 30, 0),
    )


@pytest.fixture
def mock_issue_pending():
    """Create a mock issue with 'pending' status."""
    return CapeIssue(
        id=2,
        description="Test issue with pending status",
        status="pending",
        created_at=datetime(2024, 1, 1, 12, 0, 0),
        updated_at=datetime(2024, 1, 1, 12, 30, 0),
    )


@pytest.fixture
def mock_issue_completed():
    """Create a mock issue with 'completed' status."""
    return CapeIssue(
        id=3,
        description="Test issue with completed status",
        status="completed",
        created_at=datetime(2024, 1, 1, 12, 0, 0),
        updated_at=datetime(2024, 1, 1, 13, 0, 0),
    )


@pytest.fixture
def mock_comments():
    """Create mock comments."""
    return [
        CapeComment(
            id=1,
            issue_id=1,
            comment="First comment",
            created_at=datetime(2024, 1, 1, 12, 10, 0),
        ),
        CapeComment(
            id=2,
            issue_id=1,
            comment="Second comment",
            created_at=datetime(2024, 1, 1, 12, 20, 0),
        ),
    ]


def test_auto_refresh_activates_for_started_status(mock_issue_started, mock_comments):
    """Test that auto-refresh activates when issue status is 'started'."""
    # Create screen instance
    screen = IssueDetailScreen(issue_id=1)

    # Mock set_interval to return a mock timer
    mock_timer = Mock()
    mock_timer.resume = Mock()
    mock_timer.pause = Mock()
    screen.set_interval = Mock(return_value=mock_timer)

    # Mock query_one to avoid widget lookup issues
    screen.query_one = Mock(return_value=Mock())

    # Set initial state
    screen.auto_refresh_active = False
    screen.refresh_timer = mock_timer

    # Simulate data display with started status
    screen._display_data(mock_issue_started, mock_comments)

    # Verify auto-refresh was activated
    assert screen.auto_refresh_active is True
    mock_timer.resume.assert_called_once()


def test_auto_refresh_inactive_for_pending_status(mock_issue_pending, mock_comments):
    """Test that auto-refresh remains inactive when issue status is 'pending'."""
    # Create screen instance
    screen = IssueDetailScreen(issue_id=2)

    # Mock set_interval to return a mock timer
    mock_timer = Mock()
    mock_timer.resume = Mock()
    mock_timer.pause = Mock()

    # Mock query_one to avoid widget lookup issues
    screen.query_one = Mock(return_value=Mock())

    # Set initial state
    screen.auto_refresh_active = False
    screen.refresh_timer = mock_timer

    # Simulate data display with pending status
    screen._display_data(mock_issue_pending, mock_comments)

    # Verify auto-refresh was NOT activated
    assert screen.auto_refresh_active is False
    mock_timer.resume.assert_not_called()


def test_auto_refresh_inactive_for_completed_status(mock_issue_completed, mock_comments):
    """Test that auto-refresh remains inactive when issue status is 'completed'."""
    # Create screen instance
    screen = IssueDetailScreen(issue_id=3)

    # Mock set_interval to return a mock timer
    mock_timer = Mock()
    mock_timer.resume = Mock()
    mock_timer.pause = Mock()

    # Mock query_one to avoid widget lookup issues
    screen.query_one = Mock(return_value=Mock())

    # Set initial state
    screen.auto_refresh_active = False
    screen.refresh_timer = mock_timer

    # Simulate data display with completed status
    screen._display_data(mock_issue_completed, mock_comments)

    # Verify auto-refresh was NOT activated
    assert screen.auto_refresh_active is False
    mock_timer.resume.assert_not_called()


def test_timer_cleanup_on_unmount():
    """Test that timer is properly stopped when screen is unmounted."""
    # Create screen instance
    screen = IssueDetailScreen(issue_id=1)

    # Mock timer
    mock_timer = Mock()
    mock_timer.stop = Mock()
    screen.refresh_timer = mock_timer
    screen.auto_refresh_active = True

    # Simulate unmount
    screen.on_unmount()

    # Verify timer was stopped
    mock_timer.stop.assert_called_once()
    assert screen.auto_refresh_active is False


def test_auto_refresh_deactivates_on_status_change(
    mock_issue_started, mock_issue_completed, mock_comments
):
    """Test that auto-refresh deactivates when issue status changes from 'started' to 'completed'."""
    # Create screen instance
    screen = IssueDetailScreen(issue_id=1)

    # Mock set_interval to return a mock timer
    mock_timer = Mock()
    mock_timer.resume = Mock()
    mock_timer.pause = Mock()

    # Mock query_one to avoid widget lookup issues
    screen.query_one = Mock(return_value=Mock())

    # Set initial state
    screen.auto_refresh_active = False
    screen.refresh_timer = mock_timer

    # Simulate data display with started status
    screen._display_data(mock_issue_started, mock_comments)

    # Verify auto-refresh was activated
    assert screen.auto_refresh_active is True
    mock_timer.resume.assert_called_once()

    # Simulate status change to completed
    screen._display_data(mock_issue_completed, mock_comments)

    # Verify auto-refresh was deactivated
    assert screen.auto_refresh_active is False
    mock_timer.pause.assert_called_once()


# Tests for IssueForm Widget


def test_issue_form_initialization_with_default_text():
    """Test IssueForm initializes with default empty text."""
    form = IssueForm()
    assert form.initial_text == ""
    assert form.on_save_callback is None
    assert form.on_cancel_callback is None


def test_issue_form_initialization_with_custom_text():
    """Test IssueForm initializes with provided initial text."""
    initial_text = "Test issue description"
    form = IssueForm(initial_text=initial_text)
    assert form.initial_text == initial_text


def test_issue_form_validation_empty_description():
    """Test IssueForm rejects empty description."""
    save_callback = Mock()
    form = IssueForm(on_save_callback=save_callback)

    # Mock the screen and TextArea
    mock_screen = Mock()
    mock_textarea = Mock()
    mock_textarea.text = ""

    # Use PropertyMock to mock the screen property
    with patch.object(type(form), 'screen', new_callable=PropertyMock, return_value=mock_screen):
        form.query_one = Mock(return_value=mock_textarea)

        # Trigger save action
        form.action_save()

        # Verify callback was NOT called and notification was shown
        save_callback.assert_not_called()
        mock_screen.notify.assert_called_once()
        assert "cannot be empty" in mock_screen.notify.call_args[0][0]


def test_issue_form_validation_placeholder_text():
    """Test IssueForm rejects placeholder text."""
    save_callback = Mock()
    form = IssueForm(on_save_callback=save_callback)

    # Mock the screen and TextArea
    mock_screen = Mock()
    mock_textarea = Mock()
    mock_textarea.text = "Enter issue description..."

    # Use PropertyMock to mock the screen property
    with patch.object(type(form), 'screen', new_callable=PropertyMock, return_value=mock_screen):
        form.query_one = Mock(return_value=mock_textarea)

        # Trigger save action
        form.action_save()

        # Verify callback was NOT called
        save_callback.assert_not_called()
        mock_screen.notify.assert_called_once()


def test_issue_form_validation_too_short():
    """Test IssueForm rejects description shorter than 10 characters."""
    save_callback = Mock()
    form = IssueForm(on_save_callback=save_callback)

    # Mock the screen and TextArea
    mock_screen = Mock()
    mock_textarea = Mock()
    mock_textarea.text = "Short"  # 5 characters

    # Use PropertyMock to mock the screen property
    with patch.object(type(form), 'screen', new_callable=PropertyMock, return_value=mock_screen):
        form.query_one = Mock(return_value=mock_textarea)

        # Trigger save action
        form.action_save()

        # Verify callback was NOT called
        save_callback.assert_not_called()
        mock_screen.notify.assert_called_once()
        assert "at least 10 characters" in mock_screen.notify.call_args[0][0]


def test_issue_form_validation_too_long():
    """Test IssueForm rejects description longer than 10,000 characters."""
    save_callback = Mock()
    form = IssueForm(on_save_callback=save_callback)

    # Mock the screen and TextArea
    mock_screen = Mock()
    mock_textarea = Mock()
    mock_textarea.text = "x" * 10001  # 10,001 characters

    # Use PropertyMock to mock the screen property
    with patch.object(type(form), 'screen', new_callable=PropertyMock, return_value=mock_screen):
        form.query_one = Mock(return_value=mock_textarea)

        # Trigger save action
        form.action_save()

        # Verify callback was NOT called
        save_callback.assert_not_called()
        mock_screen.notify.assert_called_once()
        assert "10,000 characters" in mock_screen.notify.call_args[0][0]


def test_issue_form_validation_valid_description():
    """Test IssueForm accepts valid description."""
    save_callback = Mock()
    form = IssueForm(on_save_callback=save_callback)

    # Mock the TextArea (no screen mock needed for valid case)
    mock_textarea = Mock()
    valid_description = "This is a valid description that is long enough"
    mock_textarea.text = valid_description
    form.query_one = Mock(return_value=mock_textarea)

    # Trigger save action
    form.action_save()

    # Verify callback WAS called with cleaned description
    save_callback.assert_called_once_with(valid_description)


def test_issue_form_cancel_callback():
    """Test IssueForm calls cancel callback."""
    cancel_callback = Mock()
    form = IssueForm(on_cancel_callback=cancel_callback)

    # Trigger cancel action
    form.action_cancel()

    # Verify callback was called
    cancel_callback.assert_called_once()


# Tests for CommentsWidget


def test_comments_widget_initialization():
    """Test CommentsWidget can be initialized."""
    widget = CommentsWidget()
    assert widget is not None


def test_comments_widget_empty_state(mock_comments):
    """Test CommentsWidget displays empty state message."""
    widget = CommentsWidget()
    widget.clear = Mock()
    widget.write = Mock()

    # Update with empty comments list
    widget.update_comments([])

    # Verify it was cleared and empty message shown
    widget.clear.assert_called_once()
    widget.write.assert_called_once_with("No comments yet")


def test_comments_widget_with_comments(mock_comments):
    """Test CommentsWidget displays comments correctly."""
    widget = CommentsWidget()
    widget.clear = Mock()
    widget.write = Mock()

    # Update with comments
    widget.update_comments(mock_comments)

    # Verify it was cleared
    widget.clear.assert_called_once()

    # Verify comments were written (2 comments * 2 lines each = 4 writes)
    assert widget.write.call_count >= 2


def test_comments_widget_timestamp_formatting(mock_comments):
    """Test CommentsWidget formats timestamps correctly."""
    widget = CommentsWidget()
    widget.clear = Mock()
    widget.write = Mock()

    # Update with comments
    widget.update_comments(mock_comments)

    # Check that timestamps are formatted
    calls = widget.write.call_args_list
    # First call should include formatted timestamp
    first_call_text = calls[0][0][0]
    assert "2024-01-01 12:10" in first_call_text


# Tests for Conditional Comments Visibility


def test_comments_section_hidden_for_pending_issue(mock_issue_pending, mock_comments):
    """Test that comments section is not shown for pending issues."""
    screen = IssueDetailScreen(issue_id=2)

    # Mock query_one to simulate no CommentsWidget exists
    def mock_query_side_effect(selector, *args):
        if selector == CommentsWidget:
            raise Exception("Widget not found")
        return Mock()

    screen.query_one = Mock(side_effect=mock_query_side_effect)
    screen.refresh_timer = Mock()

    # Display data with pending status
    screen._display_data(mock_issue_pending, mock_comments)

    # Verify that no attempt was made to update comments
    # (because widget shouldn't exist for pending issues)
    assert screen.issue.status == "pending"


def test_comments_section_visible_for_started_issue(mock_issue_started, mock_comments):
    """Test that comments section is shown for started issues."""
    screen = IssueDetailScreen(issue_id=1)

    # Mock widgets
    mock_comments_widget = Mock(spec=CommentsWidget)
    mock_container = Mock()

    def mock_query_side_effect(selector, *args):
        if selector == "#issue-content":
            return Mock()
        elif selector == CommentsWidget:
            return mock_comments_widget
        elif selector == "#detail-container":
            return mock_container
        return Mock()

    screen.query_one = Mock(side_effect=mock_query_side_effect)
    screen.refresh_timer = Mock()
    screen.refresh_timer.resume = Mock()

    # Display data with started status
    screen._display_data(mock_issue_started, mock_comments)

    # Verify comments widget was updated
    mock_comments_widget.update_comments.assert_called_once_with(mock_comments)


def test_comments_section_visible_for_completed_issue(mock_issue_completed, mock_comments):
    """Test that comments section is shown for completed issues."""
    screen = IssueDetailScreen(issue_id=3)

    # Mock widgets
    mock_comments_widget = Mock(spec=CommentsWidget)
    mock_container = Mock()

    def mock_query_side_effect(selector, *args):
        if selector == "#issue-content":
            return Mock()
        elif selector == CommentsWidget:
            return mock_comments_widget
        elif selector == "#detail-container":
            return mock_container
        return Mock()

    screen.query_one = Mock(side_effect=mock_query_side_effect)
    screen.refresh_timer = Mock()

    # Display data with completed status
    screen._display_data(mock_issue_completed, mock_comments)

    # Verify comments widget was updated
    mock_comments_widget.update_comments.assert_called_once_with(mock_comments)


# Tests for 'v' Key Binding


def test_v_key_triggers_view_detail():
    """Test that 'v' key binding triggers action_view_detail method."""
    from cape_cli.tui import IssueListScreen

    # Create screen instance
    screen = IssueListScreen()

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
