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
5. TodoWrite used to track execution steps in complex skills

## Non-Goals

- Cross-skill handoff orchestration (not in scope)
- Adding new skills for missing workflow stages (not in scope)
- Changing the tools, references, or content logic of any skill (only the dialogue structure)

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

| Skill | Output Path |
|---|---|
| `db-schema-designer` | `prd/DDL.md` or `design/<feature>/schema.md` |
| `proto-api-generator` | `prd/API.md` or `design/<feature>/api.md` |
| `spec-writer` | `prd/SPEC.md` |
| `spec-diff-pipeline` | `design/changes/<change-id>/` (multiple artifacts) |

---

## Universal Conventions (Both Tiers)

- **Always write to disk** — never output only in conversation
- **Path follows dev.md** — `prd/`, `design/changes/<id>/`, `docs/`
- **TodoWrite** — required for Tier 2, optional for Tier 1
- **Language policy** — skill instructions may be Chinese or English; output document language follows user input
- **HARD-GATE format:**

```
<HARD-GATE>
[Condition that must be met before writing output]
If inputs are incomplete, ask first. Do not assume.
</HARD-GATE>
```

---

## SKILL.md Structure Templates

### Tier 1 Template Addition

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

### Tier 2 Template Addition

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

---

## Implementation Order

### Batch 1 — Light Dialogue (smaller changes, establish baseline)
1. `project-intake`
2. `prd`
3. `ux-analyst`
4. `proto-service-generator`

### Batch 2 — Deep Dialogue (larger changes, reference db-schema-designer)
5. `proto-api-generator`
6. `spec-writer`
7. `spec-diff-pipeline`
8. `db-schema-designer` (finalize, ensure consistency with other Tier 2 skills)

---

## Testing

After each skill is updated, use `skill-creator` to run 2-3 real test prompts and verify:
- HARD-GATE triggers correctly (incomplete input → asks before writing)
- Dialogue flow feels natural (not too many / too few questions)
- Output is written to correct local path

---

## Reference

- `skills/skills/db-schema-designer/SKILL.md` — Tier 2 reference implementation (in progress)
- `references/dev.md` — canonical directory structure and workflow stages
- superpowers brainstorming skill — HARD-GATE and checklist pattern source
