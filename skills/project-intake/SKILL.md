---
name: project-intake
description: Organize scattered project inputs and generate standardized intake documents. Use when users mention project kickoff, requirement initialization, PRD preparation, input organization, requirement gathering, or turning prototypes/demos/drafts into structured documents. Apply to new feature development, project initialization, requirement clarification, and similar scenarios. Always complete intake before writing PRD or any detailed design.
---

# Project Intake

Organize scattered project inputs into structured documentation, clarifying project boundaries and known/unknown items.

## When to Use

Use this skill when:
- User mentions "new project", "new feature", "build something"
- User provides PRD draft, prototype, screenshots, Figma links
- User describes ideas without formal documentation
- Team needs to clarify "what's known vs what's unknown"
- Before any detailed design work begins

## Input Types

This skill processes the following input types (not all required, but will identify and document):

- Initial PRD or requirement description
- Prototype demos (Figma, HTML demo, screenshots, videos)
- Interaction specifications or user flow diagrams
- Existing code repositories or modules
- User's verbal descriptions or supplementary notes
- Competitive analysis or reference cases

## Output Document

Generate `docs/00-intake.md` (create docs directory if it doesn't exist)

## Document Structure

Organize content with the following structure, keeping each section concise:

### 1. Project Goal (One Sentence)

Express the core project goal in one sentence. No more than two lines.

### 2. Current Available Inputs

List all provided inputs including:
- PRD/requirement documents (if any)
- Prototype/design files or links
- Code repositories or modules
- User's supplementary descriptions

**Mark the status** of each item: "completed" or "draft/initial"

### 3. Missing Inputs

List inputs required for project kickoff but not yet provided, such as:
- Key business process diagrams
- User role definitions
- Success criteria
- Existing system boundaries

### 4. Confirmed Primary Roles

List user roles or system roles involved. No need for detailed permission definitions.

### 5. Confirmed Primary Modules

List identified core functional modules or system components.

### 6. Demo Reference Type

Clearly mark:
- **Visual Reference**: Demo serves as UI/visual style reference only, not representing interaction behavior
- **Behavior Reference**: Demo shows complete user interaction flow, behaviors need to be implemented

### 7. Existing Code/Repository Boundaries

If existing code exists:
- Related repositories or modules
- Technology stack of the code
- Which parts might be reused

### 8. Unresolved Items List

List all items that are not yet determined and need clarification. One sentence per item.

## Writing Principles

1. **Keep it concise**: 3-5 lines per section, don't expand into details
2. **Lock down boundaries**: Focus on clarifying "known vs unknown", not writing detailed requirements
3. **Distinguish facts from assumptions**: Mark what user confirmed vs what's inferred
4. **Don't write PRD**: Don't expand business processes or feature details here - these belong in PRD phase

## Completion Criteria

Ensure at completion:
- [x] Project goal clearly expressed in one sentence
- [x] All available inputs listed with status marked
- [x] Missing inputs clearly listed, team knows what to collect next
- [x] Confirmed roles and modules listed
- [x] Demo reference type clearly marked
- [x] Code boundaries identified (if applicable)
- [x] All unresolved items listed

## Output Location

If user doesn't specify output location, default to:
- `docs/00-intake.md`

Follow user's specified location if provided.
