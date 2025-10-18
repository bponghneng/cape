---
scraped_url: "https://docs.roocode.com/features/custom-modes"
scraped_date: "2025-10-13"
---

# Customizing Modes

Roo Code allows you to create custom modes to tailor behavior to specific tasks or workflows. Modes can be global (available across projects) or project-specific.

Sticky Models remember the last model used with each mode so you can assign different models per task without reconfiguring.

---

## Why Use Custom Modes?

- Specialization for tasks like documentation, testing, or refactoring
- Safety by restricting access to sensitive files or commands
- Experimentation with prompts and configurations
- Team collaboration through shared mode definitions

---

## What's Included in a Custom Mode?

| Property | Description |
| --- | --- |
| `slug` | Unique identifier used internally and for linking instruction directories. |
| `name` | Display name shown in the UI. |
| `description` | Short summary displayed in the mode selector UI. |
| `roleDefinition` | Defines the mode’s identity and expertise in the system prompt. |
| `groups` | Configures allowed toolsets and file permissions. |
| `whenToUse` (optional) | Guides automated mode selection and orchestration. |
| `customInstructions` (optional) | Additional behavioral rules appended near the end of the system prompt. |

---

## Import and Export Modes

Use the Modes view to export or import modes as YAML files for sharing, backups, or templates.

### Key Features

- Shareable setups bundled into a single YAML file
- Easy backups and migrations between projects
- Slug changes handled automatically during import

### Exporting

1. Open the Modes view.
2. Select a mode.
3. Click **Export Mode** and save the `.yaml` file.

The export bundles configuration and any rules stored in `.roo/rules-{slug}/`.

### Importing

1. Click **Import Mode** in the Modes view.
2. Select the mode YAML file.
3. Choose Project (stored in `.roo/`) or Global scope (stored in your global Roo config directory).

Paths are normalized for cross-platform sharing.

---

## Exported YAML Format

```yaml
customModes:
  - slug: "my-custom-mode"
    name: "My Custom Mode"
    roleDefinition: "..."
    description: "..."
    groups:
      edit:
        enabled: true
        fileRegex:
          - "^src/.*"
```

You can edit the slug before importing; Roo updates related paths.

---

## Methods for Creating and Configuring Modes

1. **Ask Roo**: Use Roo’s conversational interface to generate modes.
2. **Modes Page**: Create and edit modes through the UI.
3. **Manual Configuration**: Define modes in YAML or JSON for advanced control.

YAML is preferred for readability and easier editing of complex structures.

---

## Mode-Specific Instructions via Files

Associate instruction files by placing them in `.roo/rules-{slug}/`. Roo includes these instructions when the mode is active. A generic `.roo/rules/` directory can store shared rules across modes.

---

## Configuration Precedence

Project-level modes override global modes with the same slug. Properties are not merged; project definitions replace global ones entirely.

---

## Overriding Default Modes

You can override built-in modes (Code, Architect, Ask, Debug) globally or per project. Exports include any customizations made to these modes.

---

## Understanding Regex in Custom Modes

Use `fileRegex` to restrict file editing access.

Guidelines:

- JSON requires double escaping (e.g., `"\\.md$"`).
- YAML usually needs a single escape (e.g., `\.md$`).
- Patterns match full relative paths.
- Invalid regex patterns are rejected with an error.

Common patterns:

- `\.md$` matches markdown files
- `^src/.*` matches files in `src/`
- `^(?!.*(test|spec))\.(js|ts)$` matches `.js`/`.ts` excluding tests

Operations blocked by regex rules raise `FileRestrictionError` with details about the mode and allowed patterns.

---

## Additional Features

- Built-in mode customizations are preserved in exports.
- Deleting a mode through the UI prompts about removing the associated rules folder.
- A global rules directory provides shared instructions across modes.

---

## Troubleshooting

- Reload VS Code if a new mode does not appear.
- Validate regex patterns before applying them.
- Remember project modes fully override global modes with the same slug.
