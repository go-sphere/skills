---
name: proto-api-generator
description: Design proto3 + HTTP API contracts for go-sphere scaffold projects from prompts, input folders, or requirement docs with mock data. Use when defining service APIs, selecting between entpb/shared/custom messages, and enforcing scaffold conventions, router-safety rules, and service-local error placement. This skill is REQUIRED for any proto API design task in go-sphere scaffold - always use it instead of writing proto files from scratch.
---

# Proto API Generator

Design implementation-ready `proto3 + HTTP` contracts for go-sphere scaffold projects.

<HARD-GATE>
Do not write any `.proto` file or API design document until the following are confirmed through dialogue:
- Which service module is being designed (e.g., `task`, `user`, `order`)
- Whether this is a new file or an addition to an existing proto
- The primary message strategy (entpb / shared / custom) for at least the main entities

If any of these are missing, ask one question at a time before proceeding.
When a design decision has multiple reasonable options (message type, route strategy, pagination shape), present 2-3 options with your recommendation — do not choose unilaterally.
</HARD-GATE>

## Operating Model

1. Follow go-sphere scaffold conventions unless the user explicitly requests deviation.
2. Treat local references as the working source of truth for scaffold rules, runtime behavior, and output shape.
3. Keep outputs protocol-first; do not rely on lint plugins, scripts, or manual edits to generated files as substitutes for reasoning checks.

## Checklist (track with TodoWrite)

At task start, call TodoWrite to create a task for each numbered item below. Mark each complete before moving to the next.

1. Confirm module name, file mode (new / add to existing), and message strategy — through dialogue with the user, not by inferring from context
2. Ask clarifying questions one at a time for any ambiguous scope or behavior
3. For non-obvious decisions, propose 2-3 options with recommendation
4. Present service overview (service name, RPC list) — get approval
5. Present message designs section by section — get approval for each
6. Run Final Gate checklist (`references/go-sphere-api-definitions-checklist.md`)
7. Write the API design doc to disk (`prd/API.md` or `design/<feature>/api.md`)
8. Ask if the user wants to proceed to proto file generation

**Output path rule:** Use `design/<feature>/api.md` if the user names a specific feature or change-id; default to `prd/API.md` otherwise.

## Task Intake

Supported task inputs:

1. Prompt-only: infer entities and use cases, then state assumptions explicitly.
2. Folder input: inspect only the provided folders; prefer scaffold-standard structure (`proto/`, `internal/`, `api/`) when present.
3. Requirement + mock demo: treat requirement docs as business truth, mock payloads as response-shape truth, and Ent schema as implementation reference rather than contract mirror.

## Progressive Reference Loading

Do not load every reference by default. Load the smallest set that can support the current decision.

### Start Here

1. [references/repo-proto-conventions-reference.md](references/repo-proto-conventions-reference.md)
   Use for package style, route namespace strategy, pagination defaults, reuse policy, naming compatibility, and topology rules.

### Load Only When Needed

1. Final output shape selection or final formatting:
   [references/proto-output-template.md](references/proto-output-template.md)
   Then load exactly one template:
   - [references/proto-output-condensed-template.md](references/proto-output-condensed-template.md)
   - [references/proto-output-full-template.md](references/proto-output-full-template.md)
2. Service routes, path templates, or backend portability:
   [references/router-conflict-reference.md](references/router-conflict-reference.md)
3. HTTP method, binding, body, or response shaping:
   [references/go-sphere-api-definitions-reference.md](references/go-sphere-api-definitions-reference.md)
4. Error enums, `sphere.errors`, or runtime error behavior:
   [references/go-sphere-error-handling-reference.md](references/go-sphere-error-handling-reference.md)
5. Package layout, codegen pipeline, or runtime assumptions:
   [references/protocol-and-codegen-reference.md](references/protocol-and-codegen-reference.md)
   [references/proto-packages-and-runtime-reference.md](references/proto-packages-and-runtime-reference.md)

### Final Gate

1. [references/go-sphere-api-definitions-checklist.md](references/go-sphere-api-definitions-checklist.md)

If any required check fails, stop and output `Validation Notes -> Blocking Issues` with corrected proposals.
Do not replace local references with external links in final outputs.

## Core Decisions

### File Mode

Classify each target proto file as one of:

1. `service proto`: contains a `service` definition.
2. `message-only proto`: contains messages or enums only.

Mode handling:

1. `service proto` must satisfy service-only topology, route, and error-placement rules.
2. `message-only proto` is allowed and must record service-only exemptions explicitly.
3. Both modes must still satisfy naming, import, runtime, and codegen compatibility checks.

### Reuse Order

Default reuse priority:

1. Reuse `entpb` when it already satisfies external contract needs.
2. Reuse or extract `shared.v1` messages for cross-service usage.
3. Create custom DTO or VO only when contract shaping requires it.

Use custom DTO or VO only when at least one condition is true:

1. Sensitive or internal fields must be hidden.
2. Cross-aggregate composition is required.
3. External contract stability must be isolated from storage model changes.

### Error Placement Default

1. Keep service-specific business errors in the same proto file as the owning `service`.
2. Reuse or create shared errors only for cross-service semantics.
3. For `message-only proto`, skip service-local error placement rules but still validate runtime and import compatibility.

## Workflow

1. Classify each target file by mode.
2. Read scaffold conventions first and choose package style, service prefix, and compatibility constraints before drafting.
3. Decide reuse (`entpb`, `shared.v1`, custom DTO or VO`) before finalizing message shapes.
4. For `service proto`, define business use cases, HTTP bindings, route-safe paths, and error enums.
5. For `message-only proto`, draft messages and enums only, then record service-only exemptions in validation notes.
6. Load detailed HTTP, error, router, or runtime references only when the draft actually depends on them.
7. Choose the deliverable shape late:
   - use the condensed template for straightforward CRUD with clear reuse and routing;
   - use the full template for custom business logic, multiple services, complex routing, or heavy validation notes.
8. Run the final checklist before delivery.

## Non-Negotiables

Keep these principles in mind throughout the task. Detailed rule text lives in the references and checklist.

1. Design business capability first; avoid table-mirror public contracts.
2. List APIs require pagination; batch APIs are preferred over repeated single reads.
3. Avoid `oneof` in HTTP-exposed request or response messages.
4. Keep error contracts machine-readable and stable.
5. Do not leak sensitive or storage-only fields into external contracts.
6. Keep routes conflict-safe; when backend is unknown, design for the Gin-safe subset first.
7. Add concise `//` business comments for exposed `service/rpc`, core messages, and key enum values.

## Mandatory Pre-Output Checklist

BEFORE writing the final proto file, you MUST verify all of the following:

### Package Naming Check
- [ ] Package name follows scaffold convention: `dash.v1` for generic, or `{module}.v1` for domain-specific (e.g., `user.v1`, `order.v1`, `article.v1`)
- [ ] Package declaration is in the format `package {name}.v1;`

### HTTP Binding Check
- [ ] Every RPC method has `option (google.api.http)` annotation
- [ ] HTTP method (get/post/put/delete) matches the operation semantics
- [ ] Route path follows REST conventions with proper path parameters

### Error Handling Check
- [ ] Service proto files MUST include a service-local error enum (e.g., `ArticleError`, `OrderError`, `AuthError`)
- [ ] Error enum uses `(sphere.errors.options)` annotation with proper status codes
- [ ] At minimum, include `NOT_FOUND` and `INVALID_PARAMETER` error codes

### Field Type Check
- [ ] ID fields use `int64` (not `string`)
- [ ] Timestamps use `google.protobuf.Timestamp`
- [ ] Pagination uses `page`/`page_size` with `total_size`/`total_page` in response

### Validation Check
- [ ] Required fields have `(buf.validate.field)` constraints
- [ ] String fields have `min_len` or `min_bytes` where appropriate
- [ ] Numeric fields have `gte`/`lte` bounds where appropriate

### Reuse Check
- [ ] Consider using entpb messages when they match contract needs
- [ ] Consider using shared.v1 for cross-service messages

If ANY check fails, fix the proto file before delivering. Do not output proto files that fail these checks.

## Output

Use [references/proto-output-template.md](references/proto-output-template.md) only as the template selector.
Before final formatting, load exactly one of:

1. [references/proto-output-condensed-template.md](references/proto-output-condensed-template.md)
2. [references/proto-output-full-template.md](references/proto-output-full-template.md)
