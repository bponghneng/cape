---
description: Use an automated review report to work through issues one by one with simplicity-first fixes.
---

# Work Through Automated Review Issues

Use the automated review report below to drive a focused round of fixes or follow-up plans in the `mexican-train` repository.

## Instructions

- Read `AGENTS.md` to align with the workspace structure and "Simplicity-First Mindset".
- Treat `$ARGUMENTS` as the full plain-text report produced by an automated reviewer (for example, `specs/chore-phinx-migrations-setup-review.md`).
- Apply the workflow rules and simplicity-first guidelines from `mexican-train/AGENTS.md`:
  - Research first, then propose, then implement.
  - Prefer the smallest coherent change that solves each issue.
  - Respect existing patterns and conventions in the codebase.
- Do not blindly apply suggestions; always verify them against the actual code, specs, and project documentation.
- When a change would be large or architecture-impacting, prefer to create or update a plan under `specs/` instead of implementing it directly, and clearly mark that issue as deferred in your report.

## Parsing the Review Report

- The report is organized into sections separated by `=====` lines.
- For each section, extract the following fields:
  - **File**: path after `File:` (for example, `api/phinx.php` or `specs/api/magic-link-jwt-auth.md`).
  - **Line range**: text after `Line:` (for example, `18 to 26`).
  - **Type**: value after `Type:` (for example, `potential_issue`).
  - **Prompt**: any text that appears after `Prompt for AI Agent:` up to the next blank line or section separator. This may be empty or missing.
- Treat each `File` section as a separate issue, even if multiple issues refer to the same file.

## Per-Issue Workflow

Process issues strictly in the order they appear in the report.

For each issue:

1. **Gather context**
   - Open the referenced file and inspect the indicated line range plus nearby context.
   - If a `Prompt for AI Agent` is present and non-empty, treat it as the primary instruction.
   - If the prompt is missing or empty, infer the concern from the code or spec around the referenced lines.
2. **Decide approach**
   - Decide whether this issue can be addressed as a **small, local change** that fits within the existing architecture.
   - If the issue implies a broader refactor, significant schema change, or spec overhaul:
     - Do not implement it directly.
     - Instead, create or update an implementation plan under `specs/` (for example, using the bug/chore plan formats) and mark this issue as `needs_followup` in your report.
3. **Propose the change**
   - Before editing files, briefly describe the intended change (what and why) in your working notes for this issue. This satisfies the “discuss before implementing” expectation.
   - Ensure the proposal is consistent with:
     - `AGENTS.md` (simplicity-first, minimal dependencies).
     - Any relevant docs such as `README.md`, `IMPLEMENTATION_GUIDE.md`, and specs under `specs/`.
4. **Implement small, clear fixes**
   - For issues classified as small and well-understood:
     - Apply the minimal code or spec change that resolves the issue.
     - Keep changes tightly scoped to the referenced behavior; avoid unrelated refactors.
     - When the issue concerns specs (for example, under `specs/api/`), update the specification text and examples consistently.
     - When the issue concerns executable code (for example, under `api/` or `app-old/`), ensure changes compile and match existing style.
   - Update or add tests/docs if that is necessary to keep the change safe and understandable.
5. **Validation**
   - When practical, run targeted validation appropriate to the area you touched (for example, PHP static analysis or tests for `api/`, or frontend tests for `app-old/`).
   - At minimum, re-read the changed code/spec to ensure it is internally consistent and does not obviously break existing behavior.

## Report

After processing all issues, produce a concise, machine-readable summary of what you did.

- Your entire output must be a single valid JSON object with no additional text before or after it.
- Use this shape (fields may be extended but not removed):

```json
{
  "summary": "Processed automated review issues and applied small, targeted fixes where safe.",
  "issues": [
    {
      "file": "specs/api/magic-link-jwt-auth.md",
      "lines": "236-239",
      "type": "potential_issue",
      "status": "fixed",
      "notes": "Unified error response for missing vs expired magic-link tokens."
    },
    {
      "file": "api/phinx.php",
      "lines": "18-26",
      "type": "potential_issue",
      "status": "fixed",
      "notes": "Added validation for required DB_* environment variables."
    },
    {
      "file": "specs/api/magic-link-jwt-auth.md",
      "lines": "196-221",
      "type": "potential_issue",
      "status": "needs_followup",
      "notes": "Requires broader design/spec decisions; created or recommended a plan in specs/."
    }
  ]
}
```

- `status` must be one of:
  - `fixed` – issue addressed via code/spec change.
  - `skipped` – intentionally not changed (explain why).
  - `needs_followup` – requires a separate plan or human decision.

## Automated Review Report

$ARGUMENTS
