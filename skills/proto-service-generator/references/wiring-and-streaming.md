# Wiring, Imports, Reuse, and Streaming

What to do around the method bodies: dependency injection, import and naming rules, finding
existing code to reuse, and the server-streaming SSE template.

## Wire Injection

When adding usecase dependencies:

`internal/service/wire.go`:
```go
var ProviderSet = wire.NewSet(
    NewService,
    usecase.NewUsecase,
)
```

`internal/service/xxx/service.go`:
```go
func NewService(db *dao.Dao, usecaseUC *usecase.Usecase) *Service {
    return &Service{db: db, usecaseUC: usecaseUC}
}
```

---

## Import & Naming

- File: `XxxService` → `xxx.go` (snake_case)
- Receiver: `(s *Service)`
- Signatures: match interface exactly
- Imports: `context`, `errors`, `conv`, `entbind`, generated API package only

---

## Reuse First

Before adding code, search for existing patterns:
```bash
# Find existing services
rg -n "type Service struct" internal/service
# Find bind/render helpers
rg -n "entbind\.|s\.render\." internal
# Find provider sets
rg -n "ProviderSet" internal/service
```

---

## Server-Streaming SSE Template

`protoc-gen-sphere` generates a push-style interface for
`rpc Watch(Request) returns (stream Reply)`:

```go
Watch(context.Context, *v1.WatchRequest, func(*v1.WatchReply) error) error
```

For unknown business logic, keep the stub shape exact:

```go
func (s *Service) Watch(
    ctx context.Context,
    req *v1.WatchRequest,
    send func(*v1.WatchReply) error,
) error {
    return errors.New("not implemented: Watch")
}
```

For an implemented producer, observe both cancellation and backpressure:

```go
func (s *Service) Watch(
    ctx context.Context,
    req *v1.WatchRequest,
    send func(*v1.WatchReply) error,
) error {
    ticker := time.NewTicker(time.Second)
    defer ticker.Stop()

    for seq := int64(0); ; seq++ {
        select {
        case <-ctx.Done():
            return ctx.Err()
        case <-ticker.C:
            if err := send(&v1.WatchReply{Sequence: seq}); err != nil {
                return err
            }
        }
    }
}
```

Rules:

- Treat `send` as a blocking operation that provides backpressure.
- Stop immediately on a send error; it commonly means the client disconnected.
- Do not start an untracked goroutine or retain `send` after the method returns.
- Do not use `httpx.Context`; the runtime deliberately separates request
  preparation from the producer phase.
- Returning `nil` emits the terminal `done` event. Returning an error before
  the first reply may produce a regular JSON error; a later error becomes the
  terminal SSE `error` event.
