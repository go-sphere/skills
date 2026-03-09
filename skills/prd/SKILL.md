---
name: prd
description: "Generate high-quality Product Requirements Documents (PRDs) following go-sphere development workflow. Use when: user wants to create a PRD, document requirements, plan a feature, or translate business ideas into product specs. Required for the PRD solidification phase in AI Agent collaboration development."
---

# Product Requirements Document (PRD)

Generate comprehensive, production-grade PRDs that bridge the gap between business vision and technical execution.

## When to Use This Skill

**Trigger when:**
- User wants to "write a PRD", "create product requirements", or "document a feature"
- Transitioning from Intake to PRD solidification phase
- User provides initial ideas, demos, or prototypes needing formalization
- User asks to "plan a feature", "define scope", or "clarify requirements"

**Produces:**
- `prd/PRD.md` - the main Product Requirements Document

---

## Workflow

### Decision Point: Discovery or Draft?

**Ask clarifying questions FIRST when:**
- User provides only vague idea ("build something cool")
- Critical details missing (who, what success looks like)
- Multiple reasonable interpretations possible

**Skip to drafting when:**
- User provides sufficient detail in initial request
- Clear problem statement + target users + success criteria provided
- User explicitly says "just write it" or provides complete context

### Phase 1: Discovery (If Needed)

Gather context through targeted questions. Keep it brief - 3-5 questions max.

**Typical Questions:**
- Problem: What pain point are we solving?
- Why now: Why important at this time?
- Success: How will we measure success?
- Scope: What's in/out of scope?
- Users: Who are the target users?

### Phase 2: Analysis & Synthesis

Synthesize understanding:
- Map key user flows
- Identify core business processes
- Define module boundaries
- List key pages/scenes
- Identify risks and dependencies

### Phase 3: PRD Drafting

Generate document using the standard schema below.

---

## PRD Schema (Use These Exact Section Names)

### 1. Background & Goals

**Must include:**
- Problem statement (what pain point?)
- Why now (why important at this time?)
- Success criteria (3-5 measurable KPIs)

### 2. User Personas

**Must include:**
- Primary users identified
- Their characteristics/jobs
- Current workflow pain points

### 3. Core Business Processes

**Must include:**
- Primary workflow steps
- Decision points
- Key user interactions

**DO NOT include:** Detailed state machines, API calls, database schemas

### 4. Module Boundaries

**Must include:**
- What modules/components involved
- How modules interact (high-level)
- External dependencies

**DO NOT include:** Technical implementation details, code structure

### 5. Pages & Scenes Inventory

**Must include:**
- List of key pages/scenes
- Entry conditions
- Exit conditions

### 6. Success Criteria

**Must include:**
- Quantitative metrics (not vague "fast", "easy")
- How each metric measured

**Example:**
- BAD: "The system should be fast"
- GOOD: "Search returns within 200ms for 10k records"

### 7. Scope / Non-Scope

**Must include:**
- What's built in this phase
- What's NOT built (explicitly)

### 8. Risks & Dependencies

**Must include:**
- Technical risks
- External dependencies
- Key assumptions

---

## Quality Standards

### Include (Do)

- Business context and motivation
- User roles and workflows
- Clear measurable success metrics
- Explicit scope boundaries
- Known risks and dependencies

### Exclude (Don't)

**These belong in SPEC, NOT PRD:**
- Field types or data structures
- Database table designs
- API response structures
- Internal state machines
- Detailed error codes
- Technical architecture details
- Code-level implementation

### Example: What Goes Where

| Content | PRD | SPEC |
|---------|-----|------|
| Problem statement | ✅ | ✅ |
| User personas | ✅ | ✅ |
| User flows | ✅ | ✅ |
| Success metrics | ✅ | ✅ |
| Module boundaries | ✅ | ✅ |
| Page inventory | ✅ | ❌ |
| API contracts | ❌ | ✅ |
| Database schema | ❌ | ✅ |
| State machines | ❌ | ✅ |
| Technical architecture | ❌ | ✅ |

---

## Expert Insights

> "The most important section is the first part - what is the background and context? What is the problem, why does it matter, and why does it matter now?" - Maggie Crowley

> "Whenever we're devising a new product, we start by writing a press release describing it in a way that speaks to the customer." - Bill Carr

> "We tend to keep them pretty light. I like to have the minimal amount of context that ensures everyone's on the same page." - Eric Simons

> "If you're not prototyping and building to see what you want to build, you're doing it wrong." - Aparna Chennapragada

---

## Common Mistakes to Avoid

1. **Starting with solution** - Always lead with problem and context
2. **No success criteria** - Every PRD needs measurable KPIs
3. **Including technical details** - Save API/schema for SPEC phase
4. **Vague scope** - Explicitly state what's NOT included
5. **Missing "Why Now"** - Justify timing, not just what and how
6. **Over-detailing** - Keep PRD lightweight; save depth for SPEC

---

## Completion Criteria

Ensure at completion:
- [x] Background clearly states problem and why now
- [x] User personas identified
- [x] Core business processes documented
- [x] Module boundaries defined (high-level only)
- [x] Pages/scenes inventory complete
- [x] Success criteria are measurable
- [x] Scope/non-scope explicitly listed
- [x] Risks and dependencies documented
- [x] NO technical implementation details

---

## Output Location

Default to `prd/PRD.md`

Follow user's specified location if provided.
