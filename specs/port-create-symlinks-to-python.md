# Chore: Port create-symlinks.ps1 to Python UV Single-File Script

## Chore Description
Port the existing PowerShell script `scripts/create-symlinks.ps1` to a Python single-file script using UV's inline script metadata format (PEP 723). The new Python script should:

1. Be executable as a standalone UV script with inline dependency declarations
2. Maintain all the functionality of the PowerShell version:
   - Create symlinks from cape repository to target directory
   - Handle agent files, hooks, commands, and AI documentation
   - Support force mode to skip confirmations
   - Validate repository structure and target directory
   - Batch symlink operations with proper error handling
   - Optionally copy `.env.hooks.example` file when hooks are created
3. Use cross-platform Python libraries for filesystem operations
4. Include proper CLI argument parsing and help text
5. Provide clear user feedback with colored output
6. Follow UV script best practices with shebang for direct execution

The script should be named `scripts/create-symlinks.py` and be executable on all platforms (Windows, macOS, Linux).

## Relevant Files
Use these files to resolve the chore:

- **scripts/create-symlinks.ps1** (lines 1-301) - Source PowerShell implementation containing all the logic to port:
  - Symlink creation logic with batch operations
  - Directory validation and parent directory creation
  - Handling of existing symlinks, files, and directories
  - Environment file copying with user confirmation
  - Force mode support
  - CLI parameter parsing and help text

- **scripts/create-symlinks.sh** (lines 1-248) - Bash implementation that can serve as cross-reference:
  - Configuration-driven symlink mappings
  - Error handling patterns
  - User interaction patterns

- **ai_docs/uv-scripts-guide.md** (lines 1-361) - UV scripts documentation:
  - Lines 122-157: Creating scripts with inline metadata using `uv init --script`
  - Lines 130-176: Declaring script dependencies with `uv add --script`
  - Lines 197-231: Using shebang to create executable files
  - Lines 143-149: Script metadata format with dependencies declaration

### New Files
- **scripts/create-symlinks.py** - New Python UV single-file script that replaces the PowerShell version with cross-platform Python implementation

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Initialize the UV Python script with metadata
- Use `uv init --script` to create the basic script structure at `scripts/create-symlinks.py`
- Specify Python 3.12+ as the minimum version requirement
- Set up the shebang line for direct execution: `#!/usr/bin/env -S uv run --script`

### Step 2: Add required dependencies
- Use `uv add --script` to add dependencies needed for the script:
  - `rich` - for colored console output and user interaction
  - `click` - for CLI argument parsing with help text
  - No additional dependencies needed as `pathlib` and `os` are in stdlib

### Step 3: Implement core configuration and constants
- Define symlink mapping configuration matching the PowerShell version:
  - `agents/claude-code` → `.claude/agents` (*.md files)
  - `agents/opencode` → `.opencode/agent` (*.md files)
  - `hooks/claude-code` → `.claude/hooks` (all files/dirs)
  - `commands/claude-code` → `.claude/commands` (all files/dirs)
  - `ai_docs` → `ai_docs` (*.md files)
- Define constants for validation:
  - Required repository directories: `["agents", "hooks", "commands", "scripts"]`
  - Environment sample file: `.env.hooks.example`

### Step 4: Implement utility functions
- **Path resolution**: Function to expand ~ and resolve to absolute paths
- **Repository validation**: Function to verify script is run from cape repository root by checking for required directories
- **Source validation**: Function to verify source paths exist before creating symlinks
- **Parent directory creation**: Function to create parent directories for target symlinks

### Step 5: Implement symlink creation logic
- **Single symlink creation**: Function to create one symlink with error handling:
  - Check if source exists
  - Create parent directory if needed
  - Handle existing target (skip if regular file/directory, replace if symlink)
  - Create the symlink
  - Return success/failure status
- **File discovery**: Function to find files matching patterns in source directories:
  - Support glob patterns (*.md, *)
  - Support recursive vs single-level discovery
  - Return list of relative paths
- **Batch processing**: Function to collect all symlink operations before execution
- **Progress tracking**: Count total operations and successful operations

### Step 6: Implement environment file handling
- Function to detect if hooks were created during symlink operations
- Function to prompt user (or auto-proceed in force mode) for copying `.env.hooks.example`
- Function to copy the environment sample file to target directory
- Display informational message about configuring API keys

### Step 7: Implement CLI interface with Click
- Define main CLI command with:
  - Required `target_dir` argument with path validation
  - `--force` / `-f` flag to skip confirmations
  - Help text matching PowerShell version functionality
- Add parameter validation:
  - Ensure target_dir is provided
  - Expand and resolve target_dir to absolute path
  - Validate target directory parent exists and is writable

### Step 8: Implement main execution flow
- Get repository root (parent of scripts directory)
- Validate repository structure
- Display repository and target paths
- Collect all symlink operations from configuration
- Execute symlink creation for each mapping
- Track which operations succeeded/failed
- Display summary with colored output
- Handle environment file if hooks were created

### Step 9: Add colored output and user feedback
- Use `rich` library for colored console output:
  - Green for success messages
  - Yellow for warnings
  - Red for errors
  - Cyan for informational notes
- Display progress during operations
- Show clear summary at the end with operation counts

### Step 10: Make script executable and test
- Add shebang line at the top of the file
- Make the script executable on Unix-like systems with `chmod +x scripts/create-symlinks.py` (skip on Windows)
- Manually test the script with various scenarios:
  - Run with help flag: `uv run scripts/create-symlinks.py --help`
  - Run with test target directory: `uv run scripts/create-symlinks.py /tmp/test-target`
  - Run with force mode: `uv run scripts/create-symlinks.py /tmp/test-target --force`
  - Verify symlinks are created correctly
  - Verify environment file copying works

### Step 11: Validation
- Run all validation commands to ensure the script works correctly across scenarios
- Verify zero regressions and correct functionality

## Validation Commands
Execute every command to validate the chore is complete with zero regressions.

- `uv run scripts/create-symlinks.py --help` - Verify help text displays correctly
- `uv run scripts/create-symlinks.py /tmp/cape-test-target --force` - Test script execution with force mode in a temporary directory
- `ls -la /tmp/cape-test-target/.claude/agents` - Verify agent symlinks were created
- `ls -la /tmp/cape-test-target/.claude/hooks` - Verify hooks symlinks were created
- `ls -la /tmp/cape-test-target/.claude/commands` - Verify commands symlinks were created
- `ls -la /tmp/cape-test-target/ai_docs` - Verify AI docs symlinks were created
- `test -f /tmp/cape-test-target/.env.hooks.example && echo "Environment file copied"` - Verify environment file was copied
- `rm -rf /tmp/cape-test-target` - Cleanup test directory

## Notes
- The Python script should be cross-platform compatible, working on Windows, macOS, and Linux
- Use `pathlib.Path` for all path operations to ensure cross-platform compatibility
- On Windows, creating symlinks may require administrator privileges (same as PowerShell version)
- The `rich` library provides excellent cross-platform colored output without platform-specific ANSI codes
- `click` library provides robust CLI argument parsing with automatic help generation
- The UV script format with inline metadata ensures dependencies are automatically managed
- The shebang `#!/usr/bin/env -S uv run --script` makes the script directly executable on Unix-like systems
- Consider that the PowerShell version uses elevated permissions batch mode - the Python version should handle permissions gracefully with clear error messages
