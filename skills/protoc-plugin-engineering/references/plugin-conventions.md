# Plugin Conventions

Normative words: **must** (new and refactored code satisfies it), **should**
(default; deviation needs a stated reason), **may** (per-plugin choice).

## Standard Directory

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

## Command-Line Entrypoint

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
| `new_errors_func` | `NewErrorFunc` |

Initialisms stay uppercase: `JSON`, `HTTP`, `URI`, `URL`, `API`, `ID`. Never
`Json`, `Http`, `Id`.

### Errors and Exit

- `run()` returns an error; `main()` prints it and exits non-zero.
- No `log.Fatal`, `os.Exit`, or `panic` in testable functions.
- Flag errors name the parameter and the offending value.
- Fixed errors use `errors.New`; contextual errors use `fmt.Errorf` with `%w`.

## Config Model

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

## Generator Contract

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

Template rules, generated-output determinism, AST rewriters, error reporting, and compatibility
live in `plugin-output-rules.md`.
