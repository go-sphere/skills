# Plugin Output Rules

Templates, generated-output determinism, in-place AST rewriting, error and comment handling, and
compatibility. Directory layout, entrypoint, config model, and the generator contract live in
`plugin-conventions.md`.

## Templates

Embed the default with `go:embed`; never reassign the variable after init:

```go
//go:embed template.tmpl
var defaultTemplate string
```

Provide an instantiated renderer:

```go
type Renderer struct { template *template.Template }

func NewRenderer(path string) (*Renderer, error)
func (r *Renderer) Execute(w io.Writer, data any) error
```

- `path == ""` uses the embedded template.
- Custom templates are read and parsed once, in `NewRenderer`.
- `Execute` does not mutate the renderer.
- Parse errors include the template path; execution errors include the current
  proto file or generation unit.
- Two generators built with different templates must not affect each other.
- Custom template capability is exposed only through `Config.TemplateFile`.

Template functions do presentation formatting only — no descriptor traversal,
config decisions, or business branching. Precompute complex data in Go.

**String safety:** any dynamic content entering a Go string literal must go
through `strconv.Quote` or an equivalent template function. Never hand-concatenate
quotes around user input, proto comments, paths, or option values.

## Generated Output

**Header.** Must state the generating plugin, "do not edit", the input proto
file, and the protoc/plugin version when available. Header text and blank lines
stay stable within a plugin. An AST rewriter preserves the original
`protoc-gen-go` header — it must not impersonate the original generator.

**Filename and package.** Output filename derives from the input file path plus a
fixed suffix, never from the working directory or an absolute path. Package uses
`file.GoPackageName`. One suffix rule per output kind (e.g. `.sphere.pb.go`).
Changing the naming rule is a compatibility change requiring separate review.

**Imports.** Use `protogen.GeneratedFile.QualifiedGoIdent`. Never hand-write an
import block or guess aliases. Import only for identifiers actually generated.
Prefer `new(T)`-style keep-alive expressions. Do not use blank identifiers to
paper over invalid imports unless the reference is itself part of the contracted
output.

**Order and formatting.** Preserve declaration order where the descriptor has
one. Sort map-derived output (`slices.Sorted(maps.Keys(m))`). Deduplicate
repeated lists deterministically. Let `protogen`/`gofmt` handle final formatting.
Never rely on trailing whitespace for layout. Handle newlines in comments so the
generated syntax stays valid.

**Change strategy.** Distinguish *semantic* changes (new methods, changed tags,
error codes, runtime behavior) from *presentational* ones (blank lines, comments,
variable names, keep-alive style). Both update golden files, but they should be
committed and reviewed separately. A feature change must not opportunistically
reformat all historical output; a large style-only update needs its scope and
no-semantic-change basis stated in the change description.

## AST Rewriters

Beyond the common rules, a rewriter such as `protoc-gen-sphere-binding` must:

- Return a file-contextual error on parse failure — never fall back to string replacement.
- Rewrite only the target struct fields/tags, preserving other declarations, comments, and the header.
- Be idempotent: a second run over already-rewritten input produces no further diff.
- Return input unchanged when there is no target field.
- Normalize, deduplicate, and snapshot alias config.
- Use accurate verbs in exported API names, e.g. `RetagAST`.
- Keep a `Deprecated:`-annotated compatibility wrapper when fixing old names, unless a breaking release is explicitly scheduled.

## Errors and Comments

Error text follows Go convention: lowercase start, no trailing period, `%q` for
external input, describes the failed action and object (`parse template %q: %w`),
avoids repeating words the caller already supplied, and never swallows the
underlying error.

Exported types, functions, methods, and constants need Go doc starting with the
name. One file per package carries a package comment. Explain *why*, not what the
next line does. Normalize proto comments before emitting them without changing
their meaning. Deprecation notices use the recognized `Deprecated:` paragraph and
name the replacement.

## Compatibility

These may break downstream code:

- Renaming exported `Config` fields
- Removing exported functions or constants
- Changing generated filenames
- Changing template data structures
- Changing flag names or defaults
- Changing generated interfaces, tags, error codes, or method signatures

Before making one: search the organization for call sites and custom templates;
decide whether a `Deprecated` alias or wrapper can be kept; add compatibility
tests for both old and new entrypoints; document the migration in release notes;
if compatibility is impossible, schedule an explicit breaking release.

Renaming purely internal unexported names needs no compatibility layer — but must
still not produce unrelated generated diffs.
