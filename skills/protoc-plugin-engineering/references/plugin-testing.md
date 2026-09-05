# Plugin Testing

Three layers, each catching what the others cannot.

```
+------------------------------------------+
| Layer 3: Golden file regression tests    |
| - Prevent unexpected generated changes   |
| - Compare complete output                |
| - Update only with -update-golden        |
+------------------------------------------+
| Layer 2: Functional integration tests    |
| - Precompiled .pb descriptor sets        |
| - Full proto syntax and extensions       |
| - Verify generated code structure        |
+------------------------------------------+
| Layer 1: Unit tests                      |
| - Hand-written descriptors               |
| - Fast edge cases, no file dependencies  |
| - Errors, empty values, skip logic       |
+------------------------------------------+
```

## Directory Layout

```
protoc-gen-*/
|-- generate/
|   `-- <plugin-name>/
|       |-- <plugin-name>.go
|       |-- <plugin-name>_test.go     # Layer 1
|       |-- golden_test.go            # Layer 3
|       `-- testdata/
|           |-- buf.yaml              # buf module + fixture deps
|           |-- buf.lock              # pinned deps (buf dep update)
|           |-- proto/                # test .proto sources
|           |-- pb/                   # descriptor sets built by buf
|           `-- golden/               # expected output
|-- Makefile
`-- go.mod
```

## Required Coverage

### Config tests
- Defaults equal the real CLI defaults
- `DefaultConfig()` returns independent objects
- nil, empty, malformed, and mutually exclusive config
- GoIdent legal/illegal boundaries
- Map-derived error ordering is stable
- Mutating the source config after `NewGenerator` does not change behavior

### Generation tests
- Minimal valid descriptor
- Empty service, empty enum, no target option
- Streaming, repeated types, cross-package references
- Non-applicable files produce no output
- One generator processing several files does not leak state
- The same input run repeatedly yields identical output

### Template tests
- Embedded default parses and executes
- Custom template file works
- Missing or malformed template gives a diagnosable error
- Two generators with different templates stay isolated
- Special characters entering Go strings still compile

### Golden tests
- Fixture `CompilerVersion` is pinned so the host protoc version cannot pollute headers
- `.proto`, precompiled descriptors, and golden output are maintained together
- Tests compare by default; only an explicit `-update-golden` writes
- Every golden diff is reviewed by a human — a passing test is not proof the output is correct
- Generated `.go` is syntax-parsed; key fixtures are compiled

### CLI tests
- Flag defaults and custom values
- Missing required parameters
- `--version`
- Config errors surface from `run`
- proto3 optional is supported
- The CLI initializes the generator only once across multiple files

### AST rewriter tests
- No target tag → bytes or semantics unchanged
- Rerunning on rewritten input produces no diff
- Comments, header, and non-target fields preserved
- Invalid Go input returns a parse error
- Mutating the alias slice after construction does not affect the generator

## Pitfalls

These bite almost every protoc-plugin suite.

1. **`plugin.Files[0]` is usually a dependency.** `protogen.Plugin.Files` holds
   *every* file in the request — including `google/protobuf/descriptor.proto` and
   imported extension protos — ordered dependencies-first. Only files in
   `FileToGenerate` have `Generate == true`. Select by the `Generate` flag, never
   by index.

2. **The descriptor set must bundle imports, and you must pass all of it.**
   Custom options live in an imported `.proto`. `buf build` bundles dependencies
   by default; feed the **entire** `set.File` slice to your `ProtoFile` helper.
   Passing a single descriptor makes `protogen.Options{}.New` fail to resolve
   imports.

3. **`GeneratedFile.Content()` returns `([]byte, error)`.** It runs gofmt and
   synthesizes the import block, so it can fail on malformed output. Check the
   error — `string(genFile.Content())` does not compile.

4. **Extension references use the proto package, not the Go path.** With
   `package sphere.errors;` the option is `(sphere.errors.default_status)`, while
   the `import` path is relative to the buf module root
   (`sphere/errors/errors.proto`).

5. **Pin `CompilerVersion` for stable golden headers.** Set a fixed
   `pluginpb.Version` in the request; an unset version renders as `(unknown)` and
   golden files churn with the host toolchain.

6. **Commit the fixtures.** `.pb` descriptor sets, golden files, and `buf.lock`
   must be checked in so `go test ./...` runs without `buf` installed. Only
   `make testdata` / `make update-golden` need `buf`. Confirm `.gitignore` does
   not exclude them.

7. **Keep source info so comments survive.** If the plugin emits anything derived
   from proto comments — Go doc, Swagger `@Description` — the descriptor set needs
   `source_code_info`. `buf build` keeps it unless `--exclude-source-info`; raw
   `protoc` needs `--include_source_info` explicitly, or golden output silently
   loses every comment.

8. **Build a fully-populated `Config`, not a bare struct literal.** Generated
   output references router/context/handler and response types from `Config`'s
   `protogen.GoIdent` fields. A bare `&http.Config{Omitempty: true}` leaves them
   empty and produces non-representative golden files:

   ```go
   cfg := http.DefaultConfig()
   cfg.Omitempty = false
   genFile, err := http.GenerateFile(plugin, file, cfg)
   ```

## Fixture and Golden Workflow

- Fixture compilation lives behind a Make target (`make testdata`), resolving deps
  from `testdata/buf.lock`.
- Scope `-update-golden` to the package that declares the flag; passing it to
  `./...` fails test binaries that do not declare it.
- After updating golden files, rerun the full test suite.
- Suggested Make targets: `test`, `test-race`, `lint`, `update-golden`,
  `generate`, `check`.

## Cross-Project Reuse

`generate/internal/testutil` should carry the same implementation in all four
plugins — descriptor-set loading, request construction with a pinned compiler
version, target-file selection by `Generate`, and content extraction with error
checking. Diverging copies are how these pitfalls creep back in.
