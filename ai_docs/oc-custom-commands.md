---
scraped_url: "https://opencode.ai/docs/commands/"
scraped_date: "2025-10-13"
---

# Commands

Create custom commands for repetitive tasks.

Custom commands let you specify a prompt you want to run when that command is executed in the TUI.

Custom commands are in addition to the built-in commands like `/init`, `/undo`, `/redo`, `/share`, `/help`. [Learn more](https://opencode.ai/docs/tui#commands).

---

## Create command files

Create markdown files in the `command/` directory to define custom commands.

Create `.opencode/command/test.md`:

```
```

The frontmatter defines command properties. The content becomes the template.

Use the command by typing `/` followed by the command name.

```
```

---

## Configure

You can add custom commands through the OpenCode config or by creating markdown files in the `command/` directory.

### JSON

Use the `command` option in your OpenCode [config](https://opencode.ai/docs/config):

```
```

Now you can run this command in the TUI:

```
```

### Markdown

You can also define commands using markdown files. Place them in:

- Global: `~/.config/opencode/command/`
- Per-project: `.opencode/command/`

```
```

The markdown file name becomes the command name. For example, `test.md` lets you run:

```
```

---

## Prompt config

The prompts for the custom commands support several special placeholders and syntax.

### Arguments

Pass arguments to commands using the `$ARGUMENTS` placeholder.

```
```

Run the command with arguments:

```
```

And `$ARGUMENTS` will be replaced with `Button`.

### Shell output

Use _! `command`_ to inject [bash command](https://opencode.ai/docs/tui#bash-commands) output into your prompt.

For example, to create a custom command that analyzes test coverage:

```
```

Or to review recent changes:

```
```

Commands run in your project’s root directory and their output becomes part of the prompt.

### File references

Include files in your command using `@` followed by the filename.

```
```

The file content gets included in the prompt automatically.

---

## Options

Let’s look at the configuration options in detail.

### Template

The `template` option defines the prompt that will be sent to the LLM when the command is executed.

```
```

This is a **required** config option.

### Description

Use the `description` option to provide a brief description of what the command does.

```
```

This is shown as the description in the TUI when you type in the command.

### Agent

Use the `agent` config to optionally specify which [agent](https://opencode.ai/docs/agents) should execute this command. If this is a [subagent](https://opencode.ai/docs/agents/#subagents) the command will trigger a subagent invocation by default. To disable this behavior, set `subtask` to `false`.

```
```

This is an **optional** config option. If not specified, defaults to your current agent.

### Subtask

Use the `subtask` boolean to force the command to trigger a [subagent](https://opencode.ai/docs/agents/#subagents) invocation. This useful if you want the command to not pollute your primary context.

```
```

This is an **optional** config option.

### Model

Use the `model` config to override the default model for this command.

```
```

This is an **optional** config option.

---

## Built-in

opencode includes several built-in commands like `/init`, `/undo`, `/redo`, `/share`, `/help`; [learn more](https://opencode.ai/docs/tui#commands).

If you define a custom command with the same name, it will override the built-in command.
