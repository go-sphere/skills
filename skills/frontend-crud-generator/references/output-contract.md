# Output Contract

## Table of Contents
- [Output Modes](#output-modes)
- [Writing Rules](#writing-rules)
- [Report Format Selection](#report-format-selection)
- [Condensed Report (Simple Tasks)](#condensed-report-simple-tasks)
- [Full Report (Complex Tasks)](#full-report-complex-tasks)
- [Quality Gates](#quality-gates)

## Output Modes

| Mode | Behavior |
|---|---|
| `write` (default) | create and edit files in the project, then report |
| `content` | write nothing; print complete file contents for review or copy |

Switch to `content` whenever the user says "show me first", "don't write", "只看", or "先给我看". Never write to a path the user has not seen: list target paths before the first write of a session.

## Writing Rules

**New files** — write the complete file. No placeholders, no `TODO`, no partial snippets.

**Existing shared files** — router tables, menu arrays, wrapper/transport modules, permission declarations:

1. read the file immediately before editing
2. apply a minimal edit with an exact anchor; never rewrite the whole file
3. if the file's content does not match what discovery reported, stop editing that file and report the divergence instead of forcing the edit
4. never edit generated files (`Api.ts` and other generated artifacts)

**Already-existing pages** — if a page, route module, menu entry, or wrapper method for the module already exists, this run updates it: read it, patch with exact anchors, and leave everything discovery did not ask you to change. Never regenerate or replace a working page wholesale because the requested page mode happens to include it.

When a page can be added without touching a shared file, prefer that. When registration requires an edit, do it in the same pass and report exactly what changed.

## Report Format Selection

- **Condensed report**: straightforward CRUD with clear client methods
- **Full report**: dashboards, custom actions, multiple registration points, or any degraded run

The report is the only thing guaranteed to be read by the user. It always opens with the Convention Report from [conventions-discovery.md](conventions-discovery.md).

## Condensed Report (Simple Tasks)

Exactly four sections:

### 1) Convention Report
Framework and pack, generated client path, API consumption pattern, route registration mechanism, sources read, confidence.

### 2) Recognized APIs
```
- `<methodName>`: `<classification>` | `<HTTP method> <path>` | `<key params>`
  - Response: `<itemsKey>` / `<totalKey>` after the project's unwrap convention
  - Missing: `<none | list of absent CRUD operations>`
```

### 3) Files
Every path written (or proposed in `content` mode), marking each as new or edited.

### 4) Route Registration
What was registered, in which file, through which mechanism; plus the route names introduced.

## Full Report (Complex Tasks)

All sections below, in order:

1. **Convention Report** — as above.
2. **Scaffold Fit Decision** — module, page mode, route base, whether a detail page is included, notable choices.
3. **Recognized APIs** — full endpoint list with classification, request params, and response keys.
4. **API Capability Matrix**

   | Operation | Method | Path | Available | Notes |
   | --- | --- | --- | --- | --- |

5. **Files** — paths written/edited (or proposed), new vs edited.
6. **File Contents** — only in `content` mode, or when the user asks; complete files.
7. **Validation Notes** — assumptions, risks, the project's typecheck/build command and whether it was run, open questions.
8. **Blocking Issues** — only when a gate failed: the rule, why the output is non-deliverable, and the proposed correction. Also list requested capabilities the client cannot support as contract gaps, each naming the endpoint or field it would need. The condensed report carries the same gaps in its `Missing` line.

## Quality Gates

Before reporting, verify all of these; pack-specific checks live in each pack's `## Verification`.

- [ ] Convention Report is present and its sources are real files that were read
- [ ] Only one framework pack's idioms appear in the output
- [ ] Generated files untouched; no new runtime dependency added; no new shared business component introduced
- [ ] Pagination base and query keys match the project's observed convention
- [ ] Filters correspond to real query parameters; server `total` preserved
- [ ] Invalid route id shows an error and never falls back to create mode
- [ ] Destructive actions use the project's confirmation primitive
- [ ] Mutations refresh the affected region
- [ ] Uncertain payload fields are runtime-guarded
- [ ] Missing endpoints are reported and the UI degrades cleanly
- [ ] Requested capabilities with no backing endpoint or field are reported as contract gaps, not fabricated
- [ ] Existing pages, routes, menus, and wrappers were checked first and are updated in place when present
- [ ] Route names are unique (where the framework uses them) and registration is complete for the project's mechanism
- [ ] Page-caching identity rule satisfied when the framework caches pages (component name matches route name where required)
- [ ] Permission wiring uses only keys that exist in the project, or is explicitly absent
- [ ] Report section order and paths match this contract
