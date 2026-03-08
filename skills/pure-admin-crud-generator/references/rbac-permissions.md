# RBAC Permissions Guide

## Overview
Pure-admin-thin uses RBAC (Role-Based Access Control) for permission management. Generated pages should integrate with the platform's permission system.

## Permission Types

### 1. Page-Level Permissions (roles)
Control which roles can access a page.

```ts
// In route meta
meta: {
  roles: ["admin", "editor"] // Only these roles can access
}
```

### 2. Button-Level Permissions (auths)
Control which roles can see/use specific buttons.

```ts
// In route meta
meta: {
  auths: ["btn_add", "btn_edit", "btn_delete"]
}
```

## Using Permissions in Generated Pages

### Checking Page Permission
```ts
import { usePermissionStoreHook } from "@/store/modules/permission";

const permissionStore = usePermissionStoreHook();

// Check if user has specific role
const canAccess = permissionStore.roles.some(role => ["admin"].includes(role));
```

### Checking Button Permission
```ts
// In template with v-if
<el-button v-if="permissionStore.auths.includes('btn_add')">Add</el-button>

// Or use directive v-auth
<el-button v-auth="'btn_add'">Add</el-button>
```

## Common Auth Keys

| Auth Key | Description |
| --- | --- |
| `btn_add` | Create/Add button |
| `btn_edit` | Edit button |
| `btn_delete` | Delete button |
| `btn_detail` | View detail button |
| `btn_export` | Export button |
| `btn_import` | Import button |

## Integration with Generated Pages

### Button-Level Permission
```vue
<template>
  <el-table-column label="操作" width="120">
    <template #default="{ row }">
      <el-button
        v-auth="'btn_edit'"
        type="primary"
        link
        @click="handleEdit(row)"
      >
        编辑
      </el-button>
      <el-button
        v-auth="'btn_delete'"
        type="danger"
        link
        @click="handleDelete(row)"
      >
        删除
      </el-button>
    </template>
  </el-table-column>
</template>
```

### Page-Level Permission
When generating route modules, add `auths` based on available operations:

```ts
// Route module
meta: {
  auths: [
    "btn_list",      // List page access
    "btn_add",       // Create operation
    "btn_edit",      // Edit operation
    "btn_delete"     // Delete operation
  ]
}
```

## Best Practices

1. **Consistent naming**: Use standard prefixes (`btn_`, `role_`)
2. **Default to hidden**: If uncertain, use `v-auth` to hide by default
3. **Role hierarchy**: Admin typically has all permissions
4. **Backend-driven**: Real permissions should come from backend API
