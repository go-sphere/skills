---
name: godoc
description: Write Go doc comments and verified examples that let AI agents use a module through go doc. Use when documenting Go packages, 补充 Go 文档, 写给 AI agent 的 API 文档, or adding usage examples. Not for general test-suite review — that is `go-test-engineering`.
---

# Go Doc for Agents

Make the exported API usable from package and symbol documentation without requiring a
separate guide. Put the smallest useful recipe in doc comments and verify it with Go examples.

## Steps

1. Read repository instructions, the supported Go version, and existing documentation conventions. Identify the requested packages and preserve unrelated changes.
2. Read exported declarations, implementations, tests, and current examples. Establish actual behavior before describing it. Flag unresolved contracts instead of inventing guarantees.
3. Read the syntax reference before writing comments. Read the examples reference when adding or repairing usage recipes.
4. Write one package overview, usually in `doc.go`. Name the use case, recommended entry points, shortest setup/use/cleanup sequence, and relevant alternatives. Include an indented code recipe with the real import path so plain `go doc` exposes basic usage.
5. Document each in-scope exported symbol's contract at its declaration. Keep each symbol understandable when queried alone. Use the contract table below to select relevant details.
6. Add or update external-package examples for the important recipes. Reuse existing examples when they already cover the workflow. Keep the short comment recipe consistent with its compiled example.
7. Format changed Go files using the repository's formatter. Inspect package and symbol output with `go doc`. Run example tests and the affected package tests. Compile-check comment recipes too; they are not tested automatically.
8. Review the diff for unsupported promises, broken symbol links, stale examples, and unrelated edits. Report changed packages and verification results.

| Documented surface | Contract details to establish |
|---|---|
| Package | What it solves, recommended constructor or entry point, setup, dependencies, cleanup |
| Type | Zero-value usability, initialization, concurrent access, ownership of mutable data |
| Function or method | Effect, parameter meaning, units, defaults, return meaning, side effects |
| Fallible operation | Missing/empty behavior, sentinel or typed errors, wrapping, partial results, panic conditions |
| Context-aware operation | Cancellation/deadline behavior, whether work outlives the call |
| Resource or task | Who closes/stops it, required ordering, repeated calls, post-close behavior |
| Interface | Guarantees every implementation must satisfy; document driver differences on drivers |
| Options or fields | Units, valid range, zero meaning, precedence, when configuration takes effect |

## Reference Map

| Read | When |
|---|---|
| [references/comment-syntax.md](references/comment-syntax.md) | Before writing or restructuring Go doc comments |
| [references/examples.md](references/examples.md) | When writing, updating, or verifying a code recipe or Example function |

## Rules

1. Keep essential usage and contracts in Go comments; a README link must not replace them.
2. Describe observable behavior and caller decisions rather than narrating implementation.
3. Use existing identifiers and actual import paths; do not invent APIs to make a recipe convenient.
4. Document only relevant constraints; do not fill every comment with a fixed checklist.
5. Name the symbol in its opening sentence; use the repository's documentation language.
6. Use Go doc syntax inside comments, not full Markdown.
7. State concurrency, ownership, nil, and lifecycle guarantees only when supported by code or an established contract.
8. Preserve behavior and public signatures; documentation work does not authorize redesigning the API.
9. Keep examples deterministic and usable through the exported API; handle errors and release owned resources.
10. Keep package overviews concise; link detailed symbol contracts rather than duplicating all of them.
11. Do not create a separate usage guide or modify consumer AGENTS.md merely to compensate for incomplete Go documentation.
12. Do not claim docs are automatically loaded by agents; consumers must query go doc or their documentation tools.

## Output

Deliver the edited Go doc comments and any example tests inside the requested module.
Summarize the packages touched, usable entry points, exact checks run, and unresolved contracts.
Provide a concrete package or symbol `go doc` command the consumer can use.

## Related Skills

- Upstream — none; use the existing exported API and established behavior as inputs.
- Downstream — none; self-contained API documentation and verified recipes are the deliverable.
- Boundary — `go-test-engineering` owns general suite audits and contract-test design; this skill owns documentation and usage examples.
- Companion — `protoc-plugin-engineering` when documenting a generator's own Go API; preserve generated-file ownership rules.
- If a referenced skill is not installed in this session, name it in the handoff message and continue with the current artifact; do not stall.
