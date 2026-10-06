# Plugin Review Checklist

Walk every box before approving or delivering a plugin change. A failed box is a blocking
finding, not a nit.

**Structure**
- [ ] `main.go` only adapts the protoc protocol and assembles objects
- [ ] `Config`, `Generator`, template, and domain logic have clear boundaries
- [ ] Files named by responsibility; no mixed `utils.go` / `common.go` / `helper.go`
- [ ] Deviations in special plugins have a stated justification

**Config and state**
- [ ] `DefaultConfig()` equals the real CLI defaults and returns independent objects
- [ ] `Validate` is nil-safe and its error text is order-stable
- [ ] Generator deep-copies reference-typed config
- [ ] No mutable package-level templates or cross-file state
- [ ] A custom template affects only its own instance

**Output**
- [ ] Non-applicable files produce no output — never a header-only shell
- [ ] Filename, header, package, and imports are stable
- [ ] Map-derived output is sorted; repeated lists deduped and ordered
- [ ] Dynamic strings pass through `strconv.Quote`
- [ ] The generated diff contains only what this change requires
- [ ] AST rewrites are idempotent and preserve non-target content

**Compatibility**
- [ ] Changes to exported API, flags, defaults, or template data are identified
- [ ] Compatible old APIs keep a `Deprecated:` wrapper
- [ ] Breaking changes have migration notes and a release plan

**Verification**
- [ ] Unit, descriptor, golden, and CLI tests cover this change
- [ ] Golden diffs were reviewed by a human, not just made green
- [ ] `go test -race`, `go vet`, lint, and nilaway pass
- [ ] Module verifies independently under `GOWORK=off`

