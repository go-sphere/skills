# Output Template: Requirement -> DB Schema Brief

Use this template as the final response shape.  
Keep section order unchanged and do not omit required fields.

## 1) Input Summary

- Source type: prompt / markdown / runnable demo / repository code
- Business scope:
- Assumptions:
- Evidence priority or conflict resolution notes (if any):

## 2) Core Entities and Lifecycle

| Entity | Lifecycle Status | Key Timestamps | Constraints |
|---|---|---|---|
| | | | |

## 3) Field Design Notes

- Schema comments:
- Field comments:
- Nullability policy (`Optional/Nillable` decisions):
- Enum policy (prefer Ent `field.Enum`)/default:
- Unique/immutable/default constraints:
- Soft-delete policy:
- Array candidates (typed-first when dialect-safe):
- JSON exceptions (must justify why typed fields and arrays are insufficient):

## 4) ID Strategy

- ID source: generator-managed / custom field
- If generator-managed, config location (e.g. ent tool config):
- If custom, business reason and compatibility impact:

## 5) Relation Strategy

- One-to-many decisions:
- Many-to-many decisions and rationale (relation-entity > array > join > JSON fallback):
- Array field support check (dialect/cross-db constraints):
- Weak relation ID naming convention:

## 6) Query-Driven Index Plan

| Query Pattern | Recommended Index | Reason |
|---|---|---|
| | | |

## 7) Ent Implementation Plan

- Optional edges only where clearly useful
- Enum definitions centralized in schema code
- Required comments/constraints checklist:

## 8) Go Batch Retrieval Plan (`WHERE IN`)

- Source query:
- ID collect + dedupe:
- Chunk size:
- Backfill map strategy:
- Cross-service alternative (`BatchGet*` RPC):

## 9) Project Integration (sphere-layout)

- ent tool config impact (`IDType` / features / autoproto):
- bind registration impact (`cmd/tools/bind/main.go#createFilesConf`):
- render/dao/service touchpoints:
- `WithIgnoreFields` impact (timestamps/sensitive fields):

## 10) Post-Change Commands

- Schema/code generation commands (minimum):
  - `make gen/proto`
- Validation/lint commands (minimum):
  - `go test ./...` (or explicit alternative)

## 11) Consistency and Risk Control

- Dangling reference checks:
- Snapshot fields:
- Migration/deferred decisions:

## Generation Diff Checklist

- entpb/proto definitions changed and consumed:
- bind/map generated changes consumed by render/service:
- new entity registered in bind config:
- ignore-field rules reviewed (`created_at/updated_at`, sensitive fields):

## Output Constraints

- Keep all 11 sections, even when a section has "N/A".
- If assumptions are used, label them explicitly as assumptions.
- If any required validation is missing, add a `Blocking Notes` line under the affected section.
