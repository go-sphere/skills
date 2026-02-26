# SQL Output Pattern

## File Skeleton

```sql
-- seed.sql
-- Source inputs: prompt + product_doc.md + demo.go
-- Dialect: sqlite (assumed)
-- Assumptions:
-- - users.email is unique
-- - projects belongs to organizations

BEGIN TRANSACTION;

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

## Insert Strategy

- Always include explicit column list.
- Group inserts by table and dependency order.
- Prefer batched multi-row `INSERT` for readability and speed.

## Conflict Strategy

Only add conflict handling when requested or clearly needed:

- PostgreSQL: `ON CONFLICT (...) DO NOTHING/UPDATE`
- SQLite: `INSERT OR IGNORE` (or modern upsert syntax)
- MySQL: `INSERT IGNORE` or `ON DUPLICATE KEY UPDATE`

## Verification Snippets

Optionally append lightweight checks:

```sql
SELECT COUNT(*) AS org_count FROM organizations;
SELECT COUNT(*) AS user_count FROM users;
SELECT COUNT(*) AS project_count FROM projects;
```

Use verification queries only when user asks for post-insert checks.
