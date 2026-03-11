# sphere-workflow for Cursor

`sphere-workflow` now includes a Cursor plugin manifest in `.cursor-plugin/plugin.json`.

## Included Assets

- `.cursor-plugin/plugin.json` declares the Cursor plugin package
- `hooks/hooks.json` registers the session bootstrap hook
- `hooks/session-start` injects the `using-sphere-workflow` bootstrap context
- `skills/` contains the bundled follow-up skills

## Repository Layout

Clone the repository anywhere Cursor can access:

```bash
git clone https://github.com/go-sphere/skills.git ~/src/sphere-workflow
```

The clone itself is the plugin root. Cursor should see:

- `.cursor-plugin/plugin.json`
- `hooks/`
- `skills/`

## Local Plugin Usage

Use your normal Cursor local plugin flow against this repository root. The plugin manifest entrypoint is:

- `.cursor-plugin/plugin.json`

After registration, start a fresh Cursor agent session and ask for a go-sphere task. The session-start hook should preload `using-sphere-workflow`, then Cursor can route into the bundled follow-up skills.

## Verification

At the repository root:

```bash
bash tests/run-tests.sh
```

This validates:

- Cursor plugin manifest exists and parses as JSON
- Cursor plugin points at the local `skills/` directory and `hooks/hooks.json`
- Claude/Codex/OpenCode assets remain consistent

## Updating

```bash
cd ~/src/sphere-workflow && git pull
```

## Uninstalling

Remove the local Cursor plugin registration that points at this repository clone, then delete the clone if you no longer need it.

## Troubleshooting

1. Confirm `.cursor-plugin/plugin.json` exists in the clone.
2. Confirm `hooks/hooks.json` and `hooks/session-start` exist and are executable.
3. Start a fresh Cursor session after updating or re-registering the plugin.
