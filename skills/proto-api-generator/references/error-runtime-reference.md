# Reference: Error Runtime Behavior

Local copy of https://go-sphere.github.io/docs/guides/error-handling/ (synced 2026-09-07).
Covers the generated Go methods, returning and composing errors in a service, and the JSON error
response clients receive. Declaring the enums and their annotations lives in
`error-definition-reference.md`.

Where a generic example here conflicts with a scaffold convention or a rule in this skill,
follow the skill.

## Using the Generated Code

After running `buf generate`, the plugin will create a file named `{proto_name}_errors.pb.go` (e.g., `user_errors.pb.go`). This file contains a Go enum and several helper methods that allow you to use it as a standard Go error.

### Generated Methods

For each `enum UserError`, the following methods are generated:

- `Error() string`: Implements Go's `error` interface. Returns `reason` when set; otherwise the enum value name.
- `GetCode() int32`: Returns the numeric enum value (e.g., `1001`).
- `GetStatus() int32`: Returns the configured HTTP status code.
- `GetMessage() string`: Returns the default error message.
- `Join(errs ...error) error`: Wraps one or more source errors with `httpx.NewError`. This is the recommended way to return an error while preserving the original cause.
- `JoinWithMessage(msg string, errs ...error) error`: Similar to `Join`, but allows you to provide a custom, dynamic message at runtime.

There is no generated `GetReason()` method. The enum itself implements `httpx.StatusError`, `httpx.CodeError`, and `httpx.MessageError`, so returning it from a service method is enough for `httpz` to set status, code, and message.

### Example: Returning an Error in Go

In your service implementation, you can now return one of the generated errors.

```go
package service

import (
    "context"
    "fmt"
    sharedv1 "myproject/api/shared/v1" // Import the generated package
)

func (s *UserService) GetUser(ctx context.Context, req *GetUserRequest) (*User, error) {
    if req.Id <= 0 {
        return nil, sharedv1.UserError_USER_ERROR_INVALID_ID.Join(
            fmt.Errorf("user ID must be positive, got: %d", req.Id))
    }
    
    user, err := s.userRepo.GetByID(ctx, req.Id)
    if err != nil {
        if errors.Is(err, sql.ErrNoRows) {
            return nil, sharedv1.UserError_USER_ERROR_NOT_FOUND.Join(err)
        }
        return nil, fmt.Errorf("failed to get user: %w", err)
    }
    
    return user, nil
}

func (s *UserService) CreateUser(ctx context.Context, req *CreateUserRequest) (*User, error) {
    if !isValidEmail(req.Email) {
        return nil, sharedv1.UserError_USER_ERROR_INVALID_EMAIL.JoinWithMessage(
            fmt.Sprintf("email '%s' is not valid", req.Email), nil)
    }
    
    // Check if user already exists
    existing, _ := s.userRepo.GetByEmail(ctx, req.Email)
    if existing != nil {
        return nil, sharedv1.UserError_USER_ERROR_ALREADY_EXISTS.Join(
            fmt.Errorf("user with email %s already exists", req.Email))
    }
    
    user, err := s.userRepo.Create(ctx, req)
    if err != nil {
        return nil, fmt.Errorf("failed to create user: %w", err)
    }
    
    return user, nil
}
```

### HTTP Error Response

When this error is handled by `httpz.WithJson`, it is converted into an HTTP response with the enum's status code and this JSON body:

```json
{
  "success": false,
  "code": 1001,
  "message": "User not found"
}
```

`ErrorResponse.Error` is populated with `err.Error()` only when `httpz.SetDebugMode(true)`. Unclassified errors (a plain `error` that does not implement `httpx.CodeError` / `httpx.MessageError`) report `code: 0` and the generic HTTP status text, so driver and database strings are not leaked to clients.

Use `httpz.SetDefaultErrorParser` in the template (see `internal/pkg/render/errors.go`) to map validation and persistence errors before the default `httpx.ParseError` fallback.

## Error Composition

You can compose multiple errors using the generated methods:

```go
// Simple error with context
return nil, UserError_USER_ERROR_NOT_FOUND.Join(err)

// Error with custom message
return nil, UserError_USER_ERROR_INVALID_EMAIL.JoinWithMessage(
    fmt.Sprintf("Invalid email format: %s", email), validationErr)

// Multiple errors can be joined
return nil, UserError_USER_ERROR_VALIDATION_FAILED.Join(
    emailErr, passwordErr, ageErr)
```

The generated error types implement `httpx`'s error interfaces so `httpz` can produce consistent JSON responses across every adapter.
