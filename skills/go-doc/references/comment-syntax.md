# Go Doc Comment Syntax

Use this reference when writing comments. The formatting described here targets Go 1.19+.
For older supported versions, check the toolchain's output before using newer syntax.

## Placement and opening sentences

Attach the comment directly to its package, type, function, constant, or variable declaration.
Do not leave an empty source line between the comment and declaration.
Use `//` for ordinary doc comments. Separate paragraphs with an empty `//` line.

Begin package comments with `Package <name> ...` and symbol comments with the symbol name.
Put the package overview in one file; multiple package comments are combined.
`doc.go` is a convention, not a special documentation format.

## Supported structure

| Need | Go comment syntax | Common mistake |
|---|---|---|
| Paragraph | Unindented prose, separated by an empty comment line | Indenting prose turns it into preformatted text |
| Heading | `// # Usage` with blank comment lines around it | Using Markdown heading levels or omitting the space after # |
| Symbol link | `[NewClient]`, `[Client.Get]`, `[io.Reader]` | Linking an identifier that does not exist |
| External link | `[Guide]` plus `[Guide]: https://example.com/guide` in the same comment | Using inline Markdown `[Guide](url)` |
| Bullet list | Indent the markers: `//   - Item` | Unindented lists may become prose |
| Numbered list | Indent the markers: `//  1. Item` | Expecting automatic renumbering |
| Code block | Blank comment line, then code indented after `//` | Triple-backtick fences or unindented braces |
| Deprecation | A paragraph starting `Deprecated: ` with a replacement | Treating it as a heading |

Lists contain prose only; place code blocks outside lists. Avoid nested lists.
Do not rely on bold, italics, inline-code backticks, tables, images, or raw HTML rendering.
Write identifier names plainly in prose; use brackets for actual documentation links.
Use a single heading level. Run gofmt and inspect the result instead of manually maintaining spacing.

Symbol links use current-package names or package-qualified names. Cross-package shorthand
requires a resolvable import name; a full import path avoids ambiguity. In a `doc.go` file,
use `[context.Context]` or `[encoding/json.Decoder]` without adding unused imports just for links.
Each comment has its own external-link definitions. Definitions in the package comment do
not supply links for a method comment.

## Package overview with a visible recipe

This is a complete illustrative `doc.go` for a fictional `example.com/demo/greeting` module.
Adapt names, imports, and claims to the target package's real behavior.

```go
// Package greeting formats greeting messages.
//
// Use [Hello] when the caller already has a display name.
//
// # Usage
//
//	import (
//		"fmt"
//		"example.com/demo/greeting"
//	)
//
//	fmt.Println(greeting.Hello("Ada"))
//	// Prints: Hello, Ada!
//
// # Input rules
//
//   - An empty name produces "Hello, stranger!".
//   - Names are preserved without trimming whitespace.
//
// Hello has no shared mutable state and is safe for concurrent use.
package greeting
```

The import block and call form a usage fragment, not a complete Go source file.
Verify it in an Example or temporary consumer program before publishing it.

## Symbol comments queried alone

Do not make a symbol's contract depend on reading the package introduction first.
For this fictional API, the function comment would be:

```go
// Hello returns "Hello, " followed by name and an exclamation mark.
// If name is empty, Hello returns "Hello, stranger!".
// Hello preserves whitespace and is safe for concurrent use.
func Hello(name string) string {
	if name == "" {
		return "Hello, stranger!"
	}
	return "Hello, " + name + "!"
}
```

For fallible APIs, explain how the caller distinguishes errors and whether partial results
remain usable. For resource APIs, name the caller responsible for cleanup. Add a short
symbol-level recipe when ordering or error handling is easy to misuse.

## Tool visibility

| Consumer tool | What the author must supply |
|---|---|
| `go doc <import-path>` | Package comment containing the basic recipe and entry points |
| `go doc <import-path> <Symbol>` | Symbol comment containing the local contract |
| `go doc -all <import-path>` | Package and exported-symbol comments; this does not include Example bodies |
| pkg.go.dev / pkgsite | The same comments plus associated Example functions |
| Source-reading agent | The comments plus `example_test.go`; no need for a separate guide for basic use |

## Sources

- [Go Doc Comments](https://go.dev/doc/comment): syntax, links, placement, and formatting.
- [go doc command](https://pkg.go.dev/cmd/doc): command arguments and `-all` behavior.
