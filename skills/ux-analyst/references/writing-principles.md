# Writing Behavior Instead of UI

## Write Behavior, Not UI

Bad:

- "Click the Submit button"
- "The form has Name and Email fields"
- "Show a success message"

Good:

- "Submit becomes enabled only when all required fields have valid values and no validation errors exist"
- "On submission, advances the order to `pending_review`; on failure, displays field-level validation errors and preserves all entered data"
- "On success, displays a toast for 3 seconds, then redirects to `/orders` with the success filter applied"

## Include State Transitions

For each action that changes state, document it in this shape:

```
Action: Submit Order
Pre-condition: All required fields valid AND order total > 0
Post-state: draft → pending_review
Side effects:
  - Order number generated
  - Confirmation email queued
  - Inventory reserved for 15 minutes
```

## Define Entry and Exit Criteria

Every page must answer three questions:

1. How do I get here? (entry)
2. What happens next? (exit)
3. What blocks me? (blocking)

## Do Not Describe Layout

Leave these out — they are design decisions, not behavior:

- "Button is in the top-right corner"
- "The form uses a two-column layout"
- "Card has a shadow and rounded corners"

## Do Not Use Generic Actions

Each of these is unfinished. Say exactly what happens:

- "Process submission" — process it how, into which state?
- "Show message" — which message, in which context?
- "Save data" — saved where, with which validation?
