---
name: prd
description: "Write a Product Requirements Document: problem framing, personas, business processes, module boundaries, page inventory, measurable success criteria, scope, and risks. Use when the user wants a PRD, requirements documented, or a business idea turned into a product plan — 写 PRD, 整理需求, 需求文档. Not for API contracts, schemas, or implementation detail — that is `spec-writer`."
---

# Product Requirements Document (PRD)

Produce a PRD that connects business intent to technical execution without leaking implementation
detail. Output: `prd/PRD.md`.

## Inputs

Do not write `prd/PRD.md` until the problem statement, the target users, and at least one success
criterion are clear. If any is missing, ask for it — one question at a time — before drafting.

Skip discovery and draft directly when the user already gave a clear problem statement, target
users, and success criteria, or explicitly said "just write it".

## Steps

1. Decide whether discovery is needed. Ask questions first when the idea is vague, when who-and-what-success is missing, or when several reasonable interpretations exist.
2. Run discovery if needed: at most 3-5 targeted questions covering the problem, why now, how success is measured, what is in and out of scope, and who the users are.
3. Synthesize: map the key user flows, identify the core business processes, define module boundaries, list the key pages and scenes, and name the risks and dependencies.
4. Draft the document using the 8-section schema.
5. Write it to `prd/PRD.md`, creating the `prd/` directory if needed.
6. Verify the completion criteria below.
7. Report the file path and ask whether any section needs adjustment.

## Reference Map

| Read | When |
|------|------|
| [references/prd-schema.md](references/prd-schema.md) | Always, before step 4 — the exact sections, the PRD-versus-SPEC split, and the common mistakes |

## Rules

1. Lead with the problem and its context. Never open with the solution.
2. Every success metric is quantitative and says how it is measured.
3. State what is explicitly out of scope. A PRD without non-scope is incomplete.
4. Justify "why now", not only the what and the how.
5. Keep technical detail out: no field types, no table designs, no API response shapes, no internal state machines, no error codes, no architecture.
6. Keep the document lightweight. Depth belongs in the SPEC.
7. Always write to disk. Never deliver the PRD only in the conversation.

## Output

Write to `prd/PRD.md` by default, or to the location the user names.

Before finishing, confirm every item:

- [ ] Background states the problem and why now.
- [ ] User personas are identified.
- [ ] Core business processes are documented.
- [ ] Module boundaries are defined at a high level only.
- [ ] The pages and scenes inventory is complete.
- [ ] Success criteria are measurable.
- [ ] Scope and non-scope are both explicit.
- [ ] Risks and dependencies are documented.
- [ ] No technical implementation detail leaked in.

## Related Skills

- Upstream — `project-intake` supplies `docs/00-intake.md`; run `interview-me` first when the business direction is still unresolved.
- Downstream — `spec-writer` is always the next stage; when prototypes or demos exist, `ux-analyst` comes first. Hand off once the PRD completion criteria are met and no implementation details leaked in.
- Boundary — use `spec-writer` for engineering contracts, state machines, and API or schema detail; this skill owns problem framing, personas, scope, and success metrics. Use `ux-analyst` for per-screen behavior semantics.
- Companion — `interview-me` when discovery answers stay vague; if it is unavailable, list the open questions under risks and dependencies instead.
- If a referenced skill is not installed in this session, name it in the handoff message and continue with the current artifact; do not stall.
