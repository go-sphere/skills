# sphere-workflow for Codex

Use `sphere-workflow` with Codex through native skill discovery.

## Quick Install

Tell Codex:

```text
Fetch and follow instructions from https://raw.githubusercontent.com/go-sphere/skills/refs/heads/main/.codex/INSTALL.md
```

## Manual Install

```bash
git clone https://github.com/go-sphere/skills.git ~/.codex/sphere-workflow
mkdir -p ~/.agents/skills
ln -s ~/.codex/sphere-workflow/skills ~/.agents/skills/sphere-workflow
```

Restart Codex after creating the symlink.

## How It Works

- Codex scans `~/.agents/skills/` at startup.
- The `sphere-workflow` symlink exposes this repository's bundled skills.
- `using-sphere-workflow` is the bootstrap skill that routes the task into the right workflow stage.

## Updating

```bash
cd ~/.codex/sphere-workflow && git pull
```

## Uninstalling

```bash
rm ~/.agents/skills/sphere-workflow
rm -rf ~/.codex/sphere-workflow
```

## Troubleshooting

1. Verify the symlink: `ls -la ~/.agents/skills/sphere-workflow`
2. Verify bootstrap skill exists: `ls ~/.codex/sphere-workflow/skills/using-sphere-workflow`
3. Restart Codex after changing the symlink or updating the clone
