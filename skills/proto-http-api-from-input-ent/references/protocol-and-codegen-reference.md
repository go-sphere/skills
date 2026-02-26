# Reference: Protocol and Code Generation

## Purpose

Provide a full local copy of go-sphere protocol-first and code generation guidance, so API design decisions stay aligned with the generator pipeline.

## Source

- URL: https://go-sphere.github.io/docs/concepts/protocol-and-codegen/
- Upstream markdown: https://raw.githubusercontent.com/go-sphere/go-sphere.github.io/master/content/docs/concepts/protocol-and-codegen.md
- Last synced by this skill update: 2026-02-25

## How To Use This Reference

1. Use this when defining package layout and generator expectations.
2. Ensure proto output can pass through the intended plugin chain without manual patching.
3. Keep generated code as a product of proto definitions, not handwritten drift.

## Skill Override Note

If a generic example in the upstream copy conflicts with this skill's scaffold conventions or hard gates, follow the skill's rules and keep this reference as background material.

## Official Document (Full Local Copy)

Sphere follows a "protocol-first" approach where you define your APIs once in Protobuf and generate everything else from those definitions. This ensures consistency across your entire stack and reduces boilerplate code.

## Core Philosophy

The fundamental principle is: **Define once, generate everywhere**.

Instead of writing HTTP handlers, request/response structs, validation code, and documentation separately, you:

1. **Define services and messages** in `.proto` files
2. **Annotate with HTTP mappings** using `google.api.http`
3. **Configure field binding** with Sphere binding options
4. **Generate everything else** using protoc plugins

This approach provides:
- **Consistency**: All layers use the same contracts
- **Type Safety**: Compile-time guarantees across the stack
- **Documentation**: API docs generated from source of truth
- **Client SDKs**: Automatically generated for multiple languages
- **Reduced Boilerplate**: No manual HTTP handler writing

## Protocol as Contract

Your `.proto` files serve as the authoritative definition of:
- **Data structures** (messages)
- **API operations** (services and methods)
- **Error conditions** (enums with metadata)
- **HTTP mapping** (via annotations)
- **Field constraints** (via validation rules)

## Code Generation Pipeline

### Generator Chain

The code generation happens in a specific order:

1. **protoc-gen-go**: Generate base Go types
2. **[protoc-gen-sphere-binding](https://api.github.com/repos/go-sphere/protoc-gen-sphere-binding)**: Add struct tags for binding
3. **[protoc-gen-sphere](https://api.github.com/repos/go-sphere/protoc-gen-sphere)**: Generate HTTP handlers and routing
4. **[protoc-gen-sphere-errors](https://api.github.com/repos/go-sphere/protoc-gen-sphere-errors)**: Generate error types and handling
5. **[protoc-gen-route](https://api.github.com/repos/go-sphere/protoc-gen-route)**: Generate custom routing (optional)

### What Gets Generated

From your proto definitions, you automatically get:

**Server-side Code:**
- Service interfaces to implement
- HTTP handlers with proper routing
- Request binding with validation
- Response marshaling with proper headers
- Error handling with consistent formatting

**Client-side Code:**
- OpenAPI/Swagger documentation
- TypeScript SDKs (optional)
- Go client stubs (if needed)
- Validation schemas for frontend use

**Developer Tools:**
- Interactive documentation via Swagger UI
- API testing endpoints
- Type definitions for IDE support

## Benefits of This Approach

### Type Safety
- Compile-time verification of API contracts
- No runtime surprises from mismatched types
- Automatic validation of required fields
- IDE support with autocomplete and error checking

### Consistency
- Single source of truth for API definitions
- Consistent naming across all generated code
- Uniform error handling patterns
- Standardized HTTP response formats

### Developer Experience
- Faster iteration cycles
- Less boilerplate code to maintain
- Clear separation of concerns
- Automatic documentation updates

### Scalability
- Easy to add new services and methods
- Version management built-in
- Multiple output targets from one definition
- Team coordination through shared contracts

## Protocol Organization

### Recommended Structure
```
proto/
├── shared/v1/           # Common messages
│   ├── user.proto
│   └── common.proto
├── api/v1/              # Service definitions
│   ├── user_service.proto
│   └── auth_service.proto
└── errors/v1/           # Error definitions
    ├── user_errors.proto
    └── common_errors.proto
```

### Versioning Strategy
- Use explicit version packages (`v1`, `v2`)
- Keep shared types separate from services
- Plan for backwards compatibility
- Document breaking changes clearly

## Best Practices

### Proto Design
1. **Clear naming**: Use descriptive, consistent names
2. **Proper grouping**: Organize by domain and version
3. **Forward compatibility**: Design for future evolution
4. **Documentation**: Comment services, methods, and fields

### Code Generation
1. **Frequent regeneration**: Update generated code early and often
2. **Don't edit generated files**: All changes go in `.proto` files
3. **Version control**: Commit both `.proto` and generated files
4. **Automation**: Integrate generation into build process

## Related Guides

For detailed information on:
- **Defining HTTP APIs**: See [API Definitions](go-sphere-api-definitions-reference.md)
- **Error handling**: See [Error Handling](go-sphere-error-handling-reference.md)
- **Proto packages**: See [Proto Packages & Runtime](proto-packages-and-runtime-reference.md)
