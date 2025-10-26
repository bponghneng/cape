"""Cape Issue Management TUI - Textual-based interface for Cape workflows."""

import logging
from typing import Optional, List
from datetime import datetime

from textual.app import App, ComposeResult
from textual.screen import Screen, ModalScreen
from textual.widgets import Header, Footer, DataTable, TextArea, Button, Static, RichLog
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.timer import Timer
from textual import work
from dotenv import load_dotenv

# Import cape_cli modules
from cape_cli.database import fetch_issue, create_issue as db_create_issue, create_comment, fetch_all_issues, fetch_comments, update_issue_description
from cape_cli.models import CapeIssue, CapeComment
from cape_cli.utils import make_adw_id, setup_logger
from cape_cli import workflow

# Load environment variables
load_dotenv()

# Setup logger
logger = logging.getLogger(__name__)


class IssueListScreen(Screen):
    """Main screen displaying issue list in DataTable."""

    BINDINGS = [
        ("n", "new_issue", "New Issue"),
        ("enter", "view_detail", "View Details"),
        ("d", "view_detail", "View Details"),
        ("r", "run_workflow", "Run Workflow"),
        ("q", "quit", "Quit"),
        ("?", "help", "Help"),
    ]

    loading: reactive[bool] = reactive(False)

    def compose(self) -> ComposeResult:
        """Create child widgets for the issue list screen."""
        yield Header(show_clock=True)
        yield Static("Cape Issue Management", id="title")
        yield DataTable(id="issue_table")
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the screen when mounted."""
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.add_column("ID", width=6)
        table.add_column("Description", width=60)
        table.add_column("Status", width=12)
        table.add_column("Created", width=18)
        self.load_issues()

    @work(exclusive=True, thread=True)
    def load_issues(self) -> None:
        """Load issues from database in background thread."""
        try:
            issues = fetch_all_issues()
            self.app.call_from_thread(self._populate_table, issues)
        except Exception as e:
            self.app.call_from_thread(self.notify, f"Error loading issues: {e}", severity="error")

    def _populate_table(self, issues: List[CapeIssue]) -> None:
        """Populate the DataTable with issue data."""
        table = self.query_one(DataTable)
        table.clear()

        if not issues:
            self.notify("No issues found. Press 'n' to create one.", severity="information")
            return

        for issue in issues:
            # Truncate description to 60 characters
            desc = issue.description[:57] + "..." if len(issue.description) > 60 else issue.description

            # Format timestamp
            created = issue.created_at.strftime("%Y-%m-%d %H:%M") if issue.created_at else "Unknown"

            table.add_row(
                str(issue.id),
                desc,
                issue.status,
                created,
                key=str(issue.id)
            )

    def action_new_issue(self) -> None:
        """Show the create issue modal."""
        self.app.push_screen(CreateIssueScreen(), self.on_issue_created)

    def action_view_detail(self) -> None:
        """Navigate to issue detail screen."""
        table = self.query_one(DataTable)
        if table.cursor_row is None or table.cursor_row < 0:
            self.notify("No issue selected", severity="warning")
            return

        row_key = table.get_row_at(table.cursor_row)
        issue_id = int(row_key[0])
        self.app.push_screen(IssueDetailScreen(issue_id))

    def action_run_workflow(self) -> None:
        """Run workflow for selected issue."""
        table = self.query_one(DataTable)
        if table.cursor_row is None or table.cursor_row < 0:
            self.notify("No issue selected", severity="warning")
            return

        row_key = table.get_row_at(table.cursor_row)
        issue_id = int(row_key[0])
        self.app.push_screen(WorkflowScreen(issue_id), self.on_workflow_complete)

    def action_help(self) -> None:
        """Show help screen."""
        self.app.push_screen(HelpScreen())

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()

    def on_issue_created(self, issue_id: Optional[int]) -> None:
        """Callback after issue creation."""
        if issue_id is not None:
            self.notify(f"Issue #{issue_id} created successfully", severity="information")
            self.load_issues()

    def on_workflow_complete(self) -> None:
        """Callback after workflow completion."""
        self.load_issues()


class CreateIssueScreen(ModalScreen[Optional[int]]):
    """Modal form for creating new issues."""

    BINDINGS = [
        ("ctrl+s", "save", "Save"),
        ("escape", "cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the create issue modal."""
        yield Container(
            Static("Create New Issue", id="modal-header"),
            TextArea(id="description", language="markdown"),
            Horizontal(
                Button("Save", variant="success", id="save-btn"),
                Button("Cancel", variant="error", id="cancel-btn"),
                id="button-row"
            ),
            id="create-issue-modal"
        )

    def on_mount(self) -> None:
        """Initialize the modal when mounted."""
        text_area = self.query_one(TextArea)
        text_area.text = "Enter issue description..."
        text_area.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "save-btn":
            self.action_save()
        elif event.button.id == "cancel-btn":
            self.action_cancel()

    def action_save(self) -> None:
        """Save the new issue."""
        text_area = self.query_one(TextArea)
        description = text_area.text.strip()

        # Validation
        if not description or description == "Enter issue description...":
            self.notify("Description cannot be empty", severity="warning")
            return

        if len(description) < 10:
            self.notify("Description must be at least 10 characters", severity="warning")
            return

        if len(description) > 10000:
            self.notify("Description cannot exceed 10,000 characters", severity="warning")
            return

        # Create issue in background
        self.create_issue_handler(description)

    @work(exclusive=True, thread=True)
    def create_issue_handler(self, description: str) -> None:
        """Create issue in background thread."""
        try:
            issue = db_create_issue(description)
            self.app.call_from_thread(self.dismiss, issue.id)
        except Exception as e:
            self.app.call_from_thread(self.notify, f"Error creating issue: {e}", severity="error")

    def action_cancel(self) -> None:
        """Cancel and close the modal."""
        self.dismiss(None)


class EditDescriptionScreen(ModalScreen[bool]):
    """Modal form for editing issue description."""

    BINDINGS = [
        ("ctrl+s", "save", "Save"),
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(self, issue_id: int, current_description: str):
        """Initialize with issue ID and current description."""
        super().__init__()
        self.issue_id = issue_id
        self.current_description = current_description

    def compose(self) -> ComposeResult:
        """Create child widgets for the edit description modal."""
        yield Container(
            Static(f"Edit Issue #{self.issue_id} Description", id="modal-header"),
            TextArea(id="description", language="markdown"),
            Horizontal(
                Button("Save", variant="success", id="save-btn"),
                Button("Cancel", variant="error", id="cancel-btn"),
                id="button-row"
            ),
            id="edit-description-modal"
        )

    def on_mount(self) -> None:
        """Initialize the modal when mounted."""
        text_area = self.query_one(TextArea)
        text_area.text = self.current_description
        text_area.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "save-btn":
            self.action_save()
        elif event.button.id == "cancel-btn":
            self.action_cancel()

    def action_save(self) -> None:
        """Save the updated description."""
        text_area = self.query_one(TextArea)
        description = text_area.text.strip()

        # Validation
        if not description:
            self.notify("Description cannot be empty", severity="warning")
            return

        if len(description) < 10:
            self.notify("Description must be at least 10 characters", severity="warning")
            return

        if len(description) > 10000:
            self.notify("Description cannot exceed 10,000 characters", severity="warning")
            return

        # Update issue in background
        self.update_description_handler(description)

    @work(exclusive=True, thread=True)
    def update_description_handler(self, description: str) -> None:
        """Update issue description in background thread."""
        try:
            update_issue_description(self.issue_id, description)
            self.app.call_from_thread(self.dismiss, True)
        except Exception as e:
            self.app.call_from_thread(self.notify, f"Error updating description: {e}", severity="error")

    def action_cancel(self) -> None:
        """Cancel and close the modal."""
        self.dismiss(False)


class IssueDetailScreen(Screen):
    """Screen showing issue details and comments."""

    BINDINGS = [
        ("escape", "back", "Back"),
        ("e", "edit_description", "Edit Description"),
        ("r", "run_workflow", "Run Workflow"),
    ]

    issue_id: int
    issue: reactive[Optional[CapeIssue]] = reactive(None)
    comments: reactive[List[CapeComment]] = reactive([])
    loading: reactive[bool] = reactive(False)
    auto_refresh_active: reactive[bool] = reactive(False)
    refresh_timer: Optional[Timer] = None

    def __init__(self, issue_id: int):
        """Initialize with issue ID."""
        super().__init__()
        self.issue_id = issue_id

    def compose(self) -> ComposeResult:
        """Create child widgets for the detail screen."""
        yield Header()
        yield Vertical(
            Static("Issue Details", id="detail-header"),
            Static("Loading...", id="issue-content"),
            Static("Comments", id="comments-header"),
            RichLog(id="comments-log"),
            id="detail-container"
        )
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the screen when mounted."""
        # Create a paused timer for auto-refresh (will be activated if issue status is "started")
        self.refresh_timer = self.set_interval(10, lambda: self.load_data(is_refresh=True), pause=True, name="comment_refresh")
        # Initial data load
        self.load_data()

    def on_unmount(self) -> None:
        """Clean up resources when screen is unmounted."""
        # Stop the refresh timer to prevent background API calls
        if self.refresh_timer is not None:
            self.refresh_timer.stop()
            self.auto_refresh_active = False

    @work(exclusive=True, thread=True)
    def load_data(self, is_refresh: bool = False) -> None:
        """Load issue and comments in background thread.

        Args:
            is_refresh: If True, this is a periodic refresh (not initial load)
        """
        try:
            # Show loading indicator for refresh operations
            if is_refresh:
                self.app.call_from_thread(self._set_loading, True)

            issue = fetch_issue(self.issue_id)
            comments = fetch_comments(self.issue_id)
            self.app.call_from_thread(self._display_data, issue, comments)

            # Clear loading indicator
            if is_refresh:
                self.app.call_from_thread(self._set_loading, False)
        except Exception as e:
            # Clear loading indicator
            if is_refresh:
                self.app.call_from_thread(self._set_loading, False)

            # Differentiate between initial load and refresh errors
            if is_refresh:
                # For refresh errors, log but don't show intrusive notification
                logger.warning(f"Auto-refresh failed for issue {self.issue_id}: {e}")
            else:
                # For initial load errors, show error to user
                logger.error(f"Failed to load issue {self.issue_id}: {e}")
                self.app.call_from_thread(self.notify, f"Error loading issue: {e}", severity="error")

    def _set_loading(self, loading: bool) -> None:
        """Set loading state for the comments log."""
        try:
            comments_log = self.query_one(RichLog)
            comments_log.loading = loading
        except Exception:
            # Ignore errors if widget is not yet mounted
            pass

    def _display_data(self, issue: CapeIssue, comments: List[CapeComment]) -> None:
        """Display issue and comments data."""
        # Check if comments have changed (for smart refresh optimization)
        comments_changed = (
            self.comments != comments or
            len(self.comments) != len(comments) or
            self.issue is None or
            self.issue.status != issue.status
        )

        # Store issue for later use
        self.issue = issue
        self.comments = comments

        # Display issue details
        status_color = {
            "pending": "yellow",
            "started": "blue",
            "completed": "green"
        }.get(issue.status, "white")

        created = issue.created_at.strftime("%Y-%m-%d %H:%M") if issue.created_at else "Unknown"
        updated = issue.updated_at.strftime("%Y-%m-%d %H:%M") if issue.updated_at else "Unknown"

        content = f"""[bold]Issue #{issue.id}[/bold]
Status: [{status_color}]{issue.status}[/{status_color}]
Created: {created}
Updated: {updated}

{issue.description}
"""
        self.query_one("#issue-content", Static).update(content)

        # Display comments (only update if changed)
        if comments_changed:
            comments_log = self.query_one(RichLog)
            comments_log.clear()

            if not comments:
                comments_log.write("No comments yet")
            else:
                for comment in comments:
                    timestamp = comment.created_at.strftime("%Y-%m-%d %H:%M") if comment.created_at else "Unknown"
                    comments_log.write(f"[dim]{timestamp}[/dim]\n{comment.comment}\n")

            # Log refresh activity
            if self.auto_refresh_active:
                logger.debug(f"Auto-refresh updated {len(comments)} comments for issue {self.issue_id}")

        # Activate or deactivate auto-refresh based on issue status
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

    def action_back(self) -> None:
        """Return to issue list."""
        self.app.pop_screen()

    def action_edit_description(self) -> None:
        """Edit the issue description if status is pending."""
        if self.issue is None:
            self.notify("Issue not loaded yet", severity="warning")
            return

        if self.issue.status != "pending":
            self.notify(
                "Only pending issues can be edited. This issue is already started or completed.",
                severity="warning"
            )
            return

        self.app.push_screen(EditDescriptionScreen(self.issue_id, self.issue.description), self.on_description_updated)

    def action_run_workflow(self) -> None:
        """Run workflow for this issue."""
        self.app.push_screen(WorkflowScreen(self.issue_id), self.on_workflow_complete)

    def on_description_updated(self, updated: bool) -> None:
        """Callback after description edit."""
        if updated:
            self.notify("Issue description updated", severity="information")
            self.load_data()

    def on_workflow_complete(self) -> None:
        """Callback after workflow completion."""
        self.load_data()


class WorkflowScreen(Screen):
    """Screen for running and monitoring workflows."""

    BINDINGS = [
        ("escape", "back", "Back (after completion)"),
    ]

    issue_id: int
    adw_id: str
    progress: reactive[str] = reactive("Initializing...")
    can_exit: reactive[bool] = reactive(False)

    def __init__(self, issue_id: int):
        """Initialize with issue ID."""
        super().__init__()
        self.issue_id = issue_id
        self.adw_id = make_adw_id()

    def compose(self) -> ComposeResult:
        """Create child widgets for the workflow screen."""
        yield Header()
        yield Vertical(
            Static(f"Workflow Execution - Issue #{self.issue_id}", id="workflow-title"),
            Static("Initializing...", id="workflow-progress"),
            RichLog(id="workflow-log", classes="log"),
            id="workflow-container"
        )
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the screen when mounted."""
        self.run_workflow()

    def watch_progress(self, progress: str) -> None:
        """Update progress display when progress changes."""
        self.query_one("#workflow-progress", Static).update(progress)

    @work(exclusive=True, thread=True)
    def run_workflow(self) -> None:
        """Execute workflow using the centralized execute_workflow function."""
        logger = setup_logger(self.adw_id, "tui_workflow")

        try:
            # Update UI to show workflow is running
            self.app.call_from_thread(self._update_progress, "Running workflow...")
            self.app.call_from_thread(self._log, f"Starting workflow for issue #{self.issue_id}")
            self.app.call_from_thread(self._log, f"ADW ID: {self.adw_id}")
            self.app.call_from_thread(self._log, "See detailed logs in agents/{adw_id}/tui_workflow/execution.log")

            # Execute the complete workflow
            # This handles: fetch, classify, plan, find plan file, implement
            # It also saves progress comments and updates issue status
            success = workflow.execute_workflow(self.issue_id, self.adw_id, logger)

            if success:
                # Success
                self.app.call_from_thread(self._update_progress, "✅ Workflow completed successfully!")
                self.app.call_from_thread(self._log, "✅ Workflow completed successfully!")
                self.app.call_from_thread(self._log, "Check issue details to see progress comments")
            else:
                # Workflow returned False (check logs for details)
                raise ValueError("Workflow execution failed - check logs for details")

            self.app.call_from_thread(self._enable_exit)

        except Exception as e:
            logger.error(f"Workflow error: {e}")
            self.app.call_from_thread(self._update_progress, f"❌ Failed: {e}")
            self.app.call_from_thread(self._log, f"❌ Error: {e}")
            self.app.call_from_thread(self.notify, f"Workflow failed: {e}", severity="error")
            self.app.call_from_thread(self._enable_exit)

    def _update_progress(self, message: str) -> None:
        """Update progress message."""
        self.progress = message

    def _log(self, message: str) -> None:
        """Log message to workflow log."""
        log = self.query_one(RichLog)
        log.write(message)

    def _enable_exit(self) -> None:
        """Enable exiting the workflow screen."""
        self.can_exit = True

    def action_back(self) -> None:
        """Return to previous screen (only after completion)."""
        if self.can_exit:
            self.app.pop_screen()
        else:
            self.notify("Workflow is still running. Please wait...", severity="warning")


class HelpScreen(ModalScreen):
    """Help screen displaying keyboard shortcuts and usage information."""

    BINDINGS = [
        ("escape", "close", "Close"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the help screen."""
        help_text = """# Cape TUI - Help

## Keyboard Shortcuts

### Issue List
- **n**: Create new issue
- **Enter/d**: View issue details
- **r**: Run workflow on selected issue
- **q**: Quit application
- **?**: Show this help screen

### Create Issue
- **Ctrl+S**: Save issue
- **Escape**: Cancel

### Edit Description
- **Ctrl+S**: Save changes
- **Escape**: Cancel

### Issue Detail
- **e**: Edit description (pending issues only)
- **r**: Run workflow
- **Escape**: Back to list

### Workflow Monitor
- **Escape**: Back (after completion)

## Workflow Stages

1. **Fetch**: Retrieve issue from database
2. **Classify**: Determine issue type (feature/bug/chore)
3. **Plan**: Generate implementation plan
4. **Implement**: Execute implementation

## Troubleshooting

- Ensure SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are set in .env
- Check log files in agents/{adw_id}/tui_workflow/execution.log
"""
        yield Container(
            Static(help_text, id="help-content"),
            id="help-modal"
        )

    def action_close(self) -> None:
        """Close the help screen."""
        self.dismiss()


class CapeApp(App):
    """Main Cape TUI application."""

    CSS_PATH = None  # Will load dynamically from package

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("?", "help", "Help"),
    ]

    def __init__(self):
        """Initialize app and load CSS from package resources."""
        super().__init__()
        # Load CSS from package resources
        try:
            from importlib.resources import files
            css_path = files("cape_cli").joinpath("cape_tui.tcss")
            self.CSS = css_path.read_text()
        except Exception as e:
            # Fallback: try to load from current directory (development mode)
            import os
            current_dir = os.path.dirname(__file__)
            css_file = os.path.join(current_dir, "cape_tui.tcss")
            if os.path.exists(css_file):
                with open(css_file) as f:
                    self.CSS = f.read()
            else:
                # Use minimal CSS if file not found
                self.CSS = ""

    def on_mount(self) -> None:
        """Initialize application on mount."""
        # Initialize logger
        adw_id = make_adw_id()
        logger = setup_logger(adw_id, "cape_tui")
        logger.info("Cape TUI application started")

        # Push initial screen
        self.push_screen(IssueListScreen())

    def action_help(self) -> None:
        """Show help screen."""
        self.push_screen(HelpScreen())


if __name__ == "__main__":
    app = CapeApp()
    app.run()
