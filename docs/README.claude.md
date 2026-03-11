# sphere-workflow for Claude Code

`sphere-workflow` includes Claude plugin manifests in `.claude-plugin/` plus the runtime hook files under `hooks/`.

## Included Assets

- `.claude-plugin/plugin.json` declares the plugin package metadata.
- `.claude-plugin/marketplace.json` provides a hosted marketplace entry for this repository.
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

## Marketplace Install

Install from the repository marketplace:

```text
/plugin marketplace add go-sphere/skills
/plugin install sphere-workflow@sphere-workflow-marketplace
```

After installation, start a fresh Claude Code session and ask for a go-sphere task. The session-start hook should preload `using-sphere-workflow`, then Claude can route into the bundled follow-up skills.

What this gives you:

- A single bootstrap entrypoint instead of manually choosing among many go-sphere skills
- Routing across PRD, spec, Ent schema, proto API, service, and scaffold implementation stages
- A cleaner Claude install story that matches `/plugin marketplace add ...` and `/plugin install ...`

## Local Plugin / Local Marketplace Usage

If you want to work from a local clone instead of the hosted GitHub marketplace, clone the repository and register one of these entrypoints:

- the plugin manifest at `.claude-plugin/plugin.json`
- the marketplace manifest at `.claude-plugin/marketplace.json`

## Verification

At the repository root:

```bash
bash tests/run-tests.sh
```

This validates:

- Claude plugin manifests exist and parse as JSON
- hook bootstrap output includes `using-sphere-workflow`
- Codex/OpenCode adapter assets are still consistent

## Release Checklist

Before telling users to install from the marketplace, verify:

1. The GitHub repository is public and the default branch is `master`.
2. `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` are committed on `master`.
3. The marketplace name remains `sphere-workflow-marketplace`.
4. The plugin name remains `sphere-workflow`.
5. `bash tests/validate-plugin-shell.sh` passes from the repository root.
6. A fresh Claude Code session can run:

```text
/plugin marketplace add go-sphere/skills
/plugin install sphere-workflow@sphere-workflow-marketplace
```

7. The installed session loads `using-sphere-workflow` through the session-start hook.

## Updating

```bash
cd ~/src/sphere-workflow && git pull
```

## Uninstalling

Remove the installed Claude plugin or the local plugin / marketplace registration that points at this repository clone, then delete the clone if you no longer need it.

## Troubleshooting

1. Confirm `.claude-plugin/plugin.json` exists in the clone.
2. Confirm `.claude-plugin/marketplace.json` exists in the clone.
3. Confirm `hooks/hooks.json` and `hooks/session-start` exist and are executable.
4. Start a fresh Claude Code session after updating or re-registering the plugin.
