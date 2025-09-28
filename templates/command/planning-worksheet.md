---
argument-hint: [additional-notes...]
description: Generate a planning worksheet from the current chat context using the planning-worksheet.md template
---

# Context

- Current Conversation: Use the active chat context as the primary source of truth (no external file references).
- Additional Notes (from args): "$ARGUMENTS"
- Template (use exactly this structure when producing the final output; do not include this Template section in your response):

```markdown
# <TICKET_ID>: <Plan Title>

<!-- Purpose: Abstract planning worksheet for senior engineer inputs to Spec Kit (spec/plan). Minimal structure to organize initial thinking; let Spec Kit infer details. Fill in all <...> placeholders. -->

## What and Why

### Intent (one-liner)

- <One sentence capturing the essence of the work>

### Value (why)

- <User/business value #1>
- <User/business value #2>

### Signals of success

- <Measurable or acceptance statement #1>
- <Measurable or acceptance statement #2>

---

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

Using the template above and the current conversation:

1. Produce a completed planning worksheet in the exact structure shown in the Template.
2. Extract Intent, Value, and Signals of success from the conversation. Keep them concise.
3. Outline Constraints & principles and Unknowns & assumptions.
   - Use [NEEDS CLARIFICATION: ...] for any ambiguity rather than guessing.
4. Provide a brief Approach sketch aligned to the conversation context.
5. Set an appropriate Execution cadence (e.g., “Generic phases” or “Add QA checkpoint prior to release”).
6. Fill Logistics with any IDs/owners/links mentioned in the conversation. If not present, leave placeholders.
7. If "$ARGUMENTS" is provided, incorporate them as clarifying notes or into relevant sections.
8. Output only the completed planning worksheet as Markdown. Do not include commentary, the raw template, or extra prose.

# Output Format

Return a single Markdown document that strictly follows the section headings in the template:

- “What and Why” → Intent, Value, Signals of success
- “How: Implementation Plan” → Constraints & principles, Unknowns & assumptions, Approach sketch, Execution cadence, Logistics
- Optional: Risks & mitigations, Scope (in/out), Notes & links
