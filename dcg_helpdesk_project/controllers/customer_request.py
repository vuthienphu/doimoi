import base64
from odoo import http, _
from odoo.http import request


class CustomerRequestController(http.Controller):

    @http.route('/customer/request', type='http', auth='public', website=True, sitemap=True)
    def customer_request_form(self, **kw):
        return request.render('dcg_helpdesk_project.customer_request_form_template', {})

    @http.route('/customer/request/submit', type='http', auth='public', methods=['POST'], website=True, csrf=True)
    def customer_request_submit(self, **post):
        company_name = (post.get('company_name') or '').strip()
        contact_name = (post.get('contact_name') or '').strip()
        contact_phone = (post.get('contact_phone') or '').strip()
        contact_email = (post.get('contact_email') or '').strip()
        contact_department = (post.get('contact_department') or '').strip()
        contact_position = (post.get('contact_position') or '').strip()
        name = (post.get('name') or '').strip()
        description = (post.get('description') or '').strip()

        errors = []
        if not company_name:
            errors.append(_('Vui lòng nhập Tên công ty.'))
        if not contact_name:
            errors.append(_('Vui lòng nhập Họ và tên.'))
        if not contact_phone:
            errors.append(_('Vui lòng nhập Số điện thoại.'))
        if not name:
            errors.append(_('Vui lòng nhập Tiêu đề.'))
        if not description:
            errors.append(_('Vui lòng nhập Nội dung.'))

        if errors:
            return request.render('dcg_helpdesk_project.customer_request_form_template', {
                'errors': errors,
                'post': post,
            })

        # Create helpdesk ticket with sudo
        ticket_vals = {
            'name': name,
            'description': description,
            'request_source': 'web',
            'company_name': company_name,
            'contact_name': contact_name,
            'contact_phone': contact_phone,
            'contact_email': contact_email,
            'contact_department': contact_department,
            'contact_position': contact_position,
        }

        ticket = request.env['helpdesk.ticket'].sudo().create(ticket_vals)

        # Handle file uploads
        files = request.httprequest.files.getlist('attachments')
        for file in files:
            if file and file.filename:
                file_content = file.read()
                if file_content:
                    request.env['ir.attachment'].sudo().create({
                        'name': file.filename,
                        'datas': base64.b64encode(file_content),
                        'res_model': 'helpdesk.ticket',
                        'res_id': ticket.id,
                    })

        req_code = f"REQ-{ticket.id:06d}"

        return request.redirect(f'/customer/request/success?code={req_code}')

    @http.route('/customer/request/success', type='http', auth='public', website=True)
    def customer_request_success(self, code='', **kw):
        return request.render('dcg_helpdesk_project.customer_request_success_template', {
            'req_code': code,
        })
