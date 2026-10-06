# Guardrails: Pitfalls and Legitimate Defense

Read this before editing any match from `patterns.md`. The first list is what goes wrong when a
cleanup is applied carelessly. The second list is code that looks redundant but must be left
alone.

## IV. Pitfall Checklist (read before editing)

- **T1** `atomic.Pointer[T].Store(nil)` is legal and does not panic; only `atomic.Value.Store(nil)` panics. A proof that "nil is unreachable" must include "no test deliberately calls `Store(nil)`" — a test may use it to simulate the pre-initialization state, and that fallback is pinned functionality.
- **T2** Grep `*_test.go` before deleting an unexported function. Tests commonly use small helpers in `defer` (`defer _ = f.Close()` is illegal). Referenced by a test = keep.
- **T3** Removing a `default` from a switch (with a closed enum fully covered) can fail to compile: if one enum value returns early before the switch, the compiler does not know that, and without the default it reports a missing return. Such an "unreachable default" is normal Go and is not over-defensiveness.
- **T4** `strings.Repeat(s, n)` panics on negative n, while `for range n` iterates zero times. Before rewriting a loop, check whether tests pin negative or zero bounds; use `max(n, 0)` to preserve semantics when needed.
- **T5** Behavior change is not only about the happy path: silently ignoring a nil option → panicking is a behavior change too. Tightening invalid-input handling is not authorized by "zero behavior change".
- **T6** An exported constructor's defensive copy may protect a legal special usage: when the functional Option is an exported type, users can write custom Options that store shared pointers, and the copy defends against post-call mutation. Do not delete it as over-defensiveness.
- **T7** Lazy-allocation rewrites must pass static analysis: nilaway-class tools are sensitive to "pass nil as an argument, then dereference it". Run the lint gate after the change, and adjust the shape if it fails (for example, keep a non-nil outer function).
- **T8** A comment left behind after deleting a check must say **why it is safe** (which lock order or unique construction site it depends on), not what was deleted.

## V. Legitimate-Defense Whitelist (never report these)

These patterns look excessive but carry real weight. Skip them entirely when scanning:

1. **Sharded lock arrays** (for example 128 mutexes selected by hash): usually required for the "at most one consumer" semantics of `GetDel`-style operations; a documented semantic in the interface docs is the evidence.
2. **recover wrapping a write**: it defends against a caller-supplied `Stringer`/`MarshalJSON`/`LogValuer` panicking — fmt evaluates lazily, so the recover must wrap the write, not the evaluation.
3. **Driver-behavior-driven retry/batching**: `ErrConflict` retry with `runtime.Gosched()`, `ErrTxnTooBig` batching, protocol-level short-circuits on empty input. A comment naming the driver and error code is the evidence.
4. **Zero-value re-checks at exported interface boundaries**: a middleware re-checking when `Claims.GetUID()` returns zero plus nil — third-party implementations are outside your control; this is defense in depth.
5. **Documented cloning**: `slices.Clone` of a roles slice, cloning the slice inside `WithShutdownSignals` — these prevent real aliasing bugs, and the comment usually names the sharing party.
6. **Fail closed**: a middleware returning true when the route cannot be determined (so auth/ratelimit still run) rather than false. "Silently skip" is the dangerous direction.
7. **Complex queues pinned by stall/concurrency tests**: a custom bounded queue replacing `io.Pipe` usually exists because the write path must never block on a slow consumer.
8. **Tool-driven explicit allocation**: a map allocated early with a comment saying "so nilaway can see the reachability" — a weighed trade-off is not a problem.
9. **The static-analysis gate itself**: nilaway's presence in the lint gate is what demands explicit nil handling; work with it rather than fighting it.

## Test-vetoed Findings: Two Worked Cases

A failing test means the claim was wrong. Roll back, record, move on. These two cases are the
ones that actually bite:

- `atomic.Pointer[T].Store(nil)` does **not** panic (only `atomic.Value` panics, and only on a nil interface). A seemingly unreachable nil fallback may be functionality pinned by a test that explicitly calls `Store(nil)` to simulate "use before initialization".
- An unexported helper may be referenced directly from `_test.go` — especially around `defer f.Close()`, because `defer _ = f.Close()` is not a legal statement and a tiny helper is the cleanest errcheck-safe spelling. Before deleting any unexported identifier, your grep must include test files.
