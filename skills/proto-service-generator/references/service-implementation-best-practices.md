# Service Implementation Best Practices

## Table of Contents

1. Interface Assertion Template
2. Stub Template for Unknown Logic
3. Simple CRUD (Direct Ent) Template
4. Append-Only Update Pattern
5. Complex Logic Split to Usecase
6. Wire Injection Pattern
7. Import and Naming Checklist
8. Sphere Feature Reuse Pattern

## 1) Interface Assertion Template

Each service file must include an interface assertion to enforce compile-time completeness checks.

```go
var _ dashv1.AdminSessionServiceHTTPServer = (*Service)(nil)
```

## 2) Stub Template for Unknown Logic

When business logic cannot be safely inferred, generate a compilable stub first instead of guessing.

```go
package dash

import (
	"context"
	"errors"

	dashv1 "github.com/go-sphere/sphere-layout/api/dash/v1"
)

func (s *Service) RefreshSomething(ctx context.Context, req *dashv1.RefreshSomethingRequest) (*dashv1.RefreshSomethingResponse, error) {
	return nil, errors.New("not implemented: RefreshSomething")
}
```

## 3) Simple CRUD (Direct Ent) Template

For simple CRUD, call Ent directly in Service and do not add an extra DAO business layer.

```go
package dash

import (
	"context"

	"entgo.io/ent/dialect/sql"
	dashv1 "github.com/go-sphere/sphere-layout/api/dash/v1"
	"github.com/go-sphere/sphere-layout/internal/pkg/conv"
	"github.com/go-sphere/sphere-layout/internal/pkg/database/ent/keyvaluestore"
	"github.com/go-sphere/sphere-layout/internal/pkg/render/entbind"
)

var _ dashv1.KeyValueStoreServiceHTTPServer = (*Service)(nil)

func (s *Service) CreateKeyValueStore(ctx context.Context, req *dashv1.CreateKeyValueStoreRequest) (*dashv1.CreateKeyValueStoreResponse, error) {
	item, err := entbind.CreateKeyValueStore(s.db.KeyValueStore.Create(), req.KeyValueStore).Save(ctx)
	if err != nil {
		return nil, err
	}
	return &dashv1.CreateKeyValueStoreResponse{
		KeyValueStore: s.render.KeyValueStore(item),
	}, nil
}

func (s *Service) GetKeyValueStore(ctx context.Context, req *dashv1.GetKeyValueStoreRequest) (*dashv1.GetKeyValueStoreResponse, error) {
	item, err := s.db.KeyValueStore.Get(ctx, req.Id)
	if err != nil {
		return nil, err
	}
	return &dashv1.GetKeyValueStoreResponse{
		KeyValueStore: s.render.KeyValueStore(item),
	}, nil
}

func (s *Service) ListKeyValueStores(ctx context.Context, req *dashv1.ListKeyValueStoresRequest) (*dashv1.ListKeyValueStoresResponse, error) {
	query := s.db.KeyValueStore.Query()
	count, err := query.Clone().Count(ctx)
	if err != nil {
		return nil, err
	}
	totalPage, pageSize := conv.Page(count, int(req.PageSize))
	rows, err := query.Clone().
		Limit(pageSize).
		Order(keyvaluestore.ByID(sql.OrderDesc())).
		Offset(pageSize * int(req.Page)).
		All(ctx)
	if err != nil {
		return nil, err
	}
	return &dashv1.ListKeyValueStoresResponse{
		KeyValueStores: conv.Map(rows, s.render.KeyValueStore),
		TotalSize:      int64(count),
		TotalPage:      int64(totalPage),
	}, nil
}

func (s *Service) UpdateKeyValueStore(ctx context.Context, req *dashv1.UpdateKeyValueStoreRequest) (*dashv1.UpdateKeyValueStoreResponse, error) {
	item, err := entbind.UpdateOneKeyValueStore(
		s.db.KeyValueStore.UpdateOneID(req.KeyValueStore.Id),
		req.KeyValueStore,
	).Save(ctx)
	if err != nil {
		return nil, err
	}
	return &dashv1.UpdateKeyValueStoreResponse{
		KeyValueStore: s.render.KeyValueStore(item),
	}, nil
}

func (s *Service) DeleteKeyValueStore(ctx context.Context, req *dashv1.DeleteKeyValueStoreRequest) (*dashv1.DeleteKeyValueStoreResponse, error) {
	if err := s.db.KeyValueStore.DeleteOneID(req.Id).Exec(ctx); err != nil {
		return nil, err
	}
	return &dashv1.DeleteKeyValueStoreResponse{}, nil
}
```

## 4) Append-Only Update Pattern

Do not rewrite existing files. Append only missing pieces.

Execution order:
1. Read all method signatures from `type XxxServiceHTTPServer interface`.
2. Scan existing methods in target `internal/service/<module>/<service>.go`.
3. Append only missing methods.
4. Append assertion if missing.
5. Add only required imports; do not change existing logic.

## 5) Complex Logic Split to Usecase

When method flow is clearly complex (cross-entity transactions, reusable orchestration, long flows), split into `internal/usecase/<module>/<service>/`.

Example structure:

```text
internal/usecase/dash/admin_session/
  usecase.go
```

`usecase.go` example:

```go
package adminsession

import (
	"context"
)

type Usecase struct{}

func NewUsecase() *Usecase {
	return &Usecase{}
}

func (u *Usecase) RunComplexFlow(ctx context.Context, userID int64) error {
	// TODO: implement business flow
	return nil
}
```

Service usage example:

```go
type Service struct {
	// ...
	adminSessionUC *adminsession.Usecase
}

func (s *Service) SomeComplexMethod(ctx context.Context, req *dashv1.SomeComplexMethodRequest) (*dashv1.SomeComplexMethodResponse, error) {
	if err := s.adminSessionUC.RunComplexFlow(ctx, req.UserId); err != nil {
		return nil, err
	}
	return &dashv1.SomeComplexMethodResponse{}, nil
}
```

## 6) Wire Injection Pattern

After adding a usecase, ensure providers can inject into service.

`internal/usecase/dash/admin_session/wire.go` (optional):

```go
package adminsession

import "github.com/google/wire"

var ProviderSet = wire.NewSet(
	NewUsecase,
)
```

`internal/service/wire.go` update example:

```go
var ProviderSet = wire.NewSet(
	api.NewService,
	dash.NewService,
	bot.NewService,
	adminsession.NewUsecase,
)
```

`internal/service/dash/service.go` constructor update example:

```go
func NewService(
	db *dao.Dao,
	wechat *wechat.Wechat,
	cache cache.ByteCache,
	store storage.CDNStorage,
	adminSessionUC *adminsession.Usecase,
) *Service {
	return &Service{
		db:             db,
		wechat:         wechat,
		cache:          cache,
		storage:        store,
		adminSessionUC: adminSessionUC,
	}
}
```

## 7) Import and Naming Checklist

1. File naming: `XxxService -> xxx.go` (snake_case).
2. Receiver: always `func (s *Service)`.
3. Import `context`, `errors`, `sql`, `conv`, `entbind` as needed.
4. Do not import unused packages; do not modify generated files under `api/*`.
5. After changes, run at least:
`go test ./internal/service/...`, `go test ./cmd/app/...`.

## 8) Sphere Feature Reuse Pattern

Use existing Sphere/repository capabilities before writing custom code.

Reuse checks:
1. Search sibling services for existing patterns.
2. Search for existing middleware/auth/error handling flow in server setup.
3. Search for existing bind/render helpers before adding mapping code.
4. Search provider sets before adding duplicate constructors.

Suggested lookup commands:

```bash
rg -n "Register.*ServiceHTTPServer|NewAuthMiddleware|WithJson|sphere\\.errors|ProviderSet" internal api
rg -n "entbind\\.|entmap\\.|conv\\.Page|DeleteOneID|UpdateOneID|IDIn\\(" internal
rg -n "type Service struct|func NewService\\(" internal/service
```

If `sphere-feature-workflow` is available, use it together with this skill:
1. Let it guide end-to-end Sphere feature integration.
2. Keep this skill focused on service file coverage and method implementation shape.
3. Prefer framework-native flow over custom duplicated code.
