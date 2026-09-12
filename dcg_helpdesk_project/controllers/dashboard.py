from odoo import http, fields, _
from odoo.http import request
from datetime import datetime, date, timedelta
import calendar


class CustomerRequestDashboardController(http.Controller):

    @http.route(['/helpdesk/dashboard/data', '/dcg_helpdesk_project/dashboard_data'], type='jsonrpc', auth='user')
    def get_dashboard_data(
        self,
        date_preset=None,
        date_from=None,
        date_to=None,
        partner_id=None,
        project_id=None,
        team_id=None,
        user_id=None,
        request_source=None,
        stage_id=None,
        **kwargs
    ):
        domain = []

        # 1. Date Range Handling
        today = date.today()
        if date_preset:
            if date_preset == 'today':
                date_from = today.strftime('%Y-%m-%d')
                date_to = today.strftime('%Y-%m-%d')
            elif date_preset == '7days':
                date_from = (today - timedelta(days=6)).strftime('%Y-%m-%d')
                date_to = today.strftime('%Y-%m-%d')
            elif date_preset == '30days':
                date_from = (today - timedelta(days=29)).strftime('%Y-%m-%d')
                date_to = today.strftime('%Y-%m-%d')
            elif date_preset == 'this_month':
                date_from = today.replace(day=1).strftime('%Y-%m-%d')
                last_day = calendar.monthrange(today.year, today.month)[1]
                date_to = today.replace(day=last_day).strftime('%Y-%m-%d')
            elif date_preset == 'last_month':
                first_of_this_month = today.replace(day=1)
                last_of_last_month = first_of_this_month - timedelta(days=1)
                first_of_last_month = last_of_last_month.replace(day=1)
                date_from = first_of_last_month.strftime('%Y-%m-%d')
                date_to = last_of_last_month.strftime('%Y-%m-%d')
            elif date_preset == 'this_quarter':
                current_quarter = (today.month - 1) // 3 + 1
                first_month_of_quarter = 3 * (current_quarter - 1) + 1
                date_from = date(today.year, first_month_of_quarter, 1).strftime('%Y-%m-%d')
                last_month_of_quarter = first_month_of_quarter + 2
                last_day_of_quarter = calendar.monthrange(today.year, last_month_of_quarter)[1]
                date_to = date(today.year, last_month_of_quarter, last_day_of_quarter).strftime('%Y-%m-%d')
            elif date_preset == 'this_year':
                date_from = date(today.year, 1, 1).strftime('%Y-%m-%d')
                date_to = date(today.year, 12, 31).strftime('%Y-%m-%d')

        if date_from:
            domain.append(('create_date', '>=', f"{date_from} 00:00:00"))
        if date_to:
            domain.append(('create_date', '<=', f"{date_to} 23:59:59"))

        # 2. Entity Filters
        if partner_id:
            domain.append(('partner_id', '=', int(partner_id)))
        if project_id:
            domain.append(('project_id', '=', int(project_id)))
        if team_id:
            domain.append(('team_id', '=', int(team_id)))
        if user_id:
            if user_id == 'unassigned' or user_id is False:
                domain.append(('user_id', '=', False))
            else:
                domain.append(('user_id', '=', int(user_id)))
        if request_source:
            domain.append(('request_source', '=', str(request_source)))
        if stage_id:
            domain.append(('stage_id', '=', int(stage_id)))

        Ticket = request.env['helpdesk.ticket']
        tickets = Ticket.search(domain)

        total_count = len(tickets)

        # 3. Filter Options for Header Toolbar
        partners = request.env['res.partner'].search_read(
            [('is_company', '=', True)], ['id', 'name'], order='name asc'
        )
        projects = request.env['project.project'].search_read(
            [], ['id', 'name'], order='name asc'
        )
        teams = request.env['helpdesk.team'].search_read(
            [], ['id', 'name'], order='name asc'
        )
        users = request.env['res.users'].search_read(
            [('share', '=', False)], ['id', 'name'], order='name asc'
        )
        stages = request.env['helpdesk.stage'].search_read(
            [], ['id', 'name', 'sequence'], order='sequence asc'
        )
        source_selection = Ticket._fields['request_source'].selection
        sources = [
            {'code': k, 'name': v}
            for k, v in (source_selection if isinstance(source_selection, (list, tuple)) else [])
        ]

        # 4. KPI Calculations
        first_stage = stages[0] if stages else None
        new_stage_id = first_stage['id'] if first_stage else False

        new_tickets_count = len(tickets.filtered(lambda t: t.stage_id.id == new_stage_id or (t.stage_id and t.stage_id.sequence == 1)))
        in_progress_count = len(tickets.filtered(lambda t: t.stage_id and not t.stage_id.fold and t.stage_id.id != new_stage_id))
        waiting_count = len(tickets.filtered(lambda t: not t.user_id or not t.stage_id))
        urgent_count = len(tickets.filtered(lambda t: t.priority == '3'))
        without_task_count = len(tickets.filtered(lambda t: t.task_count == 0))

        kpi = {
            'total': total_count,
            'new': new_tickets_count,
            'processing': in_progress_count,
            'waiting': waiting_count,
            'urgent': urgent_count,
            'without_task': without_task_count,
        }

        # 5. Breakdown by Stage
        all_stages = request.env['helpdesk.stage'].search([], order='sequence asc')
        by_stage = []
        for stage in all_stages:
            stage_tickets = tickets.filtered(lambda t: t.stage_id.id == stage.id)
            cnt = len(stage_tickets)
            pct = round((cnt / total_count * 100), 1) if total_count > 0 else 0.0
            by_stage.append({
                'id': stage.id,
                'name': stage.name,
                'count': cnt,
                'percentage': pct,
                'fold': stage.fold,
            })

        # 6. Breakdown by Request Source
        source_colors = {
            'web': '#F0631A',
            'zalo': '#0E7C66',
            'internal': '#3B82F6',
            'other': '#6B7280',
        }
        by_source = []
        source_dict = dict(source_selection) if isinstance(source_selection, (list, tuple)) else {}
        for src_code in ['web', 'zalo', 'internal', 'other']:
            src_name = source_dict.get(src_code, src_code.capitalize())
            cnt = len(tickets.filtered(lambda t: t.request_source == src_code))
            pct = round((cnt / total_count * 100), 1) if total_count > 0 else 0.0
            by_source.append({
                'code': src_code,
                'name': src_name,
                'count': cnt,
                'percentage': pct,
                'color': source_colors.get(src_code, '#6B7280'),
            })

        # 7. Breakdown by Priority
        priority_colors = {
            '3': '#EF4444',
            '2': '#F97316',
            '1': '#EAB308',
            '0': '#3B82F6',
        }
        priority_names = {
            '3': 'Khẩn cấp',
            '2': 'Cao',
            '1': 'Ưu tiên',
            '0': 'Bình thường',
        }
        by_priority = []
        for prio_code in ['3', '2', '1', '0']:
            cnt = len(tickets.filtered(lambda t: t.priority == prio_code))
            pct = round((cnt / total_count * 100), 1) if total_count > 0 else 0.0
            by_priority.append({
                'code': prio_code,
                'name': priority_names.get(prio_code, prio_code),
                'count': cnt,
                'percentage': pct,
                'color': priority_colors.get(prio_code, '#3B82F6'),
            })

        # 8. Breakdown by User (Assignee)
        user_counts = {}
        unassigned_count = 0
        for t in tickets:
            if t.user_id:
                user_counts[t.user_id] = user_counts.get(t.user_id, 0) + 1
            else:
                unassigned_count += 1

        by_user = []
        sorted_users = sorted(user_counts.items(), key=lambda x: x[1], reverse=True)
        for usr, cnt in sorted_users:
            by_user.append({
                'id': usr.id,
                'name': usr.name,
                'count': cnt,
                'percentage': round((cnt / total_count * 100), 1) if total_count > 0 else 0.0,
            })
        if unassigned_count > 0 or not by_user:
            by_user.append({
                'id': False,
                'name': 'Chưa giao',
                'count': unassigned_count,
                'percentage': round((unassigned_count / total_count * 100), 1) if total_count > 0 else 0.0,
            })

        # 9. Task Performance Stats
        all_tasks = tickets.mapped('task_ids')
        total_tasks = len(all_tasks)
        tickets_with_task = len(tickets.filtered(lambda t: t.task_count > 0))
        tickets_without_task = total_count - tickets_with_task
        completed_tasks = len(all_tasks.filtered(lambda task: getattr(task, 'stage_id', False) and getattr(task.stage_id, 'fold', False)))

        task_stats = {
            'total_tasks': total_tasks,
            'tickets_with_task': tickets_with_task,
            'tickets_without_task': tickets_without_task,
            'completed_tasks': completed_tasks,
        }

        # 10. Attention Tickets
        attention_domain = domain + [
            '|', '|', '|',
            ('priority', '=', '3'),
            ('user_id', '=', False),
            ('task_ids', '=', False),
            ('stage_id.sequence', '=', 1)
        ]
        attention_records = Ticket.search(attention_domain, order='priority desc, id desc', limit=15)
        if not attention_records and tickets:
            attention_records = Ticket.search(domain, order='create_date desc', limit=10)

        attention_tickets = []
        for r in attention_records:
            company_display = r.partner_id.name if r.partner_id else (r.company_name or _('N/A'))
            project_display = r.project_id.name if r.project_id else _('Chưa gán')
            user_display = r.user_id.name if r.user_id else _('Chưa giao')
            stage_display = r.stage_id.name if r.stage_id else _('Mới')
            prio_name = priority_names.get(r.priority, 'Bình thường')

            attention_tickets.append({
                'id': r.id,
                'code': f"REQ-{r.id:06d}",
                'name': r.name,
                'company': company_display,
                'project': project_display,
                'priority': r.priority,
                'priority_name': prio_name,
                'user': user_display,
                'user_id': r.user_id.id if r.user_id else False,
                'stage': stage_display,
                'stage_id': r.stage_id.id if r.stage_id else False,
                'stage_fold': r.stage_id.fold if r.stage_id else False,
                'create_date': r.create_date.strftime('%Y-%m-%d %H:%M') if r.create_date else '',
                'request_source': r.request_source,
                'task_count': r.task_count,
            })

        return {
            'filter_options': {
                'partners': partners,
                'projects': projects,
                'teams': teams,
                'users': users,
                'stages': stages,
                'request_sources': sources,
            },
            'kpi': kpi,
            'by_stage': by_stage,
            'by_source': by_source,
            'by_priority': by_priority,
            'by_user': by_user,
            'task_stats': task_stats,
            'attention_tickets': attention_tickets,
        }

