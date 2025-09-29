---
scraped_url: "https://docs.roocode.com/basic-usage/using-modes"
scraped_date: "2025-09-27"
---

# Roo Code: Using Modes

Modes in Roo Code are specialized personas that tailor the assistant's behavior to your current task. Each mode offers different capabilities, expertise, and access levels to help you accomplish specific goals.

## Sticky Models & Mode Persistence

Each mode remembers your last-used model. When switching modes, Roo automatically selects that model—no manual selection needed. Assign different models to different modes (e.g., Gemini 2.5 Preview for `🏗️ Architect` mode, Claude Sonnet 3.7 for `💻 Code` mode) and Roo will switch models automatically when you change modes.

Additionally, your selected mode persists between sessions—Roo remembers which mode you were using when you return.

---

## Why Use Different Modes?

- **Task specialization:** Get precisely the type of assistance you need for your current task
- **Safety controls:** Prevent unintended file modifications when focusing on planning or learning
- **Focused interactions:** Receive responses optimized for your current activity
- **Workflow optimization:** Seamlessly transition between planning, implementing, debugging, and learning

---

## Switching Between Modes

Four ways to switch modes:

### 1. Dropdown Menu
Click the selector to the left of the chat input

![Using the dropdown menu to switch modes](https://docs.roocode.com/img/using-modes/using-modes.png)

### 2. Slash Command
Type `/architect`, `/ask`, `/debug`, `/code`, or `/orchestrator` at the beginning of your message. This will switch to that mode and clear the input field.

![Using slash commands to switch modes](https://docs.roocode.com/img/using-modes/using-modes-1.png)

### 3. Toggle Command/Keyboard Shortcut
Use the keyboard shortcut below, applicable to your operating system. Each press cycles through the available modes in sequence, wrapping back to the first mode after reaching the end.

| Operating System | Shortcut |
| --- | --- |
| macOS | ⌘ + . |
| Windows | Ctrl + . |
| Linux | Ctrl + . |

### 4. Accept Suggestions
Click on mode switch suggestions that Roo offers when appropriate

![Accepting a mode switch suggestion from Roo](https://docs.roocode.com/img/using-modes/using-modes-2.png)

---

## Built-in Modes

### Code Mode (Default)

| Aspect | Details |
| --- | --- |
| **Name** | `💻 Code` |
| **Description** | A skilled software engineer with expertise in programming languages, design patterns, and best practices |
| **Tool Access** | Full access to all tool groups: `read`, `edit`, `browser`, `command`, `mcp` |
| **Ideal For** | Writing code, implementing features, debugging, and general development |
| **Special Features** | No tool restrictions—full flexibility for all coding tasks |

### Ask Mode

| Aspect | Details |
| --- | --- |
| **Name** | `❓ Ask` |
| **Description** | A knowledgeable technical assistant focused on providing thorough and complete answers. It's less inclined to switch to implementing code unless explicitly requested and may use diagrams for clarification. |
| **Tool Access** | Limited access: `read`, `browser`, `mcp` only (cannot edit files or run commands) |
| **Ideal For** | Code explanation, concept exploration, and technical learning |
| **Special Features** | Optimized for detailed, informative responses, often using diagrams for clarity, without modifying your project. |

### Architect Mode

| Aspect | Details |
| --- | --- |
| **Name** | `🏗️ Architect` |
| **Description** | An experienced technical leader and planner who helps design systems and create implementation plans |
| **Tool Access** | Access to `read`, `browser`, `mcp`, and restricted `edit` (markdown files only) |
| **Ideal For** | System design, high-level planning, and architecture discussions |
| **Special Features** | Follows a structured approach from information gathering to detailed planning |

### Debug Mode

| Aspect | Details |
| --- | --- |
| **Name** | `🪲 Debug` |
| **Description** | An expert problem solver specializing in systematic troubleshooting and diagnostics |
| **Tool Access** | Full access to all tool groups: `read`, `edit`, `browser`, `command`, `mcp` |
| **Ideal For** | Tracking down bugs, diagnosing errors, and resolving complex issues |
| **Special Features** | Uses a methodical approach of analyzing, narrowing possibilities, and fixing issues. Includes custom instructions to reflect, distill possibilities, add logs, and confirm before fixing. |

### Orchestrator Mode (aka Boomerang Mode)

| Aspect | Details |
| --- | --- |
| **Name** | `🪃 Orchestrator` |
| **Description** | A strategic workflow orchestrator (aka Boomerang Mode) that breaks down complex tasks and delegates them to specialized modes. Learn more about [Boomerang Tasks](https://docs.roocode.com/features/boomerang-tasks). |
| **Tool Access** | No direct tool access (uses `new_task` tool to delegate work to other modes) |
| **Ideal For** | Managing multi-step projects, coordinating work across different modes, and automating complex workflows |
| **Special Features** | Uses the [`new_task`](https://docs.roocode.com/advanced-usage/available-tools/new-task) tool to delegate subtasks to other modes. |

---

## Customizing Modes

Tailor Roo Code's behavior by customizing existing modes or creating new specialized assistants. Define tool access, file permissions, and behavior instructions to enforce team standards or create purpose-specific assistants. See [Custom Modes documentation](https://docs.roocode.com/features/custom-modes) for setup instructions.

### Understanding Tool Groups

Each tool group provides specific capabilities:

- **`read`**: File reading, listing, and searching capabilities
- **`edit`**: File modification and creation capabilities
- **`browser`**: Web browsing and search capabilities
- **`command`**: Terminal command execution
- **`mcp`**: Model Context Protocol server interactions

For detailed information about available tools, see the [Available Tools documentation](https://docs.roocode.com/advanced-usage/available-tools/tool-use-overview).
