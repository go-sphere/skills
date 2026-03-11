# Reference: Proto Output Template (Condensed)

## Purpose

Provide the smallest valid final-output shape for straightforward scaffold CRUD tasks.

## When To Load

Load this template only for simple tasks with clear package choice, clear reuse choice, and no unusual routing or error-design complexity.

## Required Section Order

### 1) Scaffold Fit Decision

Use a brief table such as:

| Target Package | Route Style | Notes |
| --- | --- | --- |
| dash.v1 | action-style | follows scaffold |

### 2) Proto Structure Check

Use a short pass or fail table such as:

| Check Item | Result |
| --- | --- |
| One service per file | pass |
| Declaration order | pass |

If the file is `message-only proto`, record the exemption briefly.

### 3) Route Conflict Check

Include this section only when the draft exposes HTTP service routes.
Keep it short unless the routing is non-trivial.

### 4) Proto3 Contract

Provide the actual proto content.

### 5) Reuse Decision

Use a brief table such as:

| Object | Choice | Reason |
| --- | --- | --- |
| User | entpb.User | existing model |

### 6) Mandatory Confirmation

When every required check passes, include:

`All required checks passed.`

## Condensed-Mode Guardrails

1. Escalate to the full template if the task includes custom business flows, substantial mock output design, multiple services, or heavy validation notes.
2. Do not omit route-safety evidence when service routes exist.
3. Do not emit `Mandatory Confirmation` if any required item is unresolved.
