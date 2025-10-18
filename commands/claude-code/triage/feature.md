---
description: Triage a feature into an implementation plan.
---

# Triage a Feature into an Implementation Plan

Create a new implementation plan for a new feature using the exact specified markdown `Plan Format`. Follow the `Instructions` to conduct the research and create the plan. Focus on `Relevant Files` in `README.md`.

## Instructions

- IMPORTANT: You're writing a plan to implement a feature that will add value to the application.
- IMPORTANT: The `Feature` describes the work that must be done, but remember that we're not implementing the feature yet. We're creating the plan using the `Plan Format` below.
- Research the codebase to determine the problem specified in the `Feature` and identify the best solution.
- Use the `research-specialist` and `react-native-architect` agents to research the feature. Follow the `Research Methods` to focus your research.
- Use the `taskmaster` agent to break down the solution into a plan with actionable work increments that can be completed in 1-2 days by a single engineer.
- Create the plan in the `./specs/` directory using the following naming convention: `./specs/feature-<feature name>-plan.md`.
- Use the `Plan Format` below to create the plan.
- IMPORTANT: Replace every <placeholder> in the `Plan Format` with the requested value. Add as much detail as needed to implement the feature successfully.
- Instructions for subagents:
    - Use your reasoning model: THINK HARD about the feature requirements, design and implementation approach.
    - Start your work by reading the `CLAUDE.md` and `README.md` files.
    - Follow existing patterns and conventions in the codebase. Don't reinvent the wheel.
    - Design for extensibility and maintainability, but remember to keep a simplicity mindset.
    - Respect the `Relevant Files` listed in the `README.md`.

## Research Method

- Use the `research-specialist` subagent to identify best practices and patterns and to source documentation related to the feature.
- Use the `react-native-architect` subagent to understand the architecture of the codebase, to detail existing implementations and to determine the best solution.
- Clearly define the specific problem or opportunity the feature addresses.
- Describe the proposed solution approach and how it solves the problem.
- Find and list the files that are relevant to the feature implementation and understand why they are relevant.
- IMPORTANT: Propose test coverage to address only critical scenarios. Focus on core functionality. Avoid excessive testing of edge cases.
- Consider legacy patterns that may need to be refactored, alternate approaches or design patterns that may be more appropriate or context that is relevant to the feature that will be helpful to lead engineers planning work increments specific to this feature.
- IMPORTANT: Remember the simplicity mindset when reporting the results of your research. Your analysis and recommendations should be as simple as possible. Be clear, concise and thorough.

## Plan Format

```md
# Feature: <feature name>

## Description

<describe the feature in detail, including its purpose and value to users>

## User Story

As a <type of user>
I want to <action/goal>
So that <benefit/value>

## Problem Statement
<clearly define the specific problem or opportunity this feature addresses>

## Solution Statement
<describe the proposed solution approach and how it solves the problem>

## Relevant Files

Use these files to implement the feature.

<find and list the files that are relevant to the increment. Describe why they are relevant in bullet points. Include snippets for database migrations and schema, context modules and functions, controller methods, view modules and functions, API endpoint routes and other relevant code for the increment. If there are new files that need to be created for the increment, list them in an h4 'New Files' section.>

## Implementation Plan

### Phase 1: Foundation
<describe the foundational work needed before implementing the main feature>

### Phase 2: Core Implementation
<describe the main implementation work for the feature>

### Phase 3: Integration
<describe how the feature will integrate with existing functionality>

## Step by Step Tasks

IMPORTANT: Execute every step in order, top to bottom.

<list step by step tasks as h3 headers plus bullet points. Use as many h3 headers as needed to implement the feature. Order matters, start with the foundational shared changes required then move on to the specific implementation. Include creating tests throughout the implementation process. Your last step should be running the `Validation Commands` to validate the feature works correctly with zero regressions.>

## Testing Strategy

### Unit Tests
<describe unit tests needed for the feature>

### Integration Tests
<describe integration tests needed for the feature>

### Edge Cases
<list edge cases that need to be tested>

## Acceptance Criteria
<list specific, measurable criteria that must be met for the feature to be considered complete>

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

<list commands you'll use to validate with 100% confidence the feature is implemented correctly with zero regressions. every command must execute without errors so be specific about what you want to run to validate the feature works as expected. Include commands to test the feature end-to-end.>
- `cd ws2-mobile` - Change directory to the root of the codebase.
- `npm run format` - Format the codebase.
- `npm run lint` - Lint the codebase.
- `npm run type-check` - Type check the codebase.
- `npm run test` - Run the test suite.
- `cd ..` - Change directory to workspace root.


## Notes
<optionally list any additional notes, future considerations, or context that are relevant to the feature that will be helpful to the tech lead planning work increments>
```

## Feature

$ARGUMENTS

## Report

Summarize the work you've done using the following JSON format:

```json
{
    "feature": "<feature name>",
    "plan": "<plan file path>",
    "summary": "<concise summary of the work you've done>"
}
```