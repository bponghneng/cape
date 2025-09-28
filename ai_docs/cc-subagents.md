---
scraped_url: "https://docs.anthropic.com/en/docs/claude-code/sub-agents"
scraped_date: "2025-09-27"
---

# Claude Code Subagents

Custom subagents in Claude Code are specialized AI assistants that can be invoked to handle specific types of tasks. They enable more efficient problem-solving by providing task-specific configurations with customized system prompts, tools and a separate context window.

## What are Subagents?

Subagents are pre-configured AI personalities that Claude Code can delegate tasks to. Each subagent:

- Has a specific purpose and expertise area
- Uses its own context window separate from the main conversation
- Can be configured with specific tools it's allowed to use
- Includes a custom system prompt that guides its behavior

When Claude Code encounters a task that matches a subagent's expertise, it can delegate that task to the specialized subagent, which works independently and returns results.

## Key Benefits

### Context Preservation

Each subagent operates in its own context, preventing pollution of the main conversation and keeping it focused on high-level objectives.

### Specialized Expertise

Subagents can be fine-tuned with detailed instructions for specific domains, leading to higher success rates on designated tasks.

### Reusability

Once created, subagents can be used across different projects and shared with your team for consistent workflows.

### Flexible Permissions

Each subagent can have different tool access levels, allowing you to limit powerful tools to specific subagent types.

## Quick Start

To create your first subagent:

### 1. Open the subagents interface

Run the following command:

```
/agents
```

### 2. Select 'Create New Agent'

Choose whether to create a project-level or user-level subagent

### 3. Define the subagent

- **Recommended**: Generate with Claude first, then customize to make it yours
- Describe your subagent in detail and when it should be used
- Select the tools you want to grant access to (or leave blank to inherit all tools)
- The interface shows all available tools, making selection easy
- If you're generating with Claude, you can also edit the system prompt in your own editor by pressing `e`

### 4. Save and use

Your subagent is now available! Claude will use it automatically when appropriate, or you can invoke it explicitly:

```
> Use the code-reviewer subagent to check my recent changes
```

## Subagent Configuration

### File Locations

Subagents are stored as Markdown files with YAML frontmatter in two possible locations:

| Type | Location | Scope | Priority |
| --- | --- | --- | --- |
| **Project subagents** | `.claude/agents/` | Available in current project | Highest |
| **User subagents** | `~/.claude/agents/` | Available across all projects | Lower |

When subagent names conflict, project-level subagents take precedence over user-level subagents.

### File Format

Each subagent is defined in a Markdown file with this structure:

```markdown
---
name: your-sub-agent-name
description: Description of when this subagent should be invoked
tools: tool1, tool2, tool3  # Optional - inherits all tools if omitted
model: sonnet  # Optional - specify model alias or 'inherit'
---

Your subagent's system prompt goes here. This can be multiple paragraphs
and should clearly define the subagent's role, capabilities, and approach
to solving problems.

Include specific instructions, best practices, and any constraints
the subagent should follow.
```

#### Configuration Fields

| Field | Required | Description |
| --- | --- | --- |
| `name` | Yes | Unique identifier using lowercase letters and hyphens |
| `description` | Yes | Natural language description of the subagent's purpose |
| `tools` | No | Comma-separated list of specific tools. If omitted, inherits all tools from the main thread |
| `model` | No | Model to use for this subagent. Can be a model alias (`sonnet`, `opus`, `haiku`) or `'inherit'` to use the main conversation's model. If omitted, defaults to the [configured subagent model](https://docs.claude.com/en/docs/claude-code/model-config) |

### Model Selection

The `model` field allows you to control which [AI model](https://docs.claude.com/en/docs/claude-code/model-config) the subagent uses:

- **Model alias**: Use one of the available aliases: `sonnet`, `opus`, or `haiku`
- **`'inherit'`**: Use the same model as the main conversation (useful for consistency)
- **Omitted**: If not specified, uses the default model configured for subagents (`sonnet`)

Using `'inherit'` is particularly useful when you want your subagents to adapt to the model choice of the main conversation, ensuring consistent capabilities and response style throughout your session.

### Available Tools

Subagents can be granted access to any of Claude Code's internal tools. See the [tools documentation](https://docs.claude.com/en/docs/claude-code/settings#tools-available-to-claude) for a complete list of available tools.

**Recommended:** Use the `/agents` command to modify tool access - it provides an interactive interface that lists all available tools, including any connected MCP server tools, making it easier to select the ones you need.

You have two options for configuring tools:

- **Omit the `tools` field** to inherit all tools from the main thread (default), including MCP tools
- **Specify individual tools** as a comma-separated list for more granular control (can be edited manually or via `/agents`)

**MCP Tools**: Subagents can access MCP tools from configured MCP servers. When the `tools` field is omitted, subagents inherit all MCP tools available to the main thread.

## Managing Subagents

### Using the /agents Command (Recommended)

The `/agents` command provides a comprehensive interface for subagent management:

- **List all subagents**: View existing project and user subagents
- **Create new subagents**: Interactive creation with Claude's assistance
- **Edit existing subagents**: Modify configurations and system prompts
- **Delete subagents**: Remove unused subagents
- **Tool selection**: Visual interface for selecting available tools

### Direct File Management

You can also manage subagents by directly editing the Markdown files in:
- `.claude/agents/` (project-level)
- `~/.claude/agents/` (user-level)

## Using Subagents Effectively

### Automatic Delegation

Claude Code automatically selects appropriate subagents based on the task context and the subagent's description. Make your descriptions specific and action-oriented for best results.

### Explicit Invocation

You can explicitly request a specific subagent:

```
> Use the debugger subagent to analyze this error
> Have the code-reviewer check this function
> Ask the data-scientist to analyze these metrics
```

## Example Subagents

### Code Reviewer

```markdown
---
name: code-reviewer
description: Code review specialist for pull requests, code quality, and best practices. Use proactively for any code review tasks.
tools: Read, Grep, Glob
---

You are an expert code reviewer focused on quality, maintainability, and best practices.

When reviewing code:
1. Check for correctness and logic errors
2. Evaluate code structure and organization
3. Assess adherence to coding standards
4. Look for security vulnerabilities
5. Consider performance implications
6. Review test coverage

Focus on:
- Code is clear and readable
- Functions and variables are well-named
- No duplicated code
- Proper error handling
- No exposed secrets or API keys
- Input validation implemented
- Good test coverage
- Performance considerations addressed

Provide feedback organized by priority:
- Critical issues (must fix)
- Warnings (should fix)
- Suggestions (consider improving)

Include specific examples of how to fix issues.
```

### Debugger

```markdown
---
name: debugger
description: Debugging specialist for errors, test failures, and unexpected behavior. Use proactively when encountering any issues.
tools: Read, Edit, Bash, Grep, Glob
---

You are an expert debugger specializing in root cause analysis.

When invoked:
1. Capture error message and stack trace
2. Identify reproduction steps
3. Isolate the failure location
4. Implement minimal fix
5. Verify solution works

Debugging process:
- Analyze error messages and logs
- Check recent code changes
- Form and test hypotheses
- Add strategic debug logging
- Inspect variable states

For each issue, provide:
- Root cause explanation
- Evidence supporting the diagnosis
- Specific code fix
- Testing approach
- Prevention recommendations

Focus on fixing the underlying issue, not just symptoms.
```

### Data Scientist

```markdown
---
name: data-scientist
description: Data analysis expert for SQL queries, BigQuery operations, and data insights. Use proactively for data analysis tasks and queries.
tools: Bash, Read, Write
model: sonnet
---

You are a data scientist specializing in SQL and BigQuery analysis.

When invoked:
1. Understand the data analysis requirement
2. Write efficient SQL queries
3. Use BigQuery command line tools (bq) when appropriate
4. Analyze and summarize results
5. Present findings clearly

Key practices:
- Write optimized SQL queries with proper filters
- Use appropriate aggregations and joins
- Include comments explaining complex logic
- Format results for readability
- Provide data-driven recommendations

For each analysis:
- Explain the query approach
- Document any assumptions
- Highlight key findings
- Suggest next steps based on data

Always ensure queries are efficient and cost-effective.
```

## Best Practices

- **Start with Claude-generated agents**: We highly recommend generating your initial subagent with Claude and then iterating on it to make it personally yours. This approach gives you the best results - a solid foundation that you can customize to your specific needs.
- **Design focused subagents**: Create subagents with single, clear responsibilities rather than trying to make one subagent do everything. This improves performance and makes subagents more predictable.
- **Write detailed prompts**: Include specific instructions, examples, and constraints in your system prompts. The more guidance you provide, the better the subagent will perform.
- **Limit tool access**: Only grant tools that are necessary for the subagent's purpose. This improves security and helps the subagent focus on relevant actions.
- **Version control**: Check project subagents into version control so your team can benefit from and improve them collaboratively.

## Advanced Usage

### Chaining Subagents

For complex workflows, you can chain multiple subagents:

```
> First use the code-analyzer subagent to find performance issues, then use the optimizer subagent to fix them
```

### Dynamic Subagent Selection

Claude Code intelligently selects subagents based on context. Make your `description` fields specific and action-oriented for best results.

## Performance Considerations

- **Context efficiency**: Agents help preserve main context, enabling longer overall sessions
- **Latency**: Subagents start off with a clean slate each time they are invoked and may add latency as they gather context that they require to do their job effectively.

## Related Documentation

- [Slash commands](https://docs.claude.com/en/docs/claude-code/slash-commands) - Learn about other built-in commands
- [Settings](https://docs.claude.com/en/docs/claude-code/settings) - Configure Claude Code behavior
- [Hooks](https://docs.claude.com/en/docs/claude-code/hooks) - Automate workflows with event handlers
