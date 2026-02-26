# ID and Relationship Rules

## Deterministic ID Policy

Generate IDs that are stable across runs and meaningful in domain context.

### Integer IDs

Reserve fixed ranges per table:

- `users`: 1001-1999
- `organizations`: 2001-2999
- `projects`: 3001-3999

Use sequential increments within range. Never randomize.

### String IDs

Use semantic keys:

- `usr_admin`
- `org_acme`
- `proj_mobile_app`

Keep format consistent within table.

### UUID IDs

Use deterministic UUID (v5-style) from stable key tuple:

- namespace constant + table name + business key

Do not use random UUID4 in seed data unless user explicitly asks for randomness.

## Foreign Key Integrity Rules

- Insert parent rows before child rows.
- For join tables, insert both sides first, then join rows.
- Reuse exact IDs from source rows; do not remap mid-file.
- If dialect allows deferred constraints, still preserve logical order for readability.

## Multi-Tenant Convention

When tenant/account scopes exist:

- Create 2-3 tenants/accounts first.
- Ensure scoped tables include valid tenant/account FK.
- Keep cross-tenant leakage out of sample data unless explicitly testing isolation bugs.

## Business Meaning Rules

- Keep timestamps coherent (creation before update; parent before child).
- Keep status transitions plausible (e.g., `draft` before `published`).
- Keep ownership chains valid (`project.owner_id` must match an existing user).

## Consistency Ledger

Before final SQL, maintain an internal mapping ledger:

- Entity logical name -> concrete ID
- Unique field values already used
- FK target existence

Use this ledger to prevent collisions and broken links.
