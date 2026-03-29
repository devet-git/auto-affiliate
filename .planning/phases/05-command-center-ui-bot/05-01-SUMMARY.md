---
plan: 05-01
status: complete
completed_at: 2026-03-29
key_files:
  created:
    - web/src/App.tsx
    - web/src/components/ProtectedRoute.tsx
    - web/src/pages/Login.tsx
    - web/src/pages/Dashboard.tsx
    - web/src/lib/api.ts
    - web/src/store/authStore.ts
  modified:
    - web/vite.config.ts
    - web/tsconfig.json
    - web/tsconfig.app.json
    - web/src/index.css
---

# 05-01 Summary: Khởi tạo React Vite & Auth Flow

## What was built
- Thiết lập React SPA với Vite, TailwindCSS (v3), và Shadcn UI.
- Viết `Login.tsx` dùng form Shadcn, kết nối token endpoint của backend.
- Tạo `api.ts` `axios` interceptor tự động inject Authorization header.
- Cấu hình Zustand store lưu trữ Authentication và `ProtectedRoute` cho trang Dashboard.

## Deviations
- Shadcn CLI validate failed với Tailwind v4 nên đã revert Tailwind về v3.4 bằng cách uninstall library cũ và init lại. 
- Sửa các alias imports do lỗi setup của CLI so với Vite v6 structure mới.

## Next Steps
- Implement dữ liệu render trên Dashboard Layout (05-02).
