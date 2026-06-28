# DCG Knowledge SOP

Kho Tri thức & Quy trình chuẩn — SOP, FAQ, Best Practice, Known Issue, Coding Standard — trên nền **Odoo 18 Community**.

## 5 model mới

| # | Model | Vai trò |
|---|---|---|
| 1 | `dcg.knowledge.category` | Danh mục: SOP, FAQ, Best Practice, Known Issue... (8 seed) |
| 2 | `dcg.knowledge.tag` | Tag đa chiều: module, technology, process, domain |
| 3 | `dcg.knowledge.article` | Bài viết chính: lifecycle, view count, rating, link project/ticket |
| 4 | `dcg.knowledge.revision` | Version history nội dung |
| 5 | `dcg.knowledge.feedback` | Rating + comment từ team |

## Article types

SOP, FAQ, Best Practice, Known Issue, Coding Standard, Guide, Checklist, Other.

Form tự động hiện tab phù hợp: FAQ → Question/Answer, Known Issue → Problem/Root Cause/Solution.

## Lifecycle

```
Draft → Submit Review → In Review → Publish → Published → Archive
```

Published articles có thể "Save Revision" để snapshot nội dung trước khi sửa.

## Tích hợp Dashboard

Sau khi cài module này, dashboard có thể bổ sung Knowledge Dashboard widget:
- Most Viewed SOP, Top FAQ, Pending Review, Knowledge Coverage

## Sequence: `KB/00001`

## Tác giả

Công ty TNHH Đổi Mới G.R.O.U.P
