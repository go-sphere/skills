# Model Extraction Guide

## Input Priority

Use this precedence when sources conflict:

1. Explicit user requirement in current prompt
2. Ent schema and migration definitions
3. Demo program behavior and hardcoded examples
4. Product documentation narrative
5. Conservative inference (must be stated as assumption)

## Entity Extraction Checklist

For each entity/table, capture:

- Table name
- Primary key type and generation style
- Required fields vs nullable fields
- Unique fields/composite unique constraints
- Status/state fields and allowed values
- Audit fields (`created_at`, `updated_at`, etc.)

For Ent-based inputs, inspect:

- `field.*` definitions (`Optional`, `Default`, `Unique`, `Sensitive`)
- `edge.To` and `edge.From` plus `Required`/`Unique`
- enum-like validation constraints

## Relationship Extraction Checklist

Capture relationship graph with cardinality:

- 1-N: parent id in child table
- 1-1: unique foreign key or shared key strategy
- N-N: explicit join table and uniqueness pair

Create a dependency graph and topological insert order before writing SQL.

## Data Size Heuristic

Unless user gives a target size:

- Core entities: 3-10 rows each
- Reference dictionaries: complete minimal set
- Join rows: enough to demonstrate real linkage, not full cross product

## Assumption Discipline

If a required field meaning is unclear, infer from:

- Field name (`status`, `owner_id`, `tenant_id`)
- Related records in demo code
- Product terminology in docs

Always record assumptions in SQL header comments with concise bullets.
