---
description: Create Plane work items from a feature implementation plan.
thinking: true    
---

# Create Plane Work Items from a Implementation Plan

Parse the implementation increments in the `Implementation Plan` and create Plane work items using the exact specified markdown `Work Item Format`. Follow the `Instructions` to parse the `Implementation Plan` and create the work items as directed. Report the created work items as outlined in `Report`.

## Instructions

- You're parsing a feature implementation plan and creating Plane work items from it.
- IMPORTANT: Before parsing the `Implementation Plan`, read `ai_docs/plane-project-info.md` for reference information on workspace objects available in Plane.
- Read the `Implementation Plan` and identify:
  - The implementation plan file
  - The following Plane properties specified:
    - Issue Type or Type - default to "Development"
    - State - default to "DEV Backlog"
    - Cycle - default to the cycle of the current date
- Read the implementation plan file and identify the `Implementation Increments` section.
- For each increment, create a Plane work item using the exact specified markdown `Work Item Format` and set the issue type, state, and cycle properties as specified.
    
## Work Item Format

```md
# <Increment Title>

## Description

<description of the increment from the plan file>

## Implementation Details

<implementation details of the increment from the plan file>

## Relevant Files

<relevant files of the increment from the plan file>

## Key Test Cases

<key test cases of the increment from the plan file>

## Acceptance Criteria

<acceptance criteria of the increment from the plan file>

## Dependencies

<dependencies of the increment from the plan file>

## Notes

<notes of the increment from the plan file>
```

## Implementation Plan

$ARGUMENTS

## Report
- Summarize the created work items in a concise bullet point list:
  - <identifier of the work item>: <title of the work item>