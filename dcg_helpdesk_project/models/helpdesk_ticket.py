from odoo import api, fields, models, _
import json
import logging
import urllib.request
from datetime import timedelta

_logger = logging.getLogger(__name__)


class HelpdeskTicket(models.Model):
    _name = 'helpdesk.ticket'
    _description = 'Yêu cầu Hỗ trợ / Ticket'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(string='Tiêu đề Yêu cầu', required=True, tracking=True)
    description = fields.Html(string='AI Phân tích & Đánh giá')
    original_request_content = fields.Html(
        string='Nội dung Yêu cầu gốc',
        help='Nội dung trao đổi / chat Zalo thô trực tiếp từ khách hàng',
    )
    partner_id = fields.Many2one('res.partner', string='Khách hàng', tracking=True)
    stage_id = fields.Many2one('helpdesk.stage', string='Trạng thái', tracking=True, group_expand='_read_group_stage_ids')
    team_id = fields.Many2one('helpdesk.team', string='Đội ngũ hỗ trợ', tracking=True)
    user_id = fields.Many2one('res.users', string='Người phụ trách', tracking=True)
    priority = fields.Selection([
        ('0', 'Bình thường'),
        ('1', 'Ưu tiên'),
        ('2', 'Cao'),
        ('3', 'Khẩn cấp'),
    ], string='Độ ưu tiên', default='0')
    active = fields.Boolean(string='Kích hoạt', default=True)

    request_source = fields.Selection([
        ('web', 'Website'),
        ('zalo', 'Zalo'),
        ('internal', 'Nội bộ'),
        ('other', 'Khác'),
    ], string='Nguồn yêu cầu', default='internal', required=True)

    company_name = fields.Char(
        string='Tên công ty (Form)',
        help='Tên công ty do khách hàng điền từ form yêu cầu công khai',
    )
    contact_name = fields.Char(string='Họ và tên')
    contact_email = fields.Char(string='Email')
    contact_phone = fields.Char(string='Số điện thoại')
    contact_department = fields.Char(string='Phòng ban')
    contact_position = fields.Char(string='Chức vụ')

    external_ticket_id = fields.Integer(string='ID Ticket phụ', index=True)
    external_ticket_ref = fields.Char(string='Mã Ticket phụ')
    external_partner_id = fields.Char(string='ID Partner phụ', index=True)
    zalo_channel_id = fields.Many2one('res.partner.zalo.channel', string='Kênh Zalo / Map Partner')

    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Dự án',
        domain="[('partner_id', '=', partner_id)]",
        help='Dự án liên quan đến yêu cầu này. Được lọc theo Công ty chọn ở trường Khách hàng.',
    )

    task_ids = fields.One2many(
        comodel_name='project.task',
        inverse_name='helpdesk_ticket_id',
        string='Danh sách Task',
    )
    task_count = fields.Integer(
        string='Số lượng Task',
        compute='_compute_task_count',
    )

    @api.model
    def _read_group_stage_ids(self, stages, domain):
        return self.env['helpdesk.stage'].search([])

    @api.onchange('zalo_channel_id')
    def _onchange_zalo_channel_id(self):
        if self.zalo_channel_id:
            if self.zalo_channel_id.partner_id and not self.partner_id:
                self.partner_id = self.zalo_channel_id.partner_id
            if self.zalo_channel_id.project_id and not self.project_id:
                self.project_id = self.zalo_channel_id.project_id

    @api.depends('task_ids')
    def _compute_task_count(self):
        for ticket in self:
            ticket.task_count = len(ticket.task_ids)

    @api.model
    def cron_sync_external_tickets(self):
        ICP = self.env['ir.config_parameter'].sudo()
        enabled_param = ICP.get_param('dcg_helpdesk.external_api_enabled')
        if not enabled_param or str(enabled_param).strip().lower() not in ('true', '1'):
            _logger.info("External Ticket Sync is disabled or not configured.")
            return True

        base_url = ICP.get_param('dcg_helpdesk.external_api_base_url')
        db = ICP.get_param('dcg_helpdesk.external_api_db')
        login = ICP.get_param('dcg_helpdesk.external_api_login')
        password = ICP.get_param('dcg_helpdesk.external_api_password')

        def is_invalid(val):
            return not val or str(val).strip().lower() in ('false', 'none', '', 'disabled')

        if is_invalid(base_url) or is_invalid(db) or is_invalid(login) or is_invalid(password):
            _logger.warning("Missing or invalid external API configuration in System Parameters (base_url, db, login, password). Sync aborted.")
            return False

        base_url = str(base_url).rstrip('/')

        endpoint = f"{base_url}/jsonrpc"

        def jsonrpc_call(service, method, *args):
            payload = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "service": service,
                    "method": method,
                    "args": list(args),
                }
            }
            req = urllib.request.Request(
                endpoint,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                res = json.loads(resp.read().decode('utf-8'))
                if 'error' in res:
                    raise RuntimeError(res['error'])
                return res.get('result')

        try:
            uid = jsonrpc_call('common', 'login', db, login, password)
            if not uid:
                _logger.error("JSON-RPC login failed to external system %s", base_url)
                return False

            # Lọc các Ticket được tạo hoặc cập nhật trong vòng 2 ngày gần nhất (2-day cutoff)
            cutoff_dt = fields.Datetime.now() - timedelta(days=2)
            cutoff_str = fields.Datetime.to_string(cutoff_dt)
            sync_domain = ['|', ('create_date', '>=', cutoff_str), ('write_date', '>=', cutoff_str)]

            _logger.info("=== [SYNC START] Fetching external tickets (Last 2 days cutoff: %s) ===", cutoff_str)

            fields_to_read = [
                "id", "ticket_ref", "name", "description", "team_id", "stage_id",
                "partner_id", "user_id", "priority", "create_date", "write_date", "close_date"
            ]
            tickets_data = jsonrpc_call(
                'object', 'execute_kw',
                db, uid, password,
                'gerp.helpdesk.ticket', 'search_read',
                [sync_domain],
                {"fields": fields_to_read, "order": "create_date desc", "limit": 200}
            )

            if not tickets_data:
                _logger.info("[SYNC] No external tickets created or updated in the last 2 days (Cutoff: %s).", cutoff_str)
                return True

            _logger.info("[SYNC] Search read returned %d external tickets modified in last 2 days.", len(tickets_data))

            # Lấy danh sách messages/notes qua custom API method gerp_get_messages (Request 2c)
            ext_ticket_ids = [t['id'] for t in tickets_data if t.get('id')]
            messages_by_ext_id = {}
            if ext_ticket_ids:
                try:
                    msgs_raw = jsonrpc_call(
                        'object', 'execute_kw',
                        db, uid, password,
                        'gerp.helpdesk.ticket', 'gerp_get_messages',
                        [ext_ticket_ids]
                    )
                    if msgs_raw and isinstance(msgs_raw, list):
                        for msg in msgs_raw:
                            tid = msg.get('ticket_id')
                            if tid:
                                messages_by_ext_id.setdefault(tid, []).append(msg)
                        _logger.info("[SYNC] Fetched %d message/chat entries for %d external tickets via gerp_get_messages.", len(msgs_raw), len(ext_ticket_ids))
                except Exception as msg_err:
                    _logger.warning("[SYNC WARNING] Could not fetch gerp_get_messages during sync: %s", str(msg_err))

            created_count = 0
            updated_count = 0
            up_to_date_count = 0

            for t_data in tickets_data:
                ext_id = t_data.get('id')
                if not ext_id:
                    continue

                ext_name = t_data.get('name') or f"Ticket {ext_id}"
                ext_ref = t_data.get('ticket_ref') or ''

                # 1. Xử lý Kênh Zalo (res.partner.zalo.channel)
                ext_partner = t_data.get('partner_id')
                ext_partner_id = str(ext_partner[0]) if ext_partner and isinstance(ext_partner, (list, tuple)) else (str(ext_partner) if ext_partner else False)
                ext_partner_name = ext_partner[1] if ext_partner and isinstance(ext_partner, (list, tuple)) and len(ext_partner) > 1 else False

                zalo_channel = False
                mapped_partner_id = False
                mapped_project_id = False

                if ext_partner_id:
                    zalo_channel = self.env['res.partner.zalo.channel'].search([
                        ('channel_id', '=', ext_partner_id)
                    ], limit=1)
                    if not zalo_channel:
                        zalo_channel = self.env['res.partner.zalo.channel'].create({
                            'name': ext_partner_name or f"Kênh Zalo {ext_partner_id}",
                            'channel_id': ext_partner_id,
                            'partner_id': False,
                        })
                        _logger.info("[SYNC] Created new Zalo channel: ID %s, Name '%s' (unmapped partner)", ext_partner_id, zalo_channel.name)
                    mapped_partner_id = zalo_channel.partner_id.id if zalo_channel.partner_id else False
                    mapped_project_id = zalo_channel.project_id.id if zalo_channel.project_id else False

                # 2. Xử lý nội dung chat, AI phân tích và độ ưu tiên
                ext_desc = t_data.get('description') or ''
                msgs = messages_by_ext_id.get(ext_id, [])

                # Lọc các nội dung tin nhắn chat của khách hàng
                chat_bodies = []
                for m in msgs:
                    body = m.get('body')
                    if body and isinstance(body, str) and body.strip():
                        if body.strip() not in chat_bodies:
                            chat_bodies.append(body.strip())

                raw_chat_html = "".join(chat_bodies) if chat_bodies else False
                ai_analysis_html = ext_desc.strip() if ext_desc and isinstance(ext_desc, str) and ext_desc.strip() else False

                # Map priority từ hệ thống ngoài ('low', 'normal', 'medium', 'high', 'urgent', '0', '1', '2', '3')
                raw_priority = str(t_data.get('priority') or '0').strip().lower()
                priority_map = {
                    '0': '0', '1': '1', '2': '2', '3': '3',
                    'low': '0', 'normal': '0', 'medium': '1', 'high': '2', 'urgent': '3'
                }
                mapped_priority = priority_map.get(raw_priority, '0')

                # 3. Tìm kiếm ticket nội bộ theo: external_ticket_id -> external_ticket_ref
                # (KHÔNG tìm kiếm theo name vì nhiều ticket có cùng tiêu đề mẫu)
                ticket = self.search([('external_ticket_id', '=', ext_id)], limit=1)
                if not ticket and ext_ref:
                    ticket = self.search([('external_ticket_ref', '=', ext_ref)], limit=1)

                # 4. Nếu chưa có ticket thì tạo mới (để rỗng partner/project nếu kênh chưa map)
                if not ticket:
                    default_stage = self.env['helpdesk.stage'].search([], order='sequence asc, id asc', limit=1)
                    create_vals = {
                        'name': ext_name,
                        'external_ticket_id': ext_id,
                        'external_ticket_ref': ext_ref,
                        'external_partner_id': ext_partner_id or False,
                        'request_source': 'zalo',
                        'original_request_content': raw_chat_html,
                        'description': ai_analysis_html,
                        'zalo_channel_id': zalo_channel.id if zalo_channel else False,
                        'partner_id': mapped_partner_id or False,
                        'project_id': mapped_project_id or False,
                        'stage_id': default_stage.id if default_stage else False,
                        'priority': mapped_priority,
                    }
                    ticket = self.create(create_vals)
                    created_count += 1
                    _logger.info(
                        "[SYNC CREATE] Created local Ticket ID %d (Ext ID: %s | Ref: '%s' | Name: '%s')",
                        ticket.id, ext_id, ext_ref, ext_name
                    )
                    continue

                # 5. Nếu ticket đã tồn tại thì kiểm tra khác biệt để cập nhật
                update_vals = {}
                changed_fields = []

                if (ticket.original_request_content or False) != (raw_chat_html or False):
                    update_vals['original_request_content'] = raw_chat_html
                    changed_fields.append('Nội dung Yêu cầu gốc (Chat Zalo)')

                if (ticket.description or False) != (ai_analysis_html or False):
                    update_vals['description'] = ai_analysis_html
                    changed_fields.append('AI Phân tích & Đánh giá')

                if (ticket.name or '') != ext_name:
                    update_vals['name'] = ext_name
                    changed_fields.append('Tiêu đề Yêu cầu')

                if ext_ref and (ticket.external_ticket_ref or '') != ext_ref:
                    update_vals['external_ticket_ref'] = ext_ref
                    changed_fields.append('Mã Ticket phụ')

                if ext_partner_id and (ticket.external_partner_id or '') != ext_partner_id:
                    update_vals['external_partner_id'] = ext_partner_id
                    changed_fields.append('ID Partner phụ')

                if mapped_partner_id and not ticket.partner_id:
                    update_vals['partner_id'] = mapped_partner_id
                    changed_fields.append('Khách hàng (Partner)')

                if mapped_project_id and not ticket.project_id:
                    update_vals['project_id'] = mapped_project_id
                    changed_fields.append('Dự án')

                if zalo_channel and not ticket.zalo_channel_id:
                    update_vals['zalo_channel_id'] = zalo_channel.id
                    changed_fields.append('Kênh Zalo')

                if not ticket.external_ticket_id:
                    update_vals['external_ticket_id'] = ext_id
                    changed_fields.append('ID Ticket phụ')

                if update_vals:
                    ticket.write(update_vals)
                    updated_count += 1
                    _logger.info(
                        "[SYNC UPDATE] Local Ticket ID %d (Ext ID: %s | Ref: '%s'): Updated fields [%s]",
                        ticket.id, ext_id, ext_ref, ", ".join(changed_fields)
                    )
                else:
                    up_to_date_count += 1
                    _logger.info(
                        "[SYNC OK] Local Ticket ID %d (Ext ID: %s | Ref: '%s'): Content is up to date.",
                        ticket.id, ext_id, ext_ref
                    )

            _logger.info(
                "=== [SYNC SUMMARY] Processed %d external tickets: Created=%d | Updated=%d | Up-to-date=%d ===",
                len(tickets_data), created_count, updated_count, up_to_date_count
            )
            return True

        except Exception as e:
            _logger.exception("Error syncing external tickets: %s", str(e))
            return False

    def action_open_ticket_tasks(self):
        self.ensure_one()
        return {
            'name': _('Danh sách Task'),
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.task_ids.ids)],
            'context': {
                'default_helpdesk_ticket_id': self.id,
                'default_project_id': self.project_id.id if self.project_id else False,
                'default_partner_id': self.partner_id.id if self.partner_id else False,
            },
        }

    def action_create_task_wizard(self):
        self.ensure_one()
        if not self.partner_id or not self.project_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'message': _('Phải xác định Công ty và Dự án trước khi tạo Task.'),
                },
            }
        return {
            'name': _('Tạo Task'),
            'type': 'ir.actions.act_window',
            'res_model': 'helpdesk.ticket.create.task.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_ticket_id': self.id,
                'default_project_id': self.project_id.id,
                'default_task_name': self.name,
                'default_description': self.description,
            },
        }

    @api.model_create_multi
    def create(self, vals_list):
        tickets = super().create(vals_list)
        for ticket in tickets:
            try:
                ticket._send_mobile_push_notification()
            except Exception as e:
                _logger.warning("Failed to send mobile push notification for ticket %s: %s", ticket.id, e)
        return tickets

    def _send_mobile_push_notification(self):
        self.ensure_one()
        recipients = self.env['res.users']
        if self.user_id:
            recipients |= self.user_id
        if self.team_id and self.team_id.member_ids:
            recipients |= self.team_id.member_ids

        if not recipients:
            return

        if 'mobile.notification.service' in self.env:
            title = f"Có Ticket mới: #{str(self.id).zfill(5)}"
            body = self.name or "Bạn có yêu cầu hỗ trợ mới cần xử lý."
            self.env['mobile.notification.service'].sudo().send_notification_to_users(
                user_ids=recipients.ids,
                title=title,
                body=body,
                model='helpdesk.ticket',
                res_id=self.id,
            )

