---
name: project-intake
description: Organize scattered project inputs into one standardized intake document that separates what is known from what is missing. Use at project or feature kickoff, for requirement initialization, or to turn prototypes, demos, screenshots, and drafts into a structured document — 项目启动, 需求梳理, 整理输入. Run before any PRD. Not for multi-round decision interviews — that is `interview-me`.
---

# Project Intake

Organize scattered project inputs into one structured document that locks down project boundaries
and separates known items from unknown ones. Output: `docs/00-intake.md`.

## Inputs

Do not generate `docs/00-intake.md` until both are confirmed:

1. At least one concrete input: a PRD draft, a prototype, a description, or a repo link.
2. A one-sentence project goal, or enough context to infer one.

If the inputs are too vague to produce a meaningful document, ask first. Never assume.

This skill processes any of: an initial PRD or requirement description; prototype demos (Figma,
HTML demo, screenshots, videos); interaction specs or user flow diagrams; existing code
repositories or modules; the user's verbal descriptions and notes; competitive analysis or
reference cases. None is individually required — identify and document whatever exists.

## Steps

1. Scan everything the user provided. Extract the project goal, the available inputs, and the visible gaps.
2. If the goal is unclear or no concrete input exists, ask one question to unblock, for example "What problem is this project solving?"
3. Keep asking one follow-up at a time until all eight sections can be filled.
4. Write `docs/00-intake.md`, creating the `docs/` directory if needed.
5. Verify the completion criteria below.
6. Report the file path and ask whether anything needs adjusting.

## Reference Map

| Read | When |
|------|------|
| [references/intake-template.md](references/intake-template.md) | Always, before step 4 — the eight sections and what belongs in each |

## Rules

1. Keep every section to 3-5 lines. Do not expand into detail.
2. Focus on known versus unknown. This document locks boundaries; it does not specify requirements.
3. Mark what the user confirmed separately from what you inferred.
4. Do not write PRD content here. Business processes and feature detail belong to the `prd` stage.
5. Always write the file to disk. Never deliver the intake document only in the conversation.

## Output

Write to `docs/00-intake.md`, or to the location the user names.

Before finishing, confirm every item:

- [ ] The project goal is one clear sentence.
- [ ] Every available input is listed with its status.
- [ ] Missing inputs are listed, so the team knows what to collect next.
- [ ] Confirmed roles and modules are listed.
- [ ] The demo reference type is marked as visual or behavior.
- [ ] Code boundaries are identified, when code exists.
- [ ] Every unresolved item is listed.

## Related Skills

- Upstream — none; this skill is the entry point and accepts raw or scattered inputs.
- Downstream — `prd` once `docs/00-intake.md` is complete; when the demo reference type is `behavior reference`, `ux-analyst` comes first. Hand off when the intake document is on disk and the unresolved list is explicit.
- Boundary — use `interview-me` instead when the goal itself is still unclear and needs multi-round decision-tree interviewing; this skill produces one structured intake document in a single pass.
- Companion — `interview-me` when inputs conflict or the goal is unresolved; if it is unavailable, record the open questions in the unresolved items list instead.
- If a referenced skill is not installed in this session, name it in the handoff message and continue with the current artifact; do not stall.
