---
name: db-schema-designer
description: Design review-ready database schemas for go-sphere and similar backend projects from requirements, docs, demos, or existing APIs. Use to define or review entities, fields, relationships, constraints, indexes, lifecycle states, or schema evolution before any Ent code — including 设计数据库, 表结构设计, 建模评审. Not for writing Ent schema code or entproto annotations — that is `ent-schema-implementer`.
---

# DB Schema Designer

Turn product and backend requirements into a review-ready database design, collaboratively,
through dialogue. Present the design in sections and get approval as you go. The final brief
records decisions the user already made with you — it is not the first time they see them.

## Inputs

Do not produce the final review brief, write Ent schema code, or hand off to
`ent-schema-implementer` until every design section has been presented and the user has approved
the overall design. When requirements are ambiguous, stop and ask instead of assuming.

Before asking anything, mine what you already have: the prompt text, referenced docs, proto files,
existing Ent schemas, API contracts, mockups. Extract everything you can without asking.

## Steps

Track these with TodoWrite, one task per step.

1. Explore the inputs: docs, proto files, mockups, existing schemas, service behavior.
2. Ask clarifying questions, one at a time, until entities and key behaviors are clear.
3. Propose 2-3 options with trade-offs and a recommendation for every non-trivial decision.
4. Present the entity overview — name, purpose, key lifecycle states, no fields yet. Get approval.
5. Present the field design one entity at a time. Get approval for each.
6. Present relations and constraints: one-to-many foreign keys, many-to-many shape, uniqueness, referential integrity, deletion cascade rules. Get approval.
7. Present the index plan, every index tied to a named query pattern. Get approval.
8. Produce the final review brief from the template.
9. Write the brief to `prd/DDL.md`, or to `design/<feature>/schema.md` when the request names a feature or change-id.
10. Ask for explicit approval of the brief before handing off to `ent-schema-implementer`.

### Asking good questions

Ask one question per message. Prefer multiple choice. Focus on missing entity boundaries,
lifecycle states, business invariants, query patterns, and deletion semantics. Stop asking as soon
as you can make a reasonable proposal.

- Good: "Should deleted records be recoverable? A) Soft-delete (`deleted_at`, recoverable) B) Hard-delete (row removed) C) Archive to a separate table"
- Bad: "Can you tell me more about your requirements?"

### Decisions that must be offered as options

ID strategy (`int64` auto-increment, external ID, compound key), deletion strategy (hard, soft,
archive), many-to-many shape (join table or relation entity with attributes), complex field
representation, and money or decimal fields. Lead with your recommendation and say why.

### Volatility check

When an entity has many attributes, or the user mentions fields likely to change — marketing
flags, experiment params, per-tenant custom fields, form fields — walk the volatility decision
tree before listing columns, and surface the split as a choice:

> "This entity mixes stable fields (id, status, amount) with volatile-sounding attributes
> (marketing tag, experiment id, source). I'd suggest stable and query-hot fields as regular
> columns, volatile attributes in a typed `extra` JSON field, and a separate extension entity only
> if those attributes keep growing. Does that split look right?"

Never silently make everything a column, and never silently dump everything into JSON. Escalate to
an extension table only with evidence (module ownership, hot-row concerns, large fields). Escalate
to a dynamic field model (`custom_field_def` + `custom_field_value`) only when fields are
user-defined or tenant-defined at runtime.

## Reference Map

| Read | When |
|------|------|
| [references/modeling-rules.md](references/modeling-rules.md) | Always, before step 4 — evidence priority, field type policy, ID strategy, relations, index planning |
| [references/field-volatility.md](references/field-volatility.md) | At step 5, for any JSON field, extension table, dynamic field model, field retirement, or DDL change plan |
| [references/review-output-template.md](references/review-output-template.md) | Before step 8 — the exact brief structure |

## Rules

1. One question at a time. Never stack questions; wait for the answer.
2. Surface contentious defaults — soft delete, UUID, complex JSON — as explicit choices. Never pick one silently.
3. Check every field against the allowed type shapes. When a requested type does not fit (datetime object, UUID primary key, float money), redesign it here and explain the substitution.
4. Classify every field as core, hot (needs an index), or volatile (JSON, extension, dynamic). Call the volatile ones out explicitly.
5. Give every JSON field one of the standard names — `extra`, `metadata`, `settings`, `payload`, `attrs` — plus a one-line justification. Flag sub-keys likely to be promoted to real columns later.
6. Note which fields are mutable and which are immutable.
7. Retire a field through the staged plan — deprecated, read-only, removed from code, dropped — never by deleting it outright.
8. Every index needs a named query pattern, for example "list orders by user, paginated by created_at". No speculative indexes.
9. Write no Ent schema code, no entproto numbering, and no bind/render/service tasks here.

## Output

Write the brief to `prd/DDL.md`, or to `design/<feature>/schema.md` when the user names a module or
change-id. Follow the template exactly: keep the section order, write `N/A` for sections that do
not apply, explain every type decision in the field-type compatibility section, separate confirmed
decisions from open questions, and keep the document review-oriented rather than code-oriented.

Then ask for review:

> "Design brief written to `<path>`. Please look it over — tell me what needs adjusting. Once
> you're happy, I can hand off to `ent-schema-implementer` to write the Ent schemas."

Wait for explicit approval before handing off.

## Related Skills

- Upstream — `spec-writer` defines entities, boundaries, and states; when a spec changed, `spec-diff-pipeline` supplies `04-schema-delta.md`. When neither exists, model from the requirements the user provides directly.
- Downstream — `ent-schema-implementer`; hand off only after the user approves the brief written to `prd/DDL.md` or `design/<feature>/schema.md`.
- Boundary — use `ent-schema-implementer` to write Ent schema code and entproto annotations; this skill owns the review-ready design.
- Companion — none.
- If a referenced skill is not installed in this session, name it in the handoff message and continue with the current artifact; do not stall.
