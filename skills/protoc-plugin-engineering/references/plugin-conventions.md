# Plugin Conventions

Normative words: **must** (new and refactored code satisfies it), **should**
(default; deviation needs a stated reason), **may** (per-plugin choice).

## 1. Standard Directory

```text
protoc-gen-<name>/
├── main.go
├── main_test.go
├── Makefile
├── go.mod
└── generate/
    ├── internal/
    │   ├── template/
    │   │   ├── template.go
    │   │   ├── template.tmpl
    │   │   └── template_test.go
    │   └── testutil/
    │       └── testutil.go
    └── <domain>/
        ├── config.go
        ├── config_test.go
        ├── generate.go
        ├── generate_test.go
        ├── imports.go
        ├── <domain>.go
        ├── golden_test.go
        └── testdata/
            ├── proto/
            ├── pb/
            └── golden/
```

- `main.go`: protoc protocol adaptation, flag parsing, object assembly — nothing else.
- `config.go`: config type, defaults, parsing, validation.
- `generate.go`: `Generator`, constructor, file-level generation flow.
- `imports.go`: only when import planning is genuinely complex.
- `<domain>.go`: split by domain concept — service, enum, method, field.
- `format.go`: pure string formatting, kept out of the generation flow.
- `generate/internal/template`: private to the module.
- `generate/internal/testutil`: **should be the same implementation across all four plugins.**
- AST rewriters with no text template may omit `template/`.

Do not create `utils.go`, `common.go`, or `helper.go`. Do not split small files
just to match the diagram — split when a file carries more than one primary
responsibility.

## 2. Command-Line Entrypoint

`main.go` should contain only:

- `const version = "..."`
- `extractConfig(flags *flag.FlagSet) (*Config, error)`
- `run() error`
- `main()`

Standard flow:

1. Register flags using `DefaultConfig()` results as defaults.
2. Parse and validate config.
3. Create the `Generator` **once**.
4. Process the request through `protogen.Options.Run`.
5. Declare `plugin.SupportedFeatures = uint64(pluginpb.CodeGeneratorResponse_FEATURE_PROTO3_OPTIONAL)`.
6. Iterate only files with `file.Generate == true`.
7. Return errors to protoc; never exit the process from domain code.

Never re-parse templates or build an equivalent generator inside the file loop.
Never implement service/enum/tag logic in `main.go`.

### Naming

CLI flags use `snake_case`; Go identifiers use Go conventions:

| CLI | Go |
|-----|-----|
| `omit_empty` | `OmitEmpty` |
| `auto_remove_json` | `AutoRemoveJSON` |
| `template_file` | `TemplateFile` |
| `new_error_func` | `NewErrorFunc` |

Initialisms stay uppercase: `JSON`, `HTTP`, `URI`, `URL`, `API`, `ID`. Never
`Json`, `Http`, `Id`.

### Errors and Exit

- `run()` returns an error; `main()` prints it and exits non-zero.
- No `log.Fatal`, `os.Exit`, or `panic` in testable functions.
- Flag errors name the parameter and the offending value.
- Fixed errors use `errors.New`; contextual errors use `fmt.Errorf` with `%w`.

## 3. Config Model

Every domain package must expose:

```go
type Config struct {
    TemplateFile string
}

func DefaultConfig() *Config
func (c *Config) Validate() error
```

**Defaults**
- `DefaultConfig()` must return the plugin's real CLI defaults.
- No test fixtures, personal paths, or one project's example values.
- Constants defined once — not duplicated across flags, tests, and generator.
- Required fields stay at zero value and fail in `Validate`; do not fabricate a
  plausible-looking default.
- Each call returns an independent object.

**Validate**
- Nil-receiver safe — return a clear error, never panic.
- Depends only on the config; reads and mutates no global state.
- Checks empty strings, format, mutual exclusion, and supported ranges.
- Sorts multiple map-derived errors so the message is stable.
- Runs before any proto file is read or output produced.

Go identifier config uses `import/path;Ident`. Parse with `strings.Cut` and
reject: missing separator, empty import path, empty identifier, extra `;`, and
paths or names outside the plugin's constraints.

**Ownership.** `NewGenerator(cfg)` stores a snapshot. Values copy directly;
slices, maps, and pointers must be deep-copied into generator-private state, so
that neither of these changes an existing generator's behavior:

```go
generator, _ := NewGenerator(cfg)
cfg.TemplateFile = "another.tmpl"
cfg.Aliases[0] = "changed"
```

## 4. Generator Contract

```go
type Generator struct { /* validated, immutable dependencies */ }

func NewGenerator(cfg *Config) (*Generator, error)

func (g *Generator) GenerateFile(plugin *protogen.Plugin, file *protogen.File) (*protogen.GeneratedFile, error)

func GenerateFile(plugin *protogen.Plugin, file *protogen.File, cfg *Config) (*protogen.GeneratedFile, error)
```

The package-level `GenerateFile` is a convenience entry for tests and external
callers. The CLI must call `NewGenerator` once and reuse its method.

`NewGenerator` must reject nil config, call `Validate`, copy the config, parse
the template once, and stay read-only afterwards so it can process many files
safely.

`GenerateFile` must not mutate generator config, must not retain per-file state,
should collect current-file data in a local `fileConfig` or equivalent, must
handle only descriptors relevant to this plugin, and must add proto file /
service / method / enum context to its errors.

### No-Output Semantics

A new-file generator must return `(nil, nil)` for a non-applicable file — no
services, no target enums, no matching extension options. **Never emit a
header-only empty file.**

An in-place rewriter may use a return shape that fits its AST flow, but
"nothing to rewrite" is still a normal result, never an error.

### Local Naming

`plugin`, `file`, `generatedFile` or `g`, `cfg`, `fileCfg`, `service`, `method`,
`enum`, `field`. No `gErr`, `gSvc`, `obj`, `data1`. Within one scope, `g` must
not mean both the generator and the generated file.

## 5. Templates

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

## 6. Generated Output

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

## 7. AST Rewriters

Beyond the common rules, a rewriter such as `protoc-gen-sphere-binding` must:

- Return a file-contextual error on parse failure — never fall back to string replacement.
- Rewrite only the target struct fields/tags, preserving other declarations, comments, and the header.
- Be idempotent: a second run over already-rewritten input produces no further diff.
- Return input unchanged when there is no target field.
- Normalize, deduplicate, and snapshot alias config.
- Use accurate verbs in exported API names, e.g. `RetagAST`.
- Keep a `Deprecated:`-annotated compatibility wrapper when fixing old names, unless a breaking release is explicitly scheduled.

## 8. Errors and Comments

Error text follows Go convention: lowercase start, no trailing period, `%q` for
external input, describes the failed action and object (`parse template %q: %w`),
avoids repeating words the caller already supplied, and never swallows the
underlying error.

Exported types, functions, methods, and constants need Go doc starting with the
name. One file per package carries a package comment. Explain *why*, not what the
next line does. Normalize proto comments before emitting them without changing
their meaning. Deprecation notices use the recognized `Deprecated:` paragraph and
name the replacement.

## 9. Compatibility

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
