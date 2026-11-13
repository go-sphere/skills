# Reference: Server-Streaming (SSE) Responses

Local copy of https://go-sphere.github.io/docs/guides/api-definitions/ (synced 2026-09-07).
Covers server-streaming RPCs over SSE, the API definition best practices, and buf integration.
Unary binding rules live in `api-binding-basics-reference.md`.

Where a generic example here conflicts with a scaffold convention or a rule in this skill,
follow the skill.
## Server-Streaming Responses

Add `stream` to the reply type to expose a server-streaming RPC as SSE:

```protobuf
rpc Watch(WatchRequest) returns (stream WatchResponse) {
  option (google.api.http) = { get: "/v1/watch/{topic}" };
}
```

`protoc-gen-sphere` generates a push-style service method:

```go
Watch(context.Context, *WatchRequest, func(*WatchResponse) error) error
```

Request fields use the same URI, query, header, form, and JSON binding rules as
unary methods. Each `send` becomes one SSE JSON event. The default runtime ends
a successful stream with a `done` event and a committed failure with an `error`
event. See the official [Server Streaming](https://go-sphere.github.io/docs/guides/server-streaming/)
guide for implementation, wire format, resume, and operational guidance.

Only server-streaming is supported by the HTTP generator. Client-streaming and
bidirectional RPCs are skipped with a warning. Do not use `response_body` on a
stream: the generator warns and sends each whole reply message.

## Best Practices

1. **Use meaningful field names**: Field names become tag values, so use clear, descriptive names
2. **Choose appropriate binding locations**:
   - `BINDING_LOCATION_URI`: For resource identifiers in the path
   - `BINDING_LOCATION_QUERY`: For optional filters and pagination
   - `BINDING_LOCATION_JSON`: For complex data structures and create/update operations
3. **Be consistent with HTTP method semantics**:
   - GET: Retrieve data (no body, use query params for filters)
   - POST: Create new resources (use body for data)
   - PUT: Replace entire resources (use body for new data)
   - PATCH: Partial updates (use body for changes)
   - DELETE: Remove resources (no body, use path params for ID)

4. **Avoid overly broad wildcards** in paths to prevent ambiguous routing
5. **Prefer explicit body field** (`body: "fieldName"`) when payloads are nested
6. **Prefer not to use `oneof`** in HTTP-exposed request/response messages. Tags land on wrapper structs (`Message_Field`); generated handlers bind the parent request, so QUERY/URI/HEADER oneof members are not filled by `BindQuery`/`BindURI`/`BindHeader`. JSON codecs also handle oneof awkwardly on the wire.
7. **Never combine `body:` with `BINDING_LOCATION_FORM` fields.** Form parameters make the method body-less; declaring a body warns and fails under `fail_on_warn`. Split into two RPCs if you need both.
8. **Use only server response streams for SSE**. Model uploads and bidirectional conversations as unary HTTP operations, WebSockets, or a separate transport.
9. **Treat stream termination as part of the contract**. Clients should understand `done`, `error`, and an interrupted connection without either terminal event.


## Integration with buf

Add the required dependencies to your `buf.yaml`:

```yaml
version: v2
deps:
  - buf.build/googleapis/googleapis
  - buf.build/go-sphere/binding
```

Configure HTTP generation in `buf.gen.yaml`:

```yaml
version: v2
managed:
  enabled: true
plugins:
  - local: protoc-gen-sphere
    out: api
    opt:
      - paths=source_relative
```

Run `protoc-gen-sphere-binding` from a second template after `protoc-gen-go` has written the structs. Official templates use `buf.binding.yaml`:

```yaml
version: v2
managed:
  enabled: true
plugins:
  - local: protoc-gen-sphere-binding
    out: api
    opt:
      - paths=source_relative
      - out=api
```
