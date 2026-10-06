# Skill Authoring Contract

Rules for every skill in this repository. `tests/validate-skill-references.sh` enforces
the mechanical parts. Follow this file when adding or editing a skill.

## Why These Rules Exist

Three audiences read a skill, and they read different amounts of it:

| Audience | What it sees | What it needs |
|----------|--------------|---------------|
| The router (always loaded) | only `description` | enough to pick the right skill and reject the wrong one |
| A strong model | `SKILL.md` plus the references it decides it needs | a decision path, not prose |
| A weak model | `SKILL.md` plus whatever it is told to load | explicit, numbered, unconditional instructions |

Progressive disclosure is the budget that makes this work: descriptions stay cheap,
`SKILL.md` stays skimmable, and detail waits in references until a named condition is true.

## Size Budgets

| File | Budget | Why |
|------|--------|-----|
| `description` | 400 characters, one line | all 20 descriptions load in every session |
| `SKILL.md` | 150 lines | a skill the model must read end to end before acting |
| `references/*.md` | 200 lines | one loadable unit; split by topic, not by length |

A reference file that outgrows 200 lines is usually two topics. Split it by the question
it answers, then give each half its own load-when trigger.

## Description Formula

Write exactly three parts, in this order:

```
<What it does, one sentence>. Use when <concrete triggers, including Chinese phrasings>.
Not for <adjacent job> — that is `other-skill`.
```

Rules:

1. Open with the action, not with "This skill".
2. Triggers are things a user actually types. Keep Chinese trigger phrases — they carry real recall.
3. End with a boundary clause naming the neighbouring skill whenever one exists. Use the
   exact form ``that is `skill-name` `` so the test can resolve it.
4. Drop these: "high-quality", "REQUIRED", "always use it instead of", "comprehensive",
   restatements of the skill name, and any trigger already implied by another trigger.
5. One line. No line breaks inside the value.

## SKILL.md Section Order

Use these headings, in this order, omitting any that carry nothing:

```markdown
# Title

<One or two sentences: what this produces.>

## Inputs          # only when work must not start without them
## Steps           # numbered, imperative, 5-9 steps
## Reference Map   # table of every reference file and its load-when trigger
## Rules           # one line per rule, numbered
## Output          # the exact deliverable shape, or a pointer to a template reference
## Related Skills  # required; Upstream / Downstream / Boundary / Companion / fallback
```

Rules:

1. **Steps are a path, not a menu.** One numbered list the model can follow top to bottom.
   Branches belong in a table with a `When` column, never in nested prose.
2. **Reference Map is the only place references are introduced.** Do not also list them in
   an Overview paragraph and a Resources section — that is the duplication that made these
   files long. Every reference file under the skill must appear in the map exactly once.
3. **Every map row states a condition**, so a model knows when *not* to read the file.
   "Read for background" is not a condition. "Read before writing the first `.proto` field" is.
4. **Rules are flat.** One rule per line, imperative, no sub-bullets. If a rule needs a
   paragraph of justification, the justification goes in a reference.
5. **No duplicated content between a SKILL.md and its references.** The SKILL.md names the
   decision; the reference holds the detail.

## Reference Map Shape

```markdown
## Reference Map

Load the smallest set that answers the question in front of you.

| Read | When |
|------|------|
| [references/modeling-rules.md](references/modeling-rules.md) | Before proposing entities, fields, or indexes |
| [references/review-output-template.md](references/review-output-template.md) | Before writing the review document |
```

Order rows by when they are typically needed. Mark anything that is always needed by putting
it first and saying so ("Always, before step 2").

## Writing For Weak Models

1. Prefer imperative sentences: "Write the file to `prd/SPEC.md`." Not: "The spec should
   normally be written somewhere like `prd/SPEC.md`."
2. One instruction per sentence. Split any sentence containing "and also", "while", or
   a parenthetical qualifier.
3. Give concrete values: real paths, real command names, real field names.
4. Tables beat prose for anything with more than two cases.
5. State the failure mode next to the rule it protects, in the same row or line.
6. Never use "etc.", "and so on", or "as appropriate" in a rule. Enumerate, or say
   "anything else in the same category, which you must name in your report".
7. Avoid "consider", "may want to", "ideally". Decide, or give a `When` table.

## Related Skills Block

Required on every skill except the router. Exact bullet labels, because the test greps them:

```markdown
## Related Skills

- Upstream — <skill(s)> and the artifact they hand over. Say what to do when it is missing.
- Downstream — <skill(s)> and the condition that makes the handoff ready.
- Boundary — the adjacent skill, and which half of the work each side owns.
- Companion — a skill that runs alongside this one, or `none`.
- If a referenced skill is not installed in this session, name it in the handoff message and continue with the current artifact; do not stall.
```

## Checklist Before Committing a Skill Change

1. `bash tests/run-tests.sh` passes.
2. `description` is under 400 characters and names its boundary skill.
3. `SKILL.md` is under 150 lines and follows the section order.
4. Every reference file is linked from the Reference Map with a load-when condition.
5. No reference file exceeds 200 lines.
6. The router's Workflow Map and `README.md` still describe the skill correctly.
