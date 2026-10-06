# Reference: Defining Proto Errors

Local copy of https://go-sphere.github.io/docs/guides/error-handling/ (synced 2026-09-07).
Covers installing `protoc-gen-sphere-errors`, declaring error enums in `.proto`, and the
annotation options. Generated Go methods, runtime behavior, and the HTTP response shape live in
`error-runtime-reference.md`.

Where a generic example here conflicts with a scaffold convention or a rule in this skill,
follow the skill.

## Installation

To install [`protoc-gen-sphere-errors`](https://github.com/go-sphere/protoc-gen-sphere-errors), use the following command:

```bash
go install github.com/go-sphere/protoc-gen-sphere-errors@latest
```

## Configuration with Buf

Add the dependency to `buf.yaml`:

```yaml
version: v2
deps:
  - buf.build/go-sphere/errors
```

Then add the plugin to `buf.gen.yaml`. This tells `buf` how to execute the plugin and where to
place the generated files.

```yaml
version: v2
managed:
  enabled: true
plugins:
  - local: protoc-gen-sphere-errors
    out: api
    opt:
      - paths=source_relative
```

## Defining Errors in `.proto`

Errors are defined as `enum` types in your `.proto` files. You can use custom options from `sphere/errors/errors.proto` to attach metadata like HTTP status codes and default messages to each error.

First, import the necessary definitions in your `.proto` file:

```protobuf
import "sphere/errors/errors.proto";
```

Next, define an `enum` for your errors.

### Example: Basic Error Enum

Here is an example of an error enum:

```protobuf
syntax = "proto3";

package shared.v1;

import "sphere/errors/errors.proto";

enum UserError {
  option (sphere.errors.default_status) = 500;  // Default status for all values
  
  USER_ERROR_UNSPECIFIED = 0;
  USER_ERROR_NOT_FOUND = 1001 [(sphere.errors.options) = {
    status: 404
    message: "User not found"
  }];
  USER_ERROR_INVALID_EMAIL = 1002 [(sphere.errors.options) = {
    status: 400
    reason: "INVALID_EMAIL"
    message: "Invalid email format"
  }];
  USER_ERROR_ALREADY_EXISTS = 1003 [(sphere.errors.options) = {
    status: 409
    reason: "USER_EXISTS"
    message: "User already exists"
  }];
}
```

### Advanced Example with Reasons

```protobuf
enum PaymentError {
  option (sphere.errors.default_status) = 500;
  
  PAYMENT_ERROR_UNSPECIFIED = 0;
  PAYMENT_ERROR_INSUFFICIENT_FUNDS = 2001 [(sphere.errors.options) = {
    status: 402
    reason: "INSUFFICIENT_FUNDS"
    message: "Insufficient funds in account"
  }];
  PAYMENT_ERROR_CARD_DECLINED = 2002 [(sphere.errors.options) = {
    status: 402
    reason: "CARD_DECLINED"
    message: "Payment card was declined"
  }];
  PAYMENT_ERROR_INVALID_AMOUNT = 2003 [(sphere.errors.options) = {
    status: 400
    reason: "INVALID_AMOUNT"
    message: "Payment amount must be positive"
  }];
}
```

### Annotation Reference

- `(sphere.errors.default_status)`: An enum-level option that sets the default HTTP status code for all values. If an error value does not have a specific status, this one will be used.
- `(sphere.errors.options)`: A value-level option to customize a specific error.
  - `status`: The HTTP status code (e.g., `400`, `404`, `500`).
  - `reason`: A machine-readable reason code for programmatic error handling.
  - `message`: A user-facing default error message.

## Error Configuration Options

### Enum Level Options

- `default_status`: Sets the default HTTP status code for all enum values that don't specify their own status

### Enum Value Options

- `status`: HTTP status code (overrides default_status)
- `reason`: Optional machine-readable reason code
- `message`: Human-readable error message for client display

## Best Practices

1. **Use meaningful error codes**: Choose enum values that clearly indicate the error type
2. **Set appropriate HTTP status codes**: Use standard HTTP status codes (400, 401, 403, 404, 500, etc.)
3. **Provide clear messages**: Write user-friendly error messages in the appropriate language
4. **Use reasons for API consumers**: Include reason strings for programmatic error handling
5. **Group related errors**: Keep related errors in the same enum for better organization
6. **Preserve original errors**: Always use `.Join()` to wrap underlying errors for better debugging

## Common HTTP Status Codes

- `400`: Bad Request - Client error, invalid input
- `401`: Unauthorized - Authentication required
- `403`: Forbidden - Permission denied
- `404`: Not Found - Resource doesn't exist
- `409`: Conflict - Resource conflict
- `422`: Unprocessable Entity - Validation failed
- `429`: Too Many Requests - Rate limiting
- `500`: Internal Server Error - Server-side error
- `502`: Bad Gateway - External service error
- `503`: Service Unavailable - Service temporarily down

