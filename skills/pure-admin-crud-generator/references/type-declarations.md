# Type Declarations Guide

## Overview
Proper TypeScript types ensure type safety and IDE autocomplete. Use platform conventions for type declarations.

## Common Type Patterns

### API Response Types
```ts
// List response with pagination
export interface XxxListResponse {
  list: XxxItem[];
  total: number;
}

// Detail response
export interface XxxDetailResponse {
  item: XxxItem;
}

// Create/Update response
export interface XxxOperationResponse {
  id: number;
}
```

### Form Data Types
```ts
// Create/Update request
export interface XxxFormData {
  name: string;
  status: number;
  remark?: string;
}

// Query params
export interface XxxQueryParams {
  page: number;
  page_size: number;
  name?: string;
  status?: number;
}
```

### Table Row Types
```ts
export interface XxxItem {
  id: number;
  name: string;
  status: number;
  created_at: string;
  updated_at: string;
}
```

## Using Types in Generated Pages

### Index Page Type Usage
```ts
import type { XxxItem, XxxListResponse, XxxQueryParams } from "@/api/xxx/types";

// Table data type
const tableData = ref<XxxItem[]>([]);

// Query params
const queryParams = reactive<XxxQueryParams>({
  page: 0,
  page_size: 10,
  name: ""
});
```

### Edit Page Type Usage
```ts
import type { XxxFormData } from "@/api/xxx/types";
import type { XxxDetailResponse } from "@/api/xxx/types";

// Form data
const formData = reactive<XxxFormData>({
  name: "",
  status: 1,
  remark: ""
});

// Detail response
const detailData = ref<XxxDetailResponse["item"] | null>(null);
```

## Platform Type Exports

### RouteConfigsTable
```ts
import type { RouteConfigsTable } from "@/router/types";
```

### Form Instance
```ts
import type { FormInstance } from "element-plus";
```

## Type Inference from API

When types are not explicitly exported, infer from response:

```ts
// Infer from API call
const { data } = await getXxxList(queryParams);
// data is unknown, cast as needed
const list = (data as XxxListResponse).list;
```

## Best Practices

1. Define types close to API methods
2. Use `interface` for object shapes
3. Use `type` for unions, aliases
4. Export types for reuse across pages
5. Add JSDoc comments for complex types
