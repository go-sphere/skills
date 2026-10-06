# Detection Pattern Catalog

Read this file in full before scanning. Each pattern comes with a minimal code shape; **the shape looking similar does not make the code excess — verify the surrounding code before reporting.**

## I. Over-design

### D1. Injection points nobody can inject

A function field in an options struct that no Option ever sets — dead configuration surface.

```go
type options struct {
    uploadSuccessWithData func(ctx C, key, url string) error // no Option sets this
    ...
}
newOptions := &options{uploadSuccessWithData: defaultUploadSuccessWithData}
```

Fix: delete the field and call the default implementation directly at the call site (keep the default itself; it usually carries a valuable comment).
Verify: grep every Option constructor to confirm there is no assignment path.

### D2. Empty shells reserved for the future

A file whose entire content is a package comment saying "XX adapters can be added here later". YAGNI. Before deleting the file, confirm the other files in the package carry their own package documentation (two package comments would be redundant; usually only one is real).

### D3. Sentinels equivalent to the zero value

The sentinel simulates exactly what the zero value already does; two places maintain the same "none".

```go
cfg := &config{allowOrigins: []string{""}}        // at construction
if len(c.allowOrigins) == 0 {                      // and again at use
    c.allowOrigins = []string{""}
}
// while originMatches already returns false for allowed == "" — a nil slice behaves identically
```

Fix: delete the sentinel and the backfill logic. Verify: walk every branch the sentinel flows through and prove the empty-value path produces the same output.

### D4. Default identity closure plus a nil check — belt and braces

```go
transform: func(text string) (string, error) { return text, nil }, // default
...
if transform != nil { ... }   // consumer
```

Two guards covering one thing, and every request pays a closure call for nothing. Fix: delete the default closure and keep the nil check (nil becomes the single default state).

### D5. Wrapper functions with zero purpose

```go
func ignoreCloseError(closer func() error) { _ = closer() }
```

Do not delete it yet — see pitfall T2; it may be load-bearing in defer scenarios. Inline it as `_ = x()` only once every call site is a direct, non-defer call.

### D6. Immediately-invoked closure to build a map

```go
return n.cache.MultiSet(ctx, func() map[string]S {
    mapped := make(map[string]S, len(valMap))
    ...
    return mapped
}())
```

A plain loop with a local variable is enough; the closure is noise. When changing it, match the style of the sibling methods in the same file.

### D7. Redundant interface layering

```go
type integerish interface { ~int | ... | ~string }
type UID interface { integerish }   // adds no further constraint, pure forwarding
```

Merge it into the consuming interface; the type set is unchanged. Only merge the unexported layer.

### D8. Explicit zero values in constructors

```go
defaults := &options{hasTTL: false, singleflight: nil}  // noise
```

Delete the zero-valued fields and keep the non-zero defaults (`expiration: -1` and the like).

### D9. Double nil check plus type assertion

```go
if v := ctx.Value(k); v != nil {
    if m, ok := v.(map[string]any); ok {   // asserting on a nil interface already yields ok=false
```

Collapse into a single assertion.

## II. Over-optimization

### O1. Eagerly allocated traversal state

```go
formattable(reflect.ValueOf(v), 0, make(map[containerKey]struct{}))
```

The map used for recursion/cycle detection is allocated before anyone knows whether the value is even a container — scalars dominate the hot path and pay for it every time.
Fix (all three elements of lazy allocation are required):

```go
formattable(rv, 0, nil)
// inside the container branch:
if _, ok := seen[key]; ok { return false }   // reading a nil map is legal; check first
if seen == nil { seen = make(...) }          // allocate only on the first container
seen[key] = struct{}{}
defer delete(seen, key)                      // defer arguments evaluate when the statement executes = the map after allocation
```

Note: the recursive call must receive the reassigned local variable.

### O2. Misplaced capacity hint

```go
out := make([]rune, 0, len(runs))   // but the number actually appended is decided by outLength
```

The capacity keys off the wrong length. Either fix it, or delete the hand-written loop entirely with a library call such as `strings.Repeat`.

### O3. Reuse tricks on cold paths

`numbers = numbers[:0]` in a background sweep that runs once a minute saves one allocation — nanoseconds saved against readability lost. Allocate fresh each time instead. (Confirm it really is a cold path first.)

### O4. Resources allocated for a disabled feature

```go
quit := make(chan os.Signal, 1)
if len(options.signals) > 0 { signal.Notify(...) }   // the channel is wasted when signals is empty
```

Move the allocation inside the conditional branch. A nil channel blocks forever in `select` — which is exactly the disabled semantics.

## III. Over-defensive coding

### V1. Nil checks under a paired-lock protocol

```go
case groupStateRunning:
    if stopReqCh != nil { select { case stopReqCh <- ... } }   // dead check
```

How to verify: the channel/pointer and the state field are created and nil'd as a pair **under the same mutex** (`beginLifecycle` creates it and sets Running; `finishLifecycle` nils it and sets Stopped), and the reading site takes both the state and the channel under that same lock — so the state proves the channel non-nil. After deleting the check, leave a one-line invariant comment at the site (naming the lock order the non-nil guarantee depends on), because the code itself cannot express that constraint.

### V2. Bounds checks on a range index

```go
if result.idx >= 0 && result.idx < len(finished) { finished[result.idx] = true }
```

`idx` can only come from `for i := range stage`, and `len(finished) == len(stage)` — assign directly.

### V3. Nil ctx guaranteed by the constructor

Every call site passes the result of `context.WithCancel/WithTimeout/Background`, so `ctx != nil` is a tautology. Grep the call sites to confirm.

### V4. Logically unreachable early return

```go
if err != nil {
    handler(err)
    return        // dead return: last statement of the function
}
```

Collapse into the `if _, err := fn(); err != nil { handler(err) }` style.

### V5. Re-validation of an already-normalized value

After `NormalizeKey(key)` at the entry point, a deep path runs `NormalizeKey`/`Clean` again. When the upstream is `path.Join` (which Cleans by itself) or the entry point already validated, the repeat is pure overhead. **This pattern carries a higher false-positive risk**: delete only when the upstream guarantee is documented or obvious; defense at a boundary (the first stop for external input) always stays.

### V6. Three-line error passthrough

```go
err = m.sender.SendCode(number, code)
if err != nil { return err }
return nil
```

→ `return m.sender.SendCode(number, code)`.

Before editing anything you matched here, read `review-guardrails.md`: the pitfall checklist
and the legitimate-defense whitelist decide whether a match is actually reportable.
