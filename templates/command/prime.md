---
description: Read codebase context and build foundational knowledge
tools: Task
---

# /prime - Build Base Knowledge for AI Coders

Use the **general-purpose** agent to execute the `Discover`, `Analyze`, and
`Synthesize` sections.

## Task Instructions for Subagent

Execute comprehensive codebase analysis with the following sections:

### Discover

1. Run `git ls-files` to see all tracked files
2. List project root directory structure with `LS`
3. Find and read key configuration files (package.json, requirements.txt, etc.)
4. Locate README.md and documentation files

### Analyze

1. Read README.md and main documentation
2. Search for project entry points and main modules
3. Identify technology stack and dependencies
4. Find agents configuration files and workflow documentation
5. Search for coding standards, conventions, and patterns

### Synthesize

Create comprehensive understanding of:

- Project architecture and structure
- Technology stack and dependencies
- Development workflow and standards
- Key components and their relationships

## Report Back

The subagent should provide a complete summary of project structure, technology stack,
workflow rules, and development patterns to establish foundational knowledge for
effective coding assistance.
