# sphere-workflow

`sphere-workflow` is a plugin-style workflow bundle for coding agents working in the
go-sphere ecosystem. It packages the repository's bundled skills behind a single
bootstrap entrypoint so agents can discover the right go-sphere workflow stage
first, instead of treating the repo as a loose collection of unrelated skills.

The repository URL stays the same: `https://github.com/go-sphere/skills`.

## What the Plugin Does

- Boots the agent into the go-sphere workflow through `using-sphere-workflow`
- Routes requirement shaping, specification, schema, API, and implementation work
  to the smallest relevant bundled skill
- Preserves direct skill usage for advanced users and existing installs
- Adds thin platform adapters for Claude Code, Cursor, Codex, and OpenCode

## Installation

### Claude Code

This repository now includes the local Claude plugin assets:

- `.claude-plugin/plugin.json` defines the plugin package
- `.claude-plugin/marketplace.json` defines a local development marketplace entry
- `hooks/hooks.json` registers the session-start hook
- `hooks/session-start` injects the `using-sphere-workflow` bootstrap context
- `skills/` contains the bundled follow-up skills

Clone the repository and use your normal Claude Code local plugin or local
marketplace flow against the repository root.

Detailed docs: [docs/README.claude.md](docs/README.claude.md)

### Cursor

This repository now includes the local Cursor plugin assets:

- `.cursor-plugin/plugin.json` defines the Cursor plugin package
- `hooks/hooks.json` registers the session-start hook
- `hooks/session-start` injects the `using-sphere-workflow` bootstrap context
- `skills/` contains the bundled follow-up skills

Clone the repository and use your normal Cursor local plugin flow against the
repository root.

Detailed docs: [docs/README.cursor.md](docs/README.cursor.md)

### Codex

Tell Codex:

```text
Fetch and follow instructions from https://raw.githubusercontent.com/go-sphere/skills/refs/heads/main/.codex/INSTALL.md
```

Codex uses native skill discovery. The install path is:

```bash
git clone https://github.com/go-sphere/skills.git ~/.codex/sphere-workflow
mkdir -p ~/.agents/skills
ln -s ~/.codex/sphere-workflow/skills ~/.agents/skills/sphere-workflow
```

Detailed docs: [docs/README.codex.md](docs/README.codex.md)

### OpenCode

Tell OpenCode:

```text
Fetch and follow instructions from https://raw.githubusercontent.com/go-sphere/skills/refs/heads/main/.opencode/INSTALL.md
```

OpenCode uses a thin bootstrap plugin plus native skill discovery. The install
path is:

```bash
git clone https://github.com/go-sphere/skills.git ~/.config/opencode/sphere-workflow
mkdir -p ~/.config/opencode/plugins ~/.config/opencode/skills
ln -s ~/.config/opencode/sphere-workflow/.opencode/plugins/sphere-workflow.js ~/.config/opencode/plugins/sphere-workflow.js
ln -s ~/.config/opencode/sphere-workflow/skills ~/.config/opencode/skills/sphere-workflow
```

Detailed docs: [docs/README.opencode.md](docs/README.opencode.md)

## Workflow Map

The plugin is meant to move work through the go-sphere lifecycle in order.

```text
Scattered inputs / kickoff
  -> project-intake
PRD / product framing
  -> prd
Prototype behavior / UX semantics
  -> ux-analyst
Implementation-ready specification
  -> spec-writer
Changed spec impact analysis
  -> spec-diff-pipeline
Schema design
  -> db-schema-designer
Ent schema implementation
  -> ent-schema-implementer
Seed / fixture SQL
  -> ent-seed-sql-generator
Proto + HTTP contract design
  -> proto-api-generator
Generated service skeletons
  -> proto-service-generator
Cross-layer scaffold implementation
  -> sphere-feature-workflow
Admin CRUD surface
  -> pure-admin-crud-generator
```

The bootstrap rule is simple:

- If the user explicitly names a skill, use it.
- If the task spans multiple stages, start at the earliest missing artifact.
- If the task touches proto, schema, service, or generation boundaries, route into
  `sphere-feature-workflow`.

## Bundled Skills

### Discovery and Requirements

- `project-intake` organizes rough inputs into a structured kickoff document.
- `prd` turns agreed direction into a high-quality PRD.
- `ux-analyst` translates demos and mockups into behavioral UX flows.

### Specification and Planning

- `spec-writer` produces implementation-ready specifications.
- `spec-diff-pipeline` traces downstream impact after spec changes.

### Data and Contract Design

- `db-schema-designer` designs review-ready schemas before coding.
- `ent-schema-implementer` converts approved designs into Ent schema files.
- `ent-seed-sql-generator` creates deterministic seed SQL for development and test.
- `proto-api-generator` designs scaffold-safe proto3 + HTTP contracts.
- `proto-service-generator` generates or completes service skeletons.

### Implementation and Surfaces

- `sphere-feature-workflow` handles end-to-end scaffold feature delivery.
- `pure-admin-crud-generator` scaffolds pure-admin-thin CRUD pages and routes.

## Legacy Direct Install

The repository still works as a direct skill source for compatibility:

```bash
# Install a single skill
npx skills add https://github.com/go-sphere/skills --skill db-schema-designer

# Install multiple skills
npx skills add https://github.com/go-sphere/skills \
  --skill db-schema-designer \
  --skill ent-schema-implementer \
  --skill proto-api-generator \
  --skill sphere-feature-workflow

# Install all bundled skills
npx skills add https://github.com/go-sphere/skills
```

You can also invoke a specific skill directly after installation, for example:

```text
Use the proto-api-generator skill to generate API definitions
```

## Updating

### Codex

```bash
cd ~/.codex/sphere-workflow && git pull
```

### OpenCode

```bash
cd ~/.config/opencode/sphere-workflow && git pull
```

### Claude Code / Cursor Local Plugin

```bash
cd /path/to/your/sphere-workflow-clone && git pull
```

### Direct Skill Install

Re-run your `npx skills add ...` command when you want to refresh the installed
skills from this repository.

## Uninstalling

### Codex

```bash
rm ~/.agents/skills/sphere-workflow
rm -rf ~/.codex/sphere-workflow
```

### OpenCode

```bash
rm ~/.config/opencode/plugins/sphere-workflow.js
rm -rf ~/.config/opencode/skills/sphere-workflow
rm -rf ~/.config/opencode/sphere-workflow
```

### Claude Code Local Plugin

Remove the local plugin or local marketplace registration that points at this
repository clone, then delete the clone if you no longer need it.

### Cursor Local Plugin

Remove the local Cursor plugin registration that points at this repository
clone, then delete the clone if you no longer need it.

## Troubleshooting

### Codex cannot see the plugin

- Verify `~/.agents/skills/sphere-workflow` exists and points to the cloned `skills/` directory.
- Restart Codex after creating or updating the symlink.
- Check that `skills/using-sphere-workflow/SKILL.md` exists in the clone.

### OpenCode plugin does not load

- Verify `~/.config/opencode/plugins/sphere-workflow.js` points to `.opencode/plugins/sphere-workflow.js`.
- Verify `~/.config/opencode/skills/sphere-workflow` points to the cloned `skills/` directory.
- Restart OpenCode after creating or updating the symlinks.

### Claude Code does not inject the bootstrap

- Verify `.claude-plugin/plugin.json` exists in the clone.
- Verify `.claude-plugin/marketplace.json` exists in the clone if you use a local marketplace flow.
- Verify the repository is registered as a local plugin root.
- Check that `hooks/hooks.json` and `hooks/session-start` are present in the clone.
- Confirm the plugin root still points at the same repository checkout.

### Cursor does not inject the bootstrap

- Verify `.cursor-plugin/plugin.json` exists in the clone.
- Verify the repository is registered as a local Cursor plugin root.
- Check that `hooks/hooks.json` and `hooks/session-start` are present in the clone.
- Confirm the plugin root still points at the same repository checkout.

### I still want a single skill directly

Use the compatibility install path with `npx skills add https://github.com/go-sphere/skills`
and install only the skills you need.

## Tech Stack

- Backend framework: [go-sphere](https://github.com/go-sphere)
- ORM: [ent](https://entgo.io/)
- Protocol: Protocol Buffers (proto3)
- Frontend: Vue 3 + Element Plus (pure-admin-thin)
- Code generation: `protoc-gen-sphere*`, `protoc-gen-route`

## Contributing

Issues and pull requests are welcome. The plugin shell lives beside the bundled
skills, so changes may affect both platform adapters and the skills themselves.

## License

MIT
