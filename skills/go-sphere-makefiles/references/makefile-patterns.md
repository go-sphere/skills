# Go-Sphere Makefile Patterns

Use these as starting points, then retain the repository's required tools and specialized targets.

## Single Module

```make
GO ?= go
GOLANGCI_LINT ?= golangci-lint

DIRECT_DEPS_TEMPLATE := {{if and (not .Main) (not .Indirect) (not .Replace)}}{{.Path}}{{end}}

.DEFAULT_GOAL := check

.PHONY: deps-update tidy fmt test lint check

deps-update:
	@deps="$$(GOWORK=off $(GO) list -m -f '$(DIRECT_DEPS_TEMPLATE)' all)"; \
	if [ -n "$$deps" ]; then GOWORK=off $(GO) get -u $$deps; fi
	GOWORK=off $(GO) mod tidy

tidy:
	GOWORK=off $(GO) mod tidy

fmt:
	$(GO) fmt ./...
	$(GOLANGCI_LINT) fmt --no-config --enable gofmt --enable goimports

test:
	$(GO) test ./...

lint:
	$(GOLANGCI_LINT) fmt --no-config --enable gofmt --enable goimports --diff
	$(GO) vet ./...
	$(GOLANGCI_LINT) run --no-config

check:
	GOWORK=off $(GO) mod tidy -diff
	$(MAKE) lint
	$(MAKE) test
```

Add `buf format -w` to `fmt` and `buf lint` to `lint` only when the repository owns Protobuf sources. Add NilAway only where it is an established analyzer and preserve any justified package exclusions.

## Multiple Modules

List modules explicitly and keep each command scoped to its module:

```make
GO_MOD_DIRS := . adapter-a adapter-b conformance

deps-update:
	@set -eu; \
	for dir in $(GO_MOD_DIRS); do \
		echo "==> updating $$dir"; \
		( cd "$$dir"; \
		  deps="$$(GOWORK=off $(GO) list -m -f '$(DIRECT_DEPS_TEMPLATE)' all)"; \
		  if [ -n "$$deps" ]; then GOWORK=off $(GO) get -u $$deps; fi; \
		  GOWORK=off $(GO) mod tidy ); \
	done

test:
	@set -eu; \
	for dir in $(GO_MOD_DIRS); do \
		echo "==> testing $$dir"; \
		( cd "$$dir" && $(GO) test ./... ); \
	done
```

Use the same loop shape for `tidy`, `fmt`, `lint`, and tidy-diff verification. A subshell prevents one iteration's `cd` from leaking into the next. Keep a separate `GO_PACKAGE_DIRS` or verification list when not every module has the same role.

If local tests require cross-module replacements, export an existing repository `go.work` for test commands, while leaving dependency operations on `GOWORK=off`.

## Root Batch Dispatcher

The root contract is deliberately narrower than any individual repository:

```make
REPOS ?= \
	repo-a \
	repo-b

COMMON_TARGETS := deps-update tidy fmt test lint check

.DEFAULT_GOAL := help

.PHONY: $(COMMON_TARGETS) help

$(COMMON_TARGETS):
	@set -eu; \
	for repo in $(REPOS); do \
		test -f "$$repo/Makefile" || { echo "missing $$repo/Makefile"; exit 1; }; \
		printf '\n==> %s: %s\n' "$$repo" "$@"; \
		$(MAKE) --no-print-directory -C "$$repo" "$@"; \
	done
```

Keep the list curated so a new repository is an intentional addition. Support focused execution through `make check REPOS="repo-a repo-b"`.

For a bulk Go version editor, require a value matching `major.minor` or `major.minor.patch`, scan only `go.mod` and `go.work`, exclude vendor paths, and use `go mod edit -go` or `go work edit -go` instead of text replacement.

## Specialized Targets

Use these relationships only when they describe the repository:

```make
# Binary or command repository.
build:
	$(GO) build ./...

# Extra gates beyond the ordinary check.
verify: check api-compat

# Generator whose tests consume generated fixture descriptors.
test: testdata
	$(GO) test ./...

# Layout clean-checkout bootstrap.
init:
	$(GO) mod download
	$(MAKE) install
	$(MAKE) gen/all
	buf dep update
	$(GO) mod tidy
	$(MAKE) gen/conf
```

Do not copy a specialized target into other repositories solely for symmetry.

## CI Patterns

The Makefile remains the command contract; workflow YAML only supplies the environment and selects targets.

```yaml
- uses: actions/setup-go@v7
  with:
    go-version-file: go.mod
    cache-dependency-path: "**/go.sum"
- name: Test
  run: make test
```

For a binary, add an explicit `make build` step. For layouts, use:

```yaml
- name: Generate
  run: make init
- name: Build
  run: make build
- name: Test
  run: make test
```

For a multi-module repository, point `go-version-file` at a module with the highest Go requirement. When only installing a newer CI tool needs toolchain switching:

```yaml
- name: Install fixture tools
  env:
    GOTOOLCHAIN: auto
  run: go install example.com/tool/cmd/tool@v1.2.3
```

Keep that environment override step-scoped so the actual repository continues to test against its declared Go version.
