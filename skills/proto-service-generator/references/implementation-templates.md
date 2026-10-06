# Method Body Templates

Templates for the common method shapes. Interface assertion, file mapping, and the compilable
stub live in `service-implementation-best-practices.md`.

## Simple CRUD Template

Direct Ent call, no DAO layer:
```go
// Create
func (s *Service) CreateXxx(ctx context.Context, req *v1.CreateXxxRequest) (*v1.CreateXxxResponse, error) {
    item, err := entbind.CreateXxx(s.db.Xxx.Create(), req.Xxx).Save(ctx)
    if err != nil {
        return nil, err
    }
    return &v1.CreateXxxResponse{Xxx: s.render.Xxx(item)}, nil
}

// Get
func (s *Service) GetXxx(ctx context.Context, req *v1.GetXxxRequest) (*v1.GetXxxResponse, error) {
    item, err := s.db.Xxx.Get(ctx, req.Id)
    if err != nil {
        return nil, err
    }
    return &v1.GetXxxResponse{Xxx: s.render.Xxx(item)}, nil
}

// List (with pagination)
func (s *Service) ListXxx(ctx context.Context, req *v1.ListXxxRequest) (*v1.ListXxxResponse, error) {
    query := s.db.Xxx.Query()
    count, _ := query.Clone().Count(ctx)
    totalPage, pageSize := conv.Page(count, int(req.PageSize))
    rows, _ := query.Clone().Limit(pageSize).Order(ByID(sql.OrderDesc())).Offset(pageSize * int(req.Page)).All(ctx)
    return &v1.ListXxxResponse{
        XxxList: conv.Map(rows, s.render.Xxx),
        TotalSize: int64(count),
        TotalPage: int64(totalPage),
    }, nil
}

// Update
func (s *Service) UpdateXxx(ctx context.Context, req *v1.UpdateXxxRequest) (*v1.UpdateXxxResponse, error) {
    item, err := entbind.UpdateOneXxx(s.db.Xxx.UpdateOneID(req.Xxx.Id), req.Xxx).Save(ctx)
    if err != nil {
        return nil, err
    }
    return &v1.UpdateXxxResponse{Xxx: s.render.Xxx(item)}, nil
}

// Delete
func (s *Service) DeleteXxx(ctx context.Context, req *v1.DeleteXxxRequest) (*v1.DeleteXxxResponse, error) {
    if err := s.db.Xxx.DeleteOneID(req.Id).Exec(ctx); err != nil {
        return nil, err
    }
    return &v1.DeleteXxxResponse{}, nil
}
```

**When to use**: Method is `Create*`, `Get*`, `List*`, `Update*`, `Delete*` on single entity.

---

## Append-Only Update

**Never rewrite existing files.** Only append missing methods.

1. Read interface signatures from `api/<module>/v1/*.sphere.pb.go`
2. Check existing methods in `internal/service/<module>/xxx.go`
3. Append only missing methods + assertion + required imports
4. Classify each method by its generated signature before choosing a template; a server stream returns `error` and receives `send func(*Reply) error`.

---

## Complex Logic → Usecase

For cross-entity transactions or complex flows:
```
internal/usecase/<module>/<service>/
```

```go
package service

type Usecase struct{}

func NewUsecase() *Usecase { return &Usecase{} }

func (u *Usecase) RunComplexFlow(ctx context.Context, userID int64) error {
    // TODO: implement
    return nil
}
```

Service uses usecase:
```go
func (s *Service) ComplexMethod(ctx context.Context, req *v1.ComplexRequest) (*v1.ComplexResponse, error) {
    if err := s.usecase.RunComplexFlow(ctx, req.UserId); err != nil {
        return nil, err
    }
    return &v1.ComplexResponse{}, nil
}
```

---

