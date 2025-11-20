---
description: Validate that an implementation matches its plan and report requirement status as JSON.
---

# Plan Acceptance Validation

Review a completed implementation against its plan and report whether the plan’s requirements have been met.

## Input

- Treat `$ARGUMENTS` as the **relative path** to a single plan file to validate (for example, `specs/chore-phinx-migrations-setup-plan.md`).
- Use that path to read the plan content (the file is included at the end of this prompt).
- You may read additional files in the repository as needed to verify whether requirements are satisfied.
- This command is **read-only**: do not modify any files, configuration, or databases as part of acceptance; only inspect and report.

## Plan Structure to Expect

Plans generally follow this structure:

- `# <Plan Title>`
- `## Task Context`
- `## Description`
- `## Relevant Files`
- `## Implementation Plan`
- `## Validation`
- `## Notes / Future Considerations` (optional)

The exact section titles may vary slightly; treat headings starting with `##` as section boundaries and infer intent from the content.

## Deriving Requirements

From the plan, derive a concrete list of requirements to check. At minimum:

- From **Task Context / Goal / Constraints**:
  - High-level outcome requirements (for example, “Support multiple environments”, “Use environment variables instead of hard-coded credentials”).
- From **Description**:
  - Key functional/structural requirements (for example, “Add Phinx as migration tool”, “Create migrations for users and auth_tokens tables”).
- From **Relevant Files / New Files**:
  - File-level expectations (files that should exist or be updated, and their intended roles).
- From **Implementation Plan**:
  - Each numbered step (and any important sub-bullets) becomes one or more concrete requirements (for example, “Add Phinx dev dependency to api/composer.json”, “Create api/phinx.php with development, e2e, testing environments configured from $_ENV”, “Add composer scripts migrate:dev, migrate:e2e, migrate:testing, etc.”).
- From **Validation**:
  - Each validation command plus its expected outcome is a requirement (for example, “Phinx CLI reports a version”, “Migrations run successfully and create specific tables/columns”).

Group related requirements logically (for example, by section or phase), but ensure each requirement is specific enough to be checked in the codebase.

## Verification Approach

For each derived requirement:

1. **Identify evidence sources**
   - Map the requirement to concrete files, configuration, or database/migration artifacts that should demonstrate it has been met.
   - Use the `Relevant Files` and `New Files` sections as primary hints for where to look.
2. **Inspect the repository**
   - Open and inspect the relevant files (for example, `api/composer.json`, `api/phinx.php`, `api/db/migrations/*.php`, config files, specs).
   - When the requirement refers to database structure, infer from migrations and configuration rather than live databases when possible.
3. **Use validation commands cautiously**
   - The plan’s `Validation` section may include commands (for example, `docker compose exec api composer migrate:dev`).
   - You may run commands when safe and appropriate, but it is acceptable to infer status from code and configuration alone if running commands is not feasible.
   - If you cannot reliably run a validation command, mark the requirement’s status as `unknown` and explain why in `evidence`.
4. **Assign requirement status**
   - `met` – clear evidence in the repository (and/or successful validation commands) shows the requirement is satisfied.
   - `not_met` – clear evidence that the requirement was not satisfied (for example, missing file, missing script, wrong configuration, or validation clearly not implemented).
   - `unknown` – not enough evidence to decide (for example, external system needed, command cannot run, or ambiguity in the plan).
5. **Determine blocking vs non-blocking**
   - Consider requirements derived from **Goals**, **Constraints**, and **Validation** as blocking by default.
   - Minor notes or optional future considerations may be treated as non-blocking.

## Overall Plan Status

After checking all requirements:

- Set the overall `status` to:
  - `pass` – all blocking requirements are `met`, and there are no clearly violated constraints.
  - `fail` – one or more blocking requirements are `not_met`.
  - `partial` – no blocking requirements are clearly `not_met`, but some blocking requirements are `unknown` or there is significant ambiguity.

Explain your reasoning briefly in the `summary` field of the JSON output.

## Output (JSON Only)

This command runs in a noninteractive mode. Your **entire** output must be a single valid JSON object with **no additional text** before or after it.

Use this shape (you may add fields, but do not remove or rename these keys):

```json
{
  "plan_title": "Chore Plan: Phinx Migrations Setup",
  "status": "pass",
  "summary": "All blocking requirements from the Phinx migrations setup plan are implemented and validated.",
  "requirements": [
    {
      "id": "task-context-goal-1",
      "section": "Task Context / Goal",
      "description": "Introduce Phinx as the migration system for the API to support multiple database environments.",
      "status": "met",
      "blocking": true,
      "evidence": "api/composer.json includes robmorgan/phinx in require-dev and api/phinx.php defines development, e2e, and testing environments driven by $_ENV."
    },
    {
      "id": "impl-phase-1-step-1",
      "section": "Implementation Plan / Phase 1",
      "description": "Add Phinx as a dev dependency in api/composer.json and install it.",
      "status": "met",
      "blocking": true,
      "evidence": "composer.json updated; Phinx CLI available or configuration present."
    },
    {
      "id": "validation-step-3",
      "section": "Validation",
      "description": "Run composer migrate:dev to create users and auth_tokens tables in mexicantrain_dev.",
      "status": "unknown",
      "blocking": true,
      "evidence": "Migrations and scripts appear correctly configured, but validation command was not executed in this environment."
    }
  ],
  "unmet_blocking_requirements": [
    "impl-phase-2-step-4"
  ],
  "notes": [
    "Some validation commands could not be executed; requirements tied to those commands are marked as unknown."
  ]
}
```

- `plan_title`: Title from the plan’s top-level heading.
- `status`: `pass`, `fail`, or `partial` as defined above.
- `requirements`: One entry per derived requirement, with:
  - `id`: A stable identifier (for example, based on section and step number).
  - `section`: The section of the plan the requirement came from.
  - `description`: Short restatement of the requirement in your own words.
  - `status`: `met`, `not_met`, or `unknown`.
  - `blocking`: `true` if failure/unknown should affect overall status, otherwise `false`.
  - `evidence`: Brief explanation of how you reached the status.
- `unmet_blocking_requirements`: List of `id` values for blocking requirements that are `not_met`.
- `notes`: Optional additional context for humans or follow-up work.

If you cannot parse the plan or cannot reasonably assess its requirements, set:

- `status`: `"fail"`
- `summary`: Explain why acceptance could not be performed.
- `requirements`: An empty array or partial list with appropriate `unknown` statuses.

## Plan to Validate

- Plan file path: `$ARGUMENTS`
- Plan file content:

@$ARGUMENTS
