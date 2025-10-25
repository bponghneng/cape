# CAPE: Coordinated Agent Planning & Execution

## What is CAPE?

CAPE started as an extensive conversation with Claude Code about developing multi-agent workflows for complex brownfield codebases. Claude Code suggested the backronym name, which is laughably overblown for my actual intentions. As someone who counts himself as attitudinally Generation X, I kept the name with amusement at the irony I detected in this corporate-speak.

_A comprehensive development methodology for complex feature implementation with agent coordination and human oversight._ Despite the highly over-engineered process language, I've found the methodology and workflow documents genuinely handy as context when working with Claude Code to build agents and commands.

The repo has evolved sensibly to satisfy smaller-scale ambitions: a collection of assets I can source for configuring and running AI coder tools. CAPE provides reusable components—agent definitions, command templates, and documentation patterns—that enhance workflow flexibility without imposing rigid process constraints. As Claude says.

## Quick Start

1. **Browse:** [Agent Definitions](./agents/) for specialized AI assistants
2. **Use:** [Command Templates](./templates/) for common development tasks
3. **Reference:** [Context Engineering Knowledge Base](./ai_docs/) - curated documentation for AI coding tools
4. **Adapt:** Components to your preferred AI coding workflow
5. **Setup:** Use the symlinking script to integrate assets into your AI tool configurations

## Repository Contents

```
cape/
├── agents/                   # Specialized AI agent definitions
│   ├── claude-code/          # Claude Code subagents
│   └── opencode/             # OpenCode agent definitions
├── ai_docs/                  # AI coding assistant documentation
├── commands/                 # Command templates for AI tools
│   ├── claude-code/          # Commands for Claude Code
│   ├── opencode/             # Commands for OpenCode
│   └── roo/                  # Commands for Roo
├── hooks/                    # Scripts for lifecycle hooks
│   └── claude-code/          # Hooks for Claude Code
├── methodology/              # Original workflow documentation
├── migrations/               # Database migration scripts
├── scripts/                  # Utility scripts
├── specs/                    # Specifications for new features
├── templates/                # Reusable templates
└── workflows/                # Automated workflow scripts
```

## Available Assets

### Agent Definitions

Pre-configured AI assistants for specific development tasks:

- **Architects:** System design and planning specialists
- **Engineers:** Language-specific implementation experts
- **Reviewers:** Code quality and best practices validators
- **Testers:** Quality assurance and validation specialists

### Command Templates

Reusable prompts and instructions for common workflows:

- **Strategy Planning:** High-level approach development
- **Phase Specification:** Detailed implementation planning
- **Quality Gates:** Validation and review processes

### Context Engineering Knowledge Base

Curated reference materials for AI coding tools:

- Claude Code features and configuration
- Tool-specific guides and tutorials
- API documentation and examples

---

## Evolution

- **v3.0** (2025-10-25): Add support for scripted workflows with Supabase integration
- **v2.0** (2025-09-27): Pivot to flexible tooling approach
- **v1.x** (2025-09): Original structured methodology approach

---

_CAPE provides reusable AI coding assets without imposing rigid workflow constraints._
