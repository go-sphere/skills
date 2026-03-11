# sphere-workflow for Claude Code

`sphere-workflow` now includes Claude plugin manifests in `.claude-plugin/` in addition to the runtime hook files under `hooks/`.

## Included Assets

- `.claude-plugin/plugin.json` declares the plugin package metadata.
- `.claude-plugin/marketplace.json` provides a local development marketplace entry for this repository.
- `hooks/hooks.json` registers the session bootstrap hook.
- `hooks/session-start` injects the `using-sphere-workflow` bootstrap skill content.

## Repository Layout

Clone the repository anywhere Claude Code can access:

```bash
git clone https://github.com/go-sphere/skills.git ~/src/sphere-workflow
```

The clone itself is the plugin root. Claude should see:

- `.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json`
- `hooks/`
- `skills/`

## Local Plugin / Marketplace Usage

This repository is set up for Claude Code local plugin workflows rather than an official hosted marketplace.

Use your normal Claude Code local plugin or local marketplace flow against this repository root. The two common entrypoints are:

- the plugin manifest at `.claude-plugin/plugin.json`
- the local marketplace manifest at `.claude-plugin/marketplace.json`

After registration, start a fresh Claude Code session and ask for a go-sphere task. The session-start hook should preload `using-sphere-workflow`, then Claude can route into the bundled follow-up skills.

## Verification

At the repository root:

```bash
bash tests/run-tests.sh
```

This validates:

- Claude plugin manifests exist and parse as JSON
- hook bootstrap output includes `using-sphere-workflow`
- Codex/OpenCode adapter assets are still consistent

## Updating

```bash
cd ~/src/sphere-workflow && git pull
```

## Uninstalling

Remove the local Claude plugin or marketplace registration that points at this repository clone, then delete the clone if you no longer need it.

## Troubleshooting

1. Confirm `.claude-plugin/plugin.json` exists in the clone.
2. Confirm `.claude-plugin/marketplace.json` exists in the clone.
3. Confirm `hooks/hooks.json` and `hooks/session-start` exist and are executable.
4. Start a fresh Claude Code session after updating or re-registering the plugin.
