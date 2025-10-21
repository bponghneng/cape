# Create Issue Scripts

Documentation for the Cape issue creation CLI scripts.

## Overview

Two command-line scripts for creating Cape issues programmatically:

- `create_issue_from_string.py` - Create issue from command-line argument
- `create_issue_from_file.py` - Create issue from file contents

Both scripts use the Supabase-backed `create_issue()` function and follow the established workflow patterns with ADW ID tracking and structured logging.

## Quick Start

### Create Issue from String

```bash
# Basic usage
uv run workflows/create_issue_from_string.py "Fix login bug"

# Multi-line description
uv run workflows/create_issue_from_string.py "Add user authentication

Implement OAuth2 flow
Add session management"
```

### Create Issue from File

```bash
# Basic usage
uv run workflows/create_issue_from_file.py issue_description.txt

# With absolute path
uv run workflows/create_issue_from_file.py /tmp/feature_request.txt
```

## Prerequisites

### Required Environment Variables

Both scripts require Supabase credentials to be set:

- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY`: Service role key for database access

### Setting Up Environment Variables

1. Get credentials from your Supabase project dashboard:
   - Navigate to Project Settings → API
   - Copy the Project URL (SUPABASE_URL)
   - Copy the service_role key (SUPABASE_SERVICE_ROLE_KEY)

2. Set environment variables:
   ```bash
   export SUPABASE_URL="https://your-project.supabase.co"
   export SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"
   ```

   Or create a `.env` file in the project root:
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
   ```

## Exit Codes

Both scripts use standard exit codes:

- **0**: Success - Issue created successfully
- **1**: Error - Validation, database, file, or environment error occurred

Exit codes enable scripting integration with conditional logic.

## Output Format

### Success Output

On success, scripts print **only the numeric issue ID** to stdout:

```
456
```

This clean output format enables easy capture in shell scripts:

```bash
ISSUE_ID=$(uv run workflows/create_issue_from_string.py "New feature")
echo "Created issue: $ISSUE_ID"
```

### Error Output

Errors are logged to:
- stderr (summary error message)
- Log files at `agents/{adw_id}/create_issue_*/execution.log`

Error output does NOT pollute stdout, keeping it clean for piping and scripting.

## Scripting Integration

### Capture Issue ID

```bash
# Capture issue ID in variable
ISSUE_ID=$(uv run workflows/create_issue_from_string.py "New feature request")
echo "Created issue: $ISSUE_ID"
```

### Conditional Execution

```bash
# Use exit code for conditional logic
if uv run workflows/create_issue_from_file.py feature.txt; then
    echo "Issue created successfully"
else
    echo "Failed to create issue"
    exit 1
fi
```

### Error Handling

```bash
# Capture both stdout and stderr
ISSUE_ID=$(uv run workflows/create_issue_from_string.py "Bug fix" 2>&1)
if [ $? -eq 0 ]; then
    echo "Success! Issue ID: $ISSUE_ID"
else
    echo "Error: $ISSUE_ID"
fi
```

### Batch Creation

```bash
# Create multiple issues from files
for file in issues/*.txt; do
    echo "Creating issue from $file..."
    ISSUE_ID=$(uv run workflows/create_issue_from_file.py "$file")
    if [ $? -eq 0 ]; then
        echo "  ✅ Created: $ISSUE_ID"
    else
        echo "  ❌ Failed: $file"
    fi
done
```

## Error Scenarios and Solutions

### Missing Environment Variables

**Error**: `Missing required Supabase environment variables: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY`

**Solution**: Set required environment variables (see Prerequisites section)

### Empty Description

**Error**: `Issue description cannot be empty`

**Solution**: Provide non-empty description after trimming whitespace

**Causes**:
- Empty string argument: `""`
- Whitespace-only argument: `"   "`
- Empty file content

### File Not Found

**Error**: `File not found: /path/to/file.txt`

**Solution**: Verify file path is correct and file exists

### Invalid File Path

**Error**: `Path is not a regular file: /tmp`

**Solution**: Provide path to a regular file, not a directory

**Causes**:
- Directory path provided instead of file
- Special file types (symlinks, devices)

### Database Connection Error

**Error**: `Failed to create issue: <database error details>`

**Solution**: Check Supabase URL and credentials are correct

**Debug steps**:
1. Verify SUPABASE_URL is accessible
2. Verify SUPABASE_SERVICE_ROLE_KEY is valid
3. Check network connectivity
4. Review log files for detailed error traces

## Log Files

### Location

Log files are created at:
```
agents/{adw_id}/create_issue_from_string/execution.log
agents/{adw_id}/create_issue_from_file/execution.log
```

Where `{adw_id}` is a unique 8-character execution ID.

### Purpose

Log files contain:
- ADW ID for execution traceability
- Timestamp for each operation
- Detailed error messages and stack traces
- Database operation details

### Viewing Logs

```bash
# Find recent logs
ls -lt agents/*/create_issue_*/execution.log | head -5

# View specific log
cat agents/abc12345/create_issue_from_string/execution.log
```

## Command-Line Help

Both scripts provide built-in help:

```bash
# String script help
uv run workflows/create_issue_from_string.py --help

# File script help
uv run workflows/create_issue_from_file.py --help
```

## API Reference

### create_issue() Function

Located in `workflows/supabase_client.py`:

```python
def create_issue(description: str) -> CapeIssue
```

**Parameters**:
- `description` (str): Issue description text. Leading/trailing whitespace is trimmed. Must not be empty after trimming.

**Returns**:
- `CapeIssue`: Created issue with database-generated id, status="pending", and timestamps.

**Raises**:
- `ValueError`: If description is empty after trimming, or if database operation fails.

**Example**:
```python
from supabase_client import create_issue

issue = create_issue("Fix authentication bug")
print(f"Created issue {issue.id}")
```

## Testing

### Unit Tests

Test the `create_issue()` function:
```bash
uv run pytest workflows/test_supabase_create_issue.py -v
```

### Integration Tests

Test CLI scripts end-to-end:
```bash
uv run pytest workflows/test_cli_scripts.py -v
```

### Manual Smoke Tests

```bash
# Test string script
uv run workflows/create_issue_from_string.py "Test issue"

# Test file script
echo "Test from file" > /tmp/test.txt
uv run workflows/create_issue_from_file.py /tmp/test.txt
```

## Implementation Details

### Shared Architecture

Both scripts use:
- `create_issue()` function from `supabase_client.py` for database operations
- `make_adw_id()` for unique execution tracking
- `setup_logger()` for structured logging
- `argparse` for command-line argument parsing
- `python-dotenv` for environment variable loading

### Error Handling Pattern

1. Module functions (like `create_issue()`) raise `ValueError` for validation and database errors
2. CLI scripts catch exceptions and:
   - Log detailed error to file
   - Print user-friendly error to stderr
   - Exit with code 1

### Data Flow

**String Script**:
```
Command line argument
    ↓
parse_args()
    ↓
create_issue(description)
    ↓
Supabase insert
    ↓
Print issue.id to stdout
```

**File Script**:
```
File path argument
    ↓
read_file_description(path)
    ↓
create_issue(description)
    ↓
Supabase insert
    ↓
Print issue.id to stdout
```

## Future Enhancements

Potential extensions not in current scope:

- **Status control**: `--status` flag to create issues with status other than "pending"
- **Bulk operations**: Create multiple issues from CSV or JSON
- **Status updates**: Script to change issue status (pending → started → completed)
- **List/query**: Scripts to list issues by status or search descriptions
- **Comments**: Add comments to issues from CLI
- **GitHub sync**: Two-way integration with GitHub Issues
- **Webhooks**: Trigger events on issue creation
- **Dry run**: `--dry-run` flag to validate without creating
- **Verbose mode**: `--verbose` flag for console logging
- **stdin support**: Read from stdin (e.g., `echo "Issue" | create_issue_from_stdin.py`)
- **JSON output**: `--json` flag for machine-readable output

## Troubleshooting

### Script Not Found

If you get "command not found" error:

1. Ensure you're in the project root directory
2. Use `uv run` with full path: `uv run workflows/create_issue_from_string.py`
3. Check file exists: `ls -la workflows/create_issue_from_string.py`

### Import Errors

If you get import errors:

1. Ensure dependencies are installed (uv handles this automatically)
2. Check Python version is >=3.12
3. Verify script metadata block has correct dependencies

### Permission Denied

If you get permission errors:

1. Make scripts executable: `chmod +x workflows/create_issue_*.py`
2. Or use `uv run` which doesn't require executable permission

## Support

For issues or questions:

1. Check log files in `agents/{adw_id}/create_issue_*/execution.log`
2. Review this documentation for common scenarios
3. Verify environment variables are set correctly
4. Test Supabase connection directly
5. Review test files for expected behavior examples
