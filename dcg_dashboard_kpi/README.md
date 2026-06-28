# DCG Dashboard KPI

Dashboard điều hành cho Ban Giám đốc & Manager — **Presentation Layer** trên nền Odoo 18 Community.

## Triết lý

Module này **không sinh dữ liệu**. Nó chỉ query, tổng hợp KPI, và render. Mở 1 màn hình biết ngay công ty đang thế nào.

## Kiến trúc

```
ir.actions.client → OWL Component → RPC → Python Service → JSON
```

Không dùng form/tree/kanban view. Chỉ dùng **Client Action + OWL**.

## 5 Dashboard

| Dashboard | KPI chính |
|---|---|
| **Home** | Revenue, Profit, Margin, Active Projects, Open Tickets, Customers |
| **Executive** | Contract count, Red projects, Critical tickets, tổng thể |
| **Delivery** | Project by state/health, top projects with progress bar |
| **Finance** | Planned vs Actual, Margin, Collection, Outstanding, top margin projects |
| **Support** | Open tickets, Critical, SLA breached, recent critical table |

## Widget system

```
BaseDashboard (abstract)
├── HomeDashboard
├── ExecutiveDashboard
├── DeliveryDashboard
├── FinanceDashboard
└── SupportDashboard

KpiCard — card hiển thị 1 số với label, color, suffix, click drill-down
DashboardTable — table có click row → open record
```

## Drill-down

Click KPI card → mở Action Odoo chuẩn (list/form). Click table row → open form. Không popup.

## Backend service

`dcg.dashboard.service` (AbstractModel) — 4 method:

| Method | Data source |
|---|---|
| `get_executive_data()` | contract, project, finance, ticket, employee |
| `get_delivery_data()` | project delivery (state, health, progress) |
| `get_finance_data()` | project finance (P&L, collection, margin) |
| `get_support_data()` | warranty ticket (open, critical, SLA breach) |

## Responsive

Desktop: 4 card/row. Tablet: 2 card/row. Mobile: 1 card/row.

## Màu theo Bootstrap

primary (Revenue), success (Profit), warning (Tickets), danger (Critical), info (Margin).

## Mở rộng

Thêm dashboard mới = 3 bước:
1. Python method trong `dashboard_service.py`
2. OWL template trong `xml/dashboard.xml`
3. Class kế thừa `BaseDashboard` + register action

## Tác giả

Công ty TNHH Đổi Mới G.R.O.U.P
