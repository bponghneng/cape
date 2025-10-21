# Chore Plan: Create Issue Scripts

## Description

Extend the Supabase-backed workflow tooling with scripts that can insert new Cape issues. Provide two entry points:

- `create_issue_from_string.py`: accepts an in-memory string description, creates a `cape_issues` row, and returns the new issue ID.
- `create_issue_from_file.py`: reads a file containing the issue description, creates the row, and returns the new issue ID.

Both scripts share the existing Supabase helper (`cape/workflows/supabase.py`) so they respect the same configuration, models, and Row Level Security settings. A new shared function `create_issue(description: str) -> CapeIssue` will be added to `supabase.py` following the established pattern of `fetch_issue()` and `create_comment()`.

The scripts follow the existing workflow pattern from `adw_plan_build.py`, using argparse for CLI arguments, setup_logger for traceability, and proper error handling with exit codes.

## Relevant Files

### Existing Files to Modify

- **`cape/workflows/supabase.py`** - Add `create_issue(description: str) -> CapeIssue` function after the Comment Operations section (after line 126). This function validates the description is non-empty, inserts into the `cape_issues` table with status="pending", and returns the created CapeIssue model.

### New Files to Create

#### New Scripts

- **`cape/workflows/create_issue_from_string.py`** - CLI script accepting description as command-line argument. Uses argparse with a single positional argument, calls `create_issue()`, prints issue ID to stdout, and handles errors with sys.exit(1).

- **`cape/workflows/create_issue_from_file.py`** - CLI script reading description from file path. Validates file exists and is readable, reads with explicit UTF-8 encoding, calls `create_issue()`, prints issue ID to stdout.

#### New Test Files

- **`cape/workflows/test_supabase_create_issue.py`** - Unit tests for the `create_issue()` function including success case, empty description validation, and database error handling.

- **`cape/workflows/test_cli_scripts.py`** - Integration tests for both CLI scripts validating exit codes, stdout output, and error scenarios.

### Files Used as Reference

- **`cape/workflows/adw_plan_build.py`** (lines 1-250) - Reference pattern for script structure, argparse usage, error handling, and logging setup.

- **`cape/workflows/data_types.py`** (lines 62-87) - CapeIssue Pydantic model with field validation.

- **`cape/workflows/utils.py`** (lines 14-67) - setup_logger and make_adw_id utilities.

- **`cape/migrations/001_create_cape_issues_tables.sql`** - Database schema showing cape_issues table structure with auto-increment id, description, status, and timestamps.

## Step-by-Step Tasks

### 1. Add create_issue() function to supabase.py

Implement the shared database function for issue creation following the established pattern:

- Add function after Comment Operations section (after line 126) in `cape/workflows/supabase.py`
- Function signature: `def create_issue(description: str) -> CapeIssue`
- Validate description is not empty after stripping whitespace
- Raise `ValueError("Issue description cannot be empty")` for empty input
- Call `get_client()` to obtain Supabase singleton
- Insert issue with `{"description": description_clean, "status": "pending"}` into `cape_issues` table
- Validate `response.data` exists before constructing model
- Return `CapeIssue(**response.data[0])` constructed from database response
- Catch `APIError` and re-raise as `ValueError(f"Failed to create issue: {e}") from e`
- Include `logger.error(f"Database error creating issue: {e}")` call for diagnostics
- Add docstring documenting args, return value, and exceptions

**Validation:**
- Function follows exact code style and pattern of `fetch_issue()` and `create_comment()`
- Error messages are clear and actionable
- Exception chaining preserves stack traces with `from e`

### 2. Create create_issue_from_string.py CLI script

Create standalone script accepting description as command-line argument:

- Create file at `cape/workflows/create_issue_from_string.py`
- Add uv shebang: `#!/usr/bin/env -S uv run`
- Add inline dependencies metadata:
  ```python
  # /// script
  # requires-python = ">=3.12"
  # dependencies = ["python-dotenv", "pydantic>=2.0", "supabase>=2.0"]
  # ///
  ```
- Import required modules: `sys`, `argparse`, `load_dotenv`, `create_issue`, `setup_logger`, `make_adw_id`
- Implement `parse_args()` function with argparse:
  - Create ArgumentParser with description "Create a Cape issue from description string"
  - Add positional argument "description" with help text
  - Add usage examples in epilog
  - Return parsed args
- Implement `main()` function:
  - Call `load_dotenv()` to load environment variables
  - Parse arguments with `parse_args()`
  - Generate ADW ID with `make_adw_id()`
  - Setup logger with `setup_logger(adw_id, "create_issue_from_string")`
  - Log ADW ID and operation start
  - Try-except block:
    - Call `create_issue(args.description)` to create issue
    - Log success with issue ID
    - Print only issue ID to stdout with `print(issue.id)`
  - Catch `ValueError` and log error, exit with `sys.exit(1)`
  - Catch generic `Exception` and log unexpected error, exit with `sys.exit(1)`
- Add `if __name__ == "__main__": main()` guard

**Validation:**
- Script is executable with `uv run create_issue_from_string.py "Test description"`
- Prints only numeric issue ID to stdout on success
- Exits with code 0 on success
- Exits with code 1 on errors
- Log file created at `agents/{adw_id}/create_issue_from_string/execution.log`
- Help message displays with `--help` flag

### 3. Create create_issue_from_file.py CLI script

Create standalone script reading description from file path:

- Create file at `cape/workflows/create_issue_from_file.py`
- Add uv shebang and inline dependencies (same as create_issue_from_string.py)
- Import required modules including `Path` from `pathlib`
- Implement `read_file_description(file_path: str) -> str` helper function:
  - Create `Path` object from file_path
  - Validate file exists with `path.exists()`, raise `FileNotFoundError` if not
  - Validate is regular file with `path.is_file()`, raise `ValueError` if not
  - Try-except block:
    - Open file with explicit `encoding='utf-8'`
    - Read contents with `f.read()`
    - Return `content.strip()` to remove whitespace
  - Catch `UnicodeDecodeError` and raise `ValueError(f"Failed to decode file {file_path} as UTF-8: {e}") from e`
  - Add docstring documenting args, return value, and exceptions
- Implement `parse_args()` function:
  - Create ArgumentParser with description "Create a Cape issue from description file"
  - Add positional argument "file_path" with help text
  - Add usage examples in epilog
  - Return parsed args
- Implement `main()` function:
  - Call `load_dotenv()`
  - Parse arguments
  - Generate ADW ID and setup logger with "create_issue_from_file" trigger type
  - Log file path being read
  - Try-except block:
    - Call `read_file_description(args.file_path)` to read file
    - Log description length
    - Call `create_issue(description)` to create issue
    - Log success with issue ID
    - Print only issue ID to stdout
  - Catch `FileNotFoundError`, `ValueError`, and generic `Exception` separately
  - Log appropriate error messages and exit with `sys.exit(1)`
- Add `if __name__ == "__main__": main()` guard

**Validation:**
- Create test file with description text
- Script is executable with `uv run create_issue_from_file.py test_file.txt`
- Prints only numeric issue ID to stdout on success
- Non-existent file exits with code 1 and clear error message
- Directory path exits with code 1 and clear error message
- Empty file exits with code 1 and clear error message
- Multi-line files are handled correctly (full content used as description)

### 4. Create unit tests for create_issue() function

Write tests validating create_issue() behavior:

- Create test file `cape/workflows/test_supabase_create_issue.py`
- Import testing framework (pytest or unittest based on project convention)
- Import `create_issue` function and `CapeIssue` model
- Mock `get_client()` to return mock Supabase client
- Mock `client.table().insert().execute()` chain
- Implement test cases:
  - `test_create_issue_success`: Mock successful insert, verify returns CapeIssue with ID from response
  - `test_create_issue_empty_description`: Pass empty string "", verify raises ValueError with message "Issue description cannot be empty"
  - `test_create_issue_whitespace_only`: Pass "   ", verify raises ValueError
  - `test_create_issue_trims_description`: Pass "  Test  ", verify insert called with trimmed "Test"
  - `test_create_issue_database_error`: Mock APIError from Supabase, verify converted to ValueError with context
  - `test_create_issue_empty_response`: Mock response with data=None, verify raises ValueError
- Verify `logger.error()` called on database errors
- Verify `insert()` called with correct data structure `{"description": ..., "status": "pending"}`
- Run tests and verify all pass

**Validation:**
- All test cases pass
- Tests use mocking to isolate database layer (no actual Supabase calls)
- Test output is clear and descriptive
- Coverage includes success, error, and edge cases

### 5. Create integration tests for CLI scripts

Test both CLI scripts end-to-end:

- Create test file `cape/workflows/test_cli_scripts.py`
- Import `subprocess`, `tempfile`, `Path`
- Setup test fixtures for temporary files and test issue cleanup
- Implement tests for `create_issue_from_string.py`:
  - `test_string_valid_description`: Execute script with valid description, verify exit code 0, stdout contains numeric ID
  - `test_string_empty_description`: Execute script with empty string, verify exit code 1
  - `test_string_missing_env_vars`: Temporarily remove environment variables, verify exit code 1
- Implement tests for `create_issue_from_file.py`:
  - `test_file_valid_description`: Create temp file with description, execute script, verify exit code 0 and ID output
  - `test_file_nonexistent_file`: Execute script with non-existent path, verify exit code 1
  - `test_file_directory_path`: Execute script with directory path, verify exit code 1
  - `test_file_empty_file`: Create empty temp file, execute script, verify exit code 1
  - `test_file_multiline_description`: Create temp file with multi-line content, verify full content used
- Use `subprocess.run()` to execute scripts and capture stdout, stderr, and return code
- Clean up created test issues after each test (delete from database or use test instance)
- Run tests and verify all pass

**Validation:**
- All integration tests pass
- Tests validate exit codes are correct (0=success, 1=error)
- Tests validate stdout contains only numeric issue ID on success
- Tests handle cleanup of test data
- Tests can run against test database or with mocked Supabase

### 6. Manual end-to-end validation

Manually test both scripts against real Supabase instance:

- Verify `.env` file contains valid Supabase credentials (SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
- Test `create_issue_from_string.py`:
  - Execute: `uv run create_issue_from_string.py "Test issue from string"`
  - Verify prints numeric issue ID
  - Verify exit code 0 with `echo $?`
  - Check Supabase dashboard to confirm issue created with correct description and status="pending"
  - Verify log file created at `agents/{adw_id}/create_issue_from_string/execution.log`
  - Test with multi-line description using quotes
  - Test error handling with empty string (should exit 1)
- Test `create_issue_from_file.py`:
  - Create test file: `echo "Test issue from file" > /tmp/test_issue.txt`
  - Execute: `uv run create_issue_from_file.py /tmp/test_issue.txt`
  - Verify prints numeric issue ID and exit code 0
  - Check Supabase dashboard to confirm issue created
  - Verify log file created at `agents/{adw_id}/create_issue_from_file/execution.log`
  - Test with multi-line file containing newlines
  - Test error handling with non-existent file (should exit 1)
  - Test error handling with directory path (should exit 1)
- Verify stdout output is clean (only issue ID, no extra logging or formatting)
- Verify error messages are clear and actionable
- Clean up all test issues from Supabase dashboard
- Document any edge cases or issues discovered during testing

**Validation:**
- Both scripts work correctly against real Supabase instance
- Issues appear in Supabase dashboard with correct data
- Log files created in expected directory structure
- Stdout output is clean for scripting integration
- Error messages guide user to resolution
- All test scenarios documented

### 7. Add documentation and usage examples

Document the new scripts with complete usage information:

- Add/verify docstrings for all functions:
  - `create_issue()` function in supabase.py
  - `read_file_description()` function in create_issue_from_file.py
  - `parse_args()` functions in both scripts
  - `main()` functions in both scripts
- Create usage documentation (add to project README or create separate doc):
  - **Quick Start** section with simple examples:
    ```bash
    # Create issue from string
    uv run create_issue_from_string.py "Fix login bug"

    # Create issue from file
    uv run create_issue_from_file.py issue_description.txt
    ```
  - **Prerequisites** section documenting required environment variables:
    - `SUPABASE_URL`: Your Supabase project URL
    - `SUPABASE_SERVICE_ROLE_KEY`: Service role key for database access
    - Instructions to get credentials from Supabase dashboard
  - **Exit Codes** section:
    - 0: Success
    - 1: Error (validation, database, file, or environment issues)
  - **Output Format** section:
    - Success: Prints only numeric issue ID to stdout
    - Errors: Logged to stderr and log files
  - **Scripting Integration** section with bash example:
    ```bash
    # Capture issue ID in variable
    ISSUE_ID=$(uv run create_issue_from_string.py "New feature request")
    echo "Created issue: $ISSUE_ID"

    # Use in conditional
    if uv run create_issue_from_file.py feature.txt; then
        echo "Issue created successfully"
    else
        echo "Failed to create issue"
    fi
    ```
  - **Error Scenarios** section documenting common issues and fixes:
    - Missing environment variables → Check .env file
    - Empty description → Ensure description has content
    - File not found → Verify file path is correct
    - Database connection error → Check Supabase URL and credentials
  - **Log Files** section:
    - Location: `agents/{adw_id}/create_issue_*/execution.log`
    - Purpose: Detailed execution logs for debugging
- Add inline code comments for complex logic
- Update main project README if scripts should be documented there
- Review documentation for completeness and accuracy

**Validation:**
- All functions have complete docstrings
- Usage examples are tested and accurate
- Environment setup instructions are clear
- Error troubleshooting guidance is helpful
- Scripting examples work as documented

### 8. Run validation commands

Execute every command to validate the chore is complete with zero regressions:

- `cd cape` - Change to project root directory
- Run unit tests for create_issue function:
  - `uv run pytest cape/workflows/test_supabase_create_issue.py -v` (or appropriate test command)
  - Verify all unit tests pass
- Run integration tests for CLI scripts:
  - `uv run pytest cape/workflows/test_cli_scripts.py -v`
  - Verify all integration tests pass
- Manual smoke tests:
  - `uv run cape/workflows/create_issue_from_string.py "Validation test issue"` - Verify creates issue
  - `echo "File validation test" > /tmp/test.txt && uv run cape/workflows/create_issue_from_file.py /tmp/test.txt` - Verify creates issue
  - Verify issues appear in Supabase dashboard
  - Clean up test issues
- Run any existing project tests to verify no regressions:
  - `uv run pytest` (if project has test suite)
- Verify scripts are executable and have correct permissions
- Verify log files are created in expected locations
- `cd ..` - Return to workspace root

**Validation:**
- All tests pass with zero failures
- No regressions introduced to existing functionality
- Scripts work correctly in manual testing
- All validation commands execute successfully

## Validation Commands

Execute every command to validate the chore is complete with zero regressions.

- `cd cape` - Change to project root directory.
- `uv run pytest cape/workflows/test_supabase_create_issue.py -v` - Run unit tests for create_issue function (if pytest is configured).
- `uv run pytest cape/workflows/test_cli_scripts.py -v` - Run integration tests for CLI scripts (if pytest is configured).
- `uv run cape/workflows/create_issue_from_string.py "Validation test"` - Manual test of string script.
- `echo "Test from file" > /tmp/validation_test.txt && uv run cape/workflows/create_issue_from_file.py /tmp/validation_test.txt` - Manual test of file script.
- Verify created issues appear in Supabase dashboard and clean them up.
- `cd ..` - Return to workspace root.

## Notes

### Design Rationale

**Shared Function Approach:**
- Centralizing issue creation logic in `create_issue()` follows DRY principles
- Both CLI scripts are thin wrappers focusing on input handling
- Easier to test, maintain, and extend
- Consistent with existing pattern of `fetch_issue()` and `create_comment()`

**CLI Framework Choice (argparse):**
- Maintains consistency with existing workflow scripts (adw_plan_build.py)
- Simple positional arguments don't require advanced features of typer
- No additional dependencies beyond what's already used

**Error Handling Pattern:**
- Follows established pattern: module functions raise ValueError, CLI scripts catch and exit
- Exception chaining (`from e`) preserves stack traces for debugging
- Separate logging and user-facing error messages

**Logging with ADW ID:**
- Enables traceability across workflow executions
- Creates organized log directory structure
- Consistent with existing workflow tooling

**Output to stdout:**
- Printing only issue ID enables scripting integration
- Logs go to files, not stdout, keeping output clean
- Exit codes enable conditional logic in shell scripts

### Future Enhancements

**Potential Extensions (not in scope for this chore):**
- Add `--status` flag to create issues with status other than "pending"
- Bulk issue creation from CSV or JSON files
- Update issue status script (change pending → started → completed)
- List issues by status script
- Add comments to issues from CLI
- Integration with GitHub Issues for two-way sync
- Webhook triggers for issue creation events

**Testing Improvements:**
- Add performance tests for large descriptions
- Add concurrency tests for simultaneous issue creation
- Mock Supabase for all integration tests (currently use real instance)
- Add test coverage reporting

**Usability Enhancements:**
- Add `--dry-run` flag to validate without creating issue
- Add `--verbose` flag for detailed console logging
- Support reading from stdin (e.g., `echo "Issue" | create_issue_from_stdin.py`)
- Add JSON output mode for programmatic parsing

### Legacy Patterns

**Duplicate Files:**
The codebase analysis found duplicate files in both `/Users/bponghneng/git/cape/cape/workflows/` and `/Users/bponghneng/git/cape/workflows/`. For this chore, implement in the `cape/workflows/` directory as that appears to be the primary location based on the project structure.

**Database Schema Considerations:**
- The cape_issues table has auto-increment `id` field (SERIAL PRIMARY KEY)
- Status defaults to "pending" with CHECK constraint (pending|started|completed)
- Timestamps (created_at, updated_at) are managed by database triggers
- Pydantic model validation provides additional layer of data integrity

### Context for Planning

**Existing Infrastructure Strengths:**
- Robust Supabase client singleton with environment validation
- Comprehensive error handling pattern established
- Logging infrastructure with unique execution IDs
- Pydantic models with field validation
- Migration scripts for database schema

**Alignment with Project Goals:**
This chore enables programmatic issue creation, supporting the larger goal of automated workflow orchestration. It provides the foundation for future automation features like bulk imports, GitHub integration, and webhook-triggered workflows.

**Simplicity Mindset:**
This implementation follows MVP principles by:
- Focusing on core functionality (create issues)
- Avoiding premature features (status updates, bulk operations)
- Reusing existing infrastructure (Supabase helper, logging, models)
- Simple CLI interface (one argument, clear output)
- Deferring advanced features to future iterations
