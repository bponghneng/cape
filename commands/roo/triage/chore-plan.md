---
description: Triage a chore into an implementation plan. For immediate implementation, use the `triage/chore` command.
---

# Triage a Chore into an Implementation Plan

Create a new implementation plan for a codebase chore using the exact specified markdown `Plan Format`. Follow the `Instructions` to conduct the research and create the plan. Focus on `Relevant Files` listed in `README.md`. 

## Instructions

- IMPORTANT: You're writing a plan to resolve a codebase chore that will add value to the application.
- IMPORTANT: The `Chore` describes the work that must be done, but remember that we're not implementing the chore yet. We're creating the plan using the `Plan Format` below.
- Research the codebase to determine the problem specified in the `Chore` and identify the best solution.
- Use the `research-specialist` and `react-native-architect` agents to research the chore. Follow the `Research Methods` to focus your research.
- Use the `taskmaster` agent to break down the solution into a plan with actionable work increments that can be completed in 1-2 days by a single engineer.
- Create the plan in the `./specs/` directory using the following naming convention: `./specs/chore-<chore name>-plan.md`.
- Use the `Plan Format` below to create the plan.
- IMPORTANT: Replace every <placeholder> in the `Plan Format` with the requested value. Add as much detail as needed to implement the chore successfully.
- Instructions for subagents:
    - Use your reasoning model: THINK HARD about the chore requirements, design and implementation approach.
    - Start your work by reading the `CLAUDE.md` and `README.md` files.
    - Follow existing patterns and conventions in the codebase. Don't reinvent the wheel.
    - Design for extensibility and maintainability, but remember to keep a simplicity mindset.
    - Respect the `Relevant Files` listed in the `README.md`.

## Research Method

- Use the `research-specialist` subagent to identify best practices and patterns and to source documentation related to the chore.
- Use the `react-native-architect` subagent to understand the architecture of the codebase, to detail existing implementations and to determine the best solution.
- Clearly define the specific problem or opportunity the chore addresses.
- Describe the proposed solution approach and how it solves the problem.
- Find and list the files that are relevant to the chore implementation and understand why they are relevant.
- Consider legacy patterns that may need to be refactored, alternate approaches or design patterns that may be more appropriate or context that is relevant to the chore that will be helpful to lead engineers planning work increments specific to this chore.
- IMPORTANT: Propose test coverage to address only critical scenarios. Focus on core functionality. Avoid excessive testing of edge cases.
- IMPORTANT: Remember the simplicity mindset when reporting the results of your research. Your analysis and recommendations should be as simple as possible. Be clear, concise and thorough.

## Plan Format

```md
# Chore Plan: <chore name>

## Description

<describe the chore in detail>

## Implementation Increments

<list step by step increments as h3 headers plus bullet points. use as many h3 headers as needed to implement the chore. Order matters, start with the foundational shared changes required then move on to the specific implementation. Include creating tests throughout the implementation process. Each increment should be a complete unit of work that can be completed in 1-2 days by a single engineer. Your last step should be running the `Validation Commands` to validate the chore works correctly with zero regressions.>

### Increment 1: <title of the increment>

<describe the increment in detail>

#### Relevant Files

<find and list the files that are relevant to the increment. Describe why they are relevant in bullet points. Include snippets for database migrations and schema, context modules and functions, controller methods, view modules and functions, API endpoint routes and other relevant code for the increment. If there are new files that need to be created for the increment, list them in an h4 'New Files' section.>

#### Key Test Cases

<list key test cases for the increment. Include unit tests, integration tests and API tests as appropriate. Testing strategy should be clear, concise and lean. Focus on core functionality and minimize testing of edge cases.>

#### Acceptance Criteria
<list specific, measurable criteria that must be met for the increment to be considered complete>

#### Dependencies
<list any work increment dependencies that must be completed before this increment can be implemented>

## Notes
<optionally list any additional notes, future considerations, or context that are relevant to the feature that will be helpful to the tech lead planning work increments>
```

## Chore

$ARGUMENTS

## Report

- Summarize the workyou've just done in a concise bullet point list.
- Include the path to the plan file you created in the `./specs/chore-<chore name>-plan.md` file.
