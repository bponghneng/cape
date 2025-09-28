---
description: Compose conventional commits from unstaged changes
tools: Bash, Read, Grep, Glob
---

# /compose-commits - Compose conventional commits

Execute the `Learn`, `Analyze`, and `Compose` sections.

## Learn Conventional Commits Standard

Read ai_docs/conventional_commits.md to understand the conventional commits standard

## Analyze

1. Run `git status` to see all unstaged changes
2. Run `git diff` to understand what changed
3. Read modified files to understand the purpose of changes
4. Group related changes logically

## Compose

Create conventional commits following the standard:

- `type(scope): description`
- Types: feat, fix, docs, style, refactor, test, chore
- Include breaking changes notation if applicable
- Commit the changes

## Report

List of commits with complete conventional commit messages, including commit sha.
