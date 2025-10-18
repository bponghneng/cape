---
scraped_url: "https://docs.roocode.com/features/slash-commands"
scraped_date: "2025-10-13"
---

# Slash Commands

Create custom slash commands to automate repetitive tasks and extend Roo Code's functionality with simple markdown files.

Type `/` in chat to select a command. To create or manage commands, open Settings > Slash Commands. You can still store commands in `.roo/commands/` (project) or `~/.roo/commands/` (global).

---

## Overview

Slash commands let you create reusable prompts and workflows that can be triggered instantly. Turn complex multi-step processes into single commands, standardize team practices, and automate repetitive tasks with simple markdown files.

**Key Benefits:**

- **Workflow Automation**: Turn complex multi-step processes into single commands
- **Team Standardization**: Share commands across your team for consistent practices
- **Context Preservation**: Include project-specific context in every command
- **Quick Access**: Fuzzy search and autocomplete for instant command discovery

---

## Creating Custom Commands

Custom commands extend Roo Code's functionality by adding markdown files to specific directories:

- Project-specific: `.roo/commands/`
- Global: `~/.roo/commands/`

The filename becomes the command name. Example mappings:

- `review.md` → `/review`
- `test-api.md` → `/test-api`
- `deploy-check.md` → `/deploy-check`

Command names created in Settings are normalized to lowercase, use dashes, and strip special characters.

### Basic Command Format

Create a simple command by adding a markdown file:

```markdown
# review.md
Please review this code for:
- Performance issues
- Security vulnerabilities
- Code style violations
- Potential bugs
```

### Advanced Command with Frontmatter

Add metadata using frontmatter for enhanced functionality:

```markdown
---
description: Comprehensive code review focusing on security and performance
argument-hint: <file or directory to review>
---

# Security-First Code Review

Please perform a thorough security review of the selected code:
- Authentication & Authorization
- Input Validation
- Security Best Practices
```

Frontmatter fields:

- `description`: Appears in the command menu to describe the command
- `argument-hint`: Optional hint for expected arguments (e.g., `<file-path>`)

---

## Command Management

Manage commands from Settings:

1. Open Settings and select Slash Commands.
2. Click **New Command**, name it, and choose location (Project or Global).
3. The command file opens with starter template content.

---

## Using Slash Commands

- Type `/` to open the command menu and choose from existing commands.
- Autocomplete narrows the list (e.g., `/sam` finds `sample-command-name`).
- Descriptions appear in the menu for quick context.
- Project commands override global commands with the same name.

---

## Argument Hints

Argument hints show what input a command expects when you select it in the menu.

Examples:

- `/mode <mode_slug>`
- `/api-endpoint <endpoint-name> <http-method>`

To add hints, include `argument-hint` in frontmatter:

```markdown
---
description: Generate a new REST API endpoint with best practices
argument-hint: <endpoint-name> <http-method>
---
```

Best practices:

- Be specific with placeholders
- Show all required arguments
- Use angle brackets for placeholders
- Keep hints concise

---

## Examples and Use Cases

**Development Workflows**

- **API Endpoint Generator**: Guides creation of REST API endpoints with error handling, validation, docs, and tests.
- **Database Migration Helper**: Generates migrations with up/down scripts, transactions, and validations.

**Code Quality**

- **Performance Analyzer**: Identifies performance bottlenecks, costly queries, memory leaks, and optimization opportunities.
- **Refactoring Assistant**: Suggests improvements for readability, structure, and testability.

**Documentation**

- **README Generator**: Produces comprehensive README content covering install, usage, API docs, and more.
- **API Documentation**: Generates OpenAPI documentation with endpoints, schemas, examples, and auth requirements.

**Testing**

- **Test Generator**: Creates unit, edge case, error handling, and integration tests with mocks where needed.
- **Test Coverage Analyzer**: Identifies untested paths, recommends test cases, and checks error handling coverage.

---

## Best Practices

**Command Naming**

- Use descriptive, action-oriented names
- Keep names concise
- Use hyphens for multi-word commands
- Avoid generic names like `help`
- Remember names are slugified automatically

**Command Content**

- Start with a clear directive
- Use structured lists and sections
- Include specific requirements and project conventions
- Keep focus on a single task

**Organization**

- Group related commands in subdirectories
- Use consistent naming patterns
- Document complex commands
- Version control command files
- Share project-level commands for team alignment

---

## Built-in Commands

Roo Code includes built-in slash commands such as `/init` that perform advanced tasks like analyzing your codebase, generating configuration files, and creating documentation.

Built-in commands cannot be overridden. Project commands take priority over global ones when names match.

---

## Troubleshooting

- **Commands Not Appearing**: Ensure files are in `.roo/commands/` or `~/.roo/commands/` and have `.md` extension; reload the window if needed.
- **Command Not Found**: Roo outputs an error indicating the correct directories.
- **Template Content**: UI-created commands include starter content for customization.
- **Command Conflicts**: Duplicate names get numbered suffixes when created through the UI.
- **File System Errors**: Check write permissions and directory existence; symbolic links are supported.

---

## See Also

- [Using Modes](https://docs.roocode.com/basic-usage/using-modes)
- [Custom Instructions](https://docs.roocode.com/features/custom-instructions)
- [Keyboard Shortcuts](https://docs.roocode.com/features/keyboard-shortcuts)
- [Task Management](https://docs.roocode.com/features/task-todo-list)
