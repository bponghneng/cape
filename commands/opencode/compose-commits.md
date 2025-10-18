---
description: Compose conventional commits from unstaged changes
allowed-tools: Bash(git status:*), Bash(git diff:*), Bash(git add:*), Bash(git commit:*), Read, Grep
template: |
  ## Context

  - Current git status: !`git status`
  - Unstaged changes: !`git diff`
  - Staged changes: !`git diff --cached`
  - Current branch: !`git branch --show-current`
  - Recent commits for reference: !`git log --oneline -10`

  ## Conventional Commits Standard

  @ai_docs/conventional_commits.md

  ## Your Task

  Based on the git changes shown above, create meaningful conventional commits:

  ### 1. Group Changes
  Analyze the changes and logically group related modifications that should be committed together. Consider:
  - Functional boundaries (each commit should represent a complete logical change)
  - File relationships (related files should typically be committed together)
  - Change types (don't mix features with fixes unless tightly coupled)

  ### 2. Compose Commit Messages
  For each group, create a conventional commit message:
  - Format: `type(scope): description`
  - Types: feat, fix, docs, style, refactor, test, chore, perf, ci, build
  - Keep the first line under 72 characters
  - Use imperative mood ("Add" not "Added" or "Adds")
  - Include body text for complex changes
  - Add `BREAKING CHANGE:` footer if applicable

  ### 3. Execute Commits
  For each group:
  1. Stage the relevant files using `git add`
  2. Commit with the composed message using `git commit -m`

  ### 4. Report Results
  List all commits created with:
  - Full commit message
  - SHA hash
  - Files included

  ## Edge Cases

  - If no changes exist, report this and exit
  - If changes are already staged, unstage them before composing
  - If changes span multiple unrelated features, create separate commits
---