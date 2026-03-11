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

| Entity | Field | Type | Required | Default | Notes |
|--------|-------|------|----------|---------|-------|
| | | | | | |

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
- [ ] Relation shape matches query needs
- [ ] Indexes map to real query patterns
- [ ] Open questions are acceptable for implementation handoff

---

## Optional Appendix: Draft DDL

Include only if the user explicitly asks for SQL/DDL during review. Otherwise write `N/A`.
