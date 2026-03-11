# sphere-workflow for OpenCode

Use `sphere-workflow` with OpenCode through a thin bootstrap plugin plus native skill discovery.

## Quick Install

Tell OpenCode:

```text
Fetch and follow instructions from https://raw.githubusercontent.com/go-sphere/skills/refs/heads/master/.opencode/INSTALL.md
```

## Manual Install

```bash
git clone https://github.com/go-sphere/skills.git ~/.config/opencode/sphere-workflow
mkdir -p ~/.config/opencode/plugins ~/.config/opencode/skills
rm -f ~/.config/opencode/plugins/sphere-workflow.js
rm -rf ~/.config/opencode/skills/sphere-workflow
ln -s ~/.config/opencode/sphere-workflow/.opencode/plugins/sphere-workflow.js ~/.config/opencode/plugins/sphere-workflow.js
ln -s ~/.config/opencode/sphere-workflow/skills ~/.config/opencode/skills/sphere-workflow
```

Restart OpenCode after creating the symlinks.

## How It Works

- `.opencode/plugins/sphere-workflow.js` injects the `using-sphere-workflow` bootstrap context.
- OpenCode's native `skill` tool discovers the bundled skills through `~/.config/opencode/skills/sphere-workflow`.
- After bootstrap, follow-up skill loading stays native to OpenCode.

## Updating

```bash
cd ~/.config/opencode/sphere-workflow && git pull
```

## Uninstalling

```bash
rm ~/.config/opencode/plugins/sphere-workflow.js
rm -rf ~/.config/opencode/skills/sphere-workflow
rm -rf ~/.config/opencode/sphere-workflow
```

## Troubleshooting

1. Verify the plugin symlink: `ls -l ~/.config/opencode/plugins/sphere-workflow.js`
2. Verify the skills symlink: `ls -l ~/.config/opencode/skills/sphere-workflow`
3. Check the plugin source exists: `ls ~/.config/opencode/sphere-workflow/.opencode/plugins/sphere-workflow.js`
4. Restart OpenCode after changing symlinks or updating the clone
