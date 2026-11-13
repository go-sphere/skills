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
  --skill db-schema-designer \
  --skill ent-schema-implementer \
  --skill proto-api-generator \
  --skill sphere-feature-workflow
```

Re-run the command to refresh installed skills from this repository.

Invoke a skill by name, for example:

```text
Use the proto-api-generator skill to generate API definitions
```

or with `/<skill-name>` where the agent supports slash invocation.

## Workflow Map

The skills move work through the go-sphere lifecycle in order.

```text
Interactive requirement interview & alignment
  -> interview-me
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
Frontend pages and routes
  -> frontend-crud-generator
Layout upgrade, drift, or legacy adoption
  -> sphere-layout-sync
protoc-gen-* plugin authoring and review
  -> protoc-plugin-engineering
Go test review, repair, and authoring
  -> go-test-engineering
Go API documentation and verified usage examples for agents
  -> godoc
Go code leanness audit and safe simplification
  -> go-simplify
Codebase audit and self-contained plans for other agents
  -> improve
Migrating a non-Go codebase to Go
  -> migrate-to-golang
Makefile and Make-driven CI standardization
  -> go-sphere-makefiles
One headless task for another coding agent
  -> delegate
Several live coding agents in Rex tabs
  -> rex-desktop
```

Each skill's `## Related Skills` block names its upstream, downstream, boundary, and
companion skills, so finished work moves to the next stage without re-classifying
from scratch.

## Bundled Skills

### Discovery and Requirements

- `interview-me` deeply interviews the user through a decision tree until reaching shared technical and product consensus.
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
- `frontend-crud-generator` generates admin pages and route registration from a sphere-generated TypeScript swagger client, following the project's own framework conventions.

### Layout and Toolchain Maintenance

- `sphere-layout-sync` updates a generated project to a newer layout revision, resolves layout drift, and adopts pre-contract projects into the `.sphere/layout.lock.json` model.
- `protoc-plugin-engineering` covers authoring, refactoring, and reviewing the `protoc-gen-*` plugins themselves, including config immutability, read-only templates, output determinism, and golden-file discipline.

### Quality and Verification

- `godoc` writes self-contained Go API comments and verified usage examples so consumers and AI agents can get started through `go doc`.
- `go-test-engineering` audits, repairs, and writes behavior-focused Go tests, reusable interface contract suites, and justified golden tests.
- `migrate-to-golang` migrates a legacy or foreign-language codebase to idiomatic Go on the latest stable release, proving behavior parity with a differential A/B harness and recording telemetry, benchmarks, Go PGO results, and an HTML infographic.
- `go-simplify` audits Go code for over-design, over-optimization, and over-defensive checks, then applies behavior-neutral cleanups against a green test baseline while never breaking the exported API.
- `improve` audits a codebase read-only and writes self-contained implementation plans with verification gates for cheaper agents to execute. It can dispatch an executor through `delegate`, review the diff, and keep the plan backlog current. Adapted from [shadcn/improve](https://github.com/shadcn/improve) (MIT).
- `go-sphere-makefiles` standardizes common Make targets, root batch orchestration, and Make-driven CI without flattening multi-module, generator, or layout-specific behavior.

### Agent Orchestration

- `delegate` runs one task headless in claude, codex, kimi, agy, or pi, returns a structured result, resumes the session, and owns every agent-specific flag and executable lookup.
- `rex-desktop` coordinates several live agents as workers in Rex tabs: spawn, wait until done, follow up, and verify. It launches agents through `delegate`.

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
- [references/dev.md](references/dev.md) — the AI-agent collaboration workflow guide (indexed,
  with per-stage chapters under `references/dev/`).
- [references/prompt.md](references/prompt.md) — per-round prompt templates (indexed, with
  chapters under `references/prompt/`).

## Contributing

Issues and pull requests are welcome. Run `bash tests/run-tests.sh` before opening a
pull request.

## License

MIT
