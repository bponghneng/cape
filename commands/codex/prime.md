---
description: Read codebase context and build foundational knowledge
---

# Prime Foundational Knowledge

Quickly gather project context and return a concise summary.

## Instructions

- Read README.md and AGENTS.md
- Run the following commands:
  - `ls -1` (*nix shell) or `ls | % Name` (PowerShell)
  - `git ls-files | head -50`
- Constraints:
  - Minimize reading source code files
  - Minimize searching for patterns across the codebase
  - Minimize analysis of code relationships or architecture
  - Use directory structure and config files to infer organization
  - Keep the summary concise and actionable
  - Focus on information needed to start working effectively
- Output a **concise structured summary** under 200 words covering:
  - Project overview
  - Technology stack
  - Code organization
  - Development context, including coding and workflow conventions