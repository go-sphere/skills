---
name: proto-api-generator
description: Design proto3 and HTTP API contracts for go-sphere scaffold projects, including server-streaming SSE endpoints. Use when defining service APIs, choosing between entpb, shared, and custom messages, or enforcing scaffold conventions, route-safety rules, and service-local error placement. Not for the `protoc-gen-*` plugins themselves — that is `protoc-plugin-engineering`.
---

# Proto API Generator

Design implementation-ready `proto3` + HTTP contracts for go-sphere scaffold projects. Follow
scaffold conventions unless the user explicitly asks to deviate. Keep outputs protocol-first:
reasoning checks replace lint plugins, scripts, and manual edits to generated files.

## Inputs

Do not write a `.proto` file or an API design document until all three are confirmed through
dialogue, not inferred from context:

1. Which service module is being designed, for example `task`, `user`, `order`.
2. Whether this is a new file or an addition to an existing proto.
3. The message strategy (`entpb`, `shared`, or custom) for at least the main entities.

Ask one question at a time for anything missing. When a decision has several reasonable options —
message type, route strategy, pagination shape — present 2-3 options with your recommendation.
Never choose unilaterally.

Three kinds of task input are supported:

- Prompt only — infer entities and use cases, then state every assumption explicitly.
- Folder input — inspect only the provided folders. Prefer scaffold structure (`proto/`, `internal/`, `api/`) when present.
- Requirement plus mock demo — requirement docs are business truth, mock payloads are response-shape truth, and the Ent schema is implementation reference, not a contract to mirror.

## Steps

Track these with TodoWrite. Create one task per step and close it before starting the next.

1. Confirm module, file mode, and message strategy with the user.
2. Classify each target file: `service proto` (contains a `service`) or `message-only proto` (messages and enums only).
3. Read the scaffold conventions reference. Choose package style, service route prefix, and compatibility constraints before drafting anything.
4. Decide reuse — `entpb`, `shared.v1`, or a custom DTO/VO — before finalizing message shapes.
5. Present the service overview (service name, RPC list) and get approval.
6. Present the message designs section by section and get approval for each.
7. For a `service proto`, define business use cases, transport shape (unary or server-streaming), HTTP bindings, route-safe paths, and error enums. For a `message-only proto`, draft messages and enums only, then record the service-only exemptions in validation notes.
8. Run every check in the final-gate checklist. If any check fails, stop and output `Validation Notes -> Blocking Issues` with corrected proposals.
9. Write the API design doc to disk, then ask whether to proceed to proto file generation.

## Reference Map

Load the smallest set that supports the decision in front of you. Never load everything.

| Read | When |
|------|------|
| [references/repo-proto-conventions-reference.md](references/repo-proto-conventions-reference.md) | Always, at step 3 — package style, route namespace, pagination defaults, reuse policy, naming compatibility, topology |
| [references/api-binding-basics-reference.md](references/api-binding-basics-reference.md) | Choosing HTTP method, path template, or where a field binds from |
| [references/api-binding-advanced-reference.md](references/api-binding-advanced-reference.md) | Shaping a request body, a response body, or message-level binding defaults |
| [references/api-streaming-reference.md](references/api-streaming-reference.md) | Designing a server-streaming SSE endpoint |
| [references/router-conflict-reference.md](references/router-conflict-reference.md) | Adding service routes, path templates, or checking backend portability |
| [references/error-definition-reference.md](references/error-definition-reference.md) | Declaring error enums and `sphere.errors` annotations |
| [references/error-runtime-reference.md](references/error-runtime-reference.md) | Reasoning about runtime error behavior, composition, or the JSON error response |
| [references/protocol-and-codegen-reference.md](references/protocol-and-codegen-reference.md) | Questions about the codegen pipeline |
| [references/proto-packages-and-runtime-reference.md](references/proto-packages-and-runtime-reference.md) | Questions about package layout or runtime assumptions |
| [references/go-sphere-api-definitions-checklist.md](references/go-sphere-api-definitions-checklist.md) | Always, at step 8 — the release gate |
| [references/proto-output-condensed-template.md](references/proto-output-condensed-template.md) | Final formatting of straightforward CRUD work |
| [references/proto-output-full-template.md](references/proto-output-full-template.md) | Final formatting of custom logic, multiple services, or complex routing |

## Rules

1. Design business capability first. Never publish a table-mirror contract.
2. A `service proto` must satisfy the service-only topology, route, and error-placement rules. A `message-only proto` is allowed, but must record its exemptions explicitly. Both must satisfy naming, import, runtime, and codegen checks.
3. Reuse in this order: `entpb` when it already satisfies the external contract, then `shared.v1` for cross-service messages, then a custom DTO/VO. A custom DTO/VO needs at least one of these reasons: sensitive fields must be hidden, cross-aggregate composition is required, or external contract stability must be isolated from storage changes.
4. Keep service-specific business errors in the same proto file as the owning `service`. Create or reuse a shared error only for cross-service semantics.
5. List APIs require pagination. Prefer batch APIs over repeated single reads.
6. Avoid `oneof` in HTTP-exposed request and response messages. Tags land on wrapper structs, generated handlers bind the parent request, so QUERY/URI/HEADER oneof members are never filled. JSON codecs also handle oneof poorly.
7. Keep error contracts machine-readable and stable.
8. Never leak sensitive or storage-only fields into an external contract.
9. Keep routes conflict-safe. Official templates serve on `stdx` (`net/http`), but design for the strictest adapter's subset (Gin's) so routes stay portable. Generated handlers take an `httpx` context, never a framework context.
10. Add concise `//` business comments on exposed `service`/`rpc`, core messages, and key enum values.
11. Map only `returns (stream Reply)` methods to SSE. `protoc-gen-sphere`'s HTTP transport does not support client-streaming or bidirectional methods.
12. For every stream, decide and document completion, failure, cancellation, optional resume, and lazy-versus-eager commit as explicit contract decisions. Streaming events always carry the whole reply message; never use `response_body`.

## Output

Write the API design doc to `design/<feature>/api.md` when the user names a feature or
change-id. Otherwise write it to `prd/API.md`.

Pick exactly one output template before final formatting: the condensed template for
straightforward CRUD with clear reuse and routing, or the full template for custom business
logic, multiple services, complex routing, or heavy validation notes.

Keep drafting notes out of the final deliverable. Emit `All required checks passed.` only when
the checklist actually passes; otherwise emit `Validation Notes -> Blocking Issues` instead. Do
not replace local references with external links in final outputs.

## Related Skills

- Upstream — `spec-writer` supplies service boundaries, entities, and states; `prd` supplies scope. When a spec changed, `spec-diff-pipeline` supplies `03-api-delta.md`.
- Downstream — `sphere-feature-workflow` lands the `.proto` and runs generation; `proto-service-generator` completes the generated service interfaces; `frontend-crud-generator` builds the frontend pages and routes once the swagger client is regenerated. Hand off when the final-gate checklist passes.
- Boundary — use `protoc-plugin-engineering` for the `protoc-gen-*` plugins themselves; this skill owns the `.proto` contracts they consume.
- Companion — `sphere-feature-workflow` when the contract change must land together with schema, service, or generation changes; if it is unavailable, finish the contract and list the integration steps as follow-up.
- If a referenced skill is not installed in this session, name it in the handoff message and continue with the current artifact; do not stall.
