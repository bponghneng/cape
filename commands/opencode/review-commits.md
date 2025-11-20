---
argument-hint: "[agent-name] [number-of-commits]"
description: Perform code review using specialized reviewer agent
tools: Task
---

## Usage

```bash
/review-commits elixir-code-reviewer 3        # Review last 3 commits with Elixir expert
/review-commits react-native-code-reviewer 1  # Review last commit with React Native expert
/review-commits elixir-code-reviewer          # Review last 1 commit (default)
```

## Available Reviewer Agents

- `elixir-code-reviewer` - Elixir/Phoenix/Ecto code review specialist
- `react-native-code-reviewer` - React Native/Expo/TypeScript code review specialist

## Task Instructions for Reviewer Agent

You are being invoked to perform a code review on recent commits.

### Context to Gather

1. **Commits to review**: ${2:-1} (number of recent commits)
2. Run these commands to gather context:
   - `git log -n ${2:-1} --oneline` - List of commits
   - `git show -n ${2:-1}` - Detailed changes for each commit
   - `git branch --show-current` - Current branch

### Your Task

Perform your specialized code review on the commits gathered above, following your established review process and focus areas as defined in your agent configuration.

### Output Requirements

Provide your standard structured report format:

```markdown
# Code Review Report

## Summary

[Brief overview of changes reviewed and overall assessment]

## 🚨 Critical Issues

[Security vulnerabilities, crashes, breaking changes requiring immediate attention]

## ⚠️ Code Quality Issues

### Functional Correctness

[Logic errors, type/pattern matching issues, error handling gaps]

### Style & Standards

[Style guide violations, naming conventions, formatting issues]

### Security

[Authentication, authorization, input validation, data security concerns]

### Testing

[Test patterns, quality, coverage gaps, isolation issues]

### Performance

[Performance concerns specific to your domain]

## ✅ Positive Observations

[Well-implemented patterns and good practices noted]

## 🎯 Overall Assessment

**Status: [PASS | NEEDS_WORK | MAJOR_ISSUES]**

[Brief justification and recommended next steps]
```

### Guidelines

- Apply your specialized expertise to the code changes
- Reference project conventions from AGENTS.md when relevant
- Focus on changes shown in git diff, not entire files
- Only read full files if there's a specific concern from the diff
- Keep findings actionable and specific with line numbers/code snippets
- Follow your agent's defined scope and boundaries (advisory only, no code modification)

---
