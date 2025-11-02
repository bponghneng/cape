# CAPE ADW

CAPE ADW (Agent Development Workflow) is a specialized CLI tool for managing agent development workflows.

## Installation

```bash
uv sync
```

## Usage

```bash
# Execute ADW workflow for an issue
cape-adw <issue_id> <description>

# Show help
cape-adw --help
```

## Development

Run tests:

```bash
python -m pytest tests/ -v
```
