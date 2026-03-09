# Change Classification

Use these labels consistently in `01-spec-delta.md` and `02-impact-map.md`.

## Additive

Use when the change adds a new capability, field, section, API, state, or entity without changing the meaning of existing behavior.

Signals:
- new optional field
- new endpoint or workflow branch
- new report section
- new state that old clients can ignore safely

## Behavioral

Use when existing behavior changes even if the shape stays similar.

Signals:
- changed transition guards
- changed validation semantics
- changed defaults
- changed retry or blocking behavior
- changed archival or read-only semantics

## Breaking

Use when compatibility assumptions likely change for clients, data, routes, or persisted state.

Signals:
- renamed or removed field
- incompatible enum change
- route or RPC semantic change
- required field added to existing contract
- migration needed for persisted data

## Deepening

Use when the spec becomes more explicit and operational but the intended external behavior is mostly unchanged.

Signals:
- stronger definition of state machine
- new internal states clarified
- explicit config precedence added
- explicit recovery or observability rules added
- authoritative vs derived state clarified

Deepening often still creates downstream work. Do not classify it as "no-op" just because the user intent did not change.

## Mixed

Use when the spec contains more than one meaningful change class. If so, enumerate the components separately instead of averaging them into one vague label.

## Classification Rule

When uncertain between `behavioral` and `deepening`, ask:
- Would a compatible implementation still behave the same externally?

If mostly yes, classify as `deepening`.
If no, classify as `behavioral`.
