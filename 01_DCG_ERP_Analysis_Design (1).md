# 01_DCG_ERP_Analysis_Design

Version: 1.0

## Table of Contents

1.  System Overview
2.  Architecture
3.  Module Dependency
4.  Business Flow
5.  Module List
6.  Design Principles

------------------------------------------------------------------------

# 1. System Overview

DCG ERP là hệ thống quản lý toàn bộ vòng đời triển khai ERP trên Odoo 18
Community.

Business Flow

Lead → Opportunity → Proposal → Approval → Contract → Project → Resource
Planning → Timesheet → Finance → Warranty → Dashboard KPI

# 2. Architecture

Foundation - dcg_master_data - dcg_approval_matrix

Business - dcg_crm_presales - dcg_contract_management

Delivery - dcg_project_delivery - dcg_resource_planning -
dcg_timesheet_control - dcg_project_finance

Operation - dcg_business_trip - dcg_helpdesk_warranty -
dcg_document_management - dcg_hr_resource - dcg_asset_it

Presentation - dcg_dashboard_kpi

# 3. Module Dependency

dcg_master_data -\> approval -\> crm -\> contract -\> project -\>
resource -\> timesheet -\> finance -\> warranty -\> document -\> hr -\>
asset -\> dashboard

# 4. Design Principles

-   Modular Architecture
-   Single Source of Truth
-   Odoo 18 Standard
-   OWL + XML Dashboard
-   No Core Modification
-   Role Based Security

# 5. Module List

-   dcg_master_data
-   dcg_approval_matrix
-   dcg_crm_presales
-   dcg_contract_management
-   dcg_project_delivery
-   dcg_resource_planning
-   dcg_timesheet_control
-   dcg_project_finance
-   dcg_business_trip
-   dcg_helpdesk_warranty
-   dcg_document_management
-   dcg_hr_resource
-   dcg_asset_it
-   dcg_dashboard_kpi

> Phiên bản đầu tiên. Nội dung chi tiết từng module sẽ được bổ sung ở
> các phiên bản tiếp theo.
