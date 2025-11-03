---
description: Research codebase, web and document sources to understand patterns, architecture, and conventions for a new feature.
agent: plan
model: GLM-4.6
---

# Research for Feature Triage

Create a new research report in `specs/*.md` using the exact specified `Research Report Format`. Follow the `Instructions` to create the plan. Focus on `Relevant Files` in `README.md`. Follow `Research Methods` to use the right subagents in sequence.

## Instructions

- You're researching the implementation of an new feature specified in `Feature` to support architectural analysis and planning.
- Create the plan in the `specs/` directory using the following format: `specs/feat-<feature name>-research.md`.
- Use the `Research Report Format` below to create the plan.
- Follow the `Research Methods` to conduct the research.
- Research the codebase to understand existing patterns, architecture, and conventions.
- Research web and document sources to understand best practices and common patterns.
- Synthesize the research into a critical analysis of the new feature including a solution statement that can be used to plan the implementation and create tasks from actionable work increments.
- IMPORTANT: Replace every <placeholder> in the `Research Report Format` with the requested value. Add as much detail as needed to support architectural decisions and planning for modifications to or integration with the feature.
- Use your reasoning model: THINK HARD about the existing feature, including its design, implementation approach, and integration with other features.
- Follow existing patterns and conventions in the codebase. Don't reinvent the wheel.
- Respect the `Relevant Files` in the `README.md`.

## Research Methods

Use the following subagents in sequence:

- `research-specialist` - Use this subagent to conduct web and document searches for best practices and patterns.
- `react-native-architect` - Use this subagent to understand the architecture of the codebase and to detail existing implementations.

## Research Report Format

```md
# Feature: <feature name>

## Problem Statement

<clearly define the specific problem or opportunity the feature addresses>

## Solution Statement

<describe the proposed solution approach and how it solves the problem>

## Relevant Files

<find and list the files that are relevant to the feature implementation and describe why they are relevant in bullet points>

## Test Coverage

<describe the proposed test coverage for the feature implementation with bullet points listing the scenarios and test cases covered>

## Notes

<optionally list any additional critical analysis. Some examples are legacy patterns that may need to be refactored, alternate approaches or design patterns that may be more appropriate, or context that are relevant to the feature that will be helpful to lead engineers planning work increments specific to this feature>
```
