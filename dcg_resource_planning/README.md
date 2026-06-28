# DCG Resource Planning

Capacity planning, resource allocation, forecast, utilization, bench — PSA core trên nền **Odoo 18 Community**.

## Vị trí trong hệ thống

```
CRM (Estimate: cần bao nhiêu resource?)
  → Contract (ký → tạo plan)
    → Project Delivery (tạo → generate allocation)
      → Resource Planning ← (cầu nối)
        → Timesheet (actual hours)
          → Finance (labor cost)
```

## 7 model mới + 1 extend

| # | Model | Vai trò |
|---|---|---|
| 1 | `dcg.resource.role` | Role master (thay Selection), cost/bill rate mặc định |
| 2 | `dcg.resource.skill` | Skill matrix per employee (level 1-5, certified, years) |
| 3 | `dcg.resource.plan` | Plan header 1:1 với project (RPL/), summary |
| 4 | `dcg.resource.allocation` | Allocation % + hours, over-allocation detect |
| 5 | `dcg.resource.request` | PM request resource → HR approve → allocate (RRQ/) |
| 6 | `dcg.resource.capacity` | Monthly capacity snapshot (auto compute) |
| 7 | `dcg.resource.forecast` | Role × month demand/supply/gap |
| 8 | `hr.employee` (extend) | primary_role, skills, current_allocation_percent, is_on_bench |

## Allocation & over-allocation

Mỗi employee có thể được allocate cho nhiều project, tổng % không nên vượt 100%.
`total_allocation_percent` compute real-time từ tất cả allocation overlap, hiện cảnh báo đỏ nếu > 100%.

## Capacity = computed

`capacity_hours` (mặc định 160h/tháng) — `allocated_hours` (pro-rate từ allocation) = `available_hours`.
`utilization_rate = billable_hours / capacity_hours × 100`.
`bench_hours = capacity - allocated`.

## Resource request flow

```
PM tạo request (role + quantity + urgency + period)
  → Submit → HR/Manager Approve → Allocate employees → Mark Allocated
```

## Sequences

| Code | Prefix |
|---|---|
| dcg.resource.plan | RPL/ |
| dcg.resource.request | RRQ/ |

## Tác giả

Công ty TNHH Đổi Mới G.R.O.U.P
