from odoo import api, fields, models

class ResPartnerRiskReason(models.Model):
    _name = 'res.partner.risk.reason'
    _description = 'Nguyên nhân rủi ro khách hàng'

    name = fields.Char(string='Nguyên nhân', required=True)

class ResPartnerProductStatus(models.Model):
    _name = 'res.partner.product.status'
    _description = 'Sản phẩm/dịch vụ đang sử dụng'

    partner_id = fields.Many2one('res.partner', string='Khách hàng', ondelete='cascade')
    name = fields.Char(string='Sản phẩm/Dịch vụ', required=True)
    status = fields.Selection([
        ('using', 'Đang sử dụng'),
        ('deploying', 'Đang triển khai'),
        ('testing', 'Thử nghiệm'),
        ('stopped', 'Đã dừng'),
    ], string='Trạng thái', required=True, default='using')
    project_id = fields.Many2one('project.project', string='Dự án liên kết')
    lead_id = fields.Many2one('crm.lead', string='Cơ hội liên kết')
    notes = fields.Text(string='Ghi chú')

class ResPartnerUpsell(models.Model):
    _name = 'res.partner.upsell'
    _description = 'Cơ hội phát triển (Upsell/Cross-sell)'

    partner_id = fields.Many2one('res.partner', string='Khách hàng', ondelete='cascade')
    type = fields.Selection([
        ('upsell', 'Bán thêm (Upsell)'),
        ('cross_sell', 'Bán chéo (Cross-sell)'),
    ], string='Loại', required=True, default='upsell')
    product_name = fields.Char(string='Sản phẩm/Dịch vụ', required=True)
    expected_revenue = fields.Monetary(string='Giá trị dự kiến', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', related='partner_id.currency_id')
    expected_date = fields.Date(string='Thời gian dự kiến')
    user_id = fields.Many2one('res.users', string='Người phụ trách')
    state = fields.Selection([
        ('potential', 'Tiềm năng'),
        ('qualified', 'Đủ điều kiện'),
        ('converted', 'Đã chuyển thành Opportunity'),
        ('lost', 'Đã hủy'),
    ], string='Trạng thái', default='potential')
    notes = fields.Text(string='Ghi chú')
    opportunity_id = fields.Many2one('crm.lead', string='Cơ hội bán hàng', readonly=True)

    def action_create_opportunity(self):
        for record in self:
            if not record.opportunity_id and record.state == 'qualified':
                lead = self.env['crm.lead'].create({
                    'name': f'[{dict(self._fields["type"].selection).get(record.type)}] {record.product_name}',
                    'partner_id': record.partner_id.id,
                    'user_id': record.user_id.id or self.env.user.id,
                    'expected_revenue': record.expected_revenue,
                    'description': record.notes,
                    'type': 'opportunity'
                })
                record.opportunity_id = lead.id
                record.state = 'converted'

class ResPartner(models.Model):
    _inherit = 'res.partner'

    account_customer_status = fields.Selection([
        ('potential', 'Đang tiềm năng'),
        ('using', 'Đang sử dụng dịch vụ'),
        ('strategic', 'Khách hàng chiến lược'),
        ('risk', 'Có rủi ro'),
        ('inactive', 'Không hoạt động'),
    ], string='Trạng thái khách hàng')
    account_relationship_level = fields.Selection([
        ('none', 'Chưa thiết lập'),
        ('basic', 'Cơ bản'),
        ('good', 'Tốt'),
        ('deep', 'Quan hệ sâu'),
        ('strategic', 'Chiến lược'),
    ], string='Mức độ quan hệ')
    account_customer_potential = fields.Selection([
        ('low', 'Thấp'),
        ('medium', 'Trung bình'),
        ('high', 'Cao'),
        ('strategic', 'Chiến lược'),
    ], string='Tiềm năng khách hàng')
    account_next_evaluation_date = fields.Date(string='Ngày đánh giá tiếp theo')
    account_customer_goal = fields.Char(string='Mục tiêu khách hàng')
    account_development_strategy = fields.Char(string='Chiến lược phát triển')
    account_internal_note = fields.Char(string='Ghi chú nội bộ')

    account_business_goal = fields.Char(string='Mục tiêu kinh doanh')
    account_current_issues = fields.Char(string='Vấn đề đang gặp')
    account_current_needs = fields.Char(string='Nhu cầu hiện tại')
    account_expected_needs = fields.Char(string='Nhu cầu dự kiến')
    account_tech_orientation = fields.Char(string='Định hướng công nghệ/chuyển đổi số')

    account_product_status_ids = fields.One2many('res.partner.product.status', 'partner_id', string='Sản phẩm/dịch vụ đang dùng')
    account_upsell_ids = fields.One2many('res.partner.upsell', 'partner_id', string='Cơ hội phát triển')
    
    account_risk_level = fields.Selection([
        ('low', 'Thấp'), ('medium', 'Trung bình'), ('high', 'Cao'), ('critical', 'Rất cao'),
    ], string='Mức độ rủi ro')
    account_risk_reason_ids = fields.Many2many('res.partner.risk.reason', string='Nguyên nhân rủi ro')
    account_risk_description = fields.Text(string='Mô tả rủi ro')

    currency_id = fields.Many2one('res.currency', string='Tiền tệ', compute='_compute_currency_id')
    
    def _compute_currency_id(self):
        for partner in self:
            partner.currency_id = partner.company_id.currency_id.id or self.env.company.currency_id.id

    account_total_opportunity_count = fields.Integer(string='Tổng cơ hội', compute='_compute_account_stats')
    account_open_opportunity_count = fields.Integer(string='Cơ hội đang mở', compute='_compute_account_stats')
    account_won_opportunity_count = fields.Integer(string='Cơ hội đã thắng', compute='_compute_account_stats')
    account_total_revenue = fields.Monetary(string='Doanh thu', compute='_compute_account_stats', currency_field='currency_id')
    account_pipeline_value = fields.Monetary(string='Pipeline', compute='_compute_account_stats', currency_field='currency_id')
    account_active_contract_count = fields.Integer(string='Hợp đồng đang hiệu lực', compute='_compute_account_stats')
    account_active_project_count = fields.Integer(string='Dự án đang triển khai', compute='_compute_account_stats')
    account_processing_ticket_count = fields.Integer(string='Ticket đang xử lý', compute='_compute_account_stats')
    account_upsell_count = fields.Integer(string='Cơ hội bán thêm', compute='_compute_account_stats')

    account_role = fields.Selection([
        ('decision_maker', 'Người quyết định'),
        ('influencer', 'Người ảnh hưởng'),
        ('user', 'Người sử dụng'),
        ('technical', 'Kỹ thuật'),
        ('finance', 'Tài chính'),
        ('purchasing', 'Mua hàng')
    ], string='Vai trò (Account Plan)')

    def _compute_account_stats(self):
        for partner in self:
            if 'crm.lead' in self.env:
                leads = self.env['crm.lead'].search([('partner_id', 'child_of', partner.id), ('type', '=', 'opportunity')])
                partner.account_total_opportunity_count = len(leads)
                partner.account_open_opportunity_count = len(leads.filtered(lambda l: l.probability > 0 and l.probability < 100))
                partner.account_won_opportunity_count = len(leads.filtered(lambda l: l.probability == 100))
                partner.account_pipeline_value = sum(leads.filtered(lambda l: l.probability > 0 and l.probability < 100).mapped('expected_revenue'))
            else:
                partner.account_total_opportunity_count = partner.account_open_opportunity_count = partner.account_won_opportunity_count = partner.account_pipeline_value = 0

            if 'sale.order' in self.env:
                won_orders = self.env['sale.order'].search([('partner_id', 'child_of', partner.id), ('state', 'in', ['sale', 'done'])])
                partner.account_total_revenue = sum(won_orders.mapped('amount_untaxed'))
                partner.account_active_contract_count = len(won_orders)
            else:
                partner.account_total_revenue = partner.account_active_contract_count = 0
            
            if 'project.project' in self.env:
                partner.account_active_project_count = self.env['project.project'].search_count([('partner_id', 'child_of', partner.id)])
            else:
                partner.account_active_project_count = 0

            if 'helpdesk.ticket' in self.env:
                partner.account_processing_ticket_count = self.env['helpdesk.ticket'].search_count([('partner_id', 'child_of', partner.id), ('stage_id.is_close', '=', False)])
            else:
                partner.account_processing_ticket_count = 0

            partner.account_upsell_count = len(partner.account_upsell_ids.filtered(lambda u: u.type == 'upsell' and u.state != 'lost'))
