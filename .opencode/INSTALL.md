# Installing sphere-workflow for OpenCode

## Prerequisites

- [OpenCode.ai](https://opencode.ai) installed
- Git installed

## Installation Steps

### 1. Clone sphere-workflow

```bash
git clone https://github.com/go-sphere/skills.git ~/.config/opencode/sphere-workflow
```

### 2. Register the Plugin

Create a symlink so OpenCode discovers the plugin bootstrap:

```bash
mkdir -p ~/.config/opencode/plugins
rm -f ~/.config/opencode/plugins/sphere-workflow.js
ln -s ~/.config/opencode/sphere-workflow/.opencode/plugins/sphere-workflow.js ~/.config/opencode/plugins/sphere-workflow.js
```

### 3. Symlink Skills

Create a symlink so OpenCode's native `skill` tool discovers the bundled skills:

```bash
mkdir -p ~/.config/opencode/skills
rm -rf ~/.config/opencode/skills/sphere-workflow
ln -s ~/.config/opencode/sphere-workflow/skills ~/.config/opencode/skills/sphere-workflow
```

### 4. Restart OpenCode

Restart OpenCode. The plugin will inject the `using-sphere-workflow` bootstrap context automatically.

## Usage

### Finding Skills

Use OpenCode's native `skill` tool to list available skills:

```
use skill tool to list skills
```

### Loading the Bootstrap Skill

Use OpenCode's native `skill` tool to load the bootstrap skill explicitly:

```
use skill tool to load sphere-workflow/using-sphere-workflow
```

### Personal Skills

Create your own skills in `~/.config/opencode/skills/`:

```bash
mkdir -p ~/.config/opencode/skills/my-skill
```

Create `~/.config/opencode/skills/my-skill/SKILL.md`:

```markdown
---
name: my-skill
description: Use when [condition] - [what it does]
---

# My Skill

[Your skill content here]
```

### Project Skills

Create project-specific skills in `.opencode/skills/` within your project.

**Skill Priority:** Project skills > Personal skills > sphere-workflow skills

## Updating

```bash
cd ~/.config/opencode/sphere-workflow
git pull
```

## Troubleshooting

### Plugin not loading

1. Check plugin symlink: `ls -l ~/.config/opencode/plugins/sphere-workflow.js`
2. Check source exists: `ls ~/.config/opencode/sphere-workflow/.opencode/plugins/sphere-workflow.js`
3. Check OpenCode logs for errors

### Skills not found

1. Check skills symlink: `ls -l ~/.config/opencode/skills/sphere-workflow`
2. Verify it points to: `~/.config/opencode/sphere-workflow/skills`
3. Use the `skill` tool to list what OpenCode discovered

### Tool Mapping

When bundled skills reference Claude Code tools:
- `TodoWrite` -> `update_plan`
- `Task` with subagents -> `@mention` syntax
- `Skill` tool -> OpenCode's native `skill` tool
- File operations -> your native tools
