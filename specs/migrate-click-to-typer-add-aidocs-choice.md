# Chore: Migrate from Click to Typer for the Interface and Add Choice for Copying AI Docs

## Chore Description
Migrate the existing `scripts/create-symlinks.py` script from Click to Typer for the CLI interface. Additionally, add a choice for copying the ai_docs directory or not, giving users more control over which assets they want to include when setting up symlinks.

The current script uses Click for CLI argument parsing and automatically includes ai_docs in the symlink creation. The new implementation should:

1. Replace Click with Typer for the CLI interface while maintaining all existing functionality
2. Add a new option/choice to allow users to opt-in or opt-out of copying ai_docs
3. Preserve all existing symlink creation logic, error handling, and batch operations
4. Maintain cross-platform compatibility and elevation handling on Windows
5. Update help text and user interaction to reflect the new Typer interface
6. Keep the UV single-file script format with inline dependencies

## Relevant Files
Use these files to resolve the chore:

- **scripts/create-symlinks.py** (lines 1-560) - Current implementation using Click:
  - Lines 39: Current Click import and usage
  - Lines 468-483: Current Click command definition with arguments and options
  - Lines 60-67: Current SYMLINK_CONFIG that includes ai_docs mapping
  - Lines 471-483: Main function signature using Click decorators
  - Lines 4-7: UV script dependencies declaration including Click

### New Files
No new files needed - the changes will be made to the existing `scripts/create-symlinks.py` file.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Update UV script dependencies
- Replace `"click"` with `"typer"` in the UV script dependencies declaration (lines 4-7)
- Keep `"rich"` dependency as it's still needed for colored output
- Update the requires-python version to ensure compatibility with Typer

### Step 2: Replace Click imports with Typer
- Replace `import click` with `import typer` (line 39)
- Remove `from rich.prompt import Confirm` import as Typer has built-in confirmation handling
- Keep all other imports unchanged

### Step 3: Update SYMLINK_CONFIG to make ai_docs conditional
- Modify the SYMLINK_CONFIG structure to separate ai_docs from the other mappings
- Create a separate AI_DOCS_CONFIG constant for the ai_docs mapping
- Update the main processing logic to conditionally include ai_docs based on user choice

### Step 4: Convert Click command to Typer function
- Remove the `@click.command()`, `@click.argument()`, and `@click.option()` decorators (lines 468-470)
- Update the main function signature to use Typer's parameter annotation approach
- Convert `target_dir: str` to `target_dir: str` with proper Typer argument handling
- Convert `--force` flag to use Typer's boolean option with default False
- Add new `--include-ai-docs` / `--no-include-ai-docs` option for ai_docs choice

### Step 5: Update main function to use Typer patterns
- Modify the main function to use Typer's approach instead of Click's
- Add docstring to the main function to provide help text for Typer
- Update parameter documentation using Typer's `typer.Argument()` and `typer.Option()` annotations
- Preserve all existing validation and processing logic

### Step 6: Implement ai_docs conditional logic
- Modify the symlink processing loop to handle the ai_docs choice
- When `include_ai_docs` is True, include the AI_DOCS_CONFIG in processing
- When `include_ai_docs` is False, skip the ai_docs symlink creation
- Update user feedback messages to indicate whether ai_docs are being included or skipped

### Step 7: Replace Click path handling with Typer
- Update path validation to work with Typer's parameter handling
- Ensure the `target_dir` parameter validation continues to work correctly
- Maintain the expand_and_resolve_path functionality

### Step 8: Update confirmation prompts to use Typer
- Replace `rich.prompt.Confirm` usage with Typer's built-in confirmation handling
- Update the environment sample file copying logic to work with the new confirmation approach
- Ensure force mode still bypasses all confirmations

### Step 9: Update the main execution entry point
- Replace `if __name__ == "__main__": main()` with `if __name__ == "__main__": typer.run(main)`
- Ensure the Typer app is properly configured and runs correctly

### Step 10: Update help text and documentation
- Update the main function docstring to reflect new functionality
- Ensure help text mentions the new ai_docs choice option
- Update any inline comments that reference Click to mention Typer instead
- Verify that `--help` output is clear and comprehensive

### Step 11: Test the migration thoroughly
- Test basic functionality with the new Typer interface
- Test the new ai_docs choice option in both enabled and disabled states
- Test force mode with all combinations of options
- Test on Windows to ensure elevation and batch operations still work
- Verify backward compatibility of basic usage patterns

## Validation Commands
Execute every command to validate the chore is complete with zero regressions.

- `uv run scripts/create-symlinks.py --help` - Verify help text displays correctly with Typer interface and shows new ai_docs option
- `uv run scripts/create-symlinks.py Ctempcape-batch-test --force` - Test script execution with force mode in the existing test directory
- `uv run scripts/create-symlinks.py Ctempcape-batch-test --force --include-ai-docs` - Test script execution with ai_docs enabled
- `uv run scripts/create-symlinks.py Ctempcape-batch-test --force --no-include-ai-docs` - Test script execution with ai_docs disabled
- `Get-ChildItem Ctempcape-batch-test -Recurse | Where-Object { $_.Target -ne $null }` - Verify symlinks were created correctly on Windows
- `Test-Path "Ctempcape-batch-test\.claude\agents" -PathType Container` - Verify agent symlinks were created
- `Test-Path "Ctempcape-batch-test\.claude\hooks" -PathType Container` - Verify hooks symlinks were created  
- `Test-Path "Ctempcape-batch-test\.claude\commands" -PathType Container` - Verify commands symlinks were created
- `Test-Path "Ctempcape-batch-test\ai_docs" -PathType Container` - Verify ai_docs symlinks were created when option enabled

## Notes
- Typer provides a more modern and Pythonic approach to CLI applications with better type hints integration
- The new ai_docs choice gives users more flexibility - some may only want agent/hook configurations without the documentation
- Typer's automatic help generation and type-based validation should provide a better user experience
- The migration should maintain 100% backward compatibility for existing usage patterns (target_dir and --force)
- Windows elevation and batch processing logic should remain unchanged as it's not related to the CLI framework
- Rich library integration with Typer provides excellent colored output and formatting capabilities
- The UV script format allows easy dependency management without requiring separate requirements files