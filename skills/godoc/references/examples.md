# Examples That Teach and Stay Valid

Use this reference when adding recipes or Example functions.

## Two complementary surfaces

Put a small indented recipe in the package or symbol comment so CLI `go doc` exposes it.
Keep a corresponding compiled example in `example_test.go` for workflows worth preserving.
`go doc` does not print Example bodies. pkg.go.dev and pkgsite associate them with their target.
Do not promise that adding example tests alone makes code visible through CLI documentation.

Prefer `package <name>_test` to verify the exported API from a consumer's perspective.
Follow existing repository conventions when they require another test layout.
Use the target module's actual import path, including a major-version suffix when present.

## Naming

| Target | Example name |
|---|---|
| Package | `Example` |
| Function F | `ExampleF` |
| Type T | `ExampleT` |
| Method M on T | `ExampleT_M` |
| Additional scenario | `ExampleF_emptyInput` or `ExampleT_M_notFound` |

Suffixes after an underscore must start with a lowercase letter.
Example functions take no parameters and return no values.
Reference existing exported symbols; otherwise go test may reject the association.

## Complete external-package example

This file pairs with the fictional greeting API in the syntax reference.
It assumes the module path is `example.com/demo/greeting`.

```go
package greeting_test

import (
	"fmt"

	"example.com/demo/greeting"
)

func ExampleHello() {
	fmt.Println(greeting.Hello("Ada"))
	// Output: Hello, Ada!
}

func ExampleHello_emptyName() {
	fmt.Println(greeting.Hello(""))
	// Output: Hello, stranger!
}
```

`// Output:` makes go test run the example and compare stdout with the expected text.
Use `// Unordered output:` only when the API intentionally leaves line order unspecified.
Without an output comment, an example compiles but does not run. Use that form when an
external service prevents deterministic execution; report that the workflow was not exercised.

## Choose useful scenarios

| API characteristic | Example that helps a consumer decide what to write |
|---|---|
| Constructor plus methods | Minimal initialization, one operation, and required cleanup |
| Sentinel error | Show the real `errors.Is` branch and normal success handling |
| Optional/missing result | Show how absence differs from an operational failure |
| Context or long-running task | Show cancellation and the documented start/stop ordering |
| Generic API | Show concrete type arguments and input/output types |
| Multiple drivers | Use a simple local driver; show service-backed setup only when requested |

Add only scenarios that explain distinct caller decisions. Avoid one example per trivial getter.
Handle errors before using results. Do not ignore errors just to shorten the recipe.
Do not add sleep-based timing, external credentials, fixed ports, or unbounded background work.
Use temporary resources and deterministic values when they fit the real API.
Do not claim nil, concurrency, retry, or cleanup guarantees merely because the example needs them.

## Validation

From the target module, run commands with real package and symbol names:

```sh
go doc example.com/demo/greeting
go doc example.com/demo/greeting Hello
go doc -all example.com/demo/greeting
go test -run '^Example' ./path/to/package
go test ./path/to/package/...
```

Check the rendered CLI output, not only raw comments: headings, code indentation, and entry
points must survive formatting. Inspect linked symbol targets in source or rendered HTML;
successful compilation alone does not prove that documentation links resolve.

Comment code is not compiled by Go. Match each important comment recipe against its tested
Example. If they differ materially, compile-check the exact recipe in a temporary consumer
program against the local module. Use a temporary directory outside the repository; do not
introduce a nested module or alter the target module's dependencies for this check.

Run the repository's broader checks when required. Report compilation-only examples and
environmental blockers accurately. Do not weaken output checks to conceal a broken recipe.

## Source

- [testing examples](https://pkg.go.dev/testing#hdr-Examples): association names, output matching, and compilation-only behavior.
