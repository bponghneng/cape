---
agent: [reviewer agent name]
description: Perform comprehensive code review on recent commits
tools: Task, Bash, Read, Grep, Glob
---

# /review-commits - Perform Code Review on Recent Commits

Execute the `Gather`, `Review`, and `Report` sections.

## Usage

/review-commits [count]

## Arguments

- `count`: Number of recent commits to review (default: 1)

## Gather

1. Run `git log -n [count] --oneline` to get commit list
2. Run `git show` for each commit to see detailed changes
3. Read modified files to understand context
4. Identify scope and impact of changes

## Review

Use the `[reviewer agent name]` agent to perform comprehensive review:

- Code quality and best practices
- Security considerations
- Performance implications
- Testing coverage
- Documentation updates needed
- Breaking changes identification

## Report

Provide structured review output:

- List of commits reviewed (SHA + message)
- **IMPORTANT:** Complete reviewer output without summarization
- Categorized findings (critical, major, minor, suggestions)
- Action items and recommendations
