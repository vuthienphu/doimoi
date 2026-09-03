from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.http import request


class HelpdeskPortal(CustomerPortal):

    def _helpdesk_ticket_domain(self):
        return [('partner_id', '=', request.env.user.partner_id.id)]

    @http.route(['/my/tickets', '/my/tickets/page/<int:page>'], type='http',
                auth='user', website=True)
    def portal_my_tickets(self, page=1, sortby=None, **kw):
        domain = self._helpdesk_ticket_domain()
        Ticket = request.env['helpdesk.ticket']
        count = Ticket.search_count(domain)
        pager = portal_pager(
            url='/my/tickets',
            total=count,
            page=page,
            step=self._items_per_page,
        )
        tickets = Ticket.search(domain, limit=self._items_per_page, offset=pager['offset'])
        return request.render('helpdesk_community.portal_my_tickets', {
            'tickets': tickets,
            'pager': pager,
            'page_name': 'tickets',
        })

    @http.route(['/my/ticket/create'], type='http', auth='user', website=True)
    def portal_create_ticket(self, **kw):
        categories = request.env['helpdesk.category'].search([])
        return request.render('helpdesk_community.portal_create_ticket', {
            'categories': categories,
            'page_name': 'tickets',
        })

    @http.route(['/my/ticket/create/submit'], type='http', auth='user',
                methods=['POST'], website=True)
    def portal_create_ticket_submit(self, **post):
        vals = {
            'name': post.get('name'),
            'description': post.get('description'),
            'category_id': int(post.get('category_id')) if post.get('category_id') else False,
            'partner_id': request.env.user.partner_id.id,
        }
        ticket = request.env['helpdesk.ticket'].sudo().create(vals)
        return request.redirect('/my/ticket/%d' % ticket.id)

    @http.route(['/my/ticket/<int:ticket_id>'], type='http', auth='user', website=True)
    def portal_ticket_detail(self, ticket_id, **kw):
        ticket = request.env['helpdesk.ticket'].browse(ticket_id)
        if ticket.partner_id != request.env.user.partner_id:
            return request.redirect('/my')
        return request.render('helpdesk_community.portal_ticket_detail', {
            'ticket': ticket,
            'page_name': 'tickets',
        })
