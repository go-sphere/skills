# Layout Contract and File Ownership

Read this before editing any file in a generated go-sphere project.

The layout is an executable starter, not a framework. A generated project keeps
receiving upstream layout changes, so *where* you put code decides whether it
survives the next sync.

## 1. Identify the Layout Variant

Read `.sphere/layout.json` → `name`, or `.sphere/layout.lock.json` → `name` in a
generated project. Capabilities differ; do not assume the standard layout.

| Layout | `name` | Upstream module | Capabilities |
|--------|--------|-----------------|--------------|
| Standard | `standard` | `github.com/go-sphere/sphere-layout` | protobuf, gin-http, ent, wire, swagger, typescript-client, dashboard, password-auth, local-storage |
| Simple | `simple` | `github.com/go-sphere/sphere-simple-layout` | protobuf, gin-http, wire |
| Bun | `bun` | `github.com/go-sphere/sphere-bun-layout` | protobuf, gin-http, bun, wire, swagger, password-auth |
| Telegram | `telegram` | `github.com/go-sphere/sphere-telegram-layout` | everything in standard, plus telegram-bot |

Consequences that bite:

- **The standard layout has no bot integration.** `proto/bot/**`,
  `internal/server/bot/**`, and `internal/service/bot/**` exist only in the
  Telegram layout. Do not scaffold them into the standard layout.
- **`protoc-gen-route` runs only in the Telegram layout.** The other three
  layouts have a four-plugin chain. Check `buf.gen.yaml`.
- **The simple layout has no Ent, no swagger, no auth.** Schema-first workflows
  do not apply to it. Do not invent `internal/pkg/database/schema/**` there.
- **The bun layout uses Bun, not Ent.** Ent-specific guidance (entcrud,
  entbind/entmap, `WithIgnoreFields`) does not transfer.
- Optional capabilities do not leave empty placeholder directories. A missing
  directory means the capability is absent, not that it needs creating.

## 2. Classify Every Path Before Editing

`.sphere/layout.json` carries an `ownership` object. Patterns are evaluated in
this order, first match wins, and patterns must not overlap:

1. `generated`
2. `layout_owned`
3. `mixed`
4. everything unmatched → `project_owned` (the `default`)

| Class | Meaning | What you may do |
|-------|---------|-----------------|
| `generated` | Regenerated from handwritten sources | Never hand-edit. Change the source and rerun the generator. |
| `layout_owned` | Stable tooling, CI, generators, reusable adapters | Avoid editing. Upstream applies these directly when the local copy still equals the recorded base — your edit forces a three-way merge forever. |
| `mixed` | Application assembly and built-in feature seams | Edit carefully. Preserve both layout wiring and project additions; these are always semantically merged. |
| `project_owned` | Business contracts and implementation | Your code belongs here. Upstream never replaces it. |

Typical classification in the standard layout (always re-read the actual file —
this is illustrative, not authoritative):

- `generated`: `api/**`, `swagger/**`, `internal/pkg/database/ent/**`,
  `internal/pkg/render/{entbind,entmap}/**`, `cmd/app/wire_gen.go`,
  `proto/entpb/entpb.proto`, `buf.lock`, `go.sum`, `build/**`
- `layout_owned`: `.github/workflows/**`, `buf*.yaml`, `cmd/tools/**`,
  `scripts/**`, `internal/pkg/app/**`, `internal/pkg/httpsrv/**`, `AGENTS.md`
- `mixed`: `Makefile`, `go.mod`, `cmd/app/{builder,main,wire}.go`,
  `internal/config/**`, `internal/wire.go`, `internal/*/wire.go`,
  `internal/server/*/web.go`, `internal/pkg/database/schema/**`,
  `internal/pkg/auth/**`, `internal/service/api/auth.go`,
  `proto/api/v1/{auth,user}.proto`, `proto/shared/v1/user.proto`
- `project_owned`: your new `proto/<domain>/v1`, `internal/biz/<domain>`,
  `internal/service/<domain>`, and their tests

Note that `cmd/tools/**` is layout-owned even though
`cmd/tools/gen/entcrud/main.go` is where entities get registered. Registering a
new entity there is expected and required; restructuring that tool is not.

## 3. Where New Product Code Goes

| Kind of code | Destination |
|--------------|-------------|
| API contract | `proto/<domain>/v1` |
| Business use case / background task | `internal/biz/<domain>` |
| Generated-interface implementation | `internal/service/<domain>` |
| Transport construction and route registration | `internal/server/<transport>` |
| Persistence model | `internal/pkg/database/schema` (Ent layouts only) |
| Project-local adapter or infrastructure | `internal/pkg` |

Do not put product-specific logic into layout-owned helpers. A helper that is
genuinely reusable across unrelated projects and imports nothing from the
project module belongs in a versioned go-sphere library instead of being copied
into the layout.

## 4. Projects Without a Lock or Ownership File

A project created before the ownership contract has no `.sphere/`. Then:

- Treat every path as `project_owned` except the generated outputs listed in
  [source-of-truth-and-generated-boundaries.md](source-of-truth-and-generated-boundaries.md).
- Say explicitly in your report that ownership could not be verified.
- Do not fabricate a lock file to make the project look current. Adopting a
  legacy project into the contract is a separate, deliberate operation — see
  the `sphere-layout-sync` skill.

## 5. Reporting

For every edited path, state its classification. Any `layout_owned` or `mixed`
edit needs a one-line justification and a note on what it costs at the next
layout sync. If you cannot justify it, move the code to a `project_owned` path
instead.
