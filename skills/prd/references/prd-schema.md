# PRD Schema

Use these exact section names and order in `prd/PRD.md`.

## 1. Background & Goals

Must include: the problem statement (which pain point), why now (why it matters at this time), and
success criteria (3-5 measurable KPIs).

## 2. User Personas

Must include: the primary users, their characteristics and jobs, and the pain points in their
current workflow.

## 3. Core Business Processes

Must include: primary workflow steps, decision points, and key user interactions.

Must not include: detailed state machines, API calls, database schemas.

## 4. Module Boundaries

Must include: which modules or components are involved, how they interact at a high level, and
external dependencies.

Must not include: technical implementation details or code structure.

## 5. Pages & Scenes Inventory

Must include: the key pages or scenes, their entry conditions, and their exit conditions.

## 6. Success Criteria

Must include: quantitative metrics and how each one is measured. Never "fast" or "easy".

- Bad: "The system should be fast."
- Good: "Search returns within 200ms for 10k records."

## 7. Scope / Non-Scope

Must include: what is built in this phase, and explicitly what is not built.

## 8. Risks & Dependencies

Must include: technical risks, external dependencies, and key assumptions.

## PRD or SPEC?

| Content | PRD | SPEC |
|---------|-----|------|
| Problem statement | yes | yes |
| User personas | yes | yes |
| User flows | yes | yes |
| Success metrics | yes | yes |
| Module boundaries | yes | yes |
| Page inventory | yes | no |
| API contracts | no | yes |
| Database schema | no | yes |
| State machines | no | yes |
| Technical architecture | no | yes |

These belong in the SPEC, never in the PRD: field types and data structures, database table
designs, API response structures, internal state machines, detailed error codes, technical
architecture, and code-level implementation.

## Common Mistakes

1. Starting with the solution. Lead with problem and context.
2. No success criteria. Every PRD needs measurable KPIs.
3. Including technical details. Save API and schema work for the SPEC phase.
4. Vague scope. State explicitly what is not included.
5. Missing "why now". Justify the timing, not only the what and how.
6. Over-detailing. Keep the PRD lightweight; depth belongs in the SPEC.

## Framing Notes

> "The most important section is the first part — what is the background and context? What is the
> problem, why does it matter, and why does it matter now?" — Maggie Crowley

> "Whenever we're devising a new product, we start by writing a press release describing it in a
> way that speaks to the customer." — Bill Carr

> "We tend to keep them pretty light. I like to have the minimal amount of context that ensures
> everyone's on the same page." — Eric Simons

> "If you're not prototyping and building to see what you want to build, you're doing it wrong."
> — Aparna Chennapragada
