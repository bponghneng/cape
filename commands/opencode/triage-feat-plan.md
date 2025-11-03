---
description: Triage a feature research report into an implementation plan.
agent: plan
model: GLM-4.6
---

# Triage a Research Report into an Implementation Plan

Design and plan the implementation of `Research Report` using the exact specified markdown `Plan Format`. Follow the `Instructions` to create the plan and use the `Relevant Files` to focus on the right files.

## Instructions

- You're writing a document to translate a feature research report into a plan to implement a feature that will add value to the application.
- Use the `taskmaster` agent to break down `Research Report` into actionable work increments that can be completed in 1-2 days by a single engineer.
- Create the plan in the `specs/*.md` file. Name it appropriately based on the `Feature`.
- Use the `Plan Format` below to create the plan.
- Read the reasearch report file specified in `Research Report`.
- IMPORTANT: Replace every <placeholder> in the `Plan Format` with the requested value. Add as much detail as needed to implement the feature successfully.
- Use your reasoning model: THINK HARD about the feature requirements, design, and implementation approach.
- Follow existing patterns and conventions in the codebase. Don't reinvent the wheel.
- Design for extensibility and maintainability, but remember the simplicity mindset.
- Respect requested files in the `Relevant Files` section.
- Start your research by reading the `CLAUDE.md` and `ws2-mobile/README.md` files.

## Relevant Files

Focus on the following files:

- `ws2-mobile/package.json` - Contains the project configuration and dependencies.
- `ws2-mobile/README.md` - Contains the project overview and instructions.
- `ws2-mobile/src/**` - Contains the source code for the application.

Ignore all other files in the codebase.

## Plan Format

```md
# Feature: <feature name>

## Feature Description

<describe the feature in detail, including its purpose and value to users>

## User Story

As a <type of user>
I want to <action/goal>
So that <benefit/value>=

## Technical Specification

<snippets for database migrations and schema, context modules and functions, controller methods, view modules and functions, API endpoint routes and other relevant code>

## Implementation Increments

<list step by step increments as h3 headers plus bullet points. use as many h3 headers as needed to implement the feature. Order matters, start with the foundational shared changes required then move on to the specific implementation. Include creating tests throughout the implementation process. Each increment should be a complete unit of work that can be completed in 1-2 days by a single engineer. Your last step should be running the `Validation Commands` to validate the feature works correctly with zero regressions.>

### Increment 1: <title of the increment>

<describe the increment in detail, including its purpose and value to users>

#### Implementation Details

<reference sections in `Technical Specification` and `Relevant Files` related to the increment>

#### Relevant Files

<find and list the files that are relevant to the increment. Describe why they are relevant in bullet points. If there are new files that need to be created for the increment, list them in an h4 'New Files' section.>

#### Key Test Cases

<list key test cases for the increment. Include unit tests, integration tests and API tests as appropriate. Testing strategy should be clear, concise and lean. Focus on core functionality and minimize testing of edge cases.>

#### Acceptance Criteria

<list specific, measurable criteria that must be met for the increment to be considered complete>

#### Dependencies

<list any work increment dependencies that must be completed before this increment can be implemented>

## Notes

<optionally list any additional notes, future considerations, or context that are relevant to the feature that will be helpful to the tech lead planning work increments>
```

## Research Report

## $ARGUMENTS
