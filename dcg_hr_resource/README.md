# DCG HR Resource

Mở rộng HR phục vụ Delivery — năng lực nhân sự triển khai dự án, trên nền **Odoo 18 Community**.

## Quan hệ với dcg_resource_planning

Module này **bổ sung** (không trùng lặp) `dcg_resource_planning`:

| dcg_resource_planning (đã có) | dcg_hr_resource (mới) |
|---|---|
| `dcg.resource.role` — vai trò | `dcg.employee.career.level` — cấp bậc |
| `dcg.resource.skill` — kỹ năng | `dcg.employee.certificate` — chứng chỉ |
| `dcg.resource.allocation` — phân bổ | `dcg.employee.training` — đào tạo |
| `dcg.resource.capacity` — năng lực kỳ | `dcg.employee.competency` — đánh giá năng lực |
| `dcg.resource.request` — yêu cầu NL | `dcg.employee.kpi` — KPI triển khai |
| | `dcg.employee.availability` — khả dụng |

## 6 model mới + 1 extend hr.employee

| # | Model | Vai trò |
|---|---|---|
| 1 | `dcg.employee.career.level` | Intern → Fresher → Junior → Senior → Leader → Director (8 seed) |
| 2 | `dcg.employee.certificate` | Chứng chỉ + hết hạn auto-compute + attachment |
| 3 | `dcg.employee.training` | Lịch sử đào tạo (course, result, provider) |
| 4 | `dcg.employee.competency` | Đánh giá theo kỳ (technical, communication, leadership... → overall) |
| 5 | `dcg.employee.kpi` | KPI delivery: utilization, billable, overtime, score |
| 6 | `dcg.employee.availability` | Trạng thái khả dụng (available/partial/allocated/leave/training/resigned) |
| 7 | `hr.employee` (extend) | hour_cost, hour_bill_rate, career_level, capacity, target_utilization |

## Menu

Nằm dưới **Resource Planning** root menu (không tạo app riêng):

```
Resource Planning
├── ...
├── HR Resource
│   ├── Certificates
│   ├── Training
│   ├── Competency
│   ├── Delivery KPIs
│   └── Availability
└── Configuration
    ├── ...
    └── Career Levels
```

## Employee form — 4 tab mới

- **Delivery Profile**: employee_code, career_level, hour_cost, bill_rate, capacity
- **Certificates**: list inline + cảnh báo hết hạn
- **Training**: lịch sử khoá học + kết quả
- **KPI**: utilization, billable, overall score (manager only)

## I18N

`i18n/vi.po` — 82 entry, 100%, đúng format Odoo 18.

## Tác giả

Công ty TNHH Đổi Mới G.R.O.U.P
