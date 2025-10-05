# Claude Code Custom Slash Commands

This directory contains custom slash command files for [Claude Code](https://claude.ai/download). These markdown files define reusable workflows and prompts that can be invoked in Claude Code using the `/` command.

## What are Custom Slash Commands?

Custom slash commands in Claude Code are markdown files with YAML frontmatter that define:
- A description of what the command does
- Optional thinking mode flag (`thinking: true`)
- The prompt/instructions to execute
- Arguments placeholder (`$ARGUMENTS`)

## File Format

```markdown
---
description: Brief description of what this command does
thinking: true  # Optional: enables reasoning model
---

# Command Title

Your command instructions here...

## Arguments
$ARGUMENTS
```

## Notes

- The `thinking: true` flag in Claude Code enables the reasoning model, which is not directly portable to Warp
- Consider breaking complex multi-argument workflows into separate, focused commands
