---
description: Triage a feature and produce a size-aware, simplicity-first implementation plan.
---

# Triage a Feature into an Implementation Plan

Create a new implementation plan for a feature using the `Plan Format` below. The goal is to give an implementer just enough clarity to build the feature confidently, while keeping the plan as small and simple as the feature allows.

## Instructions

- IMPORTANT: The `Feature` describes the work that must be done. You are not implementing it; you are creating an implementation plan.
- First, decide whether this is a **small-change**, **medium-change**, or **large-refactor** feature and record that in the plan. Use that scope to right-size your research effort and the amount of detail.
- Apply a **simplicity-first** mindset (see `mexican-train/AGENTS.md`): prefer the smallest coherent implementation that delivers the desired value, avoid premature abstractions, and keep dependencies minimal.
- Research the codebase just enough to understand the problem/opportunity, the affected areas, and a solid solution that fits existing patterns.
- Use the `Research Method` section as guidance, not a checklist; you may skip steps that are clearly unnecessary for small features.
- You may use subagents (`research-specialist`, `php-architect`, `taskmaster`) when helpful:
  - `research-specialist` for external docs and best practices.
  - `php-architect` for architecture / design questions in `mexican-train/api`, and especially for features that affect database schemas, migrations, or authentication flows.
  - `taskmaster` to refine the implementation steps into increments of 1–2 days for a single engineer.
- Create the plan in the `./specs/` directory using the naming convention: `./specs/feature-<feature-name>-plan.md` (use a lowercase, hyphenated feature name).
- Replace every `<placeholder>` in the `Plan Format` with the requested value.
- Follow existing patterns and conventions in the codebase. Do not invent new patterns unless necessary, and call out when you do.

## Research Method

- Start by reading `AGENTS.md`, `README.md`, and any project-level instructions referenced there.
- Clearly define the problem or opportunity the feature addresses, including which users it affects and why it matters.
- Clarify any constraints (e.g., performance, compatibility, existing API contracts) and what is explicitly out of scope for this feature.
- Identify the smallest set of files and modules that are relevant to the feature. Understand how they currently behave and how the feature will interact with them.
- For small features, keep research light and focused. For medium/large features, you may:
  - Consult `research-specialist` for relevant external documentation or prior art.
  - Consult `php-architect` for architectural implications and design options.
- Propose test coverage only for critical paths introduced or modified by the feature. Focus on core behavior; avoid exhaustive edge-case enumeration.
- Keep your analysis and recommendations as simple and concise as possible while still enabling a high-confidence implementation.

## Plan Format

```md
# Feature Plan: <feature name>

## Task Context (Required)

- Scope: <small-change | medium-change | large-refactor>
- Area: <api | app-ionic | app-old | shared | other>
- Primary Users: <who this feature is for>
- Goal: <1–3 bullets describing the outcome and value of this feature>
- Constraints: <any key assumptions, constraints, or dependencies (optional)>

## Description (Required)

<2–4 bullets describing the feature, its purpose, and the value it delivers to users.>

## User Story (Recommended)

As a <type of user>  
I want to <action/goal>  
So that <benefit/value>

## Problem & Solution Overview (Required)

### Problem

<clearly describe the problem or opportunity this feature addresses.>

### Proposed Solution

<describe the high-level solution approach and how it solves the problem while fitting existing patterns.>

## Relevant Files (Required)

<list only the files that are relevant to implementing this feature and briefly describe why each is relevant.>

#### New Files (Optional)

<list any new files expected to be created for this feature, with a short note on their purpose.>

## Implementation Plan (Required)

<describe how to implement this feature in a way that matches the scope:>

- For **small features**, provide a single ordered list of 3–7 concrete steps.
- For **medium/large features**, group steps into phases (e.g., "Phase 1: Foundation", "Phase 2: Core Implementation", "Phase 3: Integration") with ordered lists under each.
- Each step should be a unit of work that can be completed in 1–2 days by a single engineer.
- Include where tests or validation are added or updated, but avoid over-specifying trivial details that can be left to the implementer’s judgement.

## Testing & Validation Strategy (Required)

<outline how to verify the feature works and does not introduce obvious regressions: unit tests, integration tests, and any key edge cases. Focus on critical paths and realistic usage scenarios, not exhaustive combinations.>

## Acceptance Criteria (Required)

<list specific, measurable criteria that must be met for the feature to be considered complete (e.g., behavior, performance, UX expectations).>

## Validation (Required)

Explain how to validate that the feature works as intended and that there are no obvious regressions.

<list the commands to run (e.g., linting, targeted tests, or other existing project commands) and briefly state what each command is validating. Include any manual verification steps (e.g., key user flows) if they are important. Choose a level of validation that gives high confidence appropriate to the scope and risk of the feature. Avoid using raw curl commands for validation.>

## Notes / Future Considerations (Optional)

<optionally list any additional notes, follow-up ideas, or context that might inform future improvements or related features.>
```

For small-change features, keep the overall plan concise: fill in `Task Context`, `Description`, a brief `User Story` (if applicable), `Problem & Solution Overview`, `Relevant Files`, a short `Implementation Plan`, and minimal `Testing & Validation` / `Acceptance Criteria`. Use `Notes / Future Considerations` only when it clearly adds value.

## Report

Summarize the work you've done using the following JSON format:

```json
{
  "feature": "<feature name>",
  "plan": "<plan file path>",
  "summary": "<concise summary of the work you've done>"
}
```

## Feature

$ARGUMENTS
