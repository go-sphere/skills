# go-sphere skills

Agent skills for the go-sphere ecosystem: requirement and spec writing, go-sphere
scaffold delivery, Go test and documentation engineering, and multi-agent
orchestration. Each skill is a directory under `skills/` with a `SKILL.md` that
coding agents can load on demand.

The repository URL is `https://github.com/go-sphere/skills`.

## Installation

```bash
# Install every skill
npx skills add https://github.com/go-sphere/skills

# Install selected skills
npx skills add https://github.com/go-sphere/skills \
  --skill sphere-ent \
  --skill sphere-api \
  --skill sphere-feature
```

Re-run the command to refresh installed skills from this repository.

Invoke a skill by name, for example:

```text
Use the sphere-api skill to generate API definitions
```

or with `/<skill-name>` where the agent supports slash invocation.

## Skill Names

Names are short so they are quick to type as `/<name>`. The prefix tells you what a skill
assumes:

| Pattern | Assumes | Skills |
|---------|---------|--------|
| `sphere-*` | a go-sphere scaffold project | `sphere-feature`, `sphere-api`, `sphere-ent`, `sphere-crud`, `sphere-sync`, `sphere-make` |
| `go-*`, `godoc` | any Go repository | `go-test`, `go-simplify`, `go-migrate`, `godoc` |
| no prefix | nothing; general purpose | `interview-me`, `prd`, `spec`, `improve`, `delegate`, `rex-desktop` |

## Workflow Map

The go-sphere delivery lifecycle runs from `interview-me` to `sphere-feature`. The rest are
maintenance, quality, and orchestration skills you can call at any point.

```text
Settle ambiguous decisions by interview
  -> interview-me
PRD / product framing
  -> prd
Implementation-ready specification
  -> spec
Ent schema implementation
  -> sphere-ent
Proto + HTTP contract design
  -> sphere-api
Features across proto, schema, and service layers
  -> sphere-feature
Frontend pages and routes
  -> sphere-crud
Layout upgrade, drift, or legacy adoption
  -> sphere-sync
Makefile and Make-driven CI standardization
  -> sphere-make
Go test review, repair, and authoring
  -> go-test
Go API documentation and verified usage examples for agents
  -> godoc
Go code leanness audit and safe simplification
  -> go-simplify
Migrating a non-Go codebase to Go
  -> go-migrate
Codebase audit and self-contained plans for other agents
  -> improve
One headless task for another coding agent
  -> delegate
Several live coding agents in Rex floating panes
  -> rex-desktop
```

Each skill's `## Related Skills` block names its upstream, downstream, boundary, and
companion skills, so finished work moves to the next stage without re-classifying
from scratch.

## Bundled Skills

### go-sphere projects (`sphere-*`)

- `sphere-feature` handles end-to-end scaffold feature delivery across proto, schema, bind/map, and service layers, including completing service methods and SSE producers from generated interfaces.
- `sphere-api` designs scaffold-safe proto3 + HTTP contracts.
- `sphere-ent` converts approved designs into Ent schema files.
- `sphere-crud` generates admin pages and route registration from a sphere-generated TypeScript swagger client, following the project's own framework conventions.
- `sphere-sync` updates a generated project to a newer layout revision, resolves layout drift, and adopts pre-contract projects into the `.sphere/layout.lock.json` model.
- `sphere-make` standardizes common Make targets, root batch orchestration, and Make-driven CI without flattening multi-module, generator, or layout-specific behavior.

### Go engineering (`go-*`, `godoc`)

- `go-test` audits, repairs, and writes behavior-focused Go tests, reusable interface contract suites, and justified golden tests.
- `godoc` writes self-contained Go API comments and verified usage examples so consumers and AI agents can get started through `go doc`.
- `go-simplify` audits Go code for over-design, over-optimization, and over-defensive checks, then applies behavior-neutral cleanups against a green test baseline while never breaking the exported API.
- `go-migrate` migrates a legacy or foreign-language codebase to idiomatic Go on the latest stable release, proving behavior parity with a differential A/B harness and recording telemetry, benchmarks, Go PGO results, and an HTML infographic.

### Requirements and planning

- `interview-me` deeply interviews the user through a decision tree until reaching shared technical and product consensus.
- `prd` turns agreed direction into a high-quality PRD.
- `spec` produces implementation-ready specifications.
- `improve` audits a codebase read-only and writes self-contained implementation plans with verification gates for cheaper agents to execute. It can dispatch an executor through `delegate`, review the diff, and keep the plan backlog current. Adapted from [shadcn/improve](https://github.com/shadcn/improve) (MIT).

### Agent orchestration

- `delegate` runs one task headless in claude, codex, kimi, agy, or pi, returns a structured result, resumes the session, and owns every agent-specific flag and executable lookup.
- `rex-desktop` coordinates several live agents as workers in Rex floating panes: spawn, wait until done, follow up, and verify. It launches agents through `delegate`.

## Default CLAUDE.md

[CLAUDE.TEMPLATE.md](CLAUDE.TEMPLATE.md) is a starting `CLAUDE.md` for a go-sphere
project: general coding-behavior guidelines plus go-sphere conventions. Copy it to the
project root as `CLAUDE.md` (or `AGENTS.md`) and fill in the project-specific section.

## Tech Stack

- Backend framework: [go-sphere](https://github.com/go-sphere)
- ORM: [ent](https://entgo.io/) (Bun in the `bun` layout)
- Protocol: Protocol Buffers (proto3)
- Frontend: Vue 3 + Element Plus (pure-admin-thin); the frontend generator follows whatever framework a project actually uses
- Code generation: `protoc-gen-sphere`, `protoc-gen-sphere-binding`, `protoc-gen-sphere-errors`, and `protoc-gen-route` (Telegram layout only)
- Project layouts: `standard`, `simple`, `bun`, `telegram` — created by `sphere-cli create --layout`, each carrying `.sphere/layout.json` ownership rules

## Progressive Loading

Every bundled skill is written for staged disclosure, so an agent reads only what the
current decision needs:

- The `description` is the only part always in context. It stays under 400 characters and
  names the neighbouring skill it should not be used for.
- `SKILL.md` stays under 150 lines: inputs, a numbered path, the reference map, the rules,
  and the output contract.
- Detail lives in `references/*.md`, each under 200 lines and each introduced exactly once,
  in that skill's `## Reference Map` table, with the condition that makes it worth reading.

`tests/run-tests.sh` enforces these budgets, and fails when a reference file is orphaned
from its skill's Reference Map.

## Authoring and Documentation

- [references/skill-authoring.md](references/skill-authoring.md) — the authoring contract for
  skills in this repository: size budgets, description formula, section order, and the
  plain-language rules that keep skills readable for smaller models.
- [docs/archive/](docs/archive/README.md) — historical workflow and prompt guides written for
  an earlier, larger skill pipeline. Not maintained.

## Contributing

Issues and pull requests are welcome. Run `bash tests/run-tests.sh` before opening a
pull request.

## License

MIT
