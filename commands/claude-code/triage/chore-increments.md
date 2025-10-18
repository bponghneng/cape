---
description: Create Increment Task Items from a chore implementation plan.
thinking: true    
---

# Create Increment Task Items from a Chore Implementation Plan

Parse the `Implementation Plan` and create increment task documents using the exact specified markdown `Increment Task Format`. Follow the `Instructions` and create the increment tasks as directed. Report the created increment tasks as outlined in `Report`.

## Instructions

- You're parsing an implementation plan for a codebase chore and creating increment task documents from it.
- Read the `Implementation Plan` and identify the implementation plan file.
- Read the implementation plan file and identify the `Implementation Increments` section.
- For each increment, create an increment task document using the exact specified markdown `Increment Task Format`. Create the file in the `./specs/` directory using the format `./specs/increment-<chore slug>-<increment number>.md`.
    
## Increment Task Format

```md
# <chore title from implementation plan>

This document is an increment task for the chore <chore title from implementation plan>. It is created from the implementation plan file <implementation plan file>. The current increment is <increment number> of <total number of increments>.

## User Story

<user story of the chore from the plan file>

## Technical Specification

<technical specification of the chore from the plan file>

## Increment Details

### Description

<description of the increment from the plan file>

### Implementation Details

<implementation details of the increment from the plan file>

### Relevant Files

<relevant files of the increment from the plan file>

### Key Test Cases

<key test cases of the increment from the plan file>

### Acceptance Criteria

<acceptance criteria of the increment from the plan file>

### Dependencies

<dependencies of the increment from the plan file>

### Notes

<notes of the increment from the plan file>
```

## Implementation Plan

$ARGUMENTS

## Report

Summarize the created increment tasks and output the following JSON:

```json
{
    "chore": "<chore title from implementation plan>",
    "implementation-plan-file": "<implementation plan file>",
    "total-increments": <total number of increments>,
    "increments": ["<increment task file>", ...]
}
```
