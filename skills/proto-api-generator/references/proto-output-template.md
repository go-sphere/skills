# Reference: Proto Output Template

## Purpose

Provide a strict, stable output structure for generated API proposals.

## Usage

Use this template in final responses with the same section order.
Do not skip required sections.

## 1) Scaffold Fit Decision

| Target Package | Service Prefix | Route Style | Pagination Style | Error Placement | Naming Exceptions | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| dash.v1 | `/api/admin...` | action-style (`/api/<resource>/list|create|update|detail|delete`) | `page/page_size` + `total_page` | service-local enum in same proto file | allow compatibility fields if needed | follows scaffold conventions |

Explain why this package/style is chosen.

## 2) Route Conflict Check

| Check Item | Result | Evidence |
| --- | --- | --- |
| Service prefix namespace isolation | pass | all `AdminService` routes stay under `/api/admin...` |
| Static vs Param sibling conflict | pass | no sibling static/param collision per method scope |
| Wildcard name consistency | pass | use `:task_id` consistently under `/v1/tasks/...` |
| Catch-all terminal-only | pass | no non-terminal `*` segments |
| Greedy shadowing risk | pass | fixed routes declared before greedy patterns (if applicable) |
| Backend portability | pass | route set is Gin-safe and works for Fiber/Echo matching rules |

## 3) Error Placement Check

| Check Item | Result | Evidence |
| --- | --- | --- |
| Service-local business errors | pass | `AdminError` is defined in `dash/v1/admin.proto` |
| Shared errors only for common semantics | pass | no service-only errors pushed to `shared` |

## 4) Comment Coverage Check

| Check Item | Result | Evidence |
| --- | --- | --- |
| RPC business comments | pass | each exposed RPC has short `//` purpose/behavior comment |
| Message business comments | pass | externally visible request/response messages are documented with `//` comments |
| Enum business comments | pass | key business error/status enum values include `//` intent comments |

## 5) API Capability Matrix

| Use Case | RPC | HTTP | Request Key Fields | Response Key Fields | Index Driver |
| --- | --- | --- | --- | --- | --- |
| ListAdmins | ListAdmins | GET /api/admin/list | page, page_size | admins, total_size, total_page | (id desc) |

## 6) Mock JSON

### 5.1 List Response

```json
{
  "admins": [],
  "total_size": 0,
  "total_page": 0
}
```

### 5.2 Detail Response

```json
{
  "admin": {
    "id": 10001,
    "username": "root"
  }
}
```

### 5.3 Error Response Example

```json
{
  "status": 400,
  "code": 1001,
  "error": "ADMIN_ERROR_CANNOT_DELETE_SELF",
  "message": "cannot delete current admin"
}
```

## 7) Reuse Decision

| Domain Object | Reuse Choice | Location | Reason |
| --- | --- | --- | --- |
| Admin | Reuse entpb | entpb.Admin | Existing model already used in dashboard APIs |
| User | Reuse shared | shared.v1.User | Shared across services |
| AdminSummary | Custom DTO | dash/v1 | Custom projection for specific UI payload |

Rules:

1. Prefer `entpb` first.
2. Prefer `shared.v1` for cross-service reuse.
3. Use custom DTO only with explicit justification.

## 8) Proto3 Contract

```proto
syntax = "proto3";

package dash.v1;

import "buf/validate/validate.proto";
import "entpb/entpb.proto";
import "google/api/annotations.proto";
import "sphere/binding/binding.proto";
import "sphere/errors/errors.proto";

service AdminService {
  // List admins with scaffold-style pagination for dashboard table pages.
  rpc ListAdmins(ListAdminsRequest) returns (ListAdminsResponse) {
    option (google.api.http) = {get: "/api/admin/list"};
  }

  // Get one admin detail by primary id.
  rpc GetAdmin(GetAdminRequest) returns (GetAdminResponse) {
    option (google.api.http) = {get: "/api/admin/detail/{id}"};
  }
}

// Query input for admin list page.
message ListAdminsRequest {
  option (sphere.binding.default_location) = BINDING_LOCATION_QUERY;

  int64 page = 1 [(buf.validate.field).int64.gte = 0];
  int64 page_size = 2 [(buf.validate.field).int64.gte = 0];
}

// List page payload for admins.
message ListAdminsResponse {
  repeated entpb.Admin admins = 1;
  int64 total_size = 2;
  int64 total_page = 3;
}

message GetAdminRequest {
  int64 id = 1 [(sphere.binding.location) = BINDING_LOCATION_URI];
}

message GetAdminResponse {
  entpb.Admin admin = 1;
}

// Domain errors for AdminService business operations.
enum AdminError {
  option (sphere.errors.default_status) = 500;

  ADMIN_ERROR_UNSPECIFIED = 0;
  ADMIN_ERROR_CANNOT_DELETE_SELF = 1001 [(sphere.errors.options) = {
    status: 400
    message: "cannot delete current admin"
  }];
}
```

## 9) Error Enum Design

| Enum Value | Code | HTTP Status | Reason | Message | Trigger Condition |
| --- | --- | --- | --- | --- | --- |
| ADMIN_ERROR_CANNOT_DELETE_SELF | 1001 | 400 | (optional) | cannot delete current admin | caller tries to delete self |

Runtime usage guidance:

- `AdminError_ADMIN_ERROR_CANNOT_DELETE_SELF.Join(err)`
- `AdminError_ADMIN_ERROR_CANNOT_DELETE_SELF.JoinWithMessage("...", err)`

## 10) Ent -> Proto Mapping

| Ent Field | Proto Field | Exposed | Notes |
| --- | --- | --- | --- |
| id | id | yes | direct mapping via entpb |
| username | username | yes | direct mapping via entpb |
| password | password | conditional | clear/mask if response must not expose sensitive data |

## 11) Validation Notes

Always include:

- Assumptions
- Risks
- Open Questions

## 12) Blocking Issues (Only if Any Required Check Fails)

Use this section only when fail-fast is triggered.

Format:

- Issue: `<rule that failed>`
- Why blocked: `<why output is non-deliverable>`
- Correction: `<revised route/error/schema proposal>`

If this section exists, the draft is non-deliverable.

## 13) Mandatory Confirmation

Include exactly one of the following:

- `All required checks passed.`
- `Draft blocked due to required-check failures.`
