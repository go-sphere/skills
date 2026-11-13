# Audit Playbook

What to look for, per category. Each subagent (or direct audit pass) gets its category section plus **Finding format**. Adapt depth to repository size: a 2K-line CLI gets a lighter pass than a 500K-line monorepo.

A finding is only a finding with evidence. "Probably has N+1 queries somewhere" is not a finding. `orders/api.ts:142 issues one query per order item inside a loop` is.

Audit hand-written code only. Generated and vendored files are on the recon skip list; a defect there belongs to the generator or schema that produced it. Ecosystem notes: for Go and go-sphere, read `go-ecosystem.md`.

---

## 1. Correctness / Bugs

The highest-trust category: real bugs found by reading, not speculation.

- Error handling: swallowed or log-only errors on critical paths, ignored return values that carry errors, missing error states in UI code.
- Async and concurrency hazards: unawaited promises, unjoined threads or goroutines, races on shared state, missing cancellation or cleanup (listeners never removed, stale closures in effects).
- Null flows: forced unwraps (`!`, `unwrap()`, unchecked type assertions), optional chaining that hides a value which must exist, unchecked indexing.
- Boundary conditions: off-by-one, empty collections, timezone and locale assumptions, integer overflow in counters and IDs.
- State machines: impossible states representable in the types; status enums with unhandled branches (a `default:` that silently does nothing).
- Data integrity: check-then-act on shared resources, missing transactions around multi-write operations, retried operations (webhooks, queues) that are not idempotent.
- Type-system escape hatches: `any`, unchecked casts, `@ts-ignore`, `unsafe`, `interface{}` clusters. Each one is a place the compiler was overruled.
- Resource leaks: unclosed handles, connections, and subscriptions; missing `finally`, `defer`, or `using`.

## 2. Security

Review only what is directly supported by code evidence. Frame findings as defensive maintenance: name the code pattern, the production impact, and the remediation. Keep plans at the level of code changes, configuration changes, and tests. Do not include runnable demonstration strings or step-by-step misuse details.

**Handling rule:** never copy a secret value into a finding or plan, because those files get committed. Give the `file:line` and the credential type ("Stripe live key at `config.ts:12`"). The fix sketch always includes rotation, because a committed secret is burned even after deletion.

**By-design is not a finding.** Standard platform conventions are intentional: honoring `https_proxy` and `NO_PROXY`, reading `~/.netrc`, a local dev tool shelling out to configured package managers. A tradeoff recorded in an ADR or decision doc is settled. Report these only when the implementation adds risk beyond the convention or the decision. A **stale ADR is itself a finding**: when the code has drifted from what the decision doc says, report the drift, because either the doc or the code is wrong. Never use the doc to suppress it.

- Credential hygiene: hardcoded keys, tokens, or passwords; credentials in committed `.env` files; credentials logged or stored in event or history tables. Remediation: remove, rotate, and move to a safer configuration path.
- Data crossing into interpreters or privileged APIs: SQL or shell commands assembled from request data (SQL and command injection), HTML sinks fed by user content (XSS), dynamic execution of runtime input, filesystem paths derived from request data (path traversal). Describe the safer API or validation boundary.
- Access control: endpoints or server actions without a server-side identity check, authorization enforced only in the client, object access by ID without an ownership or tenant check (IDOR), state-changing routes without request authenticity checks (CSRF).
- Input contracts: request bodies trusted without schema validation, file uploads without type, size, and storage limits, broad assignment from request data into persistence models (mass assignment).
- Dependency posture: run the ecosystem's audit command (`npm audit`, `pip-audit`, `cargo audit`, `govulncheck`) read-only. Report critical and high advisories that reach runtime or distribution code, and skip low-signal noise.
- Production configuration: CORS that allows credentials broadly, missing response-hardening headers (CSP) on sensitive browser surfaces, cookies without `HttpOnly`, `Secure`, or `SameSite`, debug behavior enabled in production config.
- Data minimization: PII or sensitive operational data in logs, stack traces returned to clients, internal error details in API responses.

## 3. Performance

Look for algorithmic and architectural wins. A performance finding needs an algorithmic argument or a measurement; micro-optimizations without either are not findings.

- N+1 patterns: a query or fetch per item inside a loop or per rendered list row; missing batching or eager loading.
- Wrong complexity: nested scans of the same collection; repeated `find` or `filter` inside a hot loop where a keyed lookup belongs.
- Caching gaps: identical expensive computations or fetches repeated per request or render; no data-layer caching on stable data.
- Payload size: over-fetching (`select *`, whole objects where IDs suffice), unbounded lists without pagination, large JSON shipped to clients.
- Frontend: heavyweight dependencies for trivial use, missing code-splitting on rarely used routes, unoptimized images and fonts, client-side fetching of data available at render time, render waterfalls. Defer to the framework conventions the repository follows.
- Backend: synchronous work that belongs in a queue, missing indexes implied by query patterns (flag for verification; do not claim one without schema evidence), a connection per request where pooling exists.
- Build and CI: slow CI from missing caches, redundant pipeline steps, test suites that could run in parallel.

## 4. Test Coverage

The goal is not a percentage. It is which untested code is dangerous.

- Map the critical paths (money, auth, data mutation, the feature the repository exists for) and find those with zero or trivial coverage.
- High churn plus no tests is the top refactor risk. Flag it as a "characterization tests first" candidate.
- Test quality: tests that assert nothing meaningful, heavy mocking that tests the mocks, snapshot tests nobody reads, flaky patterns (real timers, real network, order dependence).
- Missing layers: unit-only suites with no integration coverage at API boundaries, or the inverse (slow end-to-end tests for what a unit test would catch).
- Verification infrastructure: is there a one-command way to know the code works? If not, that is finding 1 and a prerequisite for every risky plan.

## 5. Tech Debt & Architecture

- Duplication: the same logic in three or more places; divergent copies that have drifted.
- Layering violations: UI importing data-layer internals, circular dependencies, a `utils` module that became a junk drawer with high fan-in.
- Dead code: unexported and unused modules, fully rolled-out feature flags that still branch, commented-out blocks without explanation, manifest dependencies no longer imported.
- Oversized units: files an order of magnitude larger than the median that everything touches; functions with double-digit parameters or deep nesting.
- Inconsistent patterns: three ways to fetch data, handle errors, or style in one repository. Pick the one the team converged on most recently and plan the consolidation.
- Abstraction mismatches: abstractions with a single implementation, or a missing abstraction where one change always touches N files in lockstep.

## 6. Dependencies & Migrations

- Major-version lag on the core framework or runtime, limited to lag with real cost: end of life, security-fix cutoffs, ecosystem incompatibility.
- Deprecated APIs in use that have announced removal dates.
- Abandoned dependencies (no release in years, archived repositories) on critical paths.
- Duplicate dependencies that solve the same problem (two date libraries, two HTTP clients).
- Lockfile and manifest drift; inconsistent version pinning across a monorepo.
- For each migration candidate, estimate the blast radius (files touched). It drives effort and whether to recommend the migration at all.

## 7. DX & Tooling

- Missing or broken: typecheck script, lint config, formatter, pre-commit hooks, editorconfig.
- Slow feedback loops: dev server or test startup measured in minutes, no watch mode, CI without caching.
- Onboarding friction: README setup steps that are wrong or incomplete, undocumented required environment variables, no `.env.example`.
- No agent guide (`AGENTS.md` or `CLAUDE.md`). When agents will execute the plans this is high leverage: recommend one and include its outline in a plan.
- Logging and errors: unstructured service logs, missing request IDs, debugging that requires code changes.

## 8. Docs

Lowest default priority. Flag docs only where their absence or error has a concrete cost:

- Public API surface of a published package without reference docs.
- Architectural decisions nobody can reconstruct (why X over Y) in an area of active dispute.
- Docs that are actively wrong, which is worse than missing: setup instructions, API examples that no longer compile.

## 9. Direction — features & where to take this next

Forward-looking: what the codebase wants to become, not what is broken. **Grounding rule:** every suggestion cites evidence from the repository. A suggestion that fits any project in the category ("add dark mode", "add AI") is noise. Sources of grounded signal:

- **Unfinished intent**: TODO and FIXME clusters around one theme, feature flags never rolled out, stubbed or half-built modules, commented-out feature code, abandoned work visible in git history.
- **Stated but undelivered**: README, docs, or roadmap promises with no code; CLI flags or config options that do nothing; issue templates for features that do not exist. A PRD or `PRODUCT.md` that names users, use cases, or a direction the code has not caught up to is the strongest grounding there is. Prefer it to inferred intent, and never propose what a decision doc already rejected; note the contradiction instead.
- **Surface asymmetries**: export without import, create without bulk-create, webhooks out but not in, an entity with CRUD minus one, a public API that internal code clearly needed and hand-rolled around.
- **The adjacent possible**: capabilities the architecture makes disproportionately cheap, such as a plugin system one interface away or an integration the data model already supports.
- **Friction worth productizing**: things users evidently do by hand around the project (visible in docs, examples, issues).

Direction findings use the standard format with two changes. **Impact** is product value: who wants this and why now. **Confidence** is how well grounded the evidence is, not certainty that it is the right call. Effort is coarser; say so. Strategy belongs to the maintainer, so give grounded options with honest trade-offs. A plan for a selected direction finding is a design or spike plan (investigate, prototype, define the API, list open questions), not a build-everything plan.

---

## Finding format

Every finding from every category and every subagent comes back in this shape:

```markdown
### [SEC-01] Short imperative title

- **Key**: `category:path:symbol`, stable across line shifts (for example `bug:internal/config/load.go:Load`). Later runs match duplicates on it.
- **Evidence**: `path/file.ts:123` — one sentence on what is there. Give the 2–5 strongest locations; write "and ~N similar sites" when widespread.
- **Impact**: What goes wrong or what is being paid. Concrete: "every order-list render issues 1+N queries", not "suboptimal".
- **Effort**: S (hours) / M (about a day) / L (multi-day), for the fix including tests.
- **Risk**: What the fix could break: LOW / MED / HIGH plus one line why.
- **Confidence**: HIGH (read the code, certain; add "reproduced" when a test showed it) / MED (strong signal, needs verification) / LOW (a smell, needs investigation). A LOW finding gets an "investigate" plan, never a "fix" plan.
- **Fix sketch**: One to three sentences. Enough to judge effort honestly; not the plan.
```

ID prefixes: `BUG`, `SEC`, `PERF`, `TEST`, `DEBT`, `DEP`, `DX`, `DOC`, `DIR`. The `Key` uses the plan category words: `bug`, `security`, `perf`, `tests`, `tech-debt`, `migration`, `dx`, `docs`, `direction`.

## Findings table

The table shown to the user has these columns, in this order: `#`, `ID`, `Finding`, `Impact`, `Effort`, `Risk`, `Confidence`, `Evidence` (the strongest `file:line`). In `branch` mode add a `Tag` column. List the full Finding-format entries below the table, or keep them ready when the user asks.

Rate impact by consequence, then lower it one level when the failure needs an unusual trigger, such as a misbehaving upstream server.

| Impact | Meaning |
|--------|---------|
| HIGH | Data loss, security exposure, outage risk, wrong results on a main path, or it blocks other work. |
| MED | A recurring cost to users or developers: slow paths, flaky tests, confusing failures. |
| LOW | Cosmetic or rare. |

## Vetting checklist

Subagents over-report. Before a finding reaches the table, open the cited code yourself and decide:

| Failure class | Action |
|---------------|--------|
| By-design behavior reported as a bug (`https_proxy` flagged as SSRF; a tradeoff recorded in an ADR) | Reject. Record it in the index under "Findings considered and rejected" with its key and one line of reasoning. |
| Real finding, wrong file or line | Correct the evidence. |
| Duplicate across subagents or across categories | Merge. Keep the strongest evidence. |
| The cited code does not say what the subagent claimed | Reject. |
| A HIGH-impact bug that a short test can show | At standard and deep depth, write the test in a scratch copy (`recon.md`) and run it. Mark the finding "reproduced" when it fails as claimed; reject or downgrade it when it does not. |
| Cannot be confirmed in the time available | Downgrade to LOW confidence, or reject. |

## Prioritization rubric

Order findings by **leverage**: impact divided by effort, discounted by confidence and fix risk. Apply these tiebreakers in order:

1. Anything that unblocks other findings (a verification baseline, characterization tests) goes first.
2. HIGH-confidence security findings outrank equal-leverage findings of other categories.
3. Findings whose fix has a clean verification story outrank those without one, because executor models succeed at them.
4. "Not worth doing" is a valid verdict. Record it with one line of reasoning so the user knows it was considered.
