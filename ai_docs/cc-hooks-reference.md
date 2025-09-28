---
scraped_url: "https://docs.claude.com/en/docs/claude-code/hooks"
scraped_date: "2025-09-27"
---

# Claude Code Hooks Reference

For a quickstart guide with examples, see [Get started with Claude Code hooks](https://docs.claude.com/en/docs/claude-code/hooks-guide).

## Configuration

Claude Code hooks are configured in your [settings files](https://docs.claude.com/en/docs/claude-code/settings):

- `~/.claude/settings.json` - User settings
- `.claude/settings.json` - Project settings
- `.claude/settings.local.json` - Local project settings (not committed)
- Enterprise managed policy settings

### Structure

Hooks are organized by matchers, where each matcher can have multiple hooks:

```json
{
  "hooks": {
    "EventName": [
      {
        "matcher": "ToolPattern",
        "hooks": [
          {
            "type": "command",
            "command": "your-command-here"
          }
        ]
      }
    ]
  }
}
```

- **matcher**: Pattern to match tool names, case-sensitive (only applicable for `PreToolUse` and `PostToolUse`)
  - Simple strings match exactly: `Write` matches only the Write tool
  - Supports regex: `Edit|Write` or `Notebook.*`
  - Use `*` to match all tools. You can also use empty string (`""`) or leave `matcher` blank.
- **hooks**: Array of commands to execute when the pattern matches
  - `type`: Currently only `"command"` is supported
  - `command`: The bash command to execute (can use `$CLAUDE_PROJECT_DIR` environment variable)
  - `timeout`: (Optional) How long a command should run, in seconds, before canceling that specific command.

For events like `UserPromptSubmit`, `Notification`, `Stop`, and `SubagentStop` that don't use matchers, you can omit the matcher field:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/prompt-validator.py"
          }
        ]
      }
    ]
  }
}
```

### Project-Specific Hook Scripts

You can use the environment variable `CLAUDE_PROJECT_DIR` (only available when Claude Code spawns the hook command) to reference scripts stored in your project, ensuring they work regardless of Claude's current directory:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/check-style.sh"
          }
        ]
      }
    ]
  }
}
```

## Hook Events

### PreToolUse

Runs after Claude creates tool parameters and before processing the tool call.

**Common matchers:**
- `Task` - Subagent tasks (see [subagents documentation](https://docs.claude.com/en/docs/claude-code/sub-agents))
- `Bash` - Shell commands
- `Glob` - File pattern matching
- `Grep` - Content search
- `Read` - File reading
- `Edit`, `MultiEdit` - File editing
- `Write` - File writing
- `WebFetch`, `WebSearch` - Web operations

### PostToolUse

Runs immediately after a tool completes successfully.
Recognizes the same matcher values as PreToolUse.

### Notification

Runs when Claude Code sends notifications. Notifications are sent when:

1. Claude needs your permission to use a tool. Example: "Claude needs your permission to use Bash"
2. The prompt input has been idle for at least 60 seconds. "Claude is waiting for your input"

### UserPromptSubmit

Runs when the user submits a prompt, before Claude processes it. This allows you to add additional context based on the prompt/conversation, validate prompts, or block certain types of prompts.

### Stop

Runs when the user stops Claude (Ctrl+C or stop button).

### SubagentStop

Runs when a subagent stops (either completed or stopped by user).

### PreCompact

Runs before Claude compacts the conversation history to manage context limits.

### SessionStart

Runs when a new Claude Code session begins.

### SessionEnd

Runs when a Claude Code session ends.

## Hook Input

All hooks receive JSON input via stdin with event-specific data.

### PreToolUse Input

```json
{
  "event": "PreToolUse",
  "tool": "Write",
  "parameters": {
    "path": "/path/to/file.py",
    "content": "print('hello')"
  },
  "projectDir": "/path/to/project"
}
```

### PostToolUse Input

```json
{
  "event": "PostToolUse",
  "tool": "Write",
  "parameters": {
    "path": "/path/to/file.py",
    "content": "print('hello')"
  },
  "result": "File written successfully",
  "projectDir": "/path/to/project"
}
```

### Notification Input

```json
{
  "event": "Notification",
  "message": "Claude needs your permission to use Bash",
  "projectDir": "/path/to/project"
}
```

### UserPromptSubmit Input

```json
{
  "event": "UserPromptSubmit",
  "prompt": "Write a hello world script",
  "conversationHistory": [...],
  "projectDir": "/path/to/project"
}
```

### Stop and SubagentStop Input

```json
{
  "event": "Stop",
  "projectDir": "/path/to/project"
}
```

### PreCompact Input

```json
{
  "event": "PreCompact",
  "conversationHistory": [...],
  "projectDir": "/path/to/project"
}
```

### SessionStart Input

```json
{
  "event": "SessionStart",
  "projectDir": "/path/to/project"
}
```

### SessionEnd Input

```json
{
  "event": "SessionEnd",
  "projectDir": "/path/to/project"
}
```

## Hook Output

Hooks can control Claude's behavior through exit codes or JSON output.

### Simple: Exit Code

- **Exit code 0**: Continue normally
- **Exit code 1**: Log error and continue
- **Exit code 2**: Block the action (PreToolUse, UserPromptSubmit, Stop, SubagentStop)

#### Exit Code 2 Behavior

- **PreToolUse**: Prevents tool execution
- **UserPromptSubmit**: Blocks prompt processing
- **Stop/SubagentStop**: Prevents stopping (user can force with second attempt)
- **Other events**: No special behavior (treated as error)

### Advanced: JSON Output

For more control, hooks can output JSON to stdout:

```json
{
  "decision": "allow|block|approve",
  "message": "Optional message to display",
  "context": "Additional context for Claude",
  "notification": "Message to show user"
}
```

#### Common JSON Fields

- **decision**: Controls the action (`allow`, `block`, `approve`)
- **message**: Displayed to user in transcript
- **context**: Added to Claude's context (UserPromptSubmit, SessionStart only)
- **notification**: Shows notification to user

#### PreToolUse Decision Control

- **allow**: Execute tool normally
- **block**: Prevent tool execution
- **approve**: Execute tool with user approval prompt

#### PostToolUse Decision Control

- **allow**: Continue normally (default)
- **block**: Not applicable (tool already executed)

#### UserPromptSubmit Decision Control

- **allow**: Process prompt normally
- **block**: Reject prompt submission
- **context**: Add information to Claude's context

#### Stop/SubagentStop Decision Control

- **allow**: Allow stopping
- **block**: Prevent stopping (user can force with second attempt)

#### SessionStart Decision Control

- **allow**: Continue session start
- **context**: Add information to Claude's initial context

#### SessionEnd Decision Control

- **allow**: Continue session end (default behavior)

## Examples

### Exit Code Example: Bash Command Validation

```bash
#!/bin/bash
# Prevent dangerous bash commands

input=$(cat)
command=$(echo "$input" | jq -r '.parameters.command // empty')

# Block dangerous commands
if echo "$command" | grep -E "(rm -rf|sudo|format)" > /dev/null; then
    echo "Dangerous command blocked: $command" >&2
    exit 2
fi

exit 0
```

### JSON Output Example: UserPromptSubmit to Add Context and Validation

```python
#!/usr/bin/env python3
import json
import sys

# Read hook input
input_data = json.load(sys.stdin)
prompt = input_data.get('prompt', '')

# Add project context
context = f"Current project: {input_data.get('projectDir', 'unknown')}"

# Block prompts containing sensitive keywords
if any(word in prompt.lower() for word in ['password', 'secret', 'key']):
    output = {
        "decision": "block",
        "message": "Prompt contains sensitive information",
        "notification": "Please avoid including sensitive data in prompts"
    }
else:
    output = {
        "decision": "allow",
        "context": context
    }

print(json.dumps(output))
```

### JSON Output Example: PreToolUse with Approval

```python
#!/usr/bin/env python3
import json
import sys

input_data = json.load(sys.stdin)
tool = input_data.get('tool')
params = input_data.get('parameters', {})

# Require approval for file operations in sensitive directories
path = params.get('path', '')
if '/etc/' in path or '/usr/' in path:
    output = {
        "decision": "approve",
        "message": f"Requesting approval for {tool} on system path: {path}"
    }
else:
    output = {"decision": "allow"}

print(json.dumps(output))
```

## Working with MCP Tools

### MCP Tool Naming

MCP (Model Context Protocol) tools are prefixed with their server name:
- `mcp_server_name_tool_name` format
- Example: `mcp_filesystem_read_file`

### Configuring Hooks for MCP Tools

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "mcp_filesystem_.*",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/filesystem-guard.sh"
          }
        ]
      }
    ]
  }
}
```

## Security Considerations

### Disclaimer

**USE AT YOUR OWN RISK**: Claude Code hooks execute arbitrary shell commands on your system automatically. By using hooks, you acknowledge that:

- You are solely responsible for the commands you configure
- Hooks can modify, delete, or access any files your user account can access
- Malicious or poorly written hooks can cause data loss or system damage
- Anthropic provides no warranty and assumes no liability for any damages resulting from hook usage
- You should thoroughly test hooks in a safe environment before production use

Always review and understand any hook commands before adding them to your configuration.

### Security Best Practices

Here are some key practices for writing more secure hooks:

1. **Validate and sanitize inputs** - Never trust input data blindly
2. **Always quote shell variables** - Use `"$VAR"` not `$VAR`
3. **Block path traversal** - Check for `..` in file paths
4. **Use absolute paths** - Specify full paths for scripts (use "$CLAUDE_PROJECT_DIR" for the project path)
5. **Skip sensitive files** - Avoid `.env`, `.git/`, keys, etc.

### Configuration Safety

Direct edits to hooks in settings files don't take effect immediately. Claude Code:

1. Captures a snapshot of hooks at startup
2. Uses this snapshot throughout the session
3. Warns if hooks are modified externally
4. Requires review in `/hooks` menu for changes to apply

This prevents malicious hook modifications from affecting your current session.

## Hook Execution Details

- **Timeout**: 60-second execution limit by default, configurable per command.
  - A timeout for an individual command does not affect the other commands.
- **Parallelization**: All matching hooks run in parallel
- **Deduplication**: Multiple identical hook commands are deduplicated automatically
- **Environment**: Runs in current directory with Claude Code's environment
  - The `CLAUDE_PROJECT_DIR` environment variable is available and contains the absolute path to the project root directory (where Claude Code was started)
- **Input**: JSON via stdin
- **Output**:
  - PreToolUse/PostToolUse/Stop/SubagentStop: Progress shown in transcript (Ctrl-R)
  - Notification/SessionEnd: Logged to debug only (`--debug`)
  - UserPromptSubmit/SessionStart: stdout added as context for Claude

## Debugging

### Basic Troubleshooting

If your hooks aren't working:

1. **Check configuration** - Run `/hooks` to see if your hook is registered
2. **Verify syntax** - Ensure your JSON settings are valid
3. **Test commands** - Run hook commands manually first
4. **Check permissions** - Make sure scripts are executable
5. **Review logs** - Use `claude --debug` to see hook execution details

Common issues:
- **Quotes not escaped** - Use `\"` inside JSON strings
- **Wrong matcher** - Check tool names match exactly (case-sensitive)
- **Command not found** - Use full paths for scripts

### Advanced Debugging

For complex hook issues:

1. **Inspect hook execution** - Use `claude --debug` to see detailed hook execution
2. **Validate JSON schemas** - Test hook input/output with external tools
3. **Check environment variables** - Verify Claude Code's environment is correct
4. **Test edge cases** - Try hooks with unusual file paths or inputs
5. **Monitor system resources** - Check for resource exhaustion during hook execution
6. **Use structured logging** - Implement logging in your hook scripts

### Debug Output Example

Use `claude --debug` to see hook execution details:

```
[DEBUG] Executing hooks for PostToolUse:Write
[DEBUG] Getting matching hook commands for PostToolUse with query: Write
[DEBUG] Found 1 hook matchers in settings
[DEBUG] Matched 1 hooks for query "Write"
[DEBUG] Found 1 hook commands to execute
[DEBUG] Executing hook command: <Your command> with timeout 60000ms
[DEBUG] Hook command completed with status 0: <Your stdout>
```

Progress messages appear in transcript mode (Ctrl-R) showing:
- Which hook is running
- Command being executed
- Success/failure status
- Output or error messages
