---
name: sphere
description: Pick which skill in this repository to run next. Use when starting go-sphere work, when unsure which skill applies, when a request spans several stages, or when asked what these skills do — including 该用哪个 skill, 这些 skill 怎么用, 从哪一步开始. Not for implementing a feature — that is `sphere-feature`.
---

# Sphere Skill Guide

Classify the request, name the one skill to run next, and hand over. Never load every skill.

## Routing Rules

Apply in order. The first rule that matches decides.

1. The user named a skill — use that skill.
2. The request spans several stages — start at the earliest missing artifact, in this order: decisions (`interview-me`), PRD (`prd`), spec (`spec`), Ent schema (`sphere-ent`), API contract (`sphere-api`), feature delivery (`sphere-feature`), frontend pages (`sphere-crud`).
3. The task pulls upstream layout changes into a project, or adopts a project that predates the layout contract — `sphere-sync`, not `sphere-feature`.
4. The task is Go code quality with no feature to build — `go-test`, `go-doc`, or `go-simplify`, not `sphere-feature`.
5. The task ports another language to Go — `go-migrate`.
6. The task reviews code (a diff, branch, PR, paths, or a repository), merges review findings, or fixes and verifies approved findings — `review-loop`, not `improve`.
7. The task audits a repository to decide what to improve, or writes plans for other agents — `improve`, not `go-simplify`.
8. The task changes go-sphere contracts, schemas, services, or generation commands — `sphere-feature`.
9. Anything else — match the task in the Workflow Map and name one skill. If none fits, say so and continue without a skill.

## Workflow Map

### Requirements and specification

- `interview-me` — settle ambiguous design decisions one question at a time.
- `prd` — write the product requirements.
- `spec` — write or revise an implementation-ready specification.

### go-sphere delivery

- `sphere-ent` — turn an approved data model into Ent schema files.
- `sphere-api` — design proto3 and HTTP contracts.
- `sphere-feature` — deliver a feature across proto, schema, service, and generation under the layout contract.
- `sphere-crud` — generate admin pages and routes from the generated TypeScript swagger client.
- `sphere-sync` — pull a newer layout revision into a project, resolve drift, or adopt a legacy project.
- `sphere-make` — standardize Make targets and Make-driven CI.

### Go quality

- `go-test` — audit, repair, or write Go tests.
- `go-doc` — write Go doc comments and verified usage examples.
- `go-simplify` — remove over-design, over-optimization, and over-defensive code without changing behavior.
- `go-migrate` — port a non-Go codebase to idiomatic Go with parity checks.

### Audit and agents

- `review-loop` — review code with one or several agents, then fix and verify only the findings the user approves.
- `improve` — audit a codebase read-only and write plans other agents can execute.
- `delegate` — hand one bounded task to another coding agent and resume its session.
- `rex-desktop` — run and coordinate several live coding agents in Rex floating panes.

## Stage Handoffs

Every skill ends with a `## Related Skills` block naming its upstream, downstream, boundary, and companion skills.

1. When a skill finishes and names a default next skill, announce the handoff with the artifact it needs, for example "next: use `sphere-api` with `prd/SPEC.md`".
2. Honor that handoff before classifying the request again.
3. Invoke the next skill when the user agrees, or when the user already asked for the whole flow and the current stage's completion criteria are met. Never blend two stages in one pass.
4. If the named skill is not installed in this session, say which skill and artifact are needed, then continue with the current work; do not stall.
5. When one request spans two skills' boundaries, own this stage's side and name the other skill for the rest.

## Operating Constraints

1. Inside a generated go-sphere project, its own `.sphere/layout.json`, `AGENTS.md`, and `docs/LAYOUT_CONTRACT.md` outrank any skill where they disagree. Read them before editing.
2. There are four official layouts — `standard`, `simple`, `bun`, `telegram` — with different capabilities. Never assume `standard`.
3. Keep stages apart: requirements, then spec, then schema and contract design, then implementation.

## Related Skills

- Upstream — none; this skill is the entry point and can run before any other.
- Downstream — the skill the routing rules name, usually `sphere-feature`.
- Boundary — this skill only picks the next skill; the skill it names does the work.
- Companion — none.
- If a referenced skill is not installed in this session, name it in the handoff message and continue with the current artifact; do not stall.
