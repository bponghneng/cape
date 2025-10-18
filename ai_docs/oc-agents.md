---
scraped_url: "https://opencode.ai/docs/agents/"
scraped_date: "2025-10-13"
---

# Agents

Configure and use specialized agents.

Agents are specialized AI assistants that can be configured for specific tasks and workflows. They allow you to create focused tools with custom prompts, models, and tool access.

You can switch between agents during a session or invoke them with the `@` mention.

---

## Types

There are two types of agents in OpenCode; primary agents and subagents.

### Primary agents

Primary agents are the main assistants you interact with directly. You can cycle through them using the **Tab** key, or your configured `switch_agent` keybind. These agents handle your main conversation and can access all configured tools.

OpenCode comes with two built-in primary agents, **Build** and **Plan**.

### Subagents

Subagents are specialized assistants that primary agents can invoke for specific tasks. You can also manually invoke them by **@ mentioning** them in your messages.

OpenCode comes with one built-in subagent, **General**.

---

## Built-in

OpenCode comes with two built-in primary agents and one built-in subagent.

### Build

_Mode_: `primary`

Build is the **default** primary agent with all tools enabled. This is the standard agent for development work where you need full access to file operations and system commands.

### Plan

_Mode_: `primary`

A restricted agent designed for planning and analysis. We use a permission system to give you more control and prevent unintended changes. By default, all of the following are set to `ask`:

- `file edits`: All writes, patches, and edits
- `bash`: All bash commands

This agent is useful when you want the LLM to analyze code, suggest changes, or create plans without making any actual modifications to your codebase.

### General

_Mode_: `subagent`

A general-purpose agent for researching complex questions, searching for code, and executing multi-step tasks. Use when searching for keywords or files and you’re not confident you’ll find the right match in the first few tries.

---

## Usage

1. For primary agents, use the **Tab** key to cycle through them during a session. You can also use your configured `switch_agent` keybind.
2. Subagents can be invoked automatically by primary agents for specialized tasks or manually by **@ mentioning** a subagent in your message.
3. Navigate between parent and child sessions using **Ctrl+Right** and **Ctrl+Left** (or your configured keybinds).

---

## Configure

You can customize the built-in agents or create your own through configuration. Agents can be configured in two ways:

### JSON

Configure agents in your `opencode.json` config file:

```
```

### Markdown

You can also define agents using markdown files. Place them in:

- Global: `~/.config/opencode/agent/`
- Per-project: `.opencode/agent/`

```
```

The markdown file name becomes the agent name. For example, `review.md` creates a `review` agent.

---

## Options

Let’s look at these configuration options in detail.

### Description

Use the `description` option to provide a brief description of what the agent does and when to use it.

```
```

This is a **required** config option.

### Temperature

Control the randomness and creativity of the LLM’s responses with the `temperature` config.

Lower values make responses more focused and deterministic, while higher values increase creativity and variability.

```
```

If no temperature is specified, OpenCode uses model-specific defaults.

### Disable

Set to `true` to disable the agent.

```
```

### Prompt

Specify a custom system prompt file for this agent with the `prompt` config.

```
```

This path is relative to where the config file is located.

### Model

Use the `model` config to override the default model for this agent.

```
```

### Tools

Control which tools are available in this agent with the `tools` config. You can enable or disable specific tools by setting them to `true` or `false`.

```
```

You can also use wildcards to control multiple tools at once.

### Permissions

Configure permissions to manage what actions an agent can take. Set `edit`, `bash`, and `webfetch` tools to `ask`, `allow`, or `deny`.

```
```

You can override these permissions per agent and set permissions for specific bash commands.

### Mode

Control the agent’s mode with the `mode` config. Set it to `primary`, `subagent`, or `all`. Defaults to `all` if unspecified.

### Additional

Any other options you specify in your agent configuration will be passed through directly to the provider as model options.

---

## Create agents

You can create new agents using the following command:

```
```

This interactive command will ask where to save the agent, gather details, and create a markdown file with the configuration.

---

## Use cases

Here are some common use cases for different agents.

- **Build agent**: Full development work with all tools enabled
- **Plan agent**: Analysis and planning without making changes
- **Review agent**: Code review with read-only access plus documentation tools
- **Debug agent**: Focused on investigation with bash and read tools enabled
- **Docs agent**: Documentation writing with file operations but no system commands

---

## Examples

Here are some example agents you might find useful.

### Documentation agent

```
```

### Security auditor

```
```
