from odoo import api, fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    department_name = fields.Char(string='Phòng ban')
    is_supplier = fields.Boolean(string='Nhà cung cấp', default=False)
    is_decision_maker = fields.Boolean(string='Người quyết định', default=False)

    def action_open_parent_company(self):
        self.ensure_one()
        if not self.parent_id:
            return
        return {
            'type': 'ir.actions.act_window',
            'name': 'Công ty',
            'res_model': 'res.partner',
            'view_mode': 'form',
            'res_id': self.parent_id.id,
            'target': 'current',
        }

class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    branch_name = fields.Char(string='Chi nhánh')
