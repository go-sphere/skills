---
name: ux-analyst
description: "Turn prototype demos into behavioral semantics: per-screen purpose, entry and exit conditions, business-level actions, user-visible states, and failure handling. Use when given Figma links, screenshots, videos, HTML demos, or wireframes and asked to document flows or screen behavior — including ux 分析, 写 UX 流程, 页面行为分析, 用户流程语义化. Not for product scope or success metrics — that is `prd`."
---

# UX Analyst

Turn a prototype from a visual representation into a behavioral specification that engineers and
other agents can implement from.

## Inputs

Do not write `prd/UX-FLOWS.md` until at least one visual or behavioral input exists: a Figma file
or link, a screenshot, a video of the interaction, an HTML/CSS demo, a user flow diagram, or a
wireframe. A PRD is optional but useful context.

If there is no visual input, ask the user for one before proceeding. If the input exists but the
scope is unclear — too many screens, or no priority among them — ask one question to narrow it.

## Steps

1. Inventory the available inputs: Figma, screenshots, video, HTML, PRD.
2. If no visual input exists, stop and ask for one.
3. If the scope is ambiguous, ask one question to narrow it.
4. Extract, per screen: page purpose, entry conditions, exit conditions, key actions, user-visible states, blocking conditions, and error scenarios.
5. Write `prd/UX-FLOWS.md`. Add `prd/SCREEN-INVENTORY.md` when the system has many screens.
6. Verify the completion criteria below.
7. Report the file paths and ask which page behaviors still need clarification.

## Reference Map

| Read | When |
|------|------|
| [references/ux-flows-template.md](references/ux-flows-template.md) | Always, before step 5 — the exact section shape of both output documents |
| [references/writing-principles.md](references/writing-principles.md) | While drafting any action or state description, to keep it behavioral instead of visual |

## Rules

1. Describe behavior, never layout. "Submit becomes enabled when all required fields are valid", not "the button sits in the top-right corner".
2. Every action states all six properties: when enabled, state change, failure handling, success behavior, recovery, and the business meaning.
3. Name concrete states. `draft → pending_review`, not "the order is updated".
4. Treat every page as a node in a business process, not as a screenshot.
5. Never write a generic action such as "process submission" or "save data" without saying what exactly happens.
6. Always write the files to disk. Never deliver UX documents only in the conversation.

## Output

Write to `prd/UX-FLOWS.md`, plus `prd/SCREEN-INVENTORY.md` when the screen count warrants it. Use
the user's location instead when they named one.

Before finishing, confirm every item:

- [ ] Every key screen has a documented purpose.
- [ ] Entry and exit conditions are specified for each screen.
- [ ] Every key action documents when enabled, state change, failure handling, success behavior, and recovery.
- [ ] User-visible states are documented, including loading, empty, error, success, and draft.
- [ ] Blocking conditions are identified with their resolution.
- [ ] Error and exception scenarios are covered with user-facing messages and retry/data-preservation behavior.
- [ ] No description reads as "click X"; every one is a business-level behavior.

## Related Skills

- Upstream — `prd` when it exists, or direct visual inputs such as Figma files, HTML demos, screenshots, and videos; at least one visual input is required.
- Downstream — `spec-writer`; hand off once page behaviors, states, and error scenarios are captured as business-level flows rather than UI descriptions.
- Boundary — `prd` owns the business-level page inventory and scope; this skill owns per-screen behavior, user-visible states, and failure semantics.
- Companion — none.
- If a referenced skill is not installed in this session, name it in the handoff message and continue with the current artifact; do not stall.
