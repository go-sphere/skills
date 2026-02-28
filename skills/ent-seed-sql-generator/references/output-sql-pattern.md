# SQL Output Pattern

Use this file as the final assembly pattern after model extraction and ID planning.

## Header Contract

Every seed artifact should start with concise metadata comments:

- source inputs used
- SQL dialect (and whether inferred/assumed)
- execution strategy (`one-shot`, `idempotent`, or `upsert`)
- non-trivial assumptions

## Canonical Skeleton

```sql
-- seed.sql
-- Source inputs: prompt + product_doc.md + demo.go
-- Dialect: sqlite (assumed)
-- Strategy: idempotent
-- Assumptions:
-- - users.email is unique
-- - projects belongs to organizations

BEGIN TRANSACTION;

-- optional cleanup section (strategy-dependent)

-- 1) organizations
INSERT INTO organizations (id, name, slug, created_at)
VALUES
  (2001, 'Acme', 'acme', '2026-01-01 09:00:00'),
  (2002, 'Nimbus', 'nimbus', '2026-01-01 09:05:00');

-- 2) users
INSERT INTO users (id, org_id, email, display_name, password_hash, created_at)
VALUES
  (1001, 2001, 'admin@acme.dev', 'Acme Admin', '$2b$12$...', '2026-01-01 09:10:00'),
  (1002, 2002, 'owner@nimbus.dev', 'Nimbus Owner', '$2b$12$...', '2026-01-01 09:11:00');

-- 3) projects
INSERT INTO projects (id, org_id, owner_id, name, status, created_at)
VALUES
  (3001, 2001, 1001, 'Mobile App', 'active', '2026-01-01 09:20:00'),
  (3002, 2002, 1002, 'Growth Site', 'active', '2026-01-01 09:21:00');

COMMIT;
```

## Strategy Snippets

Choose one strategy and keep it consistent in the file:

- `one-shot`: plain inserts, no cleanup/conflict control
- `idempotent`: cleanup or conflict-safe inserts for reruns
- `upsert`: update existing records where required by scenario

Dialect examples:

- PostgreSQL: `ON CONFLICT (...) DO NOTHING/DO UPDATE`
- SQLite: `INSERT OR IGNORE` or `ON CONFLICT (...) DO UPDATE`
- MySQL: `INSERT IGNORE` or `ON DUPLICATE KEY UPDATE`

## Authoring Rules

- Always include explicit column lists.
- Keep table blocks in dependency order.
- Prefer multi-row `VALUES` blocks when readable.
- Keep comments concise and audit-friendly.

## Optional Verification Queries

Append verification queries only when requested:

```sql
SELECT COUNT(*) AS org_count FROM organizations;
SELECT COUNT(*) AS user_count FROM users;
SELECT COUNT(*) AS project_count FROM projects;
```
