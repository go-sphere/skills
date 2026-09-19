# Reference: Proto Packages and Runtime

## Purpose

Provide a full local copy of go-sphere package/runtime concepts that affect binding annotations, runtime error shaping, and handler behavior.

## Source

- URL: https://go-sphere.github.io/docs/concepts/proto-packages-and-runtime/
- Upstream markdown: https://raw.githubusercontent.com/go-sphere/go-sphere.github.io/master/content/docs/concepts/proto-packages-and-runtime.md
- Last synced by this skill update: 2026-09-07

## How To Use This Reference

1. Use this when choosing `sphere/binding`, `sphere/errors`, and related options.
2. Validate that proposed API contracts map cleanly to Sphere runtime request/response behavior.
3. Check runtime envelope/error assumptions before finalizing proto design.

## When To Load

Load this reference when the design depends on binding annotations, runtime response envelopes, generated handler behavior, or custom runtime extensibility assumptions.

## Skill Override Note

If a generic example in the upstream copy conflicts with this skill's scaffold conventions or hard gates, follow the skill's rules and keep this reference as background material.

## Table of Contents

- [Proto Packages Overview](#proto-packages-overview)
- [Runtime Layer](#runtime-layer)

## Official Document (Full Local Copy)

Sphere extends Protobuf with specialized packages and provides a runtime layer that makes building HTTP APIs clean and efficient.

## Proto Packages Overview

Sphere includes focused Protobuf packages that keep HTTP binding, errors, and custom options declarative. These annotations power Sphere's generators and help maintain consistent, type-safe APIs.

### sphere/binding

**Purpose:**
- Declare where each field binds from (URI, query, body, header, form)
- Set message/oneof defaults and auto-tags for generated structs
- Work seamlessly with Sphere's request binding helpers

**Use when:**
- You want explicit, generator-driven request parsing rules
- You prefer consistent struct tags without hand editing

**Example:**
```protobuf
message GetUserRequest {
  int64 user_id = 1 [(sphere.binding.location) = BINDING_LOCATION_URI];
  repeated string fields = 2 [(sphere.binding.location) = BINDING_LOCATION_QUERY];
  string auth_token = 3 [(sphere.binding.location) = BINDING_LOCATION_HEADER];
}
```

See [API Definitions Guide](go-sphere-api-definitions-reference.md) for detailed examples.

### sphere/errors

**Purpose:**
- Define typed error enums with HTTP status, reason, and message
- Generate helpers to wrap causes and produce uniform JSON errors
- Map error codes to HTTP status codes automatically

**Use when:**
- You need consistent error shapes across services and clients
- You want programmatic access to status/code/reason/message

**Example:**
```protobuf
enum UserError {
  option (sphere.errors.default_status) = 500;
  
  USER_ERROR_NOT_FOUND = 1001 [(sphere.errors.options) = {
    status: 404
    reason: "USER_NOT_FOUND"
    message: "User not found"
  }];
}
```

See [Error Handling Guide](go-sphere-error-handling-reference.md) for implementation details.

### sphere/options

**Purpose:**
- Attach simple key/value metadata to RPC methods
- Let generators consume options for advanced routing or transports

**Use when:**
- You build adapters beyond HTTP
- You need custom routing hints or generator options

## Runtime Layer

Sphere's HTTP runtime is split in two:

- [`httpx`](https://github.com/go-sphere/httpx) — router/context/handler interfaces, a `stdx` (net/http) engine, and adapters for Gin, Fiber, Echo, and Hertz
- `server/httpz` — JSON envelopes plus `WithJson`, `WithSSE`, and `AbortWithJsonError` on top of `httpx`

Official templates serve on `httpx/stdx` (net/http), but generated code talks to `httpx`, not to a concrete framework's context.

### Core Components

**Response Wrappers:**
- `httpz.WithJson[T]`: wraps a handler returning `(T, error)` and serializes success to `DataResponse[T]`
- `httpz.WithSSE[T]`: wraps a two-phase server-streaming handler; messages become JSON SSE events and completion/failure becomes a terminal `done`/`error` event
- `httpz.WithSSEEagerCommit`: option for push-style streams that must commit and start heartbeats before their first reply; producer failures then become in-stream errors
- `httpz.AbortWithJsonError`: normalizes errors to `ErrorResponse` with HTTP status, application `code`, and a user-facing `message`

**Request Binding:**
- `httpx.Context` methods: `BindJSON`, `BindQuery`, `BindURI`, `BindHeader`, `BindForm`
- Struct tags come from `sphere/binding` via `protoc-gen-sphere-binding`

**Server Features:**
- **Docs Server**: auxiliary HTTP server for Swagger UI
- **File / proxy helpers**: `server/service/file`, `server/service/reverseproxy`
- **Middleware**: auth, CORS, online tracking, rate limiting, selector

### Typical Request Flow

1. **Protobuf + [`protoc-gen-sphere`](https://github.com/go-sphere/protoc-gen-sphere)** generate handler plumbing
2. **Request arrives** at an `httpx` adapter (`stdx` by default)
3. **Handler binds** request data to generated structs (using sphere/binding tags)
4. **Service method** executes business logic, returns data or a typed error
5. **`httpz.WithJson`** writes `DataResponse` or routes the error through `AbortWithJsonError`

For `returns (stream Reply)` methods, the generated handler instead prepares an
`httpz.SSEStream[*Reply]`, then calls the service with a `send` callback. Binding
errors remain ordinary JSON errors; once the SSE response is committed, later
failures are terminal `error` events. See the official
[Server Streaming](https://go-sphere.github.io/docs/guides/server-streaming/) guide.

### Example Handler

```go
// Generated by protoc-gen-sphere
func _UserService_GetUser0_HTTP_Handler(srv UserServiceHTTPServer) httpx.Handler {
    return httpz.WithJson(func(ctx httpx.Context) (*User, error) {
        var in GetUserRequest
        if err := ctx.BindHeader(&in); err != nil {
            return nil, err
        }
        if err := ctx.BindQuery(&in); err != nil {
            return nil, err
        }
        if err := ctx.BindURI(&in); err != nil {
            return nil, err
        }
        return srv.GetUser(ctx.Context(), &in)
    })
}
```

### Extensibility

- **Custom Router Types**: swap the default `stdx` engine for Gin, Fiber, Echo, or Hertz via `httpx` adapters and [`protoc-gen-sphere`](https://github.com/go-sphere/protoc-gen-sphere) `router_type` / `context_type` flags
- **Response Envelope**: override `data_resp_type` / `error_resp_type` / `server_handler_func`
- **Streaming Wrapper**: override `stream_handler_func` / `stream_type` for generated server streams
- **Error Parser**: `httpz.SetDefaultErrorParser` to merge validation or domain-specific errors
- **Debug leaks**: `httpz.SetDebugMode(true)` includes `err.Error()` in `ErrorResponse.Error`; production leaves it empty

See the official [HTTP Runtime](https://go-sphere.github.io/docs/guides/http-runtime) guide for envelopes, debug mode, and adapter wiring.
