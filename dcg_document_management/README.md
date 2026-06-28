# DCG Document Management

DMS (Document Management System) cho toàn bộ vòng đời dự án, trên nền **Odoo 18 Community**.

## 10 model mới

| # | Model | Vai trò |
|---|---|---|
| 1 | `dcg.document` | Core: document lifecycle (Draft → Review → Approved → Published → Archived) |
| 2 | `dcg.document.version` | Version control: document → version → ir.attachment |
| 3 | `dcg.document.folder` | Folder tree (parent/child) — thư mục theo project/customer |
| 4 | `dcg.document.category` | Phân loại: Contract, BRD, SRS, Test, Manual, Acceptance... |
| 5 | `dcg.document.type` | Quy định: requires_approval, requires_version, portal_visible, retention |
| 6 | `dcg.document.tag` | Tag đa chiều: Urgent, Confidential, Internal, Final... |
| 7 | `dcg.document.review` | Review/approval workflow per document |
| 8 | `dcg.document.link` | Generic business link: 1 doc → nhiều object (project, contract, ticket, trip) |
| 9 | `dcg.document.template` | Mẫu tạo nhanh (NDA, Proposal, BRD...) + default content |
| 10 | `dcg.document.checklist` | Kiểm tra đủ tài liệu trước Go-live per project |

## Điểm khác biệt so với ir.attachment

```
ir.attachment = file vật lý
dcg.document  = business object có lifecycle, version, review, permission
```

Document → Version → Attachment: mỗi khi cập nhật file, tạo version mới thay vì sửa trực tiếp.

## Document lifecycle

```
Draft → Submit Review → In Review → Approve → Published → Archive
                                  → Rejected → Reset to Draft
```

Published document không sửa trực tiếp — tạo version mới.

## Checklist

PM mở project → thấy checklist:
- ✅ Biên bản nghiệm thu (linked → approved)
- ✅ User Manual (linked → published)
- ❌ Deployment Guide (chưa upload)
- ❌ Training Video (chưa upload)

## I18N

`i18n/vi.po` — 99 entry, 100%, đúng format Odoo 18.

## Tác giả

Công ty TNHH Đổi Mới G.R.O.U.P
