---
argument-hint: "[additional-notes...]"
description: Generate a planning worksheet from the current chat context using the planning-worksheet.md template
allowed-tools: Read
template: |
  ## Context

  - Current conversation: Use the active chat context as the primary source of truth (no external file references).
  - Additional notes (from args): "$ARGUMENTS"

  ## Project Context

  @CLAUDE.md

  ## Template

  Use exactly these two structures when producing the final output; do not include this Template section in your response:

  Template A — What and Why

  ```markdown
  # <Feature, Chore or Bugfix Title>

  ## What and Why

  ### Intent (one-liner)

  - <One sentence capturing the essence of the work>

  ### Value (why)

  - <User/business value #1>
  - <User/business value #2>

  ### Signals of success

  - <Measurable or acceptance statement #1>
  - <Measurable or acceptance statement #2>
  ```

  Template B — How: Implementation Plan

  ```markdown
  # <Feature, Chore or Bugfix Title>

  ## How: Implementation Plan

  ### Constraints & principles

  - <Guardrails, org principles, and boundaries to respect>

  ### Unknowns & assumptions

  - [NEEDS CLARIFICATION: <question or ambiguity>]
  - [NEEDS CLARIFICATION: <question or ambiguity>]

  ### Approach sketch

  <Freeform: short paragraph, quick flow description, or lightweight diagram in text>

  ### Execution cadence

  <e.g., "Generic phases" or "Add QA checkpoint prior to release">

  ### Logistics

  - Task ID(s): <Archon ID, ticket IDs>
  - Owner(s): <names/roles>
  - Links: <Task link(s) | PR(s) | Design Doc(s)/ADR(s)>
  - Type/Scope: <Feature | Bugfix | Codebase chore | Experiment | Documentation; key surfaces/components>

  ### Risks & mitigations (Optional)

  - <Top risks and how you'd address them>

  ### Scope (in/out) (Optional)

  - In: <Key items>
  - Out: <Key exclusions>

  ### Notes & links (Optional)

  - <Pointers to context, prior art, or references>
  ```

  # Your Task

  Using the templates above and the current conversation:

  1. Produce TWO completed Markdown documents:
     - Document 1: What and Why (Template A)
     - Document 2: How: Implementation Plan (Template B)
  2. Extract Intent, Value, and Signals of success from the conversation for Document 1. Keep them concise.
  3. For Document 2, outline Constraints & principles and Unknowns & assumptions.
     - Use [NEEDS CLARIFICATION: ...] for any ambiguity rather than guessing.
  4. Provide a brief Approach sketch aligned to the conversation context.
  5. Set an appropriate Execution cadence (e.g., "Generic phases" or "Add QA checkpoint prior to release").
  6. Fill Logistics with any IDs/owners/links mentioned in the conversation. If not present, leave placeholders.
  7. If "$ARGUMENTS" is provided, incorporate them as clarifying notes or into relevant sections of either document.
  8. Output only the two completed Markdown documents. Do not include commentary, the raw template, or extra prose.

  # Output Format

  Return TWO Markdown documents, in this order:

  1) What and Why document (Template A):
     - Includes: Intent, Value, Signals of success
  2) How: Implementation Plan document (Template B):
     - Includes: Constraints & principles, Unknowns & assumptions, Approach sketch, Execution cadence, Logistics
     - Optional: Risks & mitigations, Scope (in/out), Notes & links

  Do not include commentary, the raw templates, or extra prose. Separate the two documents with a blank line and a line containing only `---`, or return them as two distinct Markdown blocks if supported.
---