# Reference: HTTP Path Mapping and Request Binding

Local copy of https://go-sphere.github.io/docs/guides/api-definitions/ (synced 2026-09-07).
Covers `google.api.http` path mapping, HTTP method semantics, and where each field binds from.
Body and response shaping live in `api-binding-advanced-reference.md`. Streaming lives in
`api-streaming-reference.md`.

Where a generic example here conflicts with a scaffold convention or a rule in this skill,
follow the skill.

Sphere defines HTTP interfaces for services using standard Protobuf plus `google.api.http`
annotations. The rules below map gRPC methods to RESTful HTTP endpoints.
## Getting Started: A Basic Example

To expose a gRPC method as an HTTP endpoint, you need to define it in a `.proto` file and add an HTTP annotation.

Here is a basic example of a `TestService` that defines a simple `RunTest` method, exposed as an HTTP `POST` request.

```protobuf
syntax = "proto3";

package your.service.v1;

import "google/api/annotations.proto";
import "sphere/binding/binding.proto";

// The Test service definition.
service TestService {
  // RunTest method
  rpc RunTest(RunTestRequest) returns (RunTestResponse) {
    option (google.api.http) = {
      post: "/v1/test/{path_test1}"
      body: "*"
    };
  }
}

// The request message for the RunTest RPC.
message RunTestRequest {
  // URI path parameter
  string path_test1 = 1 [(sphere.binding.location) = BINDING_LOCATION_URI];
  // Request body field
  string field_test1 = 2;
  // Query parameter
  string query_test1 = 3 [(sphere.binding.location) = BINDING_LOCATION_QUERY];
}

// The response message for the RunTest RPC.
message RunTestResponse {
  string field_test1 = 1;
  string query_test1 = 3;
}
```

### Key Components

1. **`import "google/api/annotations.proto";`**: This import is required to use HTTP annotations.
2. **`import "sphere/binding/binding.proto";`**: This import is required for binding annotations.
3. **`service TestService { ... }`**: Defines your gRPC service.
4. **`rpc RunTest(...) returns (...)`**: Defines a method within the service.
5. **`option (google.api.http) = { ... };`**: This is the core of the HTTP mapping.
   - **`post: "/v1/test/{path_test1}"`**: This specifies that the `RunTest` method should be exposed as an HTTP `POST`
   - **`body: "*"`**: Indicates that the entire request message (except URI params) should be sent as JSON body
6. **`[(sphere.binding.location) = ...]`**: This annotation specifies where the field should be bound from in the HTTP request.

Sphere uses these definitions to automatically generate server-side stubs and routing information.

## URL Path Mapping

Sphere converts gRPC-Gateway style URL paths from your `.proto` definitions into `httpx` routes (`:param` and `*wildcard`). Official templates serve those routes through the `stdx` (net/http) engine; the Gin, Fiber, Echo, and Hertz adapters accept the same patterns.

The following table shows how Protobuf URL paths are translated:

| Protobuf Path Template                           | Generated httpx Route                       |
|--------------------------------------------------|---------------------------------------------|
| `/users/{user_id}`                               | `/users/:user_id`                           |
| `/users/{user_id}/posts/{post_id}`               | `/users/:user_id/posts/:post_id`            |
| `/files/{file_path=**}`                          | `/files/*file_path`                         |
| `/files/{name=*}`                                | `/files/:name`                              |
| `/static/{path=assets/*}`                        | `/static/assets/:path`                      |
| `/static/{path=assets/**}`                       | `/static/assets/*path`                      |
| `/projects/{project_id}/locations/{location=**}` | `/projects/:project_id/locations/*location` |
| `/api/{version=v1}/users`                        | `/api/v1/users`                             |
| `/users/{user_id}/posts/{post_id=drafts}`        | `/users/:user_id/posts/drafts`              |
| `/docs/{path=guides/**}`                         | `/docs/guides/*path`                        |

## HTTP Methods and Body Binding

### Request Binding Behavior

Different HTTP methods have different default binding behaviors:

#### GET, HEAD, DELETE, and OPTIONS Requests
- Path parameters must be top-level fields marked with `BINDING_LOCATION_URI`. Nested templates such as `{user.id}` are not supported.
- Remaining fields must be marked `BINDING_LOCATION_QUERY`, `BINDING_LOCATION_HEADER`, or `BINDING_LOCATION_FORM` (or the message `default_location`). Unmarked fields fail generation.
- No request body is expected. JSON-bound fields on these methods fail generation.
- If `google.api.http` still declares `body`, `protoc-gen-sphere` warns (or fails with `fail_on_warn`) and generates the handler **without** `BindJSON`

#### POST, PUT, and PATCH Requests
- Path parameters are bound to fields marked with `BINDING_LOCATION_URI`
- By default, all other fields are expected in the JSON request body
- You can override this with explicit binding locations
- If `google.api.http` declares no `body` at all, `protoc-gen-sphere` warns (or fails with `fail_on_warn`)

#### Methods With Form Parameters

A method that has **any** `BINDING_LOCATION_FORM` field is treated as body-less,
regardless of HTTP method. This is a hard rule in `buildHTTPRule`:

- Declaring `body:` on such a method emits `body should not be declared when form
  parameters are present` — a warning normally, a **hard generation failure**
  under `fail_on_warn`.
- The resolved body is cleared and `HasBody` is forced to `false`, so the
  generated handler emits `ctx.BindForm` and **never** `ctx.BindJSON`.
- The Swagger annotation becomes `// @Accept mpfd` (multipart form data) instead
  of `// @Accept json`.

So form uploads and JSON bodies are mutually exclusive on one method:

```protobuf
// CORRECT - form upload, no body declared
rpc UploadAvatar(UploadAvatarRequest) returns (UploadAvatarResponse) {
  option (google.api.http) = {
    post: "/api/v1/users/{user_id}/avatar"
    // no body: field
  };
}

message UploadAvatarRequest {
  int64 user_id = 1 [(sphere.binding.location) = BINDING_LOCATION_URI];
  bytes file = 2 [(sphere.binding.location) = BINDING_LOCATION_FORM];
  string caption = 3 [(sphere.binding.location) = BINDING_LOCATION_FORM];
}
```

```protobuf
// WRONG - body plus form parameters; warns, and fails under fail_on_warn
option (google.api.http) = {
  post: "/api/v1/users/{user_id}/avatar"
  body: "*"
};
```

If a request genuinely needs both a structured JSON payload and a file upload,
split it into two RPCs rather than mixing the binding locations.

### Field Binding Locations

Use the `sphere.binding.location` annotation to control where each field is bound from:

```protobuf
message GetUserRequest {
  // URI path parameter
  int64 user_id = 1 [(sphere.binding.location) = BINDING_LOCATION_URI];
  // Query parameter
  repeated string fields = 2 [(sphere.binding.location) = BINDING_LOCATION_QUERY];
  // Header value
  string auth_token = 3 [(sphere.binding.location) = BINDING_LOCATION_HEADER];
}

message UpdateUserRequest {
  // URI path parameter
  int64 user_id = 1 [(sphere.binding.location) = BINDING_LOCATION_URI];
  // JSON body (default for POST/PUT/PATCH)
  User user = 2;
}
```

Available binding locations:
- `BINDING_LOCATION_URI`: Path parameters
- `BINDING_LOCATION_QUERY`: Query string parameters
- `BINDING_LOCATION_JSON`: JSON request body (default for non-GET methods)
- `BINDING_LOCATION_HEADER`: HTTP headers
- `BINDING_LOCATION_FORM`: Form data

