# DEV-READY SPEC – ODOO 18 COMMUNITY
## Bộ đặc tả triển khai kỹ thuật theo module
### Version: v1.0

> Tài liệu này là lớp **dev-ready** tiếp theo của `full_solution_outline_odoo18.md`.
> Mục tiêu: để BA / Tech Lead / Dev Odoo có thể bắt đầu tách task, dựng module, model, view, security và workflow.

---

# 1. Quy ước chung

## 1.1. Quy ước module
Custom module đặt theo prefix:
- `x_master_data`
- `x_approval_matrix`
- `x_crm_presales`
- `x_business_trip`
- `x_contract_management`
- `x_project_delivery`
- `x_timesheet_control`
- `x_capacity_allocation`
- `x_project_finance`
- `x_helpdesk_warranty`
- `x_hr_resource`
- `x_asset_it`
- `x_knowledge_sop`
- `x_dashboard_kpi`

## 1.2. Quy ước kỹ thuật
- Model: `x.module.object`
- XML ID:
  - menu: `menu_*`
  - action: `action_*`
  - sequence: `seq_*`
  - group: `group_*`
  - rule: `rule_*`
  - view: `view_*`
- State field:
  - ưu tiên `draft`, `to_approve`, `approved`, `done`, `cancelled`
- Tất cả model nghiệp vụ chính nên kế thừa:
  - `mail.thread`
  - `mail.activity.mixin`

## 1.3. Quy ước thư mục mỗi module
```python
module_name/
├── __init__.py
├── __manifest__.py
├── security/
│   ├── security.xml
│   └── ir.model.access.csv
├── data/
│   ├── sequence.xml
│   ├── cron.xml
│   ├── mail_template.xml
│   └── master_data.xml
├── models/
│   ├── __init__.py
│   ├── *.py
├── views/
│   ├── menu.xml
│   ├── *_views.xml
│   └── *_wizard_views.xml
├── wizard/
│   ├── __init__.py
│   └── *.py
├── report/
│   ├── *.xml
│   └── *.py
```

---

# 2. Danh sách module dev-ready

1. `x_master_data`
2. `x_approval_matrix`
3. `x_crm_presales`
4. `x_business_trip`
5. `x_contract_management`
6. `x_project_delivery`
7. `x_timesheet_control`
8. `x_capacity_allocation`
9. `x_project_finance`
10. `x_helpdesk_warranty`
11. `x_hr_resource`
12. `x_asset_it`
13. `x_knowledge_sop`
14. `x_dashboard_kpi`

---

# 3. APP 01 – `x_master_data`

# 3.1. Mục tiêu
Lưu master data dùng chung cho toàn hệ thống:
- ngành khách hàng
- nguồn khách hàng
- dịch vụ
- loại hợp đồng
- loại phụ lục
- loại nghiệm thu
- ticket type / severity / priority
- SLA policy
- loại chi phí
- cost center
- KPI target
- alert rule

---

# 3.2. `__manifest__.py`

```python
{
    'name': 'Master Data',
    'version': '18.0.1.0.0',
    'depends': ['base', 'mail', 'hr'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/master_data.xml',
        'views/menu.xml',
        'views/customer_industry_views.xml',
        'views/customer_source_views.xml',
        'views/service_catalog_views.xml',
        'views/contract_type_views.xml',
        'views/ticket_master_views.xml',
        'views/sla_policy_views.xml',
        'views/expense_type_views.xml',
        'views/cost_center_views.xml',
        'views/kpi_target_views.xml',
        'views/alert_rule_views.xml',
    ],
    'installable': True,
}
```

---

# 3.3. Models

## 3.3.1. `x.customer.industry`
### Fields
- `name` – Char, required, tracking
- `code` – Char, index
- `active` – Boolean, default=True
- `note` – Text

### SQL constraint
- unique `code`

### Views
- tree: code, name, active
- form: general + note
- search: name, code, active

---

## 3.3.2. `x.customer.source`
### Fields
- `name`
- `code`
- `active`
- `note`

---

## 3.3.3. `x.service.catalog`
### Fields
- `name`
- `code`
- `service_type` = implementation/support/license/consulting/training
- `description`
- `active`

---

## 3.3.4. `x.contract.type`
## 3.3.5. `x.contract.appendix.type`
## 3.3.6. `x.acceptance.type`

Các model trên cùng cấu trúc:
- `name`
- `code`
- `description`
- `active`

---

## 3.3.7. `x.ticket.type`
## 3.3.8. `x.ticket.severity`
## 3.3.9. `x.ticket.priority`

### `x.ticket.severity`
Nên có field:
- `response_hours_default`
- `resolution_hours_default`
- `sequence`

---

## 3.3.10. `x.sla.policy`
### Fields
- `name`
- `code`
- `ticket_type_id`
- `severity_id`
- `response_hours`
- `resolution_hours`
- `working_calendar_id`
- `active`

---

## 3.3.11. `x.expense.type`
### Fields
- `name`
- `code`
- `expense_group`
- `is_billable`
- `active`

---

## 3.3.12. `x.cost.center`
### Fields
- `name`
- `code`
- `manager_id`
- `active`

---

## 3.3.13. `x.kpi.target`
### Fields
- `name`
- `target_type`
- `department_id`
- `owner_id`
- `period_type`
- `target_value`
- `unit`
- `active`

---

## 3.3.14. `x.alert.rule`
### Fields
- `name`
- `rule_type`
- `model_name`
- `condition_json`
- `recipient_group_ids`
- `active`

---

# 3.4. Menu
## Root menu
- Cấu hình

## Child menu
- Ngành khách hàng
- Nguồn khách hàng
- Danh mục dịch vụ
- Loại hợp đồng
- Loại phụ lục
- Loại nghiệm thu
- Ticket Type
- Ticket Severity
- Ticket Priority
- SLA Policy
- Loại chi phí
- Cost Center
- KPI Target
- Alert Rule

---

# 3.5. Security
## Groups
- `group_master_data_user`
- `group_master_data_manager`

## Access
- user: read
- manager: full CRUD

---

# 3.6. Dev task breakdown
1. Tạo toàn bộ model master
2. Tạo menu config
3. Tạo tree/form/search cho từng master
4. Tạo security + access
5. Tạo master data demo nếu cần

---

# 4. APP 02 – `x_approval_matrix`

# 4.1. Mục tiêu
Engine phê duyệt dùng chung.

---

# 4.2. `__manifest__.py`

```python
{
    'name': 'Approval Matrix',
    'version': '18.0.1.0.0',
    'depends': ['mail', 'x_master_data'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/menu.xml',
        'views/approval_matrix_views.xml',
        'views/approval_request_views.xml',
    ],
    'installable': True,
}
```

---

# 4.3. Models

## 4.3.1. `x.approval.matrix`
### Fields
- `name`
- `approval_type`
- `company_id`
- `department_id`
- `active`
- `note`

## 4.3.2. `x.approval.matrix.line`
### Fields
- `matrix_id`
- `sequence`
- `approver_type`
- `user_id`
- `group_id`
- `condition_json`
- `min_amount`
- `max_amount`

## 4.3.3. `x.approval.request`
### Fields
- `name`
- `approval_type`
- `res_model`
- `res_id`
- `requester_id`
- `current_step`
- `state`
- `requested_date`
- `approved_date`
- `reject_reason`

## 4.3.4. `x.approval.log`
### Fields
- `request_id`
- `sequence`
- `approver_id`
- `action`
- `action_date`
- `note`

---

# 4.4. Service / mixin khuyến nghị
Tạo abstract model:
## `x.approval.mixin`
### Fields
- `approval_request_id`
- `approval_state`

### Methods
- `action_submit_approval()`
- `_get_approval_type()`
- `_get_approval_amount()`
- `_get_approval_department()`
- `_approval_approved_callback()`
- `_approval_rejected_callback()`

Các module nghiệp vụ kế thừa mixin này.

---

# 4.5. Menu
- Approval
  - Ma trận phê duyệt
  - Yêu cầu chờ duyệt
  - Lịch sử duyệt

---

# 4.6. Security
## Groups
- `group_approval_user`
- `group_approval_manager`

---

# 4.7. Dev task breakdown
1. Tạo matrix + line + request + log
2. Tạo approval mixin
3. Tạo form approve/reject
4. Tạo menu approval
5. Tích hợp callback cho module nghiệp vụ

---

# 5. APP 03 – `x_crm_presales`

# 5.1. Mục tiêu
Mở rộng CRM theo quy trình presales:
- requirement survey
- scope
- estimate
- presales cost
- approval deal

---

# 5.2. `__manifest__.py`

```python
{
    'name': 'CRM Presales',
    'version': '18.0.1.0.0',
    'depends': ['crm', 'sale', 'contacts', 'x_master_data', 'x_approval_matrix'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/res_partner_views.xml',
        'views/crm_lead_views.xml',
        'views/crm_requirement_views.xml',
        'views/crm_solution_scope_views.xml',
        'views/crm_estimate_views.xml',
        'views/crm_presales_cost_views.xml',
    ],
    'installable': True,
}
```

---

# 5.3. Kế thừa `res.partner`

## Fields
- `is_company_customer`
- `customer_code`
- `tax_code`
- `industry_id`
- `source_id`
- `account_manager_id`
- `customer_rank_level`
- `cooperation_status`
- `debt_risk_level`
- `support_level`
- `note_internal`

## Smart buttons
- Opportunities
- Quotations
- Contracts
- Projects
- Tickets

---

# 5.4. Kế thừa `crm.lead`

## Fields
- `opportunity_code`
- `customer_need_summary`
- `pain_point`
- `business_goal`
- `competitor_info`
- `risk_note`
- `solution_scope_summary`
- `estimated_ba_hours`
- `estimated_dev_hours`
- `estimated_test_hours`
- `estimated_pm_hours`
- `estimated_cost`
- `estimated_margin`
- `presales_cost_amount`
- `deal_approval_state`

## Buttons
- Tạo khảo sát
- Tạo estimate
- Gửi duyệt deal
- Tạo báo giá

---

# 5.5. Models

## `x.crm.requirement`
### Fields
- `name`
- `lead_id`
- `partner_id`
- `survey_date`
- `owner_id`
- `current_system`
- `pain_point`
- `business_goal`
- `scope_summary`
- `department_involved`
- `input_data_desc`
- `output_data_desc`
- `attachment_ids`

## `x.crm.solution.scope`
### Fields
- `name`
- `lead_id`
- `service_catalog_id`
- `scope_type`
- `description`
- `sequence`

## `x.crm.estimate`
### Fields
- `name`
- `lead_id`
- `version`
- `estimated_ba_hours`
- `estimated_dev_hours`
- `estimated_test_hours`
- `estimated_pm_hours`
- `estimated_support_hours`
- `estimated_cost`
- `estimated_revenue`
- `estimated_margin`
- `estimated_timeline_days`
- `state`

## `x.crm.presales.cost`
### Fields
- `name`
- `lead_id`
- `expense_type_id`
- `trip_id`
- `expense_date`
- `description`
- `amount`
- `currency_id`
- `attachment_ids`

---

# 5.6. Views
## `crm.lead` form tabs
- Overview
- Requirement Survey
- Solution Scope
- Estimate
- Presales Cost
- Approval

## Search filters
- my opportunities
- high risk
- low margin
- waiting approval

---

# 5.7. Security
## Groups
- `group_presales_user`
- `group_presales_manager`

---

# 5.8. Dev task breakdown
1. Kế thừa partner
2. Kế thừa lead
3. Tạo 4 model presales
4. Tạo tab trên lead form
5. Tạo button tạo báo giá / approval
6. Tạo domain & smart button

---

# 6. APP 04 – `x_business_trip`

# 6.1. Mục tiêu
Quản lý công tác / onsite / tạm ứng / chi phí / quyết toán.

---

# 6.2. `__manifest__.py`

```python
{
    'name': 'Business Trip',
    'version': '18.0.1.0.0',
    'depends': ['mail', 'hr', 'account', 'x_master_data', 'x_approval_matrix'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/menu.xml',
        'views/business_trip_views.xml',
        'views/business_trip_settlement_views.xml',
    ],
    'installable': True,
}
```

---

# 6.3. Models

## `x.business.trip`
### Fields
- `name`
- `trip_type`
- `partner_id`
- `lead_id`
- `project_id`
- `ticket_id`
- `purpose`
- `destination`
- `date_start`
- `date_end`
- `requester_id`
- `approver_id`
- `state`
- `budget_amount`
- `advance_amount`
- `actual_amount`
- `settlement_amount`
- `result_summary`
- `approval_request_id`
- `approval_state`

## `x.business.trip.member`
- `trip_id`
- `employee_id`
- `role`

## `x.business.trip.advance`
- `trip_id`
- `employee_id`
- `request_date`
- `amount`
- `currency_id`
- `payment_status`

## `x.business.trip.expense`
- `trip_id`
- `expense_type_id`
- `expense_date`
- `description`
- `amount`
- `currency_id`
- `vendor`
- `attachment_ids`

## `x.business.trip.settlement`
- `trip_id`
- `advance_amount`
- `actual_amount`
- `refund_amount`
- `additional_claim_amount`
- `settlement_date`
- `state`

## `x.business.trip.report`
- `trip_id`
- `report_type`
- `content_html`
- `result_summary`
- `followup_action`

---

# 6.4. Views
## Trip form tabs
- General
- Members
- Advance
- Expenses
- Settlement
- Report
- Approval

---

# 6.5. Workflow
draft → to_approve → approved → in_progress → done  
Nếu có settlement: done sau khi settlement complete

---

# 6.6. Security
## Groups
- `group_trip_user`
- `group_trip_manager`

---

# 6.7. Dev task breakdown
1. Tạo trip model + sequence
2. Tạo child line models
3. Tạo form nhiều tab
4. Tích hợp approval
5. Tạo report quyết toán / biên bản

---

# 7. APP 05 – `x_contract_management`

# 7.1. Mục tiêu
Quản lý báo giá → hợp đồng → phụ lục → lịch thanh toán → nghiệm thu → bảo hành.

---

# 7.2. `__manifest__.py`

```python
{
    'name': 'Contract Management',
    'version': '18.0.1.0.0',
    'depends': ['sale', 'account', 'project', 'mail', 'x_master_data', 'x_approval_matrix'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/menu.xml',
        'views/sale_order_views.xml',
        'views/contract_views.xml',
        'views/contract_appendix_views.xml',
        'views/contract_acceptance_views.xml',
    ],
    'installable': True,
}
```

---

# 7.3. Kế thừa `sale.order`

## Fields
- `lead_id`
- `presales_scope_summary`
- `delivery_timeline_note`
- `payment_term_note_custom`
- `approval_state`
- `expected_margin`
- `contract_ready`

---

# 7.4. Models

## `x.contract`
### Fields
- `name`
- `contract_no`
- `partner_id`
- `lead_id`
- `sale_order_id`
- `contract_type_id`
- `date_signed`
- `date_start`
- `date_end`
- `currency_id`
- `amount_untaxed`
- `amount_total`
- `project_manager_id`
- `sale_owner_id`
- `state`
- `payment_term_summary`
- `warranty_start_date`
- `warranty_end_date`
- `support_package`
- `note_scope`
- `note_exclusion`
- `approval_request_id`
- `approval_state`

## `x.contract.line`
- `contract_id`
- `sequence`
- `name`
- `service_catalog_id`
- `qty`
- `price_unit`
- `subtotal`
- `delivery_note`

## `x.contract.appendix`
- `contract_id`
- `name`
- `appendix_no`
- `appendix_type_id`
- `date_signed`
- `amount_delta`
- `timeline_delta`
- `scope_change_summary`
- `state`
- `approval_request_id`
- `approval_state`

## `x.contract.payment.schedule`
- `contract_id`
- `name`
- `milestone`
- `due_date`
- `amount`
- `percent`
- `condition_note`
- `invoice_status`
- `payment_status`

## `x.contract.acceptance`
- `contract_id`
- `project_id`
- `acceptance_type_id`
- `acceptance_date`
- `amount_to_invoice`
- `status`
- `signed_file`
- `note`

## `x.contract.warranty`
- `contract_id`
- `warranty_type`
- `start_date`
- `end_date`
- `sla_policy_id`
- `support_scope`
- `note`

---

# 7.5. Buttons / actions
## On `x.contract`
- Submit approval
- Approve / reject
- Activate contract
- Create project
- Generate payment schedule
- Create warranty entitlement

---

# 7.6. Views
## Contract form tabs
- General
- Lines
- Payment Schedule
- Acceptance
- Warranty
- Appendices
- Documents
- Approval

---

# 7.7. Security
## Groups
- `group_contract_user`
- `group_contract_manager`

---

# 7.8. Dev task breakdown
1. Kế thừa sale.order
2. Tạo contract + line + appendix + schedule + acceptance + warranty
3. Tạo contract sequence
4. Tạo contract form + smart buttons
5. Tích hợp approval
6. Hook tạo project

---

# 8. APP 06 – `x_project_delivery`

# 8.1. Mục tiêu
Mở rộng project thành trung tâm delivery.

---

# 8.2. `__manifest__.py`

```python
{
    'name': 'Project Delivery',
    'version': '18.0.1.0.0',
    'depends': ['project', 'mail', 'x_contract_management', 'x_master_data'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/project_project_views.xml',
        'views/project_task_views.xml',
        'views/project_phase_views.xml',
        'views/project_risk_views.xml',
        'views/project_issue_views.xml',
        'views/project_change_request_views.xml',
    ],
    'installable': True,
}
```

---

# 8.3. Kế thừa `project.project`

## Fields
- `contract_id`
- `lead_id`
- `project_code`
- `project_type`
- `delivery_status`
- `health_status`
- `date_kickoff`
- `date_go_live`
- `date_warranty_end`
- `planned_hours`
- `actual_hours`
- `planned_cost`
- `actual_cost`
- `planned_revenue`
- `actual_revenue`
- `margin_amount`
- `margin_rate`
- `customer_pm_name`
- `customer_pm_contact`

---

# 8.4. Kế thừa `project.task`

## Fields
- `task_type`
- `epic`
- `sprint`
- `billable`
- `priority_business`
- `blocked_by_task_ids`
- `delivery_phase_id`
- `contract_id`
- `ticket_id`
- `customer_visible`
- `qa_status`

---

# 8.5. Models

## `x.project.phase`
- `project_id`
- `name`
- `sequence`
- `date_start`
- `date_end`
- `status`
- `owner_id`
- `completion_rate`

## `x.project.scope.module`
- `project_id`
- `module_name`
- `scope_type`
- `description`
- `in_scope`
- `phase_id`

## `x.project.member`
- `project_id`
- `employee_id`
- `role`
- `allocation_percent`
- `date_from`
- `date_to`
- `is_billable`

## `x.project.risk`
- `project_id`
- `name`
- `risk_type`
- `impact_level`
- `probability_level`
- `owner_id`
- `mitigation_action`
- `target_date`
- `state`

## `x.project.issue`
- `project_id`
- `name`
- `issue_type`
- `severity`
- `owner_id`
- `opened_date`
- `due_date`
- `resolution_note`
- `state`

## `x.project.change.request`
- `project_id`
- `contract_id`
- `name`
- `request_source`
- `change_summary`
- `impact_scope`
- `impact_timeline`
- `impact_cost`
- `decision`
- `approval_request_id`
- `approval_state`

## `x.project.weekly.report`
- `project_id`
- `week_start`
- `week_end`
- `summary`
- `progress_note`
- `risk_note`
- `issue_note`
- `next_action`
- `health_status`

## `x.project.meeting.minute`
- `project_id`
- `meeting_date`
- `meeting_type`
- `participant_ids`
- `content_html`
- `decision_summary`
- `followup_action`

---

# 8.6. Views
## Project form tabs
- Overview
- Phases
- Scope Modules
- Members
- Tasks
- Risks
- Issues
- Change Requests
- Weekly Reports
- MOM

---

# 8.7. Security
## Groups
- `group_project_pm`
- `group_project_member`
- `group_pmo_manager`

---

# 8.8. Dev task breakdown
1. Kế thừa project.project
2. Kế thừa project.task
3. Tạo risk / issue / CR / phase / member
4. Tạo project form nhiều tab
5. Tạo weekly report / MOM
6. Tích hợp CR approval

---

# 9. APP 07 – `x_timesheet_control`

# 9.1. Mục tiêu
Bổ sung kiểm soát timesheet, approval, lock kỳ.

---

# 9.2. `__manifest__.py`

```python
{
    'name': 'Timesheet Control',
    'version': '18.0.1.0.0',
    'depends': ['hr_timesheet', 'x_project_delivery', 'x_approval_matrix'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/cron.xml',
        'views/menu.xml',
        'views/account_analytic_line_views.xml',
        'views/timesheet_period_views.xml',
        'views/timesheet_approval_views.xml',
    ],
    'installable': True,
}
```

---

# 9.3. Kế thừa `account.analytic.line`

## Fields
- `contract_id`
- `billable`
- `work_type`
- `approval_state`
- `timesheet_period_id`
- `cost_amount`
- `revenue_amount`
- `overtime_flag`

---

# 9.4. Models

## `x.timesheet.period`
- `name`
- `date_from`
- `date_to`
- `state`
- `lock_date`

## `x.timesheet.approval`
- `name`
- `employee_id`
- `manager_id`
- `date_from`
- `date_to`
- `project_id`
- `total_hours`
- `billable_hours`
- `state`
- `approval_request_id`

---

# 9.5. Chức năng
- submit timesheet theo kỳ
- approve batch
- lock period
- cảnh báo thiếu timesheet

---

# 9.6. Cron
- nhắc log timesheet
- lock kỳ cuối tháng / theo cấu hình

---

# 9.7. Security
## Groups
- `group_timesheet_user`
- `group_timesheet_manager`

---

# 9.8. Dev task breakdown
1. Kế thừa analytic line
2. Tạo period + approval batch
3. Tạo cron reminder
4. Tạo logic lock period
5. Tạo approval flow

---

# 10. APP 08 – `x_capacity_allocation`

# 10.1. Mục tiêu
Quản lý phân bổ nguồn lực / utilization.

---

# 10.2. `__manifest__.py`

```python
{
    'name': 'Capacity Allocation',
    'version': '18.0.1.0.0',
    'depends': ['hr', 'project', 'x_project_delivery', 'x_timesheet_control'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/resource_allocation_views.xml',
        'views/resource_capacity_snapshot_views.xml',
    ],
    'installable': True,
}
```

---

# 10.3. Models

## `x.resource.allocation`
- `employee_id`
- `project_id`
- `contract_id`
- `role`
- `date_from`
- `date_to`
- `allocation_percent`
- `planned_hours`
- `manager_id`
- `state`

## `x.resource.capacity.snapshot`
- `employee_id`
- `period_start`
- `period_end`
- `capacity_hours`
- `allocated_hours`
- `timesheet_hours`
- `utilization_rate`
- `overload_flag`

---

# 10.4. Views
- allocation tree / form
- heatmap / pivot / graph nếu có

---

# 10.5. Security
## Groups
- `group_capacity_user`
- `group_capacity_manager`

---

# 10.6. Dev task breakdown
1. Tạo allocation model
2. Tạo snapshot model
3. Tạo report utilization
4. Tạo cảnh báo over-allocation

---

# 11. APP 09 – `x_project_finance`

# 11.1. Mục tiêu
Tính management finance theo contract / project.

---

# 11.2. `__manifest__.py`

```python
{
    'name': 'Project Finance',
    'version': '18.0.1.0.0',
    'depends': [
        'account',
        'analytic',
        'hr_timesheet',
        'x_contract_management',
        'x_project_delivery',
        'x_business_trip',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/cron.xml',
        'views/menu.xml',
        'views/project_finance_snapshot_views.xml',
        'views/project_cost_line_views.xml',
        'views/cashflow_forecast_views.xml',
    ],
    'installable': True,
}
```

---

# 11.3. Models

## `x.project.finance.snapshot`
- `partner_id`
- `contract_id`
- `project_id`
- `period_month`
- `contract_value`
- `recognized_revenue`
- `invoiced_amount`
- `collected_amount`
- `timesheet_cost`
- `trip_cost`
- `external_cost`
- `license_cost`
- `other_cost`
- `total_cost`
- `margin_amount`
- `margin_rate`
- `overdue_amount`

## `x.project.cost.line`
- `project_id`
- `contract_id`
- `cost_type`
- `source_model`
- `source_res_id`
- `cost_date`
- `description`
- `amount`
- `currency_id`

## `x.receivable.alert`
- `partner_id`
- `contract_id`
- `invoice_id`
- `due_date`
- `overdue_days`
- `amount_due`
- `state`

## `x.cashflow.forecast`
- `contract_id`
- `project_id`
- `forecast_date`
- `forecast_amount`
- `forecast_type`
- `confidence_rate`
- `note`

---

# 11.4. Chức năng
- snapshot doanh thu / chi phí / margin
- overdue receivable
- cash-in forecast
- cost burn rate

---

# 11.5. Cron
- nightly finance snapshot
- overdue receivable scan

---

# 11.6. Security
## Groups
- `group_project_finance_user`
- `group_project_finance_manager`

---

# 11.7. Dev task breakdown
1. Tạo snapshot model
2. Tạo cost aggregation logic
3. Tạo cron snapshot
4. Tạo dashboard/report finance
5. Tạo receivable alert

---

# 12. APP 10 – `x_helpdesk_warranty`

# 12.1. Mục tiêu
Quản lý support / warranty / SLA / RCA.

---

# 12.2. `__manifest__.py`

```python
{
    'name': 'Helpdesk Warranty',
    'version': '18.0.1.0.0',
    'depends': ['mail', 'project', 'x_contract_management', 'x_master_data'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/cron.xml',
        'views/menu.xml',
        'views/helpdesk_ticket_views.xml',
        'views/helpdesk_rca_views.xml',
        'views/helpdesk_csat_views.xml',
    ],
    'installable': True,
}
```

---

# 12.3. Triển khai
## Nếu dùng `helpdesk.ticket`
Kế thừa model đó

## Nếu không có helpdesk phù hợp
Tạo model `x.helpdesk.ticket`

---

# 12.4. Fields ticket
- `name`
- `ticket_no`
- `partner_id`
- `contract_id`
- `project_id`
- `warranty_id`
- `ticket_type_id`
- `severity_id`
- `priority_id`
- `sla_policy_id`
- `response_deadline`
- `resolve_deadline`
- `sla_state`
- `root_cause`
- `solution_summary`
- `onsite_required`
- `csat_score`
- `state`

---

# 12.5. Models

## `x.helpdesk.ticket.rca`
- `ticket_id`
- `root_cause`
- `solution`
- `preventive_action`
- `owner_id`

## `x.helpdesk.onsite`
- `ticket_id`
- `trip_id`
- `onsite_date`
- `engineer_id`
- `result_summary`

## `x.helpdesk.csat`
- `ticket_id`
- `partner_id`
- `score`
- `comment`
- `submitted_date`

## `x.helpdesk.warranty.entitlement`
- `contract_id`
- `partner_id`
- `start_date`
- `end_date`
- `sla_policy_id`
- `support_scope`
- `active`

---

# 12.6. Workflow
new → triage → assigned → in_progress → waiting_customer / waiting_dev → resolved → closed

---

# 12.7. Cron
- SLA breach checker
- overdue ticket reminder

---

# 12.8. Security
## Groups
- `group_support_user`
- `group_support_manager`

---

# 12.9. Dev task breakdown
1. Chốt strategy helpdesk core/custom
2. Tạo ticket fields + SLA logic
3. Tạo RCA / CSAT / onsite
4. Tạo cron SLA
5. Tạo KB hook sau khi resolved

---

# 13. APP 11 – `x_hr_resource`

# 13.1. Mục tiêu
Quản lý skill, delivery role, KPI nguồn lực.

---

# 13.2. `__manifest__.py`

```python
{
    'name': 'HR Resource',
    'version': '18.0.1.0.0',
    'depends': ['hr', 'hr_contract', 'x_capacity_allocation'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/hr_employee_views.xml',
        'views/employee_skill_views.xml',
        'views/employee_certificate_views.xml',
        'views/employee_kpi_views.xml',
    ],
    'installable': True,
}
```

---

# 13.3. Kế thừa `hr.employee`

## Fields
- `employee_code`
- `job_family`
- `delivery_role`
- `hour_cost`
- `billable_target`
- `utilization_target`
- `skill_summary`

---

# 13.4. Models

## `x.employee.skill`
- `name`
- `category`
- `active`

## `x.employee.skill.line`
- `employee_id`
- `skill_id`
- `level`
- `years_exp`
- `last_used_date`
- `note`

## `x.employee.certificate`
- `employee_id`
- `name`
- `issuer`
- `issue_date`
- `expiry_date`
- `attachment_ids`

## `x.employee.kpi`
- `employee_id`
- `period`
- `billable_rate`
- `utilization_rate`
- `overtime_hours`
- `score`
- `note`

---

# 13.5. Security
## Groups
- `group_hr_resource_user`
- `group_hr_resource_manager`

---

# 13.6. Dev task breakdown
1. Kế thừa hr.employee
2. Tạo skill / certificate / KPI
3. Tạo tab skill / certificate trên employee form
4. Tạo report utilization / KPI

---

# 14. APP 12 – `x_asset_it`

# 14.1. Mục tiêu
Quản lý tài sản IT, cấp phát, license, bảo trì.

---

# 14.2. `__manifest__.py`

```python
{
    'name': 'Asset IT',
    'version': '18.0.1.0.0',
    'depends': ['hr', 'mail', 'x_master_data', 'x_approval_matrix'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/cron.xml',
        'data/sequence.xml',
        'views/menu.xml',
        'views/asset_item_views.xml',
        'views/asset_assignment_views.xml',
        'views/software_license_views.xml',
    ],
    'installable': True,
}
```

---

# 14.3. Models

## `x.asset.item`
- `name`
- `asset_code`
- `asset_type`
- `brand`
- `model`
- `serial_no`
- `purchase_date`
- `warranty_end_date`
- `asset_status`
- `current_holder_id`
- `assigned_project_id`
- `location`
- `note`

## `x.asset.assignment`
- `asset_id`
- `employee_id`
- `project_id`
- `date_assign`
- `date_return`
- `condition_assign`
- `condition_return`
- `state`

## `x.asset.maintenance`
- `asset_id`
- `maintenance_date`
- `maintenance_type`
- `vendor`
- `cost`
- `result_note`

## `x.software.license`
- `name`
- `vendor`
- `license_key`
- `license_type`
- `qty`
- `date_start`
- `date_end`
- `assigned_to`
- `renewal_cost`
- `state`

---

# 14.4. Cron
- license expiry reminder
- warranty expiry reminder

---

# 14.5. Security
## Groups
- `group_asset_user`
- `group_asset_manager`

---

# 14.6. Dev task breakdown
1. Tạo asset item / assignment / maintenance / license
2. Tạo cấp phát / thu hồi
3. Tạo cảnh báo hết hạn
4. Tích hợp approval nếu cần mua / cấp phát

---

# 15. APP 13 – `x_knowledge_sop`

# 15.1. Mục tiêu
Lưu SOP / KB / FAQ / lesson learned / project docs.

---

# 15.2. `__manifest__.py`

```python
{
    'name': 'Knowledge SOP',
    'version': '18.0.1.0.0',
    'depends': ['mail', 'project', 'x_helpdesk_warranty'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/knowledge_category_views.xml',
        'views/knowledge_article_views.xml',
    ],
    'installable': True,
}
```

---

# 15.3. Models

## `x.knowledge.category`
- `name`
- `parent_id`
- `sequence`

## `x.knowledge.tag`
- `name`
- `color`

## `x.knowledge.article`
- `name`
- `category_id`
- `tag_ids`
- `article_type`
- `project_id`
- `ticket_id`
- `contract_id`
- `owner_id`
- `reviewer_id`
- `version`
- `state`
- `content_html`
- `summary`
- `published_date`

---

# 15.4. Workflow
draft → review → published → archived

---

# 15.5. Security
## Groups
- `group_knowledge_user`
- `group_knowledge_manager`

---

# 15.6. Dev task breakdown
1. Tạo category/tag/article
2. Tạo editor nội dung
3. Tạo link từ project/ticket/contract
4. Tạo search / filter article type

---

# 16. APP 14 – `x_dashboard_kpi`

# 16.1. Mục tiêu
Dashboard điều hành, KPI, alert center.

---

# 16.2. `__manifest__.py`

```python
{
    'name': 'Dashboard KPI',
    'version': '18.0.1.0.0',
    'depends': [
        'x_crm_presales',
        'x_contract_management',
        'x_project_delivery',
        'x_timesheet_control',
        'x_project_finance',
        'x_helpdesk_warranty',
        'x_hr_resource',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/cron.xml',
        'views/menu.xml',
        'views/dashboard_snapshot_views.xml',
        'views/alert_log_views.xml',
        'views/dashboard_templates.xml',
    ],
    'installable': True,
}
```

---

# 16.3. Models

## `x.dashboard.snapshot`
- `snapshot_date`
- `dashboard_type`
- `payload_json`

## `x.alert.log`
- `rule_id`
- `res_model`
- `res_id`
- `message`
- `level`
- `state`
- `created_at`

---

# 16.4. Dashboard cần dựng
## Sales
- pipeline
- open opportunities
- forecast revenue

## Delivery
- project health
- overdue tasks
- issue / CR

## Finance
- margin
- receivable overdue
- cash-in forecast

## Support
- open tickets
- SLA breach
- MTTR

## HR
- utilization
- billable / non-billable
- overload

---

# 16.5. Security
## Groups
- `group_dashboard_user`
- `group_dashboard_manager`

---

# 16.6. Dev task breakdown
1. Chốt KPI đầu vào
2. Tạo model snapshot
3. Tạo cron snapshot
4. Dựng dashboard template / action client
5. Tạo alert log / badge cảnh báo

---

# 17. Mapping dữ liệu liên module

# 17.1. CRM → Contract
- `crm.lead` → `sale.order`
- `crm.lead` → `x.contract`

# 17.2. Contract → Project
- `x.contract` → `project.project`

# 17.3. Project → Task / Timesheet
- `project.project` → `project.task`
- `project.task` → `account.analytic.line`

# 17.4. Contract / Project → Finance
- `x.contract.payment.schedule`
- `x.contract.acceptance`
- `account.move`
- `account.payment`
- `account.analytic.line`
- `x.business.trip.expense`

# 17.5. Contract / Project → Helpdesk
- `x.contract.warranty`
- `x.helpdesk.warranty.entitlement`
- `ticket.project_id`
- `ticket.contract_id`

# 17.6. Ticket / Project → Knowledge
- `ticket_id`
- `project_id`
- `contract_id`

---

# 18. Ưu tiên code theo sprint

## Sprint 1
- `x_master_data`
- `x_approval_matrix`
- `x_crm_presales`

## Sprint 2
- `x_business_trip`
- `x_contract_management`

## Sprint 3
- `x_project_delivery`
- `x_timesheet_control`

## Sprint 4
- `x_capacity_allocation`
- `x_project_finance`

## Sprint 5
- `x_helpdesk_warranty`
- `x_knowledge_sop`

## Sprint 6
- `x_hr_resource`
- `x_asset_it`
- `x_dashboard_kpi`

---

# 19. Gợi ý bước tiếp theo

Sau file dev-ready này, nên viết tiếp 3 loại tài liệu nhỏ hơn:

## 19.1. Module Spec riêng từng app
Ví dụ: `x_contract_management_spec.md`
- model chi tiết
- field type
- required / readonly / tracking
- business rule
- action button
- security

## 19.2. Screen Spec
Ví dụ:
- contract form spec
- project form spec
- ticket form spec
- trip settlement spec

## 19.3. Task breakdown theo dev
Ví dụ cho `x_contract_management`
- task 1: tạo model contract
- task 2: tạo line + appendix
- task 3: tạo payment schedule
- task 4: tạo approval flow
- task 5: tạo form + smart button

---

# 20. Kết luận

Tài liệu này đã nâng blueprint lên mức **dev-ready solution**:
- có **danh sách app**
- có **manifest dependency**
- có **model / field chính**
- có **menu / view / security / workflow**
- có **task breakdown theo module**

Nếu đi tiếp, bước hợp lý nhất là **tách riêng từng app thành spec đầy đủ để dev code trực tiếp**.

Ưu tiên nên làm tiếp theo thứ tự:
1. `x_contract_management_spec.md`
2. `x_project_delivery_spec.md`
3. `x_helpdesk_warranty_spec.md`
4. `x_project_finance_spec.md`
