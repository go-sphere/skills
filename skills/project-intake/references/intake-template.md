# Intake Document Structure

Eight sections, in this order, in `docs/00-intake.md`. Keep each one to 3-5 lines.

## 1. Project Goal (One Sentence)

The core goal in one sentence. Two lines maximum.

## 2. Current Available Inputs

Every input that exists: PRD or requirement documents, prototype and design files or links, code
repositories or modules, and the user's supplementary descriptions.

Mark each item `completed` or `draft/initial`.

## 3. Missing Inputs

Inputs the project needs but does not have yet, for example key business process diagrams, user
role definitions, success criteria, or existing system boundaries.

## 4. Confirmed Primary Roles

The user roles and system roles involved. No permission detail.

## 5. Confirmed Primary Modules

The core functional modules or system components identified so far.

## 6. Demo Reference Type

Mark exactly one:

- **Visual reference** — the demo shows UI and visual style only; it does not represent interaction behavior.
- **Behavior reference** — the demo shows the real interaction flow; those behaviors must be implemented.

This choice decides whether `ux-analyst` runs before `prd`.

## 7. Existing Code/Repository Boundaries

When code already exists: the related repositories or modules, their technology stack, and which
parts might be reused.

## 8. Unresolved Items List

Every item still undetermined, one sentence each.
