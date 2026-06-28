# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import api, fields, models

TASK_TYPE_SELECTION = [
    ('ba', 'BA / Analysis'),
    ('dev', 'Development'),
    ('qa', 'Testing / QA'),
    ('review', 'Code Review'),
    ('deploy', 'Deployment'),
    ('training', 'Training'),
    ('support', 'Support'),
    ('other', 'Other'),
]

TASK_PRIORITY_SELECTION = [
    ('low', 'Low'),
    ('normal', 'Normal'),
    ('high', 'High'),
    ('critical', 'Critical'),
]


class DcgDashboardService(models.AbstractModel):
    _name = 'dcg.dashboard.service'
    _description = 'Dashboard KPI Service'

    # ==================================================================
    # HOME / EXECUTIVE — tổng hợp toàn hệ thống
    # ==================================================================
    @api.model
    def get_executive_data(self, company_id=None):
        Contract = self.env['dcg.contract']
        Project = self.env['dcg.project.delivery']
        Finance = self.env['dcg.project.finance']
        Ticket = self.env['dcg.warranty.ticket']
        Employee = self.env['hr.employee']

        contracts = Contract.search(self._cd(company_id))
        projects = Project.search(self._cd(company_id))
        finances = Finance.search(self._cd(company_id))
        tickets = Ticket.search([])

        total_rev = sum(contracts.mapped('amount_total'))
        actual_cost = sum(finances.mapped('actual_cost'))
        profit = total_rev - actual_cost
        margin = round(profit / total_rev * 100, 1) if total_rev else 0

        active = projects.filtered(lambda p: p.state in ('in_progress', 'uat'))
        red = active.filtered(lambda p: p.health_status == 'red')
        open_tk = tickets.filtered(lambda t: t.stage_id and not t.stage_id.is_done and not t.stage_id.is_cancel)
        critical = open_tk.filtered(lambda t: t.severity == 'critical')
        breached = open_tk.filtered(lambda t: t.sla_breached)

        return {
            'revenue': total_rev, 'profit': profit, 'margin': margin,
            'contract_count': len(contracts),
            'active_projects': len(active), 'red_projects': len(red),
            'open_tickets': len(open_tk), 'critical_tickets': len(critical),
            'sla_breached': len(breached),
            'employee_count': Employee.search_count([]),
            'customer_count': len(contracts.mapped('partner_id')),
        }

    # ==================================================================
    # SALES — CRM + Contract
    # ==================================================================
    @api.model
    def get_sales_data(self, company_id=None):
        Lead = self.env['crm.lead']
        Contract = self.env['dcg.contract']

        leads = Lead.search([])
        contracts = Contract.search(self._cd(company_id))

        by_commercial = {}
        for l in leads:
            cs = l.commercial_status or 'new'
            by_commercial[cs] = by_commercial.get(cs, 0) + 1

        won = leads.filtered(lambda l: l.stage_id and l.stage_id.is_won)
        total_qualified = leads.filtered(lambda l: l.commercial_status in (
            'qualified', 'proposal', 'negotiation', 'won', 'lost'))

        expiring = contracts.filtered(
            lambda c: c.end_date and c.end_date <= (fields.Date.today() + timedelta(days=90))
                      and c.state in ('active', 'in_progress')
        )

        top_customers = []
        partner_rev = {}
        for c in contracts:
            pid = c.partner_id.id
            partner_rev[pid] = partner_rev.get(pid, 0) + (c.amount_total or 0)
        for pid, rev in sorted(partner_rev.items(), key=lambda x: x[1], reverse=True)[:10]:
            p = self.env['res.partner'].browse(pid)
            top_customers.append({'id': pid, 'name': p.name, 'revenue': rev})

        return {
            'lead_count': len(leads),
            'opportunity_count': len(leads.filtered('active')),
            'won_count': len(won),
            'win_rate': round(len(won) / len(total_qualified) * 100, 1) if total_qualified else 0,
            'by_commercial': by_commercial,
            'contract_count': len(contracts),
            'expiring_contracts': len(expiring),
            'top_customers': top_customers,
        }

    # ==================================================================
    # PROJECT — Delivery + Milestone + Issue
    # ==================================================================
    @api.model
    def get_project_data(self, company_id=None):
        Project = self.env['dcg.project.delivery']
        Task = self.env['dcg.project.task']
        Stage = self.env['dcg.project.task.stage']

        projects = Project.search(self._cd(company_id))

        by_state = {}
        for p in projects:
            by_state[p.state] = by_state.get(p.state, 0) + 1

        by_health = {'green': 0, 'yellow': 0, 'red': 0}
        active = projects.filtered(lambda p: p.state in ('in_progress', 'uat', 'ready'))
        for p in active:
            by_health[p.health_status or 'green'] += 1

        done_stage_ids = Stage.search([('is_done', '=', True)]).ids
        cancel_stage_ids = Stage.search([('is_cancel', '=', True)]).ids
        start_stage_ids = Stage.search([('is_start', '=', True)]).ids
        review_stage_ids = Stage.search([('name', '=', 'In Review')]).ids
        in_progress_stage_ids = Stage.search([
            ('allow_timesheet', '=', True),
            ('id', 'not in', done_stage_ids + cancel_stage_ids + review_stage_ids)
        ]).ids

        today_datetime = fields.Datetime.now()

        top_projects = []
        for p in active.sorted('progress_percent', reverse=True)[:10]:
            delayed_days = 0
            if p.end_date and fields.Date.today() > p.end_date:
                delayed_days = (fields.Date.today() - p.end_date).days

            p_domain = [('active', '=', True), ('project_id', '=', p.id)]
            total = Task.search_count(p_domain)
            done = Task.search_count(p_domain + [('stage_id', 'in', done_stage_ids)])

            top_projects.append({
                'id': p.id, 'name': p.name,
                'progress': p.progress_percent or 0,
                'health': p.health_status or 'green',
                'pm': p.project_manager_id.name if p.project_manager_id else '',
                'delayed_days': delayed_days,
                'task_todo':        Task.search_count(p_domain + [('stage_id', 'in', start_stage_ids)]),
                'task_in_progress': Task.search_count(p_domain + [('stage_id', 'in', in_progress_stage_ids)]),
                'task_in_review':   Task.search_count(p_domain + [('stage_id', 'in', review_stage_ids)]),
                'task_done':        done,
                'task_overdue':     Task.search_count(p_domain + [
                                        ('planned_end', '<', today_datetime),
                                        ('stage_id', 'not in', done_stage_ids + cancel_stage_ids),
                                    ]),
                'task_total':       total,
                'task_completion':  round(done / total * 100, 1) if total else 0.0,
            })

        delayed = [p for p in top_projects if p['delayed_days'] > 0]

        all_domain = [('active', '=', True)]
        all_total = Task.search_count(all_domain)
        all_done = Task.search_count(all_domain + [('stage_id', 'in', done_stage_ids)])
        task_summary = {
            'todo':        Task.search_count(all_domain + [('stage_id', 'in', start_stage_ids)]),
            'in_progress': Task.search_count(all_domain + [('stage_id', 'in', in_progress_stage_ids)]),
            'in_review':   Task.search_count(all_domain + [('stage_id', 'in', review_stage_ids)]),
            'done':        all_done,
            'overdue':     Task.search_count(all_domain + [
                               ('planned_end', '<', today_datetime),
                               ('stage_id', 'not in', done_stage_ids + cancel_stage_ids),
                           ]),
            'blocked':     Task.search_count(all_domain + [('kanban_state', '=', 'blocked')]),
            'total':       all_total,
            'completion_rate': round(all_done / all_total * 100, 1) if all_total else 0.0,
        }

        return {
            'total': len(projects), 'active': len(active),
            'by_state': by_state, 'by_health': by_health,
            'top_projects': top_projects,
            'delayed_projects': sorted(delayed, key=lambda x: x['delayed_days'], reverse=True)[:5],
            'task_summary': task_summary,
        }

    @api.model
    def get_project_task_data(self, project_id=None):
        Task = self.env['dcg.project.task']
        Stage = self.env['dcg.project.task.stage']

        done_stages = Stage.search([('is_done', '=', True)])
        done_stage_ids = done_stages.ids

        cancel_stages = Stage.search([('is_cancel', '=', True)])
        cancel_stage_ids = cancel_stages.ids

        start_stages = Stage.search([('is_start', '=', True)])
        start_stage_ids = start_stages.ids

        review_stages = Stage.search([('name', '=', 'In Review')])
        review_stage_ids = review_stages.ids

        in_progress_stages = Stage.search([
            ('allow_timesheet', '=', True),
            ('id', 'not in', done_stage_ids + cancel_stage_ids + review_stage_ids)
        ])
        in_progress_stage_ids = in_progress_stages.ids

        # Domain base
        base_domain = [('active', '=', True)]
        if project_id:
            base_domain += [('project_id', '=', project_id)]

        today = fields.Date.today()
        today_datetime = fields.Datetime.now()

        # Summary counts
        summary = {
            'total':       Task.search_count(base_domain),
            'todo':        Task.search_count(base_domain + [('stage_id', 'in', start_stage_ids)]),
            'in_progress': Task.search_count(base_domain + [('stage_id', 'in', in_progress_stage_ids)]),
            'in_review':   Task.search_count(base_domain + [('stage_id', 'in', review_stage_ids)]),
            'done':        Task.search_count(base_domain + [('stage_id', 'in', done_stage_ids)]),
            'cancelled':   Task.search_count(base_domain + [('stage_id', 'in', cancel_stage_ids)]),
            'overdue':     Task.search_count(base_domain + [
                ('planned_end', '<', today_datetime),
                ('stage_id', 'not in', done_stage_ids + cancel_stage_ids),
            ]),
            'blocked':     Task.search_count(base_domain + [('kanban_state', '=', 'blocked')]),
        }

        # Scope and Task list (when project_id is provided)
        project_scopes = []
        project_tasks = []
        project_name = ""
        project_code = ""
        project_health = "green"
        if project_id:
            p = self.env['dcg.project.delivery'].browse(project_id)
            project_name = p.name
            project_code = p.project_code or ""
            project_health = p.health_status or "green"

            # Scopes progress
            scopes = self.env['dcg.project.scope'].search([('project_id', '=', project_id)])
            for s in scopes:
                s_domain = [('active', '=', True), ('scope_id', '=', s.id)]
                s_total = Task.search_count(s_domain)
                s_done = Task.search_count(s_domain + [('stage_id', 'in', done_stage_ids)])
                project_scopes.append({
                    'scope_id': s.id,
                    'scope_name': s.name,
                    'total': s_total,
                    'done': s_done,
                    'in_progress': Task.search_count(s_domain + [('stage_id', 'in', in_progress_stage_ids)]),
                    'in_review': Task.search_count(s_domain + [('stage_id', 'in', review_stage_ids)]),
                    'todo': Task.search_count(s_domain + [('stage_id', 'in', start_stage_ids)]),
                    'overdue': Task.search_count(s_domain + [
                        ('planned_end', '<', today_datetime),
                        ('stage_id', 'not in', done_stage_ids + cancel_stage_ids),
                    ]),
                    'completion': round(s_done / s_total * 100, 1) if s_total else 0.0,
                })

            # Tasks list
            tasks = Task.search([('active', '=', True), ('project_id', '=', project_id)])
            for t in tasks:
                project_tasks.append({
                    'id': t.id,
                    'code': t.code or '',
                    'name': t.name,
                    'assignee': t.assignee_id.name if t.assignee_id else '',
                    'planned_end': t.planned_end.strftime('%Y-%m-%d') if t.planned_end else '',
                    'stage_id': t.stage_id.id,
                    'stage_name': t.stage_id.name,
                    'is_start': t.stage_id.is_start,
                    'is_done': t.stage_id.is_done,
                    'is_cancel': t.stage_id.is_cancel,
                    'is_review': t.stage_id.id in review_stage_ids,
                    'is_in_progress': t.stage_id.id in in_progress_stage_ids,
                    'task_type': t.task_type or '',
                    'priority': t.priority or '',
                    'kanban_state': t.kanban_state or 'normal',
                })

        # By project
        projects = self.env['dcg.project.delivery'].search([('state', 'not in', ['done', 'closed', 'cancelled'])])
        by_project = []
        for p in projects:
            p_domain = base_domain + [('project_id', '=', p.id)]
            total = Task.search_count(p_domain)
            if total == 0:
                continue
            done = Task.search_count(p_domain + [('stage_id', 'in', done_stage_ids)])
            by_project.append({
                'project_id':      p.id,
                'project_name':    p.name,
                'project_code':    p.project_code or '',
                'health':          p.health_status or 'green',
                'todo':            Task.search_count(p_domain + [('stage_id', 'in', start_stage_ids)]),
                'in_progress':     Task.search_count(p_domain + [('stage_id', 'in', in_progress_stage_ids)]),
                'in_review':       Task.search_count(p_domain + [('stage_id', 'in', review_stage_ids)]),
                'done':            done,
                'overdue':         Task.search_count(p_domain + [
                                       ('planned_end', '<', today_datetime),
                                       ('stage_id', 'not in', done_stage_ids + cancel_stage_ids),
                                   ]),
                'blocked':         Task.search_count(p_domain + [('kanban_state', '=', 'blocked')]),
                'total':           total,
                'completion_rate': round(done / total * 100, 1) if total else 0,
            })

        # Overdue tasks (top 20)
        overdue_tasks = Task.search(base_domain + [
            ('planned_end', '<', today_datetime),
            ('stage_id', 'not in', done_stage_ids + cancel_stage_ids),
        ], order='planned_end asc', limit=20)

        # Blocked tasks (top 20)
        blocked_tasks = Task.search(base_domain + [
            ('kanban_state', '=', 'blocked'),
        ], limit=20)

        overdue_list = []
        for t in overdue_tasks:
            days = 0
            if t.planned_end:
                days = (today - t.planned_end.date()).days
            overdue_list.append({
                'task_id': t.id,
                'code': t.code or '',
                'name': t.name,
                'project_name': t.project_id.name,
                'assignee': t.assignee_id.name if t.assignee_id else '',
                'planned_end': t.planned_end.strftime('%Y-%m-%d %H:%M:%S') if t.planned_end else '',
                'days_overdue': max(days, 0),
                'priority': dict(TASK_PRIORITY_SELECTION).get(t.priority, t.priority or 'normal'),
            })

        blocked_list = []
        for t in blocked_tasks:
            blocked_list.append({
                'task_id': t.id,
                'code': t.code or '',
                'name': t.name,
                'project_name': t.project_id.name,
                'assignee': t.assignee_id.name if t.assignee_id else '',
                'priority': dict(TASK_PRIORITY_SELECTION).get(t.priority, t.priority or 'normal'),
            })

        return {
            'summary':       summary,
            'by_project':    by_project,
            'by_assignee':   self._compute_task_by_assignee(base_domain, start_stage_ids, in_progress_stage_ids, review_stage_ids, today, done_stage_ids, cancel_stage_ids),
            'by_type':       self._compute_task_by_type(base_domain, start_stage_ids, in_progress_stage_ids, review_stage_ids, done_stage_ids),
            'overdue_tasks': overdue_list,
            'blocked_tasks': blocked_list,
            'project_name': project_name,
            'project_code': project_code,
            'project_health': project_health,
            'scopes': project_scopes,
            'tasks': project_tasks,
        }

    def _compute_task_by_assignee(self, base_domain, start_stage_ids, in_progress_stage_ids, review_stage_ids, today, done_stage_ids, cancel_stage_ids):
        Task = self.env['dcg.project.task']
        tasks = Task.search(base_domain)
        assignee_data = {}
        for task in tasks:
            assignee = task.assignee_id
            if not assignee:
                continue
            aid = assignee.id
            if aid not in assignee_data:
                assignee_data[aid] = {
                    'user_id': aid,
                    'user_name': assignee.name,
                    'avatar': f'/web/image?model=res.users&id={aid}&field=avatar_128',
                    'todo': 0,
                    'in_progress': 0,
                    'overdue': 0,
                    'total': 0,
                }
            data = assignee_data[aid]
            data['total'] += 1
            stage = task.stage_id
            if stage.id in start_stage_ids:
                data['todo'] += 1
            elif stage.id in in_progress_stage_ids or stage.id in review_stage_ids:
                data['in_progress'] += 1
            
            if task.planned_end and task.planned_end < today and stage.id not in (done_stage_ids + cancel_stage_ids):
                data['overdue'] += 1
        
        sorted_assignees = sorted(assignee_data.values(), key=lambda x: x['total'], reverse=True)[:10]
        return sorted_assignees

    def _compute_task_by_type(self, base_domain, start_stage_ids, in_progress_stage_ids, review_stage_ids, done_stage_ids):
        Task = self.env['dcg.project.task']
        tasks = Task.search(base_domain)
        
        type_data = {}
        for task_type, label in TASK_TYPE_SELECTION:
            type_data[task_type] = {
                'task_type': task_type,
                'label': label,
                'todo': 0,
                'in_progress': 0,
                'done': 0,
                'total': 0,
            }
            
        for task in tasks:
            ttype = task.task_type or 'other'
            if ttype not in type_data:
                type_data[ttype] = {
                    'task_type': ttype,
                    'label': ttype.capitalize(),
                    'todo': 0,
                    'in_progress': 0,
                    'done': 0,
                    'total': 0,
                }
            data = type_data[ttype]
            data['total'] += 1
            stage = task.stage_id
            if stage.id in start_stage_ids:
                data['todo'] += 1
            elif stage.id in in_progress_stage_ids or stage.id in review_stage_ids:
                data['in_progress'] += 1
            elif stage.id in done_stage_ids:
                data['done'] += 1
                
        return list(type_data.values())

    # ==================================================================
    # RESOURCE — Allocation + Capacity + Utilization
    # ==================================================================
    @api.model
    def get_resource_data(self, company_id=None):
        Alloc = self.env['dcg.resource.allocation']
        Employee = self.env['hr.employee']
        Line = self.env['account.analytic.line']
        today = fields.Date.today()

        employees = Employee.search([])
        active_allocs = Alloc.search([
            ('state', 'not in', ['cancelled', 'done']),
            ('start_date', '<=', today), ('end_date', '>=', today),
        ])

        workload = []
        for emp in employees[:20]:
            emp_allocs = active_allocs.filtered(lambda a: a.employee_id.id == emp.id)
            total_pct = sum(emp_allocs.mapped('allocation_percent'))
            workload.append({
                'id': emp.id, 'name': emp.name,
                'allocation': round(total_pct, 0),
                'color': 'danger' if total_pct > 100 else ('warning' if total_pct > 80 else 'success'),
            })
        workload.sort(key=lambda x: x['allocation'], reverse=True)

        bench = [w for w in workload if w['allocation'] < 10]
        over = [w for w in workload if w['allocation'] > 100]

        return {
            'employee_count': len(employees),
            'allocated_count': len(set(active_allocs.mapped('employee_id.id'))),
            'bench_count': len(bench),
            'over_allocated_count': len(over),
            'workload': workload[:15],
        }

    # ==================================================================
    # FINANCE — P&L, Collection, Margin
    # ==================================================================
    @api.model
    def get_finance_data(self, company_id=None):
        Finance = self.env['dcg.project.finance']
        finances = Finance.search(self._cd(company_id))

        planned_rev = sum(finances.mapped('planned_revenue'))
        actual_rev = sum(finances.mapped('actual_revenue'))
        actual_cost = sum(finances.mapped('actual_cost'))
        collected = sum(finances.mapped('collected_amount'))
        margin = actual_rev - actual_cost
        outstanding = actual_rev - collected

        by_health = {'green': 0, 'yellow': 0, 'red': 0}
        for f in finances:
            by_health[f.finance_health or 'green'] += 1

        top_margin = []
        for f in sorted(finances, key=lambda x: x.actual_margin or 0, reverse=True)[:10]:
            top_margin.append({
                'id': f.id,
                'project': f.project_id.name if f.project_id else '',
                'revenue': f.actual_revenue, 'cost': f.actual_cost,
                'margin': f.actual_margin,
                'margin_rate': round(f.actual_margin_rate or 0, 1),
            })

        return {
            'planned_revenue': planned_rev, 'actual_revenue': actual_rev,
            'actual_cost': actual_cost, 'margin': margin,
            'margin_rate': round(margin / actual_rev * 100, 1) if actual_rev else 0,
            'collected': collected, 'outstanding': outstanding,
            'by_health': by_health, 'top_margin': top_margin,
        }

    # ==================================================================
    # SUPPORT — Tickets, SLA, Trend
    # ==================================================================
    @api.model
    def get_support_data(self):
        Ticket = self.env['dcg.warranty.ticket']
        tickets = Ticket.search([])

        open_tk = tickets.filtered(lambda t: t.stage_id and not t.stage_id.is_done and not t.stage_id.is_cancel)
        critical = open_tk.filtered(lambda t: t.severity == 'critical')
        breached = open_tk.filtered(lambda t: t.sla_breached)

        by_severity = {}
        for t in open_tk:
            by_severity[t.severity or 'low'] = by_severity.get(t.severity or 'low', 0) + 1

        by_type = {}
        for t in open_tk:
            by_type[t.ticket_type or 'other'] = by_type.get(t.ticket_type or 'other', 0) + 1

        recent_critical = []
        for t in critical.sorted('create_date', reverse=True)[:5]:
            recent_critical.append({
                'id': t.id, 'name': t.name, 'title': t.title,
                'customer': t.partner_id.name if t.partner_id else '',
                'engineer': t.support_engineer_id.name if t.support_engineer_id else '',
            })

        return {
            'total_open': len(open_tk), 'critical': len(critical),
            'sla_breached': len(breached),
            'by_severity': by_severity, 'by_type': by_type,
            'recent_critical': recent_critical,
        }

    # ==================================================================
    # ASSET — Devices, Licenses, Warranty
    # ==================================================================
    @api.model
    def get_asset_data(self):
        Asset = self.env['dcg.asset']
        License = self.env['dcg.asset.license']
        Warranty = self.env['dcg.asset.warranty']
        today = fields.Date.today()
        soon = today + timedelta(days=30)

        assets = Asset.search([])
        assigned = assets.filtered(lambda a: a.current_employee_id)
        available = assets.filtered(lambda a: not a.current_employee_id and a.stage_id and not a.stage_id.is_end)

        licenses = License.search([('active', '=', True)])
        expired_lic = licenses.filtered(lambda l: l.is_expired)
        expiring_lic = licenses.filtered(lambda l: l.expiry_date and not l.is_expired and l.expiry_date <= soon)

        warranties = Warranty.search([])
        expired_war = warranties.filtered(lambda w: w.is_expired)
        expiring_war = warranties.filtered(lambda w: w.end_date and not w.is_expired and w.end_date <= soon)

        by_stage = {}
        for a in assets:
            sn = a.stage_id.name if a.stage_id else 'Unknown'
            by_stage[sn] = by_stage.get(sn, 0) + 1

        return {
            'total': len(assets), 'assigned': len(assigned),
            'available': len(available),
            'by_stage': by_stage,
            'license_total': len(licenses),
            'license_expired': len(expired_lic),
            'license_expiring': len(expiring_lic),
            'warranty_expired': len(expired_war),
            'warranty_expiring': len(expiring_war),
        }

    # ==================================================================
    # HR — Certificate, Training, Availability
    # ==================================================================
    @api.model
    def get_hr_data(self):
        Employee = self.env['hr.employee']
        today = fields.Date.today()
        soon = today + timedelta(days=90)

        employees = Employee.search([])

        cert_expired = 0
        cert_expiring = 0
        for emp in employees:
            if hasattr(emp, 'certificate_ids'):
                for c in emp.certificate_ids:
                    if c.is_expired:
                        cert_expired += 1
                    elif c.expiry_date and c.expiry_date <= soon:
                        cert_expiring += 1

        training_count = 0
        if 'dcg.employee.training' in self.env:
            training_count = self.env['dcg.employee.training'].search_count([])

        avail_count = 0
        if 'dcg.employee.availability' in self.env:
            avail_count = self.env['dcg.employee.availability'].search_count([
                ('status', '=', 'available'),
                ('available_from', '<=', today),
                ('available_to', '>=', today),
            ])

        return {
            'employee_count': len(employees),
            'cert_expired': cert_expired,
            'cert_expiring': cert_expiring,
            'training_count': training_count,
            'available_count': avail_count,
        }

    # ==================================================================
    # BUSINESS TRIP
    # ==================================================================
    @api.model
    def get_trip_data(self):
        Trip = self.env['dcg.business.trip']
        trips = Trip.search([])

        by_state = {}
        for t in trips:
            by_state[t.state] = by_state.get(t.state, 0) + 1

        total_est = sum(trips.mapped('estimated_cost'))
        total_act = sum(trips.mapped('actual_cost'))

        return {
            'total': len(trips),
            'by_state': by_state,
            'estimated_cost': total_est,
            'actual_cost': total_act,
        }

    # ==================================================================
    # DOCUMENT
    # ==================================================================
    @api.model
    def get_document_data(self):
        Doc = self.env['dcg.document']
        docs = Doc.search([])

        waiting = docs.filtered(lambda d: d.state == 'review')
        approved = docs.filtered(lambda d: d.state == 'approved')
        published = docs.filtered(lambda d: d.state == 'published')

        return {
            'total': len(docs),
            'waiting_review': len(waiting),
            'approved': len(approved),
            'published': len(published),
        }

    # ==================================================================
    # NOTIFICATION — from mail.activity
    # ==================================================================
    @api.model
    def get_notifications(self):
        Activity = self.env['mail.activity']
        my = Activity.search([('user_id', '=', self.env.uid)], limit=10, order='date_deadline')
        items = []
        for a in my:
            items.append({
                'id': a.id,
                'summary': a.summary or a.activity_type_id.name or '',
                'model': a.res_model,
                'res_id': a.res_id,
                'deadline': str(a.date_deadline),
                'overdue': a.date_deadline < fields.Date.today() if a.date_deadline else False,
            })
        return {'activities': items, 'count': len(items)}

    # ==================================================================
    # Helper
    # ==================================================================
    def _cd(self, company_id=None):
        return [('company_id', '=', company_id)] if company_id else []
