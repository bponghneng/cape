---
agent: [reviewer agent name]
description: Command to perform a code review on a list of recent commits
---

# /review-commits - Perform a Code Review on a List of Recent Commits

## Usage
```
/review-commits $ARGUMENTS
```

## Arguments

- $ARGUMENTS: an integer count of the most recent commits to review, defaults to 1

# Perform Code Review

Use the [reviewer agent name] to review the last $ARGUMENTS commits.

Report back to me:
- A list of the commits included in the review, including sha and message
- **IMPORTANT:** Output the complete output from the reviewer and do not summarize