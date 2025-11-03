---
description: Format generated plan into an exactly formatted chore plan for ADW implementation.
thinking: true
---

# Format Chore

Reformat generated plan into an exactly formatted chore plan for ADW implementation.

## Instructions

- Rewrite the plan specified in `Plan File` using the exact `Plan Format`.

## Plan Format

```md
# Chore Plan: <chore name>

## Description

<describe the chore in detail>

## Relevant Files

<find and list the files that are relevant to the increment. Describe why they are relevant in bullet points. If there are new files that need to be created for the increment, list them in an h4 `New Files` section.>

## Step-by-Step Tasks

<list step by step tasks as h3 headers plus bullet points. use as many h3 headers as needed to implement the chore. Order matters, start with the foundational shared changes required then move on to the specific implementation. Include creating tests throughout the implementation process. Each increment should be a complete unit of work that can be completed in 1-2 days by a single engineer. Your last step should be running the `Validation Commands` to validate the chore works correctly with zero regressions.>

## Validation Commands

Execute every command to validate the chore is complete with zero regressions.

<list commands you will use to validate with 100% confidence the chore is complete with zero regressions. every command must execute without errors so be specific about what you want to run to validate the chore is complete with zero regressions. Do not validate with curl commands.>

## Notes

<optionally list any additional notes, future considerations, or context that are relevant to the feature that will be helpful to the tech lead planning work increments>
```

## Plan File

$ARGUMENTS
