# Feature: Decouple TUI from Workflow Execution

## Description

Re-architect the CAPE CLI application to run workflows as independent background processes that are detached from the TUI lifecycle. Currently, workflows execute as subprocess calls within TUI threads and terminate when the TUI closes. This feature enables workflows to run persistently in the background, allowing users to close the TUI and return later to check progress. The TUI will monitor workflow progress by observing PID files, state files, and log files in the local file system.

This architectural change improves user experience by providing operational flexibility, enhances reliability by decoupling execution from UI lifecycle, and establishes a foundation for advanced features like workflow scheduling and distributed execution.

## User Story

As a CAPE CLI user
I want to launch workflows that continue running after I close the TUI
So that I can close the terminal, perform other tasks, and return later to check workflow progress without interrupting long-running operations

## Problem Statement

The current CAPE CLI architecture tightly couples workflow execution to the TUI process lifecycle. Workflows are executed as background threads within the TUI using Textual's `@work` decorator, which means:

1. **Forced User Engagement**: Users must keep the TUI open for the entire workflow duration (potentially hours)
2. **Resource Waste**: The TUI consumes terminal resources even when user attention isn't needed
3. **Fragility**: Accidental TUI termination (network disconnection, laptop sleep, Ctrl+C) kills workflows
4. **Limited Monitoring**: Users cannot check workflow status from multiple TUI instances or external tools
5. **No Recovery**: Crashed TUI processes leave workflows in unknown states with no recovery mechanism

These limitations prevent CAPE CLI from being used effectively in production environments where long-running automated tasks are common.

## Solution Statement

Implement a process-based architecture that separates workflow execution from TUI monitoring:

**Architecture Components**:
1. **Workflow Daemon**: Standalone Python process that executes workflows independently
2. **Process Manager**: Launches workflows as detached processes using `subprocess.Popen()` with `start_new_session=True`
3. **State Synchronization**: File-based state management using PID files, JSON state files, and log files
4. **TUI Monitor**: Polling and event-driven monitoring of workflow state via file watchers
5. **Signal Handling**: Graceful shutdown via SIGTERM signals with cleanup

**Key Technical Decisions**:
- Use `subprocess.Popen(start_new_session=True)` for true process detachment (not python-daemon, for simplicity)
- Store runtime data in `~/.cape/` directory (PID files, state files, logs)
- Leverage `watchdog` library for efficient file system event monitoring
- Maintain backward compatibility with optional synchronous execution mode
- Use Pydantic models for state file schema validation

**User Experience Flow**:
1. User launches workflow from TUI → workflow starts as background process
2. TUI displays real-time progress by watching state file
3. User closes TUI → workflow continues running
4. User reopens TUI → discovers active workflows and resumes monitoring
5. User can stop workflow via TUI → sends SIGTERM signal to process

This solution provides the flexibility of background execution while maintaining the familiar TUI interface for monitoring and control.

## Relevant Files

### Core Application Files

#### `/Users/bponghneng/git/cape/cape_cli/src/cape_cli/tui.py`
**Why Relevant**: Main TUI application that needs refactoring to launch and monitor detached workflows.

**Key Sections**:
- `WorkflowScreen` class (lines 504-538): Currently uses `@work` decorator for synchronous execution
  ```python
  @work(exclusive=True, thread=True)
  def run_workflow(self) -> None:
      success = workflow.execute_workflow(self.issue_id, self.adw_id, logger)
  ```
- `IssueDetailScreen` class: Auto-refresh mechanism (10-second timer) can be extended for workflow monitoring
- `CapeApp.on_mount()`: Needs workflow discovery on startup

**Changes Needed**:
- Replace `@work` decorator with `WorkflowLauncher.launch_workflow()`
- Add state file polling with `set_interval()`
- Register state watcher callbacks for real-time updates
- Add "Stop Workflow" button and action
- Allow immediate exit without blocking on workflow completion

---

#### `/Users/bponghneng/git/cape/cape_cli/src/cape_cli/workflow.py`
**Why Relevant**: Workflow orchestration logic that needs state update hooks.

**Key Functions**:
- `execute_workflow(issue_id, adw_id, logger)`: Main workflow pipeline
  ```python
  def execute_workflow(issue_id: int, adw_id: str, logger: logging.Logger) -> bool:
      # Classification → Planning → Implementation
  ```

**Changes Needed**:
- Add optional `state_manager` parameter to all workflow functions
- Insert `state_manager.update_state()` calls at key milestones:
  - Before classification: `current_step="classify"`
  - Before planning: `current_step="plan"`
  - Before implementation: `current_step="implement"`
- Ensure state updates are non-blocking and don't fail workflow on error
- Maintain backward compatibility (state_manager optional)

---

#### `/Users/bponghneng/git/cape/cape_cli/src/cape_cli/agent.py`
**Why Relevant**: Subprocess execution of Claude Code CLI.

**Key Function**:
- `prompt_claude_code()` (lines 186-188): Uses `subprocess.run()` for synchronous execution
  ```python
  result = subprocess.run(
      cmd, stdout=f, stderr=subprocess.PIPE, text=True, env=env
  )
  ```

**Changes Needed**:
- No direct changes needed (agent.py can remain synchronous)
- The workflow daemon will call agent.py as-is
- Consider adding process ID logging for traceability

---

#### `/Users/bponghneng/git/cape/cape_cli/src/cape_cli/utils.py`
**Why Relevant**: Logging infrastructure that needs enhancement for detached processes.

**Key Function**:
- `setup_logger()`: Creates dual console/file loggers

**Changes Needed**:
- Add `detached_mode` parameter to disable console handler
- Add rotating file handler option (`RotatingFileHandler`)
- Ensure log directory creation is atomic
- Add structured logging helper: `log_workflow_event()`

---

#### `/Users/bponghneng/git/cape/cape_cli/src/cape_cli/models.py`
**Why Relevant**: Pydantic data models for type safety.

**Changes Needed**:
- Add `WorkflowState` model:
  ```python
  class WorkflowState(BaseModel):
      workflow_id: str
      issue_id: int
      status: Literal["initializing", "running", "completed", "failed", "stopped"]
      pid: int
      started_at: datetime
      updated_at: datetime
      current_step: Optional[str] = None
      error_message: Optional[str] = None
  ```

---

#### `/Users/bponghneng/git/cape/cape_cli/src/cape_cli/cli.py`
**Why Relevant**: CLI commands need workflow management extensions.

**Changes Needed**:
- Add new commands:
  - `cape workflow start <issue_id>` - Launch workflow in background
  - `cape workflow list` - List active workflows
  - `cape workflow status <workflow_id>` - Show workflow status
  - `cape workflow stop <workflow_id>` - Stop workflow
  - `cape workflow logs <workflow_id>` - Show workflow logs
  - `cape workflow cleanup` - Clean up stale PIDs

---

#### `/Users/bponghneng/git/cape/cape_cli/pyproject.toml`
**Why Relevant**: Dependency management.

**Changes Needed**:
- Add dependencies:
  ```toml
  [project.dependencies]
  watchdog = ">=6.0.0"
  psutil = ">=6.1.0"
  ```

---

### New Files

#### `src/cape_cli/paths.py`
**Purpose**: Centralized path management for runtime directories.

**Implementation**:
```python
from pathlib import Path
import os

class CapePaths:
    """Manage CAPE directory structure following XDG Base Directory specification."""

    @staticmethod
    def get_runtime_dir() -> Path:
        """Get runtime directory for PID files."""
        base = os.getenv("CAPE_RUNTIME_DIR") or Path.home() / ".cape"
        return base / "pids"

    @staticmethod
    def get_state_dir() -> Path:
        """Get state directory for workflow state files."""
        base = os.getenv("CAPE_DATA_DIR") or Path.home() / ".cape"
        return base / "state"

    @staticmethod
    def get_logs_dir() -> Path:
        """Get logs directory for workflow logs."""
        base = os.getenv("CAPE_DATA_DIR") or Path.home() / ".cape"
        return base / "logs"
```

---

#### `src/cape_cli/pid_manager.py`
**Purpose**: Robust PID file management with stale PID detection.

**Key Features**:
- Atomic PID file writes (temp file + rename)
- Stale PID cleanup using `os.kill(pid, 0)` checks
- Process validation by checking cmdline
- List active workflows
- Context manager support

---

#### `src/cape_cli/state_manager.py`
**Purpose**: Workflow state file management with JSON schema.

**Key Features**:
- Atomic JSON writes for state files
- Pydantic validation for state schema
- Partial state updates
- Datetime serialization (ISO 8601)

---

#### `src/cape_cli/process_utils.py`
**Purpose**: Process management utilities.

**Key Features**:
- Check if process is alive (`os.kill(pid, 0)` or psutil)
- Send signals with error handling
- Graceful termination (SIGTERM → wait → SIGKILL)
- Get process information (cmdline, status)

---

#### `src/cape_cli/state_watcher.py`
**Purpose**: File system watcher for state changes.

**Key Features**:
- Uses `watchdog` library for event-driven monitoring
- Callback registration for state changes
- Debouncing to prevent duplicate events
- Observer lifecycle management

---

#### `src/cape_cli/workflow_launcher.py`
**Purpose**: Launch workflows as detached background processes.

**Key Features**:
- Launch workflow using `subprocess.Popen(start_new_session=True)`
- Create PID and state files on launch
- Stop workflow via SIGTERM signal
- Update Supabase issue status (best-effort)

---

#### `src/cape_cli/workflow_daemon.py`
**Purpose**: Standalone daemon entry point for workflow execution.

**Key Features**:
- Command-line entry point: `python -m cape_cli.workflow_daemon <issue_id> <adw_id>`
- Signal handlers for SIGTERM/SIGINT
- State updates during execution
- PID file cleanup on exit
- Detached logging

---

#### `src/cape_cli/workflow_monitor.py`
**Purpose**: Query and monitor workflow status.

**Key Features**:
- Get workflow status from state files
- List active workflows
- Tail workflow logs
- Wait for workflow completion with timeout
- Caching with TTL to reduce file I/O

---

## Implementation Plan

### Phase 1: Foundation

Establish the infrastructure for process management and state synchronization before implementing workflow execution changes.

### Phase 2: Core Implementation

Implement the workflow launcher, daemon entry point, and monitoring capabilities.

### Phase 3: Integration

Integrate background workflows into the TUI, add comprehensive testing, and polish the user experience.

## Step by Step Tasks

### Task 1: Create CAPE Directory Structure

- Create `src/cape_cli/paths.py` module
- Implement `CapePaths` class with methods: `get_runtime_dir()`, `get_pids_dir()`, `get_logs_dir()`, `get_state_dir()`
- Follow XDG Base Directory specification: use `~/.cape/` as base directory
- Add environment variable overrides: `CAPE_DATA_DIR`, `CAPE_RUNTIME_DIR`
- Ensure atomic directory creation with proper permissions (0755)
- Write unit tests in `tests/test_paths.py`
- Test directory creation, environment variable override, and permission handling

### Task 2: Create PID File Management Infrastructure

- Create `src/cape_cli/pid_manager.py` with `PIDFileManager` class
- Implement `write_pid(workflow_id, pid)` using atomic file operations (temp file + rename)
- Implement `read_pid(workflow_id)` with error handling for missing/corrupted files
- Implement `delete_pid(workflow_id)` with safe deletion
- Implement `is_process_running(pid)` using `os.kill(pid, 0)` signal check
- Implement `cleanup_stale_pids()` to remove PIDs for terminated processes
- Implement `list_active_workflows()` to enumerate running workflows
- Write comprehensive unit tests in `tests/test_pid_manager.py`
- Test edge cases: missing files, invalid PIDs, permission errors, concurrent access

### Task 3: Create Workflow State File Schema

- Add `WorkflowState` Pydantic model to `src/cape_cli/models.py` with fields:
  - `workflow_id: str`, `issue_id: int`, `status: Literal[...]`, `pid: int`
  - `started_at: datetime`, `updated_at: datetime`
  - `current_step: Optional[str]`, `error_message: Optional[str]`
- Create `src/cape_cli/state_manager.py` with `StateManager` class
- Implement `write_state(state: WorkflowState)` with atomic JSON write
- Implement `read_state(workflow_id)` with JSON parsing and Pydantic validation
- Implement `update_state(workflow_id, **updates)` for partial updates
- Implement `delete_state(workflow_id)` for cleanup
- Handle datetime serialization/deserialization (ISO 8601 format)
- Write unit tests in `tests/test_state_manager.py`
- Test JSON serialization, validation, and concurrent access

### Task 4: Add Process Utilities Module

- Create `src/cape_cli/process_utils.py` module
- Implement `is_process_alive(pid)` using `psutil` if available, fallback to `os.kill(pid, 0)`
- Implement `send_signal(pid, signal)` with error handling
- Implement `terminate_process(pid, timeout=30)` with SIGTERM → wait → SIGKILL escalation
- Implement `get_process_info(pid)` returning process details (cmdline, status)
- Add `psutil>=6.1.0` to `pyproject.toml` dependencies
- Write unit tests in `tests/test_process_utils.py`
- Mock process interactions for deterministic testing

### Task 5: Implement File System Watcher for State Changes

- Add `watchdog>=6.0.0` to `pyproject.toml` dependencies
- Create `src/cape_cli/state_watcher.py` with `StateWatcher` class
- Implement observer pattern using `watchdog.observers.Observer`
- Create `StateFileEventHandler` extending `watchdog.events.FileSystemEventHandler`
- Add callback registration: `register_callback(workflow_id, callback_fn)`
- Implement debouncing to prevent duplicate events (100ms window)
- Add `start()` and `stop()` methods for observer lifecycle
- Write unit tests in `tests/test_state_watcher.py`
- Test event triggering with temporary file modifications

### Task 6: Update Utils Module for Background Logging

- Update `setup_logger()` in `src/cape_cli/utils.py` to add `detached_mode` parameter
- In detached mode, disable console handler (stdout/stderr may be closed)
- Add rotating file handler option with `RotatingFileHandler` (10MB per file, 5 backups)
- Ensure log directory creation is atomic and handles race conditions
- Add structured logging helper: `log_workflow_event(logger, step, status, details)`
- Write unit tests in `tests/test_utils.py` for new logging features
- Verify logs persist correctly when parent process exits

### Task 7: Create Workflow Launcher Module

- Create `src/cape_cli/workflow_launcher.py` with `WorkflowLauncher` class
- Implement `launch_workflow(issue_id, adw_id)` method:
  - Build command: `["python", "-m", "cape_cli.workflow_daemon", str(issue_id), adw_id]`
  - Use `subprocess.Popen()` with `start_new_session=True` for detachment
  - Set `stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True`
  - Write PID file using `PIDFileManager`
  - Create initial state file with "initializing" status
  - Update issue status to "started" in Supabase (best-effort)
- Implement `stop_workflow(workflow_id, timeout=30)` method:
  - Read PID from file
  - Send SIGTERM signal, wait up to timeout seconds
  - Send SIGKILL if still running
  - Clean up PID and state files
- Add error handling for launch failures
- Write comprehensive unit tests in `tests/test_workflow_launcher.py`
- Mock subprocess calls for unit tests
- Add integration test that launches real background process

### Task 8: Create Workflow Daemon Entry Point

- Create `src/cape_cli/workflow_daemon.py` as standalone executable module
- Implement `main(issue_id, adw_id)` function:
  - Set up signal handlers for SIGTERM and SIGINT
  - Initialize detached logging using `setup_logger(adw_id, detached_mode=True)`
  - Update state to "running" on start
  - Execute `workflow.execute_workflow(issue_id, adw_id, logger)`
  - Update state to "completed" or "failed" based on result
  - Clean up PID file on exit
- Implement signal handler `handle_shutdown_signal(signum, frame)`:
  - Set global shutdown flag
  - Update state to "stopped"
  - Perform cleanup and exit gracefully
- Add `if __name__ == "__main__"` block with argument parsing
- Add try/except wrapper to catch and log unexpected errors
- Write integration test in `tests/test_workflow_daemon.py`
- Test signal handling with real SIGTERM

### Task 9: Refactor Workflow Module for State Updates

- Add optional `state_manager` parameter to `execute_workflow()` in `src/cape_cli/workflow.py`
- Insert `state_manager.update_state(adw_id, current_step="classify")` before classification
- Insert `state_manager.update_state(adw_id, current_step="plan")` before planning
- Insert `state_manager.update_state(adw_id, current_step="implement")` before implementation
- Update state with error messages on failures
- Ensure state updates are non-blocking and don't fail workflow
- Maintain backward compatibility (state_manager optional)
- Add logging for state transitions
- Write unit tests in `tests/test_workflow.py` for state update calls
- Verify workflow still works without state_manager

### Task 10: Add Process Discovery and Recovery

- Add `discover_workflows()` method to `PIDFileManager`:
  - Scan PID directory for all .pid files
  - Read each PID file and check if process is running
  - Load corresponding state files
  - Return list of `(workflow_id, pid, state)` tuples
- Implement `recover_orphaned_workflows()` method:
  - Find state files without corresponding PID files
  - Mark as "failed" with error message
- Add `cleanup_completed_workflows(max_age_hours=24)`:
  - Remove PID and state files for completed/failed workflows older than threshold
- Write unit tests in `tests/test_pid_manager.py` for discovery
- Test recovery scenarios with mock file system state

### Task 11: Implement Workflow Monitor Class

- Create `src/cape_cli/workflow_monitor.py` with `WorkflowMonitor` class
- Implement `get_workflow_status(workflow_id)` returning `WorkflowState`
- Implement `list_active_workflows()` returning list of active workflows
- Implement `get_workflow_logs(workflow_id, lines=50)` to tail log files
- Implement `wait_for_completion(workflow_id, timeout=None, poll_interval=1)`:
  - Poll state file until status is terminal (completed/failed/stopped)
  - Return final state with timeout support
- Add caching with TTL (5 seconds) to reduce file I/O
- Write unit tests in `tests/test_workflow_monitor.py`
- Test polling behavior with mock state changes

### Task 12: Add CLI Commands for Workflow Management

- Update `src/cape_cli/cli.py` to add new commands:
  - `cape workflow start <issue_id>` - Launch workflow in background
  - `cape workflow list` - List active workflows with status
  - `cape workflow status <workflow_id>` - Show detailed workflow status
  - `cape workflow stop <workflow_id>` - Gracefully stop workflow
  - `cape workflow logs <workflow_id>` - Show workflow logs
  - `cape workflow cleanup` - Clean up stale PIDs and old state files
- Use rich tables for formatted output
- Add progress spinners for async operations
- Write integration tests in `tests/test_cli.py`
- Test CLI commands with actual workflow execution

### Task 13: Update TUI WorkflowScreen for Background Monitoring

- Refactor `WorkflowScreen.run_workflow()` in `src/cape_cli/tui.py`:
  - Replace direct `workflow.execute_workflow()` call with `WorkflowLauncher.launch_workflow()`
  - Store launched `workflow_id` (adw_id) in screen instance
  - Remove `@work(exclusive=True, thread=True)` decorator
- Add polling mechanism using Textual's `set_interval()`:
  - Poll state file every 2 seconds using `WorkflowMonitor.get_workflow_status()`
  - Update progress display based on current_step
  - Update log display with new log entries
- Add state watcher integration:
  - Register callback with `StateWatcher` for real-time updates
  - Trigger UI refresh on state changes
  - Debounce rapid updates (max 1 update per second to UI)
- Add "Stop Workflow" button and action:
  - Call `WorkflowLauncher.stop_workflow()` on button press
  - Show confirmation dialog
  - Update UI to show stopping status
- Update exit behavior:
  - Allow immediate exit without waiting for workflow completion
  - Show notification that workflow continues in background
  - Provide workflow_id for later monitoring
- Write unit tests in `tests/test_tui.py` for workflow monitoring
- Test screen lifecycle and cleanup

### Task 14: Add Active Workflows View to Issue Detail Screen

- Update `IssueDetailScreen` in `src/cape_cli/tui.py`:
  - Add section showing active workflows for this issue
  - Query `WorkflowMonitor.list_active_workflows()` filtered by `issue_id`
  - Display workflow status, current step, and elapsed time
  - Update display every 5 seconds
- Add keybinding `w` to view all workflows for issue
- Add keybinding `s` to stop active workflow
- Show workflow status indicator in issue header (green indicator for running workflows)
- Add auto-refresh toggle for workflow list
- Write unit tests in `tests/test_tui.py`
- Test multiple concurrent workflows for same issue

### Task 15: Add Global Workflows Screen to TUI

- Create `WorkflowsScreen` class in `src/cape_cli/tui.py`:
  - DataTable showing: workflow_id, issue_id, status, current_step, elapsed_time, action buttons
  - Auto-refresh every 3 seconds
  - Keyboard navigation with arrow keys
- Add keybindings:
  - `w` from IssueListScreen to open WorkflowsScreen
  - `Enter` to view workflow details
  - `s` to stop selected workflow
  - `l` to view logs for selected workflow
  - `Escape` to return to issue list
- Implement workflow detail modal showing full state information and recent log tail
- Add filtering by status (running, completed, failed)
- Add sorting options (by start time, by issue_id)
- Write unit tests in `tests/test_tui.py`
- Test screen with multiple active workflows

### Task 16: Implement Workflow Discovery on TUI Startup

- Update `CapeApp.on_mount()` in `src/cape_cli/tui.py`:
  - Call `PIDFileManager.discover_workflows()` on startup
  - Call `PIDFileManager.recover_orphaned_workflows()` to handle crashes
  - Show notification if active workflows found
  - Provide quick access to workflows screen
- Add startup cleanup:
  - Call `PIDFileManager.cleanup_stale_pids()`
  - Remove old completed workflow state (>24 hours)
- Log discovery results
- Write unit tests in `tests/test_tui.py`
- Test behavior with pre-existing workflow files

### Task 17: Add Workflow Notifications and Status Indicators

- Add workflow status indicators to IssueListScreen:
  - Show spinning indicator for issues with running workflows
  - Show checkmark for recently completed workflows
  - Show error icon for failed workflows
- Implement toast notifications for workflow events:
  - Workflow started, completed, failed, stopped by user
- Add state watcher callbacks to trigger notifications
- Register global callback in CapeApp
- Write unit tests in `tests/test_tui.py`
- Test notification timing and deduplication

### Task 18: Write Integration Tests for Detached Workflows

- Create `tests/integration/test_detached_workflow.py`:
  - Test workflow launch and detachment
  - Test TUI exit while workflow runs
  - Test workflow completion detection
  - Test graceful shutdown via SIGTERM
  - Test force kill via SIGKILL
  - Test stale PID cleanup
  - Test orphaned workflow recovery
- Create `tests/integration/test_workflow_monitor.py`:
  - Test monitoring multiple concurrent workflows
  - Test state file watching and callbacks
  - Test log tailing during execution
  - Test wait_for_completion with timeout
- Create `tests/integration/test_tui_workflow.py`:
  - Test TUI workflow launch and monitoring
  - Test TUI displaying workflow progress
  - Test stopping workflow from TUI
  - Test discovering workflows on startup
- Use pytest fixtures for test isolation
- Use temporary directories for state files
- Mock Supabase calls to avoid external dependencies
- Add cleanup in teardown to kill test processes

### Task 19: Add Error Handling and Edge Cases

- Handle PID file corruption: invalid JSON/format, partial writes, concurrent access
- Handle state file corruption: invalid JSON schema, missing required fields
- Handle process failures: crashes without cleanup, killed by system (OOM), zombie states
- Handle file system issues: disk full, permission errors, directory deletion during operation
- Add retry logic with exponential backoff for transient failures
- Add validation for workflow_id format
- Add safeguards against PID reuse (check cmdline)
- Write unit tests for each error scenario
- Document error handling behavior

### Task 20: Update Documentation and User Guide

- Update `README.md` with detached workflow features:
  - Architecture overview
  - CLI commands for workflow management
  - TUI workflow monitoring features
- Create architecture documentation describing system components and interactions
- Create user guide for workflow management:
  - How to launch workflows in background
  - How to monitor active workflows
  - How to stop running workflows
  - How to view workflow logs
  - Troubleshooting common issues
- Add docstrings to all new modules and classes
- Add inline code comments for complex logic

### Task 21: Performance Testing and Optimization

- Create performance test suite `tests/performance/test_workflow_performance.py`:
  - Launch 10 concurrent workflows
  - Measure state file write/read latency
  - Measure PID file operations throughput
  - Measure TUI responsiveness during monitoring
  - Measure memory usage over time
- Profile CPU usage with cProfile and identify hotspots
- Optimize state file format and I/O patterns
- Add caching layer with TTL for frequently accessed data
- Implement rate limiting for state updates
- Test scalability with 50+ workflows
- Document performance characteristics
- Set performance benchmarks for regression testing

### Task 22: Security Review and Hardening

- Review file permissions for PID/state/log files (set restrictive permissions 0600 for sensitive files)
- Review signal handling security: validate signal sources, prevent signal injection
- Review process launching security: sanitize command arguments, prevent command injection
- Add input validation for all user inputs
- Review temporary file creation (use `tempfile` module)
- Check for TOCTOU vulnerabilities in PID management
- Add security considerations to documentation
- Run security linting tools (bandit)

### Task 23: Run Validation Commands

- Execute all validation commands to ensure the feature works correctly with zero regressions
- Fix any issues found during validation
- Verify all tests pass
- Verify code formatting and linting pass

## Testing Strategy

### Unit Tests

**Coverage Target**: >90% for all new modules

**Focus Areas**:
- PID file manager operations (write, read, delete, cleanup)
- State file manager operations (write, read, update, validate)
- Process utilities (is_alive, send_signal, terminate)
- State watcher event handling and callbacks
- Workflow launcher process creation and termination
- Path management and directory creation

**Testing Approach**:
- Mock file system operations for deterministic tests
- Use temporary directories for integration-style unit tests
- Mock subprocess calls to avoid spawning real processes
- Test error conditions and edge cases explicitly
- Use pytest fixtures for setup/teardown

### Integration Tests

**Coverage Target**: All critical paths

**Focus Areas**:
- Detached workflow execution (launch → run → complete)
- TUI workflow monitoring (launch → monitor → stop)
- Process lifecycle (start → signal → cleanup)
- State synchronization (write → watch → read)
- Workflow discovery and recovery on startup
- Multi-workflow concurrent execution

**Testing Approach**:
- Use real subprocess execution in isolated environment
- Use temporary file system locations
- Mock Supabase database calls
- Add cleanup in teardown to kill spawned processes
- Test signal handling with real SIGTERM/SIGKILL
- Verify file cleanup after process termination

### Edge Cases

**Test Scenarios**:
- PID file corruption or partial writes
- State file corruption or invalid JSON
- PID file exists but process is dead (stale PID)
- PID reuse by unrelated process
- Concurrent workflow launches with same workflow_id
- File system full or permission denied errors
- Process crashes mid-execution without cleanup
- Orphaned state files without PID files
- Multiple TUI instances monitoring same workflow
- Network interruption during Supabase update
- Rapid state changes causing event flooding
- Workflow stops before daemon writes PID file

**Testing Approach**:
- Explicitly create corrupted files in test setup
- Simulate file system errors with mocks
- Test concurrent access with threading
- Verify graceful degradation and error messages

## Acceptance Criteria

1. **Detached Execution**:
   - Workflows launch as background processes using `subprocess.Popen(start_new_session=True)`
   - Workflows survive TUI termination (verified by closing TUI and checking process still running)
   - Workflows are not child processes of TUI (verified by checking `ps` output)
   - Workflows continue running after TUI closes and complete successfully

2. **State Management**:
   - On workflow start, PID file is created in `~/.cape/pids/{workflow_id}.pid`
   - On workflow start, log file is created in `~/.cape/logs/{workflow_id}.log`
   - On workflow start, state file is created in `~/.cape/state/{workflow_id}.json`
   - State file contains valid JSON matching `WorkflowState` schema
   - State file updates during workflow execution at each milestone
   - PID file is removed on workflow completion or termination

3. **TUI Polling**:
   - TUI discovers active workflows on startup via `discover_workflows()`
   - TUI displays real-time workflow progress by polling state files every 2 seconds
   - TUI updates UI when state changes are detected
   - TUI uses state watcher for immediate updates (< 1 second latency)
   - TUI shows list of active workflows with status, current step, elapsed time

4. **Graceful Stop**:
   - "Stop" action in TUI sends SIGTERM to process via `os.kill(pid, signal.SIGTERM)`
   - TUI waits up to 30 seconds for graceful shutdown
   - TUI sends SIGKILL if process doesn't stop within timeout
   - UI updates to show "stopping" then "stopped" status
   - PID and state files are cleaned up after stop

5. **Workflow Signal Handling**:
   - Workflow daemon registers signal handlers for SIGTERM and SIGINT
   - On SIGTERM, daemon updates state to "stopped"
   - On SIGTERM, daemon cleans up PID file before exiting
   - On SIGTERM, daemon logs final status message
   - Daemon exits with code 130 on SIGTERM, 0 on success, 1 on failure

6. **Backward Compatibility**:
   - Existing synchronous workflow execution still works
   - `workflow.execute_workflow()` works with and without `state_manager` parameter
   - Database schema unchanged
   - Existing tests continue to pass

7. **Error Handling**:
   - Stale PID files are detected and cleaned up on TUI startup
   - Orphaned state files are recovered and marked as failed
   - Corrupted PID/state files are handled gracefully with error messages
   - File system errors (permission denied, disk full) are handled gracefully
   - Process crashes are detected and logged

8. **Performance**:
   - State file updates complete in < 100ms
   - TUI remains responsive while monitoring workflows
   - System handles 10+ concurrent workflows without degradation
   - State watcher adds < 5% CPU overhead
   - Memory usage remains stable over extended operation

## Validation Commands

Execute every command to validate the feature works correctly with zero regressions.

- `cd /Users/bponghneng/git/cape/cape_cli` - Change directory to the root of the codebase
- `uv sync` - Install and sync project dependencies
- `pytest tests/ -v` - Run full test suite with verbose output
- `pytest tests/test_pid_manager.py -v --cov=cape_cli.pid_manager --cov-report=term-missing` - Run PID manager tests with coverage
- `pytest tests/test_state_manager.py -v --cov=cape_cli.state_manager --cov-report=term-missing` - Run state manager tests with coverage
- `pytest tests/test_workflow_launcher.py -v --cov=cape_cli.workflow_launcher --cov-report=term-missing` - Run workflow launcher tests with coverage
- `pytest tests/test_workflow_daemon.py -v` - Run workflow daemon integration tests
- `pytest tests/integration/ -v` - Run all integration tests
- `pytest tests/test_tui.py -v` - Run TUI tests
- `uv run cape workflow start 1` - Test launching a workflow from CLI (requires test issue in DB)
- `uv run cape workflow list` - Test listing active workflows from CLI
- `uv run cape workflow status <workflow_id>` - Test getting workflow status from CLI
- `uv run cape workflow logs <workflow_id>` - Test viewing workflow logs from CLI
- `uv run cape workflow stop <workflow_id>` - Test stopping a workflow from CLI
- `uv run cape workflow cleanup` - Test cleanup of stale PIDs
- `uv run cape` - Test TUI workflow monitoring (manual verification)
- `ruff check src/` - Run linter on source code
- `ruff format src/` - Format source code
- `mypy src/cape_cli/` - Run type checker

## Notes

### Implementation Timeline

Estimated timeline: **5-6 weeks** with one experienced engineer following TDD methodology.

**Week 1-2**: Foundation (Phase 1)
- Focus on directory structure, PID manager, state management
- High test coverage for infrastructure
- Early validation of file system behavior

**Week 3-4**: Core Implementation (Phase 2)
- Workflow launcher, daemon, monitoring
- Validate process detachment and signal handling
- CLI commands for workflow management

**Week 5-6**: Integration & Polish (Phase 3)
- TUI integration
- Comprehensive testing
- Documentation and performance optimization

### Technical Considerations

**Process Detachment Strategy**:
- Using `subprocess.Popen(start_new_session=True)` instead of python-daemon for simplicity
- This creates a new session, detaching from terminal
- Works on POSIX systems (Linux, macOS)
- Windows support would require different approach (future consideration)

**State Synchronization**:
- File-based state is simple and reliable for single-machine use
- Using watchdog for efficient file monitoring (event-driven vs polling)
- Caching with TTL reduces file I/O overhead
- SQLite could be considered for >100 concurrent workflows (future optimization)

**Signal Handling**:
- SIGTERM for graceful shutdown (cleanup, save state)
- SIGKILL as last resort (after 30-second timeout)
- Signal handlers must be minimal (set flags, don't do heavy work)
- Use `threading.Event` for coordination between signal handler and main loop

**Error Recovery**:
- Stale PID detection on every startup
- Orphaned workflow recovery marks as failed
- PID reuse protection by checking process cmdline
- Atomic file operations prevent corruption

### Future Enhancements

**Phase 4: Advanced Features** (Post-MVP)
- Workflow queuing and prioritization
- Resource limits (CPU, memory) per workflow
- Distributed execution across multiple machines
- Workflow templates and scheduling
- Workflow retry on failure
- Checkpoint and resume capability

**Phase 5: Observability** (Post-MVP)
- Prometheus metrics export
- Structured logging with correlation IDs
- Distributed tracing integration
- Real-time workflow dashboards

**Phase 6: Resilience** (Post-MVP)
- High availability with leader election
- State replication and backup
- Health checks and auto-recovery

### Known Limitations

**Current Scope**:
- Single-machine execution only (no distributed workflows)
- POSIX systems only (Linux, macOS) - Windows requires different approach
- No workflow queuing or resource limits
- No automatic retry on failure
- No workflow templates or scheduling

**Dependencies**:
- Requires file system support for atomic renames
- Requires POSIX signals (SIGTERM, SIGKILL)
- Requires psutil for robust process detection
- Requires watchdog for file system events

### Migration Path

**Rollout Strategy**:
1. Alpha Release: Internal testing with feature flag
2. Beta Release: Limited users with opt-in
3. GA Release: Full rollout with migration guide

**Backward Compatibility**:
- Existing synchronous workflows continue to work unchanged
- New workflows default to detached mode
- Provide `--sync` flag for legacy behavior if needed
- Database schema unchanged

### Security Considerations

**File Permissions**:
- PID files: 0644 (readable by user, not writable by others)
- State files: 0644 (readable by user)
- Log files: 0644 (readable by user)
- Directories: 0755 (user writable, others readable)

**Input Validation**:
- Validate workflow_id format (alphanumeric + hyphens only)
- Sanitize command arguments to prevent injection
- Validate PID values before sending signals
- Check process cmdline before sending signals (prevent PID reuse attacks)

**Signal Security**:
- Only send signals to processes we created (check cmdline)
- Handle EPERM (permission denied) gracefully
- Don't expose PID file contents to other users

### Performance Characteristics

**Expected Performance**:
- State file write: < 50ms
- State file read: < 20ms
- PID file operations: < 10ms
- TUI state polling: 2 seconds interval
- State watcher latency: < 500ms
- Memory per workflow: ~5MB (daemon process overhead)
- CPU overhead: < 1% per workflow (mostly idle)

**Scalability**:
- Tested with 10 concurrent workflows
- Expected to handle 50+ workflows on modern hardware
- File system I/O is the bottleneck (consider SQLite for >100 workflows)

**Optimization Opportunities**:
- Use orjson for faster JSON serialization
- Batch state updates (rate limiting)
- Use inotify directly instead of watchdog (Linux only)
- Consider msgpack for binary state format
