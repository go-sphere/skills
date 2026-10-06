# UX-FLOWS.md and SCREEN-INVENTORY.md Structure

Use these section shapes. Keep the headings; drop a subsection only when the screen genuinely has
nothing to say there, and note why.

## UX-FLOWS.md

### 1. Document Overview

State what the document covers, how many key screens it describes, and the high-level user
journey.

### 2. Screen/Page Definitions

Repeat sections 2.1 through 2.7 for each key screen.

#### 2.1 Page Purpose

- What is this page's goal?
- Who uses it?
- What business problem does it solve?

#### 2.2 Entry Conditions

- How does the user arrive at this page?
- What must be true before the page is accessible?
- What authentication or authorization is required?
- What prerequisite states must hold, for example "must have completed step 1"?

#### 2.3 Exit Conditions

- What triggers leaving this page?
- Where does the user go next?
- Which other exit paths exist?

#### 2.4 Key Actions (Business-Level)

Describe business semantics, not "click submit button". Use this table:

| Action | When Enabled | State Change | Failure Handling | Success Behavior | Recovery |
|--------|--------------|--------------|------------------|------------------|----------|
| Submit form | All required fields filled | Advances to `pending_review` | Show validation errors | Redirect to list page | Resume from last saved draft |
| Delete item | User has delete permission | Marks as `archived` | Show error toast, keep page | Refresh list, show success toast | None (soft delete) |
| Approve request | Request in `pending` state | Advances to `approved` | Show error with reason | Navigate to next item | Can revert within 24h |

Every action must state all six columns:

- **When Enabled** — under what conditions the action can be triggered.
- **State Change** — whether the action advances or modifies business state.
- **Failure Handling** — what happens on failure, and which error messages appear.
- **Success Behavior** — redirect, toast, state update.
- **Recovery** — whether an interrupted flow can be resumed.

#### 2.5 User-Visible States

Document every state the user can see: loading (what shows while fetching), empty (what shows
with no data), error (what shows when something fails), success (what confirms completion), and
draft or in-progress (whether the user can save and return later).

#### 2.6 Blocking Conditions

What prevents the user from proceeding: permission checks, unmet prerequisites, business rule
blocks such as "cannot submit after deadline", system unavailability, rate limiting.

For each one: what triggers the block, what the user sees, and how to resolve it.

#### 2.7 Error and Exception Scenarios

What can go wrong and how it is communicated: network errors, validation failures, permission
denied, concurrent modification conflicts, timeouts, service unavailable.

For each one: the user-facing message, whether the action can be retried, whether data is
preserved, and any compensating action needed.

## SCREEN-INVENTORY.md

Write this file only when the system has many screens.

### Screen List

| Screen ID | Screen Name | Route/URL | Primary User Role | Purpose |
|-----------|-------------|-----------|-------------------|---------|
| S1 | Order List | `/orders` | Customer | View and manage orders |
| S2 | Order Detail | `/orders/:id` | Customer | View order details |
| S3 | Order Edit | `/orders/:id/edit` | Customer | Modify order |
| S4 | Order Create | `/orders/new` | Customer | Create new order |

### Navigation Map

```
S1 (List) → S2 (Detail) → S3 (Edit)
S1 (List) → S4 (Create)
S2 (Detail) → S3 (Edit)
```
