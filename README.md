# Go-Sphere Skills

A collection of AI skills designed for the go-sphere ecosystem and related technology stacks.

## Skills Quick List

| Skill Name | Description |
| --- | --- |
| `project-intake` | Organize scattered project inputs and generate standardized intake documents for new projects. |
| `prd` | Generate high-quality Product Requirements Documents (PRDs) following go-sphere workflow. |
| `ux-analyst` | Transform prototype demos from visual representations into behavioral UX flow documents. |
| `spec-writer` | Write or revise implementation-ready specifications for products, systems, APIs, workflows, and technical designs with Symphony-like depth. |
| `spec-diff-pipeline` | Analyze spec changes from git diff or version comparison and generate impact maps, API/schema deltas, and task plans. |
| `db-schema-designer` | Design review-ready database schemas before coding, with Ent + proto3 compatibility constraints baked in. |
| `ent-schema-implementer` | Implement approved database designs as Go Ent schemas with entproto and integration guidance. |
| `ent-seed-sql-generator` | Generate deterministic executable SQL seed data from Ent schemas and related inputs. |
| `proto-api-generator` | Design scaffold-compatible proto3 + HTTP API contracts for go-sphere projects. |
| `proto-service-generator` | Generate or complete service skeletons from generated `*ServiceHTTPServer` interfaces. |
| `sphere-feature-workflow` | Execute end-to-end feature delivery in sphere-layout with protocol-first generated-code-safe workflow. |
| `pure-admin-crud-generator` | Generate pure-admin-thin CRUD pages and route modules from swagger-ts-api methods. |

## Skills Overview

### Project Initiation

#### project-intake
Organize scattered project inputs and generate standardized intake documents, clarifying project boundaries and known/unknown items.

**Use cases:**
- New project or feature kickoff
- Organize PRD drafts, prototypes, or requirement descriptions
- Clarify "what's known vs what's unknown" before detailed design
- Process Figma links, screenshots, demos, and verbal descriptions
- Generate initial intake document (`docs/00-intake.md`)

#### prd
Generate high-quality Product Requirements Documents (PRDs) that bridge business vision and technical execution.

**Use cases:**
- Create PRDs from business requirements or initial ideas
- Document user personas and core business processes
- Define measurable success criteria and KPIs
- Clarify scope and non-scope boundaries
- Transition from intake to PRD solidification phase

#### ux-analyst
Transform prototype demos from visual representations into behavioral semantics that engineers can implement.

**Use cases:**
- Convert Figma designs, screenshots, or HTML demos to UX flow documents
- Document screen/page behaviors, entry/exit conditions
- Define user actions with state changes and failure handling
- Map screen navigation and user journeys
- Generate `prd/UX-FLOWS.md` and `prd/SCREEN-INVENTORY.md`

### Specification & Planning

#### spec-writer
Write or revise implementation-ready specifications for products, systems, APIs, workflows, runtime services, and technical designs.

**Use cases:**
- Create new specs from requirements or PRD documents
- Rewrite ambiguous specs into executable SPEC.md
- Deepen existing specs that feel too thin or vague
- Update specs after scope changes
- Apply Symphony-like structural style for complex systems

#### spec-diff-pipeline
Analyze spec changes from git diff or two version files and automatically produce downstream planning artifacts.

**Use cases:**
- Generate impact maps from SPEC.md changes
- Refresh API/proto planning after spec updates
- Analyze database/schema impact from specification changes
- Identify which product surfaces are affected
- Break implementation into executable task plans

### Database & Schema

#### db-schema-designer
Design review-ready database schemas from requirement documents, prompts, or existing code before entering implementation.

**Use cases:**
- Extract and design entity models from requirements
- Review entities, fields, relations, and indexes before coding
- Enforce Ent + proto3-compatible field type policies during design
- Produce Markdown review briefs with optional draft DDL appendix

#### ent-schema-implementer
Implement approved database designs as Go Ent schemas for go-sphere projects.

**Use cases:**
- Translate approved database reviews into Ent schema files
- Add entproto annotations and field numbering
- Plan bind/render/service integration impact
- Prepare generation and verification follow-up steps

#### ent-seed-sql-generator
Generate deterministic SQL seed data from Ent schema definitions.

**Use cases:**
- Initialize data for dev/test environments
- Create realistic sample data with relationships
- Output executable SQL seed files
- Generate datasets with stable (non-random) IDs

### API & Protocol

#### proto-api-generator
Design proto3 + HTTP API contracts for go-sphere scaffold projects.

**Use cases:**
- Protocol-first API design
- Generate protobuf definitions from requirements/Ent schemas
- Choose between entpb/shared/custom messages
- HTTP route conflict detection and error handling conventions

#### proto-service-generator
Generate service implementation skeletons from generated API interfaces.

**Use cases:**
- Generate service files from `*ServiceHTTPServer` interfaces
- CRUD service templates with direct Ent integration
- Interface assertion checks and safe append-only updates
- Placeholder stubs for unknown business logic

### Full-Stack Workflows

#### sphere-feature-workflow
Implement end-to-end feature changes in go-sphere scaffold projects.

**Use cases:**
- Add or modify APIs, proto definitions, and Ent schemas
- Protocol-first development workflow
- Multi-layer coordinated changes (proto → schema → service → render)
- Avoid manual edits to generated files

#### pure-admin-crud-generator
Generate CRUD pages and route modules for pure-admin-thin admin backends.

**Use cases:**
- Generate admin pages from swagger-ts-api output
- Scaffold list/edit/detail pages
- Auto-configure route modules
- Vue 3 + Element Plus backend development

## Installation

Install any skill using the `npx skills` command:

```bash
# Install a single skill
npx skills add https://github.com/go-sphere/skills --skill db-schema-designer

# Install multiple skills
npx skills add https://github.com/go-sphere/skills \
  --skill db-schema-designer \
  --skill ent-schema-implementer \
  --skill proto-api-generator \
  --skill sphere-feature-workflow

# Install all skills
npx skills add https://github.com/go-sphere/skills
```

## Usage

After installation, skills are automatically activated when matching scenarios are detected, or can be explicitly invoked:

```
# Auto-activation (when task matches skill scenarios)
User: Help me design and review a database schema for user management

# Explicit invocation
User: Use the proto-api-generator skill to generate API definitions
```

## Skill Composition

These skills work together to cover the complete development workflow:

```
Requirements Input
  ↓
project-intake (Organize inputs, clarify boundaries)
  ↓
prd (Create product requirements document)
  ↓
ux-analyst (Convert designs to behavioral flows)
  ↓
spec-writer (Create detailed specification)
  ↓
spec-diff-pipeline (Analyze impact)
  ↓
db-schema-designer (Design and review schema)
  ↓
ent-schema-implementer (Implement approved Ent schema)
  ↓
proto-api-generator (Design API)
  ↓
sphere-feature-workflow (End-to-end implementation)
  ├─ proto-service-generator (Generate service skeleton)
  └─ ent-seed-sql-generator (Generate test data)
  ↓
pure-admin-crud-generator (Generate admin backend)
```

## Tech Stack

- **Backend Framework**: [go-sphere](https://github.com/go-sphere)
- **ORM**: [ent](https://entgo.io/)
- **Protocol**: Protocol Buffers (proto3)
- **Frontend Framework**: Vue 3 + Element Plus (pure-admin-thin)
- **Code Generation**: protoc-gen-sphere*, protoc-gen-route

## License

MIT

## Contributing

Issues and Pull Requests are welcome to improve these skills.

Detailed documentation for each skill is located in the corresponding `SKILL.md` file.
