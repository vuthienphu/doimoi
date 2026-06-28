# 03_DCG_ERP_Developer_Guide

Version: 1.0

# Table of Contents

1.  Development Environment
2.  Project Structure
3.  Coding Convention
4.  Odoo Module Standard
5.  Python Convention
6.  XML Convention
7.  OWL Convention
8.  Security
9.  Dashboard Development
10. Performance
11. Git Workflow
12. Code Review Checklist

------------------------------------------------------------------------

# 1. Development Environment

Platform

-   Odoo 18 Community
-   PostgreSQL 16+
-   Python 3.11
-   NodeJS LTS

Recommended IDE

-   PyCharm
-   VS Code

------------------------------------------------------------------------

# 2. Project Structure

Each module must follow:

module_name/

-   models/
-   views/
-   security/
-   wizard/
-   report/
-   controllers/
-   data/
-   demo/
-   static/src/js
-   static/src/xml
-   static/src/scss
-   **manifest**.py

------------------------------------------------------------------------

# 3. Coding Convention

Naming

Model

dcg.project

Class

ProjectDelivery

Method

action_confirm()

Variable

project_id

XML ID

view_project_form

Menu

menu_project_root

Action

action_project

------------------------------------------------------------------------

# 4. Odoo Module Standard

Manifest

-   name
-   version
-   depends
-   data
-   assets

Never modify Odoo core.

Always extend using \_inherit.

------------------------------------------------------------------------

# 5. Python Convention

-   Business logic in models/services.
-   Avoid duplicated code.
-   Use ORM.
-   Avoid raw SQL unless required.
-   Validate before write/create.
-   Use logging instead of print.

Method order

1.  default_get
2.  create
3.  write
4.  unlink
5.  compute
6.  onchange
7.  action
8.  helper

------------------------------------------------------------------------

# 6. XML Convention

Views

-   tree
-   form
-   search
-   kanban
-   calendar
-   graph
-   pivot

Use xpath for inheritance.

Never duplicate views.

------------------------------------------------------------------------

# 7. OWL Convention

Dashboard

Client Action

↓

OWL Component

↓

XML Template

↓

RPC

↓

Python Service

Component naming

RevenueCard

ProjectChart

FinanceTable

Reuse component whenever possible.

------------------------------------------------------------------------

# 8. Security

Every module must contain

security/

-   ir.model.access.csv

record_rule.xml

group.xml

Access level

-   User
-   Manager
-   Administrator

Never use sudo() unless absolutely necessary.

------------------------------------------------------------------------

# 9. Dashboard Development

Use

-   Client Action
-   OWL
-   XML Template
-   Chart.js

Do not use Form View as dashboard.

Backend returns JSON.

Frontend renders UI only.

------------------------------------------------------------------------

# 10. Performance

Avoid

-   N+1 Query
-   compute inside loop
-   repeated search()

Use

read_group()

mapped()

filtered()

prefetch

Batch create/write whenever possible.

------------------------------------------------------------------------

# 11. Git Workflow

main

↓

develop

↓

feature/xxx

↓

Pull Request

↓

Code Review

↓

Merge

Commit format

\[ADD\]

\[FIX\]

\[IMP\]

\[REF\]

\[REM\]

------------------------------------------------------------------------

# 12. Code Review Checklist

Python

-   Naming
-   Logging
-   ORM
-   Performance
-   Exception

XML

-   xpath
-   translation
-   responsive

Security

-   access right
-   record rule

Dashboard

-   OWL
-   XML Template
-   RPC
-   Chart

Performance

-   SQL
-   Cache
-   Batch

Documentation

-   README
-   Manifest
-   Comment

------------------------------------------------------------------------

Developer Principles

-   Follow Odoo 18 Standard.
-   No core modification.
-   Modular architecture.
-   Reusable component.
-   Service-oriented business logic.
-   XML + OWL for dashboard.
