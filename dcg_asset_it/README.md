# DCG Asset IT

Quản trị tài sản CNTT & thiết bị triển khai dự án, trên nền **Odoo 18 Community**.

## 12 model mới + 1 extend

| # | Model | Vai trò |
|---|---|---|
| 1 | `dcg.asset` | Core: vòng đời tài sản, kanban stage, tech specs |
| 2 | `dcg.asset.type` | Laptop, Server, Router, License, Cloud... |
| 3 | `dcg.asset.category` | IT Equipment, Software, Infrastructure... |
| 4 | `dcg.asset.stage` | Dynamic: New → In Stock → Assigned → Maintenance → Retired → Disposed |
| 5 | `dcg.asset.location` | Warehouse, Office, Server Room, Customer Site |
| 6 | `dcg.asset.assignment` | Cấp phát dài hạn (employee/project) + history |
| 7 | `dcg.asset.history` | Audit trail: register/assign/return/repair/dispose |
| 8 | `dcg.asset.warranty` | Warranty per asset (vendor, start/end, expired auto) |
| 9 | `dcg.asset.maintenance` | Maintenance log + cost |
| 10 | `dcg.asset.license` | Seat tracking, expiry, over-license warning |
| 11 | `dcg.asset.software.install` | Phần mềm cài per device + license link |
| 12 | `dcg.asset.checkout` | Mượn tạm ngắn hạn (CHK/): Request → Approve → Checkout → Return |
| 13 | `hr.employee` (extend) | assigned_asset_count, smart button |

## Sequences: `AST/00001`, `CHK/00001`

## Tác giả

Công ty TNHH Đổi Mới G.R.O.U.P
