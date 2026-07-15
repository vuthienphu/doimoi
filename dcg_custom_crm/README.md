# DCG Custom CRM

Module: `dcg_custom_crm`

Odoo version: `19.0`

## 1. Muc tieu

Module bo sung chuc nang quan ly hoa hong ban hang cho CRM Odoo 19, dong thoi kiem soat quy trinh Khao sat, Demo va tu dong tao Du an khi Co hoi duoc chot thanh cong.

## 2. Dependencies

Module phu thuoc cac addon:

- `crm`
- `project`
- `mail`
- `contacts`

## 3. Pham vi nghiep vu

### 3.1. Quan ly hoa hong Bo phan Sales

Model ke thua: `crm.team`

Field bo sung:

| Field | Type | Default | Mo ta |
| --- | --- | --- | --- |
| `commission_rate` | Float | `2.0` | Phan tram hoa hong cua Bo phan Sales |

Quy tac:

- Thay doi `commission_rate` tren Bo phan Sales khong tu dong cap nhat thanh vien.
- Dong bo hoa hong cho thanh vien chi thuc hien qua button `Cap nhat toan bo hoa hong`.
- Button mo wizard xac nhan truoc khi ghi de hoa hong cua thanh vien.
- Chi cap nhat cac `crm.team.member` thuoc team hien tai.
- Sau khi cap nhat, ghi chatter tren team va hien notification so luong thanh vien da cap nhat.

### 3.2. Hoa hong Thanh vien

Model ke thua: `crm.team.member`

Field bo sung:

| Field | Type | Default | Mo ta |
| --- | --- | --- | --- |
| `commission_rate` | Float | Theo `crm_team_id.commission_rate` khi tao moi | Phan tram hoa hong rieng cua thanh vien |

Quy tac:

- Thanh vien moi lay mac dinh hoa hong tu Bo phan Sales.
- Nguoi dung co the sua hoa hong rieng cho tung thanh vien.
- Hoa hong thanh vien khong tu dong thay doi khi sua hoa hong team, tru khi chay wizard dong bo.

### 3.3. Hoa hong tren Co hoi

Model ke thua: `crm.lead`

Field bo sung:

| Field | Type | Attrs | Mo ta |
| --- | --- | --- | --- |
| `commission_rate` | Float, compute, store | readonly | Lay tu `crm.team.member` theo `team_id` va `user_id` |

Compute logic:

```python
member = env['crm.team.member'].search([
    ('crm_team_id', '=', lead.team_id.id),
    ('user_id', '=', lead.user_id.id),
    ('active', '=', True),
], limit=1)
lead.commission_rate = member.commission_rate if member else 0.0
```

### 3.4. Thong tin bo sung tren Co hoi

Model ke thua: `crm.lead`

| Field | Type | Attrs | Mo ta |
| --- | --- | --- | --- |
| `other_ids` | Many2many `res.partner` | Domain `is_company=False` | Nguoi lien he khac |
| `survey_note` | Text | editable | Ghi chu tu do cho khao sat |
| `estimate_attachment_ids` | Many2many `ir.attachment` | editable | File dinh kem uoc tinh cong viec |
| `survey_done` | Boolean | default `False` | Da hoan thanh khao sat |
| `survey_finish_date` | Datetime | readonly | Ngay gio hoan thanh khao sat |
| `demo_done` | Boolean | default `False` | Da hoan thanh demo |
| `demo_finish_date` | Datetime | readonly | Ngay gio hoan thanh demo |
| `project_id` | Many2one `project.project` | editable | Link du an. Neu da co link thi khi Won khong tao du an moi |

## 4. Quy trinh Khao sat

Buttons tren Opportunity:

| Button | Dieu kien hien | Xu ly | Chatter |
| --- | --- | --- | --- |
| `Hoan thanh khao sat` | `survey_done=False` | Set `survey_done=True`, `survey_finish_date=now()` | `Da hoan thanh khao sat ngay [datetime].` |
| `Tiep tuc khao sat` | `survey_done=True` | Mo `crm.survey.wizard` voi `type=survey` | Ghi sau khi confirm wizard |

## 5. Quy trinh Demo

Buttons tren Opportunity:

| Button | Dieu kien hien | Xu ly | Chatter |
| --- | --- | --- | --- |
| `Hoan thanh demo` | `demo_done=False` | Set `demo_done=True`, `demo_finish_date=now()` | `Da hoan thanh demo ngay [datetime].` |
| `Tiep tuc demo` | `demo_done=True` | Mo `crm.survey.wizard` voi `type=demo` | Ghi sau khi confirm wizard |

## 6. Wizard tiep tuc Khao sat/Demo

Model moi: `crm.survey.wizard`

| Field | Type | Required | Mo ta |
| --- | --- | --- | --- |
| `lead_id` | Many2one `crm.lead` | Yes | Co hoi dang thao tac |
| `type` | Selection `survey`, `demo` | Yes | Loai nghiep vu |
| `content` | Text | Yes | Noi dung khao sat/demo them |
| `date_from` | Date | Yes | Ngay bat dau |
| `date_to` | Date | Yes | Ngay ket thuc |

Validation:

- `date_to >= date_from`

Sau khi xac nhan:

- Dong wizard.
- Ghi chatter vao Opportunity.
- Khong thay doi `survey_done` hoac `demo_done`.

Noi dung chatter:

- Survey: `Khao sat them: [noi dung] - Tu [date_from] den [date_to].`
- Demo: `Demo them: [noi dung] - Tu [date_from] den [date_to].`

## 7. Wizard cap nhat hoa hong Team

Model moi: `crm.team.commission.wizard`

| Field | Type | Required | Mo ta |
| --- | --- | --- | --- |
| `team_id` | Many2one `crm.team` | Yes | Bo phan Sales hien tai |
| `commission_rate` | Float | Yes | Ty le hoa hong se dong bo |

Quyen:

- Wizard chi cap cho nhom `sales_team.group_sale_manager`.

Sau khi xac nhan:

- Cap nhat `commission_rate` cua toan bo `crm.team.member` thuoc `team_id`.
- Ghi chatter tren `crm.team`.
- Hien notification thanh cong.

## 8. Tu dong tao Project khi Opportunity Won

Trigger:

- Khi Opportunity duoc set Won bang action goc.
- Khi `stage_id` hoac `probability` thay doi va Opportunity dat dieu kien Won.

Dieu kien tao:

- `type == 'opportunity'`
- Chua co `project_id`
- `probability >= 100` hoac `stage_id.is_won=True`

Project tao moi:

| Field | Gia tri |
| --- | --- |
| `name` | `lead.name` |
| `partner_id` | `lead.partner_id` |
| `user_id` | `lead.user_id` |
| `x_lead_id` | `lead.id` |

Sau khi tao:

- Gan `lead.project_id = project`
- Ghi chatter: `Du an [ten project] da duoc tao lien ket voi Co hoi nay.`

Neu Opportunity da co `project_id`, he thong khong tao them Project moi. Khi da tao Project roi ma chuyen Opportunity ve stage xu ly, link van duoc giu lai; lan sau chuyen Won lai se khong tao trung.

## 9. View da ke thua

### 9.1. Sales Team

File: `views/crm_team_views.xml`

Ke thua:

- `sales_team.crm_team_view_form`
- `sales_team.crm_team_member_view_form`
- `sales_team.crm_team_member_view_tree`
- `sales_team.crm_team_member_view_form_from_team`
- `sales_team.crm_team_member_view_tree_from_team`
- `sales_team.crm_team_member_view_kanban`

Thay doi:

- Them `commission_rate` sau Team Leader.
- Them button `Cap nhat toan bo hoa hong` tren header.
- Them `commission_rate` vao form/list/kanban thanh vien.

### 9.2. Opportunity

File: `views/crm_lead_views.xml`

Ke thua:

- `crm.crm_lead_view_form`
- `crm.crm_case_tree_view_oppor`

Thay doi:

- Them 4 button Khao sat/Demo tren header.
- Them `commission_rate` va `project_id` trong khu vuc thong tin ban hang tren form Opportunity.
- Tach rieng 2 tab `Khao sat` va `Demo`.
- Them `other_ids`, `survey_note`, `estimate_attachment_ids`.
- Them cot `commission_rate`, `project_id` tren list Opportunity.

## 10. Security

File: `security/ir.model.access.csv`

Access da khai bao:

| Model | Group | Read | Write | Create | Delete |
| --- | --- | --- | --- | --- | --- |
| `crm.survey.wizard` | `base.group_user` | 1 | 1 | 1 | 1 |
| `crm.team.commission.wizard` | `sales_team.group_sale_manager` | 1 | 1 | 1 | 1 |

## 11. Cau truc file

```text
dcg_custom_crm/
├── __init__.py
├── __manifest__.py
├── README.md
├── controllers/
│   ├── __init__.py
│   └── main.py
├── data/
│   └── .gitkeep
├── models/
│   ├── __init__.py
│   ├── crm_lead.py
│   ├── crm_team.py
│   ├── crm_team_member.py
│   └── project_project.py
├── report/
│   └── __init__.py
├── security/
│   └── ir.model.access.csv
├── static/
│   └── description/
│       └── index.html
├── views/
│   ├── crm_lead_views.xml
│   └── crm_team_views.xml
└── wizard/
    ├── __init__.py
    ├── crm_survey_wizard.py
    ├── crm_survey_wizard_views.xml
    ├── crm_team_commission_wizard.py
    └── crm_team_commission_wizard_views.xml
```

## 12. Checklist test

- [ ] Install/upgrade module `dcg_custom_crm`.
- [ ] Mo Sales Team, kiem tra field `Phan tram hoa hong (%)`.
- [ ] Tao thanh vien moi, kiem tra default hoa hong theo team.
- [ ] Sua hoa hong team, xac nhan thanh vien khong tu dong doi.
- [ ] Bam `Cap nhat toan bo hoa hong`, confirm wizard, kiem tra hoa hong thanh vien duoc cap nhat.
- [ ] Tao Opportunity co `team_id` va `user_id`, kiem tra `commission_rate` readonly.
- [ ] Bam `Hoan thanh khao sat`, kiem tra flag, ngay hoan thanh va chatter.
- [ ] Bam `Tiep tuc khao sat`, confirm wizard, kiem tra chatter.
- [ ] Bam `Hoan thanh demo`, kiem tra flag, ngay hoan thanh va chatter.
- [ ] Bam `Tiep tuc demo`, confirm wizard, kiem tra chatter.
- [ ] Gan san `Link du an`, set Opportunity Won, kiem tra khong tao Project moi.
- [ ] Opportunity chua co `Link du an`, set Won, kiem tra Project duoc tao va lien ket vao `project_id`.
- [ ] Chuyen Opportunity tu Won ve stage xu ly, sau do Won lai, kiem tra khong tao trung Project.

## 13. Luu y ky thuat

- Khong dung onchange de dong bo hoa hong thanh vien.
- Dong bo hoa hong chi qua wizard xac nhan.
- Chatter log dung `message_post`.
- `project.project.x_lead_id` la field lien ket nguoc custom.
- Gia tri hoa hong luu theo dang so phan tram truc tiep, vi du `2.0` nghia la `2%`.
