# -*- coding: utf-8 -*-
# Mixin must be loaded first
from . import base_master_mixin

# CRM
from . import customer_industry
from . import customer_source
from . import service_catalog

# Contract
from . import contract_type
from . import contract_appendix_type
from . import acceptance_type

# Helpdesk
from . import ticket_type
from . import ticket_severity
from . import ticket_priority
from . import sla_policy

# Finance
from . import expense_type
from . import cost_center

# KPI & Alerts
from . import kpi_target
from . import alert_rule
