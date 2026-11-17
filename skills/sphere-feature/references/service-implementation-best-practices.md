# Service Implementation Best Practices

Reference for completing service implementations from generated interfaces. Load sections as needed.

## Quick Reference

| Need | Read |
|------|------|
| Interface assertion and file mapping | this file |
| Compilable stub for unknown logic | this file, Stub Template |
| Simple CRUD method | `implementation-templates.md` |
| Append-only update | `implementation-templates.md` |
| Complex logic extracted to a usecase | `implementation-templates.md`, then `wiring-and-streaming.md` |
| Wire injection, imports, reuse lookups | `wiring-and-streaming.md` |
| Server-streaming SSE method | `wiring-and-streaming.md` |

---

## Interface Assertion & File Mapping

**Mapping**: `XxxService` → `internal/service/<module>/xxx.go`

**Required assertion**:
```go
var _ dashv1.XxxServiceHTTPServer = (*Service)(nil)
```

**Discovery**:
```bash
rg -n "type .*ServiceHTTPServer interface" api
```

---

## Stub Template

For unknown logic, generate compilable stub:
```go
func (s *Service) MethodName(ctx context.Context, req *v1.MethodRequest) (*v1.MethodResponse, error) {
    return nil, errors.New("not implemented: MethodName")
}
```

---

Method body templates live in `implementation-templates.md`. Wire injection, imports, reuse
lookups, and the SSE template live in `wiring-and-streaming.md`.
