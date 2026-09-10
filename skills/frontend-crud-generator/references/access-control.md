# Access Control

## Table of Contents
- [Principle: Discover, Never Invent](#principle-discover-never-invent)
- [Two Levels of Permission](#two-levels-of-permission)
- [Wiring Generated Pages](#wiring-generated-pages)
- [Vocabulary](#vocabulary)
- [Best Practices](#best-practices)

## Principle: Discover, Never Invent

Permission systems are project-specific. The generated client does not tell you which roles or permission keys exist, and a wrong key fails silently — the button simply never renders, or the route is never reachable.

Before wiring anything, find out from the project:

- which mechanism gates routes or menus (role list, permission key, guard component, middleware)
- which mechanism gates buttons or actions (directive, wrapper component, `can*` helper)
- which keys already exist for comparable modules, and where they are declared
- whether unknown modules default to visible or hidden

If no permission system exists, or the proposed module has no keys defined, generate without permission gates and say so in Validation Notes. Do not introduce a permission system the project does not have.

## Two Levels of Permission

| Level | Controls | Typical source |
|---|---|---|
| Page / route access | whether the page can be opened | route metadata, guard wrapper, menu filter |
| Action / button visibility | whether a specific control appears | permission key check, directive, helper |

Keep them separate. Hiding a button is not access control — the backend remains authoritative and must reject unauthorized calls. Generated UI only reflects permissions; it never substitutes for them.

## Wiring Generated Pages

- Route-level: follow the discovered mechanism exactly. If comparable modules set no role/permission metadata, do not add it speculatively.
- Action-level: gate create, edit, delete, detail, export, and import buttons when the project defines keys for them.
- Default to hidden rather than disabled when a key exists: disabled controls advertise capability the user does not have.
- When a list page is reachable but a mutation is not permitted, the mutation controls are simply absent.
- Report which keys were used and where they were declared. If a key is referenced but not defined anywhere, that is a Blocking Issue, not a detail.

## Vocabulary

Use the project's existing key names. Where a project follows the common sphere convention, the vocabulary is:

| Key | Operation |
| --- | --- |
| `btn_list` | list page access |
| `btn_add` | create |
| `btn_edit` | edit |
| `btn_delete` | delete |
| `btn_detail` | view detail |
| `btn_export` | export |
| `btn_import` | import |

Prefixes such as `btn_` and `role_` come from the project; never rename existing keys to fit this table.

## Best Practices

1. **Consistent naming** — reuse the project's prefix and casing.
2. **Default to hidden** — an unknown key should not reveal a control.
3. **Backend-driven** — real permissions arrive from the API; never hardcode a superuser set in generated page code.
4. **Report the wiring** — the Convention Report states the mechanism and keys; Validation Notes state anything assumed.
5. **Degrade cleanly** — no permission metadata is a valid outcome; inventing it is not.
