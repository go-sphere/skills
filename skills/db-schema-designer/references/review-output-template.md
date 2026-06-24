# Review Output Template: Requirement -> Database Design Brief

Use this exact template for review-stage database design output.

---

## 1) Input Summary

- **Source type**: prompt / markdown / proto / repository / runnable demo
- **Business scope**:
- **Assumptions**:
- **Evidence conflicts & resolution**:

---

## 2) Core Entities

| Entity | Purpose | Lifecycle | Key Constraints |
|--------|---------|-----------|-----------------|
| | | | |

---

## 3) Table Design

| Entity | Field | Type | Required | Default | Volatility | Notes |
|--------|-------|------|----------|---------|------------|-------|

Volatility legend: `core` (stable column) / `hot` (indexed query field) / `volatile` (JSON / extension / dynamic).

**Nullability decisions**:
**Mutable vs immutable fields**:
**Enum / status definitions**:

---

## 4) Field Type Compatibility

- **Timestamp policy**:
- **Enum / status representation**:
  Store stable string values in the database; proto generation maps them to `int32` enums.
- **Array policy**:
- **JSON / complex object policy**:
- **ID type policy**:
- **Money representation**:
- **Other type constraints**:

---

## 4a) Volatility and Extension Strategy

Fill this section even when the answer is "everything is core columns" — that itself is a decision worth recording.

| Entity | Stable Core Columns | Indexed Query-Hot Columns | Volatile Storage |
|--------|---------------------|---------------------------|------------------|

**JSON fields used**:

| Entity | JSON Field | Purpose / Justification | Known Sub-keys | Promotion Candidates |
|--------|-----------|--------------------------|----------------|----------------------|

JSON field name should be one of: `extra`, `metadata`, `settings`, `payload`, `attrs`.

**Extension tables**:

| Main Entity | Extension Entity | Reason for Split | Lifecycle |
|-------------|-------------------|------------------|-----------|

**Dynamic field model** (`custom_field_def` + `custom_field_value`):

- **In use**: yes / no
- **Scope** (which business types this covers):
- **Why dynamic, not columns or JSON**:

**Promotion plan** (volatile → column candidates already foreseeable):

- 

---

## 4b) Field Lifecycle

Fields being deprecated or replaced as part of this change.

| Entity | Field | Stage | Replacement | Plan |
|--------|-------|-------|-------------|------|

Stages: `active` / `deprecated` / `read_only` / `removed_from_code` / `dropped`. Write `N/A` if none.

---

## 5) ID Strategy

- **Strategy**:
- **Reasoning**:
- **Compatibility impact**:

---

## 6) Relations

**One-to-many decisions**:
**Many-to-many decisions**:
**Snapshot vs live-reference decisions**:

---

## 7) Constraints and Data Integrity

- **Uniqueness constraints**:
- **Referential integrity rules**:
- **Deletion policy**:
- **Audit / timestamp fields**:

---

## 8) Index Plan

| Query Pattern | Index | Justification |
|--------------|-------|---------------|
| | | |

---

## 8a) DDL Change Management

- **Migration tool** (Atlas / Bytebase / Flyway / other):
- **Online-DDL needed?** (for large existing tables): yes / no — name the table and the tool (`gh-ost` / `pt-online-schema-change`)
- **Required-column rollout** (new non-null columns on existing data):
- **Production auto-migrate forbidden**: confirm production never runs `client.Schema.Create` at boot

---

## 9) Open Questions

- 

---

## 10) Approval Risks

- 

---

## 11) Review Checklist

- [ ] Entities and ownership boundaries are correct
- [ ] Required vs optional fields are justified
- [ ] Field types fit downstream Ent + proto3 constraints
- [ ] Every field is classified as core / hot / volatile
- [ ] JSON fields use the standard names and carry a justification
- [ ] Extension tables and dynamic field model decisions are explicit (or marked N/A)
- [ ] Promotion candidates (JSON → column) are listed
- [ ] Deprecated fields have a multi-stage plan, not a direct drop
- [ ] Relation shape matches query needs
- [ ] Indexes map to real query patterns
- [ ] DDL change management constraints are noted for any large-table change
- [ ] Open questions are acceptable for implementation handoff

---

## Optional Appendix: Draft DDL

Include only if the user explicitly asks for SQL/DDL during review. Otherwise write `N/A`.
