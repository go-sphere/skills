# Reference: Router Path Conflict Rules (Gin / Fiber / Echo)

## Purpose

Prevent generated HTTP paths from causing runtime router conflicts or ambiguous matches across Go router backends used by Sphere (`gin`, `fiber`, `echo`).

## When To Load

Load this reference whenever the output includes service routes, path templates, wildcard segments, or backend portability claims.

## Source

- Gin source (router conflict/panic rules): https://raw.githubusercontent.com/gin-gonic/gin/master/tree.go
- HttpRouter README (Gin radix behavior model): https://raw.githubusercontent.com/julienschmidt/httprouter/master/README.md
- Fiber routing guide: https://raw.githubusercontent.com/gofiber/fiber/v2/docs/guide/routing.md
- Echo routing guide: https://raw.githubusercontent.com/labstack/echox/master/website/docs/guide/routing.md
- Last synced by this skill update: 2026-02-25

## Why This Matters

A proto path that is syntactically valid can still fail at runtime, for example in Gin with panic patterns such as:

- `':task_id' in new path '/v1/tasks/:task_id/risks' conflicts with existing wildcard ':id' ...`

This skill must pre-check route compatibility before finalizing paths.

## Table of Contents

- [Gin / HttpRouter Rules (Strict)](#gin--httprouter-rules-strict)
- [Fiber Rules (Order-sensitive)](#fiber-rules-order-sensitive)
- [Echo Rules (Priority-driven)](#echo-rules-priority-driven)
- [Cross-Backend Design Rules (Required)](#cross-backend-design-rules-required)
- [Pre-Delivery Route Conflict Check](#pre-delivery-route-conflict-check)
- [Required Fail-Fast Rule](#required-fail-fast-rule)

## Gin / HttpRouter Rules (Strict)

### Conflict-prone rules

1. Do not mix static and param routes for the same segment under the same method scope.
   - Example conflict pattern: `/user/new` vs `/user/:user`.
2. Keep wildcard name consistent at the same path depth/branch.
   - Example risky pair: `/v1/tasks/:id` and `/v1/tasks/:task_id/risks`.
3. Allow only one wildcard token per segment.
4. Wildcards must be named (no empty `:` or `*`).
5. Catch-all (`*name`) must appear only at the end of the path.

### Safe patterns

1. Prefer a canonical param name per resource branch (`:task_id` everywhere on `/tasks/...`).
2. Avoid sibling static-vs-param segment collisions for the same method.
3. Avoid catch-all routes in API contracts unless explicitly required.

## Fiber Rules (Order-sensitive)

1. Route declaration order matters.
2. Put fixed/static routes before variable routes.
3. Greedy params (`*`, `+`) can shadow more specific patterns if declared first.
4. Escape special parameter characters when needed as literals (for example custom method suffixes).

## Echo Rules (Priority-driven)

1. Match priority is `Static` > `Param` > `Match-any`.
2. Match-any (`*`) has one effective wildcard behavior in a route.
   - Multiple `*` tokens behave as first-wildcard-to-end semantics.
3. Although routes can be declared in any order, ambiguous wildcard design should still be avoided.

## Cross-Backend Design Rules (Required)

Apply these rules to every generated route set:

1. Use one stable service-level prefix namespace (for example all `AdminService` routes under `/api/admin...`).
2. Use one canonical wildcard name per resource level.
3. Prefer explicit static action suffixes after stable resource params, for example:
   - `/v1/tasks/:task_id/risks`
   - `/v1/tasks/:task_id:cancel` (when framework escaping/runtime support is confirmed)
4. Avoid broad wildcard forms in business APIs:
   - avoid `/v1/tasks/*path` unless absolutely necessary.
5. Keep path segments unambiguous and deterministic.
6. If target backend is unknown, design for the strictest common subset (Gin-safe first).

## Pre-Delivery Route Conflict Check

Before final output, run a conceptual check list:

1. Build method-scoped route groups.
2. Verify each service has a unique/stable route namespace prefix.
3. For each depth level, detect static-vs-param sibling collisions.
4. Detect wildcard-name divergence at same branch depth.
5. Detect non-terminal catch-all usage.
6. Detect greedy wildcard overlaps that could shadow specific routes.
7. Confirm compatibility decision notes in output.

## Required Fail-Fast Rule

If any route conflict check fails, the draft is non-deliverable.
Stop and output `Validation Notes -> Blocking Issues` with corrected path proposals.
