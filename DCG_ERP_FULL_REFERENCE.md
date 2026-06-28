# DCG ERP System — Odoo 18 Community
# Chi tiết 15 module · 109 model · 1346 field
# Công ty TNHH Đổi Mới G.R.O.U.P — 2026

---

## 1. Tổng quan hệ thống

| # | Module | Models | Fields | Vai trò |
|---|--------|--------|--------|---------|
| 1 | `dcg_master_data` | 15 | 61 | Core master data, abstract mixin, seed data |
| 2 | `dcg_approval_matrix` | 6 | 98 | Engine phê duyệt đa cấp, mixin |
| 3 | `dcg_crm_presales` | 7 | 155 | CRM mở rộng, estimate, presales cost |
| 4 | `dcg_contract_management` | 8 | 135 | Hợp đồng, phụ lục, thanh toán, nghiệm thu |
| 5 | `dcg_project_delivery` | 7 | 128 | Triển khai dự án, scope, milestone, issue, CR |
| 6 | `dcg_timesheet_control` | 5 | 66 | Chấm công, sheet approval, OT |
| 7 | `dcg_project_finance` | 5 | 84 | P&L dự án, cost/revenue lines, variance |
| 8 | `dcg_business_trip` | 4 | 73 | Công tác, thành viên, chi phí, sync finance |
| 9 | `dcg_helpdesk_warranty` | 9 | 99 | Ticket bảo hành, SLA, dynamic stage, KB |
| 10 | `dcg_resource_planning` | 8 | 108 | Capacity, allocation %, forecast, request |
| 11 | `dcg_document_management` | 10 | 89 | DMS: folder, version, review, checklist |
| 12 | `dcg_hr_resource` | 7 | 76 | Năng lực NS: career, certificate, KPI |
| 13 | `dcg_asset_it` | 13 | 118 | Tài sản CNTT, license, assignment, checkout |
| 14 | `dcg_knowledge_sop` | 5 | 56 | Tri thức: SOP, FAQ, best practice, revision |
| 15 | `dcg_dashboard_kpi` | 1 | — | Dashboard OWL (presentation layer) |
| | **TỔNG** | **110** | **1346+** | |

## 2. Sơ đồ dependency

```
dcg_master_data
│
├── dcg_approval_matrix
│
├── dcg_crm_presales
│   └── dcg_contract_management
│       └── dcg_project_delivery
│           ├── dcg_timesheet_control
│           │   └── dcg_project_finance
│           │       └── dcg_business_trip
│           │
│           ├── dcg_helpdesk_warranty
│           │
│           ├── dcg_resource_planning
│           │   └── dcg_hr_resource
│           │
│           ├── dcg_document_management
│           │
│           └── dcg_knowledge_sop
│
├── dcg_asset_it
│
└── dcg_dashboard_kpi ──→ (reads all modules)
```

## 3. Sơ đồ liên kết model

### 3.1 Luồng nghiệp vụ chính (CRM → Delivery → Finance)

```
crm.lead (CRM)
  │ commercial_status, presales_owner_id
  │
  ├──→ dcg.crm.requirement (REQ/) ──→ dcg.crm.solution.scope
  │
  ├──→ dcg.crm.estimate (EST/) ──→ dcg.crm.estimate.line
  │                                        │
  │                                        ▼
  ├──→ sale.order ──→ dcg.contract (CTR/) ──→ dcg.contract.line
  │                       │                ──→ dcg.contract.payment
  │                       │                ──→ dcg.contract.appendix (APX/)
  │                       │                ──→ dcg.contract.acceptance (ACC/)
  │                       │
  │                       ▼
  │              dcg.project.delivery (PRJ/) ──→ dcg.project.scope
  │                       │                  ──→ dcg.project.milestone
  │                       │                  ──→ dcg.project.member
  │                       │                  ──→ dcg.project.issue
  │                       │                  ──→ dcg.project.change.request (CR/)
  │                       │
  │              ┌────────┼──────────┐
  │              ▼        ▼          ▼
  │     dcg.timesheet  dcg.project  dcg.business
  │     .sheet (TS/)   .finance     .trip (TRIP/)
  │         │         (FIN/)            │
  │         ▼            │              ▼
  │   account.        ┌──┴──┐     expense
  │   analytic.line   ▼     ▼     (→ finance)
  │   (timesheet)   cost  revenue
  │   (→ finance)   line    line
  │
  └──→ dcg.warranty.ticket (TKT/) ──→ dcg.warranty.activity
              │                    ──→ dcg.warranty.solution
              └──→ dcg.warranty.sla
```

### 3.2 Luồng nhân sự (HR → Resource → Allocation)

```
hr.employee
  ├──→ dcg.resource.role (master)
  ├──→ dcg.resource.skill (employee × skill × level)
  ├──→ dcg.employee.career.level
  ├──→ dcg.employee.certificate
  ├──→ dcg.employee.training
  ├──→ dcg.employee.competency
  ├──→ dcg.employee.kpi
  └──→ dcg.employee.availability

dcg.resource.plan (RPL/) ──→ dcg.project.delivery (1:1)
  ├──→ dcg.resource.allocation (employee × project × %)
  └──→ dcg.resource.request (RRQ/)

dcg.resource.capacity (employee × month)
dcg.resource.forecast (role × month)
```

### 3.3 Tài liệu & Tài sản

```
dcg.document (DOC/) ──→ dcg.document.version ──→ ir.attachment
  ├──→ dcg.document.folder (tree)
  ├──→ dcg.document.category
  ├──→ dcg.document.type (rules: approval, version, portal)
  ├──→ dcg.document.tag
  ├──→ dcg.document.template
  ├──→ dcg.document.review
  ├──→ dcg.document.link (generic: model + res_id)
  └──→ dcg.document.checklist (per project)

dcg.asset (AST/) ──→ dcg.asset.type
  ├──→ dcg.asset.category
  ├──→ dcg.asset.stage (dynamic)
  ├──→ dcg.asset.location
  ├──→ dcg.asset.assignment (long-term)
  ├──→ dcg.asset.history (audit)
  ├──→ dcg.asset.warranty
  ├──→ dcg.asset.maintenance
  ├──→ dcg.asset.license (seat tracking)
  ├──→ dcg.asset.software.install
  └──→ dcg.asset.checkout (CHK/ short-term)

dcg.knowledge.article (KB/) ──→ dcg.knowledge.category
  ├──→ dcg.knowledge.tag
  ├──→ dcg.knowledge.revision
  └──→ dcg.knowledge.feedback
```

## 4. Danh sách sequence (19 tổng)

| Prefix | Model | Module |
|--------|-------|--------|
| `APR/` | `dcg.approval.request` | `dcg_approval_matrix` |
| `REQ/` | `dcg.crm.requirement` | `dcg_crm_presales` |
| `EST/` | `dcg.crm.estimate` | `dcg_crm_presales` |
| `CTR/` | `dcg.contract` | `dcg_contract_management` |
| `APX/` | `dcg.contract.appendix` | `dcg_contract_management` |
| `ACC/` | `dcg.contract.acceptance` | `dcg_contract_management` |
| `PRJ/` | `dcg.project.delivery` | `dcg_project_delivery` |
| `CR/` | `dcg.project.change.request` | `dcg_project_delivery` |
| `TS/` | `dcg.timesheet.sheet` | `dcg_timesheet_control` |
| `OT/` | `dcg.timesheet.ot.request` | `dcg_timesheet_control` |
| `FIN/` | `dcg.project.finance` | `dcg_project_finance` |
| `TRIP/` | `dcg.business.trip` | `dcg_business_trip` |
| `TKT/` | `dcg.warranty.ticket` | `dcg_helpdesk_warranty` |
| `RPL/` | `dcg.resource.plan` | `dcg_resource_planning` |
| `RRQ/` | `dcg.resource.request` | `dcg_resource_planning` |
| `DOC/` | `dcg.document` | `dcg_document_management` |
| `AST/` | `dcg.asset` | `dcg_asset_it` |
| `CHK/` | `dcg.asset.checkout` | `dcg_asset_it` |
| `KB/` | `dcg.knowledge.article` | `dcg_knowledge_sop` |

## 5. Giá trị Selection chính

### `ACCEPTANCE_STATE_SELECTION`

| Value | Label |
|-------|-------|
| `draft` | Draft |
| `confirmed` | Confirmed |
| `cancelled` | Cancelled |

### `ACCEPTANCE_TYPE_SELECTION`

| Value | Label |
|-------|-------|
| `phase` | Phase Acceptance |
| `milestone` | Milestone Acceptance |
| `final` | Final Acceptance |
| `warranty_handover` | Warranty / Handover |

### `ACTION_SELECTION`

| Value | Label |
|-------|-------|
| `submit` | Submit |
| `approve` | Approve |
| `reject` | Reject |
| `cancel` | Cancel |

### `ACTIVITY_TYPE_SELECTION`

| Value | Label |
|-------|-------|
| `assign` | Assign |
| `comment` | Comment |
| `call` | Call |
| `meeting` | Meeting |
| `deploy` | Deploy |
| `testing` | Testing |
| `customer_reply` | Customer Reply |
| `system` | System |

### `ALLOC_STATE_SELECTION`

| Value | Label |
|-------|-------|
| `draft` | Draft |
| `confirmed` | Confirmed |
| `done` | Done |
| `cancelled` | Cancelled |

### `APPENDIX_STATE_SELECTION`

| Value | Label |
|-------|-------|
| `draft` | Draft |
| `waiting_approval` | Waiting Approval |
| `approved` | Approved |
| `effective` | Effective |
| `cancelled` | Cancelled |

### `APPENDIX_TYPE_SELECTION`

| Value | Label |
|-------|-------|
| `scope_change` | Scope Change |
| `value_change` | Value Change |
| `timeline_extension` | Timeline Extension |
| `general_update` | General Update |

### `APPROVAL_STATE_SELECTION`

| Value | Label |
|-------|-------|
| `not_required` | Not Required |
| `draft` | Draft |
| `waiting` | Waiting Approval |
| `approved` | Approved |
| `rejected` | Rejected |
| `cancelled` | Cancelled |

### `APPROVAL_TYPE_SELECTION`

| Value | Label |
|-------|-------|
| `deal_approval` | Deal Approval |
| `trip_approval` | Business Trip Approval |
| `contract_approval` | Contract Approval |
| `appendix_approval` | Contract Appendix Approval |
| `change_request_approval` | Project Change Request Approval |
| `timesheet_approval` | Timesheet Approval |
| `asset_request_approval` | Asset Request Approval |

### `APPROVER_TYPE_SELECTION`

| Value | Label |
|-------|-------|
| `specific_user` | Specific User |
| `group` | Group |
| `employee_manager` | Employee Manager |

### `ARTICLE_AUDIENCE_SELECTION`

| Value | Label |
|-------|-------|
| `all` | All Employees |
| `delivery` | Delivery Team |
| `support` | Support Team |
| `management` | Management |
| `customer` | Customer Facing |

### `ARTICLE_STATE_SELECTION`

| Value | Label |
|-------|-------|
| `draft` | Draft |
| `review` | In Review |
| `published` | Published |
| `archived` | Archived |

### `ARTICLE_TYPE_SELECTION`

| Value | Label |
|-------|-------|
| `sop` | SOP |
| `faq` | FAQ |
| `best_practice` | Best Practice |
| `known_issue` | Known Issue |
| `coding_standard` | Coding Standard |
| `guide` | Guide |
| `checklist` | Checklist |
| `other` | Other |

### `AVAILABILITY_STATUS_SELECTION`

| Value | Label |
|-------|-------|
| `available` | Available |
| `partial` | Partially Available |
| `allocated` | Fully Allocated |
| `leave` | On Leave |
| `training` | Training |
| `resigned` | Resigned |

### `CHANGE_TYPE_SELECTION`

| Value | Label |
|-------|-------|
| `add` | Add New Scope |
| `update` | Update Existing Scope |
| `remove` | Remove Scope |

### `CHARGE_TYPE_SELECTION`

| Value | Label |
|-------|-------|
| `billable` | Billable |
| `non_billable` | Non-billable |
| `investment` | Investment |

### `COMMERCIAL_STATUS_SELECTION`

| Value | Label |
|-------|-------|
| `draft` | Draft |
| `qualification` | Qualification |
| `surveying` | Surveying |
| `estimating` | Estimating |
| `waiting_approval` | Waiting Approval |
| `quoted` | Quoted |
| `won` | Won |
| `lost` | Lost |

### `COMPLEXITY_SELECTION`

| Value | Label |
|-------|-------|
| `low` | Low |
| `medium` | Medium |
| `high` | High |

### `CONTRACT_STATE_SELECTION`

| Value | Label |
|-------|-------|
| `draft` | Draft |
| `waiting_approval` | Waiting Approval |
| `approved` | Approved |
| `active` | Active |
| `in_progress` | In Progress |
| `done` | Completed |
| `cancelled` | Cancelled |
| `closed` | Closed |

### `CONTRACT_TYPE_SELECTION`

| Value | Label |
|-------|-------|
| `implementation` | Implementation Contract |
| `support` | Support/Maintenance Contract |
| `training` | Training Contract |
| `consulting` | Consulting Contract |
| `license` | License Contract |
| `other` | Other |

### `COOPERATION_STATUS_SELECTION`

| Value | Label |
|-------|-------|
| `new` | New |
| `negotiating` | Negotiating |
| `active` | Active |
| `on_hold` | On Hold |
| `closed` | Closed |

### `COST_TYPE_SELECTION`

| Value | Label |
|-------|-------|
| `labor` | Labor |
| `travel` | Travel |
| `subcontract` | Subcontract |
| `license` | License / Software |
| `expense` | General Expense |
| `other` | Other |

### `CR_STATE_SELECTION`

| Value | Label |
|-------|-------|
| `draft` | Draft |
| `analysis` | Impact Analysis |
| `approved` | Approved |
| `rejected` | Rejected |
| `implemented` | Implemented |
| `cancelled` | Cancelled |

### `CUSTOMER_RANK_LEVEL_SELECTION`

| Value | Label |
|-------|-------|
| `strategic` | Strategic |
| `vip` | VIP |
| `normal` | Normal |
| `low` | Low |

### `DEBT_RISK_LEVEL_SELECTION`

| Value | Label |
|-------|-------|
| `low` | Low |
| `medium` | Medium |
| `high` | High |

### `DOCUMENT_STATE_SELECTION`

| Value | Label |
|-------|-------|
| `draft` | Draft |
| `review` | In Review |
| `approved` | Approved |
| `published` | Published |
| `archived` | Archived |
| `cancelled` | Cancelled |

### `ESTIMATE_STATE_SELECTION`

| Value | Label |
|-------|-------|
| `draft` | Draft |
| `review` | In Review |
| `approved` | Approved |
| `rejected` | Rejected |
| `archived` | Archived |

### `EXPENSE_CATEGORY_SELECTION`

| Value | Label |
|-------|-------|
| `transport` | Transport |
| `hotel` | Hotel |
| `allowance` | Allowance |
| `meal` | Meal |
| `entertainment` | Entertainment |
| `visa` | Visa / Documents |
| `other` | Other |

### `EXPENSE_SOURCE_SELECTION`

| Value | Label |
|-------|-------|
| `estimated` | Estimated |
| `actual` | Actual |
| `adjustment` | Adjustment |

### `FINANCE_HEALTH_SELECTION`

| Value | Label |
|-------|-------|
| `green` | Green |
| `yellow` | Yellow |
| `red` | Red |

### `FINANCE_STATE_SELECTION`

| Value | Label |
|-------|-------|
| `draft` | Draft |
| `active` | Active |
| `on_hold` | On Hold |
| `done` | Done |
| `closed` | Closed |

### `HEALTH_STATUS_SELECTION`

| Value | Label |
|-------|-------|
| `green` | Green |
| `yellow` | Yellow |
| `red` | Red |

### `ISSUE_PRIORITY_SELECTION`

| Value | Label |
|-------|-------|
| `low` | Low |
| `medium` | Medium |
| `high` | High |
| `critical` | Critical |

### `ISSUE_STATE_SELECTION`

| Value | Label |
|-------|-------|
| `open` | Open |
| `in_progress` | In Progress |
| `resolved` | Resolved |
| `closed` | Closed |
| `cancelled` | Cancelled |

### `ISSUE_TYPE_SELECTION`

| Value | Label |
|-------|-------|
| `issue` | Issue |
| `risk` | Risk |
| `blocker` | Blocker |
| `dependency` | Dependency |
| `customer_pending` | Customer Pending |

### `LINE_STATE_SELECTION`

| Value | Label |
|-------|-------|
| `draft` | Draft |
| `submitted` | Submitted |
| `approved` | Approved |
| `rejected` | Rejected |

### `LINE_TYPE_SELECTION`

| Value | Label |
|-------|-------|
| `contract_value` | Contract Value |
| `appendix_value` | Appendix Value |
| `invoice` | Invoice |
| `collection` | Collection |
| `adjustment` | Adjustment |

### `LINK_MODEL_SELECTION`

| Value | Label |
|-------|-------|

### `MANAGER_LEVEL_SELECTION`

| Value | Label |
|-------|-------|
| `1` | Direct Manager |
| `2` | Manager Level 2 |

### `MEMBER_ROLE_SELECTION`

| Value | Label |
|-------|-------|
| `pm` | Project Manager |
| `ba` | BA |
| `dev` | Developer |
| `qa` | QA |
| `trainer` | Trainer |
| `support` | Support |
| `sales` | Sales |
| `other` | Other |

### `MILESTONE_STATE_SELECTION`

| Value | Label |
|-------|-------|
| `draft` | Draft |
| `waiting` | Waiting |
| `in_progress` | In Progress |
| `done` | Done |
| `delayed` | Delayed |
| `cancelled` | Cancelled |

### `MILESTONE_TYPE_SELECTION`

| Value | Label |
|-------|-------|
| `kickoff` | Kickoff |
| `survey` | Survey |
| `analysis` | Analysis / Blueprint |
| `development` | Development |
| `uat` | UAT |
| `training` | Training |
| `go_live` | Go Live |
| `acceptance` | Acceptance |
| `other` | Other |

### `OT_STATE_SELECTION`

| Value | Label |
|-------|-------|
| `draft` | Draft |
| `submitted` | Submitted |
| `approved` | Approved |
| `rejected` | Rejected |
| `cancelled` | Cancelled |

### `PARTNER_STATUS_SELECTION`

| Value | Label |
|-------|-------|
| `prospect` | Prospect |
| `active` | Active Customer |
| `inactive` | Inactive |
| `blacklisted` | Blacklisted |

### `PAYMENT_STATE_SELECTION`

| Value | Label |
|-------|-------|
| `draft` | Draft |
| `waiting` | Waiting |
| `partial` | Partially Received |
| `paid` | Paid |
| `cancelled` | Cancelled |

### `PAYMENT_TYPE_SELECTION`

| Value | Label |
|-------|-------|
| `percent` | By Percentage |
| `fixed` | Fixed Amount |

### `PERIOD_TYPE_SELECTION`

| Value | Label |
|-------|-------|
| `weekly` | Weekly |
| `monthly` | Monthly |
| `manual` | Manual |

### `PLAN_STATE_SELECTION`

| Value | Label |
|-------|-------|
| `draft` | Draft |
| `active` | Active |
| `done` | Done |
| `cancelled` | Cancelled |

### `PRESALES_COST_STATE_SELECTION`

| Value | Label |
|-------|-------|
| `draft` | Draft |
| `confirmed` | Confirmed |
| `cancelled` | Cancelled |

### `PRIORITY_SELECTION`

| Value | Label |
|-------|-------|
| `highest` | Highest |
| `high` | High |
| `normal` | Normal |
| `low` | Low |

### `PROJECT_STATE_SELECTION`

| Value | Label |
|-------|-------|
| `draft` | Draft |
| `ready` | Ready for Delivery |
| `in_progress` | In Progress |
| `on_hold` | On Hold |
| `uat` | UAT |
| `done` | Completed |
| `closed` | Closed |
| `cancelled` | Cancelled |

### `PROJECT_TYPE_SELECTION`

| Value | Label |
|-------|-------|
| `implementation` | Implementation |
| `customization` | Customization |
| `support` | Support |
| `training` | Training |
| `consulting` | Consulting |
| `internal` | Internal |

### `RATING_SELECTION`

| Value | Label |
|-------|-------|
| `1` | 1 - Poor |
| `2` | 2 - Fair |
| `3` | 3 - Good |
| `4` | 4 - Very Good |
| `5` | 5 - Excellent |

### `REQUESTED_BY_SELECTION`

| Value | Label |
|-------|-------|
| `customer` | Customer |
| `internal` | Internal |

### `REQUEST_STATE_SELECTION`

| Value | Label |
|-------|-------|
| `draft` | Draft |
| `submitted` | Submitted |
| `approved` | Approved |
| `allocated` | Allocated |
| `rejected` | Rejected |
| `cancelled` | Cancelled |

### `REQUEST_URGENCY_SELECTION`

| Value | Label |
|-------|-------|
| `critical` | Critical |
| `high` | High |
| `normal` | Normal |
| `low` | Low |

### `REQUIREMENT_STATE_SELECTION`

| Value | Label |
|-------|-------|
| `draft` | Draft |
| `confirmed` | Confirmed |
| `cancelled` | Cancelled |

### `RESOURCE_TYPE_SELECTION`

| Value | Label |
|-------|-------|
| `employee` | Employee |
| `freelancer` | Freelancer |
| `vendor` | Vendor |
| `intern` | Intern |

### `REVENUE_STATE_SELECTION`

| Value | Label |
|-------|-------|
| `planned` | Planned |
| `invoiced` | Invoiced |
| `partial` | Partially Collected |
| `collected` | Collected |
| `cancelled` | Cancelled |

### `REVIEW_STATUS_SELECTION`

| Value | Label |
|-------|-------|
| `pending` | Pending |
| `approved` | Approved |
| `rejected` | Rejected |
| `comment` | Comment Only |

### `SCOPE_STATE_SELECTION`

| Value | Label |
|-------|-------|
| `draft` | Draft |
| `ready` | Ready |
| `in_progress` | In Progress |
| `done` | Done |
| `cancelled` | Cancelled |

### `SCOPE_TYPE_SELECTION`

| Value | Label |
|-------|-------|
| `implementation` | Implementation |
| `customization` | Customization |
| `integration` | Integration |
| `migration` | Migration |
| `training` | Training |
| `support` | Support |
| `other` | Other |

### `SEVERITY_SELECTION`

| Value | Label |
|-------|-------|
| `critical` | Critical |
| `high` | High |
| `medium` | Medium |
| `low` | Low |

### `SHEET_STATE_SELECTION`

| Value | Label |
|-------|-------|
| `draft` | Draft |
| `submitted` | Submitted |
| `approved` | Approved |
| `rejected` | Rejected |
| `cancelled` | Cancelled |

### `SKILL_CATEGORY_SELECTION`

| Value | Label |
|-------|-------|
| `technical` | Technical |
| `functional` | Functional |
| `domain` | Domain |
| `tool` | Tool |
| `soft` | Soft Skill |
| `other` | Other |

### `SKILL_LEVEL_SELECTION`

| Value | Label |
|-------|-------|
| `1` | 1 - Beginner |
| `2` | 2 - Basic |
| `3` | 3 - Intermediate |
| `4` | 4 - Advanced |
| `5` | 5 - Expert |

### `SOURCE_TYPE_SELECTION`

| Value | Label |
|-------|-------|
| `timesheet` | Timesheet |
| `trip` | Business Trip |
| `manual` | Manual |
| `vendor_bill` | Vendor Bill |
| `expense_claim` | Expense Claim |
| `other` | Other |

### `STEP_STATE_SELECTION`

| Value | Label |
|-------|-------|
| `pending` | Pending |
| `approved` | Approved |
| `rejected` | Rejected |
| `cancelled` | Cancelled |

### `SUPPORT_LEVEL_SELECTION`

| Value | Label |
|-------|-------|
| `standard` | Standard |
| `premium` | Premium |
| `vip` | VIP |

### `TAG_GROUP_SELECTION`

| Value | Label |
|-------|-------|
| `module` | Module |
| `technology` | Technology |
| `process` | Process |
| `domain` | Domain |
| `other` | Other |

### `TICKET_CATEGORY_SELECTION`

| Value | Label |
|-------|-------|
| `functional` | Functional |
| `technical` | Technical |
| `database` | Database |
| `integration` | Integration |
| `infrastructure` | Infrastructure |
| `training` | Training |

### `TICKET_TYPE_SELECTION`

| Value | Label |
|-------|-------|
| `bug` | Bug |
| `issue` | Issue |
| `question` | Question |
| `training` | Training |
| `support` | Support |
| `change_request` | Change Request |
| `other` | Other |

### `TRAINING_RESULT_SELECTION`

| Value | Label |
|-------|-------|
| `passed` | Passed |
| `failed` | Failed |
| `in_progress` | In Progress |
| `cancelled` | Cancelled |

### `TRIP_PURPOSE_SELECTION`

| Value | Label |
|-------|-------|
| `kickoff` | Kickoff |
| `requirement` | Requirement Survey |
| `implementation` | Implementation |
| `uat` | UAT |
| `golive` | Go-live |
| `training` | Training |
| `support` | Support |
| `warranty` | Warranty |
| `meeting` | Meeting |
| `other` | Other |

### `TRIP_STATE_SELECTION`

| Value | Label |
|-------|-------|
| `draft` | Draft |
| `waiting_approval` | Waiting Approval |
| `approved` | Approved |
| `in_progress` | In Progress |
| `done` | Done |
| `cancelled` | Cancelled |

### `TRIP_TYPE_SELECTION`

| Value | Label |
|-------|-------|
| `project_onsite` | Project Onsite |
| `customer_meeting` | Customer Meeting |
| `survey` | Survey |
| `training` | Training |
| `support` | Support |
| `internal` | Internal |
| `other` | Other |

### `TRIP_WORK_TYPE_SELECTION`

| Value | Label |
|-------|-------|
| `project_delivery` | Project Delivery |
| `presales` | Presales |
| `support` | Support |
| `internal` | Internal |
| `other` | Other |

### `WARRANTY_RESULT_SELECTION`

| Value | Label |
|-------|-------|
| `fixed` | Fixed |
| `workaround` | Workaround |
| `guidance` | Guidance |
| `duplicate` | Duplicate |
| `cannot_reproduce` | Cannot Reproduce |
| `rejected` | Rejected |

### `WORK_TYPE_SELECTION`

| Value | Label |
|-------|-------|
| `project_delivery` | Project Delivery |
| `support` | Support |
| `internal` | Internal |
| `presales` | Presales |
| `training` | Training |
| `leave_related` | Leave Related |
| `other` | Other |

## 6. dcg_master_data

**Depends:** `base`, `mail`, `hr`, `resource`

**Models:** 15 new

### `dcg.acceptance.type`
*Acceptance Type*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `description` | Text |  | Description |  |  |

### `dcg.alert.rule`
*Alert Rule*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `name` | Char |  | Rule Name | ✓ |  |
| `rule_type` | Selection | Selection |  |  |  |
| `model_name` | Char |  | Target Model |  |  |
| `condition_json` | Text |  |  |  |  |
| `recipient_group_ids` | Many2many | `res.groups` | Recipient Groups |  |  |
| `active` | Boolean |  |  |  |  |
| `note` | Text |  | Internal Note |  |  |

### `dcg.master.mixin`
*DCG Master Mixin*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `name` | Char |  | Name | ✓ |  |
| `code` | Char |  | Code |  |  |
| `sequence` | Integer |  | Sequence |  |  |
| `active` | Boolean |  | Active |  |  |
| `note` | Text |  | Internal Note |  |  |

### `dcg.contract.appendix.type`
*Contract Appendix Type*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `description` | Text |  | Description |  |  |

### `dcg.contract.type`
*Contract Type*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `description` | Text |  | Description |  |  |

### `dcg.cost.center`
*Cost Center*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `name` | Char |  | Cost Center | ✓ |  |
| `code` | Char |  | Code |  |  |
| `manager_id` | Many2one | `hr.employee` | Manager |  |  |
| `sequence` | Integer |  |  |  |  |
| `active` | Boolean |  |  |  |  |
| `note` | Text |  | Internal Note |  |  |

### `dcg.customer.industry`
*Customer Industry*

*(no custom fields)*

### `dcg.customer.source`
*Customer Source*

*(no custom fields)*

### `dcg.expense.type`
*Expense Type*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `name` | Char |  | Expense Type | ✓ |  |
| `code` | Char |  | Code |  |  |
| `expense_group` | Selection | Selection |  |  |  |
| `is_billable` | Boolean |  | Billable |  |  |
| `sequence` | Integer |  |  |  |  |
| `active` | Boolean |  |  |  |  |
| `note` | Text |  | Internal Note |  |  |

### `dcg.kpi.target`
*KPI Target*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `name` | Char |  | KPI Name | ✓ |  |
| `target_type` | Selection | Selection |  |  |  |
| `department_id` | Many2one | `hr.department` | Department |  |  |
| `owner_id` | Many2one | `hr.employee` | Owner |  |  |
| `period_type` | Selection | Selection |  |  |  |
| `target_value` | Float |  | Target Value | ✓ |  |
| `unit` | Char |  | Unit |  |  |
| `active` | Boolean |  |  |  |  |
| `note` | Text |  | Internal Note |  |  |

### `dcg.service.catalog`
*Service Catalog*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `name` | Char |  | Service Name | ✓ |  |
| `code` | Char |  | Service Code |  |  |
| `service_type` | Selection | Selection |  |  |  |
| `description` | Text |  | Description |  |  |
| `sequence` | Integer |  |  |  |  |
| `active` | Boolean |  |  |  |  |
| `note` | Text |  | Internal Note |  |  |

### `dcg.sla.policy`
*SLA Policy*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `name` | Char |  | Policy Name | ✓ |  |
| `code` | Char |  | Policy Code |  |  |
| `ticket_type_id` | Many2one | `dcg.ticket.type` | Ticket Type |  |  |
| `severity_id` | Many2one | `dcg.ticket.severity` | Severity |  |  |
| `response_hours` | Float |  | Response Hours | ✓ |  |
| `resolution_hours` | Float |  | Resolution Hours | ✓ |  |
| `working_calendar_id` | Many2one | `resource.calendar` | Working Calendar |  |  |
| `active` | Boolean |  |  |  |  |
| `note` | Text |  | Internal Note |  |  |

### `dcg.ticket.priority`
*Ticket Priority*

*(no custom fields)*

### `dcg.ticket.severity`
*Ticket Severity*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `name` | Char |  | Severity | ✓ |  |
| `code` | Char |  | Code |  |  |
| `sequence` | Integer |  |  |  |  |
| `response_hours_default` | Float |  | Default Response Hours |  |  |
| `resolution_hours_default` | Float |  | Default Resolution Hours |  |  |
| `active` | Boolean |  |  |  |  |
| `note` | Text |  | Internal Note |  |  |

### `dcg.ticket.type`
*Ticket Type*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `description` | Text |  | Description |  |  |

## 7. dcg_approval_matrix

**Depends:** `base`, `mail`, `hr`, `dcg_master_data`

**Models:** 6 new

### `dcg.approval.log`
*Approval Log*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `request_id` | Many2one | `dcg.approval.request` | Request | ✓ |  |
| `sequence` | Integer |  | Order |  |  |
| `step_no` | Integer |  | Step No. |  |  |
| `matrix_line_id` | Many2one | `dcg.approval.matrix.line` | Matrix Line |  |  |
| `request_step_id` | Many2one | `dcg.approval.request.step` | Request Step |  |  |
| `approver_id` | Many2one | `res.users` | Performed By |  |  |
| `action` | Selection | `ACTION_SELECTION` | Action | ✓ |  |
| `action_date` | Datetime |  | Action Date | ✓ |  |
| `from_state` | Char |  | From State |  |  |
| `to_state` | Char |  | To State |  |  |
| `note` | Text |  | Note / Reason |  |  |

### `dcg.approval.matrix`
*Approval Matrix*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `name` | Char |  | Matrix Name | ✓ |  |
| `code` | Char |  | Code |  |  |
| `sequence` | Integer |  | Priority |  |  |
| `active` | Boolean |  |  |  |  |
| `approval_type` | Selection | `APPROVAL_TYPE_SELECTION` | Approval Type | ✓ |  |
| `company_id` | Many2one | `res.company` | Company |  |  |
| `department_id` | Many2one | `hr.department` | Department |  |  |
| `amount_from` | Float |  | Amount From |  |  |
| `amount_to` | Float |  | Amount To |  |  |
| `currency_id` | Many2one | `res.currency` | Currency |  |  |
| `description` | Text |  | Description |  |  |
| `note` | Text |  | Internal Note |  |  |
| `line_ids` | One2many | `dcg.approval.matrix.line` | Approval Steps |  |  |
| `line_count` | Integer |  | Step Count |  | C |

### `dcg.approval.matrix.line`
*Approval Matrix Line*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `matrix_id` | Many2one | `dcg.approval.matrix` | Matrix | ✓ |  |
| `sequence` | Integer |  | Step | ✓ |  |
| `name` | Char |  | Step Name |  |  |
| `active` | Boolean |  |  |  |  |
| `approver_type` | Selection | `APPROVER_TYPE_SELECTION` | Approver Type | ✓ |  |
| `user_id` | Many2one | `res.users` | Specific User |  |  |
| `group_id` | Many2one | `res.groups` | Group |  |  |
| `manager_level` | Selection | `MANAGER_LEVEL_SELECTION` | Manager Level |  |  |
| `min_amount` | Float |  | Min Amount |  |  |
| `max_amount` | Float |  | Max Amount |  |  |
| `condition_json` | Text |  |  |  |  |
| `stop_if_rejected` | Boolean |  | Stop If Rejected |  |  |
| `matrix_approval_type` | Selection | Selection | Approval Type |  | R |
| `matrix_company_id` | Many2one | `related:matrix_id.company_id` | Company |  | R |

### `dcg.contract`
*DCG Approval Mixin*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `approval_request_id` | Many2one | `dcg.approval.request` | Approval Request |  |  |
| `approval_state` | Selection | `APPROVAL_STATE_SELECTION` | Approval Status |  |  |
| `approval_submitted_by` | Many2one | `res.users` | Submitted By |  |  |
| `approval_submitted_date` | Datetime |  | Submitted On |  |  |
| `approval_last_action_by` | Many2one | `res.users` | Approval Last Action By |  |  |
| `approval_last_action_date` | Datetime |  | Approval Last Action On |  |  |
| `approval_reject_reason` | Text |  | Approval Reject Reason |  |  |
| `approval_readonly` | Boolean |  | Locked by Approval |  | C |

### `dcg.approval.request`
*Approval Request*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `name` | Char |  | Reference | ✓ |  |
| `active` | Boolean |  |  |  |  |
| `company_id` | Many2one | `res.company` | Company |  |  |
| `approval_type` | Selection | `APPROVAL_TYPE_SELECTION` | Approval Type | ✓ |  |
| `matrix_id` | Many2one | `dcg.approval.matrix` | Matrix |  |  |
| `request_date` | Datetime |  | Submitted On |  |  |
| `approved_date` | Datetime |  | Approved On |  |  |
| `rejected_date` | Datetime |  | Rejected On |  |  |
| `cancelled_date` | Datetime |  | Cancelled On |  |  |
| `amount_total` | Float |  | Amount |  |  |
| `currency_id` | Many2one | `res.currency` | Currency |  |  |
| `note` | Text |  | Submission Note |  |  |
| `requester_id` | Many2one | `res.users` | Requester | ✓ |  |
| `requester_employee_id` | Many2one | `hr.employee` | Requester Employee |  |  |
| `requester_department_id` | Many2one | `hr.department` | Requester Department |  |  |
| `res_model` | Char |  | Source Model | ✓ |  |
| `res_id` | Integer |  | Source ID | ✓ |  |
| `res_name` | Char |  | Source Name |  |  |
| `source_ref` | Char |  | Source |  | C |
| `state` | Selection | `REQUEST_STATE_SELECTION` | Status | ✓ |  |
| `current_step` | Integer |  | Current Step |  |  |
| `current_step_id` | Many2one | `dcg.approval.request.step` | Current Step Record |  |  |
| `current_line_id` | Many2one | `dcg.approval.matrix.line` | Current Matrix Line |  |  |
| `current_approver_user_ids` | Many2many | `res.users` | Current Approvers |  |  |
| `participant_user_ids` | Many2many | `res.users` | Participants |  |  |
| `last_action_by` | Many2one | `res.users` | Last Action By |  |  |
| `last_action_date` | Datetime |  | Last Action On |  |  |
| `reject_reason` | Text |  | Reject Reason |  |  |
| `cancel_reason` | Text |  | Cancel Reason |  |  |
| `result_note` | Text |  | Result Note |  |  |
| `final_approver_id` | Many2one | `res.users` | Final Approver |  |  |
| `step_ids` | One2many | `dcg.approval.request.step` | Steps |  |  |
| `log_ids` | One2many | `dcg.approval.log` | Logs |  |  |
| `step_count` | Integer |  | Step Count |  | C |
| `log_count` | Integer |  | Log Count |  | C |
| `can_current_user_approve` | Boolean |  | Can Approve |  | C |
| `can_current_user_cancel` | Boolean |  | Can Cancel |  | C |

### `dcg.approval.request.step`
*Approval Request Step*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `request_id` | Many2one | `dcg.approval.request` | Request | ✓ |  |
| `sequence` | Integer |  | Step No. | ✓ |  |
| `matrix_line_id` | Many2one | `dcg.approval.matrix.line` | Matrix Line |  |  |
| `name` | Char |  | Step Name |  |  |
| `approver_type` | Selection | Selection |  |  |  |
| `approver_user_ids` | Many2many | `res.users` | Candidate Approvers |  |  |
| `min_amount` | Float |  | Min Amount |  |  |
| `max_amount` | Float |  | Max Amount |  |  |
| `state` | Selection | `STEP_STATE_SELECTION` | Status | ✓ |  |
| `approved_by` | Many2one | `res.users` | Approved By |  |  |
| `approved_date` | Datetime |  | Approved Date |  |  |
| `rejected_by` | Many2one | `res.users` | Rejected By |  |  |
| `rejected_date` | Datetime |  | Rejected Date |  |  |
| `note` | Text |  | Note |  |  |

## 8. dcg_crm_presales

**Depends:** `crm`, `sale`, `contacts`, `mail`, `dcg_master_data`, `dcg_approval_matrix`

**Models:** 5 new + 2 extend

### `dcg.crm.estimate`
*CRM Presales Estimate*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `name` | Char |  | Reference | ✓ |  |
| `lead_id` | Many2one | `crm.lead` | Opportunity | ✓ |  |
| `partner_id` | Many2one | `related:lead_id.partner_id` | Customer |  | R |
| `version` | Char |  | Version | ✓ |  |
| `estimate_date` | Date |  | Estimate Date |  |  |
| `owner_id` | Many2one | `res.users` | Estimated By |  |  |
| `currency_id` | Many2one | `res.currency` | Currency |  |  |
| `state` | Selection | `ESTIMATE_STATE_SELECTION` | Status |  |  |
| `is_current_version` | Boolean |  | Current Version |  |  |
| `is_approved_version` | Boolean |  | Approved Version |  |  |
| `line_ids` | One2many | `dcg.crm.estimate.line` | Estimate Lines |  |  |
| `line_count` | Integer |  | Line Count |  | C |
| `estimated_ba_hours` | Float |  | BA Hours |  | C |
| `estimated_dev_hours` | Float |  | Dev Hours |  | C |
| `estimated_test_hours` | Float |  | Test Hours |  | C |
| `estimated_pm_hours` | Float |  | PM Hours |  | C |
| `estimated_support_hours` | Float |  | Support Hours |  | C |
| `estimated_other_hours` | Float |  | Other Hours |  | C |
| `total_estimated_hours` | Float |  | Total Hours |  | C |
| `estimated_cost` | Monetary |  | Estimated Cost |  |  |
| `estimated_revenue` | Monetary |  | Estimated Revenue |  |  |
| `estimated_margin` | Monetary |  | Estimated Margin |  | C |
| `estimated_margin_rate` | Float |  |  |  |  |
| `estimated_timeline_days` | Integer |  |  |  |  |
| `estimated_timeline_note` | Text |  | Timeline Note |  |  |
| `scope_summary` | Html |  | Scope Summary |  |  |
| `assumption_note` | Html |  | Assumptions |  |  |
| `exclusion_note` | Html |  | Exclusions |  |  |
| `risk_note` | Text |  | Risk Note |  |  |
| `pricing_note` | Text |  | Pricing Note |  |  |
| `approval_required` | Boolean |  | Approval Required |  |  |
| `approval_request_id` | Many2one | `dcg.approval.request` | Approval Request |  |  |
| `approval_state` | Selection | Selection |  |  |  |
| `quotation_id` | Many2one | `sale.order` | Quotation |  |  |
| `converted_to_quotation` | Boolean |  | Converted to Quotation |  |  |

### `dcg.crm.estimate.line`
*CRM Estimate Line*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `estimate_id` | Many2one | `dcg.crm.estimate` | Estimate | ✓ |  |
| `scope_id` | Many2one | `dcg.crm.solution.scope` | Scope Item |  |  |
| `lead_id` | Many2one | `related:estimate_id.lead_id` | Opportunity |  | R |
| `sequence` | Integer |  |  |  |  |
| `name` | Char |  | Line | ✓ |  |
| `service_catalog_id` | Many2one | `dcg.service.catalog` | Service |  |  |
| `ba_hours` | Float |  | BA Hours |  |  |
| `dev_hours` | Float |  | Dev Hours |  |  |
| `test_hours` | Float |  | Test Hours |  |  |
| `pm_hours` | Float |  | PM Hours |  |  |
| `support_hours` | Float |  | Support Hours |  |  |
| `other_hours` | Float |  | Other Hours |  |  |
| `total_hours` | Float |  | Total Hours |  | C |
| `currency_id` | Many2one | `related:estimate_id.currency_id` | Currency |  | R |
| `cost_amount` | Monetary |  | Cost |  |  |
| `revenue_amount` | Monetary |  | Revenue |  |  |
| `timeline_days` | Integer |  |  |  |  |
| `note` | Text |  | Note |  |  |

### `crm.lead` *(extend)*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `opportunity_code` | Char |  | Opportunity Code |  |  |
| `account_manager_id` | Many2one | `res.users` | Account Manager |  |  |
| `presales_owner_id` | Many2one | `res.users` | Presales Owner |  |  |
| `presales_team_member_ids` | Many2many | `res.users` | Presales Team |  |  |
| `lead_source_id` | Many2one | `dcg.customer.source` | Lead Source |  |  |
| `industry_id` | Many2one | `dcg.customer.industry` | DCG Industry |  |  |
| `currency_id` | Many2one | `res.currency` | Currency |  |  |
| `customer_need_summary` | Html |  | Customer Need Summary |  |  |
| `pain_point` | Html |  | Pain Point |  |  |
| `business_goal` | Html |  | Business Goal |  |  |
| `current_system` | Html |  | Current System |  |  |
| `competitor_info` | Text |  | Competitor Info |  |  |
| `risk_note` | Text |  | Risk Note |  |  |
| `decision_deadline` | Date |  | Decision Deadline |  |  |
| `expected_go_live_date` | Date |  | Expected Go-Live Date |  |  |
| `solution_scope_summary` | Html |  | Solution Scope Summary |  |  |
| `estimated_ba_hours` | Float |  | BA Hours |  |  |
| `estimated_dev_hours` | Float |  | Dev Hours |  |  |
| `estimated_test_hours` | Float |  | Test Hours |  |  |
| `estimated_pm_hours` | Float |  | PM Hours |  |  |
| `estimated_support_hours` | Float |  | Support Hours |  |  |
| `estimated_timeline_days` | Integer |  |  |  |  |
| `estimated_cost` | Monetary |  | Estimated Cost |  |  |
| `estimated_revenue` | Monetary |  | Estimated Revenue |  |  |
| `estimated_margin` | Monetary |  | Estimated Margin |  | C |
| `estimated_margin_rate` | Float |  |  |  |  |
| `presales_cost_amount` | Monetary |  | Presales Cost Total |  | C |
| `deal_approval_required` | Boolean |  | Approval Required |  |  |
| `deal_submit_note` | Text |  | Approval Submission Note |  |  |
| `commercial_status` | Selection | `COMMERCIAL_STATUS_SELECTION` | Commercial Status |  |  |
| `requirement_ids` | One2many | `dcg.crm.requirement` | Requirement Surveys |  |  |
| `solution_scope_ids` | One2many | `dcg.crm.solution.scope` | Solution Scope |  |  |
| `estimate_ids` | One2many | `dcg.crm.estimate` | Estimates |  |  |
| `presales_cost_ids` | One2many | `dcg.crm.presales.cost` | Presales Costs |  |  |
| `requirement_count` | Integer |  |  |  | C |
| `solution_scope_count` | Integer |  |  |  | C |
| `estimate_count` | Integer |  |  |  | C |
| `presales_cost_count` | Integer |  |  |  | C |
| `quotation_count` | Integer |  |  |  | C |
| `latest_estimate_id` | Many2one | `dcg.crm.estimate` | Latest Estimate |  |  |
| `approved_estimate_id` | Many2one | `dcg.crm.estimate` | Approved Estimate |  |  |
| `quotation_id` | Many2one | `sale.order` | Primary Quotation |  |  |
| `quotation_ready` | Boolean |  | Ready for Quotation |  | C |
| `handover_note` | Html |  | Handover Note |  |  |

### `dcg.crm.presales.cost`
*CRM Presales Cost*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `name` | Char |  | Description | ✓ |  |
| `lead_id` | Many2one | `crm.lead` | Opportunity | ✓ |  |
| `partner_id` | Many2one | `related:lead_id.partner_id` | Customer |  | R |
| `expense_type_id` | Many2one | `dcg.expense.type` | Expense Type | ✓ |  |
| `expense_date` | Date |  | Date | ✓ |  |
| `description` | Text |  | Description |  |  |
| `amount` | Monetary |  | Amount | ✓ |  |
| `currency_id` | Many2one | `res.currency` | Currency | ✓ |  |
| `billable_to_customer` | Boolean |  | Billable to Customer |  |  |
| `attachment_ids` | Many2many | `ir.attachment` | Attachments / Receipts |  |  |
| `state` | Selection | `PRESALES_COST_STATE_SELECTION` | Status |  |  |

### `dcg.crm.requirement`
*CRM Requirement Survey*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `name` | Char |  | Reference | ✓ |  |
| `lead_id` | Many2one | `crm.lead` | Opportunity | ✓ |  |
| `partner_id` | Many2one | `res.partner` | Customer |  | R |
| `survey_date` | Date |  | Survey Date |  |  |
| `owner_id` | Many2one | `res.users` | Owner |  |  |
| `version` | Char |  | Version |  |  |
| `state` | Selection | `REQUIREMENT_STATE_SELECTION` | Status |  |  |
| `current_system` | Html |  | Current System |  |  |
| `pain_point` | Html |  | Pain Point |  |  |
| `business_goal` | Html |  | Business Goal |  |  |
| `scope_summary` | Html |  | Scope Summary |  |  |
| `department_involved` | Text |  | Departments Involved |  |  |
| `input_data_desc` | Html |  | Input Data Description |  |  |
| `output_data_desc` | Html |  | Output Data Description |  |  |
| `integration_requirement` | Html |  | Integration Requirement |  |  |
| `reporting_requirement` | Html |  | Reporting Requirement |  |  |
| `deployment_requirement` | Html |  | Deployment Requirement |  |  |
| `note` | Html |  | Note |  |  |
| `attachment_ids` | Many2many | `ir.attachment` | Attachments |  |  |
| `meeting_note` | Html |  | Meeting Note |  |  |
| `contact_person_ids` | Many2many | `res.partner` | Customer Contacts |  |  |

### `dcg.crm.solution.scope`
*CRM Solution Scope*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `lead_id` | Many2one | `crm.lead` | Opportunity | ✓ |  |
| `requirement_id` | Many2one | `dcg.crm.requirement` | Source Requirement |  |  |
| `sequence` | Integer |  |  |  |  |
| `name` | Char |  | Scope Item | ✓ |  |
| `service_catalog_id` | Many2one | `dcg.service.catalog` | Service |  |  |
| `scope_type` | Selection | `SCOPE_TYPE_SELECTION` | Scope Type | ✓ |  |
| `description` | Html |  | Description |  |  |
| `in_scope` | Boolean |  | In Scope |  |  |
| `estimated_complexity` | Selection | `COMPLEXITY_SELECTION` | Complexity |  |  |
| `estimated_note` | Text |  | Estimate Note |  |  |
| `active` | Boolean |  |  |  |  |

### `res.partner` *(extend)*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `is_company_customer` | Boolean |  | Target Company Customer |  |  |
| `customer_code` | Char |  | Customer Code |  |  |
| `account_manager_id` | Many2one | `res.users` | Account Manager |  |  |
| `partner_status` | Selection | `PARTNER_STATUS_SELECTION` | Customer Status |  |  |
| `dcg_industry_id` | Many2one | `dcg.customer.industry` | DCG Industry |  |  |
| `source_id` | Many2one | `dcg.customer.source` | Source |  |  |
| `customer_rank_level` | Selection | `CUSTOMER_RANK_LEVEL_SELECTION` | Customer Rank |  |  |
| `cooperation_status` | Selection | `COOPERATION_STATUS_SELECTION` | Cooperation Status |  |  |
| `debt_risk_level` | Selection | `DEBT_RISK_LEVEL_SELECTION` | Debt Risk Level |  |  |
| `support_level` | Selection | `SUPPORT_LEVEL_SELECTION` | Support Level |  |  |
| `note_internal` | Text |  | Internal Note |  |  |
| `last_presales_date` | Date |  | Last Presales Date |  |  |
| `last_contract_date` | Date |  | Last Contract Date |  |  |
| `total_opportunity_count` | Integer |  | Opportunities |  | C |
| `total_quotation_count` | Integer |  | Quotations |  | C |

## 9. dcg_contract_management

**Depends:** `sale`, `crm`, `mail`, `dcg_master_data`, `dcg_approval_matrix`, `dcg_crm_presales`

**Models:** 6 new + 2 extend

### `dcg.contract`
*Customer Contract*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `name` | Char |  | Contract Number | ✓ |  |
| `contract_code` | Char |  | Internal Code |  |  |
| `active` | Boolean |  |  |  |  |
| `company_id` | Many2one | `res.company` | Company | ✓ |  |
| `currency_id` | Many2one | `res.currency` | Currency | ✓ |  |
| `partner_id` | Many2one | `res.partner` | Customer | ✓ |  |
| `lead_id` | Many2one | `crm.lead` | Opportunity |  |  |
| `quotation_id` | Many2one | `sale.order` | Quotation |  |  |
| `estimate_id` | Many2one | `dcg.crm.estimate` | Source Estimate |  |  |
| `account_manager_id` | Many2one | `res.users` | Account Manager |  |  |
| `presales_owner_id` | Many2one | `res.users` | Presales Owner |  |  |
| `project_manager_id` | Many2one | `res.users` | Project Manager |  |  |
| `delivery_owner_id` | Many2one | `res.users` | Delivery Owner |  |  |
| `contract_type` | Selection | `CONTRACT_TYPE_SELECTION` | Contract Type |  |  |
| `sign_date` | Date |  | Signed Date |  |  |
| `effective_date` | Date |  | Effective Date |  |  |
| `start_date` | Date |  | Start Date |  |  |
| `end_date` | Date |  | End Date |  |  |
| `warranty_end_date` | Date |  | Warranty End Date |  |  |
| `amount_untaxed` | Monetary |  | Amount Untaxed |  |  |
| `tax_amount` | Monetary |  | Tax Amount |  |  |
| `amount_total` | Monetary |  | Total Amount |  |  |
| `expected_cost` | Monetary |  | Expected Cost |  |  |
| `expected_margin` | Monetary |  | Expected Margin |  | C |
| `expected_margin_rate` | Float |  |  |  |  |
| `line_amount_total` | Monetary |  | Lines Total |  | C |
| `payment_term_note` | Html |  | Payment Terms |  |  |
| `billing_note` | Text |  | Billing Note |  |  |
| `state` | Selection | `CONTRACT_STATE_SELECTION` | Status | ✓ |  |
| `contract_summary` | Html |  | Contract Summary |  |  |
| `scope_summary` | Html |  | Scope Summary |  |  |
| `assumption_note` | Html |  | Assumptions |  |  |
| `exclusion_note` | Html |  | Exclusions |  |  |
| `legal_note` | Html |  | Legal Note |  |  |
| `handover_note` | Html |  | Handover Note |  |  |
| `internal_note` | Text |  | Internal Note |  |  |
| `line_ids` | One2many | `dcg.contract.line` | Contract Lines |  |  |
| `payment_ids` | One2many | `dcg.contract.payment` | Payment Schedule |  |  |
| `appendix_ids` | One2many | `dcg.contract.appendix` | Appendices |  |  |
| `acceptance_ids` | One2many | `dcg.contract.acceptance` | Acceptances |  |  |
| `line_count` | Integer |  |  |  | C |
| `payment_count` | Integer |  |  |  | C |
| `appendix_count` | Integer |  |  |  | C |
| `acceptance_count` | Integer |  |  |  | C |
| `handover_completed` | Boolean |  | Handover Completed |  |  |
| `handover_date` | Date |  | Handover Date |  |  |
| `signed_attachment_ids` | Many2many | `ir.attachment` | Signed Documents |  |  |
| `draft_attachment_ids` | Many2many | `ir.attachment` | Draft Documents |  |  |

### `dcg.contract.acceptance`
*Contract Acceptance*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `name` | Char |  | Acceptance No. | ✓ |  |
| `contract_id` | Many2one | `dcg.contract` | Contract | ✓ |  |
| `partner_id` | Many2one | `related:contract_id.partner_id` | Customer |  | R |
| `acceptance_type` | Selection | `ACCEPTANCE_TYPE_SELECTION` | Acceptance Type | ✓ |  |
| `acceptance_date` | Date |  | Acceptance Date |  |  |
| `state` | Selection | `ACCEPTANCE_STATE_SELECTION` | Status | ✓ |  |
| `title` | Char |  | Title |  |  |
| `summary` | Html |  | Summary |  |  |
| `result_note` | Html |  | Result Note |  |  |
| `signed_by_customer` | Char |  | Signed By Customer |  |  |
| `signed_by_company` | Char |  | Signed By Company |  |  |
| `attachment_ids` | Many2many | `ir.attachment` | Attachments |  |  |
| `payment_id` | Many2one | `dcg.contract.payment` | Related Payment |  |  |
| `appendix_id` | Many2one | `dcg.contract.appendix` | Related Appendix |  |  |

### `dcg.contract.appendix`
*Contract Appendix*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `name` | Char |  | Appendix Number | ✓ |  |
| `contract_id` | Many2one | `dcg.contract` | Contract | ✓ |  |
| `partner_id` | Many2one | `related:contract_id.partner_id` | Customer |  | R |
| `appendix_type` | Selection | `APPENDIX_TYPE_SELECTION` | Appendix Type | ✓ |  |
| `appendix_date` | Date |  | Appendix Date |  |  |
| `effective_date` | Date |  | Effective Date |  |  |
| `state` | Selection | `APPENDIX_STATE_SELECTION` | Status | ✓ |  |
| `currency_id` | Many2one | `related:contract_id.currency_id` | Currency |  | R |
| `value_delta` | Monetary |  | Value Change |  |  |
| `old_amount_total` | Monetary |  | Amount Before |  |  |
| `new_amount_total` | Monetary |  | Amount After |  | C |
| `old_end_date` | Date |  | End Date Before |  |  |
| `new_end_date` | Date |  | New End Date |  |  |
| `reason` | Html |  | Reason |  |  |
| `summary` | Html |  | Summary |  |  |
| `line_ids` | One2many | `dcg.contract.appendix.line` | Change Lines |  |  |
| `line_count` | Integer |  |  |  | C |

### `dcg.contract.appendix.line`
*Contract Appendix Line*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `appendix_id` | Many2one | `dcg.contract.appendix` | Appendix | ✓ |  |
| `contract_id` | Many2one | `related:appendix_id.contract_id` | Contract |  | R |
| `contract_line_id` | Many2one | `dcg.contract.line` | Affected Contract Line |  |  |
| `sequence` | Integer |  |  |  |  |
| `name` | Char |  | Description | ✓ |  |
| `change_type` | Selection | `CHANGE_TYPE_SELECTION` | Change Type | ✓ |  |
| `description` | Html |  | Detail |  |  |
| `currency_id` | Many2one | `related:appendix_id.currency_id` | Currency |  | R |
| `quantity` | Float |  | Quantity |  |  |
| `unit_price` | Monetary |  | Unit Price |  |  |
| `amount_delta` | Monetary |  | Amount Delta |  |  |
| `planned_start_date` | Date |  | Planned Start |  |  |
| `planned_end_date` | Date |  | Planned End |  |  |
| `note` | Text |  | Note |  |  |

### `dcg.contract.line`
*Contract Line*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `contract_id` | Many2one | `dcg.contract` | Contract | ✓ |  |
| `sequence` | Integer |  |  |  |  |
| `name` | Char |  | Description | ✓ |  |
| `service_catalog_id` | Many2one | `dcg.service.catalog` | Service |  |  |
| `scope_id` | Many2one | `dcg.crm.solution.scope` | Source Scope |  |  |
| `estimate_line_id` | Many2one | `dcg.crm.estimate.line` | Source Estimate Line |  |  |
| `line_type` | Selection | `LINE_TYPE_SELECTION` | Type |  |  |
| `description` | Html |  | Detail |  |  |
| `currency_id` | Many2one | `related:contract_id.currency_id` | Currency |  | R |
| `quantity` | Float |  | Quantity |  |  |
| `uom_name` | Char |  | Unit |  |  |
| `unit_price` | Monetary |  | Unit Price |  |  |
| `amount` | Monetary |  | Amount |  | C |
| `planned_start_date` | Date |  | Planned Start |  |  |
| `planned_end_date` | Date |  | Planned End |  |  |
| `note` | Text |  | Note |  |  |
| `ba_hours` | Float |  | BA Hours |  |  |
| `dev_hours` | Float |  | Dev Hours |  |  |
| `test_hours` | Float |  | Test Hours |  |  |
| `pm_hours` | Float |  | PM Hours |  |  |
| `support_hours` | Float |  | Support Hours |  |  |
| `total_hours` | Float |  | Total Hours |  | C |

### `dcg.contract.payment`
*Contract Payment Schedule*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `contract_id` | Many2one | `dcg.contract` | Contract | ✓ |  |
| `sequence` | Integer |  | Installment |  |  |
| `name` | Char |  | Milestone | ✓ |  |
| `milestone_name` | Char |  | Milestone Detail |  |  |
| `currency_id` | Many2one | `related:contract_id.currency_id` | Currency |  | R |
| `payment_type` | Selection | `PAYMENT_TYPE_SELECTION` | Payment Type | ✓ |  |
| `percent` | Float |  |  |  |  |
| `amount` | Monetary |  | Amount |  | C |
| `amount_received` | Monetary |  | Amount Received |  |  |
| `balance_amount` | Monetary |  | Balance |  | C |
| `due_date` | Date |  | Due Date |  |  |
| `planned_invoice_date` | Date |  | Planned Invoice Date |  |  |
| `actual_received_date` | Date |  | Actual Received Date |  |  |
| `condition_note` | Html |  | Payment Condition |  |  |
| `state` | Selection | `PAYMENT_STATE_SELECTION` | Status |  |  |
| `invoice_note` | Text |  | Invoice Note |  |  |

### `crm.lead` *(extend)*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `contract_count` | Integer |  | Contracts |  | C |
| `primary_contract_id` | Many2one | `dcg.contract` | Primary Contract |  |  |

### `sale.order` *(extend)*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `contract_count` | Integer |  | Contracts |  | C |
| `contract_created` | Boolean |  | Contract Created |  |  |

## 10. dcg_project_delivery

**Depends:** `project`, `mail`, `hr`, `dcg_master_data`, `dcg_contract_management`

**Models:** 6 new + 1 extend

### `dcg.contract` *(extend)*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `project_count` | Integer |  |  |  | C |
| `primary_project_id` | Many2one | `dcg.project.delivery` | Primary Project |  |  |
| `project_created` | Boolean |  | Project Created |  |  |

### `dcg.project.change.request`
*Project Change Request*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `project_id` | Many2one | `dcg.project.delivery` | Project | ✓ |  |
| `contract_id` | Many2one | `dcg.contract` | Contract | ✓ |  |
| `scope_id` | Many2one | `dcg.project.scope` | Scope |  |  |
| `appendix_id` | Many2one | `dcg.contract.appendix` | Generated Appendix |  |  |
| `name` | Char |  | CR Number | ✓ |  |
| `request_date` | Date |  | Request Date |  |  |
| `requested_by` | Selection | `REQUESTED_BY_SELECTION` | Requested By | ✓ |  |
| `owner_id` | Many2one | `res.users` | Owner |  |  |
| `state` | Selection | `CR_STATE_SELECTION` | Status | ✓ |  |
| `description` | Html |  | Description |  |  |
| `impact_scope` | Html |  | Scope Impact |  |  |
| `impact_timeline` | Html |  | Timeline Impact |  |  |
| `impact_cost` | Html |  | Cost Impact |  |  |
| `decision_note` | Html |  | Decision Note |  |  |
| `currency_id` | Many2one | `related:contract_id.currency_id` | Currency |  | R |
| `estimated_extra_hours` | Float |  | Extra Hours |  |  |
| `estimated_extra_cost` | Monetary |  | Extra Cost |  |  |
| `estimated_value_delta` | Monetary |  | Value Delta |  |  |
| `new_target_end_date` | Date |  | New Target End Date |  |  |

### `dcg.project.delivery`
*Project Delivery*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `name` | Char |  | Project Name | ✓ |  |
| `project_code` | Char |  | Project Code |  |  |
| `active` | Boolean |  |  |  |  |
| `company_id` | Many2one | `res.company` | Company | ✓ |  |
| `currency_id` | Many2one | `res.currency` | Currency | ✓ |  |
| `contract_id` | Many2one | `dcg.contract` | Contract | ✓ |  |
| `lead_id` | Many2one | `crm.lead` | Opportunity |  |  |
| `quotation_id` | Many2one | `sale.order` | Quotation |  |  |
| `partner_id` | Many2one | `res.partner` | Customer | ✓ |  |
| `estimate_id` | Many2one | `dcg.crm.estimate` | Source Estimate |  |  |
| `project_manager_id` | Many2one | `res.users` | Project Manager |  |  |
| `delivery_owner_id` | Many2one | `res.users` | Delivery Owner |  |  |
| `presales_owner_id` | Many2one | `res.users` | Presales Owner |  |  |
| `project_type` | Selection | `PROJECT_TYPE_SELECTION` | Project Type |  |  |
| `odoo_project_id` | Many2one | `project.project` | Odoo Project |  |  |
| `kick_off_date` | Date |  | Kick-off Date |  |  |
| `start_date` | Date |  | Start Date |  |  |
| `end_date` | Date |  | End Date |  |  |
| `actual_end_date` | Date |  | Actual End Date |  |  |
| `warranty_start_date` | Date |  | Warranty Start |  |  |
| `warranty_end_date` | Date |  | Warranty End |  |  |
| `state` | Selection | `PROJECT_STATE_SELECTION` | Status | ✓ |  |
| `contract_amount_total` | Monetary |  | Contract Amount |  |  |
| `expected_cost` | Monetary |  | Expected Cost |  |  |
| `expected_margin` | Monetary |  | Expected Margin |  |  |
| `planned_effort_hours` | Float |  |  |  |  |
| `actual_effort_hours` | Float |  |  |  |  |
| `progress_percent` | Float |  |  |  |  |
| `health_status` | Selection | `HEALTH_STATUS_SELECTION` | Health |  | C |
| `overall_note` | Html |  | Overall Note |  |  |
| `project_summary` | Html |  | Project Summary |  |  |
| `scope_summary` | Html |  | Scope Summary |  |  |
| `implementation_method` | Html |  | Implementation Method |  |  |
| `assumption_note` | Html |  | Assumptions |  |  |
| `exclusion_note` | Html |  | Exclusions |  |  |
| `risk_summary` | Html |  | Risk Summary |  |  |
| `handover_note` | Html |  | Handover Note |  |  |
| `scope_ids` | One2many | `dcg.project.scope` | Scope / Work Packages |  |  |
| `milestone_ids` | One2many | `dcg.project.milestone` | Milestones |  |  |
| `member_ids` | One2many | `dcg.project.member` | Team Members |  |  |
| `issue_ids` | One2many | `dcg.project.issue` | Issues / Risks |  |  |
| `change_request_ids` | One2many | `dcg.project.change.request` | Change Requests |  |  |
| `scope_count` | Integer |  |  |  | C |
| `milestone_count` | Integer |  |  |  | C |
| `issue_count` | Integer |  |  |  | C |
| `change_request_count` | Integer |  |  |  | C |
| `member_count` | Integer |  |  |  | C |

### `dcg.project.issue`
*Project Issue / Risk / Blocker*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `project_id` | Many2one | `dcg.project.delivery` | Project | ✓ |  |
| `scope_id` | Many2one | `dcg.project.scope` | Scope |  |  |
| `milestone_id` | Many2one | `dcg.project.milestone` | Milestone |  |  |
| `name` | Char |  | Title | ✓ |  |
| `issue_type` | Selection | `ISSUE_TYPE_SELECTION` | Type | ✓ |  |
| `priority` | Selection | `ISSUE_PRIORITY_SELECTION` | Priority |  |  |
| `owner_id` | Many2one | `res.users` | Assigned To |  |  |
| `raised_by_id` | Many2one | `res.users` | Raised By |  |  |
| `description` | Html |  | Description |  |  |
| `impact` | Html |  | Impact |  |  |
| `action_plan` | Html |  | Action Plan |  |  |
| `target_date` | Date |  | Target Date |  |  |
| `resolved_date` | Date |  | Resolved Date |  |  |
| `state` | Selection | `ISSUE_STATE_SELECTION` | Status | ✓ |  |

### `dcg.project.member`
*Project Member*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `project_id` | Many2one | `dcg.project.delivery` | Project | ✓ |  |
| `user_id` | Many2one | `res.users` | User | ✓ |  |
| `employee_id` | Many2one | `hr.employee` | Employee |  |  |
| `role` | Selection | `MEMBER_ROLE_SELECTION` | Role | ✓ |  |
| `start_date` | Date |  | Start Date |  |  |
| `end_date` | Date |  | End Date |  |  |
| `allocation_percent` | Float |  |  |  |  |
| `is_billable` | Boolean |  | Billable |  |  |
| `note` | Text |  | Note |  |  |

### `dcg.project.milestone`
*Project Milestone*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `project_id` | Many2one | `dcg.project.delivery` | Project | ✓ |  |
| `scope_id` | Many2one | `dcg.project.scope` | Scope |  |  |
| `contract_payment_id` | Many2one | `dcg.contract.payment` | Payment Milestone |  |  |
| `acceptance_id` | Many2one | `dcg.contract.acceptance` | Acceptance |  |  |
| `sequence` | Integer |  |  |  |  |
| `name` | Char |  | Milestone | ✓ |  |
| `milestone_type` | Selection | `MILESTONE_TYPE_SELECTION` | Type |  |  |
| `planned_date` | Date |  | Planned Date |  |  |
| `actual_date` | Date |  | Actual Date |  |  |
| `due_date` | Date |  | Due Date |  |  |
| `state` | Selection | `MILESTONE_STATE_SELECTION` | Status |  |  |
| `progress_percent` | Float |  |  |  |  |
| `note` | Text |  | Note |  |  |

### `dcg.project.scope`
*Project Scope / Work Package*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `project_id` | Many2one | `dcg.project.delivery` | Project | ✓ |  |
| `contract_line_id` | Many2one | `dcg.contract.line` | Source Contract Line |  |  |
| `estimate_line_id` | Many2one | `dcg.crm.estimate.line` | Source Estimate Line |  |  |
| `lead_scope_id` | Many2one | `dcg.crm.solution.scope` | Source Presales Scope |  |  |
| `sequence` | Integer |  |  |  |  |
| `name` | Char |  | Work Package | ✓ |  |
| `service_catalog_id` | Many2one | `dcg.service.catalog` | Service |  |  |
| `scope_type` | Selection | `SCOPE_TYPE_SELECTION` | Type |  |  |
| `description` | Html |  | Description |  |  |
| `owner_id` | Many2one | `res.users` | Owner |  |  |
| `state` | Selection | `SCOPE_STATE_SELECTION` | Status |  |  |
| `planned_start_date` | Date |  | Planned Start |  |  |
| `planned_end_date` | Date |  | Planned End |  |  |
| `actual_end_date` | Date |  | Actual End |  |  |
| `planned_hours` | Float |  | Planned Hours |  | C |
| `actual_hours` | Float |  | Actual Hours |  |  |
| `progress_percent` | Float |  |  |  |  |
| `note` | Text |  | Note |  |  |
| `ba_hours` | Float |  | BA Hours |  |  |
| `dev_hours` | Float |  | Dev Hours |  |  |
| `test_hours` | Float |  | Test Hours |  |  |
| `pm_hours` | Float |  | PM Hours |  |  |
| `support_hours` | Float |  | Support Hours |  |  |

## 11. dcg_timesheet_control

**Depends:** `hr_timesheet`, `mail`, `hr`, `project`, `dcg_master_data`, `dcg_project_delivery`

**Models:** 2 new + 3 extend

### `account.analytic.line` *(extend)*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `dcg_sheet_id` | Many2one | `dcg.timesheet.sheet` | Timesheet Sheet |  |  |
| `line_state` | Selection | `LINE_STATE_SELECTION` | Line Status |  |  |
| `dcg_project_id` | Many2one | `dcg.project.delivery` | Delivery Project |  |  |
| `dcg_scope_id` | Many2one | `dcg.project.scope` | Work Package |  |  |
| `dcg_milestone_id` | Many2one | `dcg.project.milestone` | Milestone |  |  |
| `contract_id` | Many2one | `dcg.contract` | Contract |  |  |
| `work_type` | Selection | `WORK_TYPE_SELECTION` | Work Type |  |  |
| `charge_type` | Selection | `CHARGE_TYPE_SELECTION` | Charge Type |  |  |
| `is_billable` | Boolean |  | Billable |  | C |
| `is_overtime` | Boolean |  | Overtime |  |  |
| `overtime_hours` | Float |  | OT Hours |  |  |
| `ot_request_id` | Many2one | `dcg.timesheet.ot.request` | OT Request |  |  |
| `work_summary` | Text |  | Work Summary |  |  |
| `result_note` | Text |  | Result |  |  |
| `billing_rate` | Monetary |  | Billing Rate |  |  |
| `cost_rate` | Monetary |  | Cost Rate |  |  |
| `line_cost_amount` | Monetary |  | Cost Amount |  | C |
| `line_billing_amount` | Monetary |  | Billing Amount |  | C |

### `dcg.project.delivery` *(extend)*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `timesheet_line_count` | Integer |  | Timesheet Lines |  | C |
| `total_actual_hours` | Float |  |  |  | C |
| `total_billable_hours` | Float |  | Billable Hours |  | C |
| `total_non_billable_hours` | Float |  | Non-billable Hours |  | C |
| `total_ot_hours` | Float |  | OT Hours |  | C |

### `dcg.project.scope` *(extend)*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `ts_actual_hours` | Float |  |  |  | C |
| `ts_billable_hours` | Float |  |  |  | C |
| `ts_non_billable_hours` | Float |  |  |  | C |
| `ts_ot_hours` | Float |  |  |  | C |
| `ts_line_count` | Integer |  | TS Lines |  | C |

### `dcg.timesheet.ot.request`
*Timesheet Overtime Request*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `name` | Char |  | OT Number | ✓ |  |
| `employee_id` | Many2one | `hr.employee` | Employee | ✓ |  |
| `user_id` | Many2one | `res.users` | User | ✓ |  |
| `company_id` | Many2one | `res.company` | Company | ✓ |  |
| `request_date` | Date |  | Request Date | ✓ |  |
| `date_from` | Datetime |  | OT Start | ✓ |  |
| `date_to` | Datetime |  | OT End | ✓ |  |
| `total_hours` | Float |  | OT Hours |  | C |
| `project_id` | Many2one | `dcg.project.delivery` | Project |  |  |
| `scope_id` | Many2one | `dcg.project.scope` | Scope |  |  |
| `reason` | Text |  | Reason | ✓ |  |
| `state` | Selection | `OT_STATE_SELECTION` | Status | ✓ |  |
| `approver_id` | Many2one | `res.users` | Approver |  |  |
| `approved_date` | Datetime |  | Approved Date |  |  |
| `reject_reason` | Text |  | Reject Reason |  |  |
| `timesheet_line_ids` | One2many | `account.analytic.line` | Timesheet Lines |  |  |

### `dcg.timesheet.sheet`
*Timesheet Sheet*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `name` | Char |  | Sheet Number | ✓ |  |
| `employee_id` | Many2one | `hr.employee` | Employee | ✓ |  |
| `user_id` | Many2one | `res.users` | User | ✓ |  |
| `company_id` | Many2one | `res.company` | Company | ✓ |  |
| `date_start` | Date |  | Period Start | ✓ |  |
| `date_end` | Date |  | Period End | ✓ |  |
| `period_type` | Selection | `PERIOD_TYPE_SELECTION` | Period Type | ✓ |  |
| `week_no` | Integer |  | Week No. |  | C |
| `month_key` | Char |  | Month |  | C |
| `state` | Selection | `SHEET_STATE_SELECTION` | Status | ✓ |  |
| `approver_id` | Many2one | `res.users` | Approver |  |  |
| `submitted_date` | Datetime |  | Submitted Date |  |  |
| `approved_date` | Datetime |  | Approved Date |  |  |
| `rejected_date` | Datetime |  | Rejected Date |  |  |
| `reject_reason` | Text |  | Reject Reason |  |  |
| `note` | Text |  | Note |  |  |
| `line_ids` | One2many | `account.analytic.line` | Timesheet Lines |  |  |
| `total_hours` | Float |  | Total Hours |  | C |
| `total_billable_hours` | Float |  | Billable Hours |  | C |
| `total_non_billable_hours` | Float |  | Non-billable Hours |  | C |
| `total_ot_hours` | Float |  | OT Hours |  | C |
| `line_count` | Integer |  | Lines |  | C |

## 12. dcg_project_finance

**Depends:** `mail`, `hr`, `dcg_contract_management`, `dcg_project_delivery`, `dcg_timesheet_control`

**Models:** 3 new + 2 extend

### `dcg.contract` *(extend)*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `finance_record_id` | Many2one | `dcg.project.finance` | Finance Record |  | C |

### `dcg.project.delivery` *(extend)*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `finance_id` | Many2one | `dcg.project.finance` | Finance Record |  |  |

### `dcg.project.finance`
*Project Finance*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `name` | Char |  | Finance Code | ✓ |  |
| `project_id` | Many2one | `dcg.project.delivery` | Project | ✓ |  |
| `contract_id` | Many2one | `dcg.contract` | Contract | ✓ |  |
| `company_id` | Many2one | `res.company` | Company | ✓ |  |
| `currency_id` | Many2one | `res.currency` | Currency | ✓ |  |
| `lead_id` | Many2one | `crm.lead` | Opportunity |  |  |
| `estimate_id` | Many2one | `dcg.crm.estimate` | Source Estimate |  |  |
| `quotation_id` | Many2one | `sale.order` | Quotation |  |  |
| `project_manager_id` | Many2one | `res.users` | PM |  |  |
| `delivery_owner_id` | Many2one | `res.users` | Delivery Owner |  |  |
| `state` | Selection | `FINANCE_STATE_SELECTION` | Status | ✓ |  |
| `finance_health` | Selection | `FINANCE_HEALTH_SELECTION` | Finance Health |  | C |
| `freeze_snapshot` | Boolean |  | Freeze Planned |  |  |
| `note` | Html |  | Note |  |  |
| `planned_revenue` | Monetary |  | Planned Revenue |  |  |
| `planned_cost` | Monetary |  | Planned Cost |  |  |
| `planned_labor_cost` | Monetary |  | Planned Labor Cost |  |  |
| `planned_travel_cost` | Monetary |  | Planned Travel Cost |  |  |
| `planned_subcontract_cost` | Monetary |  | Planned Subcontract Cost |  |  |
| `planned_other_cost` | Monetary |  | Planned Other Cost |  |  |
| `planned_margin` | Monetary |  | Planned Margin |  | C |
| `planned_margin_rate` | Float |  |  |  |  |
| `actual_revenue` | Monetary |  | Actual Revenue |  | C |
| `actual_cost` | Monetary |  | Actual Cost |  | C |
| `actual_labor_cost` | Monetary |  | Actual Labor Cost |  | C |
| `actual_travel_cost` | Monetary |  | Actual Travel Cost |  | C |
| `actual_subcontract_cost` | Monetary |  | Actual Subcontract Cost |  | C |
| `actual_other_cost` | Monetary |  | Actual Other Cost |  | C |
| `actual_margin` | Monetary |  | Actual Margin |  | C |
| `actual_margin_rate` | Float |  |  |  |  |
| `invoiced_amount` | Monetary |  | Invoiced |  | C |
| `collected_amount` | Monetary |  | Collected |  | C |
| `uncollected_amount` | Monetary |  | Outstanding |  | C |
| `collection_rate` | Float |  |  |  |  |
| `planned_hours` | Float |  | Planned Hours |  |  |
| `actual_hours` | Float |  | Actual Hours |  | C |
| `billable_hours` | Float |  | Billable Hours |  | C |
| `non_billable_hours` | Float |  | Non-billable Hours |  | C |
| `ot_hours` | Float |  | OT Hours |  | C |
| `avg_cost_per_hour` | Monetary |  | Avg Cost/Hour |  | C |
| `revenue_variance` | Monetary |  | Revenue Variance |  | C |
| `cost_variance` | Monetary |  | Cost Variance |  | C |
| `margin_variance` | Monetary |  | Margin Variance |  | C |
| `hours_variance` | Float |  | Hours Variance |  | C |
| `warning_note` | Html |  | Warning Note |  |  |
| `cost_line_ids` | One2many | `dcg.project.finance.cost.line` | Cost Lines |  |  |
| `revenue_line_ids` | One2many | `dcg.project.finance.revenue.line` | Revenue Lines |  |  |
| `cost_line_count` | Integer |  |  |  | C |
| `revenue_line_count` | Integer |  |  |  | C |

### `dcg.project.finance.cost.line`
*Project Finance Cost Line*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `finance_id` | Many2one | `dcg.project.finance` | Finance Record | ✓ |  |
| `project_id` | Many2one | `dcg.project.delivery` | Project | ✓ |  |
| `contract_id` | Many2one | `dcg.contract` | Contract |  |  |
| `scope_id` | Many2one | `dcg.project.scope` | Scope |  |  |
| `milestone_id` | Many2one | `dcg.project.milestone` | Milestone |  |  |
| `cost_type` | Selection | `COST_TYPE_SELECTION` | Cost Type | ✓ |  |
| `source_type` | Selection | `SOURCE_TYPE_SELECTION` | Source | ✓ |  |
| `name` | Char |  | Description | ✓ |  |
| `description` | Text |  | Detail |  |  |
| `cost_date` | Date |  | Date | ✓ |  |
| `quantity` | Float |  | Quantity |  |  |
| `unit_price` | Monetary |  | Unit Price |  |  |
| `amount` | Monetary |  | Amount | ✓ |  |
| `currency_id` | Many2one | `res.currency` | Currency | ✓ |  |
| `employee_id` | Many2one | `hr.employee` | Employee |  |  |
| `timesheet_line_id` | Many2one | `account.analytic.line` | Timesheet Line |  |  |
| `external_ref` | Char |  | External Reference |  |  |

### `dcg.project.finance.revenue.line`
*Project Finance Revenue Line*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `finance_id` | Many2one | `dcg.project.finance` | Finance Record | ✓ |  |
| `project_id` | Many2one | `dcg.project.delivery` | Project | ✓ |  |
| `contract_id` | Many2one | `dcg.contract` | Contract | ✓ |  |
| `payment_id` | Many2one | `dcg.contract.payment` | Payment Milestone |  |  |
| `acceptance_id` | Many2one | `dcg.contract.acceptance` | Acceptance |  |  |
| `milestone_id` | Many2one | `dcg.project.milestone` | Milestone |  |  |
| `line_type` | Selection | `LINE_TYPE_SELECTION` | Type | ✓ |  |
| `name` | Char |  | Description | ✓ |  |
| `description` | Text |  | Detail |  |  |
| `revenue_date` | Date |  | Date |  |  |
| `currency_id` | Many2one | `related:finance_id.currency_id` | Currency |  | R |
| `planned_amount` | Monetary |  | Planned |  |  |
| `invoiced_amount` | Monetary |  | Invoiced |  |  |
| `collected_amount` | Monetary |  | Collected |  |  |
| `balance_amount` | Monetary |  | Balance |  | C |
| `state` | Selection | `REVENUE_STATE_SELECTION` | Status |  |  |

## 13. dcg_business_trip

**Depends:** `mail`, `hr`, `dcg_master_data`, `dcg_approval_matrix`, `dcg_project_delivery`, `dcg_project_finance`

**Models:** 3 new + 1 extend

### `dcg.business.trip`
*Business Trip*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `name` | Char |  | Trip Code | ✓ |  |
| `title` | Char |  | Title | ✓ |  |
| `company_id` | Many2one | `res.company` | Company | ✓ |  |
| `currency_id` | Many2one | `res.currency` | Currency | ✓ |  |
| `active` | Boolean |  |  |  |  |
| `requester_id` | Many2one | `res.users` | Requester | ✓ |  |
| `employee_id` | Many2one | `hr.employee` | Employee |  |  |
| `department_id` | Many2one | `hr.department` | Department |  | R |
| `manager_id` | Many2one | `res.users` | Manager |  | R |
| `partner_id` | Many2one | `res.partner` | Customer / Partner |  |  |
| `project_id` | Many2one | `dcg.project.delivery` | Project |  |  |
| `contract_id` | Many2one | `dcg.contract` | Contract |  |  |
| `scope_id` | Many2one | `dcg.project.scope` | Scope |  |  |
| `milestone_id` | Many2one | `dcg.project.milestone` | Milestone |  |  |
| `finance_id` | Many2one | `dcg.project.finance` | Finance Record |  |  |
| `trip_type` | Selection | `TRIP_TYPE_SELECTION` | Trip Type |  |  |
| `trip_purpose` | Selection | `TRIP_PURPOSE_SELECTION` | Purpose |  |  |
| `work_type` | Selection | `TRIP_WORK_TYPE_SELECTION` | Work Type |  |  |
| `is_billable` | Boolean |  | Billable |  |  |
| `is_onsite` | Boolean |  | Onsite |  |  |
| `request_date` | Date |  | Request Date | ✓ |  |
| `start_datetime` | Datetime |  | Departure | ✓ |  |
| `end_datetime` | Datetime |  | Return | ✓ |  |
| `total_days` | Float |  | Total Days |  | C |
| `departure_place` | Char |  | From |  |  |
| `destination_place` | Char |  | Destination | ✓ |  |
| `destination_address` | Text |  | Destination Address |  |  |
| `note_schedule` | Text |  | Schedule Note |  |  |
| `objective` | Html |  | Objective |  |  |
| `agenda` | Html |  | Agenda |  |  |
| `expected_result` | Html |  | Expected Result |  |  |
| `internal_note` | Text |  | Internal Note |  |  |
| `state` | Selection | `TRIP_STATE_SELECTION` | Status | ✓ |  |
| `cancel_reason` | Text |  | Cancel Reason |  |  |
| `estimated_cost` | Monetary |  | Estimated Cost |  | C |
| `actual_cost` | Monetary |  | Actual Cost |  | C |
| `cost_variance` | Monetary |  | Cost Variance |  | C |
| `member_ids` | One2many | `dcg.business.trip.member` | Members |  |  |
| `expense_ids` | One2many | `dcg.business.trip.expense` | Expenses |  |  |
| `member_count` | Integer |  |  |  | C |
| `expense_count` | Integer |  |  |  | C |

### `dcg.business.trip.expense`
*Business Trip Expense*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `trip_id` | Many2one | `dcg.business.trip` | Trip | ✓ |  |
| `project_id` | Many2one | `related:trip_id.project_id` | Project |  | R |
| `contract_id` | Many2one | `related:trip_id.contract_id` | Contract |  | R |
| `finance_id` | Many2one | `related:trip_id.finance_id` | Finance |  | R |
| `member_id` | Many2one | `dcg.business.trip.member` | Member |  |  |
| `name` | Char |  | Description | ✓ |  |
| `expense_type_id` | Many2one | `dcg.expense.type` | Expense Type |  |  |
| `expense_category` | Selection | `EXPENSE_CATEGORY_SELECTION` | Category | ✓ |  |
| `source_type` | Selection | `EXPENSE_SOURCE_SELECTION` | Source | ✓ |  |
| `description` | Text |  | Detail |  |  |
| `expense_date` | Date |  | Date |  |  |
| `quantity` | Float |  | Quantity |  |  |
| `unit_price` | Monetary |  | Unit Price |  |  |
| `amount` | Monetary |  | Amount | ✓ |  |
| `currency_id` | Many2one | `related:trip_id.currency_id` | Currency |  | R |
| `attachment_ids` | Many2many | `ir.attachment` | Receipts |  |  |
| `bill_reference` | Char |  | Bill Reference |  |  |
| `vendor_name` | Char |  | Vendor |  |  |
| `note` | Text |  | Note |  |  |
| `finance_cost_line_id` | Many2one | `dcg.project.finance.cost.line` | Finance Cost Line |  |  |
| `finance_synced` | Boolean |  | Synced to Finance |  |  |

### `dcg.business.trip.member`
*Business Trip Member*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `trip_id` | Many2one | `dcg.business.trip` | Trip | ✓ |  |
| `employee_id` | Many2one | `hr.employee` | Employee | ✓ |  |
| `user_id` | Many2one | `related:employee_id.user_id` | User |  | R |
| `department_id` | Many2one | `related:employee_id.department_id` | Department |  | R |
| `role` | Selection | `MEMBER_ROLE_SELECTION` | Role |  |  |
| `is_team_lead` | Boolean |  | Team Lead |  |  |
| `join_datetime` | Datetime |  | Join Date |  |  |
| `leave_datetime` | Datetime |  | Leave Date |  |  |
| `note` | Text |  | Note |  |  |

### `dcg.project.delivery` *(extend)*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `trip_count` | Integer |  | Trips |  | C |
| `total_trip_cost` | Monetary |  | Trip Cost |  | C |

## 14. dcg_helpdesk_warranty

**Depends:** `mail`, `dcg_master_data`, `dcg_project_delivery`, `dcg_contract_management`

**Models:** 7 new + 2 extend

### `dcg.contract` *(extend)*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `ticket_count` | Integer |  |  |  | C |

### `dcg.project.delivery` *(extend)*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `ticket_count` | Integer |  |  |  | C |

### `dcg.warranty.activity`
*Warranty Ticket Activity*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `ticket_id` | Many2one | `dcg.warranty.ticket` | Ticket | ✓ |  |
| `activity_type` | Selection | `ACTIVITY_TYPE_SELECTION` | Type | ✓ |  |
| `user_id` | Many2one | `res.users` | User | ✓ |  |
| `activity_datetime` | Datetime |  | Date/Time | ✓ |  |
| `description` | Html |  | Description |  |  |
| `duration_hours` | Float |  |  |  |  |

### `dcg.warranty.sla`
*Warranty SLA Policy*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `name` | Char |  | SLA Name | ✓ |  |
| `sequence` | Integer |  |  |  |  |
| `active` | Boolean |  |  |  |  |
| `severity` | Selection | `SEVERITY_SELECTION` | Severity |  |  |
| `priority` | Selection | `PRIORITY_SELECTION` | Priority |  |  |
| `response_hours` | Float |  |  |  |  |
| `resolve_hours` | Float |  |  |  |  |
| `description` | Text |  | Description |  |  |
| `team_id` | Many2one | `dcg.warranty.team` | Team |  |  |

### `dcg.warranty.solution`
*Warranty Solution / Knowledge Base*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `title` | Char |  | Title | ✓ |  |
| `problem` | Html |  | Problem Description |  |  |
| `solution` | Html |  | Solution |  |  |
| `module_name` | Char |  | Module |  |  |
| `keyword` | Char |  | Keywords |  |  |
| `tag_ids` | Many2many | `dcg.warranty.ticket.tag` | Tags |  |  |
| `active` | Boolean |  |  |  |  |
| `ticket_count` | Integer |  | Tickets |  | C |

### `dcg.warranty.team`
*Warranty Support Team*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `name` | Char |  | Team Name | ✓ |  |
| `leader_id` | Many2one | `res.users` | Team Leader |  |  |
| `member_ids` | Many2many | `res.users` | Members |  |  |
| `active` | Boolean |  |  |  |  |
| `description` | Text |  | Description |  |  |
| `company_id` | Many2one | `res.company` | Company |  |  |

### `dcg.warranty.ticket`
*Warranty Ticket*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `name` | Char |  | Ticket No. | ✓ |  |
| `title` | Char |  | Title | ✓ |  |
| `active` | Boolean |  |  |  |  |
| `company_id` | Many2one | `res.company` | Company | ✓ |  |
| `partner_id` | Many2one | `res.partner` | Customer | ✓ |  |
| `contact_id` | Many2one | `res.partner` | Contact Person |  |  |
| `phone` | Char |  | Phone |  |  |
| `email` | Char |  | Email |  |  |
| `project_id` | Many2one | `dcg.project.delivery` | Project |  |  |
| `contract_id` | Many2one | `dcg.contract` | Contract |  |  |
| `scope_id` | Many2one | `dcg.project.scope` | Scope |  |  |
| `ticket_type` | Selection | `TICKET_TYPE_SELECTION` | Type | ✓ |  |
| `ticket_category` | Selection | `TICKET_CATEGORY_SELECTION` | Category |  |  |
| `severity` | Selection | `SEVERITY_SELECTION` | Severity |  |  |
| `priority` | Selection | `PRIORITY_SELECTION` | Priority |  |  |
| `tag_ids` | Many2many | `dcg.warranty.ticket.tag` | Tags |  |  |
| `stage_id` | Many2one | `dcg.warranty.ticket.stage` | Stage |  |  |
| `kanban_state` | Selection | Selection |  |  |  |
| `warranty_start_date` | Date |  | Warranty Start |  | R |
| `warranty_end_date` | Date |  | Warranty End |  | R |
| `is_in_warranty` | Boolean |  | In Warranty |  | C |
| `sla_id` | Many2one | `dcg.warranty.sla` | SLA Policy |  |  |
| `response_deadline` | Datetime |  | Response Deadline |  |  |
| `resolve_deadline` | Datetime |  | Resolve Deadline |  |  |
| `sla_breached` | Boolean |  | SLA Breached |  | C |
| `team_id` | Many2one | `dcg.warranty.team` | Team |  |  |
| `owner_id` | Many2one | `res.users` | Owner |  |  |
| `support_engineer_id` | Many2one | `res.users` | Engineer |  |  |
| `reviewer_id` | Many2one | `res.users` | Reviewer |  |  |
| `assign_date` | Datetime |  | Assigned Date |  |  |
| `response_date` | Datetime |  | First Response Date |  |  |
| `resolve_date` | Datetime |  | Resolved Date |  |  |
| `close_date` | Datetime |  | Closed Date |  |  |
| `summary` | Text |  | Summary |  |  |
| `description` | Html |  | Description |  |  |
| `root_cause` | Html |  | Root Cause |  |  |
| `solution_text` | Html |  | Solution |  |  |
| `customer_feedback` | Text |  | Customer Feedback |  |  |
| `warranty_result` | Selection | `WARRANTY_RESULT_SELECTION` | Result |  |  |
| `affected_version` | Char |  | Affected Version |  |  |
| `fixed_version` | Char |  | Fixed Version |  |  |
| `commit_url` | Char |  | Commit URL |  |  |
| `estimated_hours` | Float |  | Estimated Hours |  |  |
| `spent_hours` | Float |  | Spent Hours |  |  |
| `attachment_ids` | Many2many | `ir.attachment` | Attachments |  |  |
| `activity_line_ids` | One2many | `dcg.warranty.activity` | Activity Timeline |  |  |
| `solution_id` | Many2one | `dcg.warranty.solution` | Solution Reference |  |  |
| `activity_count` | Integer |  |  |  | C |

### `dcg.warranty.ticket.stage`
*Warranty Ticket Stage*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `name` | Char |  | Stage | ✓ |  |
| `sequence` | Integer |  |  |  |  |
| `description` | Text |  | Description |  |  |
| `fold` | Boolean |  | Folded in Kanban |  |  |
| `active` | Boolean |  |  |  |  |
| `color` | Integer |  | Color |  |  |
| `is_start` | Boolean |  | Start Stage |  |  |
| `is_done` | Boolean |  | Done Stage |  |  |
| `is_cancel` | Boolean |  | Cancel Stage |  |  |
| `allow_edit` | Boolean |  | Allow Edit |  |  |
| `sla_running` | Boolean |  | SLA Running |  |  |
| `pause_sla` | Boolean |  | Pause SLA |  |  |
| `stop_sla` | Boolean |  | Stop SLA |  |  |
| `team_ids` | Many2many | `dcg.warranty.team` | Teams |  |  |

### `dcg.warranty.ticket.tag`
*Warranty Ticket Tag*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `name` | Char |  | Tag | ✓ |  |
| `description` | Text |  | Description |  |  |
| `color` | Integer |  | Color |  |  |
| `sequence` | Integer |  |  |  |  |
| `active` | Boolean |  |  |  |  |
| `group` | Selection | `TAG_GROUP_SELECTION` | Group |  |  |

## 15. dcg_resource_planning

**Depends:** `mail`, `hr`, `resource`, `dcg_master_data`, `dcg_project_delivery`, `dcg_timesheet_control`

**Models:** 7 new + 1 extend

### `hr.employee` *(extend)*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `primary_role_id` | Many2one | `dcg.resource.role` | Primary Role |  |  |
| `skill_ids` | One2many | `dcg.resource.skill` | Skills |  |  |
| `allocation_ids` | One2many | `dcg.resource.allocation` | Allocations |  |  |
| `capacity_ids` | One2many | `dcg.resource.capacity` | Capacity History |  |  |
| `current_allocation_percent` | Float |  |  |  |  |
| `is_on_bench` | Boolean |  | On Bench |  | C |
| `skill_count` | Integer |  |  |  | C |
| `active_allocation_count` | Integer |  |  |  | C |

### `dcg.resource.allocation`
*Resource Allocation*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `plan_id` | Many2one | `dcg.resource.plan` | Resource Plan |  |  |
| `project_id` | Many2one | `dcg.project.delivery` | Project | ✓ |  |
| `employee_id` | Many2one | `hr.employee` | Employee | ✓ |  |
| `user_id` | Many2one | `related:employee_id.user_id` | User |  | R |
| `department_id` | Many2one | `related:employee_id.department_id` | Department |  | R |
| `role_id` | Many2one | `dcg.resource.role` | Role | ✓ |  |
| `resource_type` | Selection | `RESOURCE_TYPE_SELECTION` | Resource Type |  |  |
| `state` | Selection | `ALLOC_STATE_SELECTION` | Status |  |  |
| `start_date` | Date |  | Start Date | ✓ |  |
| `end_date` | Date |  | End Date | ✓ |  |
| `allocation_percent` | Float |  |  |  |  |
| `allocation_hours` | Float |  | Allocated Hours |  | C |
| `actual_hours` | Float |  | Actual Hours |  | C |
| `variance_hours` | Float |  | Variance |  | C |
| `cost_rate` | Float |  |  |  |  |
| `bill_rate` | Float |  |  |  |  |
| `is_billable` | Boolean |  | Billable |  |  |
| `note` | Text |  | Note |  |  |
| `total_allocation_percent` | Float |  |  |  |  |
| `is_over_allocated` | Boolean |  | Over-allocated |  | C |

### `dcg.resource.capacity`
*Resource Capacity*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `employee_id` | Many2one | `hr.employee` | Employee | ✓ |  |
| `department_id` | Many2one | `related:employee_id.department_id` | Department |  | R |
| `role_id` | Many2one | `dcg.resource.role` | Primary Role |  |  |
| `company_id` | Many2one | `res.company` | Company | ✓ |  |
| `period_start` | Date |  | Period Start | ✓ |  |
| `period_end` | Date |  | Period End | ✓ |  |
| `period_label` | Char |  | Period |  | C |
| `capacity_hours` | Float |  |  |  |  |
| `allocated_hours` | Float |  |  |  |  |
| `actual_hours` | Float |  |  |  |  |
| `available_hours` | Float |  |  |  |  |
| `billable_hours` | Float |  |  |  |  |
| `allocation_rate` | Float |  |  |  |  |
| `utilization_rate` | Float |  |  |  |  |
| `bench_hours` | Float |  |  |  |  |

### `dcg.resource.forecast`
*Resource Forecast*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `role_id` | Many2one | `dcg.resource.role` | Role | ✓ |  |
| `department_id` | Many2one | `hr.department` | Department |  |  |
| `company_id` | Many2one | `res.company` | Company | ✓ |  |
| `period_start` | Date |  | Period Start | ✓ |  |
| `period_end` | Date |  | Period End | ✓ |  |
| `period_label` | Char |  | Period |  | C |
| `demand_count` | Integer |  |  |  |  |
| `demand_hours` | Float |  |  |  |  |
| `supply_count` | Integer |  |  |  |  |
| `supply_hours` | Float |  |  |  |  |
| `gap_count` | Integer |  |  |  |  |
| `gap_hours` | Float |  |  |  |  |
| `project_id` | Many2one | `dcg.project.delivery` | Project |  |  |
| `note` | Text |  | Note |  |  |

### `dcg.resource.plan`
*Resource Plan*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `name` | Char |  | Plan Code | ✓ |  |
| `project_id` | Many2one | `dcg.project.delivery` | Project | ✓ |  |
| `contract_id` | Many2one | `related:project_id.contract_id` | Contract |  | R |
| `partner_id` | Many2one | `related:project_id.partner_id` | Customer |  | R |
| `manager_id` | Many2one | `res.users` | Resource Manager |  |  |
| `company_id` | Many2one | `res.company` | Company | ✓ |  |
| `state` | Selection | `PLAN_STATE_SELECTION` | Status | ✓ |  |
| `allocation_ids` | One2many | `dcg.resource.allocation` | Allocations |  |  |
| `request_ids` | One2many | `dcg.resource.request` | Resource Requests |  |  |
| `planned_hours` | Float |  | Planned Hours |  |  |
| `allocated_hours` | Float |  | Allocated Hours |  | C |
| `actual_hours` | Float |  | Actual Hours |  | C |
| `remaining_hours` | Float |  | Remaining Hours |  | C |
| `allocation_count` | Integer |  |  |  | C |
| `request_count` | Integer |  |  |  | C |
| `note` | Html |  | Note |  |  |

### `dcg.resource.request`
*Resource Request*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `name` | Char |  | Request No. | ✓ |  |
| `plan_id` | Many2one | `dcg.resource.plan` | Resource Plan |  |  |
| `project_id` | Many2one | `dcg.project.delivery` | Project | ✓ |  |
| `requester_id` | Many2one | `res.users` | Requester | ✓ |  |
| `approver_id` | Many2one | `res.users` | Approver |  |  |
| `company_id` | Many2one | `res.company` | Company | ✓ |  |
| `state` | Selection | `REQUEST_STATE_SELECTION` | Status | ✓ |  |
| `role_id` | Many2one | `dcg.resource.role` | Role Needed | ✓ |  |
| `quantity` | Integer |  | Quantity | ✓ |  |
| `urgency` | Selection | `REQUEST_URGENCY_SELECTION` | Urgency |  |  |
| `needed_from` | Date |  | Needed From | ✓ |  |
| `needed_until` | Date |  | Needed Until | ✓ |  |
| `allocation_percent` | Float |  |  |  |  |
| `required_skills` | Text |  | Required Skills |  |  |
| `justification` | Html |  | Justification |  |  |
| `allocated_employee_ids` | Many2many | `hr.employee` | Allocated Employees |  |  |
| `allocation_ids` | One2many | `dcg.resource.allocation` |  |  | C |
| `fulfillment_note` | Text |  | Fulfillment Note |  |  |

### `dcg.resource.role`
*Resource Role*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `name` | Char |  | Role | ✓ |  |
| `code` | Char |  | Code | ✓ |  |
| `sequence` | Integer |  |  |  |  |
| `active` | Boolean |  |  |  |  |
| `department_id` | Many2one | `hr.department` | Department |  |  |
| `default_cost_rate` | Float |  | Default Cost Rate |  |  |
| `default_bill_rate` | Float |  | Default Bill Rate |  |  |
| `description` | Text |  | Description |  |  |
| `color` | Integer |  | Color |  |  |

### `dcg.resource.skill`
*Resource Skill*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `employee_id` | Many2one | `hr.employee` | Employee | ✓ |  |
| `skill_name` | Char |  | Skill | ✓ |  |
| `skill_category` | Selection | `SKILL_CATEGORY_SELECTION` | Category |  |  |
| `level` | Selection | `SKILL_LEVEL_SELECTION` | Level |  |  |
| `years_of_experience` | Float |  |  |  |  |
| `certified` | Boolean |  | Certified |  |  |
| `last_used_date` | Date |  | Last Used |  |  |
| `note` | Text |  | Note |  |  |

## 16. dcg_document_management

**Depends:** `mail`, `dcg_master_data`, `dcg_project_delivery`, `dcg_contract_management`

**Models:** 10 new

### `dcg.document`
*Document*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `name` | Char |  | Document Name | ✓ |  |
| `code` | Char |  | Document Code |  |  |
| `active` | Boolean |  |  |  |  |
| `company_id` | Many2one | `res.company` | Company | ✓ |  |
| `owner_id` | Many2one | `res.users` | Owner |  |  |
| `folder_id` | Many2one | `dcg.document.folder` | Folder |  |  |
| `type_id` | Many2one | `dcg.document.type` | Type |  |  |
| `category_id` | Many2one | `dcg.document.category` | Category |  |  |
| `tag_ids` | Many2many | `dcg.document.tag` | Tags |  |  |
| `template_id` | Many2one | `dcg.document.template` | From Template |  |  |
| `partner_id` | Many2one | `res.partner` | Customer |  |  |
| `project_id` | Many2one | `dcg.project.delivery` | Project |  |  |
| `contract_id` | Many2one | `dcg.contract` | Contract |  |  |
| `state` | Selection | `DOCUMENT_STATE_SELECTION` | Status | ✓ |  |
| `description` | Html |  | Description |  |  |
| `content` | Html |  | Content |  |  |
| `current_attachment_id` | Many2one | `ir.attachment` | Current File |  | C |
| `current_version` | Char |  | Current Version |  | C |
| `version_ids` | One2many | `dcg.document.version` | Versions |  |  |
| `review_ids` | One2many | `dcg.document.review` | Reviews |  |  |
| `link_ids` | One2many | `dcg.document.link` | Business Links |  |  |
| `version_count` | Integer |  |  |  | C |
| `review_count` | Integer |  |  |  | C |
| `link_count` | Integer |  |  |  | C |

### `dcg.document.category`
*Document Category*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `name` | Char |  | Category | ✓ |  |
| `code` | Char |  | Code |  |  |
| `sequence` | Integer |  |  |  |  |
| `active` | Boolean |  |  |  |  |
| `description` | Text |  | Description |  |  |

### `dcg.document.checklist`
*Document Checklist*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `project_id` | Many2one | `dcg.project.delivery` | Project | ✓ |  |
| `sequence` | Integer |  |  |  |  |
| `name` | Char |  | Required Document | ✓ |  |
| `category_id` | Many2one | `dcg.document.category` | Category |  |  |
| `type_id` | Many2one | `dcg.document.type` | Type |  |  |
| `is_mandatory` | Boolean |  | Mandatory |  |  |
| `document_id` | Many2one | `dcg.document` | Linked Document |  |  |
| `is_fulfilled` | Boolean |  | Fulfilled |  | C |
| `note` | Text |  | Note |  |  |

### `dcg.document.folder`
*Document Folder*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `name` | Char |  | Name | ✓ |  |
| `complete_name` | Char |  | Full Path |  | C |
| `parent_id` | Many2one | `dcg.document.folder` | Parent Folder |  |  |
| `child_ids` | One2many | `dcg.document.folder` | Sub-folders |  |  |
| `sequence` | Integer |  |  |  |  |
| `manager_id` | Many2one | `res.users` | Manager |  |  |
| `company_id` | Many2one | `res.company` | Company |  |  |
| `active` | Boolean |  |  |  |  |
| `description` | Text |  | Description |  |  |
| `document_count` | Integer |  |  |  | C |

### `dcg.document.link`
*Document Business Link*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `document_id` | Many2one | `dcg.document` | Document | ✓ |  |
| `link_model` | Selection | `LINK_MODEL_SELECTION` | Object Type | ✓ |  |
| `link_res_id` | Integer |  | Object ID | ✓ |  |
| `link_name` | Char |  | Object Name |  | C |
| `note` | Char |  | Note |  |  |

### `dcg.document.review`
*Document Review*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `document_id` | Many2one | `dcg.document` | Document | ✓ |  |
| `reviewer_id` | Many2one | `res.users` | Reviewer | ✓ |  |
| `review_date` | Datetime |  | Review Date |  |  |
| `status` | Selection | `REVIEW_STATUS_SELECTION` | Status | ✓ |  |
| `version_id` | Many2one | `dcg.document.version` | Version Reviewed |  |  |
| `comment` | Html |  | Comment |  |  |

### `dcg.document.tag`
*Document Tag*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `name` | Char |  | Tag | ✓ |  |
| `color` | Integer |  | Color |  |  |
| `description` | Text |  | Description |  |  |

### `dcg.document.template`
*Document Template*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `name` | Char |  | Template | ✓ |  |
| `sequence` | Integer |  |  |  |  |
| `active` | Boolean |  |  |  |  |
| `type_id` | Many2one | `dcg.document.type` | Document Type |  |  |
| `category_id` | Many2one | `dcg.document.category` | Category |  |  |
| `folder_id` | Many2one | `dcg.document.folder` | Default Folder |  |  |
| `tag_ids` | Many2many | `dcg.document.tag` | Default Tags |  |  |
| `attachment_id` | Many2one | `ir.attachment` | Template File |  |  |
| `description` | Html |  | Description / Instructions |  |  |
| `default_content` | Html |  | Default Content |  |  |

### `dcg.document.type`
*Document Type*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `name` | Char |  | Type | ✓ |  |
| `code` | Char |  | Code |  |  |
| `sequence` | Integer |  |  |  |  |
| `active` | Boolean |  |  |  |  |
| `description` | Text |  | Description |  |  |
| `requires_approval` | Boolean |  | Requires Approval |  |  |
| `requires_version` | Boolean |  | Requires Version |  |  |
| `portal_visible` | Boolean |  | Portal Visible |  |  |
| `retention_days` | Integer |  |  |  |  |

### `dcg.document.version`
*Document Version*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `document_id` | Many2one | `dcg.document` | Document | ✓ |  |
| `version_number` | Char |  | Version | ✓ |  |
| `attachment_id` | Many2one | `ir.attachment` | File |  |  |
| `file_name` | Char |  | File Name |  | R |
| `file_size` | Integer |  | Size |  | R |
| `change_log` | Text |  | Change Log |  |  |
| `created_by_id` | Many2one | `res.users` | Created By |  |  |
| `is_current` | Boolean |  | Current Version |  |  |

## 17. dcg_hr_resource

**Depends:** `hr`, `dcg_master_data`, `dcg_resource_planning`

**Models:** 6 new + 1 extend

### `dcg.employee.availability`
*Employee Availability*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `employee_id` | Many2one | `hr.employee` | Employee | ✓ |  |
| `available_from` | Date |  | From | ✓ |  |
| `available_to` | Date |  | To | ✓ |  |
| `available_hours` | Float |  | Available Hours |  |  |
| `status` | Selection | `AVAILABILITY_STATUS_SELECTION` | Status | ✓ |  |
| `note` | Text |  | Note |  |  |

### `dcg.employee.career.level`
*Employee Career Level*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `name` | Char |  | Level | ✓ |  |
| `code` | Char |  | Code |  |  |
| `sequence` | Integer |  |  |  |  |
| `minimum_years` | Float |  |  |  |  |
| `active` | Boolean |  |  |  |  |
| `description` | Text |  | Description |  |  |

### `dcg.employee.certificate`
*Employee Certificate*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `employee_id` | Many2one | `hr.employee` | Employee | ✓ |  |
| `name` | Char |  | Certificate | ✓ |  |
| `issuer` | Char |  | Issuer |  |  |
| `certificate_no` | Char |  | Certificate No. |  |  |
| `issue_date` | Date |  | Issue Date |  |  |
| `expiry_date` | Date |  | Expiry Date |  |  |
| `is_expired` | Boolean |  | Expired |  | C |
| `attachment_ids` | Many2many | `ir.attachment` | Attachments |  |  |
| `note` | Text |  | Note |  |  |

### `dcg.employee.competency`
*Employee Competency Assessment*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `employee_id` | Many2one | `hr.employee` | Employee | ✓ |  |
| `period` | Char |  | Period | ✓ |  |
| `assessment_date` | Date |  | Assessment Date |  |  |
| `reviewer_id` | Many2one | `res.users` | Reviewer |  |  |
| `technical_score` | Float |  | Technical |  |  |
| `communication_score` | Float |  | Communication |  |  |
| `leadership_score` | Float |  | Leadership |  |  |
| `problem_solving_score` | Float |  | Problem Solving |  |  |
| `teamwork_score` | Float |  | Teamwork |  |  |
| `overall_score` | Float |  | Overall |  | C |
| `strength` | Text |  | Strengths |  |  |
| `improvement` | Text |  | Areas for Improvement |  |  |
| `note` | Text |  | Note |  |  |

### `dcg.employee.kpi`
*Employee Delivery KPI*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `employee_id` | Many2one | `hr.employee` | Employee | ✓ |  |
| `period` | Char |  | Period | ✓ |  |
| `period_start` | Date |  | Period Start |  |  |
| `period_end` | Date |  | Period End |  |  |
| `utilization_rate` | Float |  |  |  |  |
| `billable_rate` | Float |  |  |  |  |
| `total_hours` | Float |  | Total Hours |  |  |
| `billable_hours` | Float |  | Billable Hours |  |  |
| `overtime_hours` | Float |  | OT Hours |  |  |
| `project_count` | Integer |  | Projects |  |  |
| `ticket_resolved` | Integer |  | Tickets Resolved |  |  |
| `customer_score` | Float |  | Customer Score |  |  |
| `manager_score` | Float |  | Manager Score |  |  |
| `overall_score` | Float |  | Overall Score |  |  |
| `is_locked` | Boolean |  | Locked |  |  |
| `note` | Text |  | Note |  |  |

### `hr.employee` *(extend)*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `employee_code` | Char |  | Employee Code |  |  |
| `career_level_id` | Many2one | `dcg.employee.career.level` | Career Level |  |  |
| `is_billable` | Boolean |  | Billable Resource |  |  |
| `join_delivery_date` | Date |  | Delivery Join Date |  |  |
| `hour_cost` | Monetary |  | Hour Cost |  |  |
| `hour_bill_rate` | Monetary |  | Hour Bill Rate |  |  |
| `currency_id` | Many2one | `related:company_id.currency_id` |  |  | R |
| `capacity_hours_month` | Float |  |  |  |  |
| `target_utilization` | Float |  |  |  |  |
| `certificate_ids` | One2many | `dcg.employee.certificate` | Certificates |  |  |
| `training_ids` | One2many | `dcg.employee.training` | Trainings |  |  |
| `competency_ids` | One2many | `dcg.employee.competency` | Competency Assessments |  |  |
| `kpi_ids` | One2many | `dcg.employee.kpi` | KPIs |  |  |
| `availability_ids` | One2many | `dcg.employee.availability` | Availability |  |  |
| `certificate_count` | Integer |  |  |  | C |
| `training_count` | Integer |  |  |  | C |

### `dcg.employee.training`
*Employee Training*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `employee_id` | Many2one | `hr.employee` | Employee | ✓ |  |
| `course_name` | Char |  | Course | ✓ |  |
| `provider` | Char |  | Provider |  |  |
| `start_date` | Date |  | Start Date |  |  |
| `end_date` | Date |  | End Date |  |  |
| `hours` | Float |  | Hours |  |  |
| `result` | Selection | `TRAINING_RESULT_SELECTION` | Result |  |  |
| `has_certificate` | Boolean |  | Certificate Received |  |  |
| `attachment_ids` | Many2many | `ir.attachment` | Attachments |  |  |
| `note` | Text |  | Note |  |  |

## 18. dcg_asset_it

**Depends:** `mail`, `hr`, `dcg_master_data`, `dcg_project_delivery`

**Models:** 12 new + 1 extend

### `dcg.asset`
*IT Asset*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `name` | Char |  | Asset Name | ✓ |  |
| `asset_code` | Char |  | Asset Code | ✓ |  |
| `display_name_computed` | Char |  |  |  | C |
| `serial_number` | Char |  | Serial Number |  |  |
| `barcode` | Char |  | Barcode |  |  |
| `company_id` | Many2one | `res.company` | Company | ✓ |  |
| `active` | Boolean |  |  |  |  |
| `type_id` | Many2one | `dcg.asset.type` | Type |  |  |
| `category_id` | Many2one | `dcg.asset.category` | Category |  |  |
| `stage_id` | Many2one | `dcg.asset.stage` | Stage |  |  |
| `location_id` | Many2one | `dcg.asset.location` | Location |  |  |
| `manufacturer` | Char |  | Manufacturer |  |  |
| `brand` | Char |  | Brand |  |  |
| `model_name` | Char |  | Model |  |  |
| `cpu` | Char |  | CPU |  |  |
| `ram` | Char |  | RAM |  |  |
| `storage` | Char |  | Storage |  |  |
| `mac_address` | Char |  | MAC Address |  |  |
| `ip_address` | Char |  | IP Address |  |  |
| `operating_system` | Char |  | OS |  |  |
| `purchase_date` | Date |  | Purchase Date |  |  |
| `vendor_id` | Many2one | `res.partner` | Vendor |  |  |
| `purchase_price` | Monetary |  | Purchase Price |  |  |
| `currency_id` | Many2one | `related:company_id.currency_id` |  |  | R |
| `current_employee_id` | Many2one | `hr.employee` | Assigned To |  | C |
| `current_project_id` | Many2one | `dcg.project.delivery` | Assigned Project |  | C |
| `assignment_ids` | One2many | `dcg.asset.assignment` | Assignments |  |  |
| `history_ids` | One2many | `dcg.asset.history` | History |  |  |
| `warranty_ids` | One2many | `dcg.asset.warranty` | Warranties |  |  |
| `maintenance_ids` | One2many | `dcg.asset.maintenance` | Maintenance |  |  |
| `software_ids` | One2many | `dcg.asset.software.install` | Software |  |  |
| `checkout_ids` | One2many | `dcg.asset.checkout` | Checkouts |  |  |
| `note` | Html |  | Note |  |  |
| `image` | Image |  | Image |  |  |

### `dcg.asset.assignment`
*Asset Assignment*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `asset_id` | Many2one | `dcg.asset` | Asset | ✓ |  |
| `employee_id` | Many2one | `hr.employee` | Employee |  |  |
| `project_id` | Many2one | `dcg.project.delivery` | Project |  |  |
| `department_id` | Many2one | `hr.department` | Department |  |  |
| `assigned_date` | Date |  | Assigned Date | ✓ |  |
| `returned_date` | Date |  | Returned Date |  |  |
| `status` | Selection | Selection | Status | ✓ |  |
| `assigned_by_id` | Many2one | `res.users` | Assigned By |  |  |
| `note` | Text |  | Note |  |  |

### `dcg.asset.category`
*Asset Category*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `name` | Char |  | Category | ✓ |  |
| `code` | Char |  | Code |  |  |
| `sequence` | Integer |  |  |  |  |
| `active` | Boolean |  |  |  |  |

### `dcg.asset.checkout`
*Asset Checkout (Short-term)*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `name` | Char |  | Checkout No. | ✓ |  |
| `asset_id` | Many2one | `dcg.asset` | Asset | ✓ |  |
| `employee_id` | Many2one | `hr.employee` | Borrower | ✓ |  |
| `purpose` | Char |  | Purpose | ✓ |  |
| `checkout_date` | Datetime |  | Checkout | ✓ |  |
| `expected_return` | Datetime |  | Expected Return | ✓ |  |
| `actual_return` | Datetime |  | Actual Return |  |  |
| `state` | Selection | Selection | Status |  |  |
| `approver_id` | Many2one | `res.users` | Approver |  |  |
| `note` | Text |  | Note |  |  |

### `dcg.asset.history`
*Asset History*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `asset_id` | Many2one | `dcg.asset` | Asset | ✓ |  |
| `action` | Selection | Selection | Action | ✓ |  |
| `action_date` | Datetime |  | Date | ✓ |  |
| `user_id` | Many2one | `res.users` | By |  |  |
| `employee_id` | Many2one | `hr.employee` | Employee |  |  |
| `description` | Text |  | Description |  |  |

### `dcg.asset.license`
*Software License*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `name` | Char |  | Software | ✓ |  |
| `license_key` | Char |  | License Key |  |  |
| `vendor_id` | Many2one | `res.partner` | Vendor |  |  |
| `purchase_date` | Date |  | Purchase Date |  |  |
| `expiry_date` | Date |  | Expiry Date |  |  |
| `is_expired` | Boolean |  | Expired |  | C |
| `seat_count` | Integer |  | Total Seats |  |  |
| `assigned_employee_ids` | Many2many | `hr.employee` | Assigned To |  |  |
| `assigned_count` | Integer |  | Used Seats |  | C |
| `available_seats` | Integer |  | Available |  | C |
| `is_over_licensed` | Boolean |  | Over-licensed |  | C |
| `cost` | Monetary |  | Cost |  |  |
| `currency_id` | Many2one | `res.currency` |  |  |  |
| `company_id` | Many2one | `res.company` |  |  |  |
| `note` | Text |  | Note |  |  |
| `active` | Boolean |  |  |  |  |

### `dcg.asset.location`
*Asset Location*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `name` | Char |  | Location | ✓ |  |
| `code` | Char |  | Code |  |  |
| `address` | Text |  | Address |  |  |
| `active` | Boolean |  |  |  |  |

### `dcg.asset.maintenance`
*Asset Maintenance*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `asset_id` | Many2one | `dcg.asset` | Asset | ✓ |  |
| `maintenance_date` | Date |  | Date | ✓ |  |
| `supplier` | Char |  | Supplier |  |  |
| `cost` | Monetary |  | Cost |  |  |
| `currency_id` | Many2one | `related:asset_id.currency_id` |  |  | R |
| `description` | Text |  | Description |  |  |
| `attachment_ids` | Many2many | `ir.attachment` | Attachments |  |  |

### `dcg.asset.software.install`
*Asset Software Install*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `asset_id` | Many2one | `dcg.asset` | Device | ✓ |  |
| `software_name` | Char |  | Software | ✓ |  |
| `version` | Char |  | Version |  |  |
| `install_date` | Date |  | Install Date |  |  |
| `license_id` | Many2one | `dcg.asset.license` | License |  |  |
| `installed_by_id` | Many2one | `res.users` | Installed By |  |  |
| `note` | Text |  | Note |  |  |

### `dcg.asset.stage`
*Asset Stage*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `name` | Char |  | Stage | ✓ |  |
| `sequence` | Integer |  |  |  |  |
| `fold` | Boolean |  | Folded |  |  |
| `is_start` | Boolean |  | Start Stage |  |  |
| `is_end` | Boolean |  | End Stage |  |  |
| `active` | Boolean |  |  |  |  |

### `dcg.asset.type`
*Asset Type*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `name` | Char |  | Type | ✓ |  |
| `code` | Char |  | Code |  |  |
| `sequence` | Integer |  |  |  |  |
| `active` | Boolean |  |  |  |  |
| `description` | Text |  | Description |  |  |

### `dcg.asset.warranty`
*Asset Warranty*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `asset_id` | Many2one | `dcg.asset` | Asset | ✓ |  |
| `vendor_id` | Many2one | `res.partner` | Vendor |  |  |
| `warranty_type` | Char |  | Warranty Type |  |  |
| `start_date` | Date |  | Start Date | ✓ |  |
| `end_date` | Date |  | End Date | ✓ |  |
| `is_expired` | Boolean |  | Expired |  | C |
| `contact` | Char |  | Contact |  |  |
| `note` | Text |  | Note |  |  |

### `hr.employee` *(extend)*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `assigned_asset_ids` | One2many | `dcg.asset.assignment` | Asset Assignments |  |  |
| `assigned_asset_count` | Integer |  |  |  | C |

## 19. dcg_knowledge_sop

**Depends:** `mail`, `dcg_master_data`, `dcg_project_delivery`, `dcg_helpdesk_warranty`

**Models:** 5 new

### `dcg.knowledge.article`
*Knowledge Article*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `title` | Char |  | Title | ✓ |  |
| `code` | Char |  | Article Code |  |  |
| `sequence` | Integer |  |  |  |  |
| `active` | Boolean |  |  |  |  |
| `company_id` | Many2one | `res.company` | Company |  |  |
| `article_type` | Selection | `ARTICLE_TYPE_SELECTION` | Type | ✓ |  |
| `category_id` | Many2one | `dcg.knowledge.category` | Category |  |  |
| `tag_ids` | Many2many | `dcg.knowledge.tag` | Tags |  |  |
| `audience` | Selection | `ARTICLE_AUDIENCE_SELECTION` | Audience |  |  |
| `summary` | Text |  | Summary |  |  |
| `content` | Html |  | Content |  |  |
| `question` | Text |  | Question |  |  |
| `answer` | Html |  | Answer |  |  |
| `problem` | Html |  | Problem |  |  |
| `solution` | Html |  | Solution |  |  |
| `root_cause` | Html |  | Root Cause |  |  |
| `state` | Selection | `ARTICLE_STATE_SELECTION` | Status | ✓ |  |
| `author_id` | Many2one | `res.users` | Author |  |  |
| `reviewer_id` | Many2one | `res.users` | Reviewer |  |  |
| `published_date` | Date |  | Published Date |  |  |
| `expiry_date` | Date |  | Expiry Date |  |  |
| `is_expired` | Boolean |  |  |  | C |
| `view_count` | Integer |  | Views |  |  |
| `like_count` | Integer |  | Likes |  |  |
| `is_pinned` | Boolean |  | Pinned |  |  |
| `is_featured` | Boolean |  | Featured |  |  |
| `project_id` | Many2one | `dcg.project.delivery` | Project |  |  |
| `ticket_id` | Many2one | `dcg.warranty.ticket` | Ticket |  |  |
| `module_name` | Char |  | Module |  |  |
| `keyword` | Char |  | Keywords |  |  |
| `attachment_ids` | Many2many | `ir.attachment` | Attachments |  |  |
| `revision_ids` | One2many | `dcg.knowledge.revision` | Revisions |  |  |
| `current_version` | Char |  | Version |  |  |
| `feedback_ids` | One2many | `dcg.knowledge.feedback` | Feedback |  |  |
| `avg_rating` | Float |  | Avg Rating |  | C |

### `dcg.knowledge.category`
*Knowledge Category*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `name` | Char |  | Category | ✓ |  |
| `code` | Char |  | Code |  |  |
| `sequence` | Integer |  |  |  |  |
| `active` | Boolean |  |  |  |  |
| `color` | Integer |  | Color |  |  |
| `description` | Text |  | Description |  |  |
| `article_count` | Integer |  |  |  | C |

### `dcg.knowledge.feedback`
*Knowledge Article Feedback*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `article_id` | Many2one | `dcg.knowledge.article` | Article | ✓ |  |
| `user_id` | Many2one | `res.users` | User | ✓ |  |
| `rating` | Float |  |  |  |  |
| `is_helpful` | Boolean |  | Helpful |  |  |
| `comment` | Text |  | Comment |  |  |

### `dcg.knowledge.revision`
*Knowledge Article Revision*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `article_id` | Many2one | `dcg.knowledge.article` | Article | ✓ |  |
| `version` | Char |  | Version | ✓ |  |
| `content_snapshot` | Html |  | Content Snapshot |  |  |
| `change_note` | Text |  | Change Note |  |  |
| `revised_by_id` | Many2one | `res.users` | Revised By |  |  |

### `dcg.knowledge.tag`
*Knowledge Tag*

| Field | Type | Comodel / Ref | String | Req | C/R |
|-------|------|---------------|--------|-----|-----|
| `name` | Char |  | Tag | ✓ |  |
| `group` | Selection | `TAG_GROUP_SELECTION` | Group |  |  |
| `color` | Integer |  | Color |  |  |
| `active` | Boolean |  |  |  |  |

## 20. dcg_dashboard_kpi

**Depends:** `web`, `dcg_master_data`, `dcg_crm_presales`, `dcg_contract_management`, `dcg_project_delivery`, `dcg_timesheet_control`, `dcg_project_finance`, `dcg_helpdesk_warranty`

**Models:** 1 AbstractModel

### `dcg.dashboard.service` *(AbstractModel — không có table)*
*Dashboard KPI Service*

| Method | Data source | Returns |
|--------|------------|---------|
| `get_executive_data()` | contract, project, finance, ticket, employee | revenue, profit, margin, counts |
| `get_sales_data()` | crm.lead, contract, partner | leads, win_rate, top_customers |
| `get_project_data()` | project delivery | by_state, by_health, top_projects, delays |
| `get_resource_data()` | allocation, employee | workload, bench, over_allocated |
| `get_finance_data()` | project finance | P&L, margin, collection, top_margin |
| `get_support_data()` | warranty ticket | open, critical, sla_breached, by_severity |
| `get_asset_data()` | asset, license, warranty | by_stage, expired, expiring |
| `get_hr_data()` | employee, certificate, training | cert_expired, available |
| `get_trip_data()` | business trip | by_state, estimated vs actual cost |
| `get_document_data()` | document | waiting_review, approved, published |
| `get_notifications()` | mail.activity | pending activities for current user |

**Frontend:** 9 OWL dashboards (Home, Executive, Sales, Project, Resource, Finance, Support, Asset) registered via `ir.actions.client`.
