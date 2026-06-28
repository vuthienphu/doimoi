# -*- coding: utf-8 -*-
from odoo import api, fields, models


class DcgEmployeeCertificate(models.Model):
    _name = 'dcg.employee.certificate'
    _description = 'Employee Certificate'
    _order = 'expiry_date desc, id desc'

    employee_id = fields.Many2one(
        'hr.employee', string='Employee', required=True,
        ondelete='cascade', index=True,
    )
    name = fields.Char(string='Certificate', required=True)
    issuer = fields.Char(string='Issuer')
    certificate_no = fields.Char(string='Certificate No.')
    issue_date = fields.Date(string='Issue Date')
    expiry_date = fields.Date(string='Expiry Date')
    is_expired = fields.Boolean(string='Expired', compute='_compute_is_expired', store=True)
    attachment_ids = fields.Many2many(
        'ir.attachment', 'dcg_employee_cert_attachment_rel',
        'cert_id', 'attachment_id', string='Attachments',
    )
    note = fields.Text(string='Note')

    @api.depends('expiry_date')
    def _compute_is_expired(self):
        today = fields.Date.today()
        for rec in self:
            rec.is_expired = bool(rec.expiry_date and rec.expiry_date < today)
