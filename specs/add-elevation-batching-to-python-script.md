# Chore: Add Administrator Elevation and Batch Symlink Creation to Python Script

## Chore Description
The PowerShell script [scripts/create-symlinks.ps1](scripts/create-symlinks.ps1:44-97) implements an intelligent elevation mechanism that:

1. **Collects all symlink operations first** without executing them
2. **Batches them into a single elevation request** via `Invoke-ElevatedBatch` function
3. **Prompts user once** to approve elevation (or auto-approves in force mode)
4. **Executes all operations** in the elevated context with a temporary script
5. **Returns results** to show success/failure for each operation

The current Python implementation [scripts/create-symlinks.py](scripts/create-symlinks.py:134-173) creates symlinks immediately as it discovers them, which means:
- Each symlink requires separate elevation on Windows
- No batching occurs
- Less efficient and more intrusive to user

This chore upgrades the Python script to match the PowerShell behavior by implementing:
- Operation collection phase (batch planning)
- Single elevation request with user confirmation
- Batch execution in elevated context
- Result reporting

## Relevant Files
Use these files to resolve the chore:

- **scripts/create-symlinks.ps1** (lines 44-97, 118-167) - PowerShell reference implementation
  - `Invoke-ElevatedBatch` function shows how to elevate once and run batched commands
  - `Add-SymlinkToBatch` function shows how to collect operations before execution
  - Temporary script generation and elevated execution pattern
  - Result tracking and reporting

- **scripts/create-symlinks.py** (lines 1-311) - Current Python implementation to upgrade
  - Lines 134-173: `create_symlink` function needs to be split into collect/execute phases
  - Lines 176-216: `process_mapping` function needs to collect operations instead of executing
  - Lines 246-310: `main` function needs batch execution logic
  - Needs Windows elevation detection and batch execution mechanism

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Add Windows platform detection and elevation utilities
- Import `platform` and `subprocess` modules for OS detection and process execution
- Add function to detect if running on Windows: `is_windows() -> bool`
- Add function to check if already running elevated on Windows (check admin privileges)
- Add function to detect if elevation is needed based on platform

### Step 2: Create operation batching data structures
- Create a `SymlinkOperation` dataclass to represent a single symlink operation:
  - `source_path: Path` - Full source path in repository
  - `target_path: Path` - Full target path where symlink will be created
  - `description: str` - Human-readable description for user feedback
- Modify `create_symlink` function to return `SymlinkOperation | OperationResult`:
  - If operation should be collected (Windows, not elevated), return `SymlinkOperation`
  - If operation can be executed immediately (non-Windows or already elevated), execute and return `OperationResult`

### Step 3: Implement batch execution for Windows elevation
- Create `execute_symlink_batch_elevated(operations: list[SymlinkOperation], force: bool) -> list[OperationResult]`:
  - Generate Python script that creates all symlinks with try/except for each
  - Script should print success/failure for each operation in parseable format
  - Save script to temporary file
  - Prompt user for elevation approval (unless force mode)
  - Use `subprocess` to execute script with elevation:
    - On Windows: Use `powershell -Command "Start-Process python -ArgumentList '<script>' -Verb RunAs -Wait"`
    - Or use `ctypes` to call `ShellExecuteW` with "runas" verb
  - Parse output to determine success/failure for each operation
  - Return list of `OperationResult` objects
  - Clean up temporary script file

### Step 4: Implement direct execution for non-Windows platforms
- Create `execute_symlink_direct(operation: SymlinkOperation) -> OperationResult`:
  - Execute the symlink creation immediately (for Linux/macOS)
  - Handle errors and return appropriate `OperationResult`
  - This path is used when elevation is not needed

### Step 5: Update process_mapping to use batch collection
- Modify `process_mapping` to collect operations instead of executing immediately:
  - Change to collect `SymlinkOperation` objects when on Windows and not elevated
  - Execute immediately when on non-Windows or already elevated
  - Return `tuple[list[SymlinkOperation], list[OperationResult]]`
- Update to track both pending operations and completed results

### Step 6: Update main execution flow for batch processing
- Modify `main` function to:
  - Detect if running on Windows and if elevation will be needed
  - Collect all operations first (batch phase)
  - If on Windows with pending operations:
    - Show summary of operations to be performed
    - Execute batch elevation with all collected operations
    - Combine results with any direct execution results
  - If not on Windows or already elevated:
    - Operations are already executed, just show results
  - Display final summary with all results

### Step 7: Add user confirmation for elevation
- Implement confirmation prompt before elevation (unless force mode):
  - Show number of symlink operations to be performed
  - Ask "Proceed with elevation to create N symlinks? (y/N)"
  - If declined, show message and exit gracefully
  - If force mode, skip confirmation and proceed

### Step 8: Improve error handling and user feedback
- Add clear messages for elevation process:
  - "Collecting symlink operations..." during batch phase
  - "Requesting elevation to create N symlinks..." before elevation
  - "Executing symlinks with elevated privileges..." during execution
  - Clear error messages if elevation fails or is denied
- Ensure all existing colored output is preserved

### Step 9: Test the implementation
- Test on Windows with administrator privileges (should execute directly)
- Test on Windows without administrator privileges (should elevate and batch)
- Test with --force flag (should skip elevation confirmation)
- Test with non-Windows platforms (should execute directly without elevation)
- Verify all symlinks are created successfully in batch mode
- Verify error handling when elevation is denied

### Step 10: Run validation commands
- Execute all validation commands to ensure functionality works correctly

## Validation Commands
Execute every command to validate the chore is complete with zero regressions.

- `uv run scripts/create-symlinks.py --help` - Verify help still works correctly
- `mkdir C:\temp\cape-batch-test && uv run scripts/create-symlinks.py C:\temp\cape-batch-test --force` - Test batch execution with force mode on Windows
- `ls C:\temp\cape-batch-test\.claude\agents` - Verify agent symlinks were created
- `ls C:\temp\cape-batch-test\.claude\hooks` - Verify hooks symlinks were created
- `ls C:\temp\cape-batch-test\.claude\commands` - Verify commands symlinks were created
- `test -f C:\temp\cape-batch-test\.env.hooks.example && echo "Environment file copied"` - Verify env file copied
- `rm -r C:\temp\cape-batch-test` - Cleanup test directory

## Notes
- The PowerShell implementation uses `Start-Process -Verb RunAs` to elevate - Python equivalent is `ctypes.windll.shell32.ShellExecuteW` with "runas" verb or using `powershell` as a wrapper
- The temporary script approach allows batching all operations into a single elevation request, which is much better UX than elevating for each symlink
- On Linux/macOS, symlinks don't require elevation (unless target directory has permission issues), so direct execution is appropriate
- The batching mechanism should be transparent - from user perspective, they approve elevation once and all symlinks are created
- Consider using `json` to communicate results from elevated script back to main process for reliable parsing
- The `ctypes` approach for Windows elevation:
  ```python
  import ctypes
  ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, script_path, None, 1)
  ```
- Alternative subprocess approach:
  ```python
  subprocess.run(["powershell", "-Command", f"Start-Process -FilePath '{sys.executable}' -ArgumentList '{script_path}' -Verb RunAs -Wait"], check=True)
  ```
