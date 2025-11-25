# Chore Plan: Extend Streaming Comments to Review and Acceptance Steps

## Task Context (Required)

- Scope: small-change
- Goal:
  - Enable streaming JSON comments for the address-review-issues workflow step
  - Enable streaming JSON comments for the plan-acceptance workflow step
- Constraints: Must follow the existing streaming pattern established for classify and plan steps

## Description (Required)

- The workflow already implements streaming JSON comments for classify and plan steps using `make_progress_comment_handler()`, which inserts real-time progress updates into the database as `CapeComment` records
- Two additional workflow steps need this same streaming capability: address-review-issues and plan-acceptance
- Both steps currently call `execute_template()` without passing a `stream_handler`, so no streaming occurs
- The underlying infrastructure (`execute_template()`, `execute_claude_template()`) already supports streaming via an optional `stream_handler` parameter
- Out of scope: Changes to the streaming infrastructure itself or to the implement step (which already has internal streaming support)

## Relevant Files (Required)

- `cape/app/src/cape/core/workflow/review.py` - Contains `notify_review_template()` which calls `execute_template()` at line 128 without streaming
- `cape/app/src/cape/core/workflow/acceptance.py` - Contains `notify_plan_acceptance()` which calls `execute_template()` at line 51 without streaming
- `cape/app/src/cape/core/workflow/runner.py` - Orchestrates the workflow and already creates handlers for classify (line 75) and plan (line 112) steps; needs to create handlers for review (line 190) and acceptance (line 200) steps
- `cape/app/src/cape/core/agent.py` - Contains `execute_template()` which already accepts and passes through `stream_handler` parameter
- `cape/app/src/cape/core/agents/claude/claude.py` - Contains `execute_claude_template()` which already accepts and uses `stream_handler` parameter
- `cape/app/src/cape/core/notifications.py` - Contains `make_progress_comment_handler()` used to create streaming handlers

#### New Files (Optional)

None - all changes are modifications to existing files.

## Implementation Plan (Required)

1. **Update `notify_review_template()` in `review.py`**
   - Add `stream_handler: Optional[Callable[[str], None]] = None` parameter to function signature at line 93
   - Add import for `Callable` and `Optional` from `typing` module at the top of the file
   - Pass `stream_handler` to `execute_template()` call at line 128

2. **Update `notify_plan_acceptance()` in `acceptance.py`**
   - Add `stream_handler: Optional[Callable[[str], None]] = None` parameter to function signature at line 13
   - Add import for `Callable` and `Optional` from `typing` module at the top of the file
   - Pass `stream_handler` to `execute_template()` call at line 51

3. **Update `execute_workflow()` in `runner.py`**
   - For the address-review-issues step (around line 188-190):
     - Create a handler using `make_progress_comment_handler(issue_id, adw_id, logger)` before the function call
     - Pass `stream_handler=review_handler` to `notify_review_template()`
   - For the plan-acceptance step (around line 198-200):
     - Create a handler using `make_progress_comment_handler(issue_id, adw_id, logger)` before the function call
     - Pass `stream_handler=acceptance_handler` to `notify_plan_acceptance()`

## Validation (Required)

Run the existing test suite to ensure no regressions:

```bash
cd cape/app
uv run pytest -q
```

This validates that:
- All existing tests pass
- Type checking passes (if pytest includes type checking)
- The new optional parameters are backward compatible

To manually verify streaming functionality works:
1. Run a workflow that includes the review step with logging enabled
2. Check the database for `CapeComment` records with `type="claude"` and `source="agent"` during the address-review-issues step
3. Check the database for similar records during the plan-acceptance step
4. Verify that comments appear incrementally during execution, not just at the end

## Notes / Future Considerations (Optional)

- The `make_progress_comment_handler()` function abstracts the streaming comment logic, making it easy to add streaming to new workflow steps
- If additional workflow steps are added in the future, they should follow this same pattern
- The streaming infrastructure is provider-agnostic (works with both Claude and potentially other agent providers)
- Consider adding integration tests specifically for streaming behavior if they don't already exist
