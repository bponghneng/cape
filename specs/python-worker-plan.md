# Feature: Python Worker Daemon for CAPE

## Description

A standalone Python daemon that continuously polls the `cape_issues` database table for pending issues and executes the appropriate workflows using the `cape-adw` command. The worker operates independently of the CLI, providing automated background processing of issues with proper locking mechanisms to prevent race conditions between multiple worker instances.

## User Story

As a CAPE system administrator
I want to have automated background workers that process pending issues
So that issues can be handled automatically without manual intervention

## Problem Statement

Currently, issues in the `cape_issues` table require manual processing through the CLI interface. There is no automated mechanism to continuously process pending issues, leading to delays in issue resolution and requiring human oversight for routine workflow execution.

## Solution Statement

Implement a standalone Python daemon that:

1. Continuously polls the database for pending issues
2. Uses atomic locking to prevent race conditions between multiple workers
3. Executes the `cape-adw` command with issue_id and description
4. Handles errors gracefully and resets failed issues for retry
5. Runs as a system service on both macOS and Linux platforms

## Relevant Files

### Existing Files

- `cape/cape-cli/src/cape_cli/database.py` - Contains `get_client()` function for database connectivity
- `cape/cape-adw/cape_adw/cli.py` - The CLI command that workers will execute
- `cape/migrations/001_create_cape_issues_tables.sql` - Base database schema

### New Files

- `cape/worker.py` - Main worker daemon implementation
- `cape/tests/test_worker.py` - Unit tests for worker functionality
- `cape/migrations/003_add_worker_assignment.sql` - Database migration for worker assignment
- `cape/scripts/install-worker.sh` - Installation script for daemon setup
- `cape/daemons/com.cape.worker.plist` - macOS launchd configuration
- `cape/daemons/cape-worker.service` - Linux systemd configuration

### Database Migration

```sql
-- Create enum type for worker IDs
CREATE TYPE worker_id AS ENUM ('alleycat-1', 'tyderium-1');

-- Add assigned_to column
ALTER TABLE cape_issues
ADD COLUMN assigned_to worker_id;

-- Create index for performance
CREATE INDEX idx_cape_issues_assigned_to ON cape_issues(assigned_to);
```

### PostgreSQL Function

```sql
CREATE OR REPLACE FUNCTION get_and_lock_next_issue(p_worker_id worker_id)
RETURNS TABLE (id INTEGER, description TEXT) AS $$
BEGIN
    RETURN QUERY
    UPDATE cape_issues
    SET status = 'started', assigned_to = p_worker_id, updated_at = now()
    WHERE id = (
        SELECT id FROM cape_issues WHERE status = 'pending'
        ORDER BY created_at ASC FOR UPDATE SKIP LOCKED LIMIT 1
    )
    RETURNING id, description;
END;
$$ LANGUAGE plpgsql;
```

## Implementation Plan

### Phase 1: Foundation

- Create database migration for worker assignment functionality
- Implement PostgreSQL function for atomic issue locking
- Set up basic project structure and imports

### Phase 2: Core Implementation

- Implement the `IssueWorker` class with polling mechanism
- Add workflow execution with proper subprocess handling
- Implement error handling and status management
- Create comprehensive logging system

### Phase 3: Integration

- Create daemon configuration files for macOS and Linux
- Implement installation scripts
- Add comprehensive test suite
- Create documentation and usage instructions

## Step by Step Tasks

### Step 1: Create Database Migration

- Create migration file `003_add_worker_assignment.sql`
- Add worker_id enum type
- Add assigned_to column to cape_issues table
- Create performance index on assigned_to column

### Step 2: Implement PostgreSQL Function

- Create `get_and_lock_next_issue` function
- Use `FOR UPDATE SKIP LOCKED` for atomic locking
- Return issue id and description
- Update issue status to 'started' and assign to worker

### Step 3: Create Worker Core Structure

- Create `cape/worker.py` file
- Import required modules (subprocess, logging, pathlib, etc.)
- Add cape_cli to path for database imports
- Implement `IssueWorker` class with constructor

### Step 4: Implement Logging System

- Create `setup_logging()` method
- Configure file and console handlers
- Set appropriate log format and level
- Create logger instance for the worker

### Step 5: Implement Issue Retrieval

- Create `get_next_issue()` method
- Use database client to call PostgreSQL function
- Handle empty results gracefully
- Return issue data or None

### Step 6: Implement Workflow Execution

- Create `execute_workflow()` method
- Call `uv run cape-adw` with issue_id and description
- Handle subprocess output and errors
- Implement timeout handling (1 hour)
- Update issue status based on execution result

### Step 7: Implement Status Updates

- Create `update_issue_status()` method
- Update issue status in database
- Handle database errors gracefully

### Step 8: Implement Main Polling Loop

- Create `run()` method with infinite loop
- Poll for issues at configured intervals
- Execute workflows when issues are found
- Sleep when no issues available

### Step 9: Create Test Suite

- Create `cape/tests/test_worker.py`
- Implement unit tests for all methods
- Use `@patch` decorators for mocking
- Test success and failure scenarios
- Test edge cases and error conditions

### Step 10: Create Daemon Configurations

- Create macOS launchd plist file
- Create Linux systemd service file
- Configure proper paths and arguments
- Set up auto-restart and logging

### Step 11: Create Installation Script

- Create `cape/scripts/install-worker.sh`
- Support both macOS and Linux
- Handle worker ID parameterization
- Set up log files and permissions
- Install and start daemon service

### Step 12: Create Documentation

- Update README with worker usage
- Document installation process
- Provide troubleshooting guide
- Add log monitoring instructions

### Step 13: Validation and Testing

- Run complete test suite
- Test daemon installation
- Verify workflow execution
- Test error handling and recovery

## Testing Strategy

### Unit Tests

- Test `get_next_issue()` with mock database responses
- Test `execute_workflow()` with mock subprocess calls
- Test `update_issue_status()` with mock database updates
- Test error handling in all methods
- Test logging functionality

### Integration Tests

- Test complete workflow execution with real database
- Test multiple worker instances with locking
- Test daemon startup and shutdown
- Test installation scripts on target platforms

### Edge Cases

- Database connection failures
- Subprocess timeouts
- Invalid issue data
- Concurrent worker access
- System resource exhaustion
- Daemon restart scenarios

## Acceptance Criteria

1. Worker successfully polls database for pending issues
2. Atomic locking prevents race conditions between multiple workers
3. Workflow execution calls `uv run cape-adw` with correct arguments
4. Failed issues are reset to 'pending' status for retry
5. Worker logs all activities to file and console
6. Daemon runs continuously on both macOS and Linux
7. Installation script properly configures system service
8. All tests pass with 100% code coverage
9. Error handling gracefully recovers from failures
10. Worker respects configured polling intervals

## Validation Commands

```bash
# Run unit tests
cd cape && python -m pytest tests/test_worker.py -v --cov=worker

# Test worker manually
cd cape && python worker.py --worker-id test-worker

# Test workflow execution
cd cape && uv run cape-adw 123 "test issue description"
```

## Notes

- Worker IDs should be unique across all instances
- Polling interval should be configurable (default: 10 seconds)
- Log rotation should be configured for production environments
- Database connection pooling should be considered for high-load scenarios
- Worker should handle graceful shutdown signals (SIGTERM, SIGINT)
- Consider implementing backoff strategy for repeated failures
- Monitor worker health through system monitoring tools
- Security considerations: limit worker permissions to necessary database operations only
