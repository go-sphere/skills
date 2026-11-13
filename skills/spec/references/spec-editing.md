# Spec Editing Playbook

Use this guide when modifying an existing spec. The goal is to produce a coherent revision, not a local patch that leaves stale assumptions behind.

## 1. Build a Change Map First

Read the document completely and identify:
- which section introduces the changed requirement
- which downstream sections depend on it
- whether the change is additive, behavioral, structural, or breaking

Do not edit linearly without this map.

## 2. Apply the Impact Matrix

If you change one of these areas, revisit the linked areas too.

- Problem statement or goals:
  Revisit non-goals, success criteria, workflows, and validation.
- Component ownership:
  Revisit boundaries, dependencies, observability, and operator actions.
- Entity shape or schema:
  Revisit contracts, examples, migration, compatibility, and tests.
- Config fields or defaults:
  Revisit precedence, environment resolution, validation, and reload behavior.
- Workflow rules:
  Revisit state transitions, retries, cancellation, cleanup, and failure handling.
- Failure behavior:
  Revisit logs, metrics, status reporting, retries, and user-visible outcomes.

## 3. Prefer Stable Structure

Unless the old structure is actively blocking clarity:
- keep heading names stable
- keep section numbering stable
- keep canonical terms stable

This makes diffs smaller and preserves shared vocabulary across code, tickets, and docs.

## 4. Make Breaking Changes Loud

If a revision changes a contract or compatibility expectation, state it explicitly.

Use a subsection such as:

```markdown
### Compatibility Impact
- Backward compatible: no
- Affected consumers: [list]
- Required migration: [steps]
- Safe rollout order: [sequence]
```

Do not make readers infer breaking changes from a field rename buried elsewhere.

## 5. Remove Contradictions, Do Not Outvote Them

After revising the main section, search the rest of the spec for old terminology, outdated defaults, previous stop conditions, or stale examples. Delete or rewrite the obsolete text.

A revised spec should tell one story from start to finish.

## 6. Finish with a Coherence Check

Before considering the revision complete, confirm these questions:
- Do the goals still match the workflows?
- Do the workflows still match the contracts and entities?
- Do failure rules still match retry and cleanup behavior?
- Do validation rules still prove the intended behavior?
- Are open questions still open, or did the revision quietly decide them?

## 7. Suggested Delta Summary

When useful, append a short summary after editing:

```markdown
## Change Summary
- Changed: [main semantic change]
- Impacted sections: [list]
- Compatibility: [compatible or breaking]
- Follow-up needed: [tests, migration, rollout, unanswered questions]
```

## 8. Editing Heuristics

- Prefer precise replacements over adding hedging text.
- Prefer one canonical rule over duplicated near-rules.
- Prefer explicit assumptions over implied assumptions.
- Prefer local brevity if the global contract remains complete.
- Prefer adding a new subsection when a change introduces a new concern that readers will need to find later.
