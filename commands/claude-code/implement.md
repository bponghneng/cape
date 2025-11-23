---
description: Execute a plan
thinking: true
---

# Implement Plan

Follow the `Instructions` to implement the provided `Plan`, adhering to project standards. Report your results with the exact `Output Format`.

## Instructions

1.  **Preparation**:
    - Read `AGENTS.md` to align with the workspace structure and "Simplicity-First Mindset".
    - Treat `$ARGUMENTS` as the **relative path** to a single plan file to implement (for example, `specs/chore-phinx-migrations-setup-plan.md`).
    - Analyze the `Plan` to understand the requirements and scope.

2.  **Execution**:
    - Implement the changes iteratively.
    - **Research First**: Use search tools (like grep) to find relevant code and understand the broader context before making any edits. This ensures you understand existing patterns and dependencies.
    - Ensure backward compatibility where required (see `AGENTS.md`).

3.  **Reporting**:
    - Run `git diff --stat` to capture the changes.
    - Compile the work summary and file list.

## Output Format

Return ONLY valid JSON with zero additional text, formatting, markdown, or explanation:

{"summary": "Concise summary of the implemented work", "files_modified": ["path/to/file1.ext", "path/to/file2.ext"], "planPath": "Relative path to the implemented plan file", "git_diff_stat": "Output string from git diff --stat", "status": "completed"}

**CRITICAL:** Your entire response must be this single line of valid JSON. Do not include:
- Code fences (```)
- Line breaks between the braces
- Any text before or after the JSON
- Markdown formatting
- Explanations or commentary

## Plan

$ARGUMENTS