# AGENTS.md

This file provides guidance to AI coding agents when working with code in this repository.

## Project Overview

CAPE (Coordinated Agent Planning & Execution) is a project that began as a concept for developing multi-agent workflows for complex codebases. It has since evolved into a collection of reusable assets for AI coder tools, providing components like agent definitions, command templates, and documentation patterns to enhance workflow flexibility.

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

## CLI Commands

**⚠️ IMPORTANT: Project Repository**: The CLI project repository is `cape_cli`. All of the development commands are run from the root of the project repository.

**Package Management**: This project uses `uv` for package management. To install or update dependencies, use the `uv sync` command.

**CLI**:
- `uv run cape` - Starts the Cape Terminal User Interface (TUI).

**Code Quality Tools**:

- `pytest`: `pytest test_cape_tui.py --cov=cape_tui --cov-report=term-missing`

**Testing**:
- `pytest`: Run tests with `pytest test_cape_tui.py -v`

**Setup**: `uv sync` - Install and sync project dependencies.

## Architecture

**Current Structure**:

- `cape_tui.py`: Single-file application (~600 lines)
- `Textual framework`: Modern TUI with reactive programming

**Key Dependencies**:

- `uv`: For package management.
- `Textual`: For the TUI framework.
- `Supabase`: For the backend database and authentication.

## Testing Strategy

This project uses `pytest` for testing. Tests are located in `cape/workflows/test_cape_tui.py`. 

- **Running tests**: `pytest test_cape_tui.py -v`
- **Checking test coverage**: `pytest test_cape_tui.py --cov=cape_tui --cov-report=term-missing`
