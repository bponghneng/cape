# Chore Plan: Create CAPE-ADW Command

## Description

Create a new `cape-adw` command that provides a specialized workflow for ADW (Agent Development Workflow) processes. This command will have its own dedicated CLI interface and workflow execution logic, while integrating with the existing Cape CLI infrastructure.

## Relevant Files

- `cape/cape-cli/pyproject.toml` - Need to add the new script entry point for the cape-adw command
- `cape/cape-cli/src/cape_cli/workflow.py` - Contains the existing workflow execution logic that will be leveraged

#### New Files

- `cape/cape-adw/__init__.py` - Python package initialization file
- `cape/cape-adw/cli.py` - CLI implementation using typer framework
- `cape/cape-adw/adw.py` - ADW-specific workflow implementation
- `cape/cape-adw/tests/test_cape_adw.py` - Tests for the ADW functionality

## Step-by-Step Tasks

### Create Directory Structure and Basic Files

- Create the `cape/cape-adw/` directory
- Create `cape/cape-adw/__init__.py` with basic package initialization
- Create `cape/cape-adw/adw.py` with the `execute_adw_workflow` function that returns a success message

### Implement CLI Interface

- Create `cape/cape-adw/cli.py` with typer-based CLI implementation
- Add the `run` command that accepts an issue_id parameter
- Implement error handling and proper exit codes

### Add Script Entry Point

- Update `cape/cape-cli/pyproject.toml` to include the new script entry point
- Add `cape-adw = "cape_adw.cli:app"` to the `[project.scripts]` section

### Create Tests

- Create `cape/cape-adw/tests/test_cape_adw.py` with basic test for the `execute_adw_workflow` function
- Test that the function returns the expected success message format

### Validate Implementation

- Run the validation commands to ensure everything works correctly

## Validation Commands

Execute every command to validate the chore is complete with zero regressions.

```bash
# Install the updated package with the new script entry point
cd cape/cape-cli && uv sync

# Test the CLI help command
uv run cape-adw --help

# Test the CLI run command with a sample issue ID
uv run cape-adw run 123

# Run the tests
cd cape/cape-adw && python -m pytest tests/ -v
```

## Notes

- The ADW workflow implementation is intentionally minimal for now, returning a success message instead of executing complex workflow logic
- This approach allows for incremental development of ADW-specific features while maintaining a working CLI interface
- The implementation follows the same patterns as existing Cape CLI commands for consistency
- Future iterations can expand the `execute_adw_workflow` function to include actual ADW-specific workflow logic
