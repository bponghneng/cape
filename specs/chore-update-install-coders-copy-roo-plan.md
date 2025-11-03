# Chore: Update Install Coders to Copy Roo Files

## Overview

Update the `create-symlinks.py` script (formerly referenced as `install-coders.py`) to copy Roo command files instead of creating symlinks for them. This change addresses Windows symlink limitations and provides better portability for Roo commands.

## Background

Currently, the `create-symlinks.py` script creates symbolic links for all command directories including Roo commands (`commands/roo -> .roo/commands`). On Windows, this requires administrator privileges and Developer Mode. Additionally, symlinks can break if the repository is moved, making the setup less robust.

## Requirements

1. **Modify Roo Command Processing**: Change the Roo commands mapping from symlink creation to file copying
2. **Preserve Directory Structure**: Maintain the same directory structure when copying files
3. **Handle Overwrites**: Implement safe overwrite behavior for existing files
4. **Maintain Compatibility**: Keep existing symlink behavior for all other directories
5. **Update Documentation**: Reflect the change in script documentation and help text

## Implementation Plan

### 1. Add Copy Operation Support

Create new functions to handle file copying operations alongside existing symlink operations:

- Add `CopyOperation` dataclass similar to `SymlinkOperation`
- Add `create_copy()` function similar to `create_symlink()`
- Add `execute_copy_direct()` function for immediate copy execution
- Add `execute_copy_batch_elevated()` function for Windows batch copying

### 2. Modify Configuration

Update the `SYMLINK_CONFIG` to distinguish between symlink and copy operations:

```python
@dataclass
class FileMapping:
    source_dir: str
    target_base: str
    pattern: str
    label: str
    recursive: bool = False
    use_copy: bool = False  # New field to determine copy vs symlink
```

Update the Roo commands configuration:
```python
FileMapping("commands/roo", ".roo/commands", "*", "Commands", recursive=True, use_copy=True)
```

### 3. Update Processing Logic

Modify `process_mapping()` to handle both copy and symlink operations:

- Check the `use_copy` flag to determine operation type
- Route to appropriate creation function (`create_copy()` vs `create_symlink()`)
- Collect operations for batch execution accordingly
- Update result handling and display

### 4. Implement Copy Functions

Create copy-specific functions:

- `create_copy()`: Handle individual file copy with overwrite logic
- `execute_copy_direct()`: Direct copy execution for non-Windows
- `execute_copy_batch_elevated()`: Batch copy execution for Windows elevation
- Use `shutil.copy2()` to preserve metadata (timestamps, permissions)

### 5. Update Main Execution Flow

Modify the main function to handle mixed operation types:

- Separate symlink and copy operations
- Execute copy operations first (no elevation needed)
- Execute symlink operations with elevation if required
- Update summary statistics to reflect both operation types

### 6. Update Documentation

Update script documentation and help text:

- Modify docstring to reflect mixed symlink/copy behavior
- Update help text to explain Roo commands are copied
- Add examples showing the new behavior
- Update error messages to be operation-type specific

## Technical Details

### Copy Operation Implementation

```python
@dataclass
class CopyOperation:
    source_path: Path
    target_path: Path
    description: str

def create_copy(
    repo_root: Path,
    target_dir: Path,
    source_rel: str,
    target_rel: str,
    description: str,
    collect_for_batch: bool = False,
) -> CopyOperation | OperationResult:
    """Create a file copy or collect it for batch execution."""
    source_path = repo_root / source_rel
    target_path = target_dir / target_rel
    
    # Verify source exists
    if not source_path.exists():
        return OperationResult(False, f"Source missing: {source_path}")
    
    # If collecting for batch, return operation
    if collect_for_batch:
        return CopyOperation(
            source_path=source_path, target_path=target_path, description=description
        )
    
    # Execute immediately
    # Create parent directory
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Handle existing target
    if target_path.exists() or target_path.is_symlink():
        if target_path.is_symlink():
            # Remove symlink and replace with copy
            target_path.unlink()
        elif target_path.is_dir():
            return OperationResult(False, f"Target directory exists, skipping: {target_path}")
        # File exists - will be overwritten by copy2
    
    # Perform copy
    try:
        shutil.copy2(source_path, target_path)
        return OperationResult(True, description)
    except (OSError, shutil.Error) as e:
        return OperationResult(False, f"{description} failed: {e}")
```

### Configuration Changes

```python
@dataclass
class FileMapping:
    source_dir: str
    target_base: str
    pattern: str
    label: str
    recursive: bool = False
    use_copy: bool = False

FILE_CONFIG = [
    FileMapping(
        "agents/claude-code", ".claude/agents", "*.md", "Agents", recursive=False
    ),
    FileMapping(
        "agents/opencode", ".opencode/agent", "*.md", "Agents", recursive=False
    ),
    FileMapping("hooks/claude-code", ".claude/hooks", "*", "Hooks", recursive=True),
    FileMapping(
        "commands/claude-code", ".claude/commands", "*", "Commands", recursive=True
    ),
    FileMapping("commands/roo", ".roo/commands", "*", "Commands", recursive=True, use_copy=True),  # Changed to copy
    FileMapping(
        "commands/opencode", ".opencode/command", "*.md", "Commands", recursive=True
    ),
    FileMapping(
        "commands/codex", ".codex/prompts", "*.md", "Prompts", recursive=True
    ),
    FileMapping(
        "commands/gemini", ".gemini/commands", "*", "Commands", recursive=True
    ),
]
```

### Benefits of This Approach

1. **Windows Compatibility**: Removes administrator requirement for Roo commands
2. **Portability**: Copied files work even if repository is moved
3. **Robustness**: No broken symlinks for Roo commands
4. **Backward Compatibility**: All other directories maintain symlink behavior
5. **Performance**: Copy operations don't require elevation on Windows
6. **Metadata Preservation**: Uses `shutil.copy2()` to maintain file timestamps

### Testing Strategy

1. **Unit Tests**: Test new copy functions with various scenarios
2. **Integration Tests**: Test full script execution with mixed operations
3. **Platform Tests**: Verify behavior on Windows, macOS, and Linux
4. **Edge Cases**: Test existing file handling, permission issues, broken symlinks

### Migration Considerations

- Existing installations with Roo symlinks will be replaced with copies on next run
- No manual intervention required - script handles replacement automatically
- Users won't notice functional difference in Roo command behavior

## Files to Modify

1. `cape/scripts/create-symlinks.py` - Main script implementation
2. Documentation files referencing symlink behavior (if any)

## Success Criteria

1. ✅ Roo commands are copied instead of symlinked
2. ✅ Directory structure is preserved
3. ✅ Existing files are handled safely
4. ✅ Other directories maintain symlink behavior
5. ✅ Script works without administrator privileges for Roo commands
6. ✅ Documentation is updated
7. ✅ Tests pass on all platforms

## Implementation Timeline

1. **Phase 1**: Add copy operation support functions
2. **Phase 2**: Update configuration and processing logic
3. **Phase 3**: Modify main execution flow
4. **Phase 4**: Update documentation and help text
5. **Phase 5**: Test and validate

---

**Created**: 2025-11-02  
**Status**: Planning Complete  
**Next Step**: Implementation