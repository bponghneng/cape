---
description: Triage a bug for immediate implementation.
---

# Triage a Bug for Immediate Implementation

Create a new plan in specs/*.md to resolve the `Bug` using the exact specified markdown `Plan Format`. Follow the `Instructions` to create the plan. Focus on `Relevant Files` listed in `README.md`.

## Instructions

- IMPORTANT: You're writing a plan to resolve a bug that will add value to the application.
- IMPORTANT: The `Bug` describes the bug that will be resolved but remember we're not resolving the bug, we're creating the plan that will be used to resolve the bug based on the `Plan Format` below.
- You're writing a plan to resolve a bug. The plan should be thorough and precise so we fix the root cause and prevent regressions.
- Create the plan in the `./specs/` directory using the following naming convention: `./specs/bug-<bug name>-plan.md`.
- Use the `Plan Format` below to create the plan.
- Research the codebase to understand the bug, reproduce it, and put together a plan to fix it.
- IMPORTANT: Replace every <placeholder> in the `Plan Format` with the requested value. Add as much detail as needed to fix the bug.
- Use your reasoning model: THINK HARD about the bug, its root cause, and the steps to fix it properly.
- IMPORTANT: Be surgical with your bug fix, solve the bug at hand and don't fall off track.
- IMPORTANT: We want the minimal number of changes that will fix and address the bug.
- Start your work by reading the `CLAUDE.md` and `README.md` files.
- Respect the `Relevant Files` listed in the `README.md`.

## Plan Format

```md
# Bug: <bug name>

## Bug Description
<describe the bug in detail, including symptoms and expected vs actual behavior>

## Problem Statement
<clearly define the specific problem that needs to be solved>

## Solution Statement
<describe the proposed solution approach to fix the bug>

## Steps to Reproduce
<list exact steps to reproduce the bug>

## Root Cause Analysis
<analyze and explain the root cause of the bug>

## Relevant Files
Use these files to fix the bug:

<find and list the files that are relevant to the bug describe why they are relevant in bullet points. If there are new files that need to be created to fix the bug, list them in an h3 'New Files' section.>

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

<list step by step tasks as h3 headers plus bullet points. use as many h3 headers as needed to fix the bug. Order matters, start with the foundational shared changes required to fix the bug then move on to the specific changes required to fix the bug. Include tests that will validate the bug is fixed with zero regressions. Your last step should be running the `Validation Commands` to validate the bug is fixed with zero regressions.>

## Validation Commands
Execute every command to validate the bug is fixed with zero regressions.

<list commands you'll use to validate with 100% confidence the bug is fixed with zero regressions. every command must execute without errors so be specific about what you want to run to validate the bug is fixed with zero regressions. Don't validate with curl commands.>
- `cd ws2-mobile` - Change directory to the root of the codebase.
- `npm run format` - Format the codebase.
- `npm run lint` - Lint the codebase.
- `npm run type-check` - Type check the codebase.
- `npm run test` - Run the test suite.
- `cd ..` - Change directory to workspace root.

## Notes
<optionally list any additional notes or context that are relevant to the bug that will be helpful to the developer>
```

## Bug
$ARGUMENTS

## Report
- Summarize the work you've just done in a concise bullet point list.
- Include a path to the plan you created in the `./specs/bug-<bug name>-plan.md` file.