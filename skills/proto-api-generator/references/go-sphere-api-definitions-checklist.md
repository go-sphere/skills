# Reference: API and Error Checklist

## Purpose

Provide strict, execution-time gates to validate contracts after drafting proto definitions.

## Scope

Use this checklist with:

- [repo-proto-conventions-reference.md](repo-proto-conventions-reference.md)
- [router-conflict-reference.md](router-conflict-reference.md)
- [go-sphere-api-definitions-reference.md](go-sphere-api-definitions-reference.md)
- [go-sphere-error-handling-reference.md](go-sphere-error-handling-reference.md)
- [protocol-and-codegen-reference.md](protocol-and-codegen-reference.md)
- [proto-packages-and-runtime-reference.md](proto-packages-and-runtime-reference.md)

## When To Load

Load this reference at final validation time after drafting contracts. Use it as the release gate, not as an initial brainstorming checklist.

## Table of Contents

- [Required Checks](#required-checks)
- [Pass/Fail Semantics](#passfail-semantics)
- [Mandatory Confirmation](#mandatory-confirmation)

## Required Checks

### A. Scaffold Fit (Required)

- [ ] Choose a scaffold-valid target package style before drafting endpoints (for example `api.v1`, `dash.v1`, `shared.v1`, `bot.v1`).
- [ ] Define one stable service-level route prefix namespace before adding service RPC paths.
- [ ] Follow scaffold path/method conventions for that package.
- [ ] Keep scaffold-compatible pagination style unless requirements explicitly demand otherwise.
- [ ] Preserve compatibility-driven field naming where existing clients depend on it.

### B. File Mode and Structure (Required)

- [ ] Confirm this checklist is applied only to proto files generated or modified by this skill in the current task.
- [ ] Classify file mode explicitly as either `service proto` or `message-only proto`.
- [ ] If file mode is `service proto`, enforce exactly one `service` in the file.
- [ ] If file mode is `service proto`, enforce strict file-prefix mapping: `snake_case` file prefix must match `PascalCase` `Service/Error` prefix.
- [ ] If file mode is `service proto`, enforce declaration order: `service` -> `message` -> `error enum`.
- [ ] If file mode is `message-only proto`, exempt service-only structure/error checks and record the exemption in validation notes.

### C. Route Conflict Safety (Required for `service proto`)

- [ ] Confirm each service route set stays under its own prefix namespace.
- [ ] Detect static-vs-param sibling collisions for the same method scope.
- [ ] Detect wildcard-name divergence at the same branch depth (`:id` vs `:task_id`).
- [ ] Ensure catch-all wildcards are terminal only.
- [ ] Ensure greedy wildcard routes do not shadow fixed routes unexpectedly.
- [ ] If backend target is unknown, keep routes Gin-safe by default.

### D. Reuse Decision (Required)

- [ ] Check whether an existing `entpb` message can be reused directly.
- [ ] Check whether the message should live in or reuse `shared.v1`.
- [ ] Document why a custom DTO/VO is needed when not reusing existing messages.

### E. HTTP and Binding (Required for HTTP-exposed `service proto`)

- [ ] Add `google.api.http` annotation to every exposed RPC.
- [ ] Mark URI fields with `BINDING_LOCATION_URI` when required.
- [ ] Use query binding for list filters and pagination.
- [ ] Use explicit `body` rules for write APIs (`"*"` or specific field).
- [ ] Avoid `oneof` in HTTP-exposed request/response messages.

### F. API Contract (Required)

- [ ] Confirm use case and mock validation happened before final proto output.
- [ ] Ensure list APIs include pagination parameters.
- [ ] Prefer explicit batch APIs over repeated single reads.
- [ ] Validate naming, typing, and evolvability.
- [ ] Add concise business comments for exposed RPCs, core messages, and key enum values (for generated swagger/openapi readability).
- [ ] Use `//` single-line style for these business comments by default.

### G. Error Contract (Required with mode-aware behavior)

- [ ] If file mode is `service proto`, define at least one domain error enum (or explicitly reuse one).
- [ ] If file mode is `service proto`, keep service-specific business errors in the same proto file as the owning service.
- [ ] Use shared proto errors only for cross-service/common errors.
- [ ] If file mode is `service proto`, include `*_UNSPECIFIED = 0`.
- [ ] If file mode is `service proto`, set enum `default_status`.
- [ ] If file mode is `service proto`, set per-value `status/reason/message` for key business errors.
- [ ] If file mode is `service proto`, document runtime error composition (`Join`, `JoinWithMessage`).

### H. Package, Runtime, and Codegen (Required)

- [ ] Confirm package/version layout is coherent with scaffold proto organization.
- [ ] Confirm imports align with selected annotations/features (`sphere/binding`, `sphere/errors`, etc.).
- [ ] Confirm response/error assumptions match go-sphere runtime behavior.
- [ ] Confirm design fits protocol-first generation and does not require manual generated-file edits.

### I. Final QA (Required)

- [ ] Ensure no sensitive/internal storage fields leak into external contracts.
- [ ] Ensure error outputs are machine-readable and stable.
- [ ] Ensure scaffold-fit, route-safety, and reuse decisions are explicit in the final deliverable.

## Pass/Fail Semantics

1. Every required checkbox must be satisfied.
2. Any unchecked required item means the draft is non-deliverable.
3. On failure, output must stop with `Validation Notes -> Blocking Issues` and corrected proposals.

## Mandatory Confirmation

Final output must explicitly include:

- `All required checks passed.`
