---
description: OpenCode Custom Slash Commands documentation
template: |
  # OpenCode Custom Slash Commands

  This directory contains custom slash command files for [OpenCode](https://opencode.ai). These markdown files define reusable workflows and prompts that can be invoked in OpenCode using the `/` command.

  ## What are Custom Slash Commands?

  Custom slash commands in OpenCode are markdown files with YAML frontmatter that define:
  - A description of what the command does
  - Optional tools and allowed tools
  - The prompt/instructions to execute in the template field
  - Arguments placeholder (`$ARGUMENTS`)

  ## File Format

  ```markdown
  ---
  description: Brief description of what this command does
  tools: Task  # Optional: specifies available tools
  allowed-tools: Bash, Read  # Optional: restricts tool usage
  template: |
    # Command Title

    Your command instructions here...

    ## Arguments
    $ARGUMENTS
  ---
  ```

  ## Key Differences from Claude Code

  - OpenCode uses `template` field instead of putting content directly in the file
  - The content should be moved into the `template` field as a multi-line string
  - Tool specifications may differ between platforms
  - All functionality remains the same (arguments, shell commands, file references)

  ## Notes

  - The `template` field contains the command instructions as a multi-line string
  - Consider breaking complex multi-argument workflows into separate, focused commands
  - Tool permissions and availability may vary between Claude Code and OpenCode
---