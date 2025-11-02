# Feature: Cape Worker Reorganization Plan

## Description

This plan outlines the reorganization of all Python worker feature files from their current scattered locations into a single, well-structured `cape/cape-worker/` directory. The reorganization will create a proper Python package structure with clear separation of concerns and improved maintainability.

## Current File Organization Issues

The current implementation spreads worker-related files across multiple directories:

- Main script at root level (`cape/worker.py`)
- Tests in general test directory (`cape/tests/`)
- Migration in shared migrations (`cape/migrations/`)
- Installation scripts in shared scripts (`cape/scripts/`)
- Daemon configs in shared daemons (`cape/daemons/`)

This scattered organization makes it difficult to:

- Locate all worker-related code
- Maintain and update the worker feature
- Understand the complete scope of the worker functionality
- Test the worker in isolation

## Proposed New Directory Structure

```
cape/cape-worker/
├── __init__.py                 # Package initialization with exports
├── __main__.py                 # Module entry point
├── worker.py                   # Core worker implementation
├── cli.py                      # Command-line interface (extracted)
├── database.py                 # Database operations (extracted)
├── config.py                   # Configuration management (new)
├── tests/
│   ├── __init__.py
│   ├── test_worker.py          # Main worker tests
│   ├── test_database.py        # Database-specific tests
│   └── test_config.py          # Configuration tests
├── migrations/
│   └── 003_add_worker_assignment.sql  # Database migration
├── scripts/
│   └── install-worker.sh       # Installation script
├── daemons/
│   ├── cape-worker.service     # Linux systemd config
│   └── com.cape.worker.plist   # macOS launchd config
├── logs/                       # Log files directory
└── README.md                   # Worker documentation
```

## File Mappings

| Current Location                                | New Location                                                | Notes                      |
| ----------------------------------------------- | ----------------------------------------------------------- | -------------------------- |
| `cape/worker.py`                                | `cape/cape-worker/worker.py`                                | Main worker implementation |
| `cape/tests/test_worker.py`                     | `cape/cape-worker/tests/test_worker.py`                     | Unit tests                 |
| `cape/migrations/003_add_worker_assignment.sql` | `cape/cape-worker/migrations/003_add_worker_assignment.sql` | Database migration         |
| `cape/scripts/install-worker.sh`                | `cape/cape-worker/scripts/install-worker.sh`                | Installation script        |
| `cape/daemons/cape-worker.service`              | `cape/cape-worker/daemons/cape-worker.service`              | Linux systemd config       |
| `cape/daemons/com.cape.worker.plist`            | `cape/cape-worker/daemons/com.cape.worker.plist`            | macOS launchd config       |

## Code Refactoring Strategy

### 1. Extract CLI Interface

Move argument parsing and main() function to `cli.py`:

- Extract `argparse` setup
- Extract `main()` function
- Keep command-line interface logic separate from core worker logic

### 2. Extract Database Operations

Move database-related methods to `database.py`:

- Extract `get_next_issue()` method
- Extract `update_issue_status()` method
- Centralize all database interaction logic

### 3. Create Configuration Module

Create `config.py` for configuration management:

- Centralize configuration constants
- Handle environment variable loading
- Provide configuration validation

### 4. Simplify Main Worker

Keep core worker logic in `worker.py`:

- Main `IssueWorker` class
- Core polling and execution logic
- Import from other modules

## Path Updates Required

### Installation Script (`cape/cape-worker/scripts/install-worker.sh`)

**Updated Path References:**

- Line 21: `WORKER_SCRIPT="${CAPE_ROOT}/cape-worker/worker.py"`
- Line 116: `local PLIST_TEMPLATE="${CAPE_ROOT}/cape-worker/daemons/com.cape.worker.plist"`
- Line 171: `local SERVICE_TEMPLATE="${CAPE_ROOT}/cape-worker/daemons/cape-worker.service"`

### Linux Systemd Service (`cape/cape-worker/daemons/cape-worker.service`)

**Updated Path References:**

- Line 10: `WorkingDirectory=CAPE_ROOT_PATH/cape-worker`
- Line 32: `StandardOutput=append:CAPE_ROOT_PATH/cape-worker/logs/worker_WORKER_ID_stdout.log`
- Line 33: `StandardError=append:CAPE_ROOT_PATH/cape-worker/logs/worker_WORKER_ID_stderr.log`

### macOS Launchd Plist (`cape/cape-worker/daemons/com.cape.worker.plist`)

**Updated Path References:**

- Line 24: `<string>CAPE_ROOT_PATH/cape-worker</string>`
- Line 46: `<string>CAPE_ROOT_PATH/cape-worker/logs/worker_WORKER_ID_stdout.log</string>`
- Line 49: `<string>CAPE_ROOT_PATH/cape-worker/logs/worker_WORKER_ID_stderr.log</string>`

### Worker Script (`cape/cape-worker/worker.py`)

**Updated Path References:**

- Line 28: `sys.path.insert(0, str(Path(__file__).parent.parent / "cape-cli" / "src"))`

## Import Changes

### Main Worker Script (`cape/cape-worker/worker.py`)

**Current Imports:**

```python
from cape_cli.database import get_client
```

**New Imports:**

```python
from .database import get_client
from .config import WorkerConfig
```

### New Database Module (`cape/cape-worker/database.py`)

**Required Imports:**

```python
import sys
from pathlib import Path
from typing import Optional, Tuple

# Add cape-cli to path for database imports
sys.path.insert(0, str(Path(__file__).parent.parent / "cape-cli" / "src"))

from cape_cli.database import get_client as _get_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
```

### New CLI Module (`cape/cape-worker/cli.py`)

**Required Imports:**

```python
import argparse
from .worker import IssueWorker
from .config import WorkerConfig
```

### Test Files (`cape/cape-worker/tests/test_*.py`)

**Current Import:**

```python
from worker import IssueWorker
```

**New Imports:**

```python
from ..worker import IssueWorker
from ..database import get_client
from ..config import WorkerConfig
```

### Package Initialization (`cape/cape-worker/__init__.py`)

**Required Exports:**

```python
from .worker import IssueWorker
from .database import get_client
from .config import WorkerConfig
from .cli import main

__all__ = ['IssueWorker', 'get_client', 'WorkerConfig', 'main']
```

### Entry Point Script (`cape/cape-worker/__main__.py`)

**New File for Package Execution:**

```python
from .cli import main

if __name__ == "__main__":
    main()
```

This will allow the worker to be run as a module: `python -m cape-worker --worker-id alleycat-1`

## Implementation Steps

### Phase 1: Create New Directory Structure

1. **Create the cape-worker package directory:**

   ```bash
   mkdir -p cape/cape-worker/{tests,migrations,scripts,daemons,logs}
   ```

2. **Create package initialization files:**
   - Create `cape/cape-worker/__init__.py`
   - Create `cape/cape-worker/tests/__init__.py`
   - Create `cape/cape-worker/__main__.py`

### Phase 2: Extract and Refactor Code

3. **Create the new configuration module:**

   - Create `cape/cape-worker/config.py` with configuration management
   - Extract configuration logic from the main worker script

4. **Create the database module:**

   - Create `cape/cape-worker/database.py` with database operations
   - Move `get_next_issue()` and `update_issue_status()` methods here
   - Update imports and path references

5. **Create the CLI module:**

   - Create `cape/cape-worker/cli.py` with argument parsing and main() function
   - Extract CLI logic from the main worker script

6. **Refactor the main worker script:**
   - Update `cape/cape-worker/worker.py` to use the new modules
   - Remove extracted code and update imports
   - Fix path references for cape-cli import

### Phase 3: Move Existing Files

7. **Move the test file:**

   - Move `cape/tests/test_worker.py` → `cape/cape-worker/tests/test_worker.py`
   - Update imports in the test file

8. **Move the migration file:**

   - Move `cape/migrations/003_add_worker_assignment.sql` → `cape/cape-worker/migrations/003_add_worker_assignment.sql`

9. **Move the installation script:**

   - Move `cape/scripts/install-worker.sh` → `cape/cape-worker/scripts/install-worker.sh`
   - Update path references in the script

10. **Move the daemon configuration files:**
    - Move `cape/daemons/cape-worker.service` → `cape/cape-worker/daemons/cape-worker.service`
    - Move `cape/daemons/com.cape.worker.plist` → `cape/cape-worker/daemons/com.cape.worker.plist`
    - Update path references in both files

### Phase 4: Create Additional Files

11. **Create additional test files:**

    - Create `cape/cape-worker/tests/test_database.py` for database-specific tests
    - Create `cape/cape-worker/tests/test_config.py` for configuration tests

12. **Create documentation:**
    - Create `cape/cape-worker/README.md` with worker-specific documentation

### Phase 5: Update References and Integration

13. **Update project documentation:**

    - Update `cape/README.md` to reference the new worker location
    - Update `cape/WORKER_README.md` if it exists

14. **Update any other references:**
    - Search for references to the old worker.py location in other files
    - Update any scripts or documentation that reference the old paths

### Phase 6: Testing and Validation

15. **Test the reorganized code:**

    - Run the test suite: `cd cape && python -m pytest cape-worker/tests/ -v`
    - Test worker execution: `cd cape && python -m cape-worker --worker-id test-worker`
    - Test installation script: `cd cape && cape-worker/scripts/install-worker.sh test-worker`

16. **Validate daemon configurations:**
    - Verify the systemd and launchd configurations work with new paths
    - Test installation on target platforms if possible

### Phase 7: Cleanup

17. **Remove old files:**

    - Remove `cape/worker.py` (original file)
    - Remove `cape/tests/test_worker.py` (original file)
    - Remove `cape/migrations/003_add_worker_assignment.sql` (original file)
    - Remove `cape/scripts/install-worker.sh` (original file)
    - Remove `cape/daemons/cape-worker.service` (original file)
    - Remove `cape/daemons/com.cape.worker.plist` (original file)

18. **Final validation:**
    - Ensure all functionality works as expected
    - Verify no broken imports or references remain
    - Update any CI/CD pipelines or deployment scripts

## Benefits of This Reorganization

1. **Modularity**: Separates concerns into distinct modules (worker, database, config, CLI)
2. **Self-Contained**: All worker-related files in one directory
3. **Package Structure**: Proper Python package with `__init__.py` and module execution support
4. **Maintainability**: Easier to find and modify worker-specific code
5. **Testing**: Dedicated test directory with comprehensive test coverage
6. **Documentation**: Worker-specific README for focused documentation
7. **Consistency**: Matches the existing `cape-adw` package naming convention

## Validation Commands

```bash
# Run unit tests
cd cape && python -m pytest cape-worker/tests/ -v --cov=cape-worker

# Test worker manually
cd cape && python -m cape-worker --worker-id test-worker

# Test installation script
cd cape && cape-worker/scripts/install-worker.sh test-worker

# Test workflow execution
cd cape && uv run cape-adw 123 "test issue description"
```

## Notes

- The hyphenated directory name `cape-worker` matches the existing `cape-adw` package naming convention
- All path references in configuration files must be updated to reflect the new structure
- The worker can now be executed as a proper Python module using `python -m cape-worker`
- The reorganization maintains backward compatibility for all existing functionality
- Consider updating any CI/CD pipelines or deployment scripts that reference the old paths
