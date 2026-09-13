# -*- coding: utf-8 -*-
import logging
from odoo import http, fields, _
from odoo.http import request
from odoo.exceptions import AccessError

_logger = logging.getLogger(__name__)


class HelpdeskTicketApiController(http.Controller):

    def _get_authenticated_user(self):
        """
        Xác thực user từ session hoặc header:
        1. request.session.uid (nếu gửi Cookie session_id)
        2. Header Authorization: Bearer <session_id> hoặc X-Session-Id
        """
        uid = request.session.uid
        if not uid:
            auth_header = request.httprequest.headers.get('Authorization') or ''
            session_id = None
            if auth_header.startswith('Bearer '):
                session_id = auth_header[7:].strip()
            if not session_id:
                session_id = request.httprequest.headers.get('X-Session-Id')

            if session_id:
                try:
                    sess = request.session_store.get(session_id)
                    if sess and sess.get('uid'):
                        uid = sess['uid']
                except Exception as e:
                    _logger.warning("Error fetching session: %s", e)

        if not uid:
            return None

        user = request.env['res.users'].sudo().browse(uid)
        if not user.exists() or not user.active:
            return None
        return user

    def _check_helpdesk_permission(self, user):
        """Kiểm tra quyền truy cập module Helpdesk"""
        allowed_groups = [
            'helpdesk_community.group_helpdesk_user',
            'helpdesk_community.group_helpdesk_team_leader',
            'helpdesk_community.group_helpdesk_manager',
            'base.group_system',
        ]
        return any(user.has_group(grp) for grp in allowed_groups)

    @http.route('/api/v1/helpdesk/tickets', type='http', auth='public', methods=['GET'], cors='*', csrf=False)
    def get_tickets(self, page=1, limit=20, stage_id=None, search=None, **kw):
        """
        Lấy danh sách Ticket cho Mobile App (áp dụng phân quyền record rule của user)
        """
        user = self._get_authenticated_user()
        if not user:
            return request.make_json_response({
                'code': 401,
                'message': 'Chưa đăng nhập hoặc phiên làm việc đã hết hạn.'
            }, status=401)

        if not self._check_helpdesk_permission(user):
            return request.make_json_response({
                'code': 403,
                'message': 'Tài khoản của bạn không có quyền truy cập Ticket.'
            }, status=403)

        try:
            page = max(1, int(page))
            limit = max(1, min(100, int(limit)))
        except (ValueError, TypeError):
            page = 1
            limit = 20

        offset = (page - 1) * limit

        domain = []
        if stage_id:
            try:
                domain.append(('stage_id', '=', int(stage_id)))
            except ValueError:
                pass

        if search:
            search_str = str(search).strip()
            domain.extend([
                '|', '|',
                ('name', 'ilike', search_str),
                ('company_name', 'ilike', search_str),
                ('partner_id.name', 'ilike', search_str),
            ])

        TicketModel = request.env['helpdesk.ticket'].with_user(user)

        try:
            total_records = TicketModel.search_count(domain)
            tickets = TicketModel.search(domain, offset=offset, limit=limit, order='create_date desc')

            data = []
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url', '')

            for t in tickets:
                data.append({
                    'id': t.id,
                    'code': f"#TK{str(t.id).zfill(5)}",
                    'name': t.name,
                    'create_date': fields.Datetime.to_string(t.create_date) if t.create_date else None,
                    'company_name': t.partner_id.name or t.company_name or '',
                    'priority': {
                        'level': t.priority or '0',
                        'label': dict(t._fields['priority'].selection).get(t.priority, 'Bình thường')
                    },
                    'stage': {
                        'id': t.stage_id.id if t.stage_id else None,
                        'name': t.stage_id.name if t.stage_id else '',
                    },
                    'request_source': {
                        'key': t.request_source or 'internal',
                        'label': dict(t._fields['request_source'].selection).get(t.request_source, 'Nội bộ')
                    },
                    'assignee': {
                        'id': t.user_id.id if t.user_id else None,
                        'name': t.user_id.name if t.user_id else '',
                        'avatar_url': f"{base_url}/web/image/res.users/{t.user_id.id}/avatar_128" if t.user_id else None,
                    },
                    'task_count': t.task_count or 0,
                })

            return request.make_json_response({
                'code': 200,
                'message': 'Thành công',
                'data': {
                    'page': page,
                    'limit': limit,
                    'total': total_records,
                    'items': data,
                }
            })
        except AccessError as e:
            return request.make_json_response({
                'code': 403,
                'message': f'Không có quyền truy cập dữ liệu: {str(e)}'
            }, status=403)
        except Exception as e:
            _logger.exception("Error in get_tickets: %s", e)
            return request.make_json_response({
                'code': 500,
                'message': 'Đã xảy ra lỗi máy chủ.'
            }, status=500)

    @http.route('/api/v1/helpdesk/tickets/<int:ticket_id>', type='http', auth='public', methods=['GET'], cors='*', csrf=False)
    def get_ticket_detail(self, ticket_id, **kw):
        """
        Lấy chi tiết 1 Ticket cho Mobile App (đầy đủ các trường render giao diện 2 màn)
        """
        user = self._get_authenticated_user()
        if not user:
            return request.make_json_response({
                'code': 401,
                'message': 'Chưa đăng nhập hoặc phiên làm việc đã hết hạn.'
            }, status=401)

        if not self._check_helpdesk_permission(user):
            return request.make_json_response({
                'code': 403,
                'message': 'Tài khoản của bạn không có quyền truy cập Ticket.'
            }, status=403)

        TicketModel = request.env['helpdesk.ticket'].with_user(user)
        ticket = TicketModel.browse(ticket_id)

        try:
            if not ticket.exists():
                return request.make_json_response({
                    'code': 404,
                    'message': 'Không tìm thấy Ticket.'
                }, status=404)

            ticket.check_access_rights('read')
            ticket.check_access_rule('read')

            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url', '')

            attachments = request.env['ir.attachment'].sudo().search([
                ('res_model', '=', 'helpdesk.ticket'),
                ('res_id', '=', ticket.id)
            ])
            attachment_list = []
            for att in attachments:
                attachment_list.append({
                    'id': att.id,
                    'name': att.name,
                    'mimetype': att.mimetype,
                    'file_size': att.file_size,
                    'url': f"{base_url}/web/content/{att.id}?download=true",
                    'is_image': (att.mimetype or '').startswith('image/'),
                    'thumbnail_url': f"{base_url}/web/image/{att.id}" if (att.mimetype or '').startswith('image/') else None
                })

            task_list = []
            for task in ticket.task_ids:
                task_list.append({
                    'id': task.id,
                    'name': task.name,
                    'stage': {
                        'id': task.stage_id.id if task.stage_id else None,
                        'name': task.stage_id.name if task.stage_id else '',
                    },
                    'assignees': [{
                        'id': u.id,
                        'name': u.name,
                        'avatar_url': f"{base_url}/web/image/res.users/{u.id}/avatar_128"
                    } for u in task.user_ids],
                    'date_deadline': fields.Date.to_string(task.date_deadline) if task.date_deadline else None,
                })

            detail = {
                'id': ticket.id,
                'code': f"#TK{str(ticket.id).zfill(5)}",
                'name': ticket.name,
                'create_date': fields.Datetime.to_string(ticket.create_date) if ticket.create_date else None,
                'priority': {
                    'level': ticket.priority or '0',
                    'label': dict(ticket._fields['priority'].selection).get(ticket.priority, 'Bình thường')
                },
                'stage': {
                    'id': ticket.stage_id.id if ticket.stage_id else None,
                    'name': ticket.stage_id.name if ticket.stage_id else '',
                },
                'request_source': {
                    'key': ticket.request_source or 'internal',
                    'label': dict(ticket._fields['request_source'].selection).get(ticket.request_source, 'Nội bộ')
                },
                'customer': {
                    'partner_id': ticket.partner_id.id if ticket.partner_id else None,
                    'company_name': ticket.partner_id.name or ticket.company_name or '',
                    'contact_name': ticket.contact_name or '',
                    'contact_phone': ticket.contact_phone or '',
                    'contact_email': ticket.contact_email or '',
                    'contact_department': ticket.contact_department or '',
                    'contact_position': ticket.contact_position or '',
                },
                'project': {
                    'id': ticket.project_id.id if ticket.project_id else None,
                    'name': ticket.project_id.name if ticket.project_id else '',
                },
                'content': {
                    'original_request_content': ticket.original_request_content or '',
                    'ai_analysis': ticket.description or '',
                },
                'assignee': {
                    'id': ticket.user_id.id if ticket.user_id else None,
                    'name': ticket.user_id.name if ticket.user_id else '',
                    'avatar_url': f"{base_url}/web/image/res.users/{ticket.user_id.id}/avatar_128" if ticket.user_id else None,
                },
                'team': {
                    'id': ticket.team_id.id if ticket.team_id else None,
                    'name': ticket.team_id.name if ticket.team_id else '',
                },
                'attachments': attachment_list,
                'tasks': task_list,
            }

            return request.make_json_response({
                'code': 200,
                'message': 'Thành công',
                'data': detail
            })
        except AccessError:
            return request.make_json_response({
                'code': 403,
                'message': 'Bạn không có quyền xem Ticket này.'
            }, status=403)
        except Exception as e:
            _logger.exception("Error in get_ticket_detail: %s", e)
            return request.make_json_response({
                'code': 500,
                'message': 'Đã xảy ra lỗi máy chủ.'
            }, status=500)
