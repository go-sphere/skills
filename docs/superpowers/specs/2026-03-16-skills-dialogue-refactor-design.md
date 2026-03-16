# Skills Suite Dialogue Refactor — Design Spec

**Date:** 2026-03-16
**Scope:** 8 core skills in the go-sphere skills suite
**Goal:** Improve content quality and style consistency by converting skills that require intent clarification into a dialogue-driven pattern

---

## Problem Statement

The skills suite covers the full dev.md workflow (Intake → PRD → UX → SPEC → API → Schema → Implementation → Admin UI), but individual skills vary in style:

- Some are "one-shot output" (generate a document immediately)
- Some partially ask questions but inconsistently
- None enforce a HARD-GATE before producing output
- Output is sometimes only in the conversation, not written to disk

This causes AI to make unverified assumptions, produce documents that don't match user intent, and skip writing local files.

---

## Goals

1. All 8 target skills use dialogue-first interaction before producing output
2. HARD-GATE enforced: no document written until user confirms intent
3. Output is always written to disk at the correct path (per dev.md directory conventions)
4. Two tiers of dialogue depth matched to skill complexity
5. TodoWrite used to track execution steps in Tier 2 skills

## Non-Goals

- Cross-skill handoff orchestration (not in scope)
- Adding new skills for missing workflow stages (not in scope)
- Changing the domain content rules, references, or output format of any skill (e.g., what fields go into a spec, which modeling rules apply). Dialogue structure, interaction patterns, HARD-GATE, TodoWrite usage, and disk-write behavior are explicitly in scope.

---

## Per-Skill Integration Notes

These notes resolve ambiguities where existing skill structure must be preserved while adding dialogue scaffolding.

### `spec-writer` (Tier 2)
Current state: has a `Workflow Decision Tree` with New Spec / Revision / Deepening Pass branches.
Integration: **Prepend** the HARD-GATE block before the Workflow Decision Tree. Add a clarification step as **step 0** of New Spec Workflow: "Identify and ask about any missing inputs (problem, goals, constraints) before proceeding to step 1." Do not modify the Decision Tree itself.

### `spec-diff-pipeline` (Tier 2)
Current state: has a `Required Inputs` section that already gates execution on confirming `repo_root`, `spec_path`, and diff mode.
Integration: The existing `Required Inputs` section **counts as the HARD-GATE** for this skill. Reformat it as a `<HARD-GATE>` block and add a statement that the pipeline does not start until all required inputs are confirmed. No new dialogue structure needed beyond this.

### `proto-service-generator` (Tier 1)
Current state: English, no HARD-GATE, no workflow section. Three conditional "When To Use" prerequisites.
Integration: Add a HARD-GATE block (in English) that gates on: proto files exist, generated `*ServiceHTTPServer` interface is present. If missing, ask which module and confirm proto generation has been run. Then proceed directly to generation — no proposal step.

### `project-intake`, `prd`, `ux-analyst` (Tier 1)
Standard Tier 1 addition: prepend HARD-GATE, add Workflow section (ask → write → report path).

### `proto-api-generator`, `db-schema-designer` (Tier 2)
Standard Tier 2 addition: prepend HARD-GATE, add Checklist section with TodoWrite.

---

## Two-Tier Design

### Tier 1 — Light Dialogue

For **collection/organization** skills where user intent is usually clear but inputs may be incomplete.

**Pattern:**
1. HARD-GATE — do not write output until key inputs confirmed
2. Scan inputs, identify missing items
3. Ask one question at a time until complete
4. Generate and write document to disk
5. Inform user of file path, ask if adjustments needed

**No proposal step, no section-by-section confirmation** — once inputs are complete, proceed directly.

| Skill | Output Path |
|---|---|
| `project-intake` | `docs/00-intake.md` |
| `prd` | `prd/PRD.md` |
| `ux-analyst` | `prd/UX-FLOWS.md` |
| `proto-service-generator` | `internal/service/<module>/*.go` |

**Note on `proto-service-generator`:** This skill is in Tier 1 because the proto files it reads serve as a complete, machine-precise specification. All structural decisions (function signatures, message types, package layout) are already determined by the proto contract before generation starts. If the proto is ambiguous or missing, the skill asks for clarification before generating — but it does not need a design phase.

---

### Tier 2 — Deep Dialogue + Local Docs

For **design/decision** skills where multiple reasonable options exist and output is depended upon by downstream skills.

**Pattern:**
1. HARD-GATE — do not write any file until design is fully approved
2. Scan existing context (related docs, code, prior designs)
3. Ask one clarifying question at a time for key decision points
4. For non-obvious decisions, propose 2-3 options with recommendation
5. Present design section by section, confirm each before proceeding
6. Write local document(s) to disk after full approval
7. Inform user of file path(s), ask if handoff to next skill is needed

**TodoWrite is required** to track checklist steps.

| Skill | Output Path | Path Rule |
|---|---|---|
| `db-schema-designer` | `prd/DDL.md` or `design/<feature>/schema.md` | Use `design/<feature>/schema.md` if the user names a specific feature/module or the request is scoped to a change-id; default to `prd/DDL.md` otherwise |
| `proto-api-generator` | `prd/API.md` or `design/<feature>/api.md` | Use `design/<feature>/api.md` if the user names a specific feature/module or the request is scoped to a change-id; default to `prd/API.md` otherwise |
| `spec-writer` | `prd/SPEC.md` | Always `prd/` |
| `spec-diff-pipeline` | `design/changes/<change-id>/` (multiple artifacts) | Always feature-scoped |

---

## Universal Conventions (Both Tiers)

- **Always write to disk** — never output only in conversation
- **Path follows dev.md** — `prd/`, `design/changes/<id>/`, `docs/`
- **TodoWrite** — required for Tier 2, optional for Tier 1
- **Language policy** — skill instructions may be Chinese or English; HARD-GATE and structural markers follow the existing language of the skill being edited; output document language follows user input
- **HARD-GATE format:**

```
<HARD-GATE>
[Condition that must be met before writing output]
If inputs are incomplete, ask first. Do not assume.
</HARD-GATE>
```

---

## SKILL.md Structure Templates

The templates below show the sections to add or replace. Match the existing language of each skill file (Chinese or English).

### Tier 1 Template — Chinese

```markdown
<HARD-GATE>
未确认 [关键输入项] 前，不生成任何文档输出。
如果输入不完整，先追问再写。
</HARD-GATE>

## 工作流程

1. 扫描用户提供的输入，识别缺失项
2. 逐一追问缺失的关键信息（每次只问一个）
3. 确认无遗漏后，生成文档并写入本地文件
4. 告知用户文件路径，询问是否需要调整

## 输出
写入 `<标准路径>`，不要只在对话中输出。
```

### Tier 1 Template — English

```markdown
<HARD-GATE>
Do not generate any document output until [key inputs] are confirmed.
If inputs are incomplete, ask first — do not assume.
</HARD-GATE>

## Workflow

1. Scan the user's input and identify what is missing
2. Ask one question at a time until all key inputs are confirmed
3. Generate the document and write it to disk
4. Report the file path and ask if adjustments are needed

## Output
Write to `<standard path>`. Do not produce output only in the conversation.
```

### Tier 2 Template — Chinese

```markdown
<HARD-GATE>
未完成对话确认流程前，不写任何本地文件。
设计有分歧时，提方案让用户选，不要自行决定。
</HARD-GATE>

## Checklist（用 TodoWrite 跟踪）

1. 扫描现有上下文（相关文档、代码、已有设计）
2. 逐一追问关键决策点（每次一个问题）
3. 针对非显然决策，提 2-3 个方案 + 推荐
4. 分段展示设计，每段确认后再进入下一段
5. 全部确认后写本地文档
6. 告知路径，询问是否移交下一个 skill

## 输出
写入 `<标准路径>`。有多个 artifact 时，逐一写入并列出清单。
```

### Tier 2 Template — English

```markdown
<HARD-GATE>
Do not write any local file until the design is fully confirmed through dialogue.
When a decision has multiple reasonable options, present them — do not choose unilaterally.
</HARD-GATE>

## Checklist (track with TodoWrite)

1. Scan existing context (related docs, code, prior designs)
2. Ask one clarifying question at a time for key decision points
3. For non-obvious decisions, propose 2-3 options with a recommendation
4. Present the design section by section; confirm each before proceeding
5. Write local document(s) after full approval
6. Report file path(s) and ask if handoff to the next skill is needed

## Output
Write to `<standard path>`. If multiple artifacts are produced, list all paths after writing.
```

---

## Implementation Order

### Batch 1 — Light Dialogue (smaller changes, establish baseline)
1. `project-intake`
2. `prd`
3. `ux-analyst`
4. `proto-service-generator`

### Batch 2 — Deep Dialogue (larger changes)
5. `proto-api-generator`
6. `spec-writer`
7. `spec-diff-pipeline`
8. `db-schema-designer` — finalize: the in-progress refactor already adds dialogue structure; this step adds the mandatory disk-write step and ensures consistency with the other Tier 2 skills

**Note on `db-schema-designer`:** The current in-progress version (see `skills/skills/db-schema-designer/SKILL.md`) adds HARD-GATE and dialogue structure but does not yet write output to disk. Step 8 specifically adds that behavior.

---

## Testing

After each skill is updated, use `skill-creator` — a skill bundled in this repo, invoked via `/skill-creator` or by triggering the skill naturally — to run 2-3 real test prompts and verify:
- HARD-GATE triggers correctly (incomplete input → asks before writing)
- Dialogue flow feels natural (not too many / too few questions)
- Output is written to correct local path

**Example test prompts per tier:**

Tier 1 (`project-intake`):
- Complete input: "我要做一个任务管理系统，用户可以创建任务、分配给同事、设置截止日期"
- Incomplete input: "帮我整理项目需求" (no details → should ask before writing)

Tier 2 (`proto-api-generator`):
- Complete input: "根据 prd/SPEC.md 设计任务模块的 API，需要 CRUD 和状态流转接口"
- Ambiguous input: "设计一个 API" (no scope → should ask which module, which message type strategy, etc.)

---

## Reference

- `skills/skills/db-schema-designer/SKILL.md` — Tier 2 reference implementation (in progress; disk-write to be added in step 8)
- `skills/skills/spec-diff-pipeline/SKILL.md` — Tier 2 skill; Required Inputs section becomes the HARD-GATE block
- `skills/skills/spec-writer/SKILL.md` — Tier 2 skill with existing Workflow Decision Tree; HARD-GATE prepended, clarification step added as step 0
- `skills/skills/proto-service-generator/SKILL.md` — Tier 1 skill in English; HARD-GATE gates on proto + generated interface presence
- `references/dev.md` — canonical directory structure and workflow stages
- superpowers brainstorming skill — HARD-GATE and checklist pattern source
