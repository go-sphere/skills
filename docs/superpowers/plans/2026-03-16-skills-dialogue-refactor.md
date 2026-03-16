# Skills Dialogue Refactor Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add HARD-GATE, dialogue-first interaction, and mandatory disk-write to 8 core skills, split into two tiers based on complexity.

**Architecture:** Tier 1 (4 skills) gets a HARD-GATE block + Workflow section prepended. Tier 2 (4 skills) gets a HARD-GATE block + Checklist with TodoWrite, plus disk-write step. No domain content or references are changed.

**Tech Stack:** Markdown editing only. Verification via grep + manual skill-creator test.

---

## Chunk 1: Batch 1 — Tier 1 Skills (Light Dialogue)

### Task 1: `project-intake` — Add HARD-GATE + Workflow

**Files:**
- Modify: `skills/skills/project-intake/SKILL.md`

Current state: English, no HARD-GATE, no gate before output, has "Output Location" at bottom.

Changes:
1. Add `<HARD-GATE>` block immediately after the opening paragraph (before `## When to Use`)
2. Add `## Workflow` section before `## When to Use`
3. Add explicit "write to disk" reminder to "## Output Location" section

- [ ] **Step 1: Open and verify current state**

Run: `grep -n "HARD-GATE\|## Workflow\|write" skills/skills/project-intake/SKILL.md`
Expected: no HARD-GATE matches, no Workflow section

- [ ] **Step 2: Add HARD-GATE block after line 8 (after opening paragraph)**

Insert after line 8 (`...known/unknown items.`):

```markdown

<HARD-GATE>
Do not generate `docs/00-intake.md` until you have confirmed the following from the user:
- At least one concrete input (PRD draft, prototype, description, or repo link)
- A one-sentence project goal (or enough context to infer one)
If inputs are too vague to produce a meaningful intake doc, ask first — do not assume.
</HARD-GATE>
```

- [ ] **Step 3: Add Workflow section before `## When to Use`**

Insert before `## When to Use`:

```markdown
## Workflow

1. Scan whatever the user has provided — extract project goal, available inputs, and visible gaps
2. If the goal is unclear or no concrete inputs exist, ask one question to unblock (e.g., "What problem is this project solving?")
3. Ask one follow-up question at a time until you have enough to fill all 8 sections
4. Write `docs/00-intake.md` to disk (create `docs/` directory if needed)
5. Report the file path and ask if anything needs adjusting

```

- [ ] **Step 4: Update Output Location section to emphasize disk write**

Find:
```
If user doesn't specify output location, default to:
- `docs/00-intake.md`

Follow user's specified location if provided.
```

Replace with:
```
If user doesn't specify output location, default to:
- `docs/00-intake.md`

Follow user's specified location if provided.

**Always write the file to disk. Do not output the intake document only in the conversation.**
```

- [ ] **Step 5: Verify changes**

Run: `grep -n "HARD-GATE\|## Workflow\|Always write" skills/skills/project-intake/SKILL.md`
Expected: all three strings found

- [ ] **Step 6: Commit**

```bash
git add skills/skills/project-intake/SKILL.md
git commit -m "feat(project-intake): add HARD-GATE and dialogue workflow (Tier 1)"
```

---

### Task 2: `prd` — Add HARD-GATE + enforce disk write

**Files:**
- Modify: `skills/skills/prd/SKILL.md`

Current state: English, has partial dialogue ("Ask clarifying questions FIRST when...") under `## Workflow > Decision Point`. No HARD-GATE, no explicit disk-write enforcement.

Changes:
1. Add `<HARD-GATE>` block after the opening paragraph (before `## When to Use This Skill`)
2. Add explicit disk-write step to Phase 3 (PRD Drafting)
3. Strengthen "Output Location" to require disk write

- [ ] **Step 1: Verify current state**

Run: `grep -n "HARD-GATE\|write.*disk\|Always write" skills/skills/prd/SKILL.md`
Expected: no matches

- [ ] **Step 2: Add HARD-GATE block after line 8 (after opening paragraph)**

Insert after line 8 (`...between business vision and technical execution.`):

```markdown

<HARD-GATE>
Do not write `prd/PRD.md` until Phase 1 (Discovery) is complete or the user has provided sufficient context to skip it.
"Sufficient context" means: problem statement, target users, and at least one success criterion are clear.
If any of these are missing, ask — one question at a time — before drafting.
</HARD-GATE>
```

- [ ] **Step 3: Add disk-write step to Phase 3**

Find:
```
### Phase 3: PRD Drafting

Generate document using the standard schema below.
```

Replace with:
```
### Phase 3: PRD Drafting

Generate document using the standard schema below, then:
1. Write the completed PRD to `prd/PRD.md` (create `prd/` directory if needed)
2. Report the file path to the user
3. Ask if any section needs adjustment
```

- [ ] **Step 4: Strengthen Output Location**

Find:
```
Default to `prd/PRD.md`

Follow user's specified location if provided.
```

Replace with:
```
Default to `prd/PRD.md`

Follow user's specified location if provided.

**Always write to disk. Do not output the PRD only in the conversation.**
```

- [ ] **Step 5: Verify**

Run: `grep -n "HARD-GATE\|write.*disk\|Always write" skills/skills/prd/SKILL.md`
Expected: matches found in all three places

- [ ] **Step 6: Commit**

```bash
git add skills/skills/prd/SKILL.md
git commit -m "feat(prd): add HARD-GATE and disk-write enforcement (Tier 1)"
```

---

### Task 3: `ux-analyst` — Add HARD-GATE + Workflow

**Files:**
- Modify: `skills/skills/ux-analyst/SKILL.md`

Current state: English, no HARD-GATE, no workflow gate, has "Output Location" at bottom.

Changes:
1. Add `<HARD-GATE>` block after opening paragraph
2. Add `## Workflow` section before `## Input`
3. Add disk-write note to Output Location

- [ ] **Step 1: Verify current state**

Run: `grep -n "HARD-GATE\|## Workflow\|Always write" skills/skills/ux-analyst/SKILL.md`
Expected: no matches

- [ ] **Step 2: Add HARD-GATE block after line 8**

Insert after line 8 (`...engineers and other AI agents can use to implement features.`):

```markdown

<HARD-GATE>
Do not write `prd/UX-FLOWS.md` until at least one visual or behavioral input has been provided (Figma, screenshot, video, HTML demo, or wireframe).
If no visual input exists, ask the user to provide one before proceeding.
If input exists but the scope (which pages/screens to cover) is unclear, ask one clarifying question first.
</HARD-GATE>
```

- [ ] **Step 3: Add Workflow section before `## Input`**

Insert before `## Input`:

```markdown
## Workflow

1. Check what visual/behavioral inputs are available (Figma, screenshots, video, HTML, PRD)
2. If no visual input exists, ask the user to provide one before proceeding
3. If scope is unclear (too many screens, ambiguous priority), ask one question to narrow it
4. Analyze inputs — extract page purposes, entry/exit conditions, key actions, states
5. Write `prd/UX-FLOWS.md` to disk (and `prd/SCREEN-INVENTORY.md` if scope warrants it)
6. Report file path(s) and ask if any page behavior needs clarification

```

- [ ] **Step 4: Add disk-write note to Output Location**

Find:
```
Default: `prd/UX-FLOWS.md` and `prd/SCREEN-INVENTORY.md`

Follow user's specified location if provided.
```

Replace with:
```
Default: `prd/UX-FLOWS.md` and `prd/SCREEN-INVENTORY.md`

Follow user's specified location if provided.

**Always write to disk. Do not output UX-FLOWS only in the conversation.**
```

- [ ] **Step 5: Verify**

Run: `grep -n "HARD-GATE\|## Workflow\|Always write" skills/skills/ux-analyst/SKILL.md`
Expected: all three found

- [ ] **Step 6: Commit**

```bash
git add skills/skills/ux-analyst/SKILL.md
git commit -m "feat(ux-analyst): add HARD-GATE and dialogue workflow (Tier 1)"
```

---

### Task 4: `proto-service-generator` — Add HARD-GATE

**Files:**
- Modify: `skills/skills/proto-service-generator/SKILL.md`

Current state: English, has "When To Use" prerequisites (proto files exist, interface present, safe append-only). No HARD-GATE, no explicit gate enforcing those prerequisites before generation starts.

Changes:
1. Add `<HARD-GATE>` block after opening paragraph, gating on proto files + generated interface presence

- [ ] **Step 1: Verify current state**

Run: `grep -n "HARD-GATE" skills/skills/proto-service-generator/SKILL.md`
Expected: no matches

- [ ] **Step 2: Add HARD-GATE block after line 8**

Insert after line 8 (`...api/<module>/v1/*.sphere.pb.go.`):

```markdown

<HARD-GATE>
Do not generate or modify any service file until:
1. The target module is known (e.g., `task`, `user`, `order`)
2. The generated `*ServiceHTTPServer` interface exists in `api/<module>/v1/*.sphere.pb.go`

If the module name is not specified, ask: "Which module should I generate service files for?"
If the proto generation has not been run yet, stop and ask the user to run `make gen/proto` first.
Do not guess the module from context alone if there are multiple candidates.
</HARD-GATE>
```

- [ ] **Step 3: Verify**

Run: `grep -n "HARD-GATE" skills/skills/proto-service-generator/SKILL.md`
Expected: HARD-GATE block found

- [ ] **Step 4: Commit**

```bash
git add skills/skills/proto-service-generator/SKILL.md
git commit -m "feat(proto-service-generator): add HARD-GATE on module + interface presence (Tier 1)"
```

---

## Chunk 2: Batch 2 — Tier 2 Skills (Deep Dialogue + Local Docs)

### Task 5: `proto-api-generator` — Add HARD-GATE + Checklist + disk-write

**Files:**
- Modify: `skills/skills/proto-api-generator/SKILL.md`

Current state: English, has "Task Intake" and "Core Decisions" sections. No HARD-GATE, no Checklist, no disk-write step. Currently outputs proto design only in conversation.

Changes:
1. Add `<HARD-GATE>` block after opening paragraph
2. Add `## Checklist` section with TodoWrite after "Operating Model"
3. Add output path + disk-write step before "Progressive Reference Loading"

- [ ] **Step 1: Verify current state**

Run: `grep -n "HARD-GATE\|Checklist\|TodoWrite\|prd/API" skills/skills/proto-api-generator/SKILL.md`
Expected: no matches

- [ ] **Step 2: Add HARD-GATE block after line 8**

Insert after line 8 (`...contracts for go-sphere scaffold projects.`):

```markdown

<HARD-GATE>
Do not write any `.proto` file or API design document until the following are confirmed through dialogue:
- Which service module is being designed (e.g., `task`, `user`, `order`)
- Whether this is a new file or an addition to an existing proto
- The primary message strategy (entpb / shared / custom) for at least the main entities

If any of these are missing, ask one question at a time before proceeding.
When a design decision has multiple reasonable options (message type, route strategy, pagination shape), present 2-3 options with your recommendation — do not choose unilaterally.
</HARD-GATE>
```

- [ ] **Step 3: Add Checklist section after "## Operating Model" (before "## Task Intake")**

Insert before `## Task Intake`:

```markdown
## Checklist (track with TodoWrite)

At task start, call TodoWrite to create a task for each numbered item below. Mark each complete before moving to the next.

1. Confirm module name, file mode (new / add to existing), and message strategy
2. Ask clarifying questions one at a time for any ambiguous scope or behavior
3. For non-obvious decisions, propose 2-3 options with recommendation
4. Present service overview (service name, RPC list) — get approval
5. Present message designs section by section — get approval for each
6. Run Final Gate checklist (`references/go-sphere-api-definitions-checklist.md`)
7. Write the API design doc to disk (`prd/API.md` or `design/<feature>/api.md`)
8. Ask if the user wants to proceed to proto file generation

**Output path rule:** Use `design/<feature>/api.md` if the user names a specific feature or change-id; default to `prd/API.md` otherwise.

```

- [ ] **Step 4: Verify**

Run: `grep -n "HARD-GATE\|## Checklist\|prd/API" skills/skills/proto-api-generator/SKILL.md`
Expected: all three found

- [ ] **Step 5: Commit**

```bash
git add skills/skills/proto-api-generator/SKILL.md
git commit -m "feat(proto-api-generator): add HARD-GATE, Checklist, and disk-write (Tier 2)"
```

---

### Task 6: `spec-writer` — Prepend HARD-GATE + add step 0 to New Spec Workflow

**Files:**
- Modify: `skills/skills/spec-writer/SKILL.md`

Current state: English, has `## Workflow Decision Tree` with three branches. No HARD-GATE. New Spec Workflow starts directly at step 1 (distill contract anchors) without first asking if inputs are sufficient.

Changes:
1. Add `<HARD-GATE>` block after `## Overview`, before `## Workflow Decision Tree`
2. Prepend step 0 to New Spec Workflow: "Clarify missing inputs before proceeding"
3. Add disk-write step to all three workflow branches

- [ ] **Step 1: Verify current state**

Run: `grep -n "HARD-GATE\|step 0\|write.*disk\|prd/SPEC" skills/skills/spec-writer/SKILL.md`
Expected: no matches

- [ ] **Step 2: Add HARD-GATE block before `## Workflow Decision Tree`**

Insert before `## Workflow Decision Tree`:

```markdown
<HARD-GATE>
Do not write `prd/SPEC.md` or any spec section until the following are confirmed:
- The problem being specified is clear (not just "write a spec for X" with no further context)
- For New Spec: problem statement, system boundaries, and at least one key constraint are known
- For Revision: the existing spec file path is known and the nature of the change is described

If inputs are insufficient, ask one question at a time before proceeding to the Workflow Decision Tree.
When a specification decision has multiple valid approaches, present options — do not silently pick one.
</HARD-GATE>

```

- [ ] **Step 3: Add step 0 to New Spec Workflow**

Find:
```
## New Spec Workflow

1. Distill the request into the initial contract anchors:
```

Replace with:
```
## New Spec Workflow

0. **Clarify missing inputs** (if not already resolved by the HARD-GATE step above).
   Ask one question at a time until you have: problem statement, system boundary, at least one constraint or non-goal. Do not proceed to step 1 until these are clear.

1. Distill the request into the initial contract anchors:
```

- [ ] **Step 4: Add disk-write step at end of New Spec Workflow**

Find (exact):
```
7. Finish with conformance clarity.
   Include validation strategy, test expectations, migration or compatibility notes, implementation notes when needed, and explicit open questions.
```

Replace with:
```
7. Finish with conformance clarity.
   Include validation strategy, test expectations, migration or compatibility notes, implementation notes when needed, and explicit open questions.

8. Write the completed spec to `prd/SPEC.md` (create directory if needed). Report the path and ask the user to review before handing off to implementation.
```

- [ ] **Step 5: Add disk-write note to Revision Workflow**

Find (exact):
```
8. Finish with a delta check.
   Confirm the revised spec still tells one coherent story from goals through conformance.
```

Replace with:
```
8. Finish with a delta check.
   Confirm the revised spec still tells one coherent story from goals through conformance.

9. Write the updated spec to disk and confirm the path with the user.
```

- [ ] **Step 6: Verify**

Run: `grep -n "HARD-GATE\|Clarify missing inputs\|prd/SPEC\|Write the completed" skills/skills/spec-writer/SKILL.md`
Expected: all four strings found

- [ ] **Step 7: Commit**

```bash
git add skills/skills/spec-writer/SKILL.md
git commit -m "feat(spec-writer): add HARD-GATE, clarification step 0, and disk-write (Tier 2)"
```

---

### Task 7: `spec-diff-pipeline` — Reformat Required Inputs as HARD-GATE

**Files:**
- Modify: `skills/skills/spec-diff-pipeline/SKILL.md`

Current state: English, has `## Required Inputs` section that already gates on `repo_root`, `spec_path`, and diff mode. No `<HARD-GATE>` block. Output artifacts are already written to disk (the skill already produces files in `design/changes/<change-id>/`).

Changes:
1. Reformat `## Required Inputs` as a `<HARD-GATE>` block with explicit "do not start pipeline" statement
2. Keep all existing input requirements unchanged — this is a structural reformat only

- [ ] **Step 1: Verify current state**

Run: `grep -n "HARD-GATE\|## Required Inputs" skills/skills/spec-diff-pipeline/SKILL.md`
Expected: `## Required Inputs` found, no HARD-GATE

- [ ] **Step 2: Find the exact location of Required Inputs section**

Run: `grep -n "## Required Inputs\|### Mode 1\|### Mode 2\|### Supporting" skills/skills/spec-diff-pipeline/SKILL.md`

- [ ] **Step 3: Prepend HARD-GATE block before `## Required Inputs`**

Insert immediately before `## Required Inputs`:

```markdown
<HARD-GATE>
Do not start the pipeline until all required inputs below are confirmed.
Ask the user for any missing inputs one at a time before proceeding to Stage 1.
</HARD-GATE>

```

- [ ] **Step 4: Verify**

Run: `grep -n "HARD-GATE\|## Required Inputs" skills/skills/spec-diff-pipeline/SKILL.md`
Expected: HARD-GATE block appears just before Required Inputs section

- [ ] **Step 5: Commit**

```bash
git add skills/skills/spec-diff-pipeline/SKILL.md
git commit -m "feat(spec-diff-pipeline): reformat Required Inputs as HARD-GATE block (Tier 2)"
```

---

### Task 8: `db-schema-designer` — Add disk-write step to Checklist

**Files:**
- Modify: `skills/skills/db-schema-designer/SKILL.md`

Current state: Already has HARD-GATE, Checklist with TodoWrite, and full dialogue structure. Missing: the final review brief is produced in conversation but not written to disk.

Changes:
1. Add disk-write as step 8a in the Checklist (between "Produce final review brief" and "User approves")
2. Update Phase 4 description to include writing the file

- [ ] **Step 1: Verify current state**

Run: `grep -n "HARD-GATE\|write.*disk\|prd/DDL\|design.*schema" skills/skills/db-schema-designer/SKILL.md`
Expected: HARD-GATE found, no disk-write or output path

- [ ] **Step 2: Update Checklist step 8 to include disk-write**

Find:
```
8. **Produce final review brief** — using [references/review-output-template.md](references/review-output-template.md)
9. **User approves review brief** — ask explicitly before handing off
```

Replace with:
```
8. **Produce final review brief** — using [references/review-output-template.md](references/review-output-template.md)
9. **Write review brief to disk** — default path: `prd/DDL.md`; use `design/<feature>/schema.md` if the request is scoped to a named feature or change-id
10. **User approves review brief** — ask explicitly before handing off to `ent-schema-implementer`
```

- [ ] **Step 3: Update Phase 4 to reference disk-write**

Find:
```
After writing the brief, ask the user to review it:

> "Here's the full design brief. Please look it over — if anything needs adjusting, let me know and I'll update it. Once you're happy, I can hand off to `ent-schema-implementer` to start writing the Ent schemas."

Wait for explicit approval before handing off.
```

Replace with:
```
After producing the brief, write it to disk:
- Default: `prd/DDL.md`
- Feature-scoped: `design/<feature>/schema.md` (use when the user names a specific module or change-id)

Then ask the user to review it:

> "Design brief written to `<path>`. Please look it over — if anything needs adjusting, let me know and I'll update it. Once you're happy, I can hand off to `ent-schema-implementer` to start writing the Ent schemas."

Wait for explicit approval before handing off.
```

- [ ] **Step 4: Verify**

Run: `grep -n "prd/DDL\|design.*schema\|write.*disk\|Write review" skills/skills/db-schema-designer/SKILL.md`
Expected: output path references found in both Checklist and Phase 4

- [ ] **Step 5: Commit**

```bash
git add skills/skills/db-schema-designer/SKILL.md
git commit -m "feat(db-schema-designer): add disk-write step to Checklist and Phase 4 (Tier 2 finalize)"
```

---

## Post-Implementation: Smoke Test Checklist

After all 8 skills are committed, verify the HARD-GATE is present in every file:

- [ ] **Run across all 8 skills**

```bash
for skill in project-intake prd ux-analyst proto-service-generator proto-api-generator spec-writer spec-diff-pipeline db-schema-designer; do
  echo -n "$skill: "
  grep -c "HARD-GATE" skills/skills/$skill/SKILL.md
done
```

Expected: each skill shows `2` (opening + closing tag).

- [ ] **Verify disk-write present in all 8**

```bash
for skill in project-intake prd ux-analyst proto-api-generator spec-writer db-schema-designer; do
  echo -n "$skill: "
  grep -c "write\|disk\|prd/\|design/" skills/skills/$skill/SKILL.md
done
```

Expected: each has at least one match.

- [ ] **Use skill-creator to test at least one Tier 1 and one Tier 2 skill**

Tier 1 test (`project-intake`):
- Incomplete prompt: "帮我整理项目需求" → should ask clarifying question, NOT write file
- Complete prompt: "任务管理系统，用户创建任务、分配给同事、设置截止日期，基于已有 Go 后端" → should write `docs/00-intake.md`

Tier 2 test (`proto-api-generator`):
- Ambiguous: "设计一个 API" → should ask module name before proceeding
- Scoped: "根据 prd/SPEC.md 设计任务模块的 proto API，CRUD + 状态流转" → should go through dialogue, then write `prd/API.md`
