from odoo import models, fields, api
from odoo.exceptions import UserError

class CrmLeadLost(models.TransientModel):
    _inherit = 'crm.lead.lost'
    
    lost_reason_id = fields.Many2one('crm.lost.reason', string='Lý do mất cơ hội')
    competitor = fields.Char(string='Đối thủ')
    is_competitor_reason = fields.Boolean(compute='_compute_is_competitor_reason')

    @api.depends('lost_reason_id')
    def _compute_is_competitor_reason(self):
        for rec in self:
            rec.is_competitor_reason = (rec.lost_reason_id.name == 'Chọn đối thủ')

    def action_lost_reason_apply(self):
        self.ensure_one()
        if not self.lost_reason_id:
            raise UserError('Vui lòng chọn Lý do mất cơ hội.')
            
        from odoo.tools.mail import is_html_empty
        if is_html_empty(self.lost_feedback):
            raise UserError('Vui lòng nhập Ghi chú kết thúc cơ hội.')
            
        if self.lost_reason_id.name == 'Chọn đối thủ' and not self.competitor:
            raise UserError('Vui lòng nhập Đối thủ khi lý do là "Chọn đối thủ".')
            
        leads = self.env['crm.lead'].browse(self.env.context.get('active_ids'))
        leads.write({
            'competitor': self.competitor if self.competitor else False,
        })
        return super(CrmLeadLost, self).action_lost_reason_apply()