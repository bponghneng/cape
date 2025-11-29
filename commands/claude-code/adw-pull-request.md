---
allowed-tools: Bash(git add:*), Bash(git branch:*), Bash(git commit:*), Bash(git diff:*), Bash(git log:*), Bash(git status:*)
description: Compose conventional commits from repo changes and prepare a pull request summary
thinking: true
---

# Compose Commits & PR Summary

Follow the `Instructions` and `Commit Process` to create conventional commits for the repositories described in `README.md`, then respond with the exact `Output Format`.

## Instructions

- Read `README.md` to identify the repository or repositories to process, and process each in turn
- Use `cd` to change to the repo directory if needed
- Read current git status: `git status`
- Read current git diff (staged and unstaged changes): `git diff HEAD`
- Read current branch: `git branch --show-current`
- Read recent commits: `git log --oneline -10`
- Read @ai_docs/conventional-commits.md to follow the conventional commits standard

## Commit Process

### 1. Group Changes
Logically group related changes into commit units. Consider:
- Functional boundaries (each commit is a complete logical change)
- File relationships (related files usually go together)
- Change types (avoid mixing unrelated features, fixes, or chores)
- Include both staged and unstaged changes; re-stage files as needed to match logical commit groups

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

### 4. Prepare Pull Request Summary
After creating the commits:
- Generate a clear pull request title summarizing the overall change
- Write a concise pull request summary describing the scope and intent
- Ensure the title and summary reflect all commits you created

## Edge Cases

- If changes span multiple unrelated features, create separate commits

## Output Format

Return ONLY valid JSON with zero additional text, formatting, markdown, or explanation. Your entire reply must be a single JSON object matching this structure:

{"output":"pull-request","title":"<pull request title>","summary":"<pull request summary>","commits":[{"message":"<full conventional commit message>","sha":"<commit SHA identifier>","files":["repo/relative/path1","repo/relative/path2"]}]}

Rules:
- Respond exclusively with JSON in the format above
- `output` must be "pull-request"
- `title` is a concise pull request title summarizing all commits
- `summary` is a short pull request summary describing the overall scope and intent
- `commits` is an array with one entry per commit you created
- `message` is the full conventional commit message
- `sha` may be any commit SHA that uniquely identifies the commit (full or abbreviated)
- `files` is an array of repository-relative file paths included in that commit
- Do NOT include code fences, line breaks outside the JSON structure, or extra commentary
- If no commits are created, return an empty `commits` array and use a suitable `title` and `summary` explaining that no changes were committed
