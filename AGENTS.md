# AGENTS.md

This file provides guidance to AI coding agents when working with code in this repository.

## Project Overview

CAPE (Coordinated Agent Planning & Execution) is a project that began as a concept for developing multi-agent workflows for complex codebases. It has since evolved into a collection of reusable assets for AI coder tools, providing components like agent definitions, command templates, and documentation patterns to enhance workflow flexibility.

## Workflow Style & Collaboration Rules

### Code Changes & Investigation Workflow

- **Research First**: Investigate thoroughly before proposing solutions. Use search
  tools and documentation to gather facts rather than making assumptions.
- **Discuss Before Implementing**: Present findings and proposed approaches for
  approval before making code changes. Explain options and trade-offs.
- **Respect Original Code**: Try to understand where code came from and what problem
  it's solving before assuming it can be changed.
- **Question Assumptions**: If something doesn't work as expected, investigate the
  root cause. Look for version differences, environment issues, or missing context.

### Problem-Solving Workflow

1. **Analyze**: Read errors carefully and identify the real issue
2. **Research**: Use tools and documentation to understand the problem context
3. **Propose**: Present findings and suggest solution options with pros/cons
4. **Implement**: Only after approval, make minimal necessary changes
5. **Clean Up**: Remove temporary test files or debugging code

### Communication

- Ask clarifying questions when requirements are unclear
- Explain the "why" behind recommendations
- If blocked or uncertain, ask for guidance rather than guessing

## Simplicity-First Mindset

Your guidance is directed by these core principles:

1. **Start with MVP**: Focus on core functionality that delivers immediate value
2. **Avoid Premature Optimization**: Don't add features "just in case"
3. **Minimal Dependencies**: Only add what's absolutely necessary for requirements
4. **Clear Over Clever**: Simple, maintainable solutions over complex architectures

Apply these principles when evaluating whether complex patterns, or advanced optimizations are truly needed or if simpler solutions would suffice.

## CLI Commands

**⚠️ IMPORTANT: Project Repository**: The CLI project repository is `cape_cli`. All of the development commands are run from the root of the project repository.

**Package Management**: This project uses `uv` for package management. To install or update dependencies, use the `uv sync` command.

**CLI**:
- `uv run cape` - Starts the Cape Terminal User Interface (TUI).

**Code Quality Tools**:

- `pytest`: `pytest test_cape_tui.py --cov=cape_tui --cov-report=term-missing`

**Testing**:
- `pytest`: Run tests with `pytest test_cape_tui.py -v`

**Setup**: `uv sync` - Install and sync project dependencies.

## Architecture

**Current Structure**:

- `cape_tui.py`: Single-file application (~600 lines)
- `Textual framework`: Modern TUI with reactive programming

**Key Dependencies**:

- `uv`: For package management.
- `Textual`: For the TUI framework.
- `Supabase`: For the backend database and authentication.

## Testing Strategy

This project uses `pytest` for testing with the `pytest-asyncio` plugin for async test support.

### Test Organization

- **Location**: Tests are located in `cape-cli/tests/`
- **Running tests**: `uv run pytest tests/ -v`
- **Checking test coverage**: `uv run pytest tests/ --cov=cape_cli --cov-report=term-missing`

### Textual Testing Best Practices

**Official Approach**: Textual provides dedicated testing features through the `app.run_test()` method and `Pilot` object.

#### Key Principles:

1. **Use `run_test()` for integration tests**:
   - Creates an async context manager that returns a `Pilot` object
   - Runs apps in "headless" mode (no terminal updates)
   - Properly initializes the app context and lifecycle
   ```python
   async def test_something():
       app = MyApp()
       async with app.run_test() as pilot:
           # Use pilot to interact with the app
           await pilot.click("#button-id")
           await pilot.press("enter")
           # Assert on app state
           assert app.screen.some_property == expected_value
   ```

2. **DO NOT mock the `app` property**:
   - The `app` property on Screen/Widget is managed internally by Textual
   - It's a read-only property that cannot be set directly
   - Attempting to mock it will cause `AttributeError: property 'app' of 'Screen' object has no setter`
   - Use `run_test()` instead to get proper app context

3. **Use `Pilot` for user interactions**:
   - `await pilot.click(selector)` - Simulate mouse clicks on widgets
   - `await pilot.press(*keys)` - Simulate key presses
   - `await pilot.pause()` - Wait for all pending messages to be processed
   - `await pilot.pause(delay=0.1)` - Insert a delay before waiting

4. **Test structure patterns**:
   
   **Simple unit tests** (no app context needed):
   - Testing data models and fixtures
   - Testing pure functions
   - Testing modal/widget initialization
   - Testing handler methods with mocked callbacks
   
   **Integration tests** (require app context):
   - Testing complete user flows
   - Testing state changes after user interactions
   - Testing screen navigation
   - Use `run_test()` and `Pilot` for these

5. **Async test configuration**:
   - All Textual integration tests must be async
   - Configure `pytest-asyncio` with `asyncio_mode = auto` in `pytest.ini` or `pyproject.toml`
   - Or use `@pytest.mark.asyncio` decorator on each async test

#### Example Test Patterns:

**Good - Unit test without app context:**
```python
def test_modal_initialization(mock_issue):
    """Test modal initializes with correct data."""
    modal = ConfirmDeleteModal(mock_issue.id, mock_issue.description)
    assert modal.issue_id == mock_issue.id
    assert modal.issue_description == mock_issue.description
```

**Good - Integration test with run_test:**
```python
@patch("cape_cli.database.delete_issue")
async def test_delete_flow(mock_delete):
    """Test the complete delete flow."""
    mock_delete.return_value = True
    app = MyApp()
    
    async with app.run_test() as pilot:
        # Simulate user clicking delete button
        await pilot.click("#delete-btn")
        await pilot.pause()  # Wait for confirmation modal
        
        # Confirm deletion
        await pilot.click("#confirm-btn")
        await pilot.pause()  # Wait for deletion to complete
        
        # Assert the issue was deleted
        mock_delete.assert_called_once_with(expected_id)
```

**Bad - Trying to mock the app property:**
```python
# DON'T DO THIS - will fail with AttributeError
def test_something():
    screen = MyScreen()
    screen.app = Mock()  # ❌ Error: property has no setter
```

#### Testing Guidelines for This Codebase:

- **Prefer behavioral tests** over structural tests (checking method existence)
- **Test actual user flows** rather than just checking that methods exist
- **Use fixtures** for creating test data (issues, comments, etc.)
- **Mock database calls** to avoid external dependencies
- **Use `await pilot.pause()`** when testing async operations to ensure messages are processed
- **Test both success and error paths** (e.g., successful deletion vs. validation errors)
- **Keep tests focused** - each test should verify one specific behavior

#### Common Pitfalls to Avoid:

- ❌ Setting `screen.app = Mock()` directly
- ❌ Not using `async`/`await` with `run_test()`
- ❌ Forgetting to call `await pilot.pause()` after triggering async operations
- ❌ Testing only that methods exist instead of testing actual behavior
- ❌ Not mocking database calls, causing tests to require live database
- ❌ Writing tests that depend on specific timing without using `pilot.pause()`

#### Future: Integration Testing with Dependency Injection

**Recommended Pattern for Future Integration Tests:**

Instead of mocking at the function level or dealing with `@work` timing issues, use dependency injection:

```python
# Production: Real database adapter that calls actual scripts
app = CapeApp(database=ProductionDatabaseAdapter())

# Testing: Mock adapter that returns immediately
app = CapeApp(database=MockDatabaseAdapter())
```

**Benefits:**
- No timing issues - mock adapters return instantly
- No `@work` decorator complications - threads complete immediately  
- No external dependencies - no real database or scripts
- Fast tests - everything synchronous in the mock layer
- Real behavior testing - TUI code runs normally with fake data

**Implementation approach:**
- TUI reads configuration on startup (test vs. production)
- Test config provides mock adapters that return canned data
- Production config provides real adapters that call database/scripts
- Integration tests use `run_test()` with mock adapters
- No special timing logic needed in tests

This pattern separates infrastructure concerns (database, scripts) from UI logic, making both easier to test and maintain.
