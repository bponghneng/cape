# Feature: Supabase-Sourced Cape Issue Workflow

## Description

Refactor the `adw_plan_build` workflow to load Cape issues from Supabase instead of local markdown files, introducing strongly typed `CapeIssue` and `CapeComment` Pydantic models to drive the workflow. This feature replaces the file-based issue loading mechanism with a database-backed approach using Supabase, enabling future workflow automation through issue tracking and comment-based status updates.

The implementation adds a Supabase helper module with connection management, data fetching, and comment creation capabilities. The workflow will accept issue IDs as command-line arguments, fetch structured issue data from Supabase, and pass `CapeIssue` instances through the classification, planning, and implementation pipeline. This creates a foundation for automated issue management, progress tracking, and integration with external tools.

## User Story

As a workflow automation engineer
I want to load Cape issues from Supabase using integer IDs and pass strongly typed issue objects through the workflow
So that I can automate issue tracking, enable programmatic status updates, and build integrations with external tools without relying on filesystem-based issue management

## Problem Statement

The current `adw_plan_build` workflow loads issues from local markdown files, requiring manual file management and limiting automation capabilities. This file-based approach creates several challenges:

1. **Manual Issue Management**: Issues must be created and updated as markdown files, requiring filesystem access and manual coordination
2. **No Centralized Tracking**: Issue status, metadata, and history are scattered across files without a single source of truth
3. **Limited Automation**: Workflows cannot programmatically create, update, or query issues without filesystem operations
4. **Poor Integration**: External tools cannot easily access issue data or post updates without file system access
5. **No Structured Metadata**: Issue data is unstructured text without validation, timestamps, or status tracking

These limitations prevent automated issue creation from external systems, programmatic status updates, and building dashboards or reporting tools around workflow execution.

## Solution Statement

Migrate issue storage to Supabase with structured `cape_issues` and `cape_comments` tables, implementing Pydantic models (`CapeIssue`, `CapeComment`) for type-safe data handling throughout the workflow. The solution refactors the workflow to:

1. **Accept Issue IDs**: Change CLI from file paths to integer issue IDs (`uv run adw_plan_build.py <issue-id>`)
2. **Fetch from Supabase**: Load issue data from Supabase using a singleton client pattern
3. **Type-Safe Workflow**: Pass `CapeIssue` instances through classification, planning, and implementation functions
4. **Validated Data Models**: Use Pydantic for automatic validation, status defaulting, and text trimming
5. **Comment API**: Provide helper functions for posting workflow comments to issues (for future automation)

This approach maintains the existing workflow logic while replacing filesystem reads with database queries, establishing a foundation for automated issue management, status tracking, and external integrations.

## Relevant Files

### Existing Files to Modify

#### `cape/workflows/data_types.py`
**Purpose**: Add new Pydantic models for Supabase integration

**Current State**: Contains models for agent requests/responses (`AgentPromptRequest`, `AgentPromptResponse`, `AgentTemplateRequest`, `ClaudeCodeResultMessage`)

**Required Changes**:
- Add `CapeIssue` model with fields: `id`, `description`, `status`, `created_at`, `updated_at`
- Add `CapeComment` model with fields: `id`, `issue_id`, `comment`, `created_at`
- Implement `CapeIssue.from_supabase(row: dict)` factory method
- Add validation for status literals (`pending|started|completed`)
- Add field validators for text trimming and status defaulting

**Code Snippet**:
```python
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator

class CapeIssue(BaseModel):
    """Cape issue model matching Supabase schema."""

    id: int
    description: str = Field(..., min_length=1)
    status: Literal["pending", "started", "completed"] = "pending"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator("description")
    @classmethod
    def trim_description(cls, v: str) -> str:
        """Trim whitespace from description."""
        return v.strip()

    @field_validator("status", mode="before")
    @classmethod
    def default_status(cls, v):
        """Default missing status to pending."""
        return v if v else "pending"

    @classmethod
    def from_supabase(cls, row: dict) -> "CapeIssue":
        """Create CapeIssue from Supabase row."""
        return cls(**row)

class CapeComment(BaseModel):
    """Cape comment model matching Supabase schema."""

    id: Optional[int] = None
    issue_id: int
    comment: str = Field(..., min_length=1)
    created_at: Optional[datetime] = None

    @field_validator("comment")
    @classmethod
    def trim_comment(cls, v: str) -> str:
        """Trim whitespace from comment."""
        return v.strip()
```

#### `cape/workflows/adw_plan_build.py`
**Purpose**: Refactor workflow to use Supabase-backed issues

**Current State**: Accepts file path as CLI argument, reads issue content from filesystem in `classify_issue()` and `build_plan()`, passes issue text as string to agent templates

**Required Changes**:
- Update `parse_args()` to accept integer issue ID instead of file path
- Update `main()` to fetch `CapeIssue` from Supabase instead of reading file
- Refactor `classify_issue()` to accept `CapeIssue` instead of `issue_path`
- Refactor `build_plan()` to accept `CapeIssue` instead of `issue_path`
- Update logging to use issue ID and status instead of file path
- Add error handling for missing Supabase environment variables
- Add error handling for non-existent issue IDs

**Code Snippet (parse_args refactor)**:
```python
def parse_args(logger: Optional[object] = None) -> Tuple[int, Optional[str]]:
    """Parse command line arguments.

    Returns (issue_id, adw_id) where adw_id may be None."""
    if len(sys.argv) < 2:
        usage_msg = [
            "Usage: uv run adw_plan_build.py <issue-id> [adw-id]",
            "Example: uv run adw_plan_build.py 123",
            "Example: uv run adw_plan_build.py 123 abc12345",
        ]
        if logger:
            for msg in usage_msg:
                logger.error(msg)
        else:
            for msg in usage_msg:
                print(msg)
        sys.exit(1)

    try:
        issue_id = int(sys.argv[1])
    except ValueError:
        error_msg = f"Error: issue-id must be an integer, got: {sys.argv[1]}"
        if logger:
            logger.error(error_msg)
        else:
            print(error_msg)
        sys.exit(1)

    adw_id = sys.argv[2] if len(sys.argv) > 2 else None

    return issue_id, adw_id
```

**Code Snippet (classify_issue refactor)**:
```python
def classify_issue(
    issue: CapeIssue, adw_id: str, logger: object
) -> Tuple[Optional[str], Optional[str]]:
    """Classify issue and return appropriate slash command.
    Returns (command, error_message) tuple."""

    request = AgentTemplateRequest(
        agent_name=AGENT_CLASSIFIER,
        slash_command="/triage:classify",
        args=[issue.description],  # Use issue.description instead of file read
        adw_id=adw_id,
        model="sonnet",
    )
    logger.debug(
        "classify request: %s",
        request.model_dump_json(indent=2, by_alias=True),
    )
    response = execute_template(request)
    logger.debug(
        "classify response: %s",
        response.model_dump_json(indent=2, by_alias=True),
    )

    if not response.success:
        return None, response.output

    issue_command = response.output.strip()

    if issue_command == "0":
        return None, f"No command selected: {response.output}"

    if issue_command not in ["/chore", "/bug", "/feature"]:
        return None, f"Invalid command selected: {response.output}"

    # Convert to triage: prefixed command
    issue_command = f"/triage:{issue_command.lstrip('/')}"

    return issue_command, None
```

**Code Snippet (main refactor)**:
```python
def main() -> None:
    load_dotenv()

    issue_id, adw_id = parse_args()
    if not adw_id:
        adw_id = make_adw_id()

    logger = setup_logger(adw_id, "adw_plan_build")
    logger.info(f"ADW ID: {adw_id}")
    logger.info(f"Processing issue ID: {issue_id}")

    # Fetch issue from Supabase
    logger.info("\n=== Fetching issue from Supabase ===")
    try:
        issue = fetch_issue(issue_id)
        logger.info(f"Issue fetched: ID={issue.id}, Status={issue.status}")
    except ValueError as e:
        logger.error(f"Error fetching issue: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error fetching issue: {e}")
        sys.exit(1)

    # Classify the issue
    logger.info("\n=== Classifying issue ===")
    issue_command, error = classify_issue(issue, adw_id, logger)
    check_error(error, logger, "Error classifying issue")
    logger.info(f"Issue classified as: {issue_command}")

    # Build the implementation plan
    logger.info("\n=== Building implementation plan ===")
    plan_response = build_plan(issue, issue_command, adw_id, logger)
    check_error(plan_response, logger, "Error building plan")
    logger.info("✅ Implementation plan created")

    # Get the path to the plan file that was created
    logger.info("\n=== Finding plan file ===")
    plan_file_path, error = get_plan_file(plan_response.output, adw_id, logger)
    check_error(error, logger, "Error finding plan file")
    logger.info(f"Plan file created: {plan_file_path}")

    # Implement the plan
    logger.info("\n=== Implementing solution ===")
    implement_response = implement_plan(plan_file_path, adw_id, logger)
    check_error(implement_response, logger, "Error implementing solution")
    logger.info("✅ Solution implemented")

    logger.info("\n=== Workflow completed successfully ===")
```

#### `cape/workflows/utils.py`
**Purpose**: No changes required for this feature

**Current State**: Provides `make_adw_id()` and `setup_logger()` functions

**Why No Changes**: The utility functions work with issue IDs as easily as file paths; logging changes are isolated to `adw_plan_build.py`

### New Files

#### `cape/workflows/supabase.py`
**Purpose**: Supabase client singleton and helper functions for issue/comment operations

**Required Functionality**:
- Singleton Supabase client with environment variable validation
- `fetch_issue(issue_id: int) -> CapeIssue` - fetch issue by ID
- `create_comment(issue_id: int, text: str) -> CapeComment` - create comment
- Error handling for missing environment variables
- Error handling for database operation failures
- Logging for database operations

**Code Snippet**:
```python
"""Supabase client and helper functions for Cape issue workflow."""

import os
import logging
from typing import Optional
from functools import lru_cache

from supabase import create_client, Client
from postgrest.exceptions import APIError
from dotenv import load_dotenv

from data_types import CapeIssue, CapeComment

logger = logging.getLogger(__name__)

# ============================================================================
# Configuration
# ============================================================================

class SupabaseConfig:
    """Configuration for Supabase connection."""

    def __init__(self):
        self.url: Optional[str] = os.environ.get("SUPABASE_URL")
        self.service_role_key: Optional[str] = os.environ.get(
            "SUPABASE_SERVICE_ROLE_KEY"
        )

    def validate(self) -> None:
        """Validate required environment variables are set."""
        missing = []

        if not self.url:
            missing.append("SUPABASE_URL")
        if not self.service_role_key:
            missing.append("SUPABASE_SERVICE_ROLE_KEY")

        if missing:
            raise ValueError(
                f"Missing required Supabase environment variables: "
                f"{', '.join(missing)}. "
                f"Please set these in your environment or .env file."
            )

# ============================================================================
# Client Singleton
# ============================================================================

_client: Optional[Client] = None

@lru_cache()
def get_client() -> Client:
    """Get or create the global Supabase client instance."""
    global _client

    if _client is None:
        config = SupabaseConfig()
        config.validate()

        _client = create_client(config.url, config.service_role_key)
        logger.info("Supabase client initialized")

    return _client

# ============================================================================
# Issue Operations
# ============================================================================

def fetch_issue(issue_id: int) -> CapeIssue:
    """Fetch issue from Supabase by ID."""
    client = get_client()

    try:
        response = (
            client
            .table("cape_issues")
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

# ============================================================================
# Comment Operations
# ============================================================================

def create_comment(issue_id: int, text: str) -> CapeComment:
    """Create a comment on an issue."""
    client = get_client()

    comment_data = {
        "issue_id": issue_id,
        "comment": text.strip(),
    }

    try:
        response = (
            client
            .table("cape_comments")
            .insert(comment_data)
            .execute()
        )

        if not response.data:
            raise ValueError("Comment creation returned no data")

        return CapeComment(**response.data[0])

    except APIError as e:
        logger.error(f"Database error creating comment on issue {issue_id}: {e}")
        raise ValueError(f"Failed to create comment on issue {issue_id}: {e}") from e
```

#### `cape/.env.example` or `cape/.env.hooks.example`
**Purpose**: Document required environment variables for Supabase

**Required Content**:
```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
```

#### `cape/migrations/001_create_cape_issues_tables.sql`
**Purpose**: Supabase migration to create required database tables

**Required Content**:
```sql
-- Create cape_issues table
CREATE TABLE IF NOT EXISTS cape_issues (
    id SERIAL PRIMARY KEY,
    description TEXT NOT NULL,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'started', 'completed')),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Create cape_comments table
CREATE TABLE IF NOT EXISTS cape_comments (
    id SERIAL PRIMARY KEY,
    issue_id INT NOT NULL REFERENCES cape_issues(id) ON DELETE CASCADE,
    comment TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_cape_issues_status ON cape_issues(status);
CREATE INDEX IF NOT EXISTS idx_cape_comments_issue_id ON cape_comments(issue_id);

-- Create updated_at trigger for cape_issues
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_cape_issues_updated_at BEFORE UPDATE ON cape_issues
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

#### `cape/migrations/README.md`
**Purpose**: Document migration execution instructions

**Required Content**:
```markdown
# Supabase Migrations

## Prerequisites

- Supabase CLI installed: `brew install supabase/tap/supabase`
- Supabase project created
- Environment variables set in `.env` file

## Running Migrations

### Option 1: Using Supabase CLI

1. Link to your Supabase project:
   ```bash
   supabase link --project-ref your-project-ref
   ```

2. Apply migration:
   ```bash
   supabase db push
   ```

### Option 2: Manual SQL Execution

1. Navigate to your Supabase project dashboard
2. Go to SQL Editor
3. Copy and paste the contents of `001_create_cape_issues_tables.sql`
4. Execute the SQL

## Verification

After running migrations, verify tables exist:

```sql
SELECT * FROM cape_issues;
SELECT * FROM cape_comments;
```
```

## Implementation Plan

### Phase 1: Foundation
Establish Supabase connectivity, database schema, and core data models before touching workflow code. This phase creates the foundation for database-backed issue management.

**Deliverables**:
- Supabase tables created via migration
- Pydantic models defined with validation
- Supabase helper module with client singleton
- Environment variable configuration
- Test data inserted for validation

### Phase 2: Core Implementation
Refactor workflow functions to accept `CapeIssue` instances instead of file paths, replacing filesystem reads with Supabase queries while maintaining existing workflow logic.

**Deliverables**:
- `parse_args()` accepts issue IDs
- `classify_issue()` and `build_plan()` accept `CapeIssue` objects
- `main()` fetches issues from Supabase
- Logging updated to use issue IDs
- Error handling for database operations

### Phase 3: Integration
Complete the integration with comprehensive testing, documentation updates, and validation that the workflow executes end-to-end with Supabase-backed issues.

**Deliverables**:
- Unit tests for Pydantic models
- Unit tests for Supabase helper functions
- Integration tests for workflow with mocked Supabase
- Documentation updates
- End-to-end validation

## Step by Step Tasks

### 1. Create Database Schema

- Create `cape/migrations/` directory for SQL migration files
- Write `001_create_cape_issues_tables.sql` with table definitions:
  - `cape_issues` table with columns: `id SERIAL PRIMARY KEY`, `description TEXT NOT NULL`, `status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'started', 'completed'))`, `created_at TIMESTAMPTZ DEFAULT now()`, `updated_at TIMESTAMPTZ DEFAULT now()`
  - `cape_comments` table with columns: `id SERIAL PRIMARY KEY`, `issue_id INT NOT NULL REFERENCES cape_issues(id) ON DELETE CASCADE`, `comment TEXT NOT NULL`, `created_at TIMESTAMPTZ DEFAULT now()`
  - Indexes on `cape_issues.status` and `cape_comments.issue_id`
  - Trigger to auto-update `cape_issues.updated_at` on row updates
- Create `migrations/README.md` with execution instructions for Supabase CLI and manual SQL
- Execute migration to create tables in Supabase project

### 2. Define Pydantic Data Models

- Open `cape/workflows/data_types.py`
- Add `CapeIssue` Pydantic model with fields: `id: int`, `description: str`, `status: Literal["pending", "started", "completed"]`, `created_at: Optional[datetime]`, `updated_at: Optional[datetime]`
- Add `@field_validator("description")` to trim whitespace from description
- Add `@field_validator("status", mode="before")` to default missing status to `"pending"`
- Add `@classmethod from_supabase(cls, row: dict) -> CapeIssue` factory method
- Add `CapeComment` Pydantic model with fields: `id: Optional[int]`, `issue_id: int`, `comment: str`, `created_at: Optional[datetime]`
- Add `@field_validator("comment")` to trim whitespace from comment text
- Write unit tests for `CapeIssue` validation (status defaulting, text trimming, timestamp parsing)
- Write unit tests for `CapeComment` validation

### 3. Implement Supabase Helper Module

- Create `cape/workflows/supabase.py` file
- Add imports: `os`, `logging`, `functools.lru_cache`, `supabase.create_client`, `supabase.Client`, `postgrest.exceptions.APIError`, `dotenv.load_dotenv`
- Define `SupabaseConfig` class with `url` and `service_role_key` properties from environment
- Implement `SupabaseConfig.validate()` method to check required environment variables and raise `ValueError` with clear message if missing
- Implement `get_client()` function using `@lru_cache()` decorator for singleton pattern
- Add global `_client` variable initialized to `None`
- In `get_client()`, validate config and create client using `create_client(url, key)` if `_client` is `None`
- Implement `fetch_issue(issue_id: int) -> CapeIssue` function
- In `fetch_issue()`, query `cape_issues` table using `.select("*").eq("id", issue_id).maybe_single().execute()`
- Handle `response.data is None` case by raising `ValueError` with message "Issue with id {issue_id} not found"
- Catch `APIError` exceptions and re-raise as `ValueError` with context
- Return `CapeIssue.from_supabase(response.data)` on success
- Implement `create_comment(issue_id: int, text: str) -> CapeComment` function
- In `create_comment()`, insert comment into `cape_comments` table with `issue_id` and trimmed `text`
- Return `CapeComment(**response.data[0])` on success
- Add error handling for `APIError` with logging and re-raising as `ValueError`
- Write unit tests for `SupabaseConfig.validate()` with missing environment variables
- Write unit tests for `fetch_issue()` with mocked Supabase client (success and not found cases)
- Write unit tests for `create_comment()` with mocked Supabase client

### 4. Update Environment Configuration

- Check if `cape/.env.hooks.example` exists, otherwise use `cape/.env.example`
- Add Supabase environment variables to example file:
  ```bash
  # Supabase Configuration
  SUPABASE_URL=https://your-project.supabase.co
  SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
  ```
- Update project documentation (if exists) to mention required Supabase environment variables
- Create local `.env` file (gitignored) with actual Supabase credentials for testing

### 5. Refactor CLI Argument Parsing

- Open `cape/workflows/adw_plan_build.py`
- Update `parse_args()` function signature to return `Tuple[int, Optional[str]]` instead of `Tuple[str, Optional[str]]`
- Update usage messages to show `<issue-id>` instead of `<issue-path>`:
  - "Usage: uv run adw_plan_build.py <issue-id> [adw-id]"
  - "Example: uv run adw_plan_build.py 123"
  - "Example: uv run adw_plan_build.py 123 abc12345"
- Add try/except block around `int(sys.argv[1])` to catch `ValueError`
- If conversion fails, log error message "Error: issue-id must be an integer, got: {sys.argv[1]}" and exit with code 1
- Update return statement to `return issue_id, adw_id` where `issue_id` is an integer
- Write unit tests for `parse_args()` with valid integer input
- Write unit tests for `parse_args()` with invalid non-integer input
- Write unit tests for `parse_args()` with missing required argument

### 6. Refactor classify_issue Function

- Import `CapeIssue` from `data_types` at top of `adw_plan_build.py`
- Update `classify_issue()` function signature: change `issue_path: str` parameter to `issue: CapeIssue`
- Remove `issue = Path(issue_path).read_text()` line
- Update `AgentTemplateRequest` args to use `args=[issue.description]` instead of `args=[issue]`
- Keep all other logic unchanged (classification, validation, response parsing)
- Update docstring to reflect new parameter type
- Write unit tests for `classify_issue()` with mock `CapeIssue` object and mock `execute_template()`

### 7. Refactor build_plan Function

- Update `build_plan()` function signature: change `issue_path: str` parameter to `issue: CapeIssue`
- Remove `issue = Path(issue_path).read_text()` line
- Update `AgentTemplateRequest` args to use `args=[issue.description]` instead of `args=[issue]`
- Keep all other logic unchanged (template execution, response handling)
- Update docstring to reflect new parameter type
- Write unit tests for `build_plan()` with mock `CapeIssue` object and mock `execute_template()`

### 8. Refactor main Workflow Function

- Import `fetch_issue` from `supabase` module at top of file
- Update `main()` function to call `issue_id, adw_id = parse_args()` (now returns int)
- Update logging from `f"Processing issue: {issue_path}"` to `f"Processing issue ID: {issue_id}"`
- Add section "=== Fetching issue from Supabase ===" with `logger.info()`
- Wrap `fetch_issue(issue_id)` call in try/except block:
  - Catch `ValueError` (missing issue or database error) and log error with `logger.error()`
  - Catch generic `Exception` and log "Unexpected error fetching issue"
  - Exit with code 1 on any error
- Log successful fetch: `f"Issue fetched: ID={issue.id}, Status={issue.status}"`
- Update `classify_issue()` call to pass `issue` instead of `issue_path`
- Update `build_plan()` call to pass `issue` instead of `issue_path`
- Keep all other workflow logic unchanged (plan finding, implementation)
- Write integration tests for `main()` with mocked `fetch_issue()`, `classify_issue()`, `build_plan()`, `get_plan_file()`, and `implement_plan()`

### 9. Update Logging Throughout Workflow

- Review all `logger.info()` and `logger.debug()` statements in `adw_plan_build.py`
- Replace references to file paths with issue IDs where applicable
- Ensure error messages reference issue IDs instead of file paths
- Add issue status to relevant log messages (e.g., when issue is fetched)
- Verify log file structure in `agents/{adw_id}/adw_plan_build/execution.log` still works correctly

### 10. Add Comprehensive Error Handling

- Review all Supabase operations for proper error handling
- Ensure `fetch_issue()` provides clear error messages for:
  - Missing environment variables (from `SupabaseConfig.validate()`)
  - Non-existent issue IDs
  - Database connection failures
  - Malformed response data
- Ensure `create_comment()` provides clear error messages for:
  - Invalid issue IDs (foreign key constraint)
  - Empty comment text
  - Database connection failures
- Add logging for all database operations (info level for success, error level for failures)
- Write unit tests for error cases in Supabase helper functions

### 11. Create Unit Tests for Pydantic Models

- Create `cape/workflows/tests/` directory if it doesn't exist
- Create `test_data_types.py` file
- Write test for `CapeIssue` status defaulting: create instance without status, assert `status == "pending"`
- Write test for `CapeIssue` description trimming: create instance with whitespace, assert trimmed
- Write test for `CapeIssue` status validation: attempt to create with invalid status, assert validation error
- Write test for `CapeIssue.from_supabase()`: pass dict with all fields, assert correct parsing
- Write test for `CapeIssue.from_supabase()` with timestamps: pass ISO timestamp strings, assert parsed to datetime
- Write test for `CapeComment` comment trimming: create instance with whitespace, assert trimmed
- Write test for `CapeComment` validation: create with missing required fields, assert validation error

### 12. Create Unit Tests for Supabase Helper

- Create `test_supabase.py` file in `cape/workflows/tests/`
- Write test for `SupabaseConfig.validate()` with missing `SUPABASE_URL`: mock `os.environ`, assert `ValueError` raised
- Write test for `SupabaseConfig.validate()` with missing `SUPABASE_SERVICE_ROLE_KEY`: assert `ValueError` raised
- Write test for `SupabaseConfig.validate()` with both variables missing: assert both listed in error message
- Write test for `fetch_issue()` success case: mock Supabase client, return sample data, assert `CapeIssue` returned
- Write test for `fetch_issue()` not found case: mock `response.data = None`, assert `ValueError` raised with message "Issue with id {id} not found"
- Write test for `fetch_issue()` API error: mock `APIError` exception, assert `ValueError` raised with context
- Write test for `create_comment()` success case: mock Supabase client, assert `CapeComment` returned
- Write test for `create_comment()` API error: mock `APIError`, assert `ValueError` raised
- Use `unittest.mock.patch` or `pytest-mock` for mocking Supabase client
- Use `pytest.fixture` for common mock setup (mock client, mock data)

### 13. Create Integration Tests for Workflow

- Create `test_adw_plan_build.py` file in `cape/workflows/tests/`
- Write test for `main()` end-to-end success path:
  - Mock `sys.argv` with valid issue ID
  - Mock `fetch_issue()` to return sample `CapeIssue`
  - Mock `classify_issue()` to return valid command
  - Mock `build_plan()` to return successful response
  - Mock `get_plan_file()` to return valid file path
  - Mock `implement_plan()` to return successful response
  - Assert workflow completes without errors
- Write test for `main()` with Supabase fetch failure:
  - Mock `fetch_issue()` to raise `ValueError`
  - Assert `sys.exit(1)` called
  - Assert error logged
- Write test for `parse_args()` with invalid input:
  - Mock `sys.argv` with non-integer issue ID
  - Assert `sys.exit(1)` called
- Use `pytest` as test runner
- Use `unittest.mock.patch` to mock functions and environment

### 14. Update Documentation

- Update `cape/README.md` if exists to mention Supabase requirement
- Document new environment variables (`SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`)
- Update workflow invocation examples to use issue IDs instead of file paths
- Add section on database setup and migration execution
- Create or update `cape/workflows/README.md` with:
  - Overview of Supabase integration
  - Required environment variables
  - Database schema documentation
  - Example usage with issue IDs
  - Migration instructions
- Add troubleshooting section for common errors (missing env vars, missing tables, invalid issue IDs)

### 15. Add pyproject.toml or Dependencies File

- Check if `cape/pyproject.toml` exists, otherwise create it
- Add `supabase-py` dependency (version `^2.0.0` or latest stable)
- Add `pydantic` dependency (version `^2.0.0` or latest compatible)
- Add `python-dotenv` dependency (already exists, verify version)
- Add `pytest` and `pytest-mock` as dev dependencies for testing
- Update script dependencies in `adw_plan_build.py` header:
  ```python
  # /// script
  # dependencies = ["python-dotenv", "pydantic", "supabase"]
  # ///
  ```

### 16. Create Sample Test Data

- Write SQL script `cape/migrations/002_seed_test_data.sql` to insert sample issues:
  ```sql
  INSERT INTO cape_issues (id, description, status) VALUES
  (1, 'Fix login page CSS styling issues', 'pending'),
  (2, 'Add user profile photo upload feature', 'started'),
  (3, 'Refactor authentication module to use JWT', 'completed');
  ```
- Document in `migrations/README.md` that this is optional seed data for testing
- Add instructions for clearing test data: `DELETE FROM cape_issues WHERE id IN (1, 2, 3);`

### 17. Validate End-to-End Workflow

- Ensure Supabase project is running and tables exist
- Ensure `.env` file contains valid `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY`
- Insert test issue into `cape_issues` table: `INSERT INTO cape_issues (description) VALUES ('Test issue for workflow validation') RETURNING id;`
- Note the returned issue ID
- Run workflow: `cd cape && uv run workflows/adw_plan_build.py <issue-id>`
- Verify workflow logs show:
  - "Fetching issue from Supabase" section
  - "Issue fetched: ID=X, Status=pending"
  - "Classifying issue" section
  - "Building implementation plan" section
  - "Finding plan file" section
  - "Implementing solution" section
  - "Workflow completed successfully"
- Check that no errors are logged
- Verify plan file was created in expected location
- Delete test issue: `DELETE FROM cape_issues WHERE id = <issue-id>;`

### 18. Run Validation Commands

Execute every command to validate the feature works correctly with zero regressions.

- `cd cape` - Change directory to the project root
- `python -m pytest workflows/tests/test_data_types.py -v` - Run Pydantic model tests
- `python -m pytest workflows/tests/test_supabase.py -v` - Run Supabase helper tests
- `python -m pytest workflows/tests/test_adw_plan_build.py -v` - Run workflow integration tests
- `python -m pytest workflows/tests/ -v --cov=workflows --cov-report=term-missing` - Run all tests with coverage report
- `uv run workflows/adw_plan_build.py` - Verify usage message shows issue ID syntax
- `uv run workflows/adw_plan_build.py invalid-id` - Verify error handling for non-integer input
- `uv run workflows/adw_plan_build.py 99999` - Verify error handling for non-existent issue ID
- `uv run workflows/adw_plan_build.py <valid-test-issue-id>` - Run full workflow with valid test issue
- `cd ..` - Return to workspace root

## Testing Strategy

### Unit Tests

**Pydantic Models** (`test_data_types.py`):
- Test `CapeIssue` field validation (description trimming, status defaulting to "pending")
- Test `CapeIssue` status literal enforcement (reject invalid statuses)
- Test `CapeIssue.from_supabase()` factory method with various input formats
- Test timestamp parsing from ISO strings to datetime objects
- Test `CapeComment` field validation (comment trimming)
- Test `CapeComment` required field validation

**Supabase Helper** (`test_supabase.py`):
- Test `SupabaseConfig.validate()` with missing environment variables
- Test `fetch_issue()` with mocked successful response
- Test `fetch_issue()` with non-existent issue ID (response.data = None)
- Test `fetch_issue()` with APIError exception
- Test `create_comment()` with mocked successful response
- Test `create_comment()` with APIError exception
- Test client singleton pattern (multiple calls to `get_client()` return same instance)

**Workflow Functions** (`test_adw_plan_build.py`):
- Test `parse_args()` with valid integer issue ID
- Test `parse_args()` with invalid non-integer input (expect sys.exit)
- Test `parse_args()` with missing required argument (expect sys.exit)
- Test `classify_issue()` with mock `CapeIssue` and mock `execute_template()`
- Test `build_plan()` with mock `CapeIssue` and mock `execute_template()`

### Integration Tests

**End-to-End Workflow** (`test_adw_plan_build.py`):
- Test `main()` with all functions mocked for success path
- Test `main()` with `fetch_issue()` raising ValueError (expect sys.exit)
- Test `main()` with `classify_issue()` returning error (expect sys.exit)
- Test logging output contains expected messages (issue ID, status, workflow steps)
- Mock environment variables for Supabase configuration
- Mock Supabase client to avoid real database calls during tests

**Manual Integration Testing**:
- Create real test issue in Supabase
- Run workflow with test issue ID
- Verify workflow completes successfully
- Verify logging shows correct issue ID and status
- Verify plan file is created
- Clean up test data

### Edge Cases

**Missing or Invalid Data**:
- Missing required environment variables (`SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`)
- Non-existent issue ID provided to workflow
- Invalid issue ID format (non-integer, negative number)
- Issue with missing or null description in database
- Issue with invalid status value in database (should be prevented by CHECK constraint)
- Database connection timeout or failure
- Malformed Supabase response (missing expected fields)

**Validation Edge Cases**:
- Description with only whitespace (should trim and fail validation)
- Very long description (verify no truncation or errors)
- Issue with timestamps as None vs valid datetime
- Comment creation on non-existent issue ID (foreign key constraint violation)

**Concurrency and State**:
- Multiple workflow instances accessing same Supabase client (singleton pattern)
- Issue updated in database between fetch and workflow completion (acceptable, workflow uses fetched snapshot)

## Acceptance Criteria

- `main()` fetches a `CapeIssue` from Supabase using an integer issue ID and drives the workflow without reading local files
- CLI usage is `uv run workflows/adw_plan_build.py <issue-id> [adw-id]` where `<issue-id>` is an integer
- `CapeIssue` and `CapeComment` Pydantic models validate data correctly (trim text, default status to "pending", parse timestamps)
- Supabase helper module (`supabase.py`) provides `fetch_issue()` and `create_comment()` functions with error handling
- Environment variables `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are validated on client initialization with clear error messages if missing
- `classify_issue()` and `build_plan()` functions accept `CapeIssue` instances instead of file paths and use `issue.description` for agent templates
- Logging reflects issue IDs and statuses instead of file paths throughout workflow
- File-based usage is completely removed with no CLI flag for legacy support
- Unit tests cover:
  - `CapeIssue` and `CapeComment` model validation (status defaulting, text trimming, timestamp parsing)
  - Supabase helper functions with mocked client (fetch success, fetch not found, comment creation, API errors)
  - Workflow functions with mocked dependencies (argument parsing, issue classification, plan building)
- Integration tests cover:
  - `main()` workflow orchestration with all functions mocked
  - Error pathways (missing env vars, invalid issue ID, database errors)
  - End-to-end execution with real Supabase test database (optional)
- Documentation updated:
  - Environment variable requirements documented in `.env.example` or project README
  - Workflow invocation instructions show issue ID syntax
  - Migration execution instructions provided
  - Database schema documented
- Supabase migration scripts exist:
  - `001_create_cape_issues_tables.sql` creates `cape_issues` and `cape_comments` tables with specified schema
  - Tables include CHECK constraint for status values
  - Indexes created on `cape_issues.status` and `cape_comments.issue_id`
  - Auto-update trigger for `cape_issues.updated_at` column

## Validation Commands

Execute every command to validate the feature works correctly with zero regressions.

- `cd cape` - Change directory to the project root
- `python -m pytest workflows/tests/test_data_types.py -v` - Run Pydantic model unit tests
- `python -m pytest workflows/tests/test_supabase.py -v` - Run Supabase helper unit tests
- `python -m pytest workflows/tests/test_adw_plan_build.py -v` - Run workflow integration tests
- `python -m pytest workflows/tests/ -v --cov=workflows --cov-report=term-missing` - Run all tests with coverage report
- `uv run workflows/adw_plan_build.py` - Verify usage message shows correct syntax (should display help and exit)
- `uv run workflows/adw_plan_build.py invalid-id` - Verify error handling for non-integer input (should log error and exit)
- `uv run workflows/adw_plan_build.py 99999` - Verify error handling for non-existent issue ID (should log error and exit)
- `cd ..` - Return to workspace root

**Manual Validation**:
- Insert test issue: `INSERT INTO cape_issues (description) VALUES ('Test workflow issue') RETURNING id;` in Supabase SQL editor
- Note the returned issue ID
- Run: `cd cape && uv run workflows/adw_plan_build.py <issue-id>`
- Verify workflow completes successfully with no errors
- Verify logs show issue ID and status
- Clean up: `DELETE FROM cape_issues WHERE id = <issue-id>;`

## Notes

### Future Enhancements

**Automated Status Updates**:
- Update issue status to "started" when workflow begins
- Update issue status to "completed" when workflow finishes successfully
- Post workflow progress comments using `create_comment()` at each stage

**Issue Creation from External Systems**:
- API endpoint or CLI command to create issues from GitHub issues, Jira tickets, etc.
- Webhook integration to automatically trigger workflows when issues are created

**Querying and Reporting**:
- CLI command to list issues by status: `uv run workflows/list_issues.py --status pending`
- Dashboard to visualize workflow execution metrics (success rate, duration, issue status distribution)

**Comment Integration**:
- CLI command to add comments to issues: `uv run workflows/comment.py <issue-id> "Comment text"`
- Fetch comments in workflow for context (e.g., user clarifications)

### Technical Debt Considerations

**Migration Rollback**:
- Current migration script lacks DOWN migration for rollback
- Consider adding `001_create_cape_issues_tables_down.sql` to drop tables cleanly

**Connection Pooling**:
- Supabase handles connection pooling server-side (Supavisor)
- No client-side pooling needed, but monitor connection limits for high-volume workflows

**Data Archival**:
- No retention policy for old issues/comments
- Consider adding `archived_at` timestamp and archival process for completed issues

**Rate Limiting**:
- No rate limiting on Supabase operations
- Consider adding retry logic with exponential backoff for transient failures

### Alternative Approaches Considered

**File-based Hybrid**:
- Keep file-based loading with optional `--issue-id` flag
- Rejected: Increases complexity and maintains two code paths
- Decision: Clean break to Supabase-only approach simplifies maintenance

**SQLite Instead of Supabase**:
- Use local SQLite database for simpler setup
- Rejected: Loses cloud-native benefits, multi-user access, and future webhook integrations
- Decision: Supabase provides better foundation for automation and external integrations

**REST API Layer**:
- Build FastAPI REST API for issue management instead of direct Supabase access
- Rejected: Premature abstraction, adds unnecessary complexity for current requirements
- Decision: Direct Supabase access is simpler; REST API can be added later if needed

**Async Supabase Client**:
- Use async patterns (`acreate_client()`, `await` syntax) for better performance
- Rejected: Current workflow is sequential and synchronous; async adds complexity without clear benefit
- Decision: Keep synchronous pattern; revisit if concurrency becomes a requirement

### Context for Lead Engineers

**Workflow Impact**:
- Existing workflow logic (`classify_issue`, `build_plan`, `implement_plan`) unchanged except for data source
- Agent templates continue to receive issue description as string argument
- Logging structure and file organization (`agents/{adw_id}/`) remains identical

**Database Design Rationale**:
- `status` field limited to 3 values (`pending|started|completed`) to keep MVP simple
- Timestamps (`created_at`, `updated_at`) included for future audit/reporting needs but not used in initial workflow
- Foreign key with `ON DELETE CASCADE` ensures comments are automatically cleaned up with issues

**Testing Philosophy**:
- Focus on critical paths: model validation, Supabase operations, workflow orchestration
- Mock Supabase client for unit tests to avoid database dependency
- Provide optional integration test against real Supabase for validation
- Avoid excessive edge case testing (e.g., database corruption scenarios)

**Environment Configuration**:
- Service role key used instead of anon key to bypass Row Level Security (RLS)
- No RLS policies initially; can be added later if multi-tenancy or access control needed
- `python-dotenv` already in use; `.env` file pattern established

**Extensibility Points**:
- `create_comment()` API ready for future status updates but unused in initial implementation
- Pydantic models can easily add fields (e.g., `assignee`, `priority`) without breaking existing code
- Repository pattern can be introduced later if multiple tables need similar CRUD operations
