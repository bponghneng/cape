# Plan: Add Streaming JSON Comments to All Workflow Steps (Except Review)

## Overview

Currently, only the **implement** step uses `make_progress_comment_handler` to stream JSON output as comments. This plan extends streaming to all other agent execution steps except review.

## Current State

- **Implement step**: Uses `execute_implement_plan()` which calls `make_progress_comment_handler()` and passes it to `agent.execute_prompt(request, stream_handler=handler)`
- **Classify step**: Uses `execute_template()` without streaming support
- **Plan step**: Uses `execute_template()` without streaming support
- **Review step**: Uses `execute_template()` - will NOT be changed (as requested)

## Changes Required

### 1. Update `execute_claude_template()` in `cape/app/src/cape/core/agents/claude/claude.py`

Add `stream_handler` parameter to support streaming:

```python
def execute_claude_template(
    request: ClaudeAgentTemplateRequest,
    *,
    stream_handler: Optional[Callable[[str], None]] = None
) -> ClaudeAgentPromptResponse:
    """Execute a Claude Code template with slash command and arguments."""
    # ... existing code ...

    # Execute using ClaudeAgent - now with stream_handler
    agent = ClaudeAgent()
    response = agent.execute_prompt(agent_request, stream_handler=stream_handler)

    # ... rest of function ...
```

### 2. Update `execute_template()` in `cape/app/src/cape/core/agent.py`

Add `stream_handler` parameter to the facade function:

```python
def execute_template(
    request: ClaudeAgentTemplateRequest,
    *,
    stream_handler: Optional[Callable[[str], None]] = None
) -> ClaudeAgentPromptResponse:
    """Execute a Claude Code template with slash command and arguments."""
    return execute_claude_template(request, stream_handler=stream_handler)
```

### 3. Update `classify_issue()` in `cape/app/src/cape/core/workflow/classify.py`

Add `stream_handler` parameter and pass through to `execute_template()`:

```python
def classify_issue(
    issue: CapeIssue, adw_id: str, logger: Logger,
    stream_handler: Optional[Callable[[str], None]] = None
) -> Tuple[Optional[SlashCommand], Optional[Dict[str, str]], Optional[str]]:
    """Classify issue and return appropriate slash command."""
    # ... existing setup ...

    response = execute_template(request, stream_handler=stream_handler)

    # ... rest of function ...
```

### 4. Update `build_plan()` in `cape/app/src/cape/core/workflow/plan.py`

Add `stream_handler` parameter and pass through to `execute_template()`:

```python
def build_plan(
    issue: CapeIssue, command: SlashCommand, adw_id: str, logger: Logger,
    stream_handler: Optional[Callable[[str], None]] = None
) -> ClaudeAgentPromptResponse:
    """Build implementation plan for the issue using the specified command."""
    # ... existing setup ...

    response = execute_template(request, stream_handler=stream_handler)

    # ... rest of function ...
```

### 5. Update `runner.py` to create and pass stream handlers

In the workflow runner, create handlers for classify and plan steps:

```python
# For classify step
classify_handler = make_progress_comment_handler(issue.id, adw_id, logger)
command, classification, error = classify_issue(issue, adw_id, logger, stream_handler=classify_handler)

# For plan step
plan_handler = make_progress_comment_handler(issue.id, adw_id, logger)
response = build_plan(issue, command, adw_id, logger, stream_handler=plan_handler)

# Review step - NO handler (as requested)
notify_review_template(review_file, issue.id, adw_id, logger)
```

## Files to Modify

1. `cape/app/src/cape/core/agents/claude/claude.py` - Add `stream_handler` to `execute_claude_template()`
2. `cape/app/src/cape/core/agent.py` - Add `stream_handler` to `execute_template()` facade
3. `cape/app/src/cape/core/workflow/classify.py` - Add `stream_handler` to `classify_issue()`
4. `cape/app/src/cape/core/workflow/plan.py` - Add `stream_handler` to `build_plan()`
5. `cape/app/src/cape/core/workflow/runner.py` - Create and pass handlers for classify/plan steps

## Testing

- Run workflow with debug logging to verify streaming comments are inserted for classify and plan steps
- Verify review step does NOT have streaming comments
- Check database for inserted `CapeComment` records with `type="claude"` and `source="agent"`
