# Go-Sphere Skills

A collection of AI skills designed for the go-sphere ecosystem and related technology stacks.

## Skills Overview

### Database & Schema

#### db-schema-from-requirements
Generate production-ready Go + Ent database schema designs from requirement documents, prompts, or existing code.

**Use cases:**
- Extract and design entity models from requirements
- Design Ent schema fields with proper constraints
- Plan weak-relation ID strategies and indexes
- Design database migration strategies

#### ent-seed-sql
Generate deterministic SQL seed data from Ent schema definitions.

**Use cases:**
- Initialize data for dev/test environments
- Create realistic sample data with relationships
- Output executable SQL seed files
- Generate datasets with stable (non-random) IDs

### API & Protocol

#### proto-http-api-from-input-ent
Design proto3 + HTTP API contracts for go-sphere scaffold projects.

**Use cases:**
- Protocol-first API design
- Generate protobuf definitions from requirements/Ent schemas
- Choose between entpb/shared/custom messages
- HTTP route conflict detection and error handling conventions

#### proto-service-skeleton
Generate service implementation skeletons from generated API interfaces.

**Use cases:**
- Generate service files from `*ServiceHTTPServer` interfaces
- CRUD service templates with direct Ent integration
- Interface assertion checks and safe append-only updates
- Placeholder stubs for unknown business logic

### Full-Stack Workflows

#### sphere-layout-feature-workflow
Implement end-to-end feature changes in go-sphere scaffold projects.

**Use cases:**
- Add or modify APIs, proto definitions, and Ent schemas
- Protocol-first development workflow
- Multi-layer coordinated changes (proto → schema → service → render)
- Avoid manual edits to generated files

#### pure-admin-thin-crud-gen
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
npx skills add https://github.com/go-sphere/skills --skill db-schema-from-requirements

# Install multiple skills
npx skills add https://github.com/go-sphere/skills \
  --skill proto-http-api-from-input-ent \
  --skill sphere-layout-feature-workflow

# Install all skills
npx skills add https://github.com/go-sphere/skills --all
```

## Usage

After installation, skills are automatically activated when matching scenarios are detected, or can be explicitly invoked:

```
# Auto-activation (when task matches skill scenarios)
User: Help me design a database schema for user management

# Explicit invocation
User: Use the proto-http-api-from-input-ent skill to generate API definitions
```

## Skill Composition

These skills work together to cover the complete development workflow:

```
Requirements Input
  ↓
db-schema-from-requirements (Design schema)
  ↓
proto-http-api-from-input-ent (Design API)
  ↓
sphere-layout-feature-workflow (End-to-end implementation)
  ├─ proto-service-skeleton (Generate service skeleton)
  └─ ent-seed-sql (Generate test data)
  ↓
pure-admin-thin-crud-gen (Generate admin backend)
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
