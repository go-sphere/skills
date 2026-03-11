# Reference: Proto Output Template (Full)

## Purpose

Provide the full final-output shape for complex proto API proposals.

## When To Load

Load this template only when the task includes custom business logic, multiple services, complex routing, substantial validation discussion, or explicit error-design work.

## Required Section Order

### 1) Scaffold Fit Decision

Summarize package choice, service prefix, route style, pagination style, error placement, naming exceptions, and brief rationale.

Suggested columns:

| Target Package | Service Prefix | Route Style | Pagination Style | Error Placement | Naming Exceptions | Notes |
| --- | --- | --- | --- | --- | --- | --- |

### 2) Proto Structure Check

Show pass or fail evidence for:

1. File mode
2. One-service rule when applicable
3. File-prefix to service or error-prefix mapping
4. Declaration order
5. Explicit exemptions for `message-only proto`

### 3) Route Conflict Check

Show pass or fail evidence for:

1. Service prefix namespace isolation
2. Static versus param sibling conflicts
3. Wildcard naming consistency
4. Catch-all placement
5. Greedy shadowing risk
6. Backend portability assumptions

### 4) Error Placement Check

Show whether service-local and shared errors are placed appropriately for the file mode.

### 5) Comment Coverage Check

Confirm concise `//` business comments exist for exposed RPCs, core messages, and key enum values.

### 6) API Capability Matrix

Map business use cases to RPC, HTTP mapping, request keys, response keys, and expected index drivers.

### 7) Mock JSON

Include only the mock payloads needed to validate the external contract shape, typically:

1. list response
2. detail response
3. error response

### 8) Reuse Decision

Document the choice for each major payload:

1. reuse `entpb`
2. reuse `shared.v1`
3. introduce custom DTO or VO with explicit reason

### 9) Proto3 Contract

Provide the actual proto content.

### 10) Error Enum Design

Summarize code, HTTP status, optional reason, message, and trigger condition for each key business error.
Add brief runtime guidance when the task defines service errors.

### 11) Ent -> Proto Mapping

Map important Ent fields to exposed proto fields and note masking, omission, or reshaping decisions where relevant.

### 12) Validation Notes

Record:

1. checklist outcome
2. explicit exemptions
3. non-blocking caveats

### 13) Blocking Issues

Include this section only when any required check fails.
Use the format `Validation Notes -> Blocking Issues` and give corrected proposals.

### 14) Mandatory Confirmation

Include this only when every required check passes:

`All required checks passed.`

## Full-Mode Guardrails

1. Keep section order stable.
2. Omit irrelevant detail; full mode is for completeness, not filler.
3. Do not duplicate the full text of checklist rules inside the deliverable.
4. If the target file is `message-only proto`, keep service-only sections brief and record the exemption instead of fabricating service evidence.
