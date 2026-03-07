# Output Template: Requirement → Schema Brief

Use this exact template for all schema outputs. Keep section order unchanged.

---

## 1) Input Summary

- **Source type**: prompt / markdown / proto / repository / runnable demo
- **Business scope**:
- **Assumptions** (if any):
- **Evidence conflicts & resolution** (if any):

---

## 2) Core Entities

| Entity | Lifecycle Field | Key Timestamps | Constraints |
|--------|----------------|----------------|-------------|
| | | | |

---

## 3) Field Design

| Field | Type | Policy | Entproto # | Notes |
|-------|------|--------|------------|-------|
| | | | | |

**Policy**: Required / Optional / Unique / Immutable / Default(value)

**Nullability decisions**:
**Enum definitions**:
**Soft-delete policy** (if any):

---

## 4) ID Strategy

- **Strategy**: generator-managed / custom field
- **If generator-managed**: Default behavior, no config needed
- **If custom**: Business reason + compatibility impact

---

## 5) Relations

**One-to-many decisions**:
**Many-to-many decisions** (relation-entity / array / join / JSON):

---

## 6) Index Plan

| Query Pattern | Index | Justification |
|--------------|-------|---------------|
| | | |

---

## 7) Ent Implementation

- Schema annotations: `entproto.Message()` ✓
- Fields with `entproto.Field(n)` ✓
- Enum mapping with values from 1 ✓
- Comments on key fields ✓

---

## 8) Batch Query Plan

- **Source query**:
- **ID collection + dedupe**:
- **Chunk size**:
- **Backfill strategy**:

---

## 9) Integration Impact

- **Bind registration**: New entity → `createFilesConf`
- **WithIgnoreFields**: `created_at`, `updated_at`, sensitive fields
- **Render/Service touchpoints**:
- **Generation diff checklist**:
  - [ ] entpb/proto generated
  - [ ] bind/map changes consumed
  - [ ] New entity registered

---

## 10) Post-Change Commands

```bash
make gen/proto
go test ./...
```

---

## 11) Risk & Consistency

- **Dangling reference checks**:
- **Snapshot fields**:
- **Deferred decisions**:

---

## Blocking Notes

(Add any incomplete items here with required action)

---

## Output Constraints

- Keep all 11 sections in order
- Mark assumptions as `Assumption:` prefix
- If section not applicable, write "N/A" explicitly
