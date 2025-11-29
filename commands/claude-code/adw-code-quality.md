---
description: Run code quality tools and fix reported errors and warnings
allowed-tools: Bash, Read, Edit, TodoWrite
thinking: true
---

# ADW Code Quality

Run code quality tools across the project and fix any reported errors and warnings. The respond with the exact `Output Format`.

## Instructions

Follow these steps in sequence to ensure code quality across all project components. Each subsection should be customized with project-specific tools, commands, and paths.

### 1. Setup and Context
- Describe how to change to the main project directory (for example, `cd <project-root>`)
- Describe how to initialize any required services or containers (for example, Docker, databases, or background processes)
- Describe how progress through the code quality steps should be tracked (for example, using TodoWrite or another task list mechanism)

### 2. Backend / Service Code Quality

Describe the code quality checks for the primary backend or service component (for example, an API or microservice). For each check, specify the commands to run and how to handle failures.

**a. Style / Linting**
- Specify the command(s) to run the style or linting tool for the backend
- Describe how to apply automatic fixes (if available) and when manual edits are required
- Instruct to re-run the style or linting check until it passes

**b. Static Analysis**
- Specify the static analysis tool and command(s) to run it
- Describe the kinds of issues to fix (for example, type errors, undefined variables, unreachable code)
- Instruct to re-run the static analysis check after fixes until it passes

**c. Unit Tests**
- Specify how to run the backend unit test suite
- Describe how to interpret failure output and locate failing tests
- Instruct to fix underlying issues and re-run tests until they pass

**d. Integration Tests (if applicable)**
- Specify how to run backend integration tests, if they exist
- Describe how to handle failing integration tests and verify fixes

### 3. E2E Code Quality

Describe the end-to-end (E2E) test workspace (for example, a separate test project or directory) and the tools used there.

**a. Type Checking or Build**
- Specify the command(s) to run type checking or compilation for the E2E project
- Describe how to fix type or build errors and re-run checks

**b. Linting**
- Specify the lint command(s) for the E2E project
- Describe how to use any auto-fix options and when to apply manual fixes
- Instruct to re-run linting until it passes

**c. Format Check**
- Specify the command(s) to check code formatting
- Describe how to auto-format code and re-run the format check

**d. Aggregated Quality Check (if applicable)**
- Specify any combined or convenience command(s) that run all E2E quality checks
- Indicate that this command should pass once the earlier steps are resolved

### 4. Application / Frontend Code Quality

Describe the code quality checks for the primary application or frontend component.

**a. Type Checking or Build**
- Specify the build or type-check command(s) for the application
- Describe how to interpret and fix build or type-check failures
- Instruct to re-run the build or type-check until it succeeds

**b. Linting**
- Specify the lint command(s) for the application
- Describe how to fix lint issues (including auto-fix options, if available)
- Instruct to re-run linting until it passes

**c. Unit Tests**
- Specify how to run the application unit test suite
- Describe how to read failing test output and fix issues
- Instruct to re-run tests until they pass

### 5. Final Verification

Describe the final verification step for this project:
- Specify the full set of commands to re-run all relevant code quality checks (backend, E2E, application)
- Indicate that all commands should complete successfully before code quality work is considered done

## Best Practices

- Fix issues incrementally - run check, fix, re-check
- Use auto-fix tools first (phpcbf, eslint --fix, prettier)
- Read the actual error messages carefully before attempting fixes
- Verify fixes don't break existing functionality
- Update the todo list as you progress through each step
- Mark each task as in_progress before starting, completed after finishing

## Error Handling

- If Docker containers aren't running, start them: `docker compose up -d`
- If npm/composer dependencies are missing, install them first
- If a tool fails with an unexpected error, report it and ask for guidance
- Don't skip failing tests - investigate and fix the root cause

## Output Format

Return ONLY valid JSON with zero additional text, formatting, markdown, or explanation. Your entire reply must be a single JSON object matching this structure:

{"output":"code-quality","tools":["tool-command-1","tool-command-2"]}

Rules:
- Respond exclusively with JSON in the format above
- `output` must be "code-quality"
- `tools` is an array of commands run for each of the tools
- Do NOT include code fences, line breaks outside the JSON structure, or extra commentary
- If no code quality tools are run, return an empty `tools` array
