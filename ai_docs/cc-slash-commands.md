---
scraped_url: "https://docs.claude.com/en/docs/claude-code/slash-commands"
scraped_date: "2025-09-27"
---

# Claude Code Slash Commands

## Built-in Slash Commands

| Command | Purpose |
| --- | --- |
| `/add-dir` | Add additional working directories |
| `/agents` | Manage custom AI subagents for specialized tasks |
| `/bug` | Report bugs (sends conversation to Anthropic) |
| `/clear` | Clear conversation history |
| `/compact [instructions]` | Compact conversation with optional focus instructions |
| `/config` | View/modify configuration |
| `/cost` | Show token usage statistics (see [cost tracking guide](https://docs.claude.com/en/docs/claude-code/costs#using-the-cost-command) for subscription-specific details) |
| `/doctor` | Checks the health of your Claude Code installation |
| `/help` | Get usage help |
| `/hooks` | Manage hooks configuration |
| `/init` | Initialize project with CLAUDE.md guide |
| `/login` | Switch Anthropic accounts |
| `/logout` | Sign out from your Anthropic account |
| `/mcp` | Manage MCP server connections and OAuth authentication |
| `/memory` | Edit CLAUDE.md memory files |
| `/model` | Select or change the AI model |
| `/permissions` | View or update [permissions](https://docs.claude.com/en/docs/claude-code/iam#configuring-permissions) |
| `/pr_comments` | View pull request comments |
| `/review` | Request code review |
| `/status` | View account and system statuses |
| `/terminal-setup` | Install Shift+Enter key binding for newlines (iTerm2 and VSCode only) |
| `/vim` | Enter vim mode for alternating insert and command modes |

## Custom Slash Commands

Custom slash commands allow you to define frequently-used prompts as Markdown files that Claude Code can execute. Commands are organized by scope (project-specific or personal) and support namespacing through directory structures.

### Syntax

```
/<command-name> [arguments]
```

#### Parameters

| Parameter | Description |
| --- | --- |
| `<command-name>` | Name derived from the Markdown filename (without `.md` extension) |
| `[arguments]` | Optional arguments passed to the command |

### Command Types

#### Project Commands

Commands stored in your repository and shared with your team. When listed in `/help`, these commands show "(project)" after their description.

**Location**: `.claude/commands/`

In the following example, we create the `/optimize` command:

```bash
# Create a project command
mkdir -p .claude/commands
echo "Analyze this code for performance issues and suggest optimizations:" > .claude/commands/optimize.md
```

#### Personal Commands

Commands available across all your projects. When listed in `/help`, these commands show "(user)" after their description.

**Location**: `~/.claude/commands/`

In the following example, we create the `/security-review` command:

```bash
# Create a personal command
mkdir -p ~/.claude/commands
echo "Review this code for security vulnerabilities:" > ~/.claude/commands/security-review.md
```

### Features

#### Namespacing

Organize commands in subdirectories. The subdirectories are used for organization and appear in the command description, but they do not affect the command name itself. The description will show whether the command comes from the project directory (`.claude/commands`) or the user-level directory (`~/.claude/commands`), along with the subdirectory name.

Conflicts between user and project level commands are not supported. Otherwise, multiple commands with the same base file name can coexist.

For example, a file at `.claude/commands/frontend/component.md` creates the command `/component` with description showing "(project:frontend)".
Meanwhile, a file at `~/.claude/commands/component.md` creates the command `/component` with description showing "(user)".

#### Arguments

Pass dynamic values to commands using argument placeholders:

##### All arguments with `$ARGUMENTS`

The `$ARGUMENTS` placeholder captures all arguments passed to the command:

```bash
# Command definition
echo 'Fix issue #$ARGUMENTS following our coding standards' > .claude/commands/fix-issue.md

# Usage
> /fix-issue 123 high-priority
# $ARGUMENTS becomes: "123 high-priority"
```

##### Individual arguments with `$1`, `$2`, etc.

Access specific arguments individually using positional parameters (similar to shell scripts):

```bash
# Command definition
echo 'Review PR #$1 with priority $2 and assign to $3' > .claude/commands/review-pr.md

# Usage
> /review-pr 456 high alice
# $1 becomes "456", $2 becomes "high", $3 becomes "alice"
```

Use positional arguments when you need to:
- Access arguments individually in different parts of your command
- Provide defaults for missing arguments
- Build more structured commands with specific parameter roles

#### Bash Command Execution

Execute bash commands before the slash command runs using the `!` prefix. The output is included in the command context. You _must_ include `allowed-tools` with the `Bash` tool, but you can choose the specific bash commands to allow.

For example:

```markdown
---
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*)
description: Create a git commit
---

## Context

- Current git status: !`git status`
- Current git diff (staged and unstaged changes): !`git diff HEAD`
- Current branch: !`git branch --show-current`
- Recent commits: !`git log --oneline -10`

## Your Task

Create a meaningful commit message based on the changes shown above. Follow our commit message conventions:
- Use imperative mood ("Add feature" not "Added feature")
- Keep the first line under 50 characters
- Include a detailed description if needed

After creating the commit message, stage and commit the changes.
```

#### File References

Reference files in your commands using relative paths. Claude Code will automatically include the file contents:

```markdown
---
description: Review the main application file
---

Please review the following file for potential improvements:

@src/main.py

Focus on:
- Code organization
- Error handling
- Performance optimizations
```

#### Thinking Mode

Enable thinking mode for complex commands by adding `thinking: true` to the frontmatter:

```markdown
---
description: Complex analysis task
thinking: true
---

Analyze the codebase architecture and suggest improvements.
```

#### Frontmatter

Commands support YAML frontmatter for configuration:

```markdown
---
description: Brief description of what this command does
allowed-tools: Read, Write, Bash(ls:*, cat:*)
thinking: true
disable-model-invocation: false
---

Your command content here...
```

**Frontmatter options:**
- `description`: Brief description shown in `/help`
- `allowed-tools`: Restrict which tools Claude can use
- `thinking`: Enable thinking mode for complex reasoning
- `disable-model-invocation`: Prevent Claude from auto-invoking this command

## MCP Slash Commands

MCP (Model Context Protocol) servers can expose prompts as slash commands, making external tools and services accessible through Claude Code's command interface.

### Command Format

MCP slash commands follow the pattern:

```
/mcp__<server-name>__<prompt-name> [arguments]
```

### Features

#### Dynamic Discovery

MCP slash commands are automatically discovered from connected servers. No manual configuration required - just connect an MCP server and its prompts become available as slash commands.

#### Arguments

MCP commands support arguments that are passed to the underlying MCP prompt:

```bash
# Without arguments
> /mcp__github__list_prs

# With arguments
> /mcp__github__pr_review 456
> /mcp__jira__create_issue "Bug title" high
```

#### Naming Conventions

- Server and prompt names are normalized
- Spaces and special characters become underscores
- Names are lowercased for consistency

### Managing MCP Connections

Use the `/mcp` command to:
- View all configured MCP servers
- Check connection status
- Authenticate with OAuth-enabled servers
- Clear authentication tokens
- View available tools and prompts from each server

### MCP Permissions and Wildcards

When configuring [permissions for MCP tools](https://docs.claude.com/en/docs/claude-code/iam#tool-specific-permission-rules), note that **wildcards are not supported**:

- ✅ **Correct**: `mcp__github` (approves ALL tools from the github server)
- ✅ **Correct**: `mcp__github__get_issue` (approves specific tool)
- ❌ **Incorrect**: `mcp__github__*` (wildcards not supported)

To approve all tools from an MCP server, use just the server name: `mcp__servername`. To approve specific tools only, list each tool individually.

## SlashCommand Tool

The `SlashCommand` tool allows Claude to execute [custom slash commands](https://docs.claude.com/en/docs/claude-code/slash-commands#custom-slash-commands) programmatically during a conversation. This gives Claude the ability to invoke custom commands on your behalf when appropriate.

To encourage Claude to trigger `SlashCommand` tool, your instructions (prompts, CLAUDE.md, etc.) generally need to reference the command by name with its slash.

Example:

```
> Run /write-unit-test when you are about to start writing tests.
```

This tool puts each available custom slash command's metadata into context up to the character budget limit. You can use `/context` to monitor token usage and follow the operations below to manage context.

### SlashCommand Tool Supported Commands

`SlashCommand` tool only supports custom slash commands that:
- Are user-defined. Built-in commands like `/compact` and `/init` are _not_ supported.
- Have the `description` frontmatter field populated. We use the `description` in the context.

For Claude Code versions >= 1.0.124, you can see which custom slash commands `SlashCommand` tool can invoke by running `claude --debug` and triggering a query.

### Disable SlashCommand Tool

To prevent Claude from executing any slash commands via the tool:

```
/permissions
# Add to deny rules: SlashCommand
```

This will also remove SlashCommand tool (and the slash command descriptions) from context.

### Disable Specific Commands Only

To prevent a specific slash command from becoming available, add `disable-model-invocation: true` to the slash command's frontmatter.

This will also remove the command's metadata from context.

### SlashCommand Permission Rules

The permission rules support:
- **Exact match**: `SlashCommand:/commit` (allows only `/commit` with no arguments)
- **Prefix match**: `SlashCommand:/review-pr:*` (allows `/review-pr` with any arguments)

### Character Budget Limit

The `SlashCommand` tool includes a character budget to limit the size of command descriptions shown to Claude. This prevents token overflow when many commands are available.

The budget includes each custom slash command's name, args, and description.

- **Default limit**: 15,000 characters
- **Custom limit**: Set via `SLASH_COMMAND_TOOL_CHAR_BUDGET` environment variable

When the character budget is exceeded, Claude will see only a subset of the available commands. In `/context`, a warning will show with "M of N commands".

## See Also

- [Identity and Access Management](https://docs.claude.com/en/docs/claude-code/iam) - Complete guide to permissions, including MCP tool permissions
- [Interactive mode](https://docs.claude.com/en/docs/claude-code/interactive-mode) - Shortcuts, input modes, and interactive features
- [CLI reference](https://docs.claude.com/en/docs/claude-code/cli-reference) - Command-line flags and options
- [Settings](https://docs.claude.com/en/docs/claude-code/settings) - Configuration options
- [Memory management](https://docs.claude.com/en/docs/claude-code/memory) - Managing Claude's memory across sessions
