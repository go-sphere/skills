# Reference: Binding Configuration and Body Shaping

Local copy of https://go-sphere.github.io/docs/guides/api-definitions/ (synced 2026-09-07).
Covers message-level binding defaults, custom struct tags, request body patterns, and response
body patterns. Path mapping and field binding locations live in
`api-binding-basics-reference.md`.

Where a generic example here conflicts with a scaffold convention or a rule in this skill,
follow the skill.
## Advanced Binding Configuration

### Message-Level Defaults

You can set default binding behavior for entire messages:

```protobuf
message SearchUsersRequest {
  option (sphere.binding.default_location) = BINDING_LOCATION_QUERY;
  option (sphere.binding.default_auto_tags) = "form";
  
  string name = 1;        // Will be bound from query by default
  int32 age = 2;          // Will be bound from query by default
  string email = 3;       // Will be bound from query by default
}
```

### Custom Struct Tags

Add custom Go struct tags using the `auto_tags` annotation:

```protobuf
message DatabaseModel {
  option (sphere.binding.default_auto_tags) = "db";
  
  string name = 1;     // Generated: `db:"name" json:"name"`
  string email = 2;    // Generated: `db:"email" json:"email"`
}
```

## Request Body Patterns

### Full Body Binding
Most common for create/update operations:

```protobuf
rpc CreateUser(CreateUserRequest) returns (User) {
  option (google.api.http) = {
    post: "/v1/users"
    body: "*"  // Entire request message as JSON body
  };
}
```

### Specific Field as Body
When you want only one field as the body:

```protobuf
rpc UpdateUserProfile(UpdateUserProfileRequest) returns (User) {
  option (google.api.http) = {
    put: "/v1/users/{user_id}/profile"
    body: "profile"  // Only the 'profile' field as JSON body
  };
}

message UpdateUserProfileRequest {
  int64 user_id = 1 [(sphere.binding.location) = BINDING_LOCATION_URI];
  UserProfile profile = 2;  // This becomes the JSON body
}
```

## Response Body Patterns

### Default Response
By default, the entire response message is returned as JSON:

```protobuf
rpc GetUser(GetUserRequest) returns (User) {
  option (google.api.http) = { get: "/v1/users/{id}" };
}
// Returns: {"id": 1, "name": "John", "email": "john@example.com"}
```

### Specific Field as Response Body
You can return only a specific field:

```protobuf
rpc GetUserName(GetUserNameRequest) returns (GetUserNameResponse) {
  option (google.api.http) = {
    get: "/v1/users/{id}/name"
    response_body: "name"
  };
}

message GetUserNameResponse {
  string name = 1;  // Only this field is returned
}
// Returns: "John Doe" (just the string, not wrapped in JSON object)
```

