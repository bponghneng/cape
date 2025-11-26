# Plan: Extend Streaming Progress Comments to Address-Review-Issues and Plan-Acceptance Steps

## Overview

This plan extends the streaming JSON comments pattern (already implemented for classify and plan steps) to two additional workflow steps:
1. **Address Review Issues** (`notify_review_template` in `review.py`)
2. **Plan Acceptance** (`notify_plan_acceptance` in `acceptance.py`)

## Current State

| Step | Has Streaming | Location |
|------|---------------|----------|
| Classify | YES | `runner.py:75-77` |
| Plan | YES | `runner.py:112-113` |
| Implement | YES (internal) | `execute_implement_plan()` |
| Address-Review-Issues | NO | `runner.py:190` |
| Plan-Acceptance | NO | `runner.py:200` |

## Changes Required

### 1. Update `review.py` - Add stream_handler to `notify_review_template()`

**File:** `cape/app/src/cape/core/workflow/review.py`

Add `stream_handler` parameter and pass to `execute_template()`:

```python
from typing import Callable, Optional

def notify_review_template(
    review_file: str,
    issue_id: int,
    adw_id: str,
    logger: Logger,
    stream_handler: Optional[Callable[[str], None]] = None,
) -> bool:
    # ... existing validation ...

    response = execute_template(request, stream_handler=stream_handler)  # Line 128

    # ... rest unchanged ...
```

### 2. Update `acceptance.py` - Add stream_handler to `notify_plan_acceptance()`

**File:** `cape/app/src/cape/core/workflow/acceptance.py`

Add `stream_handler` parameter and pass to `execute_template()`:

```python
from typing import Callable, Optional

def notify_plan_acceptance(
    plan_path: str,
    issue_id: int,
    adw_id: str,
    logger: Logger,
    stream_handler: Optional[Callable[[str], None]] = None,
) -> bool:
    # ... existing validation ...

    response = execute_template(request, stream_handler=stream_handler)  # Line 51

    # ... rest unchanged ...
```

### 3. Update `runner.py` - Create and pass handlers for both steps

**File:** `cape/app/src/cape/core/workflow/runner.py`

Create handlers and pass them to both functions:

```python
# Lines 188-196: Address review issues step
logger.info("\n=== Notifying review template ===")
review_handler = make_progress_comment_handler(issue.id, adw_id, logger)
notify_success = notify_review_template(
    review_file, issue_id, adw_id, logger, stream_handler=review_handler
)

# Lines 198-206: Plan acceptance step
logger.info("\n=== Validating plan acceptance ===")
acceptance_handler = make_progress_comment_handler(issue.id, adw_id, logger)
acceptance_success = notify_plan_acceptance(
    implemented_plan_path, issue_id, adw_id, logger, stream_handler=acceptance_handler
)
```

## Files to Modify

1. `cape/app/src/cape/core/workflow/review.py` - Add `stream_handler` parameter to `notify_review_template()`
2. `cape/app/src/cape/core/workflow/acceptance.py` - Add `stream_handler` parameter to `notify_plan_acceptance()`
3. `cape/app/src/cape/core/workflow/runner.py` - Create and pass handlers for both steps

## Dependencies

The following are already in place from the previous implementation:
- `execute_template()` in `agent.py` already accepts `stream_handler` parameter
- `make_progress_comment_handler()` is already imported in `runner.py`
- `execute_claude_template()` in `claude.py` already accepts `stream_handler` parameter

## Testing

- Verify streaming comments are inserted for address-review-issues step
- Verify streaming comments are inserted for plan-acceptance step
- Check database for inserted `CapeComment` records with `type="claude"` and `source="agent"`
