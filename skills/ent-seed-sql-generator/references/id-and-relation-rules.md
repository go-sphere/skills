# ID and Relationship Rules

## Deterministic ID Policy

Seed IDs must be stable across reruns and meaningful to reviewers.

### Integer PKs

- Reserve non-overlapping ranges per table or domain group.
- Use monotonic increments inside each range.
- Keep room for future rows; do not pack values too tightly.

Example range strategy:

- `users`: `1000-1999`
- `organizations`: `2000-2999`
- `projects`: `3000-3999`

### String PKs

- Use semantic IDs derived from stable business keys.
- Keep one format per table (for example `usr_*`, `org_*`, `proj_*`).
- Avoid opaque random suffixes.

Examples:

- `usr_admin`
- `org_acme`
- `proj_mobile_app`

### UUID PKs

- Prefer deterministic UUID generation from stable key tuple.
- Recommended tuple: `namespace + table + business_key`.
- Avoid UUID4 randomness unless the user explicitly requests random behavior.

## Relationship Integrity Rules

- Insert parent tables before dependent child tables.
- For join tables, insert both endpoints first, then join rows.
- Reuse exact FK values from source rows; never remap IDs mid-file.
- Preserve logical dependency order even if dialect supports deferred constraints.

## Multi-Tenant Constraints

When tenant/account scope exists:

- Seed tenant/account rows first.
- Ensure every scoped table row has valid tenant/account FK.
- Do not create cross-tenant references unless isolation testing is the goal.

## Business Coherence Rules

- Timestamps must be plausible (create <= update).
- Lifecycle/state values must be realistic (`draft -> active -> archived` style progression).
- Ownership chains must resolve to existing principals.

## Consistency Ledger (Required Internal Check)

Keep an internal mapping ledger while drafting:

- logical record key -> concrete ID
- unique columns already consumed
- FK references and existence checks

Use this ledger to prevent collisions, orphan rows, and accidental duplicate uniques.
