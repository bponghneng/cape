---
description: Read codebase context and build foundational knowledge
tools: Task
---

# /prime - Build Foundational Knowledge

Use the **general-purpose** agent to quickly gather project context and return a concise summary.

## Task Instructions for Subagent

You are tasked with gathering foundational project knowledge efficiently.

### Files to Read (if they exist):

- README.md
- CLAUDE.md
- package.json (or requirements.txt, go.mod, Cargo.toml, Gemfile, etc.)
- .gitignore

### Commands to Run:

- `ls -1` (root directory listing)
- `git ls-files | head -50` (sample of tracked files)

### Your Output

Provide a **concise structured summary** (under 500 words) covering:

#### 1. Project Overview (2-3 sentences)

- What it does and problem it solves
- Key features or capabilities

#### 2. Technology Stack (3-5 bullet points)

- Primary language(s) and framework(s)
- Major dependencies (list 3-5 most important)
- Build/run tooling

#### 3. Code Organization (3-5 bullet points)

- Main directories and their purposes
- Entry points (if obvious from structure)
- Key configuration files present

#### 4. Development Context (2-4 bullet points)

- Coding conventions or standards (from CLAUDE.md)
- Common workflows or commands
- Any critical setup notes

### Constraints:

- Minimize reading source code files
- Minimize searching for patterns across the codebase
- Minimize analysis of code relationships or architecture
- Use directory structure and config files to infer organization
- Keep the summary concise and actionable
- Focus on information needed to start working effectively

---
