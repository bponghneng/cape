# AGENTS.md

This file provides guidance to AI coding agents when working with code in this repository.

## Project Overview

[description of project]

## Archon Integration & Workflow

**CRITICAL: This project uses Archon for knowledge management, task tracking, and project organization.**

### Core Archon Workflow Principles

#### The Golden Rule: Task-Driven Development with Archon

**MANDATORY: Always complete the full Archon task cycle before any coding:**

1. **Check Current Task** → Review task details and requirements
2. **Research for Task** → Search relevant documentation and examples
3. **Implement the Task** → Write code based on research
4. **Update Task Status** → Move task from "todo" → "doing" → "review"
5. **Get Next Task** → Check for next priority task
6. **Repeat Cycle**

**Task Management Rules:**

- Update all actions to Archon
- Move tasks from "todo" → "doing" → "review" (not directly to complete)
- Maintain task descriptions and add implementation notes
- DO NOT MAKE ASSUMPTIONS - check project documentation for questions

## Workflow Style & Collaboration Rules

### Code Changes & Investigation Workflow

- **Research First**: Investigate thoroughly before proposing solutions. Use search
  tools and documentation to gather facts rather than making assumptions.
- **Discuss Before Implementing**: Present findings and proposed approaches for
  approval before making code changes. Explain options and trade-offs.
- **Respect Original Code**: Try to understand where code came from and what problem
  it's solving before assuming it can be changed.
- **Question Assumptions**: If something doesn't work as expected, investigate the
  root cause. Look for version differences, environment issues, or missing context.

### Problem-Solving Workflow

1. **Analyze**: Read errors carefully and identify the real issue
2. **Research**: Use tools and documentation to understand the problem context
3. **Propose**: Present findings and suggest solution options with pros/cons
4. **Implement**: Only after approval, make minimal necessary changes
5. **Clean Up**: Remove temporary test files or debugging code

### Communication

- Ask clarifying questions when requirements are unclear
- Explain the "why" behind recommendations
- If blocked or uncertain, ask for guidance rather than guessing

## Simplicity-First Mindset

Your guidance is directed by these core principles:

1. **Start with MVP**: Focus on core functionality that delivers immediate value
2. **Avoid Premature Optimization**: Don't add features "just in case"
3. **Minimal Dependencies**: Only add what's absolutely necessary for requirements
4. **Clear Over Clever**: Simple, maintainable solutions over complex architectures

Apply these principles when evaluating whether complex patterns, or advanced optimizations are truly needed or if simpler solutions would suffice.

## Development Commands

**Package Management**: [description of package manager]

**Code Quality Tools**:

- `[code-quality-tool1]`: [command to run1]
- `[code-quality-tool2]`: [command to run2]

**Development Dependencies**: [command to install dependencies]

## Architecture

**Current Structure**:

- `[key-directory1]` - [description of key directory1]
- `[key-directory2]` - [description of key directory2]
- `[key-file1]` - [description of key file1]
- `[key-file2]` - [description of key file2]

**Key Dependencies**:

- `[key-dependency-name1]` - [description of key dependency1]
- `[key-dependency-name2]` - [description of key dependency2]

## Testing Strategy

[description of testing strategy]

- [description of test type, e.g., unit tests, integration tests, and usage in codebase]
