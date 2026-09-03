from odoo import http, fields, _
from odoo.http import request
from datetime import datetime, date


class CustomerRequestDashboardController(http.Controller):

    @http.route('/dcg_helpdesk_project/dashboard_data', type='json', auth='user')
    def get_dashboard_data(self, date_from=None, date_to=None):
        domain = []

        if date_from:
            domain.append(('create_date', '>=', f"{date_from} 00:00:00"))
        if date_to:
            domain.append(('create_date', '<=', f"{date_to} 23:59:59"))

        Ticket = request.env['helpdesk.ticket']
        tickets = Ticket.search(domain)

        total = len(tickets)
        with_task = len(tickets.filtered(lambda t: t.task_count > 0))
        in_progress = len(tickets.filtered(lambda t: not t.stage_id.fold))
        done = len(tickets.filtered(lambda t: t.stage_id.fold))
        without_task = len(tickets.filtered(lambda t: t.task_count == 0))

        by_source = {
            'web': len(tickets.filtered(lambda t: t.request_source == 'web')),
            'zalo': len(tickets.filtered(lambda t: t.request_source == 'zalo')),
            'internal': len(tickets.filtered(lambda t: t.request_source == 'internal')),
            'other': len(tickets.filtered(lambda t: t.request_source == 'other')),
        }

        # Stage breakdown
        stages_data = {}
        for ticket in tickets:
            stage_name = ticket.stage_id.name or _('New')
            stages_data[stage_name] = stages_data.get(stage_name, 0) + 1

        # Recent tickets
        recent_records = Ticket.search(domain, order='create_date desc', limit=10)
        recent_tickets = []
        for r in recent_records:
            company_display = r.partner_id.name if r.partner_id else (r.company_name or _('N/A'))
            recent_tickets.append({
                'id': r.id,
                'code': f"REQ-{r.id:06d}",
                'name': r.name,
                'company': company_display,
                'source': dict(r._fields['request_source'].selection).get(r.request_source, r.request_source),
                'stage': r.stage_id.name or _('New'),
                'stage_fold': r.stage_id.fold,
                'task_count': r.task_count,
            })

        return {
            'total': total,
            'with_task': with_task,
            'without_task': without_task,
            'in_progress': in_progress,
            'done': done,
            'by_source': by_source,
            'by_stage': stages_data,
            'recent_tickets': recent_tickets,
        }
