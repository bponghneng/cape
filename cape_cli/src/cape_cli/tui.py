"""Cape Issue Management TUI - Textual-based interface for Cape workflows."""

import logging
from typing import Optional, List
from datetime import datetime

from textual.app import App, ComposeResult
from textual.screen import Screen, ModalScreen
from textual.widgets import Header, Footer, DataTable, TextArea, Button, Static, RichLog, Collapsible
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
        ("w", "view_workflows", "View Workflows"),
        ("q", "quit", "Quit"),
        ("?", "help", "Help"),
    ]

    loading: reactive[bool] = reactive(False)
    status_timer: Optional[Timer] = None

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
        # Refresh workflow indicators every 5 seconds
        self.status_timer = self.set_interval(5, self.load_issues)

    def on_unmount(self) -> None:
        """Clean up when screen is unmounted."""
        if self.status_timer:
            self.status_timer.stop()

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
        from cape_cli.workflow_monitor import WorkflowMonitor

        table = self.query_one(DataTable)
        table.clear()

        if not issues:
            self.notify("No issues found. Press 'n' to create one.", severity="information")
            return

        # Get all active workflows for status indicators
        try:
            all_workflows = WorkflowMonitor.list_active_workflows()
            workflows_by_issue = {}
            for wf in all_workflows:
                if wf.issue_id not in workflows_by_issue:
                    workflows_by_issue[wf.issue_id] = []
                workflows_by_issue[wf.issue_id].append(wf)
        except Exception:
            workflows_by_issue = {}

        for issue in issues:
            # Truncate description to 60 characters
            desc = issue.description[:57] + "..." if len(issue.description) > 60 else issue.description

            # Format timestamp
            created = issue.created_at.strftime("%Y-%m-%d %H:%M") if issue.created_at else "Unknown"

            # Add workflow status indicator
            status_indicator = ""
            if issue.id in workflows_by_issue:
                workflows = workflows_by_issue[issue.id]
                # Check for different workflow states
                has_running = any(w.status in ["initializing", "running"] for w in workflows)
                has_failed = any(w.status == "failed" for w in workflows)

                if has_running:
                    status_indicator = " ⏳"  # Running workflow
                elif has_failed:
                    status_indicator = " ❌"  # Failed workflow

            table.add_row(
                str(issue.id),
                desc,
                issue.status + status_indicator,
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

    def action_view_workflows(self) -> None:
        """View all active workflows."""
        self.app.push_screen(WorkflowsScreen())

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
        ("w", "view_workflows", "View Workflows"),
        ("s", "stop_workflow", "Stop Active Workflow"),
    ]

    issue_id: int
    issue: reactive[Optional[CapeIssue]] = reactive(None)
    comments: reactive[List[CapeComment]] = reactive([])
    loading: reactive[bool] = reactive(False)
    auto_refresh_active: reactive[bool] = reactive(False)
    refresh_timer: Optional[Timer] = None
    workflow_timer: Optional[Timer] = None

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
            Static("Active Workflows", id="workflows-header"),
            Static("No active workflows", id="workflows-content"),
            Static("Comments", id="comments-header"),
            RichLog(id="comments-log"),
            id="detail-container"
        )
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the screen when mounted."""
        # Create a paused timer for auto-refresh (will be activated if issue status is "started")
        self.refresh_timer = self.set_interval(10, lambda: self.load_data(is_refresh=True), pause=True, name="comment_refresh")
        # Create timer for workflow status updates
        self.workflow_timer = self.set_interval(5, self.update_workflows_display, name="workflow_refresh")
        # Initial data load
        self.load_data()

    def on_unmount(self) -> None:
        """Clean up resources when screen is unmounted."""
        # Stop the refresh timer to prevent background API calls
        if self.refresh_timer is not None:
            self.refresh_timer.stop()
            self.auto_refresh_active = False
        # Stop the workflow timer
        if self.workflow_timer is not None:
            self.workflow_timer.stop()

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

        # Check for active workflows
        from cape_cli.workflow_monitor import WorkflowMonitor
        try:
            all_workflows = WorkflowMonitor.list_active_workflows()
            issue_workflows = [w for w in all_workflows if w.issue_id == issue.id]
            workflow_indicator = " 🟢" if issue_workflows else ""
        except Exception:
            workflow_indicator = ""

        content = f"""[bold]Issue #{issue.id}{workflow_indicator}[/bold]
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

    def update_workflows_display(self) -> None:
        """Update the display of active workflows for this issue."""
        from cape_cli.workflow_monitor import WorkflowMonitor

        try:
            # Get all active workflows
            all_workflows = WorkflowMonitor.list_active_workflows()

            # Filter for this issue
            issue_workflows = [w for w in all_workflows if w.issue_id == self.issue_id]

            if not issue_workflows:
                workflows_content = "[dim]No active workflows[/dim]"
            else:
                workflows_parts = []
                for wf in issue_workflows:
                    elapsed = datetime.now() - wf.started_at
                    elapsed_str = str(elapsed).split('.')[0]  # HH:MM:SS

                    status_color = {
                        "initializing": "yellow",
                        "running": "blue",
                        "completed": "green",
                        "failed": "red",
                        "stopped": "dim"
                    }.get(wf.status, "white")

                    step_info = f" - {wf.current_step}" if wf.current_step else ""

                    workflows_parts.append(
                        f"🔄 [{status_color}]{wf.status}[/{status_color}]{step_info} "
                        f"[dim]({elapsed_str}) - ID: {wf.workflow_id[:8]}...[/dim]"
                    )

                workflows_content = "\n".join(workflows_parts)

            self.query_one("#workflows-content", Static).update(workflows_content)

        except Exception as e:
            logger.warning(f"Error updating workflows display: {e}")

    def action_view_workflows(self) -> None:
        """View all workflows for this issue."""
        # For now, just show a notification
        # This could be expanded to show a detailed modal
        from cape_cli.workflow_monitor import WorkflowMonitor

        all_workflows = WorkflowMonitor.list_active_workflows()
        issue_workflows = [w for w in all_workflows if w.issue_id == self.issue_id]

        if not issue_workflows:
            self.notify("No active workflows for this issue", severity="information")
        else:
            count = len(issue_workflows)
            self.notify(f"Found {count} active workflow(s) - see 'Active Workflows' section above", severity="information")

    def action_stop_workflow(self) -> None:
        """Stop the most recent active workflow for this issue."""
        from cape_cli.workflow_monitor import WorkflowMonitor
        from cape_cli.workflow_launcher import WorkflowLauncher

        # Get all active workflows for this issue
        all_workflows = WorkflowMonitor.list_active_workflows()
        issue_workflows = [w for w in all_workflows if w.issue_id == self.issue_id]

        if not issue_workflows:
            self.notify("No active workflows to stop", severity="warning")
            return

        # Stop the most recent one
        workflow = issue_workflows[-1]

        try:
            self.notify(f"Stopping workflow {workflow.workflow_id[:8]}...", severity="information")
            success = WorkflowLauncher.stop_workflow(workflow.workflow_id, timeout=30)

            if success:
                self.notify("Workflow stopped successfully", severity="information")
            else:
                self.notify("Failed to stop workflow", severity="warning")

        except Exception as e:
            logger.error(f"Error stopping workflow: {e}")
            self.notify(f"Error stopping workflow: {e}", severity="error")

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
        ("escape", "back", "Back"),
        ("s", "stop_workflow", "Stop Workflow"),
    ]

    issue_id: int
    adw_id: str
    workflow_id: Optional[str] = None
    progress: reactive[str] = reactive("Initializing...")
    status_timer: Optional[Timer] = None

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
            Horizontal(
                Button("Stop Workflow", variant="error", id="stop-btn"),
                id="workflow-buttons"
            ),
            id="workflow-container"
        )
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the screen when mounted."""
        self.launch_workflow()
        # Poll workflow status every 2 seconds
        self.status_timer = self.set_interval(2, self.update_workflow_status)

    def on_unmount(self) -> None:
        """Clean up when screen is unmounted."""
        if self.status_timer:
            self.status_timer.stop()

    def launch_workflow(self) -> None:
        """Launch workflow as detached background process."""
        from cape_cli.workflow_launcher import WorkflowLauncher

        try:
            self._log(f"Launching workflow for issue #{self.issue_id}")
            self._log(f"Workflow ID: {self.adw_id}")

            # Launch the workflow
            workflow_id = WorkflowLauncher.launch_workflow(self.issue_id, self.adw_id)
            self.workflow_id = workflow_id

            self._update_progress("Workflow launched - running in background...")
            self._log("✅ Workflow launched successfully")
            self._log("You can close this screen - the workflow will continue running")
            self._log("Press 'Escape' to return, or 's' to stop the workflow")

        except Exception as e:
            logger.error(f"Failed to launch workflow: {e}")
            self._update_progress(f"❌ Launch failed: {e}")
            self._log(f"❌ Error: {e}")
            self.notify(f"Failed to launch workflow: {e}", severity="error")

    def update_workflow_status(self) -> None:
        """Poll workflow status and update UI."""
        if not self.workflow_id:
            return

        from cape_cli.workflow_monitor import WorkflowMonitor

        try:
            # Get workflow progress
            progress = WorkflowMonitor.get_workflow_progress(self.workflow_id)

            if not progress:
                return

            # Update progress message
            status = progress["status"]
            current_step = progress["current_step"] or "waiting"
            elapsed = progress["elapsed_str"]

            if status == "completed":
                self._update_progress(f"✅ Completed in {elapsed}")
                self._log(f"✅ Workflow completed successfully after {elapsed}")
                if self.status_timer:
                    self.status_timer.stop()
            elif status == "failed":
                error_msg = progress.get("error_message", "Unknown error")
                self._update_progress(f"❌ Failed: {error_msg}")
                self._log(f"❌ Workflow failed: {error_msg}")
                if self.status_timer:
                    self.status_timer.stop()
            elif status == "stopped":
                self._update_progress(f"⏹ Stopped by user after {elapsed}")
                self._log(f"⏹ Workflow stopped after {elapsed}")
                if self.status_timer:
                    self.status_timer.stop()
            else:
                # Running or initializing
                self._update_progress(f"⏳ {status.capitalize()}: {current_step} ({elapsed})")

        except Exception as e:
            logger.warning(f"Error updating workflow status: {e}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "stop-btn":
            self.action_stop_workflow()

    def action_stop_workflow(self) -> None:
        """Stop the running workflow."""
        if not self.workflow_id:
            self.notify("No workflow running", severity="warning")
            return

        from cape_cli.workflow_launcher import WorkflowLauncher

        try:
            self._log("Sending stop signal to workflow...")
            self._update_progress("Stopping workflow...")

            success = WorkflowLauncher.stop_workflow(self.workflow_id, timeout=30)

            if success:
                self._log("✅ Workflow stopped successfully")
                self._update_progress("⏹ Workflow stopped")
                self.notify("Workflow stopped", severity="information")
            else:
                self._log("❌ Failed to stop workflow (may have already completed)")
                self.notify("Failed to stop workflow", severity="warning")

        except Exception as e:
            logger.error(f"Error stopping workflow: {e}")
            self._log(f"❌ Error stopping workflow: {e}")
            self.notify(f"Error stopping workflow: {e}", severity="error")

    def watch_progress(self, progress: str) -> None:
        """Update progress display when progress changes."""
        self.query_one("#workflow-progress", Static).update(progress)

    def _update_progress(self, message: str) -> None:
        """Update progress message."""
        self.progress = message

    def _log(self, message: str) -> None:
        """Log message to workflow log."""
        log = self.query_one(RichLog)
        log.write(message)

    def action_back(self) -> None:
        """Return to previous screen."""
        # Can exit immediately - workflow continues in background
        self.app.pop_screen()


class WorkflowLogsModal(ModalScreen):
    """Modal showing workflow logs."""

    BINDINGS = [
        ("escape", "close", "Close"),
    ]

    def __init__(self, workflow_id: str):
        """Initialize with workflow ID."""
        super().__init__()
        self.workflow_id = workflow_id

    def compose(self) -> ComposeResult:
        """Create child widgets for the modal."""
        from cape_cli.workflow_monitor import WorkflowMonitor

        logs = WorkflowMonitor.get_workflow_logs(self.workflow_id, lines=100)

        if logs:
            log_content = "".join(logs)
        else:
            log_content = "No logs available for this workflow"

        yield Container(
            Static(f"Workflow Logs - {self.workflow_id[:16]}...", id="logs-modal-header"),
            RichLog(id="logs-modal-content"),
            id="logs-modal"
        )

    def on_mount(self) -> None:
        """Populate logs when mounted."""
        from cape_cli.workflow_monitor import WorkflowMonitor

        logs = WorkflowMonitor.get_workflow_logs(self.workflow_id, lines=100)
        log_widget = self.query_one(RichLog)

        if logs:
            for line in logs:
                log_widget.write(line.rstrip())
        else:
            log_widget.write("No logs available for this workflow")

    def action_close(self) -> None:
        """Close the modal."""
        self.dismiss()


class WorkflowDetailModal(ModalScreen):
    """Modal showing detailed workflow information."""

    BINDINGS = [
        ("escape", "close", "Close"),
    ]

    def __init__(self, workflow_id: str):
        """Initialize with workflow ID."""
        super().__init__()
        self.workflow_id = workflow_id

    def compose(self) -> ComposeResult:
        """Create child widgets for the modal."""
        from cape_cli.workflow_monitor import WorkflowMonitor

        state = WorkflowMonitor.get_workflow_status(self.workflow_id, use_cache=False)

        if not state:
            detail_text = f"Workflow {self.workflow_id} not found"
        else:
            elapsed = datetime.now() - state.started_at
            elapsed_str = str(elapsed).split('.')[0]

            detail_text = f"""# Workflow Details

**Workflow ID:** {state.workflow_id}
**Issue ID:** #{state.issue_id}
**Status:** {state.status}
**Current Step:** {state.current_step or "N/A"}
**Started:** {state.started_at.strftime("%Y-%m-%d %H:%M:%S")}
**Elapsed Time:** {elapsed_str}
**PID:** {state.pid}

"""
            if state.error_message:
                detail_text += f"**Error:** {state.error_message}\n\n"

            # Get recent logs
            logs = WorkflowMonitor.get_workflow_logs(self.workflow_id, lines=20)
            if logs:
                detail_text += "## Recent Logs\n\n```\n"
                detail_text += "".join(logs)
                detail_text += "```"
            else:
                detail_text += "## Recent Logs\n\nNo logs available"

        yield Container(
            Static(detail_text, id="workflow-detail-content"),
            id="workflow-detail-modal"
        )

    def action_close(self) -> None:
        """Close the modal."""
        self.dismiss()


class WorkflowsScreen(Screen):
    """Screen showing all active workflows in a table."""

    BINDINGS = [
        ("escape", "back", "Back"),
        ("enter", "view_detail", "View Details"),
        ("s", "stop_workflow", "Stop Workflow"),
        ("l", "view_logs", "View Logs"),
        ("r", "refresh", "Refresh"),
    ]

    refresh_timer: Optional[Timer] = None

    def compose(self) -> ComposeResult:
        """Create child widgets for the workflows screen."""
        yield Header()
        yield Static("Active Workflows", id="workflows-title")
        yield DataTable(id="workflows-table")
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the screen when mounted."""
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.add_column("Workflow ID", width=20)
        table.add_column("Issue ID", width=10)
        table.add_column("Status", width=15)
        table.add_column("Step", width=20)
        table.add_column("Elapsed", width=12)
        self.load_workflows()
        # Auto-refresh every 3 seconds
        self.refresh_timer = self.set_interval(3, self.load_workflows)

    def on_unmount(self) -> None:
        """Clean up when screen is unmounted."""
        if self.refresh_timer:
            self.refresh_timer.stop()

    def load_workflows(self) -> None:
        """Load workflows into the table."""
        from cape_cli.workflow_monitor import WorkflowMonitor

        try:
            workflows = WorkflowMonitor.list_active_workflows()
            self._populate_table(workflows)
        except Exception as e:
            logger.error(f"Error loading workflows: {e}")
            self.notify(f"Error loading workflows: {e}", severity="error")

    def _populate_table(self, workflows: List) -> None:
        """Populate the DataTable with workflow data."""
        table = self.query_one(DataTable)
        table.clear()

        if not workflows:
            # Don't show notification on refresh - empty table is self-explanatory
            return

        for wf in workflows:
            elapsed = datetime.now() - wf.started_at
            elapsed_str = str(elapsed).split('.')[0]

            # Truncate workflow ID for display
            wf_id_display = wf.workflow_id[:18] + "..." if len(wf.workflow_id) > 20 else wf.workflow_id

            table.add_row(
                wf_id_display,
                str(wf.issue_id),
                wf.status,
                wf.current_step or "N/A",
                elapsed_str,
                key=wf.workflow_id
            )

    def action_refresh(self) -> None:
        """Manually refresh the workflows."""
        self.load_workflows()
        self.notify("Workflows refreshed", severity="information")

    def action_view_detail(self) -> None:
        """View details for selected workflow."""
        table = self.query_one(DataTable)

        # Check if table has any rows
        if table.row_count == 0:
            self.notify("No workflows available", severity="warning")
            return

        if table.cursor_row is None or table.cursor_row < 0:
            self.notify("No workflow selected", severity="warning")
            return

        try:
            workflow_id = table.get_row_key_for_row(table.cursor_row)

            if workflow_id is None:
                self.notify("Invalid workflow selected", severity="warning")
                return

            self.app.push_screen(WorkflowDetailModal(str(workflow_id)))

        except Exception as e:
            logger.error(f"Error viewing workflow details: {e}")
            self.notify(f"Error viewing details: {e}", severity="error")

    def action_stop_workflow(self) -> None:
        """Stop selected workflow."""
        table = self.query_one(DataTable)

        # Check if table has any rows
        if table.row_count == 0:
            self.notify("No workflows available", severity="warning")
            return

        if table.cursor_row is None or table.cursor_row < 0:
            self.notify("No workflow selected", severity="warning")
            return

        try:
            workflow_id = table.get_row_key_for_row(table.cursor_row)

            if workflow_id is None:
                self.notify("Invalid workflow selected", severity="warning")
                return

            from cape_cli.workflow_launcher import WorkflowLauncher

            self.notify(f"Stopping workflow...", severity="information")
            success = WorkflowLauncher.stop_workflow(str(workflow_id), timeout=30)

            if success:
                self.notify("Workflow stopped successfully", severity="information")
                self.load_workflows()
            else:
                self.notify("Failed to stop workflow", severity="warning")

        except Exception as e:
            logger.error(f"Error stopping workflow: {e}")
            self.notify(f"Error stopping workflow: {e}", severity="error")

    def action_view_logs(self) -> None:
        """View logs for selected workflow."""
        table = self.query_one(DataTable)

        # Check if table has any rows
        if table.row_count == 0:
            self.notify("No workflows available", severity="warning")
            return

        if table.cursor_row is None or table.cursor_row < 0:
            self.notify("No workflow selected", severity="warning")
            return

        try:
            workflow_id = table.get_row_key_for_row(table.cursor_row)

            if workflow_id is None:
                self.notify("Invalid workflow selected", severity="warning")
                return

            # Open logs modal
            self.app.push_screen(WorkflowLogsModal(str(workflow_id)))

        except Exception as e:
            logger.error(f"Error viewing logs: {e}")
            self.notify(f"Error viewing logs: {e}", severity="error")

    def action_back(self) -> None:
        """Return to previous screen."""
        self.app.pop_screen()


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
- **w**: View all active workflows
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
- **w**: View workflows for this issue
- **s**: Stop active workflow
- **Escape**: Back to list

### Workflow Monitor
- **s**: Stop workflow
- **Escape**: Back to list

### Active Workflows Screen
- **Enter**: View workflow details
- **s**: Stop selected workflow
- **l**: View workflow logs
- **r**: Refresh list
- **Escape**: Back to list

## Background Workflows

Workflows now run as background processes that continue even after you close the TUI.
This means you can:
- Start a workflow and close the TUI
- Come back later to check progress
- Monitor multiple workflows simultaneously
- Stop running workflows at any time

## Workflow Status Indicators

- **⏳**: Workflow is currently running
- **❌**: Workflow has failed
- **🟢**: Active workflow indicator (in issue details)

## Workflow Stages

1. **Fetch**: Retrieve issue from database
2. **Classify**: Determine issue type (feature/bug/chore)
3. **Plan**: Generate implementation plan
4. **Implement**: Execute implementation

## Troubleshooting

- Ensure SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are set in .env
- Check log files in agents/{adw_id}/adw_plan_build/execution.log
- Use 'w' to view all active workflows and their status
- Workflows are stored in ~/.cape/ directory
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
        tui_logger = setup_logger(adw_id, "cape_tui")
        tui_logger.info("Cape TUI application started")

        # Discover and recover workflows
        self._discover_workflows(tui_logger)

        # Push initial screen
        self.push_screen(IssueListScreen())

    def _discover_workflows(self, tui_logger: logging.Logger) -> None:
        """Discover active workflows and clean up stale state."""
        from cape_cli.pid_manager import PIDFileManager

        try:
            tui_logger.info("Discovering active workflows...")

            # Clean up stale PIDs first
            PIDFileManager.cleanup_stale_pids()

            # Discover active workflows
            active_workflows = PIDFileManager.discover_workflows()

            if active_workflows:
                count = len(active_workflows)
                tui_logger.info(f"Found {count} active workflow(s)")
                self.notify(
                    f"Found {count} active workflow(s) - Press 'w' to view",
                    severity="information",
                    timeout=5
                )

                # Log details about each workflow
                for workflow_id, pid, state in active_workflows:
                    if state:
                        tui_logger.info(
                            f"  - Workflow {workflow_id[:8]}... "
                            f"(Issue #{state.issue_id}, Status: {state.status})"
                        )
            else:
                tui_logger.info("No active workflows found")

            # Recover orphaned workflows (workflows with state files but no PID)
            PIDFileManager.recover_orphaned_workflows()

        except Exception as e:
            tui_logger.error(f"Error during workflow discovery: {e}")
            logger.error(f"Workflow discovery error: {e}")

    def action_help(self) -> None:
        """Show help screen."""
        self.push_screen(HelpScreen())


if __name__ == "__main__":
    app = CapeApp()
    app.run()
